# ===============================================================
# src/model.py - ENTRENAMIENTO CALIBRADO + FAIRNESS
# ===============================================================

import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import roc_auc_score, average_precision_score, brier_score_loss
from xgboost import XGBClassifier

def train_model(X_train, y_train, target_label="label_diabetes"):
    """Entrena un modelo XGBoost calibrado isotónicamente"""
    Path("models").mkdir(exist_ok=True)

    base = XGBClassifier(
        n_estimators=400, max_depth=5, learning_rate=0.05,
        subsample=0.9, colsample_bytree=0.9, eval_metric="logloss",
        random_state=42
    )

    model = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
        ("clf", CalibratedClassifierCV(estimator=base, method="isotonic", cv=3))
    ])

    model.fit(X_train, y_train)
    joblib.dump(model, f"models/{target_label}_xgb_calibrated.pkl")
    print(f"✅ Modelo guardado en models/{target_label}_xgb_calibrated.pkl")
    return model

def evaluate_model(model, X_test, y_test):
    """Evalúa métricas básicas"""
    y_prob = model.predict_proba(X_test)[:, 1]
    return {
        "AUROC": roc_auc_score(y_test, y_prob),
        "AUPRC": average_precision_score(y_test, y_prob),
        "Brier": brier_score_loss(y_test, y_prob),
    }
