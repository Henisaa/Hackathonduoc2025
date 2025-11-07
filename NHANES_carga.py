# ===============================================================
# NHANES 2007–2018: CARGA + LIMPIEZA + LABELS + FEATURES + SELECCIÓN (MEJORADO)
# ===============================================================
import pandas as pd
import numpy as np
from pathlib import Path

# ===============================================================
# CONFIGURACIÓN DE CICLOS
# ===============================================================
CYCLE_TO_LETTER = {
    "2007-2008": "E",
    "2009-2010": "F",
    "2011-2012": "G",
    "2013-2014": "H",
    "2015-2016": "I",
    "2017-2018": "J"
}

# ===============================================================
# FUNCIÓN PRINCIPAL DE CARGA
# ===============================================================
def load_nhanes_data(data_dir='./data', cycles=None):
    data_path = Path(data_dir)
    if not data_path.exists():
        print(f"⚠️ ERROR: El directorio {data_path} no existe.")
        return pd.DataFrame(), {}

    if cycles is None:
        cycles = list(CYCLE_TO_LETTER.keys())

    all_data = []
    metadata = {'cycles': cycles, 'n_participants': {}}

    for cycle in cycles:
        print(f"\n📁 Cargando ciclo {cycle}...")
        letter = CYCLE_TO_LETTER.get(cycle, "")
        cycle_data = None

        # --- DEMO ---
        demo_file = data_path / f"DEMO_{letter}.csv"
        if not demo_file.exists():
            demo_file = data_path / f"DEMO_{cycle.replace('-', '_')}.csv"
        if not demo_file.exists():
            print(f"⚠️ DEMO no encontrado: {demo_file}")
            continue

        demo = pd.read_csv(demo_file)
        if 'SEQN' not in demo.columns:
            continue
        demo['CYCLE'] = cycle
        cycle_data = demo
        print(f"  ✓ DEMO cargado: {len(demo):,} registros")

        # --- EXAM ---
        exam_file = data_path / f"EXAM_{letter}.csv"
        if not exam_file.exists():
            exam_file = data_path / f"EXAM_{cycle.replace('-', '_')}.csv"
        if exam_file.exists():
            exam = pd.read_csv(exam_file)
            if 'SEQN' in exam.columns:
                cycle_data = cycle_data.merge(exam, on='SEQN', how='left')
                print(f"  ✓ EXAM merged: {len(exam):,} registros")

        # --- LAB ---
        lab_file = data_path / f"LAB_{letter}.csv"
        if not lab_file.exists():
            lab_file = data_path / f"LAB_{cycle.replace('-', '_')}.csv"
        if lab_file.exists():
            lab = pd.read_csv(lab_file)
            if 'SEQN' in lab.columns:
                lab_cols = [c for c in lab.columns if c != 'SEQN']
                lab = lab.rename(columns={c: f"LAB_{c}" for c in lab_cols})
                cycle_data = cycle_data.merge(lab, on='SEQN', how='left')
                print(f"  ✓ LAB merged: {len(lab):,} registros")

        # --- QUEST ---
        quest_file = data_path / f"QUEST_{letter}.csv"
        if not quest_file.exists():
            quest_file = data_path / f"QUEST_{cycle.replace('-', '_')}.csv"
        if quest_file.exists():
            quest = pd.read_csv(quest_file)
            if 'SEQN' in quest.columns:
                cycle_data = cycle_data.merge(quest, on='SEQN', how='left')
                print(f"  ✓ QUEST merged: {len(quest):,} registros")

        if cycle_data is not None:
            all_data.append(cycle_data)
            metadata['n_participants'][cycle] = len(cycle_data)

    if all_data:
        df = pd.concat(all_data, ignore_index=True)
        print(f"\n✅ TOTAL: {len(df):,} participantes cargados | {df.shape[1]} columnas")
    else:
        df = pd.DataFrame()
        print("⚠️ No se cargaron datos.")
    return df, metadata


# ===============================================================
# CARGA ENTRENAMIENTO Y TEST
# ===============================================================
print("\n=== 🔹 Cargando datos NHANES (TRAIN 2007–2016) ===")
df_train, _ = load_nhanes_data(
    cycles=['2007-2008','2009-2010','2011-2012','2013-2014','2015-2016']
)
print("\n=== 🔹 Cargando datos NHANES (TEST 2017–2018) ===")
df_test, _ = load_nhanes_data(cycles=['2017-2018'])

# ===============================================================
# LIMPIEZA DE DATOS
# ===============================================================
def clean_nhanes_data(df):
    df = df.copy()
    missing_codes = [7,9,77,99,777,999,7777,9999,77777,99999,'.','']

    for col in df.select_dtypes(include=[np.number]).columns:
        df[col] = df[col].replace(missing_codes, np.nan)

    if 'RIDAGEYR' in df.columns:
        df = df[(df['RIDAGEYR'] >= 18) & (df['RIDAGEYR'] <= 85)]
    if 'RIAGENDR' in df.columns:
        df['sex'] = df['RIAGENDR'].map({1:'M',2:'F'})
    if 'BMXWT' in df.columns:
        df.loc[(df['BMXWT']<30)|(df['BMXWT']>250),'BMXWT'] = np.nan
    for bp_col in ['BPXSY1','BPXSY2','BPXDI1','BPXDI2']:
        if bp_col in df.columns:
            df.loc[(df[bp_col]<30)|(df[bp_col]>250),bp_col] = np.nan

    print(f"✅ Limpieza completada: {len(df):,} registros válidos")
    return df

df_train = clean_nhanes_data(df_train)
df_test = clean_nhanes_data(df_test)

# ===============================================================
# ANTI-FUGA
# ===============================================================
LAB_COLUMNS = [c for c in df_train.columns if c.startswith('LAB_')]
print(f"\n🚨 Columnas LAB detectadas: {len(LAB_COLUMNS)} (no se usarán como features)")
with open('LAB_COLUMNS_FORBIDDEN.txt','w',encoding='utf-8') as f:
    f.write('\n'.join(LAB_COLUMNS))

# ===============================================================
# CREACIÓN DE LABELS
# ===============================================================
def create_diabetes_label(df):
    df = df.copy()
    a1c_col, glucose_col = 'LAB_LBXGH', 'LAB_LBXGLU'
    df['label_diabetes'] = 0

    if a1c_col in df.columns:
        df.loc[df[a1c_col].notna() & (df[a1c_col] >= 6.0), 'label_diabetes'] = 1
    if glucose_col in df.columns:
        df.loc[df[glucose_col].notna() & (df[glucose_col] >= 110), 'label_diabetes'] = 1

    prevalence = df['label_diabetes'].mean()
    print(f"✅ Label Diabetes creado ({prevalence:.1%} prevalencia)")
    return df

def create_hypertension_label(df):
    df = df.copy()
    sys_cols = [c for c in df.columns if c.startswith('BPXSY')]
    dia_cols = [c for c in df.columns if c.startswith('BPXDI')]
    df['sbp_mean'] = df[sys_cols].mean(axis=1,skipna=True)
    df['dbp_mean'] = df[dia_cols].mean(axis=1,skipna=True)
    df['label_hypertension'] = 0
    has_bp = df[['sbp_mean','dbp_mean']].notna().any(axis=1)
    df.loc[(df['sbp_mean']>=130)|(df['dbp_mean']>=80), 'label_hypertension'] = 1
    df = df[has_bp].copy()
    prevalence = df['label_hypertension'].mean()
    print(f"✅ Label Hipertensión creado ({prevalence:.1%})")
    return df

df_train = create_diabetes_label(df_train)
df_test = create_diabetes_label(df_test)
df_train = create_hypertension_label(df_train)
df_test = create_hypertension_label(df_test)

# ===============================================================
# FEATURE ENGINEERING (MEJORADO)
# ===============================================================
def engineer_features(df):
    df = df.copy()

    # --- Antropometría ---
    if {'BMXWT','BMXHT'}.issubset(df.columns):
        df['bmi'] = df['BMXWT'] / ((df['BMXHT'] / 100) ** 2)
        df['bmi_category'] = pd.cut(df['bmi'], bins=[0,18.5,25,30,100],
                                    labels=['underweight','normal','overweight','obese'])
    if {'BMXWAIST','BMXHT'}.issubset(df.columns):
        df['waist_height_ratio'] = df['BMXWAIST'] / df['BMXHT']
        df['high_waist_height_ratio'] = (df['waist_height_ratio'] >= 0.5).astype(int)

    # --- Demografía ---
    if 'RIDAGEYR' in df.columns:
        df['age'] = df['RIDAGEYR']
        df['age_group'] = pd.cut(df['age'], bins=[0,30,45,60,100],
                                 labels=['18-30','31-45','46-60','60+'])
        df['age_squared'] = df['age']**2
    if 'RIAGENDR' in df.columns:
        df['sex_male'] = (df['RIAGENDR']==1).astype(int)
    if 'RIDRETH3' in df.columns:
        df['ethnicity'] = df['RIDRETH3'].map({
            1:'Mexican',2:'OtherHispanic',3:'White',4:'Black',6:'Asian',7:'Other'
        }).fillna('Unknown')

    # --- Conductuales / estilo de vida ---
    if 'SMQ020' in df.columns:
        df['ever_smoker'] = (df['SMQ020']==1).astype(int)
    if 'SMD030' in df.columns:
        df['cigarettes_per_day'] = df['SMD030']
        df['current_smoker'] = (df['cigarettes_per_day']>0).astype(int)
    if {'PAQ605','PAQ620'}.issubset(df.columns):
        df['total_active_days'] = df['PAQ605'].fillna(0)+df['PAQ620'].fillna(0)
        df['meets_activity_guidelines'] = (df['total_active_days']>=5).astype(int)
    if {'SLD010H','SLD012'}.issubset(df.columns):
        df['sleep_hours'] = df['SLD010H'].fillna(df['SLD012'])
        df['short_sleep'] = (df['sleep_hours']<6).astype(int)

    # --- Interacciones ---
    if {'bmi','age'}.issubset(df.columns):
        df['bmi_age_interaction'] = df['bmi'] * df['age']
    if {'waist_height_ratio','age'}.issubset(df.columns):
        df['waist_age_interaction'] = df['waist_height_ratio'] * df['age']

    print(f"✅ Features creadas: {df.shape[1]} columnas totales")
    return df

df_train = engineer_features(df_train)
df_test = engineer_features(df_test)

# ===============================================================
# SELECCIÓN FINAL (SIN FUGA)
# ===============================================================
def select_features_no_leakage(df, target='label_diabetes'):
    candidate_features = [
        'age','age_squared','sex_male','bmi','waist_height_ratio','high_waist_height_ratio',
        'cigarettes_per_day','current_smoker','ever_smoker',
        'total_active_days','meets_activity_guidelines',
        'bmi_age_interaction','waist_age_interaction',
        'sleep_hours','short_sleep'
    ]
    features = [f for f in candidate_features if f in df.columns]
    X = df[features].copy()
    y = df[target].copy()
    valid = y.notna()
    X = X[valid]; y = y[valid]
    print(f"✅ {len(features)} features seleccionadas - {len(X)} registros válidos")
    return X, y, features

X_train, y_train, features = select_features_no_leakage(df_train, 'label_diabetes')
X_test, y_test, _ = select_features_no_leakage(df_test, 'label_diabetes')

# ===============================================================
# EXPORTAR RESULTADOS
# ===============================================================
X_train.to_csv("X_train.csv", index=False)
y_train.to_csv("y_train.csv", index=False)
X_test.to_csv("X_test.csv", index=False)
y_test.to_csv("y_test.csv", index=False)
print("\n💾 Features exportadas: X_train, y_train, X_test, y_test")
