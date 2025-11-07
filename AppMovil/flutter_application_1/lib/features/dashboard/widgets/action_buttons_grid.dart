// lib/features/dashboard/widgets/action_buttons_grid.dart
import 'package:flutter/material.dart';

class ActionButtonsGrid extends StatelessWidget {
  final VoidCallback onLogMeal;
  final VoidCallback onLogActivity;
  final VoidCallback onOpenChat;
  final VoidCallback onShowRecommendations;

  const ActionButtonsGrid({
    super.key,
    required this.onLogMeal,
    required this.onLogActivity,
    required this.onOpenChat,
    required this.onShowRecommendations,
  });

  @override
  Widget build(BuildContext context) {
    return GridView.count(
      crossAxisCount: 2,
      crossAxisSpacing: 16,
      mainAxisSpacing: 16,
      shrinkWrap: true, // Para que quepa dentro del ListView
      physics: const NeverScrollableScrollPhysics(), // Desactiva scroll
      children: [
        _ActionButton(
          text: "Analizar Producto",
          icon: Icons.camera_alt,
          color: Colors.green,
          onPressed: onLogMeal,
        ),
        _ActionButton(
          text: "Registrar Actividad",
          icon: Icons.directions_run,
          color: Colors.purple,
          onPressed: onLogActivity,
        ),
        _ActionButton(
          text: "Chat Asistente",
          icon: Icons.chat,
          color: Colors.blue,
          onPressed: onOpenChat,
        ),
        _ActionButton(
          text: "Recomendaciones",
          icon: Icons.lightbulb,
          color: Colors.orange,
          onPressed: onShowRecommendations,
        ),
      ],
    );
  }
}

// Widget interno para estilizar los botones
class _ActionButton extends StatelessWidget {
  final String text;
  final IconData icon;
  final Color color;
  final VoidCallback onPressed;

  const _ActionButton({
    required this.text,
    required this.icon,
    required this.color,
    required this.onPressed,
  });

  @override
  Widget build(BuildContext context) {
    return ElevatedButton(
      onPressed: onPressed,
      style: ElevatedButton.styleFrom(
        backgroundColor: color,
        foregroundColor: Colors.white,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
        ),
        padding: const EdgeInsets.all(16),
      ),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(icon, size: 36),
          const SizedBox(height: 8),
          Text(
            text,
            textAlign: TextAlign.center,
            style: const TextStyle(fontWeight: FontWeight.bold),
          ),
        ],
      ),
    );
  }
}