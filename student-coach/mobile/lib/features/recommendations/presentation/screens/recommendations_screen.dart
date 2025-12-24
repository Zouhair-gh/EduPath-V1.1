import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:url_launcher/url_launcher.dart';
import '../../../auth/presentation/providers/auth_provider.dart';

final recommendationsProvider = FutureProvider<List<Map<String, dynamic>>>((ref) async {
  final api = ref.read(apiServiceProvider);
  final res = await api.get('/student/recommendations');
  final list = (res.data as List).cast<Map<String, dynamic>>();
  return list;
});

class RecommendationsScreen extends ConsumerWidget {
  const RecommendationsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final recos = ref.watch(recommendationsProvider);
    return Scaffold(
      appBar: AppBar(title: const Text('Recommandations')),
      body: recos.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => Center(child: Text('Erreur: $e')),
        data: (items) => ListView.separated(
          itemCount: items.length,
          separatorBuilder: (_, __) => const Divider(height: 1),
          itemBuilder: (context, i) {
            final r = items[i];
            return ListTile(
              title: Text(r['title'] ?? ''),
              subtitle: Text(r['description'] ?? ''),
              trailing: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  IconButton(
                    icon: const Icon(Icons.thumb_up_alt_outlined),
                    tooltip: 'J\'aime',
                    onPressed: () async {
                      try {
                        await ref.read(apiServiceProvider).post('/student/interactions', data: { 'type': 'like_recommendation', 'metadata': { 'recommendation_id': r['id'] } });
                        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Merci pour votre avis !')));
                      } catch (e) {
                        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Erreur: $e')));
                      }
                    },
                  ),
                  const SizedBox(width: 4),
                  const Icon(Icons.open_in_new),
                ],
              ),
              onTap: () async {
                final url = r['url'] as String?;
                if (url != null && url.isNotEmpty) {
                  try {
                    await ref.read(apiServiceProvider).post('/student/interactions', data: { 'type': 'view_content', 'metadata': { 'recommendation_id': r['id'] } });
                  } catch (_) {}
                  final uri = Uri.parse(url);
                  if (await canLaunchUrl(uri)) {
                    await launchUrl(uri, mode: LaunchMode.externalApplication);
                  }
                }
              },
            );
          },
        ),
      ),
    );
  }
}
