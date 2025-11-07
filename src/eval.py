# ===============================================================
# src/eval.py - MÉTRICAS Y FAIRNESS
# ===============================================================

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

def subgroup_auc(y_true, y_prob, mask, label):
    if mask.sum() == 0:
        return np.nan
    auc = roc_auc_score(y_true[mask], y_prob[mask])
    print(f"{label}: AUC={auc:.3f} (n={mask.sum()})")
    return auc

def fairness_by_sex_age(X_test, y_test, y_prob):
    results = {}
    if "sex_male" in X_test.columns:
        results["gap_sex"] = abs(
            subgroup_auc(y_test, y_prob, X_test["sex_male"] == 1, "Hombres")
            - subgroup_auc(y_test, y_prob, X_test["sex_male"] == 0, "Mujeres")
        )
    if "age" in X_test.columns:
        bins = pd.cut(X_test["age"], bins=[18, 30, 45, 60, 100])
        aucs = [subgroup_auc(y_test, y_prob, bins == b, f"Edad {b}") for b in bins.cat.categories]
        results["gap_age"] = np.nanmax(aucs) - np.nanmin(aucs)
    return results
