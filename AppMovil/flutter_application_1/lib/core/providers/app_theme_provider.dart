// lib/core/providers/app_theme_provider.dart
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_application_1/core/services/storage_service.dart';

// Este provider expone un booleano: true si es modo oscuro, false si es modo claro
final appThemeProvider = StateNotifierProvider<AppThemeNotifier, bool>((ref) {
  // Obtenemos el StorageService inicializado
  final storageService = ref.watch(storageServiceFutureProvider).value;
  return AppThemeNotifier(storageService);
});


class AppThemeNotifier extends StateNotifier<bool> {
  final StorageService? _storageService;

  AppThemeNotifier(this._storageService) : super(false) {
    _loadTheme();
  }

  // Carga el tema guardado al iniciar
  Future<void> _loadTheme() async {
    if (_storageService == null) return;
    state = await _storageService!.getTheme();
  }

  // Cambia el tema y lo guarda
  Future<void> toggleTheme() async {
    state = !state;
    await _storageService?.saveTheme(state);
  }
}