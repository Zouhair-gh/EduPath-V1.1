import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../auth/presentation/providers/auth_provider.dart';
import '../../data/models/course_summary.dart';
import '../../data/models/lesson.dart';
import '../../data/models/quiz_models.dart';
import '../../data/repositories/courses_repository.dart';

final coursesRepoProvider = Provider<CoursesRepository>((ref) {
  final api = ref.read(apiServiceProvider);
  return CoursesRepository(api);
});

final coursesListProvider = FutureProvider<List<CourseSummary>>((ref) async {
  return ref.read(coursesRepoProvider).listCourses();
});

final lessonsProvider = FutureProvider.family<List<LessonModel>, int>((ref, courseId) async {
  return ref.read(coursesRepoProvider).listLessons(courseId);
});

final courseQuizzesProvider = FutureProvider.family<List<QuizSummary>, int>((ref, courseId) async {
  return ref.read(coursesRepoProvider).listQuizzes(courseId);
});

final quizDetailProvider = FutureProvider.family<QuizDetail, int>((ref, quizId) async {
  return ref.read(coursesRepoProvider).getQuiz(quizId);
});

final quizSubmitController = FutureProvider.family<Map<String, dynamic>, ({int quizId, Map<int, int> answers})>((ref, args) async {
  return ref.read(coursesRepoProvider).submitQuiz(args.quizId, args.answers);
});
