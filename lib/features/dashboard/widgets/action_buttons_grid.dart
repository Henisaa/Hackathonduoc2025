// lib/features/dashboard/widgets/action_plan_widget.dart
import 'package:flutter/material.dart';
import 'package:flutter_application_1/core/models/app_models.dart';

class ActionPlanWidget extends StatelessWidget {
  final bool isLoading;
  final List<ActionPlanGoal> goals;
  final Map<String, bool> goalsMet;
  final Function(String, bool) onCheck;

  const ActionPlanWidget({
    super.key,
    required this.isLoading,
    required this.goals,
    required this.goalsMet,
    required this.onCheck,
  });

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
              "Tu Plan de Acción (2 Semanas)",
              style: theme.textTheme.titleLarge,
            ),
            const SizedBox(height: 16),
            if (isLoading)
              const Center(
                child: Padding(
                  padding: EdgeInsets.all(16.0),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      CircularProgressIndicator(),
                      SizedBox(width: 16),
                      Text("Generando tu plan..."),
                    ],
                  ),
                ),
              )
            else if (goals.isEmpty)
              const Text("No se pudo generar un plan. Intenta más tarde.")
            else
              // Genera la lista de Checkbox
              Column(
                children: List.generate(goals.length, (index) {
                  final item = goals[index];
                  final goalId = 'goal_$index';
                  final isChecked = goalsMet[goalId] ?? false;

                  return CheckboxListTile(
                    title: Text(
                      item.goal,
                      style: TextStyle(
                        fontWeight: FontWeight.bold,
                        decoration: isChecked ? TextDecoration.lineThrough : null,
                      ),
                    ),
                    subtitle: Text(
                      item.details,
                      style: TextStyle(
                        decoration: isChecked ? TextDecoration.lineThrough : null,
                      ),
                    ),
                    value: isChecked,
                    onChanged: (bool? value) {
                      onCheck(goalId, value ?? false);
                    },
                    controlAffinity: ListTileControlAffinity.leading,
                    activeColor: theme.primaryColor,
                  );
                }),
              ),
          ],
        ),
      ),
    );
  }
}