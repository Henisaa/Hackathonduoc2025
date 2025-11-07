#!/usr/bin/env python3
"""
Script para probar la carga de datos NHANES
Ejecuta este script después de convertir los archivos .XPT a CSV
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np

# Añadir el directorio actual al path para importar funciones del notebook
sys.path.insert(0, str(Path(__file__).parent))

print("="*70)
print("🧪 PRUEBA DE CARGA DE DATOS NHANES")
print("="*70)
print()

# Verificar que existen archivos CSV
data_dir = Path('./data')
csv_files = list(data_dir.glob('*.csv'))

if not csv_files:
    print("⚠️  No se encontraron archivos CSV en ./data/")
    print()
    print("📥 INSTRUCCIONES:")
    print("   1. Descarga archivos .XPT desde: https://wwwn.cdc.gov/nchs/nhanes/Default.aspx")
    print("   2. Coloca los archivos .XPT en ./data/")
    print("   3. Convierte usando: python convertir_nhanes.py")
    print()
    sys.exit(1)

print(f"✅ Encontrados {len(csv_files)} archivo(s) CSV")
print()

# Probar lectura de cada archivo
print("📖 Probando lectura de archivos...")
print()

for csv_file in sorted(csv_files):
    try:
        # Leer solo las primeras 100 filas para prueba rápida
        df = pd.read_csv(csv_file, nrows=100)
        
        print(f"✅ {csv_file.name}")
        print(f"   Registros (muestra): {len(df)}")
        print(f"   Columnas: {len(df.columns)}")
        
        # Verificar columna SEQN
        if 'SEQN' in df.columns:
            print(f"   ✅ SEQN encontrado")
            unique_seqn = df['SEQN'].nunique()
            print(f"   SEQN únicos: {unique_seqn}")
        else:
            print(f"   ⚠️  SEQN NO encontrado (esto puede ser un problema)")
        
        # Mostrar primeras columnas
        print(f"   Primeras columnas: {', '.join(df.columns[:5].tolist())}...")
        
    except Exception as e:
        print(f"❌ {csv_file.name}: ERROR")
        print(f"   {e}")
    
    print()

# Probar la función de carga del notebook (si existe)
print("="*70)
print("🔄 Probando función load_nhanes_data...")
print("="*70)
print()

# Intentar cargar datos de entrenamiento
try:
    # Simular la función de carga básica
    cycles = ['2007-2008', '2009-2010', '2011-2012', '2013-2014', '2015-2016']
    
    all_data = []
    for cycle in cycles:
        demo_file = data_dir / f"DEMO_{cycle.replace('-', '_')}.csv"
        if demo_file.exists():
            try:
                demo = pd.read_csv(demo_file, nrows=1000)  # Limitar para prueba
                if 'SEQN' in demo.columns:
                    demo['CYCLE'] = cycle
                    all_data.append(demo)
                    print(f"✅ Cargado: DEMO_{cycle.replace('-', '_')}.csv ({len(demo)} registros)")
                else:
                    print(f"⚠️  {demo_file.name}: No tiene columna SEQN")
            except Exception as e:
                print(f"❌ Error leyendo {demo_file.name}: {e}")
        else:
            print(f"⚠️  No encontrado: DEMO_{cycle.replace('-', '_')}.csv")
    
    if all_data:
        print()
        print(f"✅ Total: {len(all_data)} ciclos cargados")
        
        # Concatenar
        df_test = pd.concat(all_data, ignore_index=True)
        print(f"   Registros totales: {len(df_test):,}")
        print(f"   Columnas totales: {df_test.shape[1]}")
        print()
        
        # Verificar distribución por ciclo
        if 'CYCLE' in df_test.columns:
            print("📊 Distribución por ciclo:")
            print(df_test['CYCLE'].value_counts().sort_index())
            print()
        
        # Verificar variables clave
        print("🔑 Variables clave disponibles:")
        key_vars = {
            'Demographics': ['RIDAGEYR', 'RIAGENDR', 'RIDRETH3'],
            'Anthropometry': ['BMXWT', 'BMXHT', 'BMXWAIST', 'BMXBMI'],
            'Blood Pressure': ['BPXSY1', 'BPXSY2', 'BPXDI1', 'BPXDI2'],
            'Laboratory': ['LAB_LBXGH', 'LAB_LBXGLU'],
        }
        
        for module, vars_list in key_vars.items():
            available = [v for v in vars_list if v in df_test.columns]
            if available:
                print(f"   ✅ {module}: {len(available)}/{len(vars_list)} disponibles")
                print(f"      {', '.join(available)}")
            else:
                print(f"   ⚠️  {module}: Ninguna variable disponible")
                print(f"      Esperadas: {', '.join(vars_list)}")
        
    else:
        print()
        print("⚠️  No se pudieron cargar datos de ningún ciclo")
        print("   Verifica que los archivos CSV estén en ./data/ con el formato correcto")
        
except Exception as e:
    print(f"❌ Error en prueba de carga: {e}")
    import traceback
    traceback.print_exc()

print()
print("="*70)
print("✅ PRUEBA DE DATOS COMPLETADA")
print("="*70)
print()
print("💡 Si todo está ✅, puedes continuar con el notebook guía")
print("   jupyter notebook GUIA_HACKATHON_SALUD_NHANES_3.ipynb")
print()

