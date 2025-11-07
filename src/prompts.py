# ===============================================================
# src/prompts.py - COACH PREVENTIVO (LLM + RAG)
# ===============================================================

import os, json
from openai import OpenAI
from dotenv import load_dotenv
from .rag import SimpleRAG

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
rag = SimpleRAG("./kb")

def generate_personalized_plan(user_profile, risk_score, top_drivers):
    query = " ".join(top_drivers)
    context_docs = rag.search(query)
    context = "\n\n".join([f"=== {d['filename']} ===\n{d['content']}" for d in context_docs])

    prompt = f"""
Eres un coach de bienestar preventivo.
Genera un plan de 2 semanas según el siguiente perfil y contexto.

Perfil:
{json.dumps(user_profile, indent=2, ensure_ascii=False)}

Riesgo: {risk_score:.1%}
Factores principales: {', '.join(top_drivers)}

Contexto:
{context}

Devuelve JSON con campos 'plan' y 'sources'.
"""

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        max_tokens=1500
    )

    return json.loads(res.choices[0].message.content)
