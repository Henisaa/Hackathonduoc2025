# ===============================================================
# src/targets.py - CREACIÓN DE ETIQUETAS
# ===============================================================

import pandas as pd

def create_diabetes_label(df):
    """Etiqueta binaria de diabetes según glucosa y HbA1c"""
    df = df.copy()
    a1c_col = "LAB_LBXGH"
    glu_col = "LAB_LBXGLU"
    df["label_diabetes"] = 0
    if a1c_col in df.columns:
        df.loc[df[a1c_col] >= 6.0, "label_diabetes"] = 1
    if glu_col in df.columns:
        df.loc[df[glu_col] >= 110, "label_diabetes"] = 1
    print(f"✅ Diabetes prevalencia: {df['label_diabetes'].mean():.1%}")
    return df

def create_hypertension_label(df):
    """Etiqueta binaria de hipertensión según presión sistólica/diastólica"""
    df = df.copy()
    sys_cols = [c for c in df.columns if c.startswith("BPXSY")]
    dia_cols = [c for c in df.columns if c.startswith("BPXDI")]
    df["sbp_mean"] = df[sys_cols].mean(axis=1, skipna=True)
    df["dbp_mean"] = df[dia_cols].mean(axis=1, skipna=True)
    df["label_hypertension"] = ((df["sbp_mean"] >= 130) | (df["dbp_mean"] >= 80)).astype(int)
    print(f"✅ Hipertensión prevalencia: {df['label_hypertension'].mean():.1%}")
    return df
