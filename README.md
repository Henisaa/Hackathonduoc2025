# 🏥 Hackathon Salud NHANES - Guía y Template

**Duoc UC 2025 - Sistema híbrido ML + LLM para predicción de riesgo cardiometabólico**

Este repositorio contiene una guía completa y código template para el hackathon de salud preventiva usando datos NHANES.

## 📋 Contenido del Repositorio

- **`GUIA_HACKATHON_SALUD_NHANES_3.ipynb`**: Notebook Jupyter con guía paso a paso completa
- **`guia.md`**: Guía rápida en Markdown con puntos clave
- **`Desafio_Salud_NHANES_2025_duoc.pdf`**: Documento oficial del desafío con rúbrica
- **`requirements.txt`**: Dependencias Python necesarias
- **`.gitignore`**: Configuración para Git

## 🚀 Quick Start

**📖 Para inicio rápido detallado (5 minutos), ver: `QUICK_START.md`**

### 1. Clonar o descargar el repositorio

```bash
git clone <url-del-repo>
cd duoc_hackaton
```

### 2. Crear entorno virtual (recomendado)

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# En macOS/Linux:
source venv/bin/activate
# En Windows:
venv\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. ⚠️ IMPORTANTE: Obtener y convertir datos NHANES

**Los datos NHANES NO vienen en CSV directamente**. Necesitas descargarlos y convertirlos.

**Opción A - Descarga Automática (Intentar primero):**

```bash
# Activar entorno virtual
source venv/bin/activate

# Descargar un archivo de prueba
python descargar_nhanes.py --cycle 2017-2018 --module DEMO

# Descargar múltiples módulos
python descargar_nhanes.py --cycle 2017-2018 --module DEMO EXAM LAB
```

**Si la descarga automática falla, usa la Opción B (descarga manual).**

**Opción B - Descarga Manual:**
1. Ve a: https://wwwn.cdc.gov/nchs/nhanes/Default.aspx
2. Descarga los archivos .XPT para cada ciclo
3. Colócalos en `./data/`

**Opción C - Convertir .XPT a CSV (cuando tengas los archivos):**

```bash
python convertir_nhanes.py
```

O usando Python:

```python
from nhanes_data_converter import convert_xpt_to_csv
from pathlib import Path

# Convertir todos los .XPT en ./data/
for xpt_file in Path('./data').glob('*.XPT'):
    convert_xpt_to_csv(xpt_file)
```

**📖 Ver guía completa**: `CONVERSION_DATOS_NHANES.md` o `QUICK_START.md`

### 5. Abrir el notebook guía

```bash
jupyter notebook GUIA_HACKATHON_SALUD_NHANES_3.ipynb
```

O si usas JupyterLab:

```bash
jupyter lab GUIA_HACKATHON_SALUD_NHANES_3.ipynb
```

## 📚 Estructura del Proyecto

```
duoc_hackaton/
├── GUIA_HACKATHON_SALUD_NHANES_3.ipynb  # Guía completa paso a paso
├── guia.md                               # Guía rápida de referencia
├── Desafio_Salud_NHANES_2025_duoc.pdf   # Documento del desafío
├── requirements.txt                      # Dependencias Python
├── .gitignore                           # Archivos a ignorar en Git
├── README.md                            # Este archivo
├── descargar_nhanes.py                  # Script para descargar datos .XPT automáticamente
├── nhanes_data_converter.py             # Script completo para convertir datos .XPT a CSV
├── convertir_nhanes.py                  # Script simple para conversión rápida
├── CONVERSION_DATOS_NHANES.md           # Guía completa de obtención y conversión de datos
├── test_entorno.py                      # Script para probar el entorno
├── test_datos.py                         # Script para probar la carga de datos
├── data/                                # Datos NHANES (agregar aquí)
├── kb/                                  # Base de conocimiento para RAG
└── models/                              # Modelos entrenados (generados)
```

## 🎯 Cómo Usar Esta Guía

### Para principiantes:

1. **Lee primero** `guia.md` para entender los conceptos clave
2. **Revisa** el PDF del desafío para entender la rúbrica
3. **Sigue** el notebook `GUIA_HACKATHON_SALUD_NHANES_3.ipynb` celda por celda
4. **Ejecuta** cada celda y entiende qué hace antes de continuar

### Para avanzados:

1. **Usa** el notebook como template y referencia rápida
2. **Adapta** el código según tus necesidades
3. **Consulta** `guia.md` para recordatorios rápidos
4. **Revisa** la rúbrica en el PDF para asegurar cumplir todos los requisitos

## 📊 Checklist de Entregables

### Funcionalidad (50%):
- [ ] Modelo ML con AUROC ≥ 0.80
- [ ] API FastAPI con `/predict` y `/coach`
- [ ] App Streamlit/Gradio deployada en HF Spaces
- [ ] Validación temporal sin fuga de datos
- [ ] Métricas de fairness por subgrupos

### LLM y RAG (25%):
- [ ] Extractor NL→JSON 100% válido
- [ ] Coach con RAG usando citas a `/kb` local
- [ ] Guardrails implementados (disclaimer, umbrales)

### Documentación (30%):
- [ ] README completo
- [ ] Reporte técnico 2-3 páginas
- [ ] Bitácora de prompts

### Presentación (20%):
- [ ] Slides preparadas (10 min)
- [ ] Demo funcional
- [ ] Screenshots de backup

## 🔑 Variables de Entorno Necesarias

Crea un archivo `.env` (NO versionarlo) con:

```bash
OPENAI_API_KEY=tu-api-key-aqui
```

**⚠️ IMPORTANTE**: Nunca subas tu `.env` a Git. Está en `.gitignore`.

## 📖 Recursos Adicionales

- **NHANES Variables**: https://wwwn.cdc.gov/nchs/nhanes/search/
- **XGBoost Docs**: https://xgboost.readthedocs.io/
- **FastAPI Tutorial**: https://fastapi.tiangolo.com/tutorial/
- **Streamlit Docs**: https://docs.streamlit.io/
- **OpenAI API**: https://platform.openai.com/docs/

## ⚠️ Disclaimer

Este sistema NO realiza diagnósticos médicos. Siempre consulta con un profesional de salud.

## 👥 Equipo

[Agregar información del equipo aquí]

## 📄 Licencia

MIT License

---

**¡ÉXITO EN EL HACKATHON! 🚀**

*Última actualización: Noviembre 2025*

