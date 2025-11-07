#CREAR ARCHIVO .env en directorio prinncipal con el siguiente texto:
#OPENAI_API_KEY="script sin comillas"
#instalar: pip install python-dotenv





# Imports generales
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import warnings
import json
from datetime import datetime

warnings.filterwarnings('ignore')
np.random.seed(42)

# Configuración visual
sns.set_style('whitegrid')
plt.rcParams['figure.figsize'] = (12, 6)

print("✅ Setup completado")

#-------#

import pandas as pd
from pathlib import Path

# Mapeo de ciclos a letras de archivo (usadas en nombres de archivo)
CYCLE_TO_LETTER = {
    '2007-2008': 'E',
    '2009-2010': 'F',
    '2011-2012': 'G',
    '2013-2014': 'H',
    '2015-2016': 'I',
    '2017-2018': 'J'
}




def load_nhanes_data(data_dir='./data', cycles=None):
    """
    Carga y merge de datos NHANES por ciclo.
    
    Args:
        data_dir: Directorio con archivos CSV
        cycles: Lista de ciclos a cargar, ej: ['2007-2008', '2009-2010']
    
    Returns:
        df: DataFrame consolidado
        metadata: Diccionario con información del merge
    """
    data_path = Path(data_dir)
    
    # Verificar que el directorio existe
    if not data_path.exists():
        print(f"⚠️ ERROR: El directorio {data_path} no existe")
        print(f"   Crea el directorio y coloca los archivos CSV allí")
        print(f"   Estructura esperada:")
        print(f"   {data_path}/")
        print(f"     ├── DEMO_2007_2008.csv")
        print(f"     ├── EXAM_2007_2008.csv")
        print(f"     ├── LAB_2007_2008.csv")
        print(f"     └── QUEST_2007_2008.csv")
        return pd.DataFrame(), {'cycles': [], 'modules': [], 'n_participants': {}}
    
    if cycles is None:
        # Ciclos de entrenamiento
        cycles = ['2007-2008', '2009-2010', '2011-2012', '2013-2014', '2015-2016']
    
    all_data = []
    metadata = {'cycles': cycles, 'modules': [], 'n_participants': {}}
    
    for cycle in cycles:
        print(f"\n📁 Cargando ciclo {cycle}...")
        cycle_data = None
        
        # 1. DEMOGRAPHICS (siempre la base)
        # Intentar ambos formatos: DEMO_2017_2018.csv (con guión bajo) y DEMO_J.csv (con letra)
        letter = CYCLE_TO_LETTER.get(cycle, '')
        demo_file = data_path / f"DEMO_{cycle.replace('-', '_')}.csv"
        if not demo_file.exists() and letter:
            # Intentar formato con letra (ej: DEMO_J.csv)
            demo_file = data_path / f"DEMO_{letter}.csv"
        if demo_file.exists():
            try:
                demo = pd.read_csv(demo_file)
                if 'SEQN' not in demo.columns:
                    print(f"  ⚠️ ERROR: Columna SEQN no encontrada en {demo_file}")
                    print(f"     Este archivo no es válido para merge")
                    continue
                demo['CYCLE'] = cycle
                cycle_data = demo
                print(f"  ✓ Demographics: {len(demo):,} registros, {len(demo.columns)} columnas")
            except Exception as e:
                print(f"  ⚠️ ERROR leyendo {demo_file}: {e}")
                continue
        else:
            print(f"  ⚠️ Demographics no encontrado: {demo_file}")
            continue
        
        # 2. EXAMINATION (antropometría y PA)
        # Intentar ambos formatos para EXAM
        exam_file = data_path / f"EXAM_{cycle.replace('-', '_')}.csv"
        if not exam_file.exists() and letter:
            exam_file = data_path / f"EXAM_{letter}.csv"
        if exam_file.exists():
            try:
                exam = pd.read_csv(exam_file)
                if 'SEQN' in exam.columns:
                    cycle_data = cycle_data.merge(exam, on='SEQN', how='left', suffixes=('', '_exam'))
                    print(f"  ✓ Examination: {len(exam):,} registros merged, {len(exam.columns)} columnas")
                else:
                    print(f"  ⚠️ Columna SEQN no encontrada en {exam_file}, saltando merge")
            except Exception as e:
                print(f"  ⚠️ ERROR leyendo {exam_file}: {e}")
        
        # 3. LABORATORY (A1c, glucosa - SOLO PARA LABEL)
        # Intentar ambos formatos para LAB
        lab_file = data_path / f"LAB_{cycle.replace('-', '_')}.csv"
        if not lab_file.exists() and letter:
            lab_file = data_path / f"LAB_{letter}.csv"
        if lab_file.exists():
            try:
                lab = pd.read_csv(lab_file)
                if 'SEQN' in lab.columns:
                    # CRÍTICO: Marcar columnas de lab para no usarlas como features
                    lab_cols = [c for c in lab.columns if c != 'SEQN']
                    lab = lab.rename(columns={c: f'LAB_{c}' for c in lab_cols})
                    cycle_data = cycle_data.merge(lab, on='SEQN', how='left')
                    print(f"  ✓ Laboratory: {len(lab):,} registros merged (SOLO PARA LABEL), {len(lab_cols)} columnas de lab")
                else:
                    print(f"  ⚠️ Columna SEQN no encontrada en {lab_file}, saltando merge")
            except Exception as e:
                print(f"  ⚠️ ERROR leyendo {lab_file}: {e}")
        else:
            print(f"  ⚠️ Laboratory no encontrado: {lab_file} (opcional pero recomendado)")
        
        # 4. QUESTIONNAIRE (sueño, actividad, tabaco)
        # Intentar ambos formatos para QUEST
        quest_file = data_path / f"QUEST_{cycle.replace('-', '_')}.csv"
        if not quest_file.exists() and letter:
            quest_file = data_path / f"QUEST_{letter}.csv"
        if quest_file.exists():
            try:
                quest = pd.read_csv(quest_file)
                if 'SEQN' in quest.columns:
                    cycle_data = cycle_data.merge(quest, on='SEQN', how='left', suffixes=('', '_quest'))
                    print(f"  ✓ Questionnaire: {len(quest):,} registros merged, {len(quest.columns)} columnas")
                else:
                    print(f"  ⚠️ Columna SEQN no encontrada en {quest_file}, saltando merge")
            except Exception as e:
                print(f"  ⚠️ ERROR leyendo {quest_file}: {e}")
        else:
            print(f"  ⚠️ Questionnaire no encontrado: {quest_file} (opcional)")
        
        # 5. DIETARY (opcional, nutrición)
        # Intentar ambos formatos para DIET
        diet_file = data_path / f"DIET_{cycle.replace('-', '_')}.csv"
        if not diet_file.exists() and letter:
            diet_file = data_path / f"DIET_{letter}.csv"
        if diet_file.exists():
            try:
                diet = pd.read_csv(diet_file)
                if 'SEQN' in diet.columns:
                    cycle_data = cycle_data.merge(diet, on='SEQN', how='left', suffixes=('', '_diet'))
                    print(f"  ✓ Dietary: {len(diet):,} registros merged, {len(diet.columns)} columnas")
                else:
                    print(f"  ⚠️ Columna SEQN no encontrada en {diet_file}, saltando merge")
            except Exception as e:
                print(f"  ⚠️ ERROR leyendo {diet_file}: {e}")
        
        if cycle_data is not None:
            all_data.append(cycle_data)
            metadata['n_participants'][cycle] = len(cycle_data)
    
    # Concatenar todos los ciclos
    if all_data:
        df = pd.concat(all_data, ignore_index=True)
        print(f"\n✅ TOTAL: {len(df):,} participantes cargados")
        print(f"   Columnas totales: {df.shape[1]}")
        print(f"   Ciclos cargados: {len(all_data)}/{len(cycles)}")
    else:
        print(f"\n⚠️ ADVERTENCIA: No se cargaron datos de ningún ciclo")
        print(f"   Verifica que los archivos CSV estén en {data_path}")
        df = pd.DataFrame()
    
    return df, metadata

# CARGAR DATOS DE ENTRENAMIENTO
df_train, meta = load_nhanes_data(cycles=['2007-2008', '2009-2010', '2011-2012', '2013-2014', '2015-2016', '2017-2018'])

# CARGAR DATOS DE TEST (ciclo ciego)
df_test, meta_test = load_nhanes_data(cycles=['2017-2018'])


#-------#

# Verificar distribución por ciclo
print("📊 Distribución por ciclo:")
print(df_train['CYCLE'].value_counts().sort_index())
print(f"\n📊 Test set: {df_test['CYCLE'].value_counts()}")

# Variables clave disponibles
print("\n🔑 Variables clave disponibles:")
key_vars = {
    'Demographics': ['RIDAGEYR', 'RIAGENDR', 'RIDRETH3'],
    'Anthropometry': ['BMXWT', 'BMXHT', 'BMXWAIST', 'BMXBMI'],
    'Blood Pressure': ['BPXSY1', 'BPXSY2', 'BPXDI1', 'BPXDI2'],
    'Laboratory': ['LAB_LBXGH', 'LAB_LBXGLU'],  # Prefijo LAB_
    'Sleep': ['SLD010H', 'SLD012'],
    'Smoking': ['SMQ020', 'SMD030'],
    'Physical Activity': ['PAQ605', 'PAQ620', 'PAD680']
}

for module, vars in key_vars.items():
    available = [v for v in vars if v in df_train.columns]
    print(f"  {module}: {len(available)}/{len(vars)} disponibles")
    if len(available) < len(vars):
        missing = [v for v in vars if v not in df_train.columns]
        print(f"    ⚠️ Faltantes: {missing}")
        

#------#

def clean_nhanes_data(df):
    """
    Limpieza estándar de datos NHANES.
    
    Maneja:
    - Valores missing codificados (77777, 99999, etc.)
    - Conversión de tipos
    - Rangos válidos
    """
    df = df.copy()
    
    # 1. Valores missing codificados en NHANES
    missing_codes = [7, 9, 77, 99, 777, 999, 7777, 9999, 77777, 99999, '.', '']
    for col in df.select_dtypes(include=[np.number]).columns:
        df[col] = df[col].replace(missing_codes, np.nan)
    
    # 2. Edad: solo adultos
    if 'RIDAGEYR' in df.columns:
        df = df[df['RIDAGEYR'] >= 18].copy()
        df = df[df['RIDAGEYR'] <= 85].copy()  # Límite superior
    
    # 3. Sexo: 1=M, 2=F
    if 'RIAGENDR' in df.columns:
        df['sex'] = df['RIAGENDR'].map({1: 'M', 2: 'F'})
    
    # 4. Antropometría: rangos razonables
    if 'BMXWT' in df.columns:  # Peso en kg
        df.loc[(df['BMXWT'] < 30) | (df['BMXWT'] > 250), 'BMXWT'] = np.nan
    
    if 'BMXHT' in df.columns:  # Altura en cm
        df.loc[(df['BMXHT'] < 120) | (df['BMXHT'] > 220), 'BMXHT'] = np.nan
    
    if 'BMXWAIST' in df.columns:  # Cintura en cm
        df.loc[(df['BMXWAIST'] < 40) | (df['BMXWAIST'] > 200), 'BMXWAIST'] = np.nan
    
    # 5. Presión arterial: rangos válidos
    for bp_col in ['BPXSY1', 'BPXSY2', 'BPXSY3']:
        if bp_col in df.columns:
            df.loc[(df[bp_col] < 70) | (df[bp_col] > 250), bp_col] = np.nan
    
    for bp_col in ['BPXDI1', 'BPXDI2', 'BPXDI3']:
        if bp_col in df.columns:
            df.loc[(df[bp_col] < 30) | (df[bp_col] > 150), bp_col] = np.nan
    
    print(f"✅ Limpieza completada: {len(df):,} registros válidos")
    return df

# Aplicar limpieza
df_train = clean_nhanes_data(df_train)
df_test = clean_nhanes_data(df_test)


#-------#


# CRÍTICO: Identificar todas las columnas de laboratorio
LAB_COLUMNS = [col for col in df_train.columns if col.startswith('LAB_')]

print(f"🚨 COLUMNAS DE LABORATORIO IDENTIFICADAS (NO USAR COMO FEATURES):")
print(f"   Total: {len(LAB_COLUMNS)} columnas")
for col in LAB_COLUMNS[:20]:  # Mostrar primeras 20
    print(f"   - {col}")

# Guardar lista para referencia
with open('LAB_COLUMNS_FORBIDDEN.txt', 'w') as f:
    f.write("\n".join(LAB_COLUMNS))

print("\n✅ Lista guardada en LAB_COLUMNS_FORBIDDEN.txt")



#------#

def create_diabetes_label(df):
    """
    Etiqueta de alto riesgo de diabetes usando A1c y/o glucosa.
    
    Criterios:
    - A1c >= 6.5% (48 mmol/mol) -> Diabetes
    - A1c 5.7-6.4% (39-47 mmol/mol) -> Prediabetes
    - Glucosa en ayunas >= 126 mg/dL -> Diabetes
    - Glucosa 100-125 mg/dL -> Prediabetes
    
    Label = 1 si Diabetes o Prediabetes avanzada (A1c >= 6.0)
    """
    df = df.copy()
    
    # Variables de laboratorio (ajustar según nombres reales)
    a1c_col = 'LAB_LBXGH'  # A1c (%), ajustar nombre
    glucose_col = 'LAB_LBXGLU'  # Glucosa (mg/dL), ajustar nombre
    
    # Inicializar label
    df['label_diabetes'] = 0
    
    # Verificar qué columnas están disponibles
    has_a1c = a1c_col in df.columns
    has_glucose = glucose_col in df.columns
    
    if not has_a1c and not has_glucose:
        print("⚠️ ADVERTENCIA: No se encontraron columnas de laboratorio (LAB_LBXGH o LAB_LBXGLU)")
        print("   Asegúrate de que los archivos LAB_*.csv estén cargados correctamente")
        return df
    
    # Criterio 1: A1c
    if has_a1c:
        # Filtrar valores válidos antes de comparar
        valid_a1c = df[a1c_col].notna()
        df.loc[valid_a1c & (df[a1c_col] >= 6.0), 'label_diabetes'] = 1
        print(f"  A1c >= 6.0%: {(valid_a1c & (df[a1c_col] >= 6.0)).sum():,} casos")
    else:
        print(f"  ⚠️ Columna {a1c_col} no encontrada")
    
    # Criterio 2: Glucosa
    if has_glucose:
        # Filtrar valores válidos antes de comparar
        valid_glucose = df[glucose_col].notna()
        df.loc[valid_glucose & (df[glucose_col] >= 110), 'label_diabetes'] = 1
        print(f"  Glucosa >= 110 mg/dL: {(valid_glucose & (df[glucose_col] >= 110)).sum():,} casos")
    else:
        print(f"  ⚠️ Columna {glucose_col} no encontrada")
    
    # Remover casos sin datos de laboratorio
    lab_cols = []
    if has_a1c:
        lab_cols.append(a1c_col)
    if has_glucose:
        lab_cols.append(glucose_col)
    
    if lab_cols:
        has_lab_data = df[lab_cols].notna().any(axis=1)
        df = df[has_lab_data].copy()
    else:
        print("⚠️ ADVERTENCIA: No hay datos de laboratorio disponibles para filtrar")
        return df
    
    prevalence = df['label_diabetes'].mean()
    print(f"\n✅ Label Diabetes creado:")
    print(f"   Prevalencia: {prevalence:.1%}")
    print(f"   n = {df['label_diabetes'].sum():,} / {len(df):,}")
    
    return df

# Crear labels
df_train = create_diabetes_label(df_train)
df_test = create_diabetes_label(df_test)



#-------




def create_hypertension_label(df):
    """
    Etiqueta de hipertensión usando mediciones de PA.
    
    Criterios (Estadio 1+):
    - Sistólica >= 130 mmHg, o
    - Diastólica >= 80 mmHg
    
    Usa promedio de 2-3 mediciones disponibles.
    """
    df = df.copy()
    
    # Calcular promedio de mediciones de PA
    sys_cols = [c for c in df.columns if c.startswith('BPXSY') and len(c) > 5 and c[5:].isdigit()]
    dia_cols = [c for c in df.columns if c.startswith('BPXDI') and len(c) > 5 and c[5:].isdigit()]
    
    if not sys_cols and not dia_cols:
        print("⚠️ ADVERTENCIA: No se encontraron columnas de presión arterial (BPXSY* o BPXDI*)")
        print("   Asegúrate de que los archivos EXAM_*.csv estén cargados correctamente")
        return df
    
    # Inicializar columnas
    if sys_cols:
        df['sbp_mean'] = df[sys_cols].mean(axis=1)
        print(f"  Columnas sistólica encontradas: {sys_cols}")
    else:
        df['sbp_mean'] = np.nan
        print("  ⚠️ No se encontraron columnas de presión sistólica")
    
    if dia_cols:
        df['dbp_mean'] = df[dia_cols].mean(axis=1)
        print(f"  Columnas diastólica encontradas: {dia_cols}")
    else:
        df['dbp_mean'] = np.nan
        print("  ⚠️ No se encontraron columnas de presión diastólica")
    
    # Criterio de hipertensión (solo si tenemos al menos una medida)
    df['label_hypertension'] = 0
    has_bp_data = df[['sbp_mean', 'dbp_mean']].notna().any(axis=1)
    
    if has_bp_data.any():
        # Aplicar criterio solo donde hay datos
        mask = (df['sbp_mean'].notna() & (df['sbp_mean'] >= 130)) | \
               (df['dbp_mean'].notna() & (df['dbp_mean'] >= 80))
        df.loc[mask, 'label_hypertension'] = 1
    
    # Remover casos sin datos de PA
    df = df[has_bp_data].copy()
    
    if len(df) > 0:
        prevalence = df['label_hypertension'].mean()
        print(f"\n✅ Label Hipertensión creado:")
        print(f"   Prevalencia: {prevalence:.1%}")
        print(f"   n = {df['label_hypertension'].sum():,} / {len(df):,}")
    else:
        print("\n⚠️ ADVERTENCIA: No hay datos de presión arterial disponibles")
    
    return df

# Opcional: crear también label de hipertensión
df_train = create_hypertension_label(df_train)
df_test = create_hypertension_label(df_test)



#------#


def engineer_features(df):
    """
    Crea features derivadas SOLO de variables permitidas.
    
    NO usar columnas de laboratorio (LAB_*).
    """
    df = df.copy()
    
    # 1. ANTROPOMETRÍA
    # IMC (Body Mass Index)
    if 'BMXWT' in df.columns and 'BMXHT' in df.columns:
        df['bmi'] = df['BMXWT'] / ((df['BMXHT'] / 100) ** 2)
        # Categorías de IMC
        df['bmi_category'] = pd.cut(df['bmi'], 
                                     bins=[0, 18.5, 25, 30, 100],
                                     labels=['underweight', 'normal', 'overweight', 'obese'])
    
    # Ratio cintura-altura (mejor predictor que IMC)
    if 'BMXWAIST' in df.columns and 'BMXHT' in df.columns:
        df['waist_height_ratio'] = df['BMXWAIST'] / df['BMXHT']
        # Riesgo si >= 0.5
        df['high_waist_height_ratio'] = (df['waist_height_ratio'] >= 0.5).astype(int)
    
    # 2. EDAD
    if 'RIDAGEYR' in df.columns:
        df['age'] = df['RIDAGEYR']
        # Grupos etarios
        df['age_group'] = pd.cut(df['age'], 
                                  bins=[0, 30, 45, 60, 100],
                                  labels=['18-30', '31-45', '46-60', '60+'])
        # Edad al cuadrado (relación no lineal)
        df['age_squared'] = df['age'] ** 2
    
    # 3. SEXO (ya mapeado en limpieza)
    if 'sex' in df.columns:
        df['sex_male'] = (df['sex'] == 'M').astype(int)
    
    # 4. SUEÑO
    sleep_cols = ['SLD010H', 'SLD012']  # Horas de sueño
    for col in sleep_cols:
        if col in df.columns:
            df['sleep_hours'] = df[col]
            # Sueño insuficiente (<7h) o excesivo (>9h)
            df['poor_sleep'] = ((df['sleep_hours'] < 7) | (df['sleep_hours'] > 9)).astype(int)
            break
    
    # 5. TABAQUISMO
    if 'SMQ020' in df.columns:  # ¿Ha fumado 100+ cigarrillos?
        df['ever_smoker'] = (df['SMQ020'] == 1).astype(int)
    
    if 'SMD030' in df.columns:  # Cigarrillos por día
        df['cigarettes_per_day'] = df['SMD030']
        df['current_smoker'] = (df['cigarettes_per_day'] > 0).astype(int)
    
    # 6. ACTIVIDAD FÍSICA
    # PAQ605: días de actividad vigorosa
    # PAQ620: días de actividad moderada
    if 'PAQ605' in df.columns and 'PAQ620' in df.columns:
        df['total_active_days'] = df['PAQ605'].fillna(0) + df['PAQ620'].fillna(0)
        # Cumple recomendaciones (150+ min/semana ≈ 5 días)
        df['meets_activity_guidelines'] = (df['total_active_days'] >= 5).astype(int)
    
    # 7. INTERACCIONES IMPORTANTES
    if 'bmi' in df.columns and 'age' in df.columns:
        df['bmi_age_interaction'] = df['bmi'] * df['age']
    
    if 'waist_height_ratio' in df.columns and 'age' in df.columns:
        df['waist_age_interaction'] = df['waist_height_ratio'] * df['age']
    
    print(f"✅ Features creadas: {df.shape[1]} columnas totales")
    
    # Listar nuevas features numéricas
    new_features = ['bmi', 'waist_height_ratio', 'age', 'age_squared',
                    'sleep_hours', 'cigarettes_per_day', 'total_active_days',
                    'bmi_age_interaction', 'waist_age_interaction']
    available_features = [f for f in new_features if f in df.columns]
    
    print(f"\n📊 Features numéricas disponibles: {len(available_features)}")
    for feat in available_features:
        if feat in df.columns:
            missing_pct = df[feat].isna().mean() * 100
            print(f"   - {feat}: {missing_pct:.1f}% missing")
    
    return df

# Aplicar ingeniería de features
df_train = engineer_features(df_train)
df_test = engineer_features(df_test)



#------#
#3.2#

def select_features_no_leakage(df, target='label_diabetes'):
    """
    Selecciona features finales SIN columnas de laboratorio.
    
    CRÍTICO: Valida que no haya fuga de datos.
    """
    # Features candidatas (ajustar según disponibilidad)
    candidate_features = [
        # Demográficas
        'age', 'age_squared', 'sex_male',
        
        # Antropometría
        'bmi', 'waist_height_ratio', 'high_waist_height_ratio',
        
        # Estilo de vida
        'sleep_hours', 'poor_sleep',
        'cigarettes_per_day', 'current_smoker', 'ever_smoker',
        'total_active_days', 'meets_activity_guidelines',
        
        # Interacciones
        'bmi_age_interaction', 'waist_age_interaction',
        
        # Presión arterial (si el label NO es hipertensión)
        # 'sbp_mean', 'dbp_mean'  # Descomentar si label = diabetes
    ]
    
    # Filtrar features disponibles
    features = [f for f in candidate_features if f in df.columns]
    
    # VALIDACIÓN ANTI-FUGA
    lab_features = [f for f in features if f.startswith('LAB_')]
    if lab_features:
        raise ValueError(f"🚨 FUGA DE DATOS DETECTADA: {lab_features}")
    
    print(f"✅ Features seleccionadas: {len(features)}")
    print(f"   Target: {target}")
    
    # Preparar X, y
    X = df[features].copy()
    y = df[target].copy()
    
    # Remover filas con target missing
    valid_idx = y.notna()
    X = X[valid_idx]
    y = y[valid_idx]
    
    print(f"\n📊 Dataset final: {len(X):,} registros")
    print(f"   Prevalencia: {y.mean():.1%}")
    
    return X, y, features

# Preparar datos finales
X_train, y_train, feature_names = select_features_no_leakage(df_train, target='label_diabetes')
X_test, y_test, _ = select_features_no_leakage(df_test, target='label_diabetes')


#--------#
#4.1#


from sklearn.linear_model import LogisticRegression
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import roc_auc_score, average_precision_score, brier_score_loss
import joblib

# Pipeline con imputación y escalado
pipeline_lr = Pipeline([
    ('imputer', SimpleImputer(strategy='median')),
    ('scaler', StandardScaler()),
    ('classifier', LogisticRegression(random_state=42, max_iter=1000, class_weight='balanced'))
])

# Entrenar
print("🔄 Entrenando Logistic Regression...")
pipeline_lr.fit(X_train, y_train)

# Predicciones
y_pred_proba_lr = pipeline_lr.predict_proba(X_test)[:, 1]

# Métricas
auroc_lr = roc_auc_score(y_test, y_pred_proba_lr)
auprc_lr = average_precision_score(y_test, y_pred_proba_lr)
brier_lr = brier_score_loss(y_test, y_pred_proba_lr)

print(f"\n✅ BASELINE - Logistic Regression:")
print(f"   AUROC: {auroc_lr:.4f}")
print(f"   AUPRC: {auprc_lr:.4f}")
print(f"   Brier Score: {brier_lr:.4f}")

# Guardar modelo
joblib.dump(pipeline_lr, 'model_baseline_lr.pkl')
print("\n💾 Modelo guardado: model_baseline_lr.pkl")


#------#
#4.2#

from xgboost import XGBClassifier
from sklearn.model_selection import StratifiedKFold

# Pipeline con imputación
imputer = SimpleImputer(strategy='median')
X_train_imp = pd.DataFrame(
    imputer.fit_transform(X_train),
    columns=X_train.columns,
    index=X_train.index
)
X_test_imp = pd.DataFrame(
    imputer.transform(X_test),
    columns=X_test.columns,
    index=X_test.index
)

# Calcular scale_pos_weight para desbalance
# Manejar caso donde no hay casos positivos (evitar división por cero)
pos_count = (y_train == 1).sum()
neg_count = (y_train == 0).sum()

if pos_count == 0:
    print("⚠️ ADVERTENCIA: No hay casos positivos en el conjunto de entrenamiento")
    print("   Verifica que el label se haya creado correctamente")
    scale_pos_weight = 1.0  # Valor por defecto
else:
    scale_pos_weight = neg_count / pos_count

print(f"   Desbalance: {neg_count:,} negativos / {pos_count:,} positivos")
print(f"   scale_pos_weight: {scale_pos_weight:.2f}")

# Modelo XGBoost
model_xgb = XGBClassifier(
    n_estimators=200,
    max_depth=5,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    scale_pos_weight=scale_pos_weight,
    random_state=42,
    eval_metric='logloss'
)

print("🔄 Entrenando XGBoost...")
model_xgb.fit(
    X_train_imp, y_train,
    eval_set=[(X_test_imp, y_test)],
    verbose=False
)

# Predicciones
y_pred_proba_xgb = model_xgb.predict_proba(X_test_imp)[:, 1]

# Métricas
auroc_xgb = roc_auc_score(y_test, y_pred_proba_xgb)
auprc_xgb = average_precision_score(y_test, y_pred_proba_xgb)
brier_xgb = brier_score_loss(y_test, y_pred_proba_xgb)

print(f"\n✅ XGBoost:")
print(f"   AUROC: {auroc_xgb:.4f} {'✓' if auroc_xgb >= 0.80 else ''}")
print(f"   AUPRC: {auprc_xgb:.4f}")
print(f"   Brier Score: {brier_xgb:.4f} {'✓' if brier_xgb <= 0.12 else ''}")

# Importancia de features
feature_importance = pd.DataFrame({
    'feature': feature_names,
    'importance': model_xgb.feature_importances_
}).sort_values('importance', ascending=False)

print("\n📊 Top 10 Features:")
print(feature_importance.head(10).to_string(index=False))

# Guardar modelo y artefactos
joblib.dump(model_xgb, 'model_xgboost.pkl')
joblib.dump(imputer, 'imputer.pkl')
joblib.dump(feature_names, 'feature_names.pkl')
print("\n💾 Modelo guardado: model_xgboost.pkl")



#----------#
#4.3#

from sklearn.calibration import calibration_curve

# Calcular curvas de calibración
prob_true_lr, prob_pred_lr = calibration_curve(y_test, y_pred_proba_lr, n_bins=10)
prob_true_xgb, prob_pred_xgb = calibration_curve(y_test, y_pred_proba_xgb, n_bins=10)

# Visualizar
fig, ax = plt.subplots(1, 1, figsize=(10, 8))

ax.plot([0, 1], [0, 1], 'k--', label='Perfect calibration')
ax.plot(prob_pred_lr, prob_true_lr, 'o-', label=f'Logistic Regression (Brier={brier_lr:.4f})')
ax.plot(prob_pred_xgb, prob_true_xgb, 's-', label=f'XGBoost (Brier={brier_xgb:.4f})')

ax.set_xlabel('Mean predicted probability', fontsize=12)
ax.set_ylabel('Fraction of positives', fontsize=12)
ax.set_title('Calibration Curves', fontsize=14, fontweight='bold')
ax.legend(loc='upper left')
ax.grid(alpha=0.3)

plt.tight_layout()
plt.savefig('calibration_curves.png', dpi=300, bbox_inches='tight')
plt.show()

print("✅ Curvas de calibración guardadas en calibration_curves.png")


#--------#

#5.1#

def analyze_fairness(df_test, y_test, y_pred_proba, feature_names):
    """
    Analiza métricas de fairness por subgrupos.
    
    Subgrupos:
    - Sexo (M vs F)
    - Edad (<45, 45-60, >60)
    - Raza/etnia NHANES
    """
    results = []
    
    # Agregar predicciones al df
    df_eval = df_test.copy()
    df_eval['y_true'] = y_test.values
    df_eval['y_pred_proba'] = y_pred_proba
    
    # 1. Por sexo
    if 'sex' in df_eval.columns:
        for sex in ['M', 'F']:
            mask = df_eval['sex'] == sex
            if mask.sum() > 100:  # Mínimo 100 casos
                auroc = roc_auc_score(df_eval.loc[mask, 'y_true'], 
                                      df_eval.loc[mask, 'y_pred_proba'])
                brier = brier_score_loss(df_eval.loc[mask, 'y_true'],
                                         df_eval.loc[mask, 'y_pred_proba'])
                results.append({
                    'subgroup': f'Sex_{sex}',
                    'n': mask.sum(),
                    'prevalence': df_eval.loc[mask, 'y_true'].mean(),
                    'auroc': auroc,
                    'brier': brier
                })
    
    # 2. Por grupo etario
    if 'age_group' in df_eval.columns:
        for age_grp in df_eval['age_group'].dropna().unique():
            mask = df_eval['age_group'] == age_grp
            if mask.sum() > 100:
                auroc = roc_auc_score(df_eval.loc[mask, 'y_true'],
                                      df_eval.loc[mask, 'y_pred_proba'])
                brier = brier_score_loss(df_eval.loc[mask, 'y_true'],
                                         df_eval.loc[mask, 'y_pred_proba'])
                results.append({
                    'subgroup': f'Age_{age_grp}',
                    'n': mask.sum(),
                    'prevalence': df_eval.loc[mask, 'y_true'].mean(),
                    'auroc': auroc,
                    'brier': brier
                })
    
    # 3. Por raza/etnia (si disponible)
    if 'RIDRETH3' in df_eval.columns:
        race_map = {
            1: 'Mexican',
            2: 'Hispanic',
            3: 'White',
            4: 'Black',
            6: 'Asian',
            7: 'Other'
        }
        for race_code, race_name in race_map.items():
            mask = df_eval['RIDRETH3'] == race_code
            if mask.sum() > 100:
                auroc = roc_auc_score(df_eval.loc[mask, 'y_true'],
                                      df_eval.loc[mask, 'y_pred_proba'])
                brier = brier_score_loss(df_eval.loc[mask, 'y_true'],
                                         df_eval.loc[mask, 'y_pred_proba'])
                results.append({
                    'subgroup': f'Race_{race_name}',
                    'n': mask.sum(),
                    'prevalence': df_eval.loc[mask, 'y_true'].mean(),
                    'auroc': auroc,
                    'brier': brier
                })
    
    # Convertir a DataFrame
    df_fairness = pd.DataFrame(results)
    
    # Calcular gaps
    if len(df_fairness) > 0:
        auroc_gap = df_fairness['auroc'].max() - df_fairness['auroc'].min()
        brier_gap = df_fairness['brier'].max() - df_fairness['brier'].min()
        
        print("\n📊 ANÁLISIS DE EQUIDAD:")
        print("="*70)
        print(df_fairness.to_string(index=False))
        print("="*70)
        print(f"\n⚖️ GAPS:")
        print(f"   AUROC gap: {auroc_gap:.4f}")
        print(f"   Brier gap: {brier_gap:.4f}")
        
        if auroc_gap > 0.05:
            print(f"\n⚠️ Gap de AUROC > 0.05 detectado")
            print("   Considerar: rebalanceo, features adicionales, o post-processing")
    
    return df_fairness

# Analizar equidad con XGBoost
fairness_results = analyze_fairness(df_test, y_test, y_pred_proba_xgb, feature_names)

# Guardar resultados
fairness_results.to_csv('fairness_analysis.csv', index=False)
print("\n💾 Análisis guardado en fairness_analysis.csv")




#---------#

#test ia#
import joblib
import pandas as pd
import numpy as np

# Cargar artefactos
model = joblib.load("model_xgboost.pkl")
imputer = joblib.load("imputer.pkl")
feature_names = joblib.load("feature_names.pkl")

# Crear un DataFrame vacío con todas las columnas esperadas
new_person = pd.DataFrame(columns=feature_names)

# Rellenar solo las variables que conoces
new_person.loc[0, "age"] = 45
new_person.loc[0, "sex_male"] = 1
new_person.loc[0, "bmi"] = 32
new_person.loc[0, "waist_height_ratio"] = 0.58
new_person.loc[0, "sleep_hours"] = 6
new_person.loc[0, "cigarettes_per_day"] = 5
new_person.loc[0, "total_active_days"] = 2
new_person.loc[0, "bmi_age_interaction"] = 32 * 45
new_person.loc[0, "waist_age_interaction"] = 0.58 * 45

# Dejar el resto como NaN → el imputer los completará automáticamente
new_person_imp = pd.DataFrame(imputer.transform(new_person), columns=feature_names)

# Predicción
prob = model.predict_proba(new_person_imp)[0, 1]
print(f"Probabilidad estimada de diabetes: {prob:.2%}")





#--------------#
#6.1#





import os
import json
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()


# Configurar API Key (usar variable de entorno)
# export OPENAI_API_KEY="tu-api-key"
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Schema de validación (del documento)
USER_PROFILE_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
        "age": {"type": "integer", "minimum": 18, "maximum": 85},
        "sex": {"type": "string", "enum": ["F", "M"]},
        "height_cm": {"type": "number", "minimum": 120, "maximum": 220},
        "weight_kg": {"type": "number", "minimum": 30, "maximum": 220},
        "waist_cm": {"type": "number", "minimum": 40, "maximum": 170},
        "sleep_hours": {"type": "number", "minimum": 3, "maximum": 14},
        "smokes_cig_day": {"type": "integer", "minimum": 0, "maximum": 60},
        "days_mvpa_week": {"type": "integer", "minimum": 0, "maximum": 7},
        "fruit_veg_portions_day": {"type": "number", "minimum": 0, "maximum": 12}
    },
    "required": ["age", "sex", "height_cm", "weight_kg", "waist_cm"]
}

print("✅ Cliente de OpenAI configurado")



#---------------#
#6.3#

def extract_user_data_from_text(user_text: str) -> dict:
    """
    Extrae datos estructurados de texto libre usando OpenAI.
    
    Args:
        user_text: Texto del usuario describiendo su perfil
    
    Returns:
        dict con datos validados según schema
    """
    
    prompt = f"""Extrae la siguiente información del texto del usuario y devuélvela en formato JSON válido.

TEXTO DEL USUARIO:
{user_text}

INSTRUCCIONES:
1. Extrae SOLO la información presente en el texto
2. Convierte unidades si es necesario:
   - Altura: convertir a centímetros (1 metro = 100 cm, 1 pie = 30.48 cm, 1 pulgada = 2.54 cm)
   - Peso: convertir a kilogramos (1 libra = 0.453592 kg)
   - Cintura: convertir a centímetros
3. Sexo: usar "M" o "F" (masculino/femenino)
4. Si falta información requerida, usa null
5. Devuelve SOLO el JSON, sin explicaciones

ESQUEMA ESPERADO:
{json.dumps(USER_PROFILE_SCHEMA, indent=2)}

JSON:"""
    
    # Llamar a OpenAI
    response = client.chat.completions.create(
        model="gpt-4o",
        max_tokens=1000,
        messages=[{
            "role": "user",
            "content": prompt
        }],
        response_format={"type": "json_object"}
    )
    
    # Extraer JSON de la respuesta
    response_text = response.choices[0].message.content.strip()
    
    # Limpiar markdown si existe
    if response_text.startswith('```'):
        response_text = response_text.split('```')[1]
        if response_text.startswith('json'):
            response_text = response_text[4:]
        response_text = response_text.strip()
    
    # Parsear JSON
    try:
        user_data = json.loads(response_text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Error parseando JSON: {e}\nRespuesta: {response_text}")
    
    # Validación básica
    required_fields = USER_PROFILE_SCHEMA['required']
    missing_fields = [f for f in required_fields if f not in user_data or user_data[f] is None]
    
    if missing_fields:
        raise ValueError(f"Faltan campos requeridos: {missing_fields}")
    
    return user_data

# Prueba
test_text = """Hola, tengo 45 años, soy mujer. 
Mido 1.65 metros y peso 75 kilos. 
Mi cintura mide 90 cm.
Duermo unas 6 horas por noche.
Fumo 10 cigarrillos al día.
Hago ejercicio 2 días a la semana.
Como 3 porciones de frutas y verduras al día."""

extracted_data = extract_user_data_from_text(test_text)
print("\n✅ DATOS EXTRAÍDOS:")
print(json.dumps(extracted_data, indent=2, ensure_ascii=False))



