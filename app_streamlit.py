import streamlit as st
import requests
import json
from fpdf import FPDF
import base64
import pandas as pd

# Configuración de página
st.set_page_config(
    page_title="Coach de Bienestar Preventivo",
    page_icon="🏥",
    layout="wide"
)

# URL de la API (ajustar según deployment)
API_URL = "http://localhost:8000"

# Header
st.title("🏥 Coach de Bienestar Preventivo")
st.markdown("""
Este sistema estima tu riesgo cardiometabólico y genera un plan personalizado.

**⚠️ DISCLAIMER:** Este NO es un diagnóstico médico. Consulta con un profesional de salud.
""")

# Sidebar para formulario
with st.sidebar:
    st.header("📋 Tu Perfil")

    # Datos demográficos
    st.subheader("Demográfico")
    age = st.number_input("Edad", min_value=18, max_value=85, value=45)
    sex = st.selectbox("Sexo", ["M", "F"], format_func=lambda x: "Masculino" if x == "M" else "Femenino")

    # Antropometría
    st.subheader("Antropometría")
    height_cm = st.number_input("Altura (cm)", min_value=120, max_value=220, value=170)
    weight_kg = st.number_input("Peso (kg)", min_value=30, max_value=220, value=75)
    waist_cm = st.number_input("Cintura (cm)", min_value=40, max_value=170, value=90)

    # Calcular IMC
    bmi = weight_kg / ((height_cm / 100) ** 2)
    st.info(f"IMC: {bmi:.1f}")

    # Estilo de vida
    st.subheader("Estilo de Vida")
    sleep_hours = st.slider("Horas de sueño/día", 3, 12, 7)
    smokes_cig_day = st.number_input("Cigarrillos/día", min_value=0, max_value=60, value=0)
    days_mvpa_week = st.slider("Días de ejercicio/semana", 0, 7, 3)
    fruit_veg_portions_day = st.slider("Porciones frutas/verduras/día", 0, 12, 5)

    # Botón de evaluación
    evaluate_button = st.button("🔍 Evaluar Riesgo", type="primary")

# Main area
if evaluate_button:
    # Preparar datos
    user_data = {
        "age": age,
        "sex": sex,
        "height_cm": height_cm,
        "weight_kg": weight_kg,
        "waist_cm": waist_cm,
        "sleep_hours": sleep_hours,
        "smokes_cig_day": smokes_cig_day,
        "days_mvpa_week": days_mvpa_week,
        "fruit_veg_portions_day": fruit_veg_portions_day
    }

    # Llamar a API de predicción
    with st.spinner("Analizando tu perfil..."):
        try:
            response = requests.post(f"{API_URL}/predict", json=user_data)

            if response.status_code == 200:
                result = response.json()

                # Mostrar resultado
                col1, col2, col3 = st.columns(3)

                with col1:
                    risk_score = result['score']
                    st.metric(
                        "Puntaje de Riesgo",
                        f"{risk_score:.1%}",
                        delta=None
                    )

                with col2:
                    st.metric(
                        "Nivel de Riesgo",
                        result['risk_level']
                    )

                with col3:
                    # Color según riesgo
                    if risk_score < 0.3:
                        color = "🟢"
                    elif risk_score < 0.6:
                        color = "🟡"
                    else:
                        color = "🔴"
                    st.metric("Indicador", color)

                # Recomendación principal
                st.info(f"📌 {result['recommendation']}")

                # Drivers de riesgo
                st.subheader("🎯 Principales Factores de Riesgo")

                drivers_df = pd.DataFrame(result['drivers'])
                st.dataframe(drivers_df, use_container_width=True)

                # Generar plan personalizado
                if st.button("📝 Generar Plan Personalizado"):
                    with st.spinner("Creando tu plan..."):
                        coach_request = {
                            "user_profile": user_data,
                            "risk_score": risk_score,
                            "top_drivers": [d['feature'] for d in result['drivers'][:3]]
                        }

                        coach_response = requests.post(f"{API_URL}/coach", json=coach_request)

                        if coach_response.status_code == 200:
                            plan_data = coach_response.json()

                            st.subheader("📋 Tu Plan de Bienestar Personalizado")
                            st.markdown(plan_data['plan'])

                            st.caption(f"📚 Fuentes: {', '.join(plan_data['sources'])}")

                            # Botón de descarga PDF
                            if st.button("⬇️ Descargar PDF"):
                                st.success("PDF generado! (implementar función de generación)")
                        else:
                            st.error(f"Error generando plan: {coach_response.status_code}")
            else:
                st.error(f"Error en predicción: {response.status_code}")

        except Exception as e:
            st.error(f"Error conectando con la API: {e}")
            st.info("Asegúrate de que la API esté corriendo en http://localhost:8000")

# Footer
st.markdown("---")
st.caption("""
Desarrollado para Hackathon IA Duoc UC 2025 | 
Basado en datos NHANES | 
⚠️ No sustituye atención médica profesional
""")

print("✅ App Streamlit guardada en app_streamlit.py")
print("   Para ejecutar: streamlit run app_streamlit.py")
