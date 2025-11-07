# 🐍 Guía de Activación del Entorno Virtual

## ✅ Entorno Virtual Creado y Configurado

El entorno virtual de Python ha sido creado exitosamente en `./venv/` con todas las dependencias instaladas.

---

## 🚀 Cómo Activar el Entorno Virtual

### En macOS/Linux:
```bash
source venv/bin/activate
```

### En Windows:
```bash
venv\Scripts\activate
```

**Indicador visual:** Cuando el entorno está activado, verás `(venv)` al inicio de tu línea de comandos.

---

## 🧪 Pruebas Rápidas

### 1. Verificar que el entorno funciona:
```bash
source venv/bin/activate
python test_entorno.py
```

Este script verifica:
- ✅ Versión de Python
- ✅ Todas las librerías instaladas
- ✅ Capacidad de leer archivos .XPT
- ✅ Scripts de conversión disponibles
- ✅ Estructura de directorios

### 2. Probar carga de datos (cuando tengas CSVs):
```bash
source venv/bin/activate
python test_datos.py
```

Este script verifica:
- ✅ Archivos CSV disponibles
- ✅ Lectura correcta de archivos
- ✅ Presencia de columna SEQN
- ✅ Carga de datos por ciclo

---

## 📦 Instalación de Dependencias (si es necesario)

Si necesitas reinstalar las dependencias:

```bash
source venv/bin/activate
pip install -r requirements.txt
```

---

## 🔧 Scripts Disponibles

### Conversión de datos:
```bash
source venv/bin/activate

# Script simple (recomendado)
python convertir_nhanes.py

# O usando el módulo completo
python -c "from nhanes_data_converter import convert_xpt_to_csv; from pathlib import Path; [convert_xpt_to_csv(f) for f in Path('./data').glob('*.XPT')]"
```

---

## 📓 Trabajar con Jupyter Notebook

### Activar el kernel del entorno virtual:
```bash
source venv/bin/activate
pip install ipykernel
python -m ipykernel install --user --name=venv --display-name "Python (venv)"
```

### Iniciar Jupyter:
```bash
source venv/bin/activate
jupyter notebook GUIA_HACKATHON_SALUD_NHANES_3.ipynb
```

---

## 🎯 Checklist de Verificación

Antes de empezar a trabajar:

- [ ] Entorno virtual activado (`(venv)` visible en terminal)
- [ ] `python test_entorno.py` ejecutado sin errores
- [ ] Archivos .XPT descargados en `./data/` (opcional)
- [ ] Archivos .XPT convertidos a CSV (opcional)
- [ ] `python test_datos.py` ejecutado sin errores (si hay datos)

---

## ❓ Solución de Problemas

### Error: "No module named 'pandas'"
**Solución:** Asegúrate de que el entorno virtual esté activado:
```bash
source venv/bin/activate
```

### Error: "pandas.read_sas() no funciona"
**Solución:** Instala soporte adicional:
```bash
source venv/bin/activate
pip install pyreadstat
```

### Error: "No se encuentran archivos .XPT"
**Solución:** 
1. Descarga archivos desde: https://wwwn.cdc.gov/nchs/nhanes/Default.aspx
2. Colócalos en `./data/`
3. Convierte a CSV: `python convertir_nhanes.py`

---

## 📚 Recursos

- **NHANES Data**: https://wwwn.cdc.gov/nchs/nhanes/Default.aspx
- **Documentación Pandas**: https://pandas.pydata.org/docs/
- **Guía de Conversión**: Ver `CONVERSION_DATOS_NHANES.md`

---

**¡El entorno está listo para trabajar! 🚀**

