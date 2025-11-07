export interface UserProfile {
    age: number;
    sex: 'male' | 'female';
    height: number;
    weight: number;
    sleep: number;
    activity: number;
    smoking: 'no' | 'past' | 'yes';
    diet: 'poor' | 'average' | 'good';
}

export interface RiskData {
    score: number;
    label: 'Bajo' | 'Moderado' | 'Alto';
    riskFactors: string[];
}

export interface ActionPlanGoal {
    goal: string;
    details: string;
}

export interface MealAnalysis {
    verdict: 'Saludable' | 'Moderado' | 'Poco Saludable' | string;
    explanation: string;
}

export interface Log {
    id: string;
    timestamp: Date;
    type: 'Comida' | 'Actividad';
}

export interface MealLog extends Log, MealAnalysis {
    type: 'Comida';
}

export interface ActivityLog extends Log {
    type: 'Actividad';
    activityType: string;
    duration: number;
}

export type HistoryLog = MealLog | ActivityLog;

export interface ChatMessage {
    sender: 'user' | 'bot';
    text: string;
}

export interface ToastMessage {
  id: number;
  message: string;
  type: 'success' | 'info' | 'error';
}
