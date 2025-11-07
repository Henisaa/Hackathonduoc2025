# ===============================================================
# train_models_calibrated.py
# MEJORA DEL MODELO: CALIBRACIÓN Y OPTIMIZACIÓN
# ===============================================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import roc_auc_score, average_precision_score, brier_score_loss
from sklearn.calibration import calibration_curve, CalibratedClassifierCV
from sklearn.model_selection import GridSearchCV
from xgboost import XGBClassifier
import joblib

# ===============================================================
# 1️⃣ CARGAR DATOS PREPROCESADOS
# ===============================================================
print("📂 Cargando datos preprocesados...")
X_train = pd.read_csv("X_train.csv")
y_train = pd.read_csv("y_train.csv").squeeze()
X_test = pd.read_csv("X_test.csv")
y_test = pd.read_csv("y_test.csv").squeeze()
feature_names = list(X_train.columns)

print(f"✅ Datos cargados: {X_train.shape[0]} train / {X_test.shape[0]} test")
print(f"   Features: {len(feature_names)} columnas")

# ===============================================================
# 2️⃣ BASELINE: REGRESIÓN LOGÍSTICA
# ===============================================================
print("\n=== 🔹 Baseline: Logistic Regression ===")

pipeline_lr = Pipeline([
    ('imputer', SimpleImputer(strategy='median')),
    ('scaler', StandardScaler()),
    ('classifier', LogisticRegression(random_state=42, max_iter=1000, class_weight='balanced'))
])

pipeline_lr.fit(X_train, y_train)
y_pred_proba_lr = pipeline_lr.predict_proba(X_test)[:, 1]

auroc_lr = roc_auc_score(y_test, y_pred_proba_lr)
auprc_lr = average_precision_score(y_test, y_pred_proba_lr)
brier_lr = brier_score_loss(y_test, y_pred_proba_lr)

print(f"\n✅ BASELINE - Logistic Regression:")
print(f"   AUROC: {auroc_lr:.4f}")
print(f"   AUPRC: {auprc_lr:.4f}")
print(f"   Brier Score: {brier_lr:.4f}")

joblib.dump(pipeline_lr, "model_baseline_lr.pkl")

# ===============================================================
# 3️⃣ MODELO AVANZADO: XGBOOST + GRIDSEARCH
# ===============================================================
print("\n=== 🔹 XGBoost Optimizado ===")

# Imputar valores faltantes
imputer = SimpleImputer(strategy='median')
X_train_imp = pd.DataFrame(imputer.fit_transform(X_train), columns=X_train.columns)
X_test_imp = pd.DataFrame(imputer.transform(X_test), columns=X_test.columns)

# Calcular peso de clase
pos_count = (y_train == 1).sum()
neg_count = (y_train == 0).sum()
scale_pos_weight = (neg_count / pos_count) if pos_count > 0 else 1.0

# GridSearch para mejorar hiperparámetros
param_grid = {
    "max_depth": [3, 4, 5],
    "learning_rate": [0.01, 0.05, 0.1],
    "n_estimators": [200, 300],
    "subsample": [0.8, 1.0],
    "colsample_bytree": [0.8, 1.0]
}

grid = GridSearchCV(
    XGBClassifier(
        scale_pos_weight=scale_pos_weight,
        random_state=42,
        eval_metric="logloss"
    ),
    param_grid,
    scoring="roc_auc",
    cv=3,
    n_jobs=-1,
    verbose=1
)

print("🔍 Buscando mejores parámetros...")
grid.fit(X_train_imp, y_train)

best_params = grid.best_params_
print(f"✅ Mejores hiperparámetros: {best_params}")

# Entrenar modelo final con los mejores parámetros
model_xgb = XGBClassifier(**best_params, random_state=42, eval_metric="logloss")
model_xgb.fit(X_train_imp, y_train)
y_pred_proba_xgb = model_xgb.predict_proba(X_test_imp)[:, 1]

auroc_xgb = roc_auc_score(y_test, y_pred_proba_xgb)
auprc_xgb = average_precision_score(y_test, y_pred_proba_xgb)
brier_xgb = brier_score_loss(y_test, y_pred_proba_xgb)

print(f"\n✅ XGBoost (Optimizado):")
print(f"   AUROC: {auroc_xgb:.4f}")
print(f"   AUPRC: {auprc_xgb:.4f}")
print(f"   Brier Score: {brier_xgb:.4f}")

# ===============================================================
# 4️⃣ CALIBRACIÓN ISOTÓNICA
# ===============================================================
print("\n📏 Calibrando modelo XGBoost con isotonic regression...")

calibrator = CalibratedClassifierCV(model_xgb, method="isotonic", cv=5)
calibrator.fit(X_train_imp, y_train)

y_pred_proba_xgb_cal = calibrator.predict_proba(X_test_imp)[:, 1]

auroc_xgb_cal = roc_auc_score(y_test, y_pred_proba_xgb_cal)
auprc_xgb_cal = average_precision_score(y_test, y_pred_proba_xgb_cal)
brier_xgb_cal = brier_score_loss(y_test, y_pred_proba_xgb_cal)

print(f"\n✅ XGBoost Calibrado:")
print(f"   AUROC: {auroc_xgb_cal:.4f}")
print(f"   AUPRC: {auprc_xgb_cal:.4f}")
print(f"   Brier Score: {brier_xgb_cal:.4f}")

# ===============================================================
# 5️⃣ CURVAS DE CALIBRACIÓN
# ===============================================================
print("\n=== 📈 Curvas de calibración ===")
prob_true_lr, prob_pred_lr = calibration_curve(y_test, y_pred_proba_lr, n_bins=10)
prob_true_xgb, prob_pred_xgb = calibration_curve(y_test, y_pred_proba_xgb, n_bins=10)
prob_true_xgb_cal, prob_pred_xgb_cal = calibration_curve(y_test, y_pred_proba_xgb_cal, n_bins=10)

fig, ax = plt.subplots(figsize=(8, 7))
ax.plot([0, 1], [0, 1], "k--", label="Perfect calibration")
ax.plot(prob_pred_lr, prob_true_lr, "o-", label=f"LR (Brier={brier_lr:.3f})")
ax.plot(prob_pred_xgb, prob_true_xgb, "s-", label=f"XGBoost (Brier={brier_xgb:.3f})")
ax.plot(prob_pred_xgb_cal, prob_true_xgb_cal, "^-", label=f"XGBoost Calibrado (Brier={brier_xgb_cal:.3f})")
ax.set_xlabel("Probabilidad predicha media", fontsize=12)
ax.set_ylabel("Proporción real de positivos", fontsize=12)
ax.set_title("Curvas de calibración - Modelos Comparados", fontweight="bold")
ax.legend(loc="upper left")
ax.grid(alpha=0.3)

plt.tight_layout()
plt.savefig("calibration_curves_improved.png", dpi=300)
plt.show()
print("✅ Curvas guardadas en calibration_curves_improved.png")

# ===============================================================
# 6️⃣ GUARDADO FINAL
# ===============================================================
joblib.dump(model_xgb, "model_xgboost_optimized.pkl")
joblib.dump(calibrator, "model_xgboost_calibrated.pkl")
print("\n💾 Modelos guardados: XGBoost optimizado y calibrado")
print("🚀 Entrenamiento y calibración completados con éxito.")
