// lib/core/theme/app_theme.dart
import 'package:flutter/material.dart';

class AppTheme {
  // Define un color base (azul, como en tu app)
  static final _baseSeedColor = Colors.blue.shade700;

  static final ThemeData lightTheme = ThemeData(
    useMaterial3: true,
    brightness: Brightness.light,
    colorScheme: ColorScheme.fromSeed(
      seedColor: _baseSeedColor,
      brightness: Brightness.light,
    ),
    appBarTheme: AppBarTheme(
      backgroundColor: Colors.grey.shade50,
      elevation: 0,
    ),
    scaffoldBackgroundColor: Colors.grey.shade100, // bg-gray-100
    cardTheme: CardTheme(
      elevation: 1,
      margin: const EdgeInsets.symmetric(vertical: 8),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
      ),
    ),
  );

  static final ThemeData darkTheme = ThemeData(
    useMaterial3: true,
    brightness: Brightness.dark,
    colorScheme: ColorScheme.fromSeed(
      seedColor: _baseSeedColor,
      brightness: Brightness.dark,
    ),
    scaffoldBackgroundColor: const Color(0xFF111827), // bg-gray-900
    cardTheme: CardTheme(
      elevation: 1,
      color: const Color(0xFF1f2937), // bg-gray-800
      margin: const EdgeInsets.symmetric(vertical: 8),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
      ),
    ),
  );
}