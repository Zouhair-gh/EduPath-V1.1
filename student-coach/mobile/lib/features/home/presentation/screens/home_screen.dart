import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../auth/presentation/providers/auth_provider.dart';
import '../widgets/metric_card.dart';
import '../widgets/motivational_message.dart';
import '../widgets/trajectory_chart.dart';
import '../providers/dashboard_provider.dart';
import '../../../notifications/services/notification_service.dart';

class HomeScreen extends ConsumerWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final dash = ref.watch(dashboardProvider);
    return Scaffold(
      appBar: AppBar(title: const Text('Tableau de bord')),
      body: dash.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => Center(child: Text('Erreur: $e')),
        data: (d) => ListView(
          padding: const EdgeInsets.all(16),
          children: [
            MetricCard(title: 'Engagement', value: d.engagement.toString()),
            const SizedBox(height: 8),
            MetricCard(title: 'Réussite', value: d.success.toString()),
            const SizedBox(height: 8),
            Row(
              children: [
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: () async {
                      try {
                        final prev = ref.read(dashboardProvider).maybeWhen(data: (d) => d, orElse: () => null);
                        await ref.read(apiServiceProvider).post('/student/interactions', data: { 'type': 'check_in' });
                        final fresh = await ref.refresh(dashboardProvider.future);
                        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Daily check-in enregistré')));
                        if (prev != null) {
                          final de = fresh.engagement - prev.engagement;
                          final ds = fresh.success - prev.success;
                          final signE = de >= 0 ? '+' : '';
                          final signS = ds >= 0 ? '+' : '';
                          ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Engagement $signE$de, Réussite $signS$ds')));
                        }
                      } catch (e) {
                        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Erreur: $e')));
                      }
                    },
                    icon: const Icon(Icons.today),
                    label: const Text('Check-in du jour'),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: () async {
                      try {
                        final prev = ref.read(dashboardProvider).maybeWhen(data: (d) => d, orElse: () => null);
                        await ref.read(apiServiceProvider).post('/student/interactions', data: { 'type': 'study_session', 'value': 15 });
                        final fresh = await ref.refresh(dashboardProvider.future);
                        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Session d\'étude 15 min enregistrée')));
                        if (prev != null) {
                          final de = fresh.engagement - prev.engagement;
                          final ds = fresh.success - prev.success;
                          final signE = de >= 0 ? '+' : '';
                          final signS = ds >= 0 ? '+' : '';
                          ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Engagement $signE$de, Réussite $signS$ds')));
                        }
                      } catch (e) {
                        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Erreur: $e')));
                      }
                    },
                    icon: const Icon(Icons.timer),
                    label: const Text('Étude 15 min'),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Row(
              children: [
                Expanded(child: MotivationalMessage(message: d.message)),
                const SizedBox(width: 12),
                Chip(
                  avatar: const Icon(Icons.local_fire_department, color: Colors.deepOrange),
                  label: Text('${d.streakDays} jours', style: const TextStyle(fontWeight: FontWeight.bold)),
                  backgroundColor: Colors.orange.shade50,
                  shape: StadiumBorder(side: BorderSide(color: Colors.orange.shade200)),
                ),
              ],
            ),
            const SizedBox(height: 8),
            TrajectoryChart(values: d.studyWeekly.isEmpty ? [10,0,15,20,5,12,18] : d.studyWeekly),
          ],
        ),
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () async {
          await NotificationService.showNotification(
            id: DateTime.now().millisecondsSinceEpoch % 100000,
            title: 'Test Notification',
            body: 'Ceci est une notification locale de test.',
            priority: 'HIGH',
          );
          // Also attempt health to auto-correct base URL if offline
          try {
            await ref.read(apiServiceProvider).get('/health');
          } catch (_) {
            // Trigger health provider fallback logic
            await ref.refresh(backendHealthProvider.future);
          }
        },
        icon: const Icon(Icons.notifications_active),
        label: const Text('Tester notif'),
      ),
    );
  }
}
