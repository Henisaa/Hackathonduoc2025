# ===============================================================
# API: Coach de Bienestar Preventivo (FastAPI)
# ===============================================================

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
import joblib
import numpy as np
import pandas as pd
from pathlib import Path

# ---------------------------------------------------------------
# 1. CONFIGURACIÓN INICIAL
# ---------------------------------------------------------------
app = FastAPI(
    title="Coach de Bienestar Preventivo",
    description="API para estimación de riesgo cardiometabólico y coaching personalizado",
    version="1.0.0"
)

# Cargar modelo entrenado (asegúrate de que existe en /models)
MODEL_PATH = Path("models/label_diabetes_xgb_calibrated.pkl")
if not MODEL_PATH.exists():
    raise FileNotFoundError(f"❌ Modelo no encontrado en {MODEL_PATH}")

model = joblib.load(MODEL_PATH)
print(f"✅ Modelo cargado desde: {MODEL_PATH}")

# ---------------------------------------------------------------
# 2. MODELOS DE DATOS (Pydantic)
# ---------------------------------------------------------------
class UserProfile(BaseModel):
    age: int = Field(..., ge=18, le=85)
    sex: str = Field(..., pattern="^[MF]$")
    height_cm: float = Field(..., ge=120, le=220)
    weight_kg: float = Field(..., ge=30, le=220)
    waist_cm: float = Field(..., ge=40, le=170)
    sleep_hours: Optional[float] = Field(None, ge=3, le=14)
    smokes_cig_day: Optional[int] = Field(None, ge=0, le=60)
    days_mvpa_week: Optional[int] = Field(None, ge=0, le=7)
    fruit_veg_portions_day: Optional[float] = Field(None, ge=0, le=12)


class RiskResponse(BaseModel):
    score: float
    risk_level: str
    recommendation: str


class CoachRequest(BaseModel):
    user_profile: UserProfile
    risk_score: float
    top_drivers: List[str]


class CoachResponse(BaseModel):
    plan: str
    sources: List[str]


# ---------------------------------------------------------------
# 3. ENDPOINTS BÁSICOS
# ---------------------------------------------------------------
@app.get("/")
def read_root():
    return {
        "message": "Bienvenido a la API del Coach de Bienestar Preventivo",
        "version": "1.0.0",
        "endpoints": ["/predict", "/coach", "/health"]
    }


@app.get("/health")
def health_check():
    return {"status": "healthy", "model_loaded": model is not None}


# ---------------------------------------------------------------
# 4. ENDPOINT: PREDICCIÓN DE RIESGO
# ---------------------------------------------------------------
@app.post("/predict", response_model=RiskResponse)
def predict_risk(profile: UserProfile):
    """
    Endpoint de predicción de riesgo cardiometabólico.
    """
    try:
        # --- Construcción de features (idénticas al entrenamiento) ---
        features = {
            "age": profile.age,
            "age_squared": profile.age ** 2,
            "sex_male": 1 if profile.sex == "M" else 0,
            "bmi": profile.weight_kg / ((profile.height_cm / 100) ** 2),
            "waist_height_ratio": profile.waist_cm / profile.height_cm,
            "high_waist_height_ratio": 1 if (profile.waist_cm / profile.height_cm) >= 0.5 else 0,
            "cigarettes_per_day": profile.smokes_cig_day or 0,
            "ever_smoker": 1 if (profile.smokes_cig_day or 0) > 0 else 0,
            "current_smoker": 1 if (profile.smokes_cig_day or 0) > 0 else 0,
            "total_active_days": profile.days_mvpa_week or 0,
            "meets_activity_guidelines": 1 if (profile.days_mvpa_week or 0) >= 5 else 0,
            "bmi_age_interaction": profile.age * (profile.weight_kg / ((profile.height_cm / 100) ** 2)),
            "waist_age_interaction": profile.age * (profile.waist_cm / profile.height_cm),
            "sleep_hours": profile.sleep_hours or 7.5,
            "short_sleep": 1 if (profile.sleep_hours or 7.5) < 7 else 0,
        }

        X = pd.DataFrame([features])

        # --- Reordenar columnas para que coincidan con el modelo ---
        if hasattr(model, "feature_names_in_"):
            X = X[model.feature_names_in_]
        else:
            print("⚠️ El modelo no tiene atributo feature_names_in_, se usará orden actual")

        # --- Predicción ---
        risk_score = float(model.predict_proba(X)[0, 1])

        # --- Clasificación de riesgo ---
        if risk_score < 0.3:
            risk_level = "Bajo"
            recommendation = "Mantener hábitos saludables"
        elif risk_score < 0.6:
            risk_level = "Moderado"
            recommendation = "Mejorar estilo de vida con coaching personalizado"
        else:
            risk_level = "Alto"
            recommendation = "Consultar con profesional de salud urgentemente"

        return RiskResponse(
            score=risk_score,
            risk_level=risk_level,
            recommendation=recommendation
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------------
# 5. ENDPOINT: PLAN PERSONALIZADO (FASE COACH)
# ---------------------------------------------------------------
@app.post("/coach", response_model=CoachResponse)
def generate_coach_plan(request: CoachRequest):
    """
    Endpoint de generación de plan personalizado (FASE RAG futura).
    """
    try:
        plan_text = f"""
        Plan personalizado de 2 semanas para mejorar tu bienestar.
        
        Basado en tu perfil (edad {request.user_profile.age} años, riesgo estimado {request.risk_score:.1%}),
        las áreas prioritarias son: {', '.join(request.top_drivers)}.
        
        Semana 1:
        - Ajusta tus hábitos diarios.
        - Registra tu actividad física y sueño.
        - Mejora la alimentación con frutas y verduras.
        
        Semana 2:
        - Incrementa gradualmente la actividad física.
        - Reduce cigarrillos si fumas.
        - Mantén un horario de sueño regular.
        
        DISCLAIMER: Este plan NO es un diagnóstico médico. Consulta con un profesional de salud.
        """

        return CoachResponse(
            plan=plan_text.strip(),
            sources=["nutricion.md", "actividad_fisica.md", "sueño.md"]
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------------
# 6. SERVIDOR LOCAL
# ---------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
