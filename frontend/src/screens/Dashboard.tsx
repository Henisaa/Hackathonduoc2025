import React from "react";

interface DashboardProps {
  profile: any;
  risk: any;
  plan: string | null;
  planSources: string[];
  onGeneratePlan: () => void;
  loadingPlan: boolean;
  goToMeals: () => void;
  reset: () => void;
}

export default function Dashboard({
  profile,
  risk,
  plan,
  planSources,
  onGeneratePlan,
  loadingPlan,
  goToMeals,
  reset,
}: DashboardProps) {
  // 🎨 Colores según el nivel de riesgo
  const getRiskColor = (level: string) => {
    switch (level) {
      case "Bajo":
        return "text-emerald-400";
      case "Moderado":
        return "text-amber-400";
      case "Alto":
        return "text-red-400";
      default:
        return "text-slate-300";
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-50 px-6 py-8">
      {/* 🧠 Header */}
      <header className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Panel de Bienestar</h1>
        <p className="text-slate-400">
          Bienvenido/a, edad {profile.age} — sexo{" "}
          {profile.sex === "M" ? "Masculino" : "Femenino"}
        </p>
      </header>

      {/* ❤️ Bloque de riesgo */}
      {risk ? (
        <section className="bg-slate-900 rounded-2xl p-6 shadow-lg mb-6 border border-slate-800">
          <h2 className="text-xl font-semibold mb-2">Riesgo estimado</h2>

          <div className="flex items-end justify-between">
            <div>
              <p className="text-4xl font-bold mb-1">
                {(risk.score * 100).toFixed(1)}%
              </p>
              <p className={`${getRiskColor(risk.risk_level)} text-lg font-semibold`}>
                {risk.risk_level}
              </p>
            </div>

            {/* Mini gauge */}
            <div
              className="w-24 h-24 rounded-full border-8"
              style={{
                borderColor:
                  risk.risk_level === "Alto"
                    ? "#ef4444"
                    : risk.risk_level === "Moderado"
                    ? "#f59e0b"
                    : "#10b981",
              }}
            ></div>
          </div>

          <p className="text-slate-300 mt-3">{risk.recommendation}</p>

          {/* Factores principales */}
          <h3 className="mt-4 text-sm font-semibold text-slate-400 uppercase tracking-wide">
            Factores principales:
          </h3>
          <ul className="mt-2 list-disc pl-5 text-slate-400">
            {(risk.drivers ??
              ["IMC elevado", "Sueño insuficiente", "Baja actividad física"]
            ).map((d: string, i: number) => (
              <li key={i}>{d}</li>
            ))}
          </ul>
        </section>
      ) : (
        <p className="text-slate-400">Calculando riesgo...</p>
      )}

      {/* ⚙️ Botones de acción */}
      <div className="flex flex-wrap gap-3 mb-6">
        <button
          onClick={onGeneratePlan}
          disabled={loadingPlan}
          className={`py-2 px-4 rounded-xl font-semibold transition ${
            loadingPlan
              ? "bg-slate-700 text-slate-400"
              : "bg-emerald-500 hover:bg-emerald-400 text-slate-950"
          }`}
        >
          {loadingPlan ? "Generando..." : "Generar Plan Personalizado"}
        </button>

        <button
          onClick={goToMeals}
          className="bg-blue-500 hover:bg-blue-400 text-slate-950 font-semibold py-2 px-4 rounded-xl transition"
        >
          Registrar Comida 🍽️
        </button>

        <button
          onClick={reset}
          className="bg-red-500 hover:bg-red-400 text-slate-950 font-semibold py-2 px-4 rounded-xl transition"
        >
          Reiniciar Perfil
        </button>
      </div>

      {/* 📋 Plan personalizado */}
      {plan && (
        <section className="mt-6 bg-slate-900 rounded-xl p-4 border border-slate-700">
          <h2 className="text-xl font-semibold mb-2">Plan de Acción</h2>
          <pre className="text-slate-300 whitespace-pre-wrap leading-relaxed">
            {plan}
          </pre>
          {planSources.length > 0 && (
            <p className="text-slate-500 text-sm mt-2">
              Fuentes: {planSources.join(", ")}
            </p>
          )}
        </section>
      )}
    </div>
  );
}
