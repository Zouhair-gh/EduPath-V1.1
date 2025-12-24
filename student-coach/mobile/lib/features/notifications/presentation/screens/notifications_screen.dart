import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../auth/presentation/providers/auth_provider.dart';

final notificationsProvider = FutureProvider<List<Map<String, dynamic>>>((ref) async {
  final api = ref.read(apiServiceProvider);
  final res = await api.get('/notifications');
  final list = (res.data as List).cast<Map<String, dynamic>>();
  return list;
});

class NotificationsScreen extends ConsumerWidget {
  const NotificationsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final notifs = ref.watch(notificationsProvider);
    return Scaffold(
      appBar: AppBar(title: const Text('Notifications')),
      body: notifs.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => Center(child: Text('Erreur: $e')),
        data: (items) => ListView.separated(
          itemCount: items.length,
          separatorBuilder: (_, __) => const Divider(height: 1),
          itemBuilder: (context, i) {
            final n = items[i];
            return ListTile(
              leading: Icon(n['is_read'] == true ? Icons.mark_email_read : Icons.markunread, color: n['is_read'] == true ? Colors.grey : Colors.blue),
              title: Text(n['title'] ?? ''),
              subtitle: Text(n['message'] ?? ''),
              trailing: IconButton(
                icon: const Icon(Icons.done_all),
                onPressed: () async {
                  await ref.read(apiServiceProvider).patch('/notifications/${n['id']}/read');
                  ref.invalidate(notificationsProvider);
                },
              ),
            );
          },
        ),
      ),
    );
  }
}
