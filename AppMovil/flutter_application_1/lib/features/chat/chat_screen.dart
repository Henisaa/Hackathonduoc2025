// lib/features/chat/chat_screen.dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:flutter_application_1/core/models/app_models.dart';
import 'package:flutter_application_1/core/providers/app_state_provider.dart';
import 'package:flutter_application_1/core/services/gemini_service.dart';
import 'package:flutter_application_1/shared_widgets/chat_bubble.dart';

class ChatScreen extends ConsumerStatefulWidget {
  const ChatScreen({super.key});

  @override
  ConsumerState<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends ConsumerState<ChatScreen> {
  final _controller = TextEditingController();
  final _scrollController = ScrollController();
  final List<ChatMessage> _messages = [
    ChatMessage(
      sender: Sender.bot,
      text:
          'Hola, soy tu asistente CardioBien 🫀. Cuéntame qué necesitas y te ayudo '
          'con recomendaciones sobre tu salud cardiometabólica.',
    ),
  ];
  bool _isSending = false;

  @override
  void dispose() {
    _controller.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  Future<void> _send() async {
    final text = _controller.text.trim();
    if (text.isEmpty || _isSending) return;

    _controller.clear();
    setState(() {
      _messages.add(ChatMessage(sender: Sender.user, text: text));
      _isSending = true;
    });

    final appData = ref.read(appStateProvider);
    final userProfile = appData.userProfile;
    final riskData = appData.riskData ??
        RiskData(score: 0.3, label: 'Bajo', riskFactors: const []);

    String reply;
    if (userProfile == null) {
      reply =
          'Primero completa tu perfil en la pestaña "Perfil" para poder darte '
          'recomendaciones personalizadas 😊.';
    } else {
      try {
        final gemini = ref.read(geminiServiceProvider);
        reply = await gemini.getChatResponse(
          _messages,
          text,
          userProfile,
          riskData,
          false,
        );
      } catch (e) {
        reply =
            'Hubo un problema al generar la respuesta. De todas formas, recuerda: '
            'actividad física regular, buena alimentación y buen sueño son la base '
            'para mejorar tu salud cardiometabólica.';
      }
    }

    if (!mounted) return;

    setState(() {
      _messages.add(ChatMessage(sender: Sender.bot, text: reply));
      _isSending = false;
    });

    await Future.delayed(const Duration(milliseconds: 100));
    if (_scrollController.hasClients) {
      _scrollController.animateTo(
        _scrollController.position.maxScrollExtent + 80,
        duration: const Duration(milliseconds: 200),
        curve: Curves.easeOut,
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Chat CardioBien'),
      ),
      body: Column(
        children: [
          Expanded(
            child: ListView.builder(
              controller: _scrollController,
              padding: const EdgeInsets.all(16),
              itemCount: _messages.length,
              itemBuilder: (context, index) {
                return Padding(
                  padding: const EdgeInsets.symmetric(vertical: 4),
                  child: ChatBubble(message: _messages[index]),
                );
              },
            ),
          ),
          const Divider(height: 1),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 6),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _controller,
                    decoration: const InputDecoration(
                      hintText: 'Escribe tu mensaje...',
                      border: OutlineInputBorder(),
                    ),
                    onSubmitted: (_) => _send(), 
                  ),
                ),
                const SizedBox(width: 8),
                IconButton(
                  onPressed: _isSending ? null : _send,
                  icon: _isSending
                      ? const SizedBox(
                          width: 18,
                          height: 18,
                          child: CircularProgressIndicator(strokeWidth: 2),
                        )
                      : const Icon(Icons.send),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
