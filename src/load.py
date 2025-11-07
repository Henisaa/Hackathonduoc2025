# ===============================================================
# src/load.py - CARGA Y LIMPIEZA NHANES
# ===============================================================

import pandas as pd
import numpy as np
from pathlib import Path

CYCLE_TO_LETTER = {
    "2007-2008": "E",
    "2009-2010": "F",
    "2011-2012": "G",
    "2013-2014": "H",
    "2015-2016": "I",
    "2017-2018": "J"
}

def load_nhanes_data(data_dir='./data', cycles=None):
    """Carga múltiples ciclos NHANES y combina en un solo DataFrame"""
    data_path = Path(data_dir)
    if not data_path.exists():
        raise FileNotFoundError(f"No existe el directorio {data_path}")

    if cycles is None:
        cycles = list(CYCLE_TO_LETTER.keys())

    all_data = []
    for cycle in cycles:
        print(f"\n📂 Cargando ciclo {cycle}")
        letter = CYCLE_TO_LETTER.get(cycle, "")
        demo_file = data_path / f"DEMO_{letter}.csv"
        if not demo_file.exists():
            print(f"⚠️ DEMO no encontrado: {demo_file}")
            continue
        df = pd.read_csv(demo_file)
        df["CYCLE"] = cycle
        all_data.append(df)

    if not all_data:
        raise ValueError("No se cargaron ciclos válidos.")
    return pd.concat(all_data, ignore_index=True)

def clean_nhanes(df):
    """Limpieza básica y validación de columnas clave"""
    df = df.copy()
    missing_codes = [7, 9, 77, 99, 777, 999, 7777, 9999, '.', '']
    for col in df.select_dtypes(include=[np.number]).columns:
        df[col] = df[col].replace(missing_codes, np.nan)

    if "RIDAGEYR" in df.columns:
        df = df[(df["RIDAGEYR"] >= 18) & (df["RIDAGEYR"] <= 85)]
    if "RIAGENDR" in df.columns:
        df["sex"] = df["RIAGENDR"].map({1: "M", 2: "F"})
    print(f"✅ Limpieza completada ({len(df)} registros)")
    return df
