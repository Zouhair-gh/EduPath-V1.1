class DashboardData {
  final int engagement;
  final int success;
  final String profile;
  final String message;
  final int streakDays;
  final List<int> studyWeekly;
  final int quizLast5Avg;
  final int quizPassRate30d;

  DashboardData({
    required this.engagement,
    required this.success,
    required this.profile,
    required this.message,
    required this.streakDays,
    required this.studyWeekly,
    required this.quizLast5Avg,
    required this.quizPassRate30d,
  });
}
