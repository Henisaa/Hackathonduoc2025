# ==============================================================
# FASE 7: LLM - COACH CON RAG (H13 a H16)
# ==============================================================
import os
import json
import numpy as np
import re
from pathlib import Path
from rank_bm25 import BM25Okapi
from openai import OpenAI
from dotenv import load_dotenv

# --------------------------------------------------------------
# 1️⃣ Configuración
# --------------------------------------------------------------
load_dotenv()
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Crear carpeta /kb
Path('./kb').mkdir(exist_ok=True)

# --------------------------------------------------------------
# 2️⃣ Base de conocimiento (fichas locales)
# --------------------------------------------------------------
KB_CONTENT = {
    'nutricion.md': """# Nutrición Saludable
## Recomendaciones Generales
- Consumir al menos 5 porciones de frutas y verduras al día
- Preferir cereales integrales sobre refinados
- Limitar azúcares añadidos a menos del 10% de calorías totales
- Reducir sodio a menos de 2300 mg/día
## Para Prevención de Diabetes
- Aumentar fibra dietética (25-30g/día)
- Elegir alimentos con bajo índice glicémico
- Limitar bebidas azucaradas
- Preferir grasas saludables (omega-3, aceite de oliva)
Fuente: American Diabetes Association, 2024
""",
    'actividad_fisica.md': """# Actividad Física
## Recomendaciones OMS
- Adultos: 150-300 min/semana de actividad moderada
- Ejercicios de fortalecimiento muscular 2+ días/semana
- Reducir tiempo sedentario
## Beneficios para Prevención
- Mejora sensibilidad a la insulina
- Ayuda a mantener peso saludable
- Reduce presión arterial
- Mejora perfil lipídico
## Inicio Gradual
- Comenzar con 10-15 min/día
- Aumentar 5 min/semana
- Incorporar actividades placenteras
Fuente: WHO Physical Activity Guidelines, 2020
""",
    'sueño.md': """# Higiene del Sueño
## Duración Recomendada
- Adultos: 7-9 horas por noche
- Dormir menos de 7 horas aumenta riesgo cardiometabólico
## Prácticas Saludables
- Horario regular
- Evitar pantallas antes de dormir
- Limitar cafeína después de las 14:00
- Ambiente fresco, oscuro y silencioso
## Relación con Salud Metabólica
- Sueño insuficiente altera hormonas del apetito
- Aumenta resistencia a la insulina
Fuente: National Sleep Foundation, 2023
""",
    'tabaquismo.md': """# Cesación del Tabaquismo
## Impacto en Salud
- Fumar duplica riesgo de diabetes tipo 2
- Aumenta riesgo cardiovascular
## Estrategias para Dejar de Fumar
1. Fijar fecha de cesación
2. Informar a familiares y amigos
3. Identificar gatillantes
4. Considerar reemplazo nicotínico
5. Buscar apoyo profesional
Fuente: CDC Smoking Cessation Guidelines, 2024
"""
}

# Guardar fichas
for filename, content in KB_CONTENT.items():
    with open(f'./kb/{filename}', 'w', encoding='utf-8') as f:
        f.write(content)
print(f"✅ Base de conocimiento creada ({len(KB_CONTENT)} fichas en ./kb)")

# --------------------------------------------------------------
# 3️⃣ Sistema RAG simple con BM25
# --------------------------------------------------------------
class SimpleRAG:
    """RAG local con BM25 (sin embeddings)."""
    def __init__(self, kb_dir='./kb'):
        self.kb_dir = Path(kb_dir)
        self.documents = []
        self.doc_names = []
        for md_file in self.kb_dir.glob('*.md'):
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
                self.documents.append(content)
                self.doc_names.append(md_file.name)
        self.tokenized_docs = [self._tokenize(doc) for doc in self.documents]
        self.bm25 = BM25Okapi(self.tokenized_docs)
        print(f"✅ RAG inicializado con {len(self.documents)} documentos")

    def _tokenize(self, text):
        return re.findall(r'\b\w+\b', text.lower())

    def search(self, query, top_k=3):
        query_tokens = self._tokenize(query)
        scores = self.bm25.get_scores(query_tokens)
        top_indices = np.argsort(scores)[-top_k:][::-1]
        results = []
        for idx in top_indices:
            if scores[idx] > 0:
                results.append({
                    'filename': self.doc_names[idx],
                    'content': self.documents[idx],
                    'score': float(scores[idx])
                })
        return results

# Inicializar RAG
rag = SimpleRAG('./kb')

# --------------------------------------------------------------
# 4️⃣ Función de generación de plan personalizado
# --------------------------------------------------------------
def generate_personalized_plan(user_data: dict, risk_score: float, top_drivers: list):
    """Genera plan personalizado usando OpenAI + RAG."""

    priority_areas = []
    if user_data.get('smokes_cig_day', 0) > 0:
        priority_areas.append('cesación tabaquismo')
    if user_data.get('sleep_hours', 8) < 7:
        priority_areas.append('mejora del sueño')
    if user_data.get('days_mvpa_week', 5) < 3:
        priority_areas.append('aumento actividad física')
    if user_data.get('fruit_veg_portions_day', 5) < 5:
        priority_areas.append('mejora alimentación')

    rag_query = f"recomendaciones para {', '.join(priority_areas)}"
    relevant_docs = rag.search(rag_query, top_k=3)
    context = "\n\n".join([
        f"=== {doc['filename']} ===\n{doc['content']}"
        for doc in relevant_docs
    ])

    prompt = f"""Eres un coach de bienestar preventivo. Genera un plan personalizado de 2 semanas.

PERFIL DEL USUARIO:
{json.dumps(user_data, indent=2, ensure_ascii=False)}

RIESGO:
- Puntaje de riesgo: {risk_score:.1%}
- Factores principales: {', '.join(top_drivers)}

ÁREAS PRIORITARIAS:
{', '.join(priority_areas) if priority_areas else 'Mantenimiento de hábitos saludables'}

CONOCIMIENTO DISPONIBLE:
{context}

INSTRUCCIONES:
1. Crea un plan de 2 semanas con acciones SMART
2. Prioriza las áreas de mayor riesgo
3. Usa solo la información de la base de conocimiento
4. Cita fuentes con el nombre del archivo entre [corchetes]
5. No inventes información
6. Incluye al final: "Este plan NO es un diagnóstico médico. Consulta con un profesional de salud."

FORMATO JSON:
{{"plan": "texto del plan", "sources": ["archivo1.md", "archivo2.md"]}}
"""

    response = client.chat.completions.create(
        model="gpt-4o",
        max_tokens=1800,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )

    plan_data = json.loads(response.choices[0].message.content.strip())

    print("\n✅ PLAN GENERADO:")
    print("\n" + plan_data['plan'])
    print(f"\n📚 Fuentes citadas: {', '.join(plan_data.get('sources', []))}")
    return plan_data

# --------------------------------------------------------------
# 5️⃣ Prueba con datos de usuario reales
# --------------------------------------------------------------
test_user_data = {
    "age": 45,
    "sex": "F",
    "height_cm": 165,
    "weight_kg": 75,
    "waist_cm": 90,
    "sleep_hours": 6,
    "smokes_cig_day": 10,
    "days_mvpa_week": 2,
    "fruit_veg_portions_day": 3
}
test_risk_score = 0.65
test_drivers = ['IMC alto', 'Tabaquismo', 'Sueño insuficiente']

plan = generate_personalized_plan(test_user_data, test_risk_score, test_drivers)
