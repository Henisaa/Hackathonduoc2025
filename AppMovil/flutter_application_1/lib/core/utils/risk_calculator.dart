// lib/core/utils/risk_calculator.dart
import 'package:flutter_application_1/core/models/app_models.dart';

/// Calcula un score de riesgo simple basado en el perfil del usuario.
/// Devuelve score 0..1, etiqueta (Bajo/Moderado/Alto) y factores de riesgo.
RiskData calculateRisk(UserProfile profile) {
  double score = 0.1; // base

  if (profile.age >= 45) score += 0.15;
  if (profile.age >= 60) score += 0.15;

  final bmi = profile.bmi;
  if (bmi >= 25 && bmi < 30) score += 0.1;
  if (bmi >= 30) score += 0.2;

  if (profile.sleep < 7) score += 0.1;
  if (profile.activity < 3) score += 0.1;

  if (profile.diet == DietQuality.poor) score += 0.15;
  if (profile.smoking == SmokingStatus.smoker) score += 0.2;

  score = score.clamp(0.0, 1.0);

  String label;
  if (score < 0.33) {
    label = 'Bajo';
  } else if (score < 0.66) {
    label = 'Moderado';
  } else {
    label = 'Alto';
  }

  final factors = <String>[];
  if (profile.age >= 45) factors.add('Edad > 45 años');
  if (bmi >= 25) factors.add('Sobrepeso / obesidad');
  if (profile.sleep < 7) factors.add('Pocas horas de sueño');
  if (profile.activity < 3) factors.add('Poca actividad física');
  if (profile.diet == DietQuality.poor) factors.add('Alimentación poco saludable');
  if (profile.smoking != SmokingStatus.nonSmoker) factors.add('Tabaquismo');

  if (factors.isEmpty) {
    factors.add('Sin factores de riesgo relevantes');
  }

  return RiskData(score: score, label: label, riskFactors: factors);
}
