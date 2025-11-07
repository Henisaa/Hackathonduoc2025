// lib/core/services/gemini_service.dart
//
// Versión simplificada "offline":
// No llama a la API real de Gemini, evita errores de API_KEY,
// pero devuelve respuestas coherentes para el plan, el chat y el análisis de comida.

import 'dart:typed_data';

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_application_1/core/models/app_models.dart';

class GeminiService {
  GeminiService();

  /// "Analiza" una imagen de producto de forma local.
  /// Solo devuelve un análisis genérico para no romper la app.
  Future<MealAnalysis> analyzeProductWithAI(Uint8List imageBytes) async {
    return MealAnalysis(
      verdict: 'Moderado',
      explanation:
          'No tengo conexión a la IA en este entorno, pero de forma general '
          'prefiere productos con bajo contenido de azúcares, grasas saturadas y sodio.',
    );
  }

  /// Chat IA "fake": usa el perfil y el riesgo para dar una respuesta coherente.
  Future<String> getChatResponse(
    List<ChatMessage> history,
    String userMessage,
    UserProfile userProfile,
    RiskData riskData,
    bool isThinkingMode,
  ) async {
    final bmi = userProfile.bmi.toStringAsFixed(1);
    final riesgo = '${(riskData.score * 100).round()}% (${riskData.label})';

    final contexto = StringBuffer()
      ..writeln('Edad: ${userProfile.age} años')
      ..writeln('IMC: $bmi')
      ..writeln('Riesgo estimado: $riesgo')
      ..writeln('Factores de riesgo: ${riskData.riskFactors.join(', ')}');

    final ultimaPregunta = userMessage.toLowerCase();

    if (ultimaPregunta.contains('peso') ||
        ultimaPregunta.contains('adelgazar') ||
        ultimaPregunta.contains('bajar grasa')) {
      return 'Según tus datos ($bmi de IMC y $riesgo), lo más importante es:\n'
          '• Mantener un déficit calórico leve con una dieta equilibrada.\n'
          '• Priorizar proteína magra y vegetales.\n'
          '• Realizar fuerza 2-3 veces por semana y al menos 150 min de cardio moderado.';
    }

    if (ultimaPregunta.contains('ejercicio') ||
        ultimaPregunta.contains('entren')) {
      return 'Para mejorar tu salud cardiometabólica te recomiendo:\n'
          '• 150–300 min/sem de actividad aeróbica moderada (caminar rápido, bici, elíptica).\n'
          '• 2–3 sesiones de fuerza de cuerpo completo.\n'
          '• Evitar pasar muchas horas seguidas sentado: levántate y camina cada 60-90 min.';
    }

    if (ultimaPregunta.contains('comida') ||
        ultimaPregunta.contains('dieta') ||
        ultimaPregunta.contains('aliment')) {
      return 'En tu caso, con riesgo $riesgo, la dieta debería centrarse en:\n'
          '• Base de frutas, verduras, legumbres y granos integrales.\n'
          '• Reducir ultraprocesados, bebidas azucaradas y frituras.\n'
          '• Preferir agua, té/infusiones sin azúcar y cocinar más en casa.';
    }

    return 'Te resumo tu situación actual:\n'
        '${contexto.toString()}\n\n'
        'En general, para mejorar tu salud cardiometabólica:\n'
        '• Mantén una alimentación basada en alimentos poco procesados.\n'
        '• Muévete todos los días, aunque sea caminatas cortas.\n'
        '• Prioriza dormir 7-9 horas por noche.\n'
        '• Evita el tabaco y limita el alcohol.';
  }

  /// Genera un plan de acción basado en los factores de riesgo detectados.
  Future<List<ActionPlanGoal>> generateActionPlanWithAI(
    List<String> riskFactors,
  ) async {
    final goals = <ActionPlanGoal>[];

    if (riskFactors.any((f) => f.toLowerCase().contains('peso') ||
        f.toLowerCase().contains('obesidad') ||
        f.toLowerCase().contains('sobrepeso'))) {
      goals.add(
        ActionPlanGoal(
          goal: 'Mejorar composición corporal',
          details:
              'Apuntar a una pérdida de 0.5 kg por semana con déficit calórico leve, '
              'subiendo la actividad física y priorizando proteína magra.',
        ),
      );
    }

    if (riskFactors.any((f) => f.toLowerCase().contains('poca actividad'))) {
      goals.add(
        ActionPlanGoal(
          goal: 'Aumentar actividad física',
          details:
              'Al menos 30 minutos de caminata rápida 5 días a la semana y 2 sesiones de fuerza.',
        ),
      );
    }

    if (riskFactors.any((f) => f.toLowerCase().contains('tabaquismo'))) {
      goals.add(
        ActionPlanGoal(
          goal: 'Reducir o dejar el tabaco',
          details:
              'Definir una fecha objetivo para abandonar el tabaco y buscar apoyo profesional si es necesario.',
        ),
      );
    }

    if (riskFactors.any((f) => f.toLowerCase().contains('alimentación'))) {
      goals.add(
        ActionPlanGoal(
          goal: 'Mejorar la calidad de la dieta',
          details:
              'Planificar menús con más frutas, verduras y legumbres y reducir ultraprocesados.',
        ),
      );
    }

    if (goals.isEmpty) {
      goals.add(
        ActionPlanGoal(
          goal: 'Mantener hábitos saludables',
          details:
              'Sigue registrando tus comidas y actividad, y mantén revisiones médicas periódicas.',
        ),
      );
    }

    return goals;
  }

  /// Recomendaciones específicas según tema (sueño, compras, ejercicio, etc.).
  Future<String> getRecommendationWithAI(
    String topic,
    UserProfile userProfile,
    RiskData riskData,
  ) async {
    final bmi = userProfile.bmi.toStringAsFixed(1);

    switch (topic) {
      case 'sleep':
        return 'Para mejorar el sueño:\n'
            '• Intenta dormir 7-9 horas diarias.\n'
            '• Evita pantallas brillantes 1 hora antes de dormir.\n'
            '• Mantén horarios regulares de sueño.';
      case 'shopping':
        return 'Al hacer las compras, en tu caso (IMC $bmi, riesgo ${riskData.label}):\n'
            '• Llena el carro con frutas, verduras, legumbres y granos integrales.\n'
            '• Revisa etiquetas y evita productos con mucho sodio, azúcares y grasas trans.\n'
            '• No vayas al supermercado con mucha hambre, para decidir mejor.';
      case 'exercise':
        return 'Recomendaciones de ejercicio:\n'
            '• 150–300 min/sem de cardio moderado.\n'
            '• 2–3 días/sem de entrenamiento de fuerza.\n'
            '• Aumenta pasos diarios (por ejemplo 8.000-10.000).';
      default:
        return 'En resumen, la combinación de actividad física regular, buena alimentación, '
            'sueño suficiente y evitar el tabaco es la base para mejorar tu salud cardiometabólica.';
    }
  }
}

// Provider de Riverpod para inyectar el servicio
final geminiServiceProvider = Provider<GeminiService>((ref) {
  return GeminiService();
});
