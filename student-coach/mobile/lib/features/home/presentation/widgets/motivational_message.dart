import 'package:flutter/material.dart';

class MotivationalMessage extends StatelessWidget {
  final String message;
  const MotivationalMessage({super.key, required this.message});

  @override
  Widget build(BuildContext context) {
    return Card(
      color: Colors.indigo.shade50,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Text(message),
      ),
    );
  }
}
