// lib/features/dashboard/dashboard_screen.dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import 'package:flutter_application_1/core/providers/app_state_provider.dart';
import 'package:flutter_application_1/features/dashboard/widgets/risk_gauge_widget.dart';
import 'package:flutter_application_1/features/dashboard/widgets/history_list_widget.dart';
import 'package:flutter_application_1/features/dashboard/widgets/water_tracker_widget.dart';

class DashboardScreen extends ConsumerWidget {
  const DashboardScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final appData = ref.watch(appStateProvider);
    final notifier = ref.read(appStateProvider.notifier);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Resumen CardioBien'),
        actions: [
          IconButton(
            icon: const Icon(Icons.person),
            onPressed: () => context.push('/profile'),
          ),
          IconButton(
            icon: const Icon(Icons.chat),
            onPressed: () => context.push('/chat'),
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            if (appData.riskData != null)
              RiskGaugeWidget(riskData: appData.riskData!),
            const SizedBox(height: 16),
            WaterTrackerWidget(
              waterCount: appData.waterCount,
              onAddWater: notifier.logWater,
            ),
            const SizedBox(height: 16),
            HistoryListWidget(history: appData.history),
          ],
        ),
      ),
      floatingActionButton: FloatingActionButton.extended(
        icon: const Icon(Icons.restaurant),
        label: const Text('Registrar comida'),
        onPressed: () => context.push('/meal-log'),
      ),
    );
  }
}
