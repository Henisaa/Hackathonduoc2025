import React, { useState } from "react";

export default function MealScreen({ goBack }: { goBack: () => void }) {
  const [image, setImage] = useState<string | null>(null);
  const [feedback, setFeedback] = useState<string>("");

  const handleImage = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const url = URL.createObjectURL(file);
      setImage(url);
      setFeedback("Comida equilibrada (simulación de análisis AI). 🍎");
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-50 flex flex-col items-center px-4 py-8">
      <h1 className="text-2xl font-semibold mb-3">Registro de Comidas</h1>
      <p className="text-slate-400 mb-6 text-center">
        Toma una foto de tu comida para recibir retroalimentación instantánea.
      </p>

      <input
        type="file"
        accept="image/*"
        capture="environment"
        onChange={handleImage}
        className="mb-4"
      />

      {image && (
        <div className="bg-slate-900 p-4 rounded-xl">
          <img src={image} alt="Comida" className="w-64 rounded-lg mb-2" />
          <p className="text-emerald-400">{feedback}</p>
        </div>
      )}

      <button
        onClick={goBack}
        className="mt-6 bg-blue-500 hover:bg-blue-400 text-slate-950 font-semibold py-2 px-4 rounded-xl"
      >
        Volver al Panel
      </button>
    </div>
  );
}
