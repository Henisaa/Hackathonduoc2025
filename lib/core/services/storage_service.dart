// lib/core/services/storage_service.dart
import 'dart:convert';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:flutter_application_1/core/models/app_models.dart';
import 'package:flutter_application_1/core/constants/app_constants.dart';

class StorageService {
  final SharedPreferences _prefs;

  StorageService(this._prefs);

  static Future<StorageService> init() async {
    final prefs = await SharedPreferences.getInstance();
    return StorageService(prefs);
  }
  
  // --- Profile ---
  Future<void> saveProfile(UserProfile profile) async {
    await _prefs.setString(storageProfileKey, jsonEncode(profile.toJson()));
  }

  Future<UserProfile?> getProfile() async {
    final jsonString = _prefs.getString(storageProfileKey);
    if (jsonString != null) {
      return UserProfile.fromJson(jsonDecode(jsonString));
    }
    return null;
  }

  // --- History ---
  Future<void> saveHistory(List<HistoryLog> history) async {
    final List<String> jsonList = history.map((log) => jsonEncode(log.toJson())).toList();
    await _prefs.setStringList(storageHistoryKey, jsonList);
  }
  
  Future<List<HistoryLog>> getHistory() async {
    final jsonList = _prefs.getStringList(storageHistoryKey);
    if (jsonList != null) {
      return jsonList.map((jsonString) => HistoryLog.fromJson(jsonDecode(jsonString))).toList();
    }
    return [];
  }

  // --- Water ---
  Future<void> saveWaterCount(int count) async {
    final today = DateTime.now().toIso8601String().substring(0, 10);
    final data = jsonEncode({'count': count, 'date': today});
    await _prefs.setString(storageWaterKey, data);
  }
  
  Future<int> getWaterCount() async {
    final jsonString = _prefs.getString(storageWaterKey);
    final today = DateTime.now().toIso8601String().substring(0, 10);
    if (jsonString != null) {
      final data = jsonDecode(jsonString);
      if (data['date'] == today) {
        return data['count'] as int;
      }
    }
    return 0; // Resetea si es un nuevo día
  }
  
  // --- Streak (Lógica de App.tsx updateStreak) ---
  Future<int> updateStreak() async {
    final jsonString = _prefs.getString(storageStreakKey) ?? '{}';
    final data = jsonDecode(jsonString);
    int currentStreak = data['currentStreak'] ?? 0;
    String? lastLogDate = data['lastLogDate'];

    final now = DateTime.now();
    final today = DateTime(now.year, now.month, now.day).toIso8601String();
    final yesterday = DateTime(now.year, now.month, now.day - 1).toIso8601String();

    if (lastLogDate != today) {
      if (lastLogDate == yesterday) {
        currentStreak += 1;
      } else {
        currentStreak = 1; // Se rompió la racha (o es la primera vez)
      }
      final newData = jsonEncode({'currentStreak': currentStreak, 'lastLogDate': today});
      await _prefs.setString(storageStreakKey, newData);
    }
    return currentStreak;
  }
  
  Future<int> getStreak() async {
     final jsonString = _prefs.getString(storageStreakKey) ?? '{}';
     final data = jsonDecode(jsonString);
     return data['currentStreak'] ?? 0;
  }

  // --- Goals ---
  Future<void> saveGoals(Map<String, bool> goals) async {
    await _prefs.setString(storageGoalsKey, jsonEncode(goals));
  }
  
  Future<Map<String, bool>> getGoals() async {
    final jsonString = _prefs.getString(storageGoalsKey);
    if (jsonString != null) {
      final decodedMap = jsonDecode(jsonString) as Map<String, dynamic>;
      return decodedMap.map((key, value) => MapEntry(key, value as bool));
    }
    return {};
  }
  
  // --- Theme ---
  Future<void> saveTheme(bool isDark) async {
    await _prefs.setString(storageThemeKey, isDark ? 'dark' : 'light');
  }
  
  Future<bool> getTheme() async {
    return _prefs.getString(storageThemeKey) == 'dark';
  }

  // --- Reset ---
  Future<void> clearAll() async {
    await _prefs.clear();
  }
}

// Provider de Riverpod
final storageServiceProvider = Provider<StorageService>((ref) {
  throw UnimplementedError("StorageService no inicializado");
});

// Un provider especial para inicializarlo asíncronamente
final storageServiceFutureProvider = FutureProvider<StorageService>((ref) async {
  return await StorageService.init();
});