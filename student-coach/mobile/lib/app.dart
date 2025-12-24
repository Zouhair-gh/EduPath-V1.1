import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'core/theme/app_theme.dart';
import 'features/auth/presentation/providers/auth_provider.dart';
import 'features/auth/presentation/screens/login_screen.dart';
import 'features/home/presentation/screens/home_screen.dart';
import 'features/notifications/presentation/screens/notifications_screen.dart';
import 'features/goals/presentation/screens/goals_screen.dart';
import 'features/recommendations/presentation/screens/recommendations_screen.dart';
import 'features/profile/presentation/screens/profile_screen.dart';

class StudentCoachApp extends ConsumerWidget {
  const StudentCoachApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final loggedIn = ref.watch(authStateProvider);
    return MaterialApp(
      title: 'StudentCoach',
      theme: AppTheme.light,
      home: loggedIn ? const HomeScreen() : const LoginScreen(),
      routes: {
        '/home': (_) => const HomeScreen(),
        '/notifications': (_) => const NotificationsScreen(),
        '/goals': (_) => const GoalsScreen(),
        '/recommendations': (_) => const RecommendationsScreen(),
        '/profile': (_) => const ProfileScreen(),
      },
    );
  }
}
