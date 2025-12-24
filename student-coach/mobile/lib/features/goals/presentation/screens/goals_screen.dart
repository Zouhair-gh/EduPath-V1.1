import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../auth/presentation/providers/auth_provider.dart';

final goalsProvider = FutureProvider<List<Map<String, dynamic>>>((ref) async {
  final api = ref.read(apiServiceProvider);
  final res = await api.get('/goals');
  final list = (res.data as List).cast<Map<String, dynamic>>();
  return list;
});

class GoalsScreen extends ConsumerWidget {
  const GoalsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final goals = ref.watch(goalsProvider);
    return Scaffold(
      appBar: AppBar(title: const Text('Mes Objectifs')),
      floatingActionButton: FloatingActionButton(
        onPressed: () => _openCreate(context, ref),
        child: const Icon(Icons.add),
      ),
      body: goals.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => Center(child: Text('Erreur: $e')),
        data: (items) => ListView.separated(
          itemCount: items.length,
          separatorBuilder: (_, __) => const Divider(height: 1),
          itemBuilder: (context, i) {
            final g = items[i];
            final progress = (g['current_value'] ?? 0) / (g['target_value'] ?? 1);
            final completed = (g['status'] == 'COMPLETED');
            return ListTile(
              title: Text(g['title'] ?? ''),
              subtitle: LinearProgressIndicator(value: progress.clamp(0.0, 1.0)),
              trailing: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Switch(
                    value: completed,
                    onChanged: (val) async {
                      if (!completed && val) {
                        final ok = await showDialog<bool>(
                          context: context,
                          builder: (ctx) => AlertDialog(
                            title: const Text('Confirmer'),
                            content: const Text('Marquer cet objectif comme terminé ?'),
                            actions: [
                              TextButton(onPressed: () => Navigator.pop(ctx, false), child: const Text('Annuler')),
                              ElevatedButton(onPressed: () => Navigator.pop(ctx, true), child: const Text('Oui')),
                            ],
                          ),
                        ) ?? false;
                        if (ok) {
                          try {
                            await ref.read(apiServiceProvider).patch('/goals/${g['id']}', data: { 'status': 'COMPLETED' });
                            await ref.read(apiServiceProvider).post('/student/interactions', data: { 'type': 'complete_goal', 'details': { 'goal_id': g['id'] } });
                            ref.invalidate(goalsProvider);
                            ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Objectif terminé !')));
                          } catch (e) {
                            ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Erreur: $e')));
                          }
                        }
                      } else if (completed && !val) {
                        final ok = await showDialog<bool>(
                          context: context,
                          builder: (ctx) => AlertDialog(
                            title: const Text('Confirmer'),
                            content: const Text('Réouvrir cet objectif et le marquer comme actif ?'),
                            actions: [
                              TextButton(onPressed: () => Navigator.pop(ctx, false), child: const Text('Annuler')),
                              ElevatedButton(onPressed: () => Navigator.pop(ctx, true), child: const Text('Oui')),
                            ],
                          ),
                        ) ?? false;
                        if (ok) {
                          try {
                            await ref.read(apiServiceProvider).patch('/goals/${g['id']}', data: { 'status': 'ACTIVE' });
                            ref.invalidate(goalsProvider);
                            ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Objectif réouvert.')));
                          } catch (e) {
                            ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Erreur: $e')));
                          }
                        }
                      }
                    },
                  ),
                  IconButton(
                    icon: const Icon(Icons.check_circle_outline),
                    tooltip: 'Marquer comme terminé',
                    onPressed: () async {
                      try {
                        await ref.read(apiServiceProvider).patch('/goals/${g['id']}', data: { 'status': 'COMPLETED' });
                        await ref.read(apiServiceProvider).post('/student/interactions', data: { 'type': 'complete_goal', 'details': { 'goal_id': g['id'] } });
                        ref.invalidate(goalsProvider);
                        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Objectif terminé !')));
                      } catch (e) {
                        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Erreur: $e')));
                      }
                    },
                  ),
                  IconButton(
                    icon: const Icon(Icons.delete),
                    onPressed: () async {
                      await ref.read(apiServiceProvider).delete('/goals/${g['id']}');
                      ref.invalidate(goalsProvider);
                    },
                  ),
                ],
              ),
            );
          },
        ),
      ),
    );
  }

  void _openCreate(BuildContext context, WidgetRef ref) {
    showDialog(
      context: context,
      builder: (context) => _CreateGoalDialog(ref: ref, onCreated: () => ref.invalidate(goalsProvider)),
    );
  }
}

class _CreateGoalDialog extends StatefulWidget {
  final VoidCallback onCreated;
  final WidgetRef ref;
  const _CreateGoalDialog({required this.ref, required this.onCreated});
  @override
  State<_CreateGoalDialog> createState() => _CreateGoalDialogState();
}

class _CreateGoalDialogState extends State<_CreateGoalDialog> {
  final _title = TextEditingController();
  final _target = TextEditingController();

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: const Text('Nouvel objectif'),
      content: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          TextField(controller: _title, decoration: const InputDecoration(labelText: 'Titre')),
          TextField(controller: _target, decoration: const InputDecoration(labelText: 'Cible (entier)'), keyboardType: TextInputType.number),
        ],
      ),
      actions: [
        TextButton(onPressed: () => Navigator.pop(context), child: const Text('Annuler')),
        ElevatedButton(
          onPressed: () async {
            final api = widget.ref.read(apiServiceProvider);
            final now = DateTime.now();
            await api.post('/goals', data: {
              'title': _title.text,
              'goal_type': 'custom',
              'target_value': int.tryParse(_target.text) ?? 1,
              'start_date': now.toIso8601String().substring(0,10),
              'deadline': now.add(const Duration(days: 7)).toIso8601String().substring(0,10),
            });
            widget.onCreated();
            if (mounted) Navigator.pop(context);
          },
          child: const Text('Créer'),
        ),
      ],
    );
  }
}
