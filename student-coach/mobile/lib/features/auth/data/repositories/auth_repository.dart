import 'package:student_coach/shared/services/api_service.dart';
import '../models/login_request.dart';

class AuthRepository {
  final ApiService api;
  AuthRepository(this.api);

  Future<Map<String, dynamic>> login(LoginRequest req, {required String deviceId, required String deviceType}) async {
    final res = await api.post(
      '/auth/login',
      data: req.toJson(),
      headers: {
        'X-Device-ID': deviceId,
        'X-Device-Type': deviceType,
      },
    );
    return res.data as Map<String, dynamic>;
  }
}
