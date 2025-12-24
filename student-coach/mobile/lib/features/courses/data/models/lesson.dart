class LessonModel {
  final int id;
  final String title;
  final String? contentUrl;
  final int order;
  final bool locked;
  final int? quizId;
  final bool quizPassed;
  LessonModel({
    required this.id,
    required this.title,
    required this.contentUrl,
    required this.order,
    required this.locked,
    required this.quizId,
    required this.quizPassed,
  });
}
