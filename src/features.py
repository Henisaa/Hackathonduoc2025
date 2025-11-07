# ===============================================================
# src/features.py - INGENIERÍA DE FEATURES
# ===============================================================

import pandas as pd

def engineer_features(df):
    """Genera variables derivadas IMC, cintura, edad, actividad, etc."""
    df = df.copy()
    if {"BMXWT", "BMXHT"}.issubset(df.columns):
        df["bmi"] = df["BMXWT"] / ((df["BMXHT"] / 100) ** 2)
    if {"BMXWAIST", "BMXHT"}.issubset(df.columns):
        df["waist_height_ratio"] = df["BMXWAIST"] / df["BMXHT"]
        df["high_waist_height_ratio"] = (df["waist_height_ratio"] >= 0.5).astype(int)
    if "RIDAGEYR" in df.columns:
        df["age"] = df["RIDAGEYR"]
        df["age_squared"] = df["age"] ** 2
    if "sex" in df.columns:
        df["sex_male"] = (df["sex"] == "M").astype(int)
    if "PAQ605" in df.columns and "PAQ620" in df.columns:
        df["total_active_days"] = df["PAQ605"].fillna(0) + df["PAQ620"].fillna(0)
        df["meets_activity_guidelines"] = (df["total_active_days"] >= 5).astype(int)
    return df
