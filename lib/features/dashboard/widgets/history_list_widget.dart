// lib/features/dashboard/widgets/history_list_widget.dart
import 'package.flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:flutter_application_1/core/models/app_models.dart';

class HistoryListWidget extends StatelessWidget {
  final List<HistoryLog> history;
  const HistoryListWidget({super.key, required this.history});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              "Historial de Registros",
              style: theme.textTheme.titleLarge,
            ),
            const SizedBox(height: 16),
            if (history.isEmpty)
              const Center(
                child: Padding(
                  padding: EdgeInsets.all(8.0),
                  child: Text("Aún no has registrado nada."),
                ),
              )
            else
              // Limita la altura como en el CSS (max-h-60)
              ConstrainedBox(
                constraints: const BoxConstraints(
                  maxHeight: 240, // Similar a max-h-60
                ),
                child: ListView.separated(
                  itemCount: history.length,
                  shrinkWrap: true,
                  separatorBuilder: (context, index) => Divider(
                    color: theme.colorScheme.surfaceVariant,
                  ),
                  itemBuilder: (context, index) {
                    final log = history[index];
                    if (log.isMeal) {
                      return _MealHistoryItem(log: log);
                    } else {
                      return _ActivityHistoryItem(log: log);
                    }
                  },
                ),
              ),
          ],
        ),
      ),
    );
  }
}

// Widget interno para logs de comida
class _MealHistoryItem extends StatelessWidget {
  final HistoryLog log;
  const _MealHistoryItem({required this.log});

  @override
  Widget build(BuildContext context) {
    final analysis = log.mealAnalysis!;
    IconData iconData;
    Color iconColor;

    switch (analysis.verdict) {
      case 'Saludable':
        iconData = Icons.check_circle;
        iconColor = Colors.green;
        break;
      case 'Moderado':
        iconData = Icons.warning;
        iconColor = Colors.orange;
        break;
      default: // 'Poco Saludable'
        iconData = Icons.error;
        iconColor = Colors.red;
    }
    
    final timeFormat = DateFormat('HH:mm'); // 'es-ES', {hour:'2-digit', minute:'2-digit'}

    return ListTile(
      leading: Icon(iconData, color: iconColor),
      title: Text("${analysis.verdict} (Producto)"),
      subtitle: Text(analysis.explanation),
      trailing: Text(timeFormat.format(log.timestamp)),
      dense: true,
    );
  }
}

// Widget interno para logs de actividad
class _ActivityHistoryItem extends StatelessWidget {
  final HistoryLog log;
  const _ActivityHistoryItem({required this.log});

  @override
  Widget build(BuildContext context) {
    final timeFormat = DateFormat('HH:mm');
    
    return ListTile(
      leading: Icon(Icons.directions_run, color: Colors.purple.shade300),
      title: Text(log.activityType ?? "Actividad"),
      subtitle: Text("Duración: ${log.duration} minutos."),
      trailing: Text(timeFormat.format(log.timestamp)),
      dense: true,
    );
  }
}