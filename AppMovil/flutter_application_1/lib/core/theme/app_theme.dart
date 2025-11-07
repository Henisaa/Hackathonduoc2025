// lib/core/theme/app_theme.dart
import 'package:flutter/material.dart';

class AppTheme {
  // Color base para generar el esquema
  static const Color _baseSeedColor = Color(0xFF1D4ED8); // azul tipo shade 700

  // Tema claro
  static final ThemeData lightTheme = ThemeData(
    useMaterial3: true,
    brightness: Brightness.light,
    colorScheme: ColorScheme.fromSeed(
      seedColor: _baseSeedColor,
      brightness: Brightness.light,
    ),
    appBarTheme: const AppBarTheme(
      backgroundColor: Color(0xFFF9FAFB), // gris muy claro
      elevation: 0,
    ),
    scaffoldBackgroundColor: const Color(0xFFF3F4F6), // bg-gray-100
    cardTheme: const CardTheme(
      elevation: 1,
      margin: EdgeInsets.symmetric(vertical: 8.0),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.all(Radius.circular(12)),
      ),
    ),
  );

  // Tema oscuro
  static final ThemeData darkTheme = ThemeData(
    useMaterial3: true,
    brightness: Brightness.dark,
    colorScheme: ColorScheme.fromSeed(
      seedColor: _baseSeedColor,
      brightness: Brightness.dark,
    ),
    scaffoldBackgroundColor: const Color(0xFF111827), // bg-gray-900
    cardTheme: const CardTheme(
      elevation: 1,
      color: Color(0xFF1F2937), // bg-gray-800
      margin: EdgeInsets.symmetric(vertical: 8.0),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.all(Radius.circular(12)),
      ),
    ),
  );
}
