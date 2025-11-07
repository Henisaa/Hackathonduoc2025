
import { GoogleGenAI, Type } from "@google/genai";
import { ActionPlanGoal, ChatMessage, MealAnalysis, RiskData, UserProfile } from '../types';

// FIX: Per @google/genai coding guidelines, API_KEY is expected to be in process.env and is a hard requirement.
const ai = new GoogleGenAI({ apiKey: process.env.API_KEY! });

const STATIC_KNOWLEDGE_BASE = `
- El programa se llama "CardioBien".
- Tu nombre es "CardioBot" y eres un asistente de salud amigable.
- Los 3 pilares de CardioBien son: Dieta, Ejercicio y Sueño.
- La meta de hidratación de la app es de 8 vasos de agua al día.
- El tabaquismo es un factor de riesgo muy impactante.
- La app ayuda a reducir el riesgo de diabetes e hipertensión (HTA).
- La app usa un puntaje de 0 a 1 (0% a 100%) para estimar el riesgo.
- Los planes de acción son de 2 semanas y usan metas SMART.
- El usuario puede registrar comidas (con fotos), actividad y peso.
`;

function getDynamicKnowledgeBase(userProfile: UserProfile, riskData: RiskData): string {
    const bmi = (userProfile.weight / ((userProfile.height / 100) ** 2)).toFixed(1);
    
    return `
    ---
    DATOS ACTUALES DEL USUARIO (CONFIDENCIAL):
    - Edad: ${userProfile.age} años
    - Sexo: ${userProfile.sex === 'male' ? 'Masculino' : 'Femenino'}
    - Peso: ${userProfile.weight} kg
    - Estatura: ${userProfile.height} cm
    - IMC: ${bmi}
    - Horas de sueño: ${userProfile.sleep}
    - Días de actividad: ${userProfile.activity}
    - Tabaquismo: ${userProfile.smoking}
    - Calidad de dieta: ${userProfile.diet}
    - RIESGO CALCULADO: ${riskData.label} (${Math.round(riskData.score * 100)}%)
    - PRINCIPALES FACTORES DE RIESGO: ${riskData.riskFactors.join(', ')}
    ---
    `;
}

export async function getChatResponse(
    history: ChatMessage[], 
    userMessage: string, 
    userProfile: UserProfile, 
    riskData: RiskData,
    isThinkingMode: boolean
): Promise<string> {
    const dynamicKnowledge = getDynamicKnowledgeBase(userProfile, riskData);
    const systemPrompt = `
Eres "CardioBot" 💖, un asistente de salud amigable, empático y motivador. 
Tu propósito es ayudar a los usuarios de la app "CardioBien".
Tu conocimiento está ESTRICTAMENTE LIMITADO al siguiente CONTEXTO. 
No respondas preguntas que no se puedan contestar usando solo este CONTEXTO.
Si te preguntan algo fuera de este CONTEXTO (ej. el clima, historia), responde amablemente: "Lo siento, solo puedo responder preguntas sobre el programa CardioBien (tu perfil, dieta, ejercicio, sueño, hidratación)."
Responde SIEMPRE en español de forma concisa.

CONTEXTO ESTATICO:
${STATIC_KNOWLEDGE_BASE}

${dynamicKnowledge}
`;
    
    const contents = [
        ...history.map(msg => ({
            role: msg.sender === 'user' ? 'user' : 'model',
            parts: [{ text: msg.text }]
        })),
        { role: 'user', parts: [{ text: userMessage }] }
    ];

    const modelName = isThinkingMode ? 'gemini-2.5-pro' : 'gemini-flash-lite-latest';
    const config: any = {
        systemInstruction: systemPrompt,
    };

    if (isThinkingMode) {
        config.thinkingConfig = { thinkingBudget: 32768 };
    }


    try {
        const response = await ai.models.generateContent({
            model: modelName,
            contents: contents,
            config: config
        });
        return response.text;
    } catch (error) {
        console.error("Gemini API Error (getChatResponse):", error);
        throw new Error("No pude conectarme con mi cerebro 🧠. Por favor, intenta de nuevo más tarde.");
    }
}

export async function analyzeProductWithAI(base64Image: string): Promise<MealAnalysis> {
    const prompt = "You are a nutritional expert for a health app. Analyze the attached image of a food product. First, identify the product. Then, provide a nutritional verdict. Respond ONLY with a JSON object following this schema: `{\"verdict\": string, \"explanation\": string}`. The 'verdict' must be one of three values in Spanish: 'Saludable', 'Moderado', or 'Poco Saludable'. The 'explanation' should be a brief, encouraging, one-sentence analysis in Spanish that includes the product name you identified. Be concise and friendly.";
    
    const imagePart = {
        inlineData: {
            data: base64Image,
            mimeType: 'image/jpeg'
        }
    };

    try {
        const response = await ai.models.generateContent({
            model: 'gemini-2.5-pro',
            contents: { parts: [imagePart, { text: prompt }] },
            config: {
                responseMimeType: "application/json",
                responseSchema: {
                    type: Type.OBJECT,
                    properties: {
                        verdict: { type: Type.STRING },
                        explanation: { type: Type.STRING }
                    },
                    required: ["verdict", "explanation"]
                }
            }
        });
        
        const jsonText = response.text;
        return JSON.parse(jsonText) as MealAnalysis;
    } catch (error) {
        console.error("Gemini API Error (analyzeProductWithAI):", error);
        throw new Error("Error al analizar la imagen del producto.");
    }
}

export async function getRecommendationWithAI(
    topic: 'sleep' | 'shopping' | 'exercise', 
    userProfile: UserProfile, 
    riskData: RiskData
): Promise<string> {
    const bmi = (userProfile.weight / ((userProfile.height / 100) ** 2)).toFixed(1);
    const userContext = `
    DATOS DEL USUARIO:
    - Edad: ${userProfile.age}, Sexo: ${userProfile.sex === 'male' ? 'Masculino' : 'Femenino'}
    - IMC: ${bmi}
    - Horas de sueño: ${userProfile.sleep}
    - Días de actividad: ${userProfile.activity}
    - Calidad de dieta: ${userProfile.diet}
    - Tabaquismo: ${userProfile.smoking}
    - Riesgo calculado: ${riskData.label} (${Math.round(riskData.score * 100)}%)
    - Factores de riesgo: ${riskData.riskFactors.join(', ')}
    `;

    let prompt = '';
    switch(topic) {
        case 'sleep':
            prompt = `Actúa como un coach de salud experto en sueño. Basado en los siguientes datos del usuario, dame 3 consejos prácticos y accionables para mejorar la calidad del sueño. Sé conciso, motivador y responde en español. Formatea la respuesta en una lista numerada.\n\n${userContext}`;
            break;
        case 'shopping':
            prompt = `Actúa como nutricionista. Basado en los siguientes datos del usuario, crea una lista de compras saludable con 5-7 productos versátiles que le ayuden a mejorar sus hábitos. Incluye una breve justificación (1 frase) para cada producto. Responde en español y formatea como una lista con viñetas.\n\n${userContext}`;
            break;
        case 'exercise':
            prompt = `Actúa como entrenador personal. Basado en los siguientes datos del usuario, sugiere una rutina de ejercicio simple para una semana, con 3 días de actividad. Describe el ejercicio y la duración/repeticiones para cada día. La rutina debe ser apropiada para su nivel de actividad y factores de riesgo. Responde en español y sé claro y alentador.\n\n${userContext}`;
            break;
    }

    try {
        const response = await ai.models.generateContent({
            model: 'gemini-2.5-pro',
            contents: prompt,
            config: {
                thinkingConfig: { thinkingBudget: 32768 }
            }
        });
        return response.text;
    } catch (error) {
        console.error("Gemini API Error (getRecommendationWithAI):", error);
        throw new Error("No pude generar la recomendación en este momento. Inténtalo de nuevo.");
    }
}

export async function generateActionPlanWithAI(riskFactors: string[]): Promise<ActionPlanGoal[]> {
    const prompt = `You are a health coach for an app. Based on the following user risk factors, create a simple and encouraging 2-week action plan. Provide 2 to 3 distinct goals. Respond ONLY with a JSON object following this schema: \`{\"goals\": Array<{\"goal\": string, \"details\": string}>}\`. The 'goal' should be a short title, and 'details' a one-sentence description of the task. All text must be in Spanish. Risk factors: [${riskFactors.join(', ')}]`;

    try {
        const response = await ai.models.generateContent({
            model: 'gemini-2.5-pro',
            contents: prompt,
            config: {
                responseMimeType: "application/json",
                responseSchema: {
                    type: Type.OBJECT,
                    properties: {
                        goals: {
                            type: Type.ARRAY,
                            items: {
                                type: Type.OBJECT,
                                properties: {
                                    goal: { type: Type.STRING },
                                    details: { type: Type.STRING }
                                },
                                required: ["goal", "details"]
                            }
                        }
                    },
                    required: ["goals"]
                },
                thinkingConfig: { thinkingBudget: 32768 }
            }
        });
        
        const jsonText = response.text;
        const result = JSON.parse(jsonText);
        return result.goals;
    } catch (error) {
        console.error("Gemini API Error (generateActionPlanWithAI):", error);
        throw new Error("Error al generar el plan de acción.");
    }
}