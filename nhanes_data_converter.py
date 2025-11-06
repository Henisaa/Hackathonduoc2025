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

# URLs base de NHANES
NHANES_BASE_URL = "https://wwwn.cdc.gov/nchs/nhanes/"

# Ciclos disponibles en NHANES
NHANES_CYCLES = {
    '2007-2008': '2007-2008',
    '2009-2010': '2009-2010',
    '2011-2012': '2011-2012',
    '2013-2014': '2013-2014',
    '2015-2016': '2015-2016',
    '2017-2018': '2017-2018'
}

# Módulos disponibles (pueden variar por ciclo)
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
# NUEVO: FUSIONAR GLU + GHB → LAB
# ===============================================================
def merge_glu_ghb_to_lab(cycle, output_dir='./data'):
    """
    Fusiona los archivos GLU_XXXX_XXXX.csv y GHB_XXXX_XXXX.csv
    en un único LAB_XXXX_XXXX.csv compatible con el pipeline.
    """
    data_path = Path(output_dir)
    cycle_underscore = cycle.replace('-', '_')

    glu_path = data_path / f"GLU_{cycle_underscore}.csv"
    ghb_path = data_path / f"GHB_{cycle_underscore}.csv"
    lab_path = data_path / f"LAB_{cycle_underscore}.csv"

    if not glu_path.exists() and not ghb_path.exists():
        print(f"⚠️ No existen archivos GLU ni GHB para {cycle}")
        return None

    print(f"\n🔄 Fusionando archivos de laboratorio para {cycle}...")
    df_glu = pd.read_csv(glu_path) if glu_path.exists() else pd.DataFrame()
    df_ghb = pd.read_csv(ghb_path) if ghb_path.exists() else pd.DataFrame()

    if not df_glu.empty and not df_ghb.empty:
        df_lab = pd.merge(df_glu, df_ghb, on='SEQN', how='outer')
        print(f"   ✓ Fusionado: {len(df_lab):,} registros")
    else:
        df_lab = df_glu if not df_glu.empty else df_ghb
        print(f"   ⚠️ Solo se encontró un archivo de laboratorio ({len(df_lab):,} registros)")

    df_lab.to_csv(lab_path, index=False)
    print(f"   💾 Guardado como {lab_path.name}")
    return str(lab_path)


# ===============================================================
# MAIN
# ===============================================================
if __name__ == "__main__":
    print("="*70)
    print("NHANES Data Converter")
    print("="*70)
    print("Este script convierte archivos NHANES (.XPT) a CSV y fusiona LABs.\n")

    cycle = '2007-2008'  # puedes cambiar el ciclo aquí
    print(f"📥 Descargando ciclo {cycle}")
    print("   (modifica el valor de 'cycle' si deseas otro periodo)\n")

    # Ejemplo de uso: descarga (si las URLs funcionan)
    # download_full_cycle(cycle)

    # Fusión automática de GLU + GHB → LAB
    merge_glu_ghb_to_lab(cycle)

    print("\n✅ Proceso completado.")
