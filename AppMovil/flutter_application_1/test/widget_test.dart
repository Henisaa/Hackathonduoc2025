import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:flutter_application_1/main.dart';

void main() {
  testWidgets('La app arranca sin errores', (WidgetTester tester) async {
    await tester.pumpWidget(
      const ProviderScope(
        child: CardioBienApp(),
      ),
    );

    // Verifica que existe un MaterialApp.router en el árbol
    expect(find.byType(MaterialApp), findsOneWidget);
  });
}
