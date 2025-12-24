import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'app.dart';
import 'features/notifications/services/notification_service.dart';
import 'shared/services/cache_service.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await NotificationService.init();
  await NotificationService.requestPermissions();
  await CacheService.init();
  runApp(const ProviderScope(child: StudentCoachApp()));
}
