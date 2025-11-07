from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
import joblib
import numpy as np
import pandas as pd
import json
from pathlib import Path

# Inicializar FastAPI
app = FastAPI(
    title="Coach de Bienestar Preventivo",
    description="API para estimación de riesgo cardiometabólico y coaching personalizado",
    version="1.0.0"
)

# Cargar modelo y artefactos
model = joblib.load('model_xgboost.pkl')
imputer = joblib.load('imputer.pkl')
feature_names = joblib.load('feature_names.pkl')

# Modelos de datos
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
    drivers: List[dict]
    recommendation: str

class CoachRequest(BaseModel):
    user_profile: UserProfile
    risk_score: float
    top_drivers: List[str]

class CoachResponse(BaseModel):
    plan: str
    sources: List[str]

# Endpoints
@app.get("/")
def read_root():
    return {
        "message": "Coach de Bienestar Preventivo API",
        "version": "1.0.0",
        "endpoints": ["/predict", "/coach", "/health"]
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "model_loaded": model is not None}

@app.post("/predict", response_model=RiskResponse)
def predict_risk(profile: UserProfile):
    """
    Endpoint de predicción de riesgo cardiometabólico.
    """
    try:
        # Crear features
        features_dict = {
            'age': profile.age,
            'sex_male': 1 if profile.sex == 'M' else 0,
            'bmi': profile.weight_kg / ((profile.height_cm / 100) ** 2),
            'waist_height_ratio': profile.waist_cm / profile.height_cm,
            'sleep_hours': profile.sleep_hours or 7.5,
            'cigarettes_per_day': profile.smokes_cig_day or 0,
            'total_active_days': profile.days_mvpa_week or 0,
        }

        # Crear DataFrame
        X = pd.DataFrame([features_dict])

        # Agregar features faltantes con valores por defecto
        for feat in feature_names:
            if feat not in X.columns:
                X[feat] = 0

        X = X[feature_names]

        # Imputar y predecir
        X_imp = imputer.transform(X)
        risk_score = float(model.predict_proba(X_imp)[0, 1])

        # Determinar nivel de riesgo
        if risk_score < 0.3:
            risk_level = "Bajo"
            recommendation = "Mantener hábitos saludables"
        elif risk_score < 0.6:
            risk_level = "Moderado"
            recommendation = "Mejorar estilo de vida con coaching personalizado"
        else:
            risk_level = "Alto"
            recommendation = "Consultar con profesional de salud urgentemente"

        # Identificar drivers (top 5 features más importantes)
        feature_importance = model.feature_importances_
        top_indices = np.argsort(feature_importance)[-5:][::-1]

        drivers = [
            {
                "feature": feature_names[idx],
                "importance": float(feature_importance[idx]),
                "value": float(X_imp[0, idx])
            }
            for idx in top_indices
        ]

        return RiskResponse(
            score=risk_score,
            risk_level=risk_level,
            drivers=drivers,
            recommendation=recommendation
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/coach", response_model=CoachResponse)
def generate_coach_plan(request: CoachRequest):
    """
    Endpoint de generación de plan personalizado con RAG.

    NOTA: Requiere integración con función generate_personalized_plan()
    """
    try:
        # Aquí iría la llamada a generate_personalized_plan()
        # Por ahora retornamos un placeholder

        plan_text = f"""Plan personalizado de 2 semanas para mejorar tu salud.

Basado en tu perfil (edad {request.user_profile.age}, riesgo {request.risk_score:.1%}),
te recomendamos enfocarte en: {', '.join(request.top_drivers)}.

DISCLAIMER: Este plan NO es un diagnóstico médico. Consulta con un profesional de salud."""

        return CoachResponse(
            plan=plan_text,
            sources=["nutricion.md", "actividad_fisica.md"]
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

print("✅ API guardada en api_main.py")
print("   Para ejecutar: uvicorn api_main:app --reload")
