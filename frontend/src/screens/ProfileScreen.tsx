import React, { useState } from "react";

export default function ProfileScreen({ onSave }: { onSave: (p: any) => void }) {
  const [form, setForm] = useState({
    age: 40,
    sex: "F",
    height_cm: 165,
    weight_kg: 70,
    waist_cm: 85,
    sleep_hours: 7,
    smokes_cig_day: 0,
    days_mvpa_week: 3,
    fruit_veg_portions_day: 3,
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setForm({ ...form, [name]: name === "sex" ? value : Number(value) });
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-950 text-slate-50 px-4">
      <div className="bg-slate-900 p-6 rounded-2xl w-full max-w-md">
        <h1 className="text-2xl font-semibold mb-4">Tu Perfil de Bienestar</h1>

        {Object.entries(form).map(([key, value]) => (
          <div key={key} className="mb-3">
            <label className="block mb-1 capitalize">{key.replace(/_/g, " ")}</label>
            <input
              type={typeof value === "number" ? "number" : "text"}
              name={key}
              value={value}
              onChange={handleChange}
              className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2"
            />
          </div>
        ))}

        <button
          onClick={() => onSave(form)}
          className="mt-4 w-full bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-semibold py-2.5 rounded-xl transition"
        >
          Guardar y Calcular Riesgo
        </button>
      </div>
    </div>
  );
}
