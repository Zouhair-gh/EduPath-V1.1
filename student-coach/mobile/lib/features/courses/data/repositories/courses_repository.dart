import 'package:student_coach/shared/services/api_service.dart';
import '../../data/models/course_summary.dart';
import '../../data/models/lesson.dart';
import '../../data/models/quiz_models.dart';

class CoursesRepository {
  final ApiService api;
  CoursesRepository(this.api);

  Future<List<CourseSummary>> listCourses() async {
    final res = await api.get('/courses');
    final list = (res.data as List).cast<Map<String, dynamic>>();
    return list
        .map((c) => CourseSummary(
              id: c['id'] as int,
              title: c['title'] as String? ?? '',
              description: c['description'] as String? ?? '',
              teacher: c['teacher'] as String? ?? '',
              enrolled: c['enrolled'] as bool? ?? false,
            ))
        .toList();
  }

  Future<void> enroll(int courseId) async {
    await api.post('/courses/$courseId/enroll');
  }

  Future<List<LessonModel>> listLessons(int courseId) async {
    final res = await api.get('/courses/$courseId/lessons');
    final list = (res.data as List).cast<Map<String, dynamic>>();
    return list
        .map((l) => LessonModel(
              id: l['id'] as int,
              title: l['title'] as String? ?? '',
              contentUrl: l['content_url'] as String?,
              order: l['order'] as int? ?? 0,
              locked: (l['locked'] as bool?) ?? (l['locked'] == 1),
              quizId: l['quiz_id'] as int?,
              quizPassed: (l['quiz_passed'] as bool?) ?? (l['quiz_passed'] == 1),
            ))
        .toList();
  }

  Future<List<QuizSummary>> listQuizzes(int courseId) async {
    final res = await api.get('/courses/$courseId/quizzes');
    final list = (res.data as List).cast<Map<String, dynamic>>();
    return list
        .map((q) => QuizSummary(
              id: q['id'] as int,
              title: q['title'] as String? ?? '',
              passThreshold: q['pass_threshold'] as int? ?? 50,
            ))
        .toList();
  }

  Future<QuizDetail> getQuiz(int quizId) async {
    final res = await api.get('/quizzes/$quizId');
    final m = (res.data as Map<String, dynamic>);
    final qs = (m['questions'] as List)
        .map((q) => QuizQuestionModel(
              id: q['id'] as int,
              prompt: q['prompt'] as String? ?? '',
              options: (q['options'] as List).cast<String>(),
              points: q['points'] as int? ?? 1,
            ))
        .toList();
    return QuizDetail(
      id: m['id'] as int,
      title: m['title'] as String? ?? '',
      description: m['description'] as String? ?? '',
      passThreshold: m['pass_threshold'] as int? ?? 50,
      questions: qs,
    );
  }

  Future<Map<String, dynamic>> submitQuiz(int quizId, Map<int, int> answers) async {
    final payload = {
      'answers': answers.entries
          .map((e) => {'question_id': e.key, 'selected_index': e.value})
          .toList(),
    };
    final res = await api.post('/quizzes/$quizId/attempts', data: payload);
    return (res.data as Map<String, dynamic>);
  }
}
