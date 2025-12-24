import 'package:dio/dio.dart';
import 'package:student_coach/core/constants/api_constants.dart';
import 'package:student_coach/shared/services/secure_storage_service.dart';

class ApiService {
  late Dio _dio;
  final SecureStorageService _storage;
  String _baseUrl = ApiConstants.baseUrl;

  ApiService(this._storage) {
    _dio = Dio(
      BaseOptions(
        baseUrl: _baseUrl,
        connectTimeout: const Duration(seconds: 30),
        receiveTimeout: const Duration(seconds: 30),
        headers: { 'Content-Type': 'application/json' },
      ),
    );

    _dio.interceptors.add(
      InterceptorsWrapper(
        onRequest: (options, handler) async {
          final token = await _storage.getAccessToken();
          if (token != null) {
            options.headers['Authorization'] = 'Bearer $token';
          }
          return handler.next(options);
        },
        onError: (error, handler) async {
          if (error.response?.statusCode == 401) {
            await _storage.clearTokens();
          }
          return handler.next(error);
        },
      ),
    );
  }

  void setBaseUrl(String baseUrl) {
    _baseUrl = baseUrl;
    _dio.options.baseUrl = baseUrl;
  }

  String getBaseUrl() => _baseUrl;

  Future<Response> get(String path, {Map<String, dynamic>? queryParameters}) => _dio.get(path, queryParameters: queryParameters);
  Future<Response> post(String path, {dynamic data, Map<String, dynamic>? headers}) =>
      _dio.post(path, data: data, options: Options(headers: headers));
  Future<Response> patch(String path, {dynamic data}) => _dio.patch(path, data: data);
  Future<Response> delete(String path) => _dio.delete(path);
}
