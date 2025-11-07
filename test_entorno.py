#!/usr/bin/env python3
"""
Script de prueba para verificar que el entorno virtual esté configurado correctamente
"""

import sys
from pathlib import Path

print("="*70)
print("🧪 PRUEBA DEL ENTORNO VIRTUAL - Hackathon Salud NHANES")
print("="*70)
print()

# 1. Verificar Python
print(f"✅ Python versión: {sys.version}")
print(f"   Ejecutable: {sys.executable}")
print()

# 2. Verificar librerías principales
print("📦 Verificando librerías instaladas...")
try:
    import pandas as pd
    print(f"   ✅ pandas {pd.__version__}")
except ImportError as e:
    print(f"   ❌ pandas: {e}")
    sys.exit(1)

try:
    import numpy as np
    print(f"   ✅ numpy {np.__version__}")
except ImportError as e:
    print(f"   ❌ numpy: {e}")
    sys.exit(1)

try:
    import sklearn
    print(f"   ✅ scikit-learn {sklearn.__version__}")
except ImportError as e:
    print(f"   ❌ scikit-learn: {e}")
    sys.exit(1)

try:
    import xgboost
    print(f"   ✅ xgboost {xgboost.__version__}")
except ImportError as e:
    print(f"   ❌ xgboost: {e}")
    sys.exit(1)

try:
    import openai
    print(f"   ✅ openai {openai.__version__}")
except ImportError as e:
    print(f"   ❌ openai: {e}")
    sys.exit(1)

try:
    import fastapi
    print(f"   ✅ fastapi {fastapi.__version__}")
except ImportError as e:
    print(f"   ❌ fastapi: {e}")
    sys.exit(1)

try:
    import streamlit
    print(f"   ✅ streamlit {streamlit.__version__}")
except ImportError as e:
    print(f"   ❌ streamlit: {e}")
    sys.exit(1)

try:
    from rank_bm25 import BM25Okapi
    print(f"   ✅ rank-bm25")
except ImportError as e:
    print(f"   ❌ rank-bm25: {e}")
    sys.exit(1)

print()

# 3. Verificar capacidad de leer archivos SAS
print("📊 Verificando capacidad de leer archivos .XPT (SAS)...")
if hasattr(pd, 'read_sas'):
    print("   ✅ pandas.read_sas() disponible")
else:
    print("   ⚠️  pandas.read_sas() NO disponible")
    print("   💡 Instala: pip install pyreadstat")
print()

# 4. Verificar scripts de conversión
print("🔧 Verificando scripts de conversión...")
try:
    from nhanes_data_converter import convert_xpt_to_csv, download_full_cycle
    print("   ✅ nhanes_data_converter.py importado correctamente")
except ImportError as e:
    print(f"   ⚠️  nhanes_data_converter.py: {e}")

try:
    from convertir_nhanes import convertir_xpt_a_csv
    print("   ✅ convertir_nhanes.py importado correctamente")
except ImportError as e:
    print(f"   ⚠️  convertir_nhanes.py: {e}")
print()

# 5. Verificar estructura de directorios
print("📁 Verificando estructura de directorios...")
base_dir = Path('.')
dirs_required = ['data', 'kb', 'models']
for dir_name in dirs_required:
    dir_path = base_dir / dir_name
    if dir_path.exists():
        print(f"   ✅ {dir_name}/ existe")
    else:
        print(f"   ⚠️  {dir_name}/ no existe (se creará automáticamente)")
        dir_path.mkdir(exist_ok=True)
        print(f"   ✅ {dir_name}/ creado")
print()

# 6. Verificar archivos de datos
print("📂 Verificando archivos de datos...")
data_dir = Path('data')
xpt_files = list(data_dir.glob('*.XPT')) + list(data_dir.glob('*.xpt'))
csv_files = list(data_dir.glob('*.csv'))

if xpt_files:
    print(f"   ✅ Encontrados {len(xpt_files)} archivo(s) .XPT:")
    for f in xpt_files[:5]:  # Mostrar solo los primeros 5
        print(f"      - {f.name}")
    if len(xpt_files) > 5:
        print(f"      ... y {len(xpt_files) - 5} más")
else:
    print("   ⚠️  No hay archivos .XPT en ./data/")
    print("   💡 Descarga desde: https://wwwn.cdc.gov/nchs/nhanes/Default.aspx")

if csv_files:
    print(f"   ✅ Encontrados {len(csv_files)} archivo(s) .CSV:")
    for f in csv_files[:5]:  # Mostrar solo los primeros 5
        print(f"      - {f.name}")
    if len(csv_files) > 5:
        print(f"      ... y {len(csv_files) - 5} más")
else:
    print("   ⚠️  No hay archivos .CSV en ./data/")
    print("   💡 Convierte los archivos .XPT usando: python convertir_nhanes.py")
print()

# 7. Prueba de lectura de CSV (si existe)
if csv_files:
    print("🧪 Prueba de lectura de CSV...")
    test_file = csv_files[0]
    try:
        df = pd.read_csv(test_file, nrows=5)
        print(f"   ✅ Leído: {test_file.name}")
        print(f"      Registros (muestra): {len(df)}")
        print(f"      Columnas: {len(df.columns)}")
        if 'SEQN' in df.columns:
            print(f"      ✅ Columna SEQN encontrada")
        else:
            print(f"      ⚠️  Columna SEQN NO encontrada")
    except Exception as e:
        print(f"   ❌ Error leyendo {test_file.name}: {e}")
else:
    print("   ⏭️  No hay CSVs para probar")
print()

# 8. Resumen final
print("="*70)
print("✅ PRUEBA COMPLETADA")
print("="*70)
print()
print("💡 Próximos pasos:")
print("   1. Si no tienes datos, descarga archivos .XPT desde NHANES")
print("   2. Convierte .XPT a CSV: python convertir_nhanes.py")
print("   3. Abre el notebook: jupyter notebook GUIA_HACKATHON_SALUD_NHANES_3.ipynb")
print("   4. Ejecuta las celdas paso a paso")
print()

