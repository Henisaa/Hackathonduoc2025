// lib/core/providers/app_state_provider.dart
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_application_1/core/models/app_models.dart';
import 'package:flutter_application_1/core/services/storage_service.dart';
import 'package:flutter_application_1/core/services/gemini_service.dart';
import 'package:flutter_application_1/core/utils/risk_calculator.dart';

// 1. Definir el Estado de la App
class AppData {
  final UserProfile? userProfile;
  final RiskData? riskData;
  final List<ActionPlanGoal> actionPlan;
  final List<HistoryLog> history;
  final int waterCount;
  final int streak;
  final Map<String, bool> goalsMet;
  final bool isPlanLoading;

  AppData({
    this.userProfile,
    this.riskData,
    this.actionPlan = const [],
    this.history = const [],
    this.waterCount = 0,
    this.streak = 0,
    this.goalsMet = const {},
    this.isPlanLoading = true,
  });

  AppData copyWith({
    UserProfile? userProfile,
    RiskData? riskData,
    List<ActionPlanGoal>? actionPlan,
    List<HistoryLog>? history,
    int? waterCount,
    int? streak,
    Map<String, bool>? goalsMet,
    bool? isPlanLoading,
  }) {
    return AppData(
      userProfile: userProfile ?? this.userProfile,
      riskData: riskData ?? this.riskData,
      actionPlan: actionPlan ?? this.actionPlan,
      history: history ?? this.history,
      waterCount: waterCount ?? this.waterCount,
      streak: streak ?? this.streak,
      goalsMet: goalsMet ?? this.goalsMet,
      isPlanLoading: isPlanLoading ?? this.isPlanLoading,
    );
  }
}

// 2. Definir el Notificador (el "cerebro")
class AppStateNotifier extends StateNotifier<AppData> {
  final Ref _ref;
  late final StorageService _storage;
  late final GeminiService _gemini;

  AppStateNotifier(this._ref) : super(AppData()) {
    // Inicialización asíncrona
    _init();
  }
  
  Future<void> _init() async {
    // Espera a que el storage esté listo
    _storage = await _ref.read(storageServiceFutureProvider.future);
    _gemini = _ref.read(geminiServiceProvider);
    
    await _initializeApp();
  }

  // Lógica de App.tsx useEffect[loadProfile]
  Future<void> _initializeApp() async {
    final profile = await _storage.getProfile();
    if (profile != null) {
      final history = await _storage.getHistory();
      final water = await _storage.getWaterCount();
      final streak = await _storage.getStreak();
      final goals = await _storage.getGoals();

      state = state.copyWith(
        userProfile: profile,
        history: history,
        waterCount: water,
        streak: streak,
        goalsMet: goals,
      );
      await _calculateRiskAndPlan(); // Calcular riesgo y cargar plan
    }
    // Si el perfil es nulo, el AppWrapper redirigirá a /profile
  }

  // Lógica de App.tsx handleProfileSave
  Future<void> saveProfile(UserProfile profile) async {
    await _storage.saveProfile(profile);
    state = state.copyWith(userProfile: profile);
    await _calculateRiskAndPlan();
  }

  // Lógica de App.tsx handleProfileReset
  Future<void> resetProfile() async {
    await _storage.clearAll();
    state = AppData(); // Resetea al estado inicial
  }

  // Lógica de App.tsx useEffect[userProfile] y useEffect[riskData]
  Future<void> _calculateRiskAndPlan() async {
    if (state.userProfile == null) return;
    state = state.copyWith(isPlanLoading: true);

    // Lógica de calculateRisk
    final riskData = calculateRisk(state.userProfile!);
    state = state.copyWith(riskData: riskData);

    // Generar plan de acción
    try {
      final goals = await _gemini.generateActionPlanWithAI(riskData.riskFactors);
      state = state.copyWith(actionPlan: goals, isPlanLoading: false);
    } catch (e) {
      state = state.copyWith(
        actionPlan: [
          ActionPlanGoal(
              goal: "Mantener Hábitos Saludables",
              details: "¡Sigue así! Intenta registrar tus comidas.")
        ],
        isPlanLoading: false,
      );
    }
  }
  
  // Lógica de App.tsx updateHistory y updateStreak
  Future<void> addHistoryLog(HistoryLog log) async {
    final updatedHistory = [log, ...state.history].take(20).toList();
    await _storage.saveHistory(updatedHistory);
    
    final newStreak = await _storage.updateStreak();
    
    state = state.copyWith(history: updatedHistory, streak: newStreak);
  }
  
  Future<void> logWater() async {
    if (state.waterCount < 8) {
      final newCount = state.waterCount + 1;
      await _storage.saveWaterCount(newCount);
      state = state.copyWith(waterCount: newCount);
    }
  }
  
  Future<void> checkGoal(String goalId, bool isChecked) async {
    final newGoals = Map<String, bool>.from(state.goalsMet);
    newGoals[goalId] = isChecked;
    await _storage.saveGoals(newGoals);
    state = state.copyWith(goalsMet: newGoals);
    
    final allDone = state.actionPlan.every((goal) {
        final id = 'goal_${state.actionPlan.indexOf(goal)}';
        return newGoals[id] == true;
    });
    
    if (allDone) {
        // (La UI puede escuchar este 'allDone' y mostrar el modal)
    }
  }
}

// 3. El Provider global
final appStateProvider = StateNotifierProvider<AppStateNotifier, AppData>((ref) {
  return AppStateNotifier(ref);
});