import React, { useState, useEffect } from "react";
import { predictRisk, generateCoachPlan } from "./services/api";
import ProfileScreen from "./screens/ProfileScreen";
import Dashboard from "./screens/Dashboard";
import MealScreen from "./screens/MealScreen";
type Screen = "loading" | "profile" | "dashboard" | "meal";

interface UserProfile {
  age: number;
  sex: "M" | "F";
  height_cm: number;
  weight_kg: number;
  waist_cm: number;
  sleep_hours: number;
  smokes_cig_day: number;
  days_mvpa_week: number;
  fruit_veg_portions_day: number;
}

interface RiskData {
  score: number;
  risk_level: string;
  recommendation: string;
  drivers: string[];
}

function App() {
  const [screen, setScreen] = useState<Screen>("loading");
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [risk, setRisk] = useState<RiskData | null>(null);
  const [plan, setPlan] = useState<string | null>(null);
  const [planSources, setPlanSources] = useState<string[]>([]);
  const [loadingPlan, setLoadingPlan] = useState(false);

  // Test API + cargar perfil almacenado
  useEffect(() => {
    const init = async () => {
      try {
        const res = await fetch("http://127.0.0.1:8000/health");
        const data = await res.json();
        console.log("API:", data);
      } catch (e) {
        console.error("No se pudo conectar con la API", e);
      }

      const saved = localStorage.getItem("user_profile");
      if (saved) {
        const p = JSON.parse(saved);
        setProfile(p);
        setScreen("dashboard");
        fetchRisk(p);
      } else {
        setScreen("profile");
      }
    };
    init();
  }, []);

  const fetchRisk = async (p: UserProfile) => {
    try {
      const response = await predictRisk(p);
      setRisk(response);
    } catch (e) {
      console.error(e);
    }
  };

  const handleSaveProfile = async (p: UserProfile) => {
    setProfile(p);
    localStorage.setItem("user_profile", JSON.stringify(p));
    setScreen("dashboard");
    await fetchRisk(p);
  };

  const handleGeneratePlan = async () => {
    if (!profile || !risk) return;
    setLoadingPlan(true);
    try {
      const payload = {
        user_profile: profile,
        risk_score: risk.score,
        top_drivers: risk.drivers.slice(0, 3),
      };
      const res = await generateCoachPlan(payload);
      setPlan(res.plan);
      setPlanSources(res.sources || []);
    } catch (e) {
      console.error(e);
      setPlan("No se pudo generar el plan. Intenta más tarde.");
    } finally {
      setLoadingPlan(false);
    }
  };

  if (screen === "loading") {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-950 text-slate-50">
        <div className="animate-pulse text-center">
          <div className="text-4xl mb-2">❤️</div>
          <p className="text-slate-300">Cargando tu asistente de salud...</p>
        </div>
      </div>
    );
  }

  if (screen === "profile") {
    return <ProfileScreen onSave={handleSaveProfile} />;
  }

  if (screen === "dashboard" && profile) {
    return (
      <Dashboard
        profile={profile}
        risk={risk}
        plan={plan}
        planSources={planSources}
        onGeneratePlan={handleGeneratePlan}
        loadingPlan={loadingPlan}
        goToMeals={() => setScreen("meal")}
        reset={() => {
          localStorage.clear();
          setProfile(null);
          setRisk(null);
          setPlan(null);
          setPlanSources([]);
          setScreen("profile");
        }}
      />
    );
  }

  if (screen === "meal") {
    return <MealScreen goBack={() => setScreen("dashboard")} />;
  }

  return null;
}

export default App;
