#!/usr/bin/env python3
"""
Script para descargar datos de NHANES desde el sitio oficial

Este script descarga archivos .XPT de NHANES usando la estructura de URL correcta.
Si la descarga automática falla, proporciona instrucciones claras para descarga manual.

Uso:
    python descargar_nhanes.py --cycle 2017-2018 --module DEMO
    python descargar_nhanes.py --ciclo 2017-2018 --modulo DEMO EXAM LAB
"""

import argparse
import sys
from pathlib import Path
import urllib.request
import urllib.error
import requests
from typing import Optional
import time

# Mapeo de ciclos a letras de archivo (usadas en nombres de archivo)
CYCLE_TO_LETTER = {
    '2007-2008': 'E',
    '2009-2010': 'F',
    '2011-2012': 'G',
    '2013-2014': 'H',
    '2015-2016': 'I',
    '2017-2018': 'J'
}

MODULE_NAMES = {
    'DEMO': 'Demographics',
    'EXAM': 'Examination',
    'LAB': 'Laboratory',
    'QUEST': 'Questionnaire',
    'DIET': 'Dietary'
}


def download_with_urllib(url: str, output_file: Path) -> bool:
    """Intenta descargar usando urllib con headers apropiados."""
    try:
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
        req.add_header('Accept', '*/*')
        req.add_header('Accept-Language', 'en-US,en;q=0.9')
        req.add_header('Referer', 'https://wwwn.cdc.gov/nchs/nhanes/Default.aspx')
        
        with urllib.request.urlopen(req, timeout=30) as response:
            content = response.read()
            
            # Verificar que no es HTML
            if content.startswith(b'<!DOCTYPE') or content.startswith(b'<html'):
                return False
            
            # Guardar archivo
            with open(output_file, 'wb') as f:
                f.write(content)
            
            return True
    except Exception:
        return False


def download_with_requests(url: str, output_file: Path) -> bool:
    """Intenta descargar usando requests con headers apropiados."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://wwwn.cdc.gov/nchs/nhanes/Default.aspx',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        }
        
        response = requests.get(url, headers=headers, timeout=30, stream=True)
        response.raise_for_status()
        
        content = response.content
        
        # Verificar que no es HTML
        if content.startswith(b'<!DOCTYPE') or content.startswith(b'<html'):
            return False
        
        # Verificar tamaño mínimo (archivos XPT son al menos unos KB)
        if len(content) < 1000:
            return False
        
        # Guardar archivo
        with open(output_file, 'wb') as f:
            f.write(content)
        
        return True
    except Exception:
        return False


def download_nhanes_file(cycle: str, module: str, output_dir: Path = Path('./data')) -> Optional[Path]:
    """
    Intenta descargar un archivo de NHANES usando la estructura de URL correcta.
    
    La URL correcta sigue el patrón:
    https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/{YEAR}/DataFiles/{MODULE}_{LETTER}.xpt
    
    Donde:
    - YEAR es el primer año del ciclo (ej: "2017" para "2017-2018")
    - MODULE es el módulo (ej: "DEMO")
    - LETTER es la letra del ciclo (ej: "J" para "2017-2018")
    
    Args:
        cycle: Ciclo de NHANES (ej: '2017-2018')
        module: Módulo (ej: 'DEMO')
        output_dir: Directorio donde guardar
    
    Returns:
        Path del archivo descargado, o None si falla
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Validar ciclo
    letter = CYCLE_TO_LETTER.get(cycle)
    if not letter:
        print(f"❌ Ciclo {cycle} no soportado")
        print(f"   Ciclos válidos: {', '.join(CYCLE_TO_LETTER.keys())}")
        return None
    
    # Construir nombre de archivo (usando letra del ciclo)
    # Los archivos se nombran como: MODULE_LETTER.xpt (ej: DEMO_J.xpt)
    filename = f"{module}_{letter}.xpt"
    output_file = output_dir / filename
    
    # Si ya existe, no descargar de nuevo
    if output_file.exists():
        print(f"✅ Archivo ya existe: {filename}")
        print(f"   Tamaño: {output_file.stat().st_size / (1024*1024):.2f} MB")
        return output_file
    
    # Extraer el primer año del ciclo para la URL
    # Ejemplo: "2017-2018" -> "2017"
    year = cycle.split('-')[0]
    
    
    # Construir URL correcta basada en el patrón real del sitio
    # Patrón: https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/{YEAR}/DataFiles/{filename}
    url = f"https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/{year}/DataFiles/{filename}"
    
    # URLs alternativas por si la principal cambia (fallback)
    urls_to_try = [
        url,  # URL principal (correcta)
        f"https://wwwn.cdc.gov/Nchs/Nhanes/{cycle.replace('-', '/')}/{filename}",
        f"https://wwwn.cdc.gov/nchs/nhanes/{cycle.replace('-', '/')}/{filename}",
    ]
    
    print(f"📥 Descargando {filename}")
    print(f"   Ciclo: {cycle} ({MODULE_NAMES.get(module, module)})")
    print(f"   Año en URL: {year}")
    print()
    
    for i, url in enumerate(urls_to_try, 1):
        print(f"   [{i}/{len(urls_to_try)}] Intentando: {url}")
        
        # Intentar con requests primero (más robusto)
        if download_with_requests(url, output_file):
            size = output_file.stat().st_size
            print(f"   ✅ Descarga exitosa!")
            print(f"   📊 Tamaño: {size / (1024*1024):.2f} MB ({size:,} bytes)")
            
            # Verificar que sea un archivo XPT válido
            with open(output_file, 'rb') as f:
                header = f.read(80)
                if b'HEADER RECORD' in header or b'XPORT' in header or (size > 1000 and not header.startswith(b'<!DOCTYPE')):
                    print(f"   ✅ Archivo XPT válido detectado")
                    return output_file
                else:
                    print(f"   ⚠️  Archivo descargado pero no parece ser XPT válido")
                    output_file.unlink()
                    continue
        
        # Intentar con urllib como fallback
        if download_with_urllib(url, output_file):
            size = output_file.stat().st_size
            print(f"   ✅ Descarga exitosa (con urllib)!")
            print(f"   📊 Tamaño: {size / (1024*1024):.2f} MB ({size:,} bytes)")
            
            # Verificar que sea un archivo XPT válido
            with open(output_file, 'rb') as f:
                header = f.read(80)
                if b'HEADER RECORD' in header or b'XPORT' in header or (size > 1000 and not header.startswith(b'<!DOCTYPE')):
                    print(f"   ✅ Archivo XPT válido detectado")
                    return output_file
                else:
                    print(f"   ⚠️  Archivo descargado pero no parece ser XPT válido")
                    output_file.unlink()
                    continue
        
        print(f"   ❌ No se pudo descargar desde esta URL")
        if i < len(urls_to_try):
            time.sleep(1)  # Pequeña pausa entre intentos
    
    # Si todas las URLs fallan, proporcionar instrucciones
    print()
    print("="*70)
    print("⚠️  DESCARGA AUTOMÁTICA FALLÓ")
    print("="*70)
    print()
    print("💡 INSTRUCCIONES PARA DESCARGA MANUAL:")
    print()
    print(f"1. Ve a: https://wwwn.cdc.gov/nchs/nhanes/Default.aspx")
    print(f"2. Selecciona el ciclo: {cycle}")
    print(f"3. Busca el módulo: {MODULE_NAMES.get(module, module)}")
    print(f"4. Descarga el archivo: {filename}")
    print(f"5. Colócalo en: {output_file}")
    print()
    print(f"📋 Información del archivo:")
    print(f"   - Nombre esperado: {filename}")
    print(f"   - Módulo: {MODULE_NAMES.get(module, module)}")
    print(f"   - Ciclo: {cycle}")
    print(f"   - Letra: {letter}")
    print()
    
    return None


def main():
    """Función principal del script."""
    parser = argparse.ArgumentParser(
        description='Descargar archivos .XPT de NHANES desde el sitio oficial',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  # Descargar un módulo
  python descargar_nhanes.py --cycle 2017-2018 --module DEMO
  
  # Descargar múltiples módulos
  python descargar_nhanes.py --cycle 2017-2018 --module DEMO EXAM LAB
  
  # Descargar usando nombres en español
  python descargar_nhanes.py --ciclo 2017-2018 --modulo DEMO EXAM LAB
        """
    )
    
    # Soporte para español e inglés
    parser.add_argument('--cycle', '--ciclo', dest='cycle', required=True,
                       help='Ciclo de NHANES (ej: 2017-2018)')
    parser.add_argument('--module', '--modulo', dest='modules', nargs='+', required=True,
                       help='Módulos a descargar (DEMO, EXAM, LAB, QUEST, DIET)')
    parser.add_argument('--output-dir', '--directorio-salida', dest='output_dir',
                       default='./data', help='Directorio donde guardar archivos')
    
    args = parser.parse_args()
    
    print("="*70)
    print("📥 DESCARGADOR DE DATOS NHANES")
    print("="*70)
    print()
    
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Validar ciclo
    if args.cycle not in CYCLE_TO_LETTER:
        print(f"❌ Ciclo no válido: {args.cycle}")
        print(f"   Ciclos válidos: {', '.join(CYCLE_TO_LETTER.keys())}")
        sys.exit(1)
    
    # Validar módulos
    valid_modules = set(MODULE_NAMES.keys())
    invalid_modules = [m for m in args.modules if m.upper() not in valid_modules]
    if invalid_modules:
        print(f"❌ Módulos no válidos: {', '.join(invalid_modules)}")
        print(f"   Módulos válidos: {', '.join(valid_modules)}")
        sys.exit(1)
    
    # Descargar cada módulo
    downloaded = []
    failed = []
    
    for module in args.modules:
        module = module.upper()
        result = download_nhanes_file(args.cycle, module, output_dir)
        if result:
            downloaded.append(result)
        else:
            failed.append(module)
        print()
    
    # Resumen
    print("="*70)
    print("📊 RESUMEN")
    print("="*70)
    print()
    
    if downloaded:
        print(f"✅ Archivos descargados exitosamente: {len(downloaded)}")
        for f in downloaded:
            size = f.stat().st_size
            print(f"   - {f.name} ({size / (1024*1024):.2f} MB)")
        print()
        print("💡 Próximo paso: Convierte a CSV usando:")
        print("   python convertir_nhanes.py")
    
    if failed:
        print(f"⚠️  Archivos que requieren descarga manual: {len(failed)}")
        for m in failed:
            print(f"   - {m}")
        print()
        print("💡 Descarga manual desde:")
        print("   https://wwwn.cdc.gov/nchs/nhanes/Default.aspx")
    
    print()
    print("="*70)


if __name__ == "__main__":
    main()

