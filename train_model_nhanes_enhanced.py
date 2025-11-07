# ===============================================================
# Modelo NHANES Mejorado (Desafío Salud 2025)
# - XGBoost + CalibratedClassifierCV (isotonic)
# - AUROC, AUPRC, Brier
# - Curva ROC y curva de calibración
# - Fairness por sexo y edad
# - Explicabilidad con permutation importance
# ===============================================================

import argparse
import os
from pathlib import Path

import numpy as np
import pandas as pd

from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.calibration import CalibratedClassifierCV, calibration_curve
from sklearn.metrics import (
    roc_auc_score, average_precision_score, brier_score_loss,
    classification_report, confusion_matrix, RocCurveDisplay,
    PrecisionRecallDisplay
)
from sklearn.inspection import permutation_importance

from xgboost import XGBClassifier
import matplotlib.pyplot as plt
import joblib
import warnings

warnings.filterwarnings("ignore", category=UserWarning)
np.random.seed(42)

# --------------------------- Utils -----------------------------

def ensure_dirs():
    Path("models").mkdir(exist_ok=True)
    Path("reports").mkdir(exist_ok=True)
    Path("reports/figs").mkdir(parents=True, exist_ok=True)

def align_test_columns(X_train, X_test):
    # Asegura que test tenga las mismas columnas (orden) que train
    missing_cols = [c for c in X_train.columns if c not in X_test.columns]
    if missing_cols:
        for c in missing_cols:
            X_test[c] = np.nan
    # Elimina columnas extra en test que no estén en train
    X_test = X_test[X_train.columns]
    return X_test

def print_header(title):
    print("\n" + "="*62)
    print(title)
    print("="*62)

def subgroup_auc(y_true, y_prob, mask, label):
    if mask.sum() == 0:
        return np.nan
    auc = roc_auc_score(y_true[mask], y_prob[mask])
    print(f"  AUC {label}: {auc:.3f}  (n={mask.sum()})")
    return auc

# ------------------------- Main train --------------------------

def main(target_label: str):
    ensure_dirs()

    # 1) Cargar datos
    print_header("1) Carga de datos")
    X_train = pd.read_csv("X_train.csv")
    y_train = pd.read_csv("y_train.csv").squeeze()
    X_test  = pd.read_csv("X_test.csv")
    y_test  = pd.read_csv("y_test.csv").squeeze()

    # Si estás entrenando hipertensión, reemplaza y_* por ese label en la exportación previa.
    # Este script asume que y_train/y_test ya corresponden al 'target_label' elegido.

    print(f"X_train: {X_train.shape} | X_test: {X_test.shape}")
    print(f"Target: {target_label}")

    # Alinear columnas entre train y test (por si hay pequeñas diferencias)
    X_test = align_test_columns(X_train, X_test)

    # 2) Pipeline: imputación + escalado + XGB + calibración isotónica
    print_header("2) Configurar pipeline (XGBoost + Calibración isotónica)")
    base_model = XGBClassifier(
        n_estimators=400,
        max_depth=5,
        learning_rate=0.05,
        subsample=0.9,
        colsample_bytree=0.9,
        min_child_weight=1.0,
        reg_lambda=1.0,
        random_state=42,
        eval_metric="logloss",
        tree_method="hist"  # usa 'gpu_hist' si tienes GPU
    )

    pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
        ("model", CalibratedClassifierCV(estimator=base_model,
                                 method="isotonic", cv=3))
    ])

    # 3) Entrenar
    print_header("3) Entrenamiento")
    pipeline.fit(X_train, y_train)

    # 4) Predicciones y métricas
    print_header("4) Evaluación global")
    y_prob = pipeline.predict_proba(X_test)[:, 1]
    y_pred_05 = (y_prob >= 0.50).astype(int)

    auc  = roc_auc_score(y_test, y_prob)
    aupr = average_precision_score(y_test, y_prob)
    brier = brier_score_loss(y_test, y_prob)

    print(f"AUROC  : {auc:.3f}")
    print(f"AUPRC  : {aupr:.3f}")
    print(f"Brier  : {brier:.3f}\n")

    print("Reporte @0.50:")
    print(classification_report(y_test, y_pred_05, digits=3))

    cm = confusion_matrix(y_test, y_pred_05)
    print("Matriz de confusión @0.50:")
    print(cm)

    # 5) Curvas ROC, PR y Calibración (guardar figuras)
    print_header("5) Curvas ROC / PR / Calibración (guardadas en reports/figs)")
    fig_roc = plt.figure()
    RocCurveDisplay.from_predictions(y_test, y_prob)
    plt.title(f"ROC - {target_label}")
    fig_roc.savefig("reports/figs/roc_curve.png", dpi=150, bbox_inches="tight")
    plt.close(fig_roc)

    fig_pr = plt.figure()
    PrecisionRecallDisplay.from_predictions(y_test, y_prob)
    plt.title(f"Precision-Recall - {target_label}")
    fig_pr.savefig("reports/figs/pr_curve.png", dpi=150, bbox_inches="tight")
    plt.close(fig_pr)

    prob_true, prob_pred = calibration_curve(y_test, y_prob, n_bins=10)
    fig_cal = plt.figure()
    plt.plot(prob_pred, prob_true, marker="o")
    plt.plot([0,1],[0,1],"--")
    plt.xlabel("Probabilidad predicha")
    plt.ylabel("Fracción positiva")
    plt.title(f"Curva de calibración - {target_label} (Brier={brier:.3f})")
    fig_cal.savefig("reports/figs/calibration_curve.png", dpi=150, bbox_inches="tight")
    plt.close(fig_cal)

    # 6) Fairness por subgrupos (si hay columnas)
    print_header("6) Fairness (subgrupos)")
    # Intentamos sexo y grupos etarios si existen en X_test
    gaps = {}

    if "sex_male" in X_test.columns:
        m_mask = X_test["sex_male"] == 1
        f_mask = X_test["sex_male"] == 0
        auc_m = subgroup_auc(y_test.values, y_prob, m_mask.values, "Hombres")
        auc_f = subgroup_auc(y_test.values, y_prob, f_mask.values, "Mujeres")
        if not (np.isnan(auc_m) or np.isnan(auc_f)):
            gaps["sexo_auc_gap"] = abs(auc_m - auc_f)
            print(f"  GAP AUC H-M: {gaps['sexo_auc_gap']:.3f}")

    if "age" in X_test.columns:
        # Bins 18-30, 31-45, 46-60, 60+
        bins = [18, 30, 45, 60, 200]
        labels = ["18-30", "31-45", "46-60", "60+"]
        age_bin = pd.cut(X_test["age"], bins=bins, labels=labels, right=True, include_lowest=True)
        aucs_age = {}
        for lab in labels:
            mask = (age_bin == lab).values
            auc_age = subgroup_auc(y_test.values, y_prob, mask, f"Edad {lab}")
            aucs_age[lab] = auc_age
        # gap máximo entre bins
        valid_aucs = [v for v in aucs_age.values() if not np.isnan(v)]
        if len(valid_aucs) >= 2:
            gaps["edad_auc_gap"] = max(valid_aucs) - min(valid_aucs)
            print(f"  GAP AUC por edad (max-min): {gaps['edad_auc_gap']:.3f}")

    # Guardar fairness en reporte
    fairness_report = {
        "AUROC": auc,
        "AUPRC": aupr,
        "Brier": brier,
        **gaps
    }
    pd.Series(fairness_report).to_csv("reports/fairness_summary.csv")
    print("\nFairness guardado en reports/fairness_summary.csv")

    # 7) Explicabilidad: permutation importance (estable y agnóstico a calibración)
    print_header("7) Explicabilidad (Permutation Importance)")
    # Para evitar sobrecargar, muestrea si hay demasiadas filas
    max_n = 5000
    if len(X_test) > max_n:
        rng = np.random.RandomState(42)
        idx = rng.choice(len(X_test), size=max_n, replace=False)
        X_explain = X_test.iloc[idx].copy()
        y_explain = y_test.iloc[idx].copy()
    else:
        X_explain = X_test.copy()
        y_explain = y_test.copy()

    perm = permutation_importance(
        pipeline, X_explain, y_explain, n_repeats=10, random_state=42, scoring="roc_auc"
    )
    importances = (
        pd.DataFrame({
            "feature": X_train.columns,
            "importance_mean": perm.importances_mean,
            "importance_std": perm.importances_std
        })
        .sort_values("importance_mean", ascending=False)
        .reset_index(drop=True)
    )
    importances.to_csv("reports/feature_importance_permutation.csv", index=False)
    print(importances.head(10))
    print("Importancias guardadas en reports/feature_importance_permutation.csv")

    # 8) Guardar modelo
    print_header("8) Guardar modelo")
    model_path = f"models/{target_label}_xgb_calibrated.pkl"
    joblib.dump(pipeline, model_path)
    print(f"✅ Modelo guardado en {model_path}")

    # 9) Resumen de consola final
    print_header("Resumen")
    print(f"AUROC={auc:.3f} | AUPRC={aupr:.3f} | Brier={brier:.3f}")
    if "sexo_auc_gap" in gaps:
        print(f"Gap AUC H-M: {gaps['sexo_auc_gap']:.3f}")
    if "edad_auc_gap" in gaps:
        print(f"Gap AUC edad: {gaps['edad_auc_gap']:.3f}")
    print("Figuras: reports/figs/  |  Reportes: reports/")
    print("Listo.")

# -------------------------- CLI -------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Entrenamiento modelo NHANES (diabetes o hipertensión) con calibración y fairness."
    )
    parser.add_argument(
        "--target", choices=["label_diabetes", "label_hypertension"],
        default="label_diabetes", help="Etiqueta objetivo a entrenar."
    )
    args = parser.parse_args()
    main(args.target)
