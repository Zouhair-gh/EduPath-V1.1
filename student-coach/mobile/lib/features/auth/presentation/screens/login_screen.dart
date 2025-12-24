import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers/auth_provider.dart';

class LoginScreen extends ConsumerStatefulWidget {
  const LoginScreen({super.key});

  @override
  ConsumerState<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends ConsumerState<LoginScreen> {
  final _email = TextEditingController();
  final _password = TextEditingController();

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Connexion')),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            Consumer(builder: (context, ref, _) {
              final health = ref.watch(backendHealthProvider);
              return ListTile(
                leading: Icon(
                  health.value == true ? Icons.check_circle : Icons.cancel,
                  color: health.value == true ? Colors.green : Colors.red,
                ),
                title: const Text('Backend connectivity'),
                subtitle: Text(health.when(
                  data: (ok) => ok ? 'Online' : 'Offline',
                  loading: () => 'Checking...',
                  error: (e, st) => 'Error',
                )),
                trailing: IconButton(
                  icon: const Icon(Icons.refresh),
                  onPressed: () => ref.refresh(backendHealthProvider),
                ),
              );
            }),
            TextField(controller: _email, decoration: const InputDecoration(labelText: 'Email')),
            TextField(controller: _password, decoration: const InputDecoration(labelText: 'Mot de passe'), obscureText: true),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: () async {
                try {
                  await ref.read(loginControllerProvider)(_email.text, _password.text);
                  if (!mounted) return;
                  Navigator.pushReplacementNamed(context, '/home');
                } catch (e) {
                  ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Erreur: $e')));
                }
              },
              child: const Text('Se connecter'),
            ),
          ],
        ),
      ),
    );
  }
}
