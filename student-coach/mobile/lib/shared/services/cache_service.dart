import 'dart:convert';
import 'package:hive_flutter/hive_flutter.dart';

class CacheService {
  static const _boxName = 'cache';
  static Future<void> init() async {
    await Hive.initFlutter();
    await Hive.openBox(_boxName);
  }

  Future<void> setJson(String key, Map<String, dynamic> value) async {
    final box = Hive.box(_boxName);
    await box.put(key, jsonEncode(value));
  }

  Map<String, dynamic>? getJson(String key) {
    final box = Hive.box(_boxName);
    final raw = box.get(key) as String?;
    if (raw == null) return null;
    return jsonDecode(raw) as Map<String, dynamic>;
  }
}
