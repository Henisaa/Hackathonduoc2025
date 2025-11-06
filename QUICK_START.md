# 🚀 QUICK START - Hackathon Salud NHANES

## ⚡ Inicio Rápido (5 minutos)

### 1. Clonar o descargar el repositorio

```bash
git clone <url-del-repo>
cd duoc_hackaton
```

### 2. Crear y activar entorno virtual

```bash
# Crear entorno virtual
python -m venv venv

# Activar (macOS/Linux)
source venv/bin/activate

# Activar (Windows)
venv\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip3 install -r requirements.txt
```

### 4. Verificar que todo funciona

```bash
python3 test_entorno.py
```

### 5. Obtener datos

**Opción A - Descarga automática (intentar primero):**

```bash
# Intentar descarga automática
python3 descargar_nhanes.py --cycle 2017-2018 --module DEMO

# O descargar múltiples módulos
python descargar_nhanes.py --cycle 2017-2018 --module DEMO EXAM LAB
```

**⚠️ Si la descarga automática falla** (común por protecciones del sitio CDC), el script te dará instrucciones claras.

**Opción B - Descarga manual (si falla la automática):**

1. Ve a: https://wwwn.cdc.gov/nchs/nhanes/Default.aspx
2. Selecciona ciclo: 2017-2018
3. Descarga: DEMO_J.XPT, EXAM_J.XPT, LAB_J.XPT
4. Coloca en: `./data/`

### 6. Convertir a CSV

```bash
python3 convertir_nhanes.py
```

### 7. Probar con datos

```bash
python3 test_datos.py
```

### 8. Abrir notebook guía

```bash
jupyter notebook GUIA_HACKATHON_SALUD_NHANES_3.ipynb
```

---

## ✅ Checklist de Verificación

Antes de empezar a trabajar:

- [ ] Entorno virtual creado y activado
- [ ] Dependencias instaladas (`pip install -r requirements.txt`)
- [ ] `python test_entorno.py` ejecutado sin errores
- [ ] Datos descargados (al menos un ciclo)
- [ ] Datos convertidos a CSV (`python convertir_nhanes.py`)
- [ ] `python test_datos.py` ejecutado sin errores
- [ ] Notebook guía abierto y funcionando

---

## 📚 Guías Detalladas

- **`README.md`**: Documentación completa del proyecto
- **`ACTIVAR_ENTORNO.md`**: Guía detallada del entorno virtual
- **`CONVERSION_DATOS_NHANES.md`**: Guía completa de obtención y conversión de datos
- **`guia.md`**: Guía rápida de referencia con puntos críticos

---

## 🆘 Problemas Comunes

### Error: "No module named 'pandas'"
**Solución**: Asegúrate de que el entorno virtual esté activado:
```bash
source venv/bin/activate
```

### Error: "No se encuentran archivos .XPT"
**Solución**: Descarga manualmente desde: https://wwwn.cdc.gov/nchs/nhanes/Default.aspx

### Error: "pandas.read_sas() no funciona"
**Solución**: 
```bash
pip install pyreadstat
```

---

**¡Éxito en el hackathon! 🚀**

