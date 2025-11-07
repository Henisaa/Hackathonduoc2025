// lib/main.dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';

import 'package:flutter_application_1/features/app_wrapper.dart';
import 'package:flutter_application_1/features/profile/profile_screen.dart';
import 'package:flutter_application_1/features/dashboard/dashboard_screen.dart';
import 'package:flutter_application_1/features/chat/chat_screen.dart';
import 'package:flutter_application_1/features/meal_log/meal_log_screen.dart';
import 'package:flutter_application_1/core/theme/app_theme.dart';
import 'package:flutter_application_1/core/providers/app_theme_provider.dart';

// 1. Define las rutas de navegación
final _router = GoRouter(
  initialLocation: '/',
  routes: [
    // El AppWrapper decide si mostrar /profile o /dashboard
    GoRoute(
      path: '/',
      builder: (context, state) => const AppWrapper(),
    ),
    GoRoute(
      path: '/profile',
      builder: (context, state) => const ProfileScreen(),
    ),
    GoRoute(
      path: '/dashboard',
      builder: (context, state) => const DashboardScreen(),
    ),
    GoRoute(
      path: '/chat',
      builder: (context, state) => const ChatScreen(),
    ),
    GoRoute(
      path: '/meal-log',
      builder: (context, state) => const MealLogScreen(),
    ),
  ],
);

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  // Carga el archivo .env para acceder a la API Key
  await dotenv.load(fileName: ".env");
  
  // Para la cámara, debemos pedir permisos (se añade en MealLogScreen)
  
  runApp(
    // 2. Envuelve la app en ProviderScope para Riverpod
    const ProviderScope(
      child: CardioBienApp(),
    ),
  );
}

class CardioBienApp extends ConsumerWidget {
  const CardioBienApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // 3. Escucha al proveedor de tema para modo dark/light
    final isDarkMode = ref.watch(appThemeProvider);

    return MaterialApp.router(
      title: 'Asistente CardioBien',
      theme: AppTheme.lightTheme,
      darkTheme: AppTheme.darkTheme,
      themeMode: isDarkMode ? ThemeMode.dark : ThemeMode.light,
      routerConfig: _router,
      debugShowCheckedModeBanner: false,
    );
  }
}