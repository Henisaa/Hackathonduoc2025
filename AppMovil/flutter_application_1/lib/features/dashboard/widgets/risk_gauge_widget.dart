// lib/features/dashboard/widgets/risk_gauge_widget.dart
import 'dart:math' as math;
import 'package:flutter/material.dart';
import 'package:flutter_application_1/core/models/app_models.dart';

class RiskGaugeWidget extends StatelessWidget {
  final RiskData riskData;
  const RiskGaugeWidget({super.key, required this.riskData});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            Text("Riesgo Cardiometabólico", style: theme.textTheme.titleLarge),
            const SizedBox(height: 16),
            // Avatar de corazón (no incluido, pero iría aquí)
            
            // Gauge
            SizedBox(
              width: 200,
              height: 100,
              child: CustomPaint(
                painter: _GaugePainter(
                  score: riskData.score,
                  backgroundColor: theme.colorScheme.surfaceVariant,
                ),
                child: Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.end,
                    children: [
                      Text(
                        "${(riskData.score * 100).round()}%",
                        style: theme.textTheme.headlineMedium?.copyWith(fontWeight: FontWeight.bold),
                      ),
                      Text(
                        riskData.label,
                        style: theme.textTheme.bodyMedium?.copyWith(color: theme.colorScheme.onSurfaceVariant),
                      ),
                      const SizedBox(height: 10), // Ajuste para el arco
                    ],
                  ),
                ),
              ),
            )
          ],
        ),
      ),
    );
  }
}

class _GaugePainter extends CustomPainter {
  final double score;
  final Color backgroundColor;

  _GaugePainter({required this.score, required this.backgroundColor});
  
  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height);
    final rect = Rect.fromCenter(center: center, width: size.width, height: size.height * 2);

    final backgroundPaint = Paint()
      ..color = backgroundColor
      ..style = PaintingStyle.stroke
      ..strokeWidth = 20;

    // Arco de fondo
    canvas.drawArc(rect, math.pi, math.pi, false, backgroundPaint);
    
    // Arco de score
    final scorePaint = Paint()
      ..shader = const SweepGradient(
        startAngle: math.pi,
        endAngle: 2 * math.pi,
        colors: [Colors.green, Colors.yellow, Colors.red],
        stops: [0.0, 0.5, 1.0],
      ).createShader(rect)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 20
      ..strokeCap = StrokeCap.round;

    canvas.drawArc(rect, math.pi, math.pi * score.clamp(0.0, 1.0), false, scorePaint);
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => true;
}