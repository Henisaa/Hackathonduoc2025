
import React, { useState, useEffect, useCallback, useRef, FormEvent } from 'react';
import { UserProfile, RiskData, ActionPlanGoal, HistoryLog, MealLog, ActivityLog, ChatMessage, MealAnalysis, ToastMessage } from './types';
import { getChatResponse, analyzeProductWithAI, generateActionPlanWithAI, getRecommendationWithAI } from './services/geminiService';

// --- Constants ---
const LOCALSTORAGE_PROFILE_KEY = 'cardiometabolic_profile';
const LOCALSTORAGE_GOALS_KEY = 'cardiometabolic_goals';
const LOCALSTORAGE_STREAK_KEY = 'cardiometabolic_streak';
const LOCALSTORAGE_WATER_KEY = 'cardiometabolic_water';
const LOCALSTORAGE_HISTORY_KEY = 'cardiometabolic_history';
const LOCALSTORAGE_THEME_KEY = 'cardiometabolic_theme';

const dailyTips = [
    "Beber un vaso de agua al despertar activa tu metabolismo.",
    "Un pequeño paseo de 10 minutos después de comer puede ayudar a la digestión.",
    "Intenta reemplazar un snack procesado por una fruta hoy.",
    "¿Sabías que la risa puede reducir la presión arterial? ¡Sonríe!",
    "Estacionar un poco más lejos y caminar cuenta como actividad.",
    "Prioriza 7-8 horas de sueño esta noche. Tu corazón te lo agradecerá.",
    "Un puñado de nueces es un snack saludable para el corazón.",
    "Intenta meditar por 5 minutos para reducir el estrés.",
    "Revisa las etiquetas de sodio. Menos de 1500mg al día es ideal."
];

const educationContent: Record<string, { title: string; text: string }> = {
    "sobrepeso": { title: "Sobrepeso e IMC", text: "El IMC (Índice de Masa Corporal) es una medida de la grasa corporal basada en la altura y el peso. Un IMC superior a 25 se considera sobrepeso. El exceso de peso ejerce presión sobre el corazón y puede llevar a presión arterial alta y diabetes tipo 2." },
    "obesidad": { title: "Obesidad e IMC", text: "Un IMC superior a 30 se considera obesidad, un factor de riesgo significativo para enfermedades cardíacas, accidentes cerebrovasculares y diabetes. Perder incluso una pequeña cantidad de peso (5-10%) puede mejorar drasticamente tu salud." },
    "baja actividad": { title: "Riesgo de Inactividad", text: "La inactividad física es un factor de riesgo principal. El ejercicio regular (como caminar 30 min/día) fortalece el corazón, mejora la circulación, ayuda a controlar el peso y reduce el estrés." },
    "fumador": { title: "Riesgo del Tabaquismo", text: "Fumar daña los vasos sanguíneos, reduce el oxígeno en la sangre y aumenta la presión arterial. Dejar de fumar es la acción más importante que puedes tomar para reducir tu riesgo cardiometabólico." },
    "pocas horas": { title: "Importancia del Sueño", text: "Dormir menos de 6-7 horas por noche está relacionado con un mayor riesgo de presión arterial alta, obesidad y diabetes. El sueño permite que tu cuerpo y corazón descansen y se reparen." },
    "dieta": { title: "Dieta y Salud", text: "Una dieta alta en alimentos procesados, azúcares y grasas saturadas contribuye directamente al sobrepeso y al colesterol alto. Priorizar frutas, verduras y granos enteros protege tu corazón." },
    "default": { title: "Factor de Riesgo", text: "Este es un factor que contribuye a tu riesgo cardiometabólico. Gestionarlo puede mejorar significativamente tu salud." }
};


// --- Helper Functions ---
const getTodayString = () => new Date().toDateString();

// --- Main App Component ---
export default function App() {
    const [currentScreen, setCurrentScreen] = useState<'loading' | 'profile' | 'dashboard' | 'mealLog' | 'chat'>('loading');
    const [userProfile, setUserProfile] = useState<UserProfile | null>(null);
    const [riskData, setRiskData] = useState<RiskData | null>(null);
    const [actionPlan, setActionPlan] = useState<ActionPlanGoal[]>([]);
    const [isPlanLoading, setIsPlanLoading] = useState(true);
    const [activeModal, setActiveModal] = useState<string | null>(null);
    const [modalContent, setModalContent] = useState({ title: '', text: '' });
    const [errorMessage, setErrorMessage] = useState('');
    const [isScreenTransitioning, setIsScreenTransitioning] = useState(false);
    const [toasts, setToasts] = useState<ToastMessage[]>([]);
    const [history, setHistory] = useState<HistoryLog[]>([]);
    const [isDarkMode, setIsDarkMode] = useState(() => {
        if (typeof window !== 'undefined') {
            return localStorage.getItem(LOCALSTORAGE_THEME_KEY) === 'dark';
        }
        return false;
    });

     useEffect(() => {
        if (isDarkMode) {
            document.documentElement.classList.add('dark');
            localStorage.setItem(LOCALSTORAGE_THEME_KEY, 'dark');
        } else {
            document.documentElement.classList.remove('dark');
            localStorage.setItem(LOCALSTORAGE_THEME_KEY, 'light');
        }
    }, [isDarkMode]);

    const addToast = useCallback((message: string, type: ToastMessage['type'] = 'info') => {
        const id = Date.now();
        setToasts(prev => [...prev, { id, message, type }]);
        setTimeout(() => removeToast(id), 4000);
    }, []);

    const removeToast = (id: number) => {
        setToasts(prev => prev.filter(t => t.id !== id));
    };

    const showError = useCallback((message: string) => {
        setErrorMessage(message);
        setActiveModal('error');
    }, []);

    const showScreen = useCallback((screenId: 'loading' | 'profile' | 'dashboard' | 'mealLog' | 'chat') => {
        setIsScreenTransitioning(true);
        setTimeout(() => {
            setCurrentScreen(screenId);
            setIsScreenTransitioning(false);
        }, 300); // Match CSS transition duration
    }, []);
    
    // --- Streak Logic ---
    const updateStreak = useCallback(() => {
        const today = getTodayString();
        const yesterday = new Date();
        yesterday.setDate(yesterday.getDate() - 1);
        const yesterdayStr = yesterday.toDateString();

        let streakData = JSON.parse(localStorage.getItem(LOCALSTORAGE_STREAK_KEY) || '{"currentStreak": 0, "lastLogDate": null}');
        if(streakData.lastLogDate !== today) {
            if(streakData.lastLogDate === yesterdayStr) {
                streakData.currentStreak += 1;
            } else {
                streakData.currentStreak = 1;
            }
            streakData.lastLogDate = today;
            localStorage.setItem(LOCALSTORAGE_STREAK_KEY, JSON.stringify(streakData));
        }
    }, []);

    const updateHistory = useCallback((newLog: HistoryLog) => {
        setHistory(prev => {
            const updated = [newLog, ...prev].slice(0, 20); // Keep last 20
            localStorage.setItem(LOCALSTORAGE_HISTORY_KEY, JSON.stringify(updated));
            return updated;
        });
        updateStreak();
    }, [updateStreak]);

    const handleMealLogged = useCallback((analysis: MealAnalysis) => {
        const newLog: MealLog = { 
            id: Date.now().toString(), 
            timestamp: new Date(), 
            type: 'Comida', 
            ...analysis 
        };
        updateHistory(newLog);
    }, [updateHistory]);

    // --- Profile & Risk Calculation ---
    useEffect(() => {
        const loadProfile = () => {
            try {
                const savedProfile = localStorage.getItem(LOCALSTORAGE_PROFILE_KEY);
                const savedHistory = JSON.parse(localStorage.getItem(LOCALSTORAGE_HISTORY_KEY) || '[]');
                setHistory(savedHistory.map((h:any) => ({...h, timestamp: new Date(h.timestamp)})));

                if (savedProfile) {
                    const profile = JSON.parse(savedProfile);
                    setUserProfile(profile);
                    showScreen('dashboard');
                } else {
                    showScreen('profile');
                }
            } catch (error) {
                console.error("Failed to load data from localStorage", error);
                showScreen('profile');
            }
        };
        loadProfile();
    }, [showScreen]);


    const handleProfileSave = (profile: UserProfile) => {
        localStorage.setItem(LOCALSTORAGE_PROFILE_KEY, JSON.stringify(profile));
        setUserProfile(profile);
        if (!sessionStorage.getItem('disclaimerShown')) {
            setActiveModal('disclaimer');
            sessionStorage.setItem('disclaimerShown', 'true');
        }
        showScreen('dashboard');
    };

    const handleProfileReset = () => {
        localStorage.clear();
        sessionStorage.clear();
        setUserProfile(null);
        setRiskData(null);
        setActionPlan([]);
        setHistory([]);
        showScreen('profile');
    };

    useEffect(() => {
        if (userProfile) {
            const calculateRisk = () => {
                let score = 0;
                const riskFactors: string[] = [];
                
                if (userProfile.age > 45) { score += 0.15; riskFactors.push("Edad mayor a 45"); }
                if (userProfile.age > 55) { score += 0.1; }

                const heightM = userProfile.height / 100;
                const bmi = userProfile.weight / (heightM * heightM);
                
                if (bmi >= 25 && bmi < 30) { score += 0.2; riskFactors.push(`Sobrepeso (IMC: ${bmi.toFixed(1)})`); }
                else if (bmi >= 30) { score += 0.3; riskFactors.push(`Obesidad (IMC: ${bmi.toFixed(1)})`); }

                if (userProfile.smoking === 'yes') { score += 0.25; riskFactors.push("Fumador actual"); }
                else if (userProfile.smoking === 'past') { score += 0.05; }

                if (userProfile.activity < 3) { score += 0.15; riskFactors.push("Baja actividad física (< 3 días/sem)"); }
                if (userProfile.sleep < 6) { score += 0.1; riskFactors.push("Pocas horas de sueño (< 6 horas)"); }
                if (userProfile.diet === 'poor') { score += 0.15; riskFactors.push("Dieta poco saludable"); }
                
                score = Math.min(Math.max(score, 0), 1);
                let label: 'Bajo' | 'Moderado' | 'Alto' = "Bajo";
                if (score > 0.3) label = "Moderado";
                if (score > 0.6) label = "Alto";
                if (riskFactors.length === 0 && score < 0.1) riskFactors.push("Riesgo bajo detectado");

                setRiskData({ score, label, riskFactors });
            };
            calculateRisk();
        }
    }, [userProfile]);

    useEffect(() => {
        if (riskData) {
            setIsPlanLoading(true);
            generateActionPlanWithAI(riskData.riskFactors)
                .then(goals => {
                    setActionPlan(goals);
                })
                .catch(error => {
                    console.error("Failed to generate action plan:", error);
                    // Fallback to a default plan
                    setActionPlan([{ goal: "Mantener Hábitos Saludables", details: "¡Sigue así! Intenta registrar tus comidas y actividad para mantener la conciencia sobre tus hábitos." }]);
                })
                .finally(() => {
                    setIsPlanLoading(false);
                });
        }
    }, [riskData]);


    const renderScreen = () => {
        const screenProps = { showScreen, showError, setActiveModal, addToast };
        switch (currentScreen) {
            case 'loading':
                return <div className="p-6 flex flex-col items-center justify-center min-h-screen"></div>;
            case 'profile':
                return <ProfileScreen onSave={handleProfileSave} {...screenProps} />;
            case 'dashboard':
                return userProfile && riskData ? <DashboardScreen
                    userProfile={userProfile}
                    setUserProfile={setUserProfile}
                    riskData={riskData}
                    actionPlan={actionPlan}
                    isPlanLoading={isPlanLoading}
                    history={history}
                    updateHistory={updateHistory}
                    onReset={handleProfileReset}
                    setModalContent={setModalContent}
                    activeModal={activeModal}
                    isDarkMode={isDarkMode}
                    toggleDarkMode={() => setIsDarkMode(prev => !prev)}
                    {...screenProps} /> : <div className="p-6 flex flex-col items-center justify-center min-h-screen dark:text-white">Cargando perfil...</div>;
            case 'mealLog':
                 return <MealLogScreen onMealLogged={handleMealLogged} {...screenProps} />;
            case 'chat':
                return userProfile && riskData ? <ChatScreen userProfile={userProfile} riskData={riskData} {...screenProps} /> : <div className="p-6 flex flex-col items-center justify-center min-h-screen dark:text-white">Cargando perfil...</div>;
            default:
                return <div className="p-6 text-red-500">Error: Pantalla no encontrada.</div>;
        }
    };

    return (
        <div className="container max-w-lg mx-auto bg-white dark:bg-gray-900 min-h-screen shadow-lg relative overflow-hidden">
            <div className={`screen ${currentScreen !== 'loading' && !isScreenTransitioning ? 'active' : ''}`}>
              {renderScreen()}
            </div>
            
            <div className="fixed top-5 right-5 z-[100] w-full max-w-sm">
                {toasts.map(toast => (
                    <Toast key={toast.id} {...toast} onClose={() => removeToast(toast.id)} />
                ))}
            </div>

            {/* Modals */}
            <Modal isOpen={activeModal === 'disclaimer'} onClose={() => setActiveModal(null)}>
                <div className="flex items-center">
                    <svg className="w-10 h-10 text-yellow-500 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>
                    <h3 className="text-xl font-bold text-gray-900 dark:text-white">Importante</h3>
                </div>
                <p className="mt-4 text-gray-600 dark:text-gray-300">Esta es una aplicación de demostración y <strong>no proporciona consejo médico real</strong>. El cálculo de riesgo y el análisis de comidas son simulaciones con fines ilustrativos.</p>
                <p className="mt-2 text-gray-600 dark:text-gray-300">No utilices esta aplicación para tomar decisiones reales sobre tu salud.</p>
                <button onClick={() => setActiveModal(null)} className="mt-6 w-full py-2 px-4 bg-blue-600 text-white font-medium rounded-md shadow hover:bg-blue-700">Entendido, continuar</button>
            </Modal>

            <Modal isOpen={activeModal === 'error'} onClose={() => setActiveModal(null)}>
                <div className="flex items-center">
                    <svg className="w-10 h-10 text-red-500 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                    <h3 className="text-xl font-bold text-gray-900 dark:text-white">Error</h3>
                </div>
                <p className="mt-4 text-gray-600 dark:text-gray-300">{errorMessage}</p>
                <button onClick={() => setActiveModal(null)} className="mt-6 w-full py-2 px-4 bg-red-600 text-white font-medium rounded-md shadow hover:bg-red-700">Cerrar</button>
            </Modal>

            <Modal isOpen={activeModal === 'education'} onClose={() => setActiveModal(null)}>
                 <div className="flex items-center">
                    <svg className="w-10 h-10 text-blue-500 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m12.728 0l.707-.707M6.343 17.657l-.707.707m12.728 0l.707.707M12 21v-1m0-16.5a7.5 7.5 0 00-7.5 7.5c0 3.067 1.83 5.693 4.5 6.91V17.5a.5.5 0 01.5.5h4a.5.5 0 01.5-.5v-1.09c2.67-1.217 4.5-3.843 4.5-6.91a7.5 7.5 0 00-7.5-7.5z"></path></svg>
                    <h3 className="text-xl font-bold text-gray-900 dark:text-white">{modalContent.title}</h3>
                </div>
                <p className="mt-4 text-gray-600 dark:text-gray-300">{modalContent.text}</p>
                 <button onClick={() => setActiveModal(null)} className="mt-6 w-full py-2 px-4 bg-blue-600 text-white font-medium rounded-md shadow hover:bg-blue-700">Entendido</button>
            </Modal>
             <Modal isOpen={activeModal === 'congrats'} onClose={() => setActiveModal(null)}>
                <div className="text-center">
                    <span className="text-7xl">🎉</span>
                    <h3 className="text-2xl font-bold text-gray-900 mt-4 dark:text-white">¡Felicidades!</h3>
                    <p className="mt-2 text-gray-600 dark:text-gray-300">¡Has completado todas tus metas del plan! Sigue así, estás haciendo un gran trabajo.</p>
                    <button onClick={() => setActiveModal(null)} className="mt-6 w-full py-2 px-4 bg-green-600 text-white font-medium rounded-md shadow hover:bg-green-700">¡Genial!</button>
                </div>
            </Modal>
        </div>
    );
}

// --- Screens ---

const ProfileScreen = ({ onSave }: { onSave: (profile: UserProfile) => void }) => {
    const [messages, setMessages] = useState<ChatMessage[]>([]);
    const [userInput, setUserInput] = useState('');
    const [profileData, setProfileData] = useState<Partial<UserProfile>>({});
    const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
    const [conversationState, setConversationState] = useState<'asking' | 'confirming' | 'finished'>('asking');
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const questions: { key: keyof UserProfile; question: string; type: 'number' | 'sex' | 'smoking' | 'diet' }[] = [
        { key: 'age', question: '¡Hola! Soy CardioBot y te ayudaré a crear tu perfil. Para empezar, ¿cuál es tu edad?', type: 'number' },
        { key: 'sex', question: 'Entendido. ¿Cuál es tu sexo biológico? (Masculino / Femenino)', type: 'sex' },
        { key: 'height', question: 'Perfecto. Ahora, dime tu estatura en centímetros.', type: 'number' },
        { key: 'weight', question: 'Gracias. ¿Cuál es tu peso actual en kilogramos?', type: 'number' },
        { key: 'sleep', question: 'Casi terminamos. En promedio, ¿cuántas horas duermes por noche?', type: 'number' },
        { key: 'activity', question: '¿Y cuántos días a la semana realizas al menos 30 minutos de actividad física?', type: 'number' },
        { key: 'smoking', question: 'Respecto al tabaco, ¿eres no fumador, ex-fumador o fumador actual?', type: 'smoking' },
        { key: 'diet', question: 'Finalmente, ¿cómo describirías la calidad de tu dieta? (Saludable, Promedio, o Poco saludable)', type: 'diet' },
    ];
    
    useEffect(() => {
        setMessages([{ sender: 'bot', text: questions[0].question }]);
    }, []);

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    const addMessage = (sender: 'user' | 'bot', text: string) => {
        setMessages(prev => [...prev, { sender, text }]);
    };
    
    const parseAnswer = (text: string, type: 'number' | 'sex' | 'smoking' | 'diet'): any => {
        const lowerText = text.toLowerCase();
        if (type === 'number') {
            const match = lowerText.match(/\d+(\.\d+)?/);
            return match ? parseFloat(match[0]) : null;
        }
        if (type === 'sex') {
            if (lowerText.includes('masculino') || lowerText.includes('hombre')) return 'male';
            if (lowerText.includes('femenino') || lowerText.includes('mujer')) return 'female';
            return null;
        }
        if (type === 'smoking') {
            if (lowerText.includes('no')) return 'no';
            if (lowerText.includes('ex')) return 'past';
            if (lowerText.includes('si') || lowerText.includes('actual')) return 'yes';
            return null;
        }
        if (type === 'diet') {
            if (lowerText.includes('saludable') || lowerText.includes('buena')) return 'good';
            if (lowerText.includes('promedio') || lowerText.includes('normal')) return 'average';
            if (lowerText.includes('poco saludable') || lowerText.includes('mala')) return 'poor';
            return null;
        }
        return null;
    };

    const handleConfirm = (input: string) => {
        const lowerInput = input.toLowerCase();
        if (lowerInput.includes('si') || lowerInput.includes('correcto')) {
            addMessage('bot', '¡Genial! Guardando tu perfil...');
            setConversationState('finished');
            setTimeout(() => {
                onSave(profileData as UserProfile);
            }, 1000);
        } else {
             addMessage('bot', 'De acuerdo, empecemos de nuevo para corregir los datos.');
             setProfileData({});
             setCurrentQuestionIndex(0);
             setConversationState('asking');
             setTimeout(() => {
                setMessages([{ sender: 'bot', text: questions[0].question }]);
             }, 500);
        }
    };
    
    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (!userInput.trim() || conversationState === 'finished') return;

        addMessage('user', userInput);
        
        if (conversationState === 'confirming') {
            handleConfirm(userInput);
            setUserInput('');
            return;
        }

        const currentQuestion = questions[currentQuestionIndex];
        const parsedValue = parseAnswer(userInput, currentQuestion.type);

        if (parsedValue !== null) {
            const updatedProfile = { ...profileData, [currentQuestion.key]: parsedValue };
            setProfileData(updatedProfile);

            const nextIndex = currentQuestionIndex + 1;
            if (nextIndex < questions.length) {
                setCurrentQuestionIndex(nextIndex);
                addMessage('bot', questions[nextIndex].question);
            } else {
                setConversationState('confirming');
                const summary = `¡Perfecto! He recopilado esta información. ¿Es correcta? (Sí/No)\n
- Edad: ${updatedProfile.age}
- Sexo: ${updatedProfile.sex === 'male' ? 'Masculino' : 'Femenino'}
- Estatura: ${updatedProfile.height} cm
- Peso: ${updatedProfile.weight} kg
- Sueño: ${updatedProfile.sleep} horas
- Actividad: ${updatedProfile.activity} días/sem
- Tabaquismo: ${updatedProfile.smoking}
- Dieta: ${updatedProfile.diet}`;
                addMessage('bot', summary);
            }
        } else {
            addMessage('bot', `No entendí bien. ${currentQuestion.question}`);
        }
        
        setUserInput('');
    };
    
    return (
         <div className="p-6 h-screen flex flex-col bg-white dark:bg-gray-900">
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-4 flex-shrink-0">Crea tu Perfil</h1>
            <div className="flex-1 p-4 space-y-4 overflow-y-auto flex flex-col bg-gray-50 dark:bg-gray-800 -mx-6">
                {messages.map((msg, index) => (
                    <div key={index} className={`chat-bubble max-w-[80%] px-4 py-2 rounded-2xl whitespace-pre-wrap ${msg.sender === 'user' ? 'bg-blue-600 text-white self-end rounded-br-md' : 'bg-gray-200 text-gray-800 self-start rounded-bl-md dark:bg-gray-700 dark:text-gray-200'}`}>
                        {msg.text}
                    </div>
                ))}
                 <div ref={messagesEndRef} />
            </div>
            <form onSubmit={handleSubmit} className="p-4 bg-white dark:bg-gray-900 border-t border-gray-200 dark:border-gray-700 flex items-center -mx-6 -mb-6 flex-shrink-0">
                <input
                    type="text"
                    value={userInput}
                    onChange={(e) => setUserInput(e.target.value)}
                    disabled={conversationState === 'finished'}
                    className="flex-1 block w-full px-4 py-3 border border-gray-300 rounded-full shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-800 dark:border-gray-600 dark:text-white dark:placeholder-gray-400"
                    placeholder={conversationState === 'asking' ? 'Escribe tu respuesta...' : 'Confirma (Sí/No)...'}
                    autoFocus
                />
                <button type="submit" disabled={!userInput.trim() || conversationState === 'finished'} className="ml-3 p-3 bg-blue-600 text-white rounded-full shadow-lg hover:bg-blue-700 focus:outline-none transition-transform active:scale-95 disabled:bg-blue-300">
                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"></path></svg>
                </button>
            </form>
        </div>
    );
};

const DashboardScreen = ({ userProfile, setUserProfile, riskData, actionPlan, isPlanLoading, history, updateHistory, onReset, showScreen, showError, setActiveModal, setModalContent, activeModal, isDarkMode, toggleDarkMode, addToast }: any) => {
    const [streak, setStreak] = useState(0);
    const [waterCount, setWaterCount] = useState(0);
    const [goals, setGoals] = useState<Record<string, boolean>>({});
    const [recommendationContent, setRecommendationContent] = useState<string | null>(null);
    const [isRecommendationLoading, setIsRecommendationLoading] = useState(false);
    
    useEffect(() => {
        const streakData = JSON.parse(localStorage.getItem(LOCALSTORAGE_STREAK_KEY) || '{"currentStreak": 0, "lastLogDate": null}');
        const today = getTodayString();
        const yesterday = new Date();
        yesterday.setDate(yesterday.getDate() - 1);
        if(streakData.lastLogDate && streakData.lastLogDate !== today && streakData.lastLogDate !== yesterday.toDateString()){
            streakData.currentStreak = 0;
            localStorage.setItem(LOCALSTORAGE_STREAK_KEY, JSON.stringify(streakData));
        }
        setStreak(streakData.currentStreak);

        const waterData = JSON.parse(localStorage.getItem(LOCALSTORAGE_WATER_KEY) || `{"count": 0, "date": "${today}"}`);
        if(waterData.date !== today) {
            setWaterCount(0);
            localStorage.setItem(LOCALSTORAGE_WATER_KEY, `{"count": 0, "date": "${today}"}`);
        } else {
            setWaterCount(waterData.count);
        }
        
        const savedGoals = JSON.parse(localStorage.getItem(LOCALSTORAGE_GOALS_KEY) || '{}');
        setGoals(savedGoals);
    }, []);
    
    const handleLogWater = () => {
        if(waterCount < 8) {
            const newCount = waterCount + 1;
            setWaterCount(newCount);
            localStorage.setItem(LOCALSTORAGE_WATER_KEY, JSON.stringify({count: newCount, date: getTodayString()}));
        }
    };
    
    const handleGoalCheck = (goalId: string, isChecked: boolean) => {
        const newGoals = {...goals, [goalId]: isChecked};
        setGoals(newGoals);
        localStorage.setItem(LOCALSTORAGE_GOALS_KEY, JSON.stringify(newGoals));

        const allChecked = actionPlan.every((_, index) => newGoals[`goal_${index}`]);
        if(allChecked && actionPlan.length > 0) {
            setActiveModal('congrats');
        }
    };

    const handleFactorClick = (factor: string) => {
        let factorKey = "default";
        if (factor.includes("Sobrepeso")) factorKey = "sobrepeso";
        else if (factor.includes("Obesidad")) factorKey = "obesidad";
        else if (factor.includes("Baja actividad")) factorKey = "baja actividad";
        else if (factor.includes("Fumador")) factorKey = "fumador";
        else if (factor.includes("Pocas horas")) factorKey = "pocas horas";
        else if (factor.includes("Dieta")) factorKey = "dieta";
        const content = educationContent[factorKey];
        setModalContent(content);
        setActiveModal('education');
    };
    
    const [currentTip, greeting] = React.useMemo(() => {
        const hour = new Date().getHours();
        const day = new Date().getDate();
        let calculatedGreeting = "¡Buenas noches!";
        if (hour < 12) calculatedGreeting = "¡Buenos días!";
        else if (hour < 19) calculatedGreeting = "¡Buenas tardes!";
        return [dailyTips[day % dailyTips.length], calculatedGreeting];
    }, []);

    const [activityType, setActivityType] = useState('Caminata');
    const [activityDuration, setActivityDuration] = useState('');
    
    const [profileFormData, setProfileFormData] = useState({
        weight: userProfile.weight.toString(),
        sleep: userProfile.sleep.toString(),
        diet: userProfile.diet,
    });

    const handleActivitySave = (e: FormEvent) => {
        e.preventDefault();
        if(!activityDuration || Number(activityDuration) <= 0) {
            showError("Por favor, ingresa una duración válida.");
            return;
        }
        const newLog: ActivityLog = { id: Date.now().toString(), timestamp: new Date(), type: 'Actividad', activityType, duration: Number(activityDuration) };
        updateHistory(newLog);
        // FIX: Corrected typo from `activeModal` to `setActiveModal`
        setActiveModal(null);
        setActivityDuration('');
        addToast('Actividad guardada con éxito', 'success');
    };

    const handleDataSave = (e: FormEvent) => {
        e.preventDefault();
        if (!profileFormData.weight || !profileFormData.sleep || Number(profileFormData.weight) <= 0 || Number(profileFormData.sleep) < 0) {
            showError("Por favor, ingresa valores válidos.");
            return;
        }
        const updatedProfile = {
            ...userProfile,
            weight: Number(profileFormData.weight),
            sleep: Number(profileFormData.sleep),
            diet: profileFormData.diet as UserProfile['diet'],
        };
        setUserProfile(updatedProfile);
        localStorage.setItem(LOCALSTORAGE_PROFILE_KEY, JSON.stringify(updatedProfile));
        // FIX: Corrected typo from `activeModal` to `setActiveModal`
        setActiveModal(null);
        addToast('Datos actualizados correctamente', 'success');
    };

    const openUpdateModal = () => {
        setProfileFormData({
            weight: userProfile.weight.toString(),
            sleep: userProfile.sleep.toString(),
            diet: userProfile.diet,
        });
        setActiveModal('updateData');
    };

    const handleGetRecommendation = async (topic: 'sleep' | 'shopping' | 'exercise') => {
        setIsRecommendationLoading(true);
        setRecommendationContent(null);
        try {
            const recommendation = await getRecommendationWithAI(topic, userProfile, riskData);
            setRecommendationContent(recommendation);
        } catch (error: any) {
            setRecommendationContent(`Error: ${error.message || "No se pudo obtener la recomendación."}`);
        } finally {
            setIsRecommendationLoading(false);
        }
    };

    const resetRecommendations = () => {
        setRecommendationContent(null);
        setIsRecommendationLoading(false);
    };

    return (
        <div className="p-6 space-y-6 overflow-y-auto h-screen pb-24">
            <div className="flex justify-between items-center">
                <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Tu Resumen</h1>
                 <div className="flex items-center space-x-2">
                    <DarkModeToggle isDarkMode={isDarkMode} toggleDarkMode={toggleDarkMode} />
                    <button onClick={onReset} title="Reiniciar Perfil (Demo)" className="text-gray-500 hover:text-red-600 dark:text-gray-400 dark:hover:text-red-500">
                        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path></svg>
                    </button>
                </div>
            </div>
            
            <div className="bg-gradient-to-r from-blue-500 to-indigo-600 text-white rounded-lg shadow-lg p-6">
                <h2 className="text-2xl font-bold">{greeting}</h2>
                <p className="mt-2 text-blue-100">Aquí tienes tu consejo de hoy:</p>
                <p className="mt-1 font-medium text-lg">"{currentTip}"</p>
            </div>
            
            {streak > 0 && (
                <div className="text-center p-3 bg-amber-100 text-amber-800 rounded-lg shadow dark:bg-amber-900 dark:text-amber-200">
                    <span className="text-2xl">🔥</span>
                    <p className="font-semibold">¡Racha de {streak} días registrando!</p>
                </div>
            )}
            
            <RiskGauge riskData={riskData} />
            
            <WaterTracker count={waterCount} onLog={handleLogWater} />

            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
                <div className="flex justify-between items-center mb-3">
                    <h2 className="text-lg font-semibold text-gray-800 dark:text-gray-100">Principales Factores de Riesgo</h2>
                    <button onClick={openUpdateModal} className="text-sm font-medium text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300">Actualizar Datos</button>
                </div>
                <ul className="space-y-2">
                    {riskData.riskFactors.map(factor => (
                        <li key={factor} onClick={() => handleFactorClick(factor)} className="flex items-center text-gray-700 dark:text-gray-300 p-2 rounded-md cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700">
                             <svg className="w-5 h-5 text-yellow-500 mr-2 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>
                            <span>{factor}</span>
                        </li>
                    ))}
                </ul>
            </div>

            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
                <h2 className="text-lg font-semibold text-gray-800 dark:text-gray-100 mb-3">Tu Plan de Acción (2 Semanas)</h2>
                {isPlanLoading ? (
                    <div className="flex items-center text-gray-500 dark:text-gray-400">
                        <Spinner />
                        <span>Generando tu plan personalizado...</span>
                    </div>
                ) : (
                    <form className="space-y-4">
                        {actionPlan.map((item, index) => {
                             const goalId = `goal_${index}`;
                             return (
                                <div key={goalId} className="flex items-start">
                                    <input type="checkbox" id={goalId} checked={!!goals[goalId]} onChange={(e) => handleGoalCheck(goalId, e.target.checked)} className="h-5 w-5 accent-blue-600 rounded mt-1"/>
                                    <label htmlFor={goalId} className="ml-3 flex-1">
                                        <h4 className="font-semibold text-gray-800 dark:text-gray-200">{item.goal}</h4>
                                        <p className="text-sm text-gray-600 dark:text-gray-400">{item.details}</p>
                                    </label>
                                </div>
                             )
                        })}
                    </form>
                )}
            </div>

            <ActionButtons onLogMeal={() => showScreen('mealLog')} onLogActivity={() => setActiveModal('activity')} onOpenChat={() => showScreen('chat')} onShowRecommendations={() => { resetRecommendations(); setActiveModal('recommendations'); }} />

            <HistoryList history={history} />
            
            <div className="h-4"></div>

             <Modal isOpen={activeModal === 'activity'} onClose={() => setActiveModal(null)}>
                <form onSubmit={handleActivitySave}>
                    <h3 className="text-xl font-bold text-gray-900 dark:text-white">Registrar Actividad</h3>
                    <p className="mt-2 text-gray-600 dark:text-gray-300">¡Genial! ¿Qué actividad completaste?</p>
                    <div className="mt-4 space-y-3">
                        <div>
                            <label htmlFor="activity-type" className="block text-sm font-medium text-gray-700 dark:text-gray-300">Tipo de Actividad</label>
                            <select id="activity-type" value={activityType} onChange={e => setActivityType(e.target.value)} className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white">
                                <option>Caminata</option><option>Correr</option><option>Gimnasio</option><option>Bicicleta</option><option>Otro</option>
                            </select>
                        </div>
                        <div>
                            <label htmlFor="activity-duration" className="block text-sm font-medium text-gray-700 dark:text-gray-300">Duración (minutos)</label>
                            <input type="number" id="activity-duration" value={activityDuration} onChange={e => setActivityDuration(e.target.value)} className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white" placeholder="Ej: 30" required/>
                        </div>
                    </div>
                    <div className="bg-gray-50 dark:bg-gray-700 -mx-6 -mb-6 px-6 py-3 mt-6 flex justify-end space-x-2">
                        <button type="button" onClick={() => setActiveModal(null)} className="py-2 px-4 bg-gray-200 text-gray-700 font-medium rounded-md hover:bg-gray-300 dark:bg-gray-600 dark:text-gray-200 dark:hover:bg-gray-500">Cancelar</button>
                        <button type="submit" className="py-2 px-4 bg-purple-600 text-white font-medium rounded-md shadow hover:bg-purple-700">Guardar Actividad</button>
                    </div>
                </form>
            </Modal>
            
             {/* FIX: Corrected typo from `activeModal` to `setActiveModal` in onClose handler */}
             <Modal isOpen={activeModal === 'recommendations'} onClose={() => setActiveModal(null)}>
                <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4">Recomendaciones IA</h3>
                {isRecommendationLoading ? (
                    <div className="text-center p-8">
                        <Spinner />
                        <p className="mt-2 text-gray-600 dark:text-gray-300">Generando tu recomendación personalizada...</p>
                    </div>
                ) : recommendationContent ? (
                    <div>
                        <div className="max-h-60 overflow-y-auto p-3 bg-gray-50 dark:bg-gray-700 rounded-md">
                           <div className="text-gray-700 dark:text-gray-200 whitespace-pre-wrap text-sm">{recommendationContent}</div>
                        </div>
                        <button onClick={resetRecommendations} className="mt-4 w-full flex justify-center py-2 px-4 border border-gray-300 dark:border-gray-500 rounded-md shadow-sm text-sm font-medium text-gray-700 dark:text-gray-200 bg-white dark:bg-gray-600 hover:bg-gray-50 dark:hover:bg-gray-500">
                            Volver
                        </button>
                    </div>
                ) : (
                    <div className="space-y-3">
                        <p className="text-gray-600 dark:text-gray-300">Elige una categoría para obtener una recomendación personalizada de nuestra IA.</p>
                        <button onClick={() => handleGetRecommendation('sleep')} className="w-full text-left p-3 bg-blue-50 hover:bg-blue-100 rounded-lg font-medium text-blue-800 transition-colors dark:bg-blue-900/50 dark:hover:bg-blue-900/80 dark:text-blue-200">🌙 Métodos para dormir mejor</button>
                        <button onClick={() => handleGetRecommendation('shopping')} className="w-full text-left p-3 bg-green-50 hover:bg-green-100 rounded-lg font-medium text-green-800 transition-colors dark:bg-green-900/50 dark:hover:bg-green-900/80 dark:text-green-200">🛒 Lista de compras saludable</button>
                        <button onClick={() => handleGetRecommendation('exercise')} className="w-full text-left p-3 bg-purple-50 hover:bg-purple-100 rounded-lg font-medium text-purple-800 transition-colors dark:bg-purple-900/50 dark:hover:bg-purple-900/80 dark:text-purple-200">💪 Rutinas de ejercicio</button>
                    </div>
                )}
            </Modal>

            <Modal isOpen={activeModal === 'updateData'} onClose={() => setActiveModal(null)}>
                 <form onSubmit={handleDataSave}>
                    <h3 className="text-xl font-bold text-gray-900 dark:text-white">Actualizar Datos</h3>
                    <p className="mt-2 text-gray-600 dark:text-gray-300">Mantén tu perfil al día para un cálculo de riesgo preciso.</p>
                    <div className="mt-4 space-y-4">
                        <div>
                            <label htmlFor="update-weight" className="block text-sm font-medium text-gray-700 dark:text-gray-300">Peso Actual (kg)</label>
                            <input type="number" id="update-weight" step="0.1" value={profileFormData.weight} onChange={e => setProfileFormData({...profileFormData, weight: e.target.value})} className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white" required/>
                        </div>
                        <div>
                            <label htmlFor="update-sleep" className="block text-sm font-medium text-gray-700 dark:text-gray-300">Horas de sueño promedio</label>
                            <input type="number" id="update-sleep" step="1" value={profileFormData.sleep} onChange={e => setProfileFormData({...profileFormData, sleep: e.target.value})} className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white" required/>
                        </div>
                        <div>
                            <label htmlFor="update-diet" className="block text-sm font-medium text-gray-700 dark:text-gray-300">Calidad de la dieta</label>
                            <select id="update-diet" value={profileFormData.diet} onChange={e => setProfileFormData({...profileFormData, diet: e.target.value as UserProfile['diet']})} className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white">
                                <option value="poor">Poco saludable</option>
                                <option value="average">Promedio</option>
                                <option value="good">Saludable</option>
                            </select>
                        </div>
                    </div>
                    <div className="bg-gray-50 dark:bg-gray-700 -mx-6 -mb-6 px-6 py-3 mt-6 flex justify-end space-x-2">
                        <button type="button" onClick={() => setActiveModal(null)} className="py-2 px-4 bg-gray-200 text-gray-700 font-medium rounded-md hover:bg-gray-300 dark:bg-gray-600 dark:text-gray-200 dark:hover:bg-gray-500">Cancelar</button>
                        <button type="submit" className="py-2 px-4 bg-blue-600 text-white font-medium rounded-md shadow hover:bg-blue-700">Guardar Cambios</button>
                    </div>
                 </form>
            </Modal>
        </div>
    );
};

const MealLogScreen = ({ showScreen, showError, addToast, onMealLogged }: any) => {
    const videoRef = useRef<HTMLVideoElement>(null);
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const streamRef = useRef<MediaStream | null>(null);

    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [analysisResult, setAnalysisResult] = useState<MealAnalysis | null>(null);
    const [photoTaken, setPhotoTaken] = useState(false);
    const [isCameraReady, setIsCameraReady] = useState(false);

    const stopCamera = useCallback(() => {
        if (streamRef.current) {
            streamRef.current.getTracks().forEach(track => track.stop());
            streamRef.current = null;
        }
        if (videoRef.current) {
            videoRef.current.srcObject = null;
            videoRef.current.onloadedmetadata = null;
        }
        setIsCameraReady(false);
    }, []);

    const startCamera = useCallback(async () => {
        if (streamRef.current) {
            stopCamera();
        }
        
        setAnalysisResult(null);
        setPhotoTaken(false);
        setIsCameraReady(false);

        try {
            const mediaStream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } });
            streamRef.current = mediaStream;
            if (videoRef.current) {
                videoRef.current.srcObject = mediaStream;
                videoRef.current.onloadedmetadata = () => {
                    setIsCameraReady(true);
                };
            }
        } catch (err) {
            console.error(err);
            showError("No se pudo acceder a la cámara. Revisa los permisos.");
            showScreen('dashboard');
        }
    }, [showError, showScreen, stopCamera]);

    useEffect(() => {
        startCamera();
        return () => {
            stopCamera();
        };
    }, [startCamera, stopCamera]);

    const handleTakePhoto = async () => {
        if (!videoRef.current || !canvasRef.current || !isCameraReady) return;
        
        const video = videoRef.current;
        const canvas = canvasRef.current;
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        canvas.getContext('2d')?.drawImage(video, 0, 0, video.videoWidth, video.videoHeight);
        
        stopCamera();
        setPhotoTaken(true);
        setIsAnalyzing(true);
        setAnalysisResult(null);

        const base64Image = canvas.toDataURL('image/jpeg', 0.8).split(',')[1];

        try {
            const result = await analyzeProductWithAI(base64Image);
            setAnalysisResult(result);
            addToast('Producto analizado con éxito', 'success');
            onMealLogged(result);
        } catch (error: any) {
            showError(error.message || "Error al analizar el producto.");
            setPhotoTaken(false); 
            startCamera(); 
        } finally {
            setIsAnalyzing(false);
        }
    };

    return (
        <div className="p-6 h-screen flex flex-col">
            <button onClick={() => showScreen('dashboard')} className="text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300 mb-4 flex items-center self-start">
                <svg className="w-5 h-5 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 19l-7-7 7-7"></path></svg>
                Volver
            </button>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">Analizar Producto</h1>
            
            <div className="mb-4 bg-gray-900 dark:bg-black rounded-lg overflow-hidden flex-grow flex items-center justify-center relative">
                <video ref={videoRef} playsInline autoPlay muted className={`${!photoTaken ? 'block' : 'hidden'} w-full h-auto max-h-full`}></video>
                <canvas ref={canvasRef} className={`${photoTaken ? 'block' : 'hidden'} w-full h-auto max-h-full`}></canvas>
                {!isCameraReady && !photoTaken && !isAnalyzing && <p className="text-gray-400 absolute">Iniciando cámara...</p>}
            </div>

            {!analysisResult && (
                <button onClick={handleTakePhoto} disabled={isAnalyzing || !isCameraReady} className="w-full flex justify-center py-3 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none disabled:bg-blue-300 disabled:cursor-not-allowed">
                    {isAnalyzing ? <Spinner /> : <><CameraIcon /> <span className="ml-2">Tomar Foto</span></>}
                </button>
            )}
            
            {isAnalyzing && (
                 <div className="mt-6 text-center">
                    <Spinner size="8" />
                    <p className="text-gray-600 dark:text-gray-300 mt-2">Analizando tu producto con IA...</p>
                </div>
            )}

            {analysisResult && !isAnalyzing && (
                <div className="mt-6">
                    <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-100 mb-2">Análisis de IA</h3>
                    <AnalysisCard analysis={analysisResult} />
                     <button onClick={startCamera} className="mt-4 w-full flex justify-center py-2 px-4 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm text-sm font-medium text-gray-700 dark:text-gray-200 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600">
                        Tomar otra foto
                    </button>
                </div>
            )}
        </div>
    );
};

const ChatScreen = ({ userProfile, riskData, showScreen, showError }: any) => {
    const [messages, setMessages] = useState<ChatMessage[]>([
        { sender: 'bot', text: '¡Hola! Soy CardioBot 💖. Puedo ver tu perfil y factores de riesgo. ¿En qué te puedo ayudar hoy?' }
    ]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [isThinkingMode, setIsThinkingMode] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages]);

    const handleSubmit = async (e: FormEvent) => {
        e.preventDefault();
        if (!input.trim() || isLoading) return;

        const userMessage: ChatMessage = { sender: 'user', text: input };
        const newMessages = [...messages, userMessage];
        setMessages(newMessages);
        setInput('');
        setIsLoading(true);

        try {
            const responseText = await getChatResponse(newMessages.slice(1), userMessage.text, userProfile, riskData, isThinkingMode);
            setMessages(prev => [...prev, { sender: 'bot', text: responseText }]);
        } catch (error: any) {
            showError(error.message);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="flex flex-col h-screen">
            <header className="p-4 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
                <div className="flex items-center">
                    <button onClick={() => showScreen('dashboard')} className="text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300 mr-2">
                        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 19l-7-7 7-7"></path></svg>
                    </button>
                    <h1 className="text-xl font-bold text-gray-900 dark:text-white">Chat Asistente</h1>
                </div>

                <div className="flex items-center space-x-2" title={isThinkingMode ? "Modo Avanzado: Usa un modelo más potente para respuestas complejas (puede ser más lento)." : "Modo Rápido: Optimizado para respuestas rápidas."}>
                    <svg className={`w-5 h-5 transition-colors ${isThinkingMode ? 'text-purple-600' : 'text-gray-400'}`} xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.477 2 2 6.477 2 12s4.477 10 10 10 10-4.477 10-10S17.523 2 12 2ZM8 12.5A1.5 1.5 0 1 1 6.5 11 1.5 1.5 0 0 1 8 12.5ZM13.5 12.5A1.5 1.5 0 1 1 12 11a1.5 1.5 0 0 1 1.5 1.5ZM19 12.5a1.5 1.5 0 1 1-1.5-1.5A1.5 1.5 0 0 1 19 12.5Z" /></svg>
                    <span className="text-sm font-medium text-gray-600 dark:text-gray-300">{isThinkingMode ? "Avanzado" : "Rápido"}</span>
                    <label htmlFor="thinking-toggle" className="relative inline-flex items-center cursor-pointer">
                        <input type="checkbox" id="thinking-toggle" className="sr-only peer" checked={isThinkingMode} onChange={() => setIsThinkingMode(!isThinkingMode)} />
                        <div className="w-11 h-6 bg-gray-200 dark:bg-gray-600 rounded-full peer peer-focus:ring-2 peer-focus:ring-blue-300 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-0.5 after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-purple-600"></div>
                    </label>
                </div>
            </header>
            
            <div className="flex-1 p-4 space-y-4 overflow-y-auto flex flex-col bg-gray-50 dark:bg-gray-900">
                {messages.map((msg, index) => (
                    <div key={index} className={`chat-bubble max-w-[80%] px-4 py-2 rounded-2xl ${msg.sender === 'user' ? 'bg-blue-600 text-white self-end rounded-br-md' : 'bg-gray-200 text-gray-800 self-start rounded-bl-md dark:bg-gray-700 dark:text-gray-200'}`}>
                        {msg.text}
                    </div>
                ))}
                {isLoading && (
                    <div className="chat-bubble bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-gray-200 self-start rounded-bl-md px-4 py-3">
                        <div className="flex items-center">
                            <span className="typing-dot"></span><span className="typing-dot"></span><span className="typing-dot"></span>
                        </div>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>
            
            <form onSubmit={handleSubmit} className="p-4 bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 flex items-center">
                <input type="text" value={input} onChange={(e) => setInput(e.target.value)} className="flex-1 block w-full px-4 py-3 border border-gray-300 rounded-full shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white" placeholder="Pregúntame sobre tu riesgo..." />
                <button type="submit" disabled={isLoading} className="ml-3 p-3 bg-blue-600 text-white rounded-full shadow-lg hover:bg-blue-700 focus:outline-none transition-transform active:scale-95 disabled:bg-blue-300">
                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"></path></svg>
                </button>
            </form>
        </div>
    );
};


// --- UI Components ---
const Modal = ({ isOpen, onClose, children }: { isOpen: boolean; onClose: () => void; children: React.ReactNode }) => {
    if (!isOpen) return null;
    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex justify-center items-center" onClick={onClose}>
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-sm m-4 p-6" onClick={e => e.stopPropagation()}>
                {children}
            </div>
        </div>
    );
};

const Toast = ({ message, type, onClose }: { message: string; type: ToastMessage['type']; onClose: () => void }) => {
    const bgColor = {
        success: 'bg-green-500',
        info: 'bg-blue-500',
        error: 'bg-red-500',
    }[type];

    useEffect(() => {
        const timer = setTimeout(onClose, 4000);
        return () => clearTimeout(timer);
    }, [onClose]);

    return (
        <div className={`text-white px-6 py-4 border-0 rounded-md relative mb-4 ${bgColor} shadow-lg transition-all duration-300 animate-fade-in-up`}>
            <span className="inline-block align-middle mr-8">
                {message}
            </span>
            <button className="absolute bg-transparent text-2xl font-semibold leading-none right-0 top-0 mt-4 mr-6 outline-none focus:outline-none" onClick={onClose}>
                <span>×</span>
            </button>
        </div>
    );
};

const Spinner = ({ size = "5" }: { size?: string }) => (
    <svg className={`spinner w-${size} h-${size} text-blue-600 dark:text-blue-400 mx-auto`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4.75v1.5M12 17.75v1.5M17.708 6.292l-1.06 1.06M7.352 16.648l-1.06 1.06M19.25 12h-1.5M6.25 12h-1.5M17.708 17.708l-1.06-1.06M7.352 7.352l-1.06-1.06" />
    </svg>
);

const RiskGauge = ({ riskData }: { riskData: RiskData }) => {
    const [facePath, setFacePath] = useState('M35 75 Q 50 85 65 75');
    const [avatarTitle, setAvatarTitle] = useState('Estoy aquí para ayudarte.');

    useEffect(() => {
        if(riskData.label === 'Bajo') {
            setFacePath('M35 75 Q 50 85 65 75');
            setAvatarTitle('¡Me siento genial! Tu riesgo es bajo.');
        } else if (riskData.label === 'Moderado') {
            setFacePath('M35 78 H 65');
            setAvatarTitle('Tu riesgo es moderado. ¡Podemos mejorarlo!');
        } else {
            setFacePath('M35 80 Q 50 70 65 80');
            setAvatarTitle('Tu riesgo es alto. Estoy aquí para ayudarte a reducirlo.');
        }
    }, [riskData.label]);
    
    return (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
            <h2 className="text-lg font-semibold text-gray-800 dark:text-gray-100 mb-2 text-center">Riesgo Cardiometabólico</h2>
            <div className="flex justify-center items-center my-4">
                <svg id="heart-avatar" className="w-24 h-24" viewBox="0 0 100 90">
                    <title>{avatarTitle}</title>
                    <path d="M50 30C20 30 10 60 10 70C10 90 30 90 50 90C70 90 90 90 90 70C90 60 80 30 50 30Z" fill="#FF5A5F"/>
                    <g transform="translate(0, 5)">
                        <circle cx="35" cy="65" r="4" fill="#333"/><circle cx="65" cy="65" r="4" fill="#333"/>
                        <path id="heart-face-path" d={facePath} stroke="#333" strokeWidth="3" fill="none" strokeLinecap="round"/>
                    </g>
                </svg>
            </div>
            <div className="gauge">
                <div className="gauge-body"></div>
                <div className="gauge-fill" style={{ '--gauge-angle': `${riskData.score * 180}deg` } as React.CSSProperties}></div>
                <div className="gauge-cover"></div>
                <div className="gauge-value dark:text-white">{Math.round(riskData.score * 100)}%</div>
                <div className="gauge-label">{riskData.label}</div>
            </div>
        </div>
    );
};

const WaterTracker = ({ count, onLog }: { count: number; onLog: () => void }) => (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
        <h2 className="text-lg font-semibold text-gray-800 dark:text-gray-100 mb-3">Tu Hidratación Hoy</h2>
        <div className="flex justify-around items-center py-2">
            {Array.from({ length: 8 }).map((_, i) => (
                <svg key={i} className={`w-8 h-8 transition-colors duration-300 ${i < count ? 'text-blue-500 fill-current' : 'text-gray-300 dark:text-gray-600 fill-current'}`} viewBox="0 0 24 24">
                    <path d="M4 4h16v2.707c0 1.32-.524 2.57-1.46 3.515L15 14.83V19a1 1 0 01-1 1H10a1 1 0 01-1-1v-4.17l-3.54-4.608C4.524 9.277 4 8.027 4 6.707V4z"/>
                </svg>
            ))}
        </div>
        <button onClick={onLog} disabled={count >= 8} className="mt-3 w-full flex justify-center items-center py-2 px-4 border font-medium rounded-md shadow-sm focus:outline-none disabled:opacity-50 disabled:cursor-not-allowed border-blue-500 text-blue-500 hover:bg-blue-50 dark:border-blue-400 dark:text-blue-400 dark:hover:bg-blue-900/40">
            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path></svg>
            {count >= 8 ? "¡Hidratación Completa!" : "Registrar 1 Vaso de Agua"}
        </button>
    </div>
);

const ActionButtons = ({ onLogMeal, onLogActivity, onOpenChat, onShowRecommendations }: any) => (
    <div className="grid grid-cols-2 gap-4">
        <button onClick={onLogMeal} className="flex flex-col items-center justify-center p-3 bg-green-500 text-white rounded-lg shadow hover:bg-green-600 transition-colors">
            <CameraIcon />
            <span className="font-medium text-sm text-center">Analizar Producto</span>
        </button>
        <button onClick={onLogActivity} className="flex flex-col items-center justify-center p-3 bg-purple-500 text-white rounded-lg shadow hover:bg-purple-600 transition-colors">
            <svg className="w-8 h-8 mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>
            <span className="font-medium text-sm text-center">Registrar Actividad</span>
        </button>
        <button onClick={onOpenChat} className="flex flex-col items-center justify-center p-3 bg-blue-500 text-white rounded-lg shadow hover:bg-blue-600 transition-colors">
            <svg className="w-8 h-8 mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 21l1.398-3.73C3.54 16.502 3 15.293 3 14c0-4.418 4.03-8 9-8s9 3.582 9 8z"></path></svg>
            <span className="font-medium text-sm text-center">Chat Asistente</span>
        </button>
         <button onClick={onShowRecommendations} className="flex flex-col items-center justify-center p-3 bg-yellow-500 text-white rounded-lg shadow hover:bg-yellow-600 transition-colors">
            <svg className="w-8 h-8 mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m12.728 0l.707-.707M6.343 17.657l-.707.707m12.728 0l.707.707M12 21v-1m0-16.5a7.5 7.5 0 00-7.5 7.5c0 3.067 1.83 5.693 4.5 6.91V17.5a.5.5 0 01.5.5h4a.5.5 0 01.5-.5v-1.09c2.67-1.217 4.5-3.843 4.5-6.91a7.5 7.5 0 00-7.5-7.5z"></path></svg>
            <span className="font-medium text-sm text-center">Recomendaciones</span>
        </button>
    </div>
);

const HistoryList = ({ history }: { history: HistoryLog[] }) => (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
        <h2 className="text-lg font-semibold text-gray-800 dark:text-gray-100 mb-3">Historial de Registros</h2>
        <div className="space-y-3 max-h-60 overflow-y-auto">
            {history.length === 0 ? (
                <p className="text-gray-500 dark:text-gray-400">Aún no has registrado nada.</p>
            ) : (
                history.map(log => (
                    <div key={log.id} className="border-b border-gray-200 dark:border-gray-700 pb-2 last:border-b-0">
                        {log.type === "Comida" ? <MealHistoryItem log={log} /> : <ActivityHistoryItem log={log} />}
                    </div>
                ))
            )}
        </div>
    </div>
);

const MealHistoryItem = ({ log }: { log: MealLog }) => {
    let iconColor = 'text-red-500';
    if(log.verdict === 'Saludable') iconColor = 'text-green-500';
    if(log.verdict === 'Moderado') iconColor = 'text-yellow-500';
    return(
        <>
            <div className="flex items-center">
                <svg className={`w-5 h-5 ${iconColor} mr-2`} fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                <span className="font-medium dark:text-gray-200">{log.verdict} (Producto)</span>
                <span className="text-xs text-gray-500 dark:text-gray-400 ml-auto">{log.timestamp.toLocaleTimeString('es-ES', {hour:'2-digit', minute:'2-digit'})}</span>
            </div>
            <p className="text-sm text-gray-600 dark:text-gray-400 ml-7">{log.explanation}</p>
        </>
    )
};

const ActivityHistoryItem = ({ log }: { log: ActivityLog }) => (
     <>
        <div className="flex items-center">
            <svg className="w-5 h-5 text-purple-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>
            <span className="font-medium dark:text-gray-200">{log.activityType}</span>
            <span className="text-xs text-gray-500 dark:text-gray-400 ml-auto">{log.timestamp.toLocaleTimeString('es-ES', {hour:'2-digit', minute:'2-digit'})}</span>
        </div>
        <p className="text-sm text-gray-600 dark:text-gray-400 ml-7">Duración: {log.duration} minutos.</p>
    </>
);

const AnalysisCard = ({ analysis }: { analysis: MealAnalysis }) => {
    let bgColor, textColor, borderColor, darkBgColor, darkTextColor, darkBorderColor;
    switch (analysis.verdict) {
        case 'Saludable': 
            [bgColor, textColor, borderColor] = ['bg-green-100', 'text-green-800', 'border-green-300'];
            [darkBgColor, darkTextColor, darkBorderColor] = ['dark:bg-green-900/50', 'dark:text-green-200', 'dark:border-green-700'];
            break;
        case 'Moderado': 
            [bgColor, textColor, borderColor] = ['bg-yellow-100', 'text-yellow-800', 'border-yellow-300'];
            [darkBgColor, darkTextColor, darkBorderColor] = ['dark:bg-yellow-900/50', 'dark:text-yellow-200', 'dark:border-yellow-700'];
            break;
        default: 
            [bgColor, textColor, borderColor] = ['bg-red-100', 'text-red-800', 'border-red-300'];
            [darkBgColor, darkTextColor, darkBorderColor] = ['dark:bg-red-900/50', 'dark:text-red-200', 'dark:border-red-700'];
    }
    return (
        <div className={`p-4 rounded-lg border ${bgColor} ${textColor} ${borderColor} ${darkBgColor} ${darkTextColor} ${darkBorderColor}`}>
            <div className="flex items-center"><strong className="text-lg">{analysis.verdict}</strong></div>
            <p className="mt-2">{analysis.explanation}</p>
        </div>
    );
};

// SVG Icons
const CameraIcon = () => <svg className="w-8 h-8 mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"></path><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z"></path></svg>;

const DarkModeToggle = ({ isDarkMode, toggleDarkMode }: { isDarkMode: boolean; toggleDarkMode: () => void; }) => (
    <button onClick={toggleDarkMode} title="Toggle Dark Mode" className="p-2 rounded-full text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors">
        {isDarkMode ? (
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"></path></svg>
        ) : (
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"></path></svg>
        )}
    </button>
);
