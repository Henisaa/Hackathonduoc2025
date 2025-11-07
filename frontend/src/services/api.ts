const API_URL = "http://127.0.0.1:8000"; // tu backend FastAPI local

export async function predictRisk(userProfile: any) {
  const res = await fetch(`${API_URL}/predict`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(userProfile),
  });
  if (!res.ok) throw new Error("Error en la predicción");
  return await res.json();
}

export async function generateCoachPlan(request: any) {
  const res = await fetch(`${API_URL}/coach`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  });
  if (!res.ok) throw new Error("Error generando plan");
  return await res.json();
}
