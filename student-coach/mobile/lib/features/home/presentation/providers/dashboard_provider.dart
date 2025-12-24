import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../data/models/dashboard_data.dart';
import '../../../auth/presentation/providers/auth_provider.dart';
import 'package:student_coach/shared/services/cache_service.dart';

final dashboardProvider = FutureProvider<DashboardData>((ref) async {
  final api = ref.read(apiServiceProvider);
  final cache = CacheService();
  try {
    final res = await api.get('/student/dashboard');
    final data = (res.data as Map<String, dynamic>);
    await cache.setJson('dashboard', data);
    return DashboardData(
      engagement: data['engagementScore'] as int? ?? 0,
      success: data['successRate'] as int? ?? 0,
      profile: data['profileLabel'] as String? ?? '-',
      message: data['motivationalMessage'] as String? ?? '',
      streakDays: data['streakDays'] as int? ?? 0,
      studyWeekly: (data['studyWeekly'] as List?)?.map((e) => (e as num).toInt()).toList() ?? const [],
    );
  } catch (_) {
    final data = cache.getJson('dashboard');
    if (data != null) {
      return DashboardData(
        engagement: data['engagementScore'] as int? ?? 0,
        success: data['successRate'] as int? ?? 0,
        profile: data['profileLabel'] as String? ?? '-',
        message: data['motivationalMessage'] as String? ?? '',
        streakDays: data['streakDays'] as int? ?? 0,
        studyWeekly: (data['studyWeekly'] as List?)?.map((e) => (e as num).toInt()).toList() ?? const [],
      );
    }
    rethrow;
  }
});
