// lib/core/models/app_models.dart
import 'dart:math' as math;

/// Sexo biológico
enum Sex { male, female }

/// Calidad de dieta
enum DietQuality { poor, average, good }

/// Tabaquismo
enum SmokingStatus { nonSmoker, occasional, smoker }

/// Perfil del usuario para evaluar riesgo
class UserProfile {
  final int age;
  final Sex sex;
  final double height; // cm
  final double weight; // kg
  final double sleep; // horas por noche
  final int activity; // días por semana
  final DietQuality diet;
  final SmokingStatus smoking;

  UserProfile({
    required this.age,
    required this.sex,
    required this.height,
    required this.weight,
    required this.sleep,
    required this.activity,
    required this.diet,
    required this.smoking,
  });

  double get bmi {
    final hMeters = height / 100;
    if (hMeters <= 0) return 0;
    return weight / math.pow(hMeters, 2);
  }

  Map<String, dynamic> toJson() => {
        'age': age,
        'sex': sex.name,
        'height': height,
        'weight': weight,
        'sleep': sleep,
        'activity': activity,
        'diet': diet.name,
        'smoking': smoking.name,
      };

  factory UserProfile.fromJson(Map<String, dynamic> json) {
    Sex parseSex(String? value) =>
        value == 'female' ? Sex.female : Sex.male;

    DietQuality parseDiet(String? value) {
      switch (value) {
        case 'good':
          return DietQuality.good;
        case 'average':
          return DietQuality.average;
        default:
          return DietQuality.poor;
      }
    }

    SmokingStatus parseSmoking(String? value) {
      switch (value) {
        case 'smoker':
          return SmokingStatus.smoker;
        case 'occasional':
          return SmokingStatus.occasional;
        default:
          return SmokingStatus.nonSmoker;
      }
    }

    return UserProfile(
      age: (json['age'] as num?)?.toInt() ?? 0,
      sex: parseSex(json['sex'] as String?),
      height: (json['height'] as num?)?.toDouble() ?? 0,
      weight: (json['weight'] as num?)?.toDouble() ?? 0,
      sleep: (json['sleep'] as num?)?.toDouble() ?? 0,
      activity: (json['activity'] as num?)?.toInt() ?? 0,
      diet: parseDiet(json['diet'] as String?),
      smoking: parseSmoking(json['smoking'] as String?),
    );
  }
}

/// Datos calculados de riesgo
class RiskData {
  final double score; // 0..1
  final String label;
  final List<String> riskFactors;

  RiskData({
    required this.score,
    required this.label,
    required this.riskFactors,
  });

  Map<String, dynamic> toJson() => {
        'score': score,
        'label': label,
        'riskFactors': riskFactors,
      };

  factory RiskData.fromJson(Map<String, dynamic> json) => RiskData(
        score: (json['score'] as num?)?.toDouble() ?? 0,
        label: json['label'] as String? ?? 'Desconocido',
        riskFactors: (json['riskFactors'] as List<dynamic>?)
                ?.map((e) => e.toString())
                .toList() ??
            const [],
      );
}

/// Objetivo puntual del plan de acción
class ActionPlanGoal {
  final String goal;
  final String details;

  ActionPlanGoal({
    required this.goal,
    required this.details,
  });

  Map<String, dynamic> toJson() => {
        'goal': goal,
        'details': details,
      };

  factory ActionPlanGoal.fromJson(Map<String, dynamic> json) =>
      ActionPlanGoal(
        goal: json['goal'] as String? ?? '',
        details: json['details'] as String? ?? '',
      );
}

/// Análisis de una comida / producto
class MealAnalysis {
  final String verdict;      // Saludable / Moderado / Alto riesgo
  final String explanation;  // Explicación en lenguaje natural

  MealAnalysis({
    required this.verdict,
    required this.explanation,
  });

  Map<String, dynamic> toJson() => {
        'verdict': verdict,
        'explanation': explanation,
      };

  factory MealAnalysis.fromJson(Map<String, dynamic> json) =>
      MealAnalysis(
        verdict: json['verdict'] as String? ?? '',
        explanation: json['explanation'] as String? ?? '',
      );
}

/// Registro de historial (actividad o comida)
class HistoryLog {
  final DateTime timestamp;
  final MealAnalysis? mealAnalysis;
  final String? activityType;
  final int? duration; // minutos

  HistoryLog({
    required this.timestamp,
    this.mealAnalysis,
    this.activityType,
    this.duration,
  });

  bool get isMeal => mealAnalysis != null;

  Map<String, dynamic> toJson() => {
        'timestamp': timestamp.toIso8601String(),
        'mealAnalysis': mealAnalysis?.toJson(),
        'activityType': activityType,
        'duration': duration,
      };

  factory HistoryLog.fromJson(Map<String, dynamic> json) => HistoryLog(
        timestamp: DateTime.tryParse(json['timestamp'] as String? ?? '') ??
            DateTime.now(),
        mealAnalysis: json['mealAnalysis'] != null
            ? MealAnalysis.fromJson(
                json['mealAnalysis'] as Map<String, dynamic>,
              )
            : null,
        activityType: json['activityType'] as String?,
        duration: (json['duration'] as num?)?.toInt(),
      );
}

/// Quién envió el mensaje en el chat
enum Sender { user, bot }

/// Mensaje de chat
class ChatMessage {
  final Sender sender;
  final String text;

  ChatMessage({
    required this.sender,
    required this.text,
  });

  Map<String, dynamic> toJson() => {
        'sender': sender.name,
        'text': text,
      };

  factory ChatMessage.fromJson(Map<String, dynamic> json) {
    Sender parseSender(String? value) =>
        value == 'user' ? Sender.user : Sender.bot;
    return ChatMessage(
      sender: parseSender(json['sender'] as String?),
      text: json['text'] as String? ?? '',
    );
  }
}
