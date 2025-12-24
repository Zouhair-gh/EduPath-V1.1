import 'dart:io' show Platform;
import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:timezone/timezone.dart' as tz;
import 'package:timezone/data/latest.dart' as tz;

class NotificationService {
  static final FlutterLocalNotificationsPlugin _notifications = FlutterLocalNotificationsPlugin();
  static bool get _isSupportedPlatform => !kIsWeb; // Skip web

  static Future<void> init() async {
    if (!_isSupportedPlatform) return; // no-op on web
    tz.initializeTimeZones();

    const androidSettings = AndroidInitializationSettings('@mipmap/ic_launcher');
    const iosSettings = DarwinInitializationSettings(
      requestAlertPermission: true,
      requestBadgePermission: true,
      requestSoundPermission: true,
    );

    const initSettings = InitializationSettings(android: androidSettings, iOS: iosSettings);

    await _notifications.initialize(initSettings, onDidReceiveNotificationResponse: (details) {
      // Handle notification click
      // details.payload can be used to route
    });
  }

  static Future<void> requestPermissions() async {
    if (!_isSupportedPlatform) return; // no-op on web
    final android = _notifications.resolvePlatformSpecificImplementation<AndroidFlutterLocalNotificationsPlugin>();
    await android?.requestNotificationsPermission();
    final ios = _notifications.resolvePlatformSpecificImplementation<IOSFlutterLocalNotificationsPlugin>();
    await ios?.requestPermissions(alert: true, badge: true, sound: true);
  }

  static Future<void> showNotification({
    required int id,
    required String title,
    required String body,
    String? payload,
    String priority = 'NORMAL',
  }) async {
    if (!_isSupportedPlatform) return; // no-op on web
    final androidDetails = AndroidNotificationDetails(
      'student_coach_channel',
      'StudentCoach Notifications',
      channelDescription: 'Notifications pour StudentCoach',
      importance: priority == 'HIGH' ? Importance.high : Importance.defaultImportance,
      priority: priority == 'HIGH' ? Priority.high : Priority.defaultPriority,
    );
    const iosDetails = DarwinNotificationDetails();
    final details = NotificationDetails(android: androidDetails, iOS: iosDetails);
    await _notifications.show(id, title, body, details, payload: payload);
  }

  static Future<void> scheduleNotification({
    required int id,
    required String title,
    required String body,
    required DateTime when,
    String? payload,
  }) async {
    if (!_isSupportedPlatform) return; // no-op on web
    const androidDetails = AndroidNotificationDetails(
      'student_coach_channel',
      'StudentCoach Notifications',
      channelDescription: 'Notifications pour StudentCoach',
      importance: Importance.high,
      priority: Priority.high,
    );
    const iosDetails = DarwinNotificationDetails();
    final details = NotificationDetails(android: androidDetails, iOS: iosDetails);
    await _notifications.zonedSchedule(
      id,
      title,
      body,
      tz.TZDateTime.from(when, tz.local),
      details,
      androidScheduleMode: AndroidScheduleMode.exactAllowWhileIdle,
      uiLocalNotificationDateInterpretation: UILocalNotificationDateInterpretation.wallClockTime,
      payload: payload,
    );
  }
}
