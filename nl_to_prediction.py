# ===============================================================
# FASE 6: LLM → JSON → IA EXPLICATIVA (Predicción de Riesgo Diabetes)
# ===============================================================

import os
import json
import joblib
import pandas as pd
from openai import OpenAI
from dotenv import load_dotenv

# ===============================================================
# 1️⃣ CARGAR VARIABLES DE ENTORNO DESDE .env
# ===============================================================
load_dotenv()  # Carga el archivo .env automáticamente

OPENAI_KEY = os.getenv("OPENAI_API_KEY")
MODEL_PATH = os.getenv("MODEL_PATH", "models/label_diabetes_xgb_calibrated.pkl")

if not OPENAI_KEY:
    raise ValueError("❌ No se encontró OPENAI_API_KEY en .env. Asegúrate de definirlo.")
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"❌ No se encontró el modelo en {MODEL_PATH}")

client = OpenAI(api_key=OPENAI_KEY)
print("✅ Cliente OpenAI configurado correctamente")


# ===============================================================
# 2️⃣ ESQUEMA DE VALIDACIÓN DEL PERFIL DE USUARIO
# ===============================================================
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


# ===============================================================
# 3️⃣ FUNCIÓN: EXTRACCIÓN DE DATOS DESDE TEXTO LIBRE
# ===============================================================
def extract_user_data_from_text(user_text: str) -> dict:
    """
    Extrae datos estructurados del texto del usuario (NL → JSON)
    usando el modelo GPT-4o de OpenAI.
    """
    prompt = f"""Extrae la siguiente información del texto del usuario y devuélvela en formato JSON válido.

TEXTO DEL USUARIO:
{user_text}

INSTRUCCIONES:
1. Extrae SOLO la información presente en el texto.
2. Convierte unidades si es necesario:
   - Altura → centímetros (1 metro = 100 cm, 1 pie = 30.48 cm, 1 pulgada = 2.54 cm)
   - Peso → kilogramos (1 libra = 0.453592 kg)
   - Cintura → centímetros
3. Sexo: usar "M" o "F"
4. Si falta información requerida, usa null.
5. Devuelve SOLO el JSON, sin texto adicional.

ESQUEMA ESPERADO:
{json.dumps(USER_PROFILE_SCHEMA, indent=2)}

JSON:
"""

    response = client.chat.completions.create(
        model="gpt-4o",
        max_tokens=800,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )

    response_text = response.choices[0].message.content.strip()

    if response_text.startswith("```"):
        response_text = response_text.split("```")[1]
        if response_text.startswith("json"):
            response_text = response_text[4:]
        response_text = response_text.strip()

    try:
        user_data = json.loads(response_text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Error parseando JSON: {e}\nRespuesta: {response_text}")

    missing = [f for f in USER_PROFILE_SCHEMA["required"]
               if f not in user_data or user_data[f] is None]
    if missing:
        raise ValueError(f"⚠️ Faltan campos requeridos: {missing}")

    return user_data


# ===============================================================
# 4️⃣ TRANSFORMACIÓN A FEATURES DEL MODELO NHANES (COMPLETA)
# ===============================================================
def transform_user_to_features(user_data: dict) -> pd.DataFrame:
    """
    Convierte el JSON de usuario en las features que espera el modelo NHANES.
    Incluye variables de sueño ('sleep_hours' y 'short_sleep').
    """
    age = user_data["age"]
    height_cm = user_data["height_cm"]
    weight_kg = user_data["weight_kg"]
    waist_cm = user_data["waist_cm"]
    sex = user_data["sex"]

    bmi = weight_kg / ((height_cm / 100) ** 2)
    waist_height_ratio = waist_cm / height_cm

    sleep_hours = user_data.get("sleep_hours", None)
    short_sleep = int(sleep_hours is not None and sleep_hours < 6)

    df = pd.DataFrame([{
        "age": age,
        "age_squared": age ** 2,
        "sex_male": 1 if sex == "M" else 0,
        "bmi": bmi,
        "waist_height_ratio": waist_height_ratio,
        "high_waist_height_ratio": int(waist_height_ratio >= 0.5),
        "cigarettes_per_day": user_data.get("smokes_cig_day", 0),
        "ever_smoker": int(user_data.get("smokes_cig_day", 0) > 0),
        "current_smoker": int(user_data.get("smokes_cig_day", 0) > 0),
        "total_active_days": user_data.get("days_mvpa_week", 0),
        "meets_activity_guidelines": int(user_data.get("days_mvpa_week", 0) >= 5),
        "bmi_age_interaction": bmi * age,
        "waist_age_interaction": waist_height_ratio * age,
        "sleep_hours": sleep_hours,
        "short_sleep": short_sleep
    }])

    print("\n🧩 Features generadas para el modelo:")
    print(df.T)
    return df



# ===============================================================
# 5️⃣ FUNCIÓN PRINCIPAL DE PREDICCIÓN
# ===============================================================
def predict_risk_from_text(user_text: str):
    print("\n📥 Texto recibido:")
    print(user_text)

    user_data = extract_user_data_from_text(user_text)
    print("\n✅ Datos extraídos:")
    print(json.dumps(user_data, indent=2, ensure_ascii=False))

    features = transform_user_to_features(user_data)

    # ✅ Cargar modelo y mantener orden de features original
    model = joblib.load(MODEL_PATH)
    print(f"\n🤖 Modelo cargado desde: {MODEL_PATH}")

    # Intentar detectar el orden original de las features
    try:
        feature_order = model.feature_names_in_
    except AttributeError:
        # Si es pipeline, accedemos al estimador base
        feature_order = getattr(model, "feature_names_in_", None)
        if feature_order is None and hasattr(model, "named_steps"):
            last_step = list(model.named_steps.values())[-1]
            feature_order = getattr(last_step, "feature_names_in_", None)

    if feature_order is not None:
        features = features.reindex(columns=feature_order, fill_value=0)
        print(f"🔧 Features reordenadas según modelo ({len(feature_order)} columnas).")

    # 🔹 Predicción
    risk = model.predict_proba(features)[:, 1][0]
    print(f"\n🔹 Riesgo estimado de diabetes: {risk:.2%}")

    if risk < 0.3:
        level = "bajo"
    elif risk < 0.6:
        level = "moderado"
    else:
        level = "alto"

    print(f"💬 Interpretación: riesgo {level.upper()} según patrones NHANES 2007–2018")

    return {"risk": risk, "level": level, "user_data": user_data}



# ===============================================================
# 6️⃣ PRUEBA MANUAL
# ===============================================================
if __name__ == "__main__":
    test_text = """Hola, tengo 45 años, soy mujer.
    Mido 1.65 metros y peso 75 kilos.
    Mi cintura mide 90 cm.
    Duermo unas 6 horas por noche.
    Fumo 10 cigarrillos al día.
    Hago ejercicio 2 días a la semana.
    Como 3 porciones de frutas y verduras al día."""

    result = predict_risk_from_text(test_text)

    print("\n📊 RESULTADO FINAL:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
