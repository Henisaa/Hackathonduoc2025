from openai import OpenAI
import json
from rank_bm25 import BM25Okapi
import numpy as np
from pathlib import Path
import os
from dotenv import load_dotenv

# ✅ Cargar variables del .env
load_dotenv()

# Crear cliente con la clave de entorno
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Schema de validación (movido desde el notebook)
USER_PROFILE_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
        "age": {"type": "integer", "minimum": 18, "maximum": 85},
        "sex": {"type": "string", "enum": ["F", "M"]},
        "height_cm": {"type": "number", "minimum": 120, "maximum": 220},
        "weight_kg": {"type": "number", "minimum": 30, "maximum": 220},
        "waist_cm": {"type": "number", "minimum": 40, "maximum": 170},
        "sleep_hours": {"type": "number", "minimum": 3, "maximum": 14},
        "smokes_cig_day": {"type": "integer", "minimum": 0, "maximum": 60},
        "days_mvpa_week": {"type": "integer", "minimum": 0, "maximum": 7},
        "fruit_veg_portions_day": {"type": "number", "minimum": 0, "maximum": 12}
    },
    "required": ["age", "sex", "height_cm", "weight_kg", "waist_cm"]
}



class SimpleRAG:
    """Sistema RAG básico con BM25 para búsqueda en /kb local."""
    
    def __init__(self, kb_dir='./kb'):
        self.kb_dir = Path(kb_dir)
        self.documents = []
        self.doc_names = []
        
        for md_file in self.kb_dir.glob('*.md'):
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
                self.documents.append(content)
                self.doc_names.append(md_file.name)
        
        self.tokenized_docs = [doc.lower().split() for doc in self.documents]
        self.bm25 = BM25Okapi(self.tokenized_docs)
        print(f"✅ RAG inicializado con {len(self.documents)} documentos")
    
    def search(self, query, top_k=3):
        query_tokens = query.lower().split()
        scores = self.bm25.get_scores(query_tokens)
        
        top_indices = np.argsort(scores)[-top_k:][::-1]
        
        return [
            {'filename': self.doc_names[idx], 'content': self.documents[idx], 'score': scores[idx]}
            for idx in top_indices if scores[idx] > 0
        ]

# Crear una instancia global del RAG para que la API la use
rag = SimpleRAG('./kb')

def extract_user_data_from_text(user_text: str) -> dict:
    """
    Extrae datos estructurados de texto libre usando OpenAI.
    """
    prompt = f"""Extrae la siguiente información del texto del usuario y devuélvela en formato JSON válido.

TEXTO DEL USUARIO:
{user_text}

INSTRUCCIONES:
1. Extrae SOLO la información presente en el texto
2. Convierte unidades si es necesario:
   - Altura: convertir a centímetros (1 metro = 100 cm, 1 pie = 30.48 cm, 1 pulgada = 2.54 cm)
   - Peso: convertir a kilogramos (1 libra = 0.453592 kg)
   - Cintura: convertir a centímetros
3. Sexo: usar "M" o "F" (masculino/femenino)
4. Si falta información requerida, usa null
5. Devuelve SOLO el JSON, sin explicaciones

ESQUEMA ESPERADO:
{json.dumps(USER_PROFILE_SCHEMA, indent=2)}

JSON:"""
    
    # Llamar a OpenAI
    response = client.chat.completions.create(
        model="gpt-4o",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )
    
    # Extraer JSON de la respuesta
    response_text = response.choices[0].message.content.strip()
    
    # Limpiar markdown si existe
    if response_text.startswith('```'):
        response_text = response_text.split('```')[1]
        if response_text.startswith('json'):
            response_text = response_text[4:]
        response_text = response_text.strip()
    
    # Parsear JSON
    try:
        user_data = json.loads(response_text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Error parseando JSON: {e}\\nRespuesta: {response_text}")
    
    # Validación básica
    required_fields = USER_PROFILE_SCHEMA['required']
    missing_fields = [f for f in required_fields if f not in user_data or user_data[f] is None]
    
    if missing_fields:
        raise ValueError(f"Faltan campos requeridos en el texto: {missing_fields}")
    
    return user_data


def generate_personalized_plan(user_data: dict, risk_score: float, top_drivers: list) -> dict:
    """
    Genera plan personalizado usando OpenAI + RAG.
    
    Args:
        user_data: Datos del usuario extraídos
        risk_score: Puntaje de riesgo (0-1)
        top_drivers: Lista de principales factores de riesgo
    
    Returns:
        dict con plan de acción
    """
    
    # 1. Identificar áreas prioritarias
    priority_areas = []
    
    if user_data.get('smokes_cig_day', 0) > 0:
        priority_areas.append('cesación tabaquismo')
    
    if user_data.get('sleep_hours', 8) < 7:
        priority_areas.append('mejora del sueño')
    
    if user_data.get('days_mvpa_week', 5) < 3:
        priority_areas.append('aumento actividad física')
    
    if user_data.get('fruit_veg_portions_day', 5) < 5:
        priority_areas.append('mejora alimentación')
    
    # 2. Buscar conocimiento relevante
    rag_query = f"recomendaciones para {', '.join(priority_areas)}"
    relevant_docs = rag.search(rag_query, top_k=3)
    
    # 3. Construir contexto para OpenAI
    context = "\n\n".join([
        f"=== {doc['filename']} ===\n{doc['content']}" 
        for doc in relevant_docs
    ])
    
    # 4. Prompt para OpenAI
    prompt = f"""Eres un coach de bienestar preventivo. Genera un plan personalizado de 2 semanas.

PERFIL DEL USUARIO:
{json.dumps(user_data, indent=2, ensure_ascii=False)}

EVALUACIÓN DE RIESGO:
- Puntaje de riesgo cardiometabólico: {risk_score:.1%}
- Principales factores de riesgo: {', '.join(top_drivers)}

ÁREAS PRIORITARIAS:
{', '.join(priority_areas) if priority_areas else 'Mantenimiento de hábitos saludables'}

CONOCIMIENTO DISPONIBLE:
{context}

INSTRUCCIONES:
1. Crea un plan de 2 semanas con acciones SMART (específicas, medibles, alcanzables, relevantes, temporales)
2. Prioriza las áreas de mayor riesgo
3. USA SOLO información de la base de conocimiento proporcionada
4. CITA las fuentes usando el nombre del archivo entre [corchetes]
5. NO inventes ni alucines información
6. Incluye un disclaimer: "Este plan NO es un diagnóstico médico. Consulta con un profesional de salud."

FORMATO:
{{"plan": "texto del plan", "sources": ["archivo1.md", "archivo2.md"]}}

JSON:"""
    
    # 5. Llamar a OpenAI
    response = client.chat.completions.create(
        model="gpt-4o",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )
    
    response_text = response.choices[0].message.content.strip()
    
    # Limpiar markdown
    if response_text.startswith('```'):
        response_text = response_text.split('```')[1]
        if response_text.startswith('json'):
            response_text = response_text[4:]
        response_text = response_text.strip()
    
    plan_data = json.loads(response_text)
    
    # 6. Validar que se usaron fuentes reales
    cited_sources = plan_data.get('sources', [])
    valid_sources = [doc['filename'] for doc in relevant_docs]
    
    for source in cited_sources:
        if source not in valid_sources:
            print(f"⚠️ Fuente potencialmente alucinada: {source}")
    
    return plan_data

# Bloque de prueba: solo se ejecuta si corres "python rag_module.py"
if __name__ == "__main__":
    # --- Prueba de extracción de texto ---
    print("--- Probando Extracción de Texto ---")
    test_text = """Hola, tengo 45 años, soy mujer. 
Mido 1.65 metros y peso 75 kilos. 
Mi cintura mide 90 cm.
Duermo unas 6 horas por noche."""
    try:
        extracted_data = extract_user_data_from_text(test_text)
        print("\n✅ DATOS EXTRAÍDOS:")
        print(json.dumps(extracted_data, indent=2, ensure_ascii=False))
    except ValueError as e:
        print(f"❌ ERROR: {e}")

    # --- Prueba de generación de plan ---
    print("\n--- Probando Generación de Plan ---")
    if 'extracted_data' in locals():
        test_risk_score = 0.65
        test_drivers = ['IMC alto', 'Sueño insuficiente']
        try:
            plan = generate_personalized_plan(extracted_data, test_risk_score, test_drivers)
            print("\n✅ PLAN GENERADO (PRUEBA):")
            print("\n" + plan['plan'])
            print(f"\n📚 Fuentes citadas: {', '.join(plan['sources'])}")
        except Exception as e:
            print(f"❌ ERROR generando plan: {e}")
    else:
        print("⏭️  Saltando prueba de plan porque la extracción falló.")