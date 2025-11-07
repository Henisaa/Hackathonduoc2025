#!/usr/bin/env python3
"""
Script simple para convertir archivos .XPT de NHANES a CSV

Uso:
    python convertir_nhanes.py

Este script busca todos los archivos .XPT en ./data/ y los convierte a CSV.
"""

import pandas as pd
from pathlib import Path
import sys

def convertir_xpt_a_csv(xpt_file, output_dir=None):
    """
    Convierte un archivo .XPT a CSV.
    
    Args:
        xpt_file: Ruta al archivo .XPT
        output_dir: Directorio de salida (opcional)
    
    Returns:
        bool: True si se convirtió exitosamente
    """
    xpt_path = Path(xpt_file)
    
    if not xpt_path.exists():
        print(f"❌ Archivo no encontrado: {xpt_file}")
        return False
    
    if output_dir is None:
        output_dir = xpt_path.parent
    else:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
    
    csv_file = output_dir / f"{xpt_path.stem}.csv"
    
    # Si ya existe el CSV, preguntar si sobrescribir
    if csv_file.exists():
        print(f"⚠️  Ya existe: {csv_file.name}")
        respuesta = input("   ¿Sobrescribir? (s/n): ").lower()
        if respuesta != 's':
            print(f"   ⏭️  Omitiendo...")
            return False
    
    try:
        print(f"🔄 Convirtiendo: {xpt_path.name} → {csv_file.name}")
        
        # Leer archivo .XPT
        df = pd.read_sas(xpt_path, encoding='utf-8')
        
        # Guardar como CSV
        df.to_csv(csv_file, index=False)
        
        print(f"   ✅ Listo: {len(df):,} registros, {len(df.columns)} columnas")
        
        # Verificar que tenga SEQN
        if 'SEQN' in df.columns:
            print(f"   ✅ Columna SEQN encontrada")
        else:
            print(f"   ⚠️  ADVERTENCIA: Columna SEQN no encontrada")
        
        return True
        
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        return False


def main():
    """Función principal"""
    print("="*70)
    print("NHANES Data Converter - Convertir .XPT a CSV")
    print("="*70)
    print()
    
    # Buscar archivos .XPT en ./data/
    data_dir = Path('./data')
    data_dir.mkdir(exist_ok=True)
    
    xpt_files = list(data_dir.glob('*.XPT')) + list(data_dir.glob('*.xpt'))
    
    if not xpt_files:
        print("⚠️  No se encontraron archivos .XPT en ./data/")
        print()
        print("📥 INSTRUCCIONES:")
        print("1. Descarga los archivos .XPT desde:")
        print("   https://wwwn.cdc.gov/nchs/nhanes/Default.aspx")
        print()
        print("2. Coloca los archivos .XPT en ./data/")
        print()
        print("3. Ejecuta este script de nuevo")
        print()
        print("Ejemplo de archivos esperados:")
        print("  ./data/DEMO_2007_2008.XPT")
        print("  ./data/EXAM_2007_2008.XPT")
        print("  ./data/LAB_2007_2008.XPT")
        print("  ./data/QUEST_2007_2008.XPT")
        sys.exit(1)
    
    print(f"✅ Encontrados {len(xpt_files)} archivo(s) .XPT:")
    for xpt_file in xpt_files:
        print(f"   - {xpt_file.name}")
    print()
    
    # Convertir cada archivo
    exitosos = 0
    for xpt_file in xpt_files:
        if convertir_xpt_a_csv(xpt_file):
            exitosos += 1
        print()
    
    # Resumen
    print("="*70)
    print(f"✅ Resumen: {exitosos}/{len(xpt_files)} archivos convertidos")
    print("="*70)
    
    # Verificar archivos CSV creados
    csv_files = list(data_dir.glob('*.csv'))
    if csv_files:
        print(f"\n📄 Archivos CSV creados ({len(csv_files)}):")
        for csv_file in sorted(csv_files):
            print(f"   ✅ {csv_file.name}")
    
    print()
    print("💡 Si todos los archivos están convertidos, puedes continuar con el notebook guía")


if __name__ == "__main__":
    main()

