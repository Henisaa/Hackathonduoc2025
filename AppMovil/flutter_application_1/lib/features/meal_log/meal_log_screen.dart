// lib/features/meal_log/meal_log_screen.dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:flutter_application_1/core/models/app_models.dart';
import 'package:flutter_application_1/core/providers/app_state_provider.dart';

class MealLogScreen extends ConsumerStatefulWidget {
  const MealLogScreen({super.key});

  @override
  ConsumerState<MealLogScreen> createState() => _MealLogScreenState();
}

class _MealLogScreenState extends ConsumerState<MealLogScreen> {
  final _formKey = GlobalKey<FormState>();
  final _productController = TextEditingController();
  final _notesController = TextEditingController();
  String _verdict = 'Moderado';

  @override
  void dispose() {
    _productController.dispose();
    _notesController.dispose();
    super.dispose();
  }

  String? _required(String? value) {
    if (value == null || value.trim().isEmpty) {
      return 'Campo obligatorio';
    }
    return null;
  }

  Future<void> _save() async {
    if (!_formKey.currentState!.validate()) return;

    final analysis = MealAnalysis(
      verdict: _verdict,
      explanation:
          'Producto: ${_productController.text.trim()}. ${_notesController.text.trim()}',
    );

    final log = HistoryLog(
      timestamp: DateTime.now(),
      mealAnalysis: analysis,
    );

    await ref.read(appStateProvider.notifier).addHistoryLog(log);

    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Comida registrada en el historial')),
      );
      Navigator.of(context).pop();
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Registrar comida'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Form(
          key: _formKey,
          child: Column(
            children: [
              TextFormField(
                controller: _productController,
                decoration: const InputDecoration(
                  labelText: 'Producto / comida',
                ),
                validator: _required,
              ),
              const SizedBox(height: 12),
              DropdownButtonFormField<String>(
                value: _verdict,
                decoration: const InputDecoration(
                  labelText: 'Evaluación',
                ),
                items: const [
                  DropdownMenuItem(
                    value: 'Saludable',
                    child: Text('Saludable'),
                  ),
                  DropdownMenuItem(
                    value: 'Moderado',
                    child: Text('Moderado'),
                  ),
                  DropdownMenuItem(
                    value: 'Alto riesgo',
                    child: Text('Alto riesgo'),
                  ),
                ],
                onChanged: (value) {
                  if (value != null) {
                    setState(() => _verdict = value);
                  }
                },
              ),
              const SizedBox(height: 12),
              TextFormField(
                controller: _notesController,
                decoration: const InputDecoration(
                  labelText: 'Notas / comentarios',
                ),
                maxLines: 3,
              ),
              const SizedBox(height: 24),
              SizedBox(
                width: double.infinity,
                child: ElevatedButton.icon(
                  onPressed: _save,
                  icon: const Icon(Icons.save),
                  label: const Text('Guardar'),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
