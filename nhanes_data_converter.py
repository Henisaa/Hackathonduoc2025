"""
NHANES Data Converter - Descarga y conversión de datos NHANES
=======================================================================
Convierte los archivos .XPT de NHANES (SAS Transport) a CSV
y fusiona automáticamente los módulos de laboratorio GLU + GHB → LAB.
"""

import pandas as pd
from pathlib import Path
import urllib.request
import warnings

warnings.filterwarnings('ignore')

# ===============================================================
# CONFIGURACIÓN DE CICLOS
# ===============================================================
NHANES_BASE_URL = "https://wwwn.cdc.gov/nchs/nhanes/"

CYCLE_TO_LETTER = {
    "2007-2008": "E",
    "2009-2010": "F",
    "2011-2012": "G",
    "2013-2014": "H",
    "2015-2016": "I",
    "2017-2018": "J"
}

MODULES = {
    'DEMO': 'Demographics',
    'EXAM': 'Examination',
    'LAB': 'Laboratory',
    'QUEST': 'Questionnaire',
    'DIET': 'Dietary'
}

# ===============================================================
# DESCARGA Y CONVERSIÓN DE ARCHIVOS
# ===============================================================
def download_nhanes_file(cycle, module, output_dir='./data'):
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    cycle_underscore = cycle.replace('-', '_')
    filename_xpt = f"{module}_{cycle_underscore}.XPT"
    filename_csv = f"{module}_{cycle_underscore}.csv"
    filepath_xpt = Path(output_dir) / filename_xpt
    filepath_csv = Path(output_dir) / filename_csv

    if filepath_csv.exists():
        print(f"✓ {filename_csv} ya existe, omitiendo descarga")
        return str(filepath_csv)

    url = f"{NHANES_BASE_URL}{cycle}/{filename_xpt}"
    try:
        print(f"📥 Descargando {filename_xpt}...")
        urllib.request.urlretrieve(url, filepath_xpt)
        print(f"   ✓ Descargado: {filepath_xpt}")
    except Exception as e:
        print(f"   ⚠️ ERROR descargando: {e}")
        print(f"   💡 Descarga manual recomendada desde:")
        print(f"      https://wwwn.cdc.gov/nchs/nhanes/{cycle}/")
        return None

    try:
        print(f"🔄 Convirtiendo {filename_xpt} a CSV...")
        df = pd.read_sas(filepath_xpt, encoding='utf-8')
        df.to_csv(filepath_csv, index=False)
        print(f"   ✓ Convertido: {filepath_csv}")
        print(f"   📊 Registros: {len(df):,}, Columnas: {len(df.columns)}")
        return str(filepath_csv)
    except Exception as e:
        print(f"   ⚠️ ERROR convirtiendo: {e}")
        return None

# ===============================================================
# CONVERTIR MANUALMENTE ARCHIVOS XPT A CSV
# ===============================================================
def convert_xpt_to_csv(xpt_file, output_dir=None):
    xpt_path = Path(xpt_file)
    if not xpt_path.exists():
        print(f"⚠️ Archivo no encontrado: {xpt_file}")
        return None
    if output_dir is None:
        output_dir = xpt_path.parent
    else:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

    csv_file = output_dir / f"{xpt_path.stem}.csv"
    try:
        print(f"🔄 Convirtiendo {xpt_path.name} a CSV...")
        df = pd.read_sas(xpt_path, encoding='utf-8')
        df.to_csv(csv_file, index=False)
        print(f"   ✓ Convertido: {csv_file}")
        print(f"   📊 Registros: {len(df):,}, Columnas: {len(df.columns)}")
        return str(csv_file)
    except Exception as e:
        print(f"   ⚠️ ERROR: {e}")
        return None

# ===============================================================
# DESCARGAR UN CICLO COMPLETO (OPCIONAL)
# ===============================================================
def download_full_cycle(cycle, modules=['DEMO', 'EXAM', 'LAB', 'QUEST'], output_dir='./data'):
    print(f"\n{'='*70}")
    print(f"📦 Descargando ciclo {cycle}")
    print(f"{'='*70}")
    results = {}
    for module in modules:
        print(f"\n📁 Módulo: {module} ({MODULES.get(module, module)})")
        csv_file = download_nhanes_file(cycle, module, output_dir)
        results[module] = csv_file

    print(f"\n{'='*70}")
    print(f"✅ Resumen del ciclo {cycle}:")
    print(f"{'='*70}")
    for module, csv_file in results.items():
        if csv_file:
            print(f"  ✓ {module}: {Path(csv_file).name}")
        else:
            print(f"  ✗ {module}: No descargado")
    return results

# ===============================================================
# FUSIÓN DE LABORATORIOS GLU + GHB → LAB
# ===============================================================
def merge_glu_ghb_to_lab(cycle, output_dir='./data'):
    """
    Fusiona los archivos GLU + GHB → LAB para el ciclo indicado.
    Soporta nombres por año (GLU_2007_2008.csv) o por letra (GLU_E.csv).
    """
    data_path = Path(output_dir)
    cycle_underscore = cycle.replace('-', '_')
    letter = CYCLE_TO_LETTER.get(cycle, '')

    # Buscar posibles rutas
    glu_paths = [
        data_path / f"GLU_{cycle_underscore}.csv",
        data_path / f"GLU_{letter}.csv"
    ]
    ghb_paths = [
        data_path / f"GHB_{cycle_underscore}.csv",
        data_path / f"GHB_{letter}.csv"
    ]

    glu_file = next((p for p in glu_paths if p.exists()), None)
    ghb_file = next((p for p in ghb_paths if p.exists()), None)
    lab_file = data_path / f"LAB_{cycle_underscore}.csv"

    if not glu_file and not ghb_file:
        print(f"⚠️ No existen archivos GLU ni GHB para {cycle}")
        return None

    print(f"\n🔄 Fusionando archivos de laboratorio para {cycle}...")

    df_glu = pd.read_csv(glu_file) if glu_file else pd.DataFrame()
    df_ghb = pd.read_csv(ghb_file) if ghb_file else pd.DataFrame()

    if not df_glu.empty and not df_ghb.empty:
        df_lab = pd.merge(df_glu, df_ghb, on='SEQN', how='outer')
        print(f"   ✓ Fusionado: {len(df_lab):,} registros")
    else:
        df_lab = df_glu if not df_glu.empty else df_ghb
        print(f"   ⚠️ Solo se encontró un archivo de laboratorio ({len(df_lab):,} registros)")

    df_lab.to_csv(lab_file, index=False)
    print(f"   💾 Guardado como {lab_file.name}")
    return str(lab_file)

# ===============================================================
# MAIN
# ===============================================================
if __name__ == "__main__":
    print("="*70)
    print("NHANES Data Converter")
    print("="*70)
    print("Convierte y fusiona datos NHANES GLU + GHB → LAB\n")

    # Ejecutar para todos los ciclos relevantes
    for cycle in CYCLE_TO_LETTER.keys():
        merge_glu_ghb_to_lab(cycle)

    print("\n✅ Proceso completado con éxito.")
