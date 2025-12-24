import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../data/models/course_summary.dart';
import '../providers/courses_provider.dart';

class CoursesScreen extends ConsumerWidget {
  const CoursesScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final courses = ref.watch(coursesListProvider);
    return Scaffold(
      appBar: AppBar(title: const Text('Cours')),
      body: courses.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => Center(child: Text('Erreur: $e')),
        data: (list) => ListView.separated(
          padding: const EdgeInsets.all(12),
          itemBuilder: (_, i) => _CourseTile(course: list[i]),
          separatorBuilder: (_, __) => const SizedBox(height: 8),
          itemCount: list.length,
        ),
      ),
    );
  }
}

class _CourseTile extends ConsumerWidget {
  final CourseSummary course;
  const _CourseTile({required this.course});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Card(
      child: ListTile(
        title: Text(course.title, style: const TextStyle(fontWeight: FontWeight.bold)),
        subtitle: Text('${course.teacher}\n${course.description}'),
        isThreeLine: true,
        trailing: ElevatedButton(
          onPressed: course.enrolled
              ? () {
                  Navigator.push(context, MaterialPageRoute(builder: (_) => CourseDetailScreen(courseId: course.id, title: course.title)));
                }
              : () async {
                  await ref.read(coursesRepoProvider).enroll(course.id);
                  ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Inscription effectuée')));
                  ref.invalidate(coursesListProvider);
                },
          child: Text(course.enrolled ? 'Ouvrir' : 'S\'inscrire'),
        ),
      ),
    );
  }
}

class CourseDetailScreen extends ConsumerWidget {
  final int courseId;
  final String title;
  const CourseDetailScreen({super.key, required this.courseId, required this.title});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final lessons = ref.watch(lessonsProvider(courseId));
    final quizzes = ref.watch(courseQuizzesProvider(courseId));
    return Scaffold(
      appBar: AppBar(title: Text(title)),
      body: ListView(
        padding: const EdgeInsets.all(12),
        children: [
          const Text('Leçons', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
          lessons.when(
            loading: () => const Padding(padding: EdgeInsets.all(8), child: LinearProgressIndicator()),
            error: (e, _) => Text('Erreur leçons: $e'),
            data: (ls) => Column(
              children: ls.map((l) => ListTile(
                leading: Icon(l.locked ? Icons.lock : Icons.play_circle_fill,
                    color: l.locked ? Colors.grey : Colors.blue),
                title: Text(l.title),
                subtitle: Text(l.contentUrl ?? ''),
                enabled: !l.locked,
                onTap: l.locked
                    ? () {
                        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Leçon verrouillée. Veuillez réussir le quiz précédent.')));
                      }
                    : () {
                        Navigator.push(context, MaterialPageRoute(builder: (_) => LessonDetailScreen(lesson: l, courseId: courseId)));
                      },
              )).toList(),
            ),
          ),
          const SizedBox(height: 16),
          const Text('Quiz', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
          quizzes.when(
            loading: () => const Padding(padding: EdgeInsets.all(8), child: LinearProgressIndicator()),
            error: (e, _) => Text('Erreur quiz: $e'),
            data: (qs) => Column(
              children: qs.map((q) => ListTile(
                leading: const Icon(Icons.quiz),
                title: Text(q.title),
                subtitle: Text('Seuil: ${q.passThreshold}%'),
                onTap: () {
                  Navigator.push(context, MaterialPageRoute(builder: (_) => QuizScreen(quizId: q.id, title: q.title)));
                },
              )).toList(),
            ),
          ),
        ],
      ),
    );
  }
}

class LessonDetailScreen extends ConsumerWidget {
  final LessonModel lesson;
  final int courseId;
  const LessonDetailScreen({super.key, required this.lesson, required this.courseId});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      appBar: AppBar(title: Text(lesson.title)),
      body: ListView(
        padding: const EdgeInsets.all(12),
        children: [
          Row(children: [
            const Icon(Icons.play_circle_fill, color: Colors.blue),
            const SizedBox(width: 8),
            Expanded(child: Text(lesson.contentUrl ?? '')),
          ]),
          const SizedBox(height: 12),
          ElevatedButton.icon(
            onPressed: lesson.quizId == null
                ? null
                : () {
                    Navigator.push(context, MaterialPageRoute(builder: (_) => QuizScreen(quizId: lesson.quizId!, title: 'Quiz ${lesson.title}')));
                  },
            icon: const Icon(Icons.quiz),
            label: Text(lesson.quizPassed ? 'Quiz réussi' : 'Passer le quiz'),
          ),
        ],
      ),
    );
  }
}

class QuizScreen extends ConsumerStatefulWidget {
  final int quizId;
  final String title;
  const QuizScreen({super.key, required this.quizId, required this.title});

  @override
  ConsumerState<QuizScreen> createState() => _QuizScreenState();
}

class _QuizScreenState extends ConsumerState<QuizScreen> {
  final Map<int, int> _answers = {};

  @override
  Widget build(BuildContext context) {
    final quiz = ref.watch(quizDetailProvider(widget.quizId));
    return Scaffold(
      appBar: AppBar(title: Text(widget.title)),
      body: quiz.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => Center(child: Text('Erreur: $e')),
        data: (q) => ListView(
          padding: const EdgeInsets.all(12),
          children: [
            Text(q.description),
            const SizedBox(height: 12),
            ...q.questions.map((question) => Card(
              child: Padding(
                padding: const EdgeInsets.all(8),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(question.prompt, style: const TextStyle(fontWeight: FontWeight.bold)),
                    const SizedBox(height: 8),
                    ...List.generate(question.options.length, (idx) => RadioListTile<int>(
                          value: idx,
                          groupValue: _answers[question.id],
                          title: Text(question.options[idx]),
                          onChanged: (v) {
                            setState(() {
                              _answers[question.id] = v!;
                            });
                          },
                        )),
                  ],
                ),
              ),
            )),
            const SizedBox(height: 12),
            ElevatedButton.icon(
              onPressed: () async {
                try {
                  final result = await ref.read(quizSubmitController((quizId: widget.quizId, answers: _answers)).future);
                  final percent = result['percent'] as int? ?? 0;
                  final passed = result['passed'] as bool? ?? false;
                  ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Score: $percent%  ${passed ? 'Réussi' : 'Échoué'}')));
                  // Refresh lessons to unlock next if passed
                  // ignore: unused_result
                  ref.refresh(lessonsProvider(courseId));
                  // Refresh quiz detail view (optional)
                  // ignore: unused_result
                  ref.refresh(quizDetailProvider(widget.quizId));
                } catch (e) {
                  ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Erreur soumission: $e')));
                }
              },
              icon: const Icon(Icons.send),
              label: const Text('Soumettre'),
            ),
          ],
        ),
      ),
    );
  }
}
