// lib/features/profile/profile_screen.dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import 'package:flutter_application_1/core/models/app_models.dart';
import 'package:flutter_application_1/core/providers/app_state_provider.dart';

class ProfileScreen extends ConsumerStatefulWidget {
  const ProfileScreen({super.key});

  @override
  ConsumerState<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends ConsumerState<ProfileScreen> {
  final _formKey = GlobalKey<FormState>();
  final _ageController = TextEditingController(text: '35');
  final _heightController = TextEditingController(text: '170');
  final _weightController = TextEditingController(text: '70');
  final _sleepController = TextEditingController(text: '7');
  final _activityController = TextEditingController(text: '3');

  Sex _sex = Sex.male;
  DietQuality _diet = DietQuality.average;
  SmokingStatus _smoking = SmokingStatus.nonSmoker;

  @override
  void dispose() {
    _ageController.dispose();
    _heightController.dispose();
    _weightController.dispose();
    _sleepController.dispose();
    _activityController.dispose();
    super.dispose();
  }

  String? _requiredNumber(String? value) {
    if (value == null || value.trim().isEmpty) {
      return 'Campo obligatorio';
    }
    final num? parsed = num.tryParse(value);
    if (parsed == null) return 'Debe ser numérico';
    if (parsed <= 0) return 'Debe ser mayor a 0';
    return null;
  }

  Future<void> _save() async {
    if (!_formKey.currentState!.validate()) return;

    final profile = UserProfile(
      age: int.parse(_ageController.text),
      sex: _sex,
      height: double.parse(_heightController.text),
      weight: double.parse(_weightController.text),
      sleep: double.parse(_sleepController.text),
      activity: int.parse(_activityController.text),
      diet: _diet,
      smoking: _smoking,
    );

    await ref.read(appStateProvider.notifier).saveProfile(profile);
    if (mounted) {
      context.go('/dashboard');
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Tu perfil de salud'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Completa tu perfil para estimar tu riesgo cardiometabólico.',
                style: theme.textTheme.bodyMedium,
              ),
              const SizedBox(height: 16),
              Row(
                children: [
                  Expanded(
                    child: TextFormField(
                      controller: _ageController,
                      decoration: const InputDecoration(
                        labelText: 'Edad',
                        suffixText: 'años',
                      ),
                      keyboardType: TextInputType.number,
                      validator: _requiredNumber,
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: DropdownButtonFormField<Sex>(
                      value: _sex,
                      decoration: const InputDecoration(
                        labelText: 'Sexo',
                      ),
                      items: const [
                        DropdownMenuItem(
                          value: Sex.male,
                          child: Text('Masculino'),
                        ),
                        DropdownMenuItem(
                          value: Sex.female,
                          child: Text('Femenino'),
                        ),
                      ],
                      onChanged: (value) {
                        if (value != null) {
                          setState(() => _sex = value);
                        }
                      },
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              Row(
                children: [
                  Expanded(
                    child: TextFormField(
                      controller: _heightController,
                      decoration: const InputDecoration(
                        labelText: 'Estatura',
                        suffixText: 'cm',
                      ),
                      keyboardType: TextInputType.number,
                      validator: _requiredNumber,
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: TextFormField(
                      controller: _weightController,
                      decoration: const InputDecoration(
                        labelText: 'Peso',
                        suffixText: 'kg',
                      ),
                      keyboardType: TextInputType.number,
                      validator: _requiredNumber,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              Row(
                children: [
                  Expanded(
                    child: TextFormField(
                      controller: _sleepController,
                      decoration: const InputDecoration(
                        labelText: 'Sueño',
                        helperText: 'Horas por noche',
                      ),
                      keyboardType: TextInputType.number,
                      validator: _requiredNumber,
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: TextFormField(
                      controller: _activityController,
                      decoration: const InputDecoration(
                        labelText: 'Actividad física',
                        helperText: 'Días / semana',
                      ),
                      keyboardType: TextInputType.number,
                      validator: _requiredNumber,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              DropdownButtonFormField<DietQuality>(
                value: _diet,
                decoration: const InputDecoration(
                  labelText: 'Calidad de dieta',
                ),
                items: const [
                  DropdownMenuItem(
                    value: DietQuality.poor,
                    child: Text('Poco saludable'),
                  ),
                  DropdownMenuItem(
                    value: DietQuality.average,
                    child: Text('Intermedia'),
                  ),
                  DropdownMenuItem(
                    value: DietQuality.good,
                    child: Text('Saludable'),
                  ),
                ],
                onChanged: (value) {
                  if (value != null) {
                    setState(() => _diet = value);
                  }
                },
              ),
              const SizedBox(height: 12),
              DropdownButtonFormField<SmokingStatus>(
                value: _smoking,
                decoration: const InputDecoration(
                  labelText: 'Tabaquismo',
                ),
                items: const [
                  DropdownMenuItem(
                    value: SmokingStatus.nonSmoker,
                    child: Text('No fumo'),
                  ),
                  DropdownMenuItem(
                    value: SmokingStatus.occasional,
                    child: Text('Ocasional'),
                  ),
                  DropdownMenuItem(
                    value: SmokingStatus.smoker,
                    child: Text('Fumo diariamente'),
                  ),
                ],
                onChanged: (value) {
                  if (value != null) {
                    setState(() => _smoking = value);
                  }
                },
              ),
              const SizedBox(height: 24),
              SizedBox(
                width: double.infinity,
                child: ElevatedButton.icon(
                  onPressed: _save,
                  icon: const Icon(Icons.check),
                  label: const Text('Guardar perfil'),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
