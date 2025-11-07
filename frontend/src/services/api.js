const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

export async function predictRisk(data) {
  const response = await fetch(`${API_URL}/predict`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!response.ok) throw new Error("Error en la predicción");
  return await response.json();
}

export async function generateCoachPlan(data) {
  const response = await fetch(`${API_URL}/coach`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!response.ok) throw new Error("Error generando el plan");
  return await response.json();
}
