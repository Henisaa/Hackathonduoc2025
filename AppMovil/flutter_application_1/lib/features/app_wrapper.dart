// lib/features/app_wrapper.dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:flutter_application_1/core/providers/app_state_provider.dart';

class AppWrapper extends ConsumerWidget {
  const AppWrapper({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Escucha el estado del perfil de usuario
    final profile = ref.watch(appStateProvider.select((data) => data.userProfile));
    
    // El AppStateNotifier se inicializa solo y carga el perfil.
    // Cuando el estado cambie, este widget re-evaluará.

    // Aún no sabemos si el perfil está cargado o no
    if (profile == null) {
        // Podríamos estar cargando desde SharedPreferences
        // O podría ser un usuario nuevo.
        
        // Vamos a darle un frame para que cargue
        return FutureBuilder(
            future: Future.delayed(const Duration(milliseconds: 500)), // Simula tiempo de carga
            builder: (context, snapshot) {
                // Volvemos a chequear el provider
                final latestProfile = ref.read(appStateProvider).userProfile;
                if (latestProfile == null) {
                    // Si sigue nulo, es usuario nuevo.
                    WidgetsBinding.instance.addPostFrameCallback((_) {
                        context.go('/profile');
                    });
                } else {
                    // Se cargó el perfil.
                     WidgetsBinding.instance.addPostFrameCallback((_) {
                        context.go('/dashboard');
                    });
                }
                return const Scaffold(
                    body: Center(child: CircularProgressIndicator())
                );
            },
        );
    }

    // Ya tenemos perfil, vamos al dashboard
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.go('/dashboard');
    });
    
    // Muestra un loader mientras ocurre la redirección
    return const Scaffold(
      body: Center(child: CircularProgressIndicator()),
    );
  }
}