# 🚨 GUÍA RÁPIDA - HACKATHON SALUD NHANES
## Puntos Críticos y Errores Comunes a Evitar

---

## ⚠️ REGLA #1: ANTI-FUGA DE DATOS (CRÍTICO)

### ❌ NUNCA hacer:
```python
# SI EL LABEL USA A1c/GLUCOSA:
features = ['edad', 'sexo', 'bmi', 'LBXGH']  # ❌ FUGA!
```

### ✅ SIEMPRE hacer:
```python
# Marcar columnas de lab al cargar
lab_cols = [c for c in lab.columns if c != 'SEQN']
lab = lab.rename(columns={c: f'LAB_{c}' for c in lab_cols})

# Validar features
LAB_COLUMNS = [col for col in df.columns if col.startswith('LAB_')]
features = [f for f in candidate_features if not f.startswith('LAB_')]
```

---

## 📊 MANEJO DE DATOS NHANES (LO MÁS DIFÍCIL)

### Estructura básica:
```python
# 1. DEMOGRAPHICS (siempre primero)
demo = pd.read_csv('DEMO_2017_2018.csv')
demo['CYCLE'] = '2017-2018'

# 2. MERGE otros módulos
exam = pd.read_csv('EXAM_2017_2018.csv')
data = demo.merge(exam, on='SEQN', how='left')

# 3. LAB (SOLO para label, renombrar)
lab = pd.read_csv('LAB_2017_2018.csv')
lab = lab.rename(columns={c: f'LAB_{c}' for c in lab.columns if c != 'SEQN'})
data = data.merge(lab, on='SEQN', how='left')
```

### Variables clave NHANES:
- **SEQN**: ID único (clave para merge)
- **RIDAGEYR**: Edad
- **RIAGENDR**: Sexo (1=M, 2=F)
- **BMXWT**: Peso (kg)
- **BMXHT**: Altura (cm)
- **BMXWAIST**: Cintura (cm)
- **BPXSY1/BPXDI1**: Presión arterial
- **LBXGH**: A1c (%)
- **LBXGLU**: Glucosa (mg/dL)

### Valores missing en NHANES:
```python
missing_codes = [7, 9, 77, 99, 777, 999, 7777, 9999, '.', '']
for col in df.select_dtypes(include=[np.number]).columns:
    df[col] = df[col].replace(missing_codes, np.nan)
```

---

## 🎯 VALIDACIÓN TEMPORAL (OBLIGATORIO)

### ❌ NUNCA hacer:
```python
# K-fold aleatorio - PROHIBIDO como única validación
from sklearn.model_selection import KFold
kf = KFold(n_splits=5, shuffle=True)  # ❌
```

### ✅ SIEMPRE hacer:
```python
# Split por ciclos
train_cycles = ['2007-2008', '2009-2010', '2011-2012', '2013-2014', '2015-2016']
test_cycles = ['2017-2018']

df_train = df[df['CYCLE'].isin(train_cycles)]
df_test = df[df['CYCLE'].isin(test_cycles)]
```

---

## 🤖 MODELO ML - QUICK START

### Pipeline mínimo viable:
```python
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

pipeline = Pipeline([
    ('imputer', SimpleImputer(strategy='median')),
    ('scaler', StandardScaler()),
    ('model', LogisticRegression(class_weight='balanced', random_state=42))
])

pipeline.fit(X_train, y_train)
y_pred_proba = pipeline.predict_proba(X_test)[:, 1]
```

### Métricas obligatorias:
```python
from sklearn.metrics import roc_auc_score, average_precision_score, brier_score_loss

auroc = roc_auc_score(y_test, y_pred_proba)  # META: ≥ 0.80
auprc = average_precision_score(y_test, y_pred_proba)
brier = brier_score_loss(y_test, y_pred_proba)  # META: ≤ 0.12

print(f"AUROC: {auroc:.4f} {'✓' if auroc >= 0.80 else '✗'}")
print(f"Brier: {brier:.4f} {'✓' if brier <= 0.12 else '✗'}")
```

---

## 🧠 LLM - EXTRACTOR NL→JSON

### Setup inicial:
```python
from openai import OpenAI
import os

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
```

### Template básico:
```python
prompt = f"""Extrae información del usuario y devuelve JSON válido.

TEXTO: {user_text}

SCHEMA:
{{
  "age": int (18-85),           # REQUERIDO
  "sex": "M" o "F",            # REQUERIDO
  "height_cm": float (120-220), # REQUERIDO
  "weight_kg": float (30-220),  # REQUERIDO
  "waist_cm": float (40-170),   # REQUERIDO
  "sleep_hours": float (3-14),  # Opcional
  "smokes_cig_day": int (0-60), # Opcional
  "days_mvpa_week": int (0-7),  # Opcional
  "fruit_veg_portions_day": float (0-12) # Opcional
}}

Convierte unidades:
- Altura: a centímetros
- Peso: a kilogramos

Devuelve SOLO JSON sin explicaciones.
JSON:"""

response = client.chat.completions.create(
    model="gpt-4o",
    max_tokens=1000,
    messages=[{"role": "user", "content": prompt}],
    response_format={"type": "json_object"}
)

# Extraer respuesta
response_text = response.choices[0].message.content.strip()
```

---

## 📚 LLM - COACH CON RAG

### Reglas de oro:
1. **SIEMPRE usar RAG**: Buscar en /kb antes de generar
2. **NUNCA alucinar**: Solo citar fuentes reales
3. **SIEMPRE incluir disclaimer**: No diagnóstico médico

### Template:
```python
from openai import OpenAI
import os

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# 1. Buscar en KB
relevant_docs = rag.search(f"recomendaciones para {área_riesgo}", top_k=3)

# 2. Construir contexto
context = "\n\n".join([f"=== {doc['filename']} ===\n{doc['content']}" 
                       for doc in relevant_docs])

# 3. Prompt
prompt = f"""Crea plan de 2 semanas para usuario.

PERFIL: {json.dumps(user_data)}
RIESGO: {risk_score:.1%}

CONOCIMIENTO DISPONIBLE:
{context}

REGLAS:
- USA SOLO información del contexto
- CITA fuentes [archivo.md]
- NO inventes información
- Incluye disclaimer

JSON: {{"plan": "...", "sources": ["archivo.md"]}}
"""

# 4. Llamar a OpenAI
response = client.chat.completions.create(
    model="gpt-4o",
    max_tokens=2000,
    messages=[{"role": "user", "content": prompt}],
    response_format={"type": "json_object"}
)

plan_data = json.loads(response.choices[0].message.content.strip())
```

---

## 🚀 API FASTAPI - MÍNIMO VIABLE

```python
from fastapi import FastAPI
from pydantic import BaseModel
import joblib

app = FastAPI()
model = joblib.load('model.pkl')

class UserProfile(BaseModel):
    age: int
    sex: str
    weight_kg: float
    height_cm: float

@app.post("/predict")
def predict(profile: UserProfile):
    # Crear features
    bmi = profile.weight_kg / ((profile.height_cm/100)**2)
    X = pd.DataFrame([{'age': profile.age, 'bmi': bmi}])
    
    # Predecir
    risk_score = model.predict_proba(X)[0, 1]
    
    return {"score": float(risk_score)}

# Ejecutar: uvicorn api_main:app --reload
```

---

## ⚖️ FAIRNESS - ANÁLISIS POR SUBGRUPOS

```python
def analyze_fairness(df, y_true, y_pred_proba):
    results = []
    
    # Por sexo
    for sex in ['M', 'F']:
        mask = df['sex'] == sex
        auroc = roc_auc_score(y_true[mask], y_pred_proba[mask])
        results.append({'group': f'Sex_{sex}', 'auroc': auroc})
    
    # Por edad
    for age_group in ['18-45', '46-60', '60+']:
        # ... similar
    
    # Calcular gap
    gap = max([r['auroc'] for r in results]) - min([r['auroc'] for r in results])
    
    print(f"AUROC Gap: {gap:.4f} {'✓' if gap < 0.05 else '⚠️'}")
    
    return results
```

---

## ⏱️ CRONOGRAMA RECOMENDADO (27 horas)

| Hora | Actividad | Responsable |
|------|-----------|-------------|
| H0-H2 | Setup + carga datos + baseline | ML Lead |
| H2-H6 | Ingeniería features + modelo | ML Lead |
| H6-H10 | Extractor NL→JSON | LLM Lead |
| H10-H16 | Coach RAG + guardrails | LLM Lead |
| H16-H20 | API + App Streamlit | Frontend Lead |
| H20-H22 | Calibración + fairness | ML Lead |
| H22-H24 | Documentación + reporte | Docs Lead |
| H24-H26 | Presentación + slides | Todos |
| H26-H27 | Ensayo + ajustes finales | Todos |

---

## 📋 CHECKLIST ANTES DE PRESENTAR

### Funcionalidad (peso 50%):
- [ ] AUROC ≥ 0.80
- [ ] API /predict funciona
- [ ] API /coach funciona
- [ ] App deployada en HF Spaces
- [ ] Sin fuga de datos verificado

### Documentación (peso 30%):
- [ ] README completo
- [ ] Reporte técnico 2-3 páginas
- [ ] Bitácora de prompts

### Presentación (peso 20%):
- [ ] Slides preparadas (10 min)
- [ ] Demo ensayada
- [ ] Screenshots backup

---

## 🆘 TROUBLESHOOTING RÁPIDO

### Problema: AUROC bajo (<0.75)
**Soluciones:**
1. Verificar anti-fuga de datos
2. Agregar features de interacción (bmi*age)
3. Probar XGBoost con más árboles
4. Verificar imputación de missing

### Problema: Brier Score alto (>0.15)
**Soluciones:**
1. Calibración con CalibratedClassifierCV
2. Ajustar threshold del modelo
3. Verificar desbalance de clases

### Problema: RAG alucina fuentes
**Soluciones:**
1. Validar sources en response
2. Limitar top_k a 3
3. Hacer prompt más estricto

### Problema: API no conecta
**Soluciones:**
```bash
# Verificar puerto
lsof -i :8000

# Matar proceso
kill -9 [PID]

# Reiniciar
uvicorn api_main:app --reload --port 8000
```

---

## 🎯 PUNTOS CLAVE PARA MÁXIMA PUNTUACIÓN

### Rigor técnico ML (30 pts):
- **AUROC ≥ 0.80**: 12 pts - Usa XGBoost con early stopping
- **Brier ≤ 0.12**: 6 pts - Calibra con isotonic regression
- **Validación temporal**: 6 pts - Split por ciclos, NO k-fold
- **Explicabilidad**: 6 pts - SHAP values o feature importance

### LLMs y RAG (25 pts):
- **Extractor 100% válido**: 8 pts - Schema validation + unit conversion
- **Coach con citas**: 9 pts - RAG con BM25, validar sources
- **Guardrails**: 8 pts - Umbrales + disclaimer + derivación

### Producto y UX (25 pts):
- **App funcional**: 10 pts - Streamlit con manejo de errores
- **Export PDF**: 5 pts - fpdf o reportlab
- **Claridad**: 10 pts - Mensajes simples + UX intuitiva

### Reproducibilidad (15 pts):
- **Repo limpio**: 6 pts - requirements.txt + seeds + scripts
- **Documentación**: 5 pts - README + comentarios
- **Fairness**: 4 pts - Análisis completo por subgrupos

### Presentación (15 pts):
- **Storytelling**: 6 pts - Hook + problema + impacto
- **Comunicación técnica**: 5 pts - Explicar sin jerga
- **Timing**: 4 pts - 10 min exactos + demo fluida

---

## 💡 TIPS DE SUPERVIVENCIA

1. **Comienza simple**: Baseline LR antes de XGBoost
2. **Valida temprano**: Test anti-fuga desde H2
3. **Documenta mientras trabajas**: No dejes para H24
4. **Backup constante**: Git commit cada hora
5. **Divide tareas**: Trabajar en paralelo maximiza tiempo
6. **Prioriza entregables**: Asegura obligatorios antes de extras
7. **Ensaya demo**: Prepara screenshots si falla en vivo
8. **Descansa**: 5 min de break cada 2 horas

---

## 🎓 RECURSOS QUICK ACCESS

- **NHANES Variables**: https://wwwn.cdc.gov/nchs/nhanes/search/
- **XGBoost Docs**: https://xgboost.readthedocs.io/
- **FastAPI Tutorial**: https://fastapi.tiangolo.com/tutorial/
- **Streamlit Docs**: https://docs.streamlit.io/
- **OpenAI API**: https://platform.openai.com/docs/

---

## 🏆 FRASE MOTIVACIONAL

> "El hackathon no se trata de perfección, sino de aprendizaje, 
> iteración rápida y crear impacto real en salud preventiva."

**¡ÉXITO EQUIPO! 🚀**

---

**Última actualización**: Noviembre 2025  
**Versión**: 1.0  
**Duoc UC Hackathon IA 2025**