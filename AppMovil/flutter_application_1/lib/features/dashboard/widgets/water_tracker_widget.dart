// lib/features/dashboard/widgets/water_tracker_widget.dart
import 'package:flutter/material.dart';

class WaterTrackerWidget extends StatelessWidget {
  final int waterCount;
  final VoidCallback onAddWater;

  const WaterTrackerWidget({
    super.key,
    required this.waterCount,
    required this.onAddWater,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    const int maxGlasses = 8;

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          children: [
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Agua diaria',
                    style: theme.textTheme.titleLarge,
                  ),
                  const SizedBox(height: 8),
                  Text(
                    '$waterCount de $maxGlasses vasos',
                    style: theme.textTheme.bodyMedium,
                  ),
                ],
              ),
            ),
            IconButton(
              onPressed: waterCount >= maxGlasses ? null : onAddWater,
              icon: const Icon(Icons.local_drink),
              tooltip: 'Agregar vaso de agua',
            ),
          ],
        ),
      ),
    );
  }
}
