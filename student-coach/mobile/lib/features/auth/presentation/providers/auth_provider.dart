import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:student_coach/shared/services/secure_storage_service.dart';
import 'package:student_coach/shared/services/api_service.dart';
import 'package:student_coach/core/constants/api_constants.dart';
import '../../data/repositories/auth_repository.dart';
import '../../data/models/login_request.dart';

final secureStorageProvider = Provider((ref) => SecureStorageService());
final apiServiceProvider = Provider((ref) => ApiService(ref.read(secureStorageProvider)));
final authRepoProvider = Provider((ref) => AuthRepository(ref.read(apiServiceProvider)));

final authStateProvider = StateProvider<bool>((ref) => false);

final loginControllerProvider = Provider((ref) {
  final repo = ref.read(authRepoProvider);
  final storage = ref.read(secureStorageProvider);
  final state = ref.read(authStateProvider.notifier);
  return (String email, String password) async {
    final deviceType = kIsWeb ? 'web' : 'windows';
    final tokens = await repo.login(
      LoginRequest(email: email, password: password),
      deviceId: 'dev',
      deviceType: deviceType,
    );
    await storage.saveTokens(tokens['access_token'] as String, tokens['refresh_token'] as String?);
    state.state = true;
  };
});

// Health check provider used by login screen to show backend connectivity
final backendHealthProvider = FutureProvider.autoDispose<bool>((ref) async {
  final api = ref.read(apiServiceProvider);
  // Try current base URL first
  try {
    await api.get('/health');
    return true;
  } catch (_) {
    // Fallback to localhost for web environments
    try {
      api.setBaseUrl('http://localhost:8091/api/v1');
      await api.get('/health');
      return true;
    } catch (e) {
      // Revert to default for other platforms
      api.setBaseUrl(ApiConstants.baseUrl);
      return false;
    }
  }
});
