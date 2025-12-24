import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:video_player/video_player.dart';
import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:flutter_html/flutter_html.dart';
import '../../data/models/course_summary.dart';
import '../../data/models/lesson.dart';
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
                        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Leçon verrouillée. Veuillez réussir le quiz précédent ou contacter l'enseignant.')));
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
                  Navigator.push(context, MaterialPageRoute(builder: (_) => QuizScreen(quizId: q.id, title: q.title, courseId: courseId)));
                },
              )).toList(),
            ),
          ),
        ],
      ),
    );
  }
}

class LessonDetailScreen extends ConsumerStatefulWidget {
  final LessonModel lesson;
  final int courseId;
  const LessonDetailScreen({super.key, required this.lesson, required this.courseId});

  @override
  ConsumerState<LessonDetailScreen> createState() => _LessonDetailScreenState();
}

class _LessonDetailScreenState extends ConsumerState<LessonDetailScreen> {
  VideoPlayerController? _controller;
  bool _hasError = false;

  @override
  void initState() {
    super.initState();
    if (widget.lesson.contentUrl != null && widget.lesson.contentUrl!.isNotEmpty) {
      _controller = VideoPlayerController.network(widget.lesson.contentUrl!)
        ..initialize().then((_) {
          if (mounted) setState(() {});
        }).catchError((error) {
          if (mounted) setState(() { _hasError = true; });
        });
      _controller!.addListener(() {
        if (_controller!.value.hasError && !_hasError) {
          if (mounted) setState(() { _hasError = true; });
        }
      });
    }
  }

  @override
  void dispose() {
    _controller?.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text(widget.lesson.title)),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (kIsWeb)
              Container(
                height: 220,
                child: Html(
                  data: '''
                    <video width="100%" height="220" controls>
                      <source src="${widget.lesson.contentUrl ?? ''}" type="video/mp4">
                      Your browser does not support the video tag.
                    </video>
                  ''',
                ),
              )
            else if (_hasError)
              Container(
                height: 220,
                color: Colors.black12,
                child: const Center(
                  child: Text(
                    'Failed to load video. Please try again later.',
                    style: TextStyle(color: Colors.red),
                    textAlign: TextAlign.center,
                  ),
                ),
              )
            else if (_controller != null && _controller!.value.isInitialized) ...[
              Container(
                height: 220,
                color: Colors.black,
                child: Center(
                  child: AspectRatio(
                    aspectRatio: _controller!.value.aspectRatio,
                    child: VideoPlayer(_controller!),
                  ),
                ),
              ),
              const SizedBox(height: 8),
              Center(
                child: IconButton(
                  iconSize: 48,
                  icon: Icon(
                    _controller!.value.isPlaying ? Icons.pause_circle : Icons.play_circle,
                    color: Colors.blue,
                  ),
                  onPressed: () {
                    setState(() {
                      if (_controller!.value.isPlaying) {
                        _controller!.pause();
                      } else {
                        _controller!.play();
                      }
                    });
                  },
                ),
              ),
            ]
            else
              Container(
                constraints: const BoxConstraints(maxHeight: 220),
                child: Row(children: [
                  const Icon(Icons.play_circle_fill, color: Colors.blue),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      widget.lesson.contentUrl ?? '',
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                ]),
              ),
            const SizedBox(height: 12),
            // Video analytics placeholder
            Card(
              color: Colors.grey[100],
              child: Padding(
                padding: const EdgeInsets.all(8),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: const [
                    Text('Statistiques vidéo', style: TextStyle(fontWeight: FontWeight.bold)),
                    Text('Durée regardée, nombre de lectures, etc.'),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 12),
          ],
        ),
      ),
    );
  }
}

class QuizScreen extends ConsumerStatefulWidget {
  final int quizId;
  final String title;
  final int? courseId;
  const QuizScreen({super.key, required this.quizId, required this.title, this.courseId});

  @override
  ConsumerState<QuizScreen> createState() => _QuizScreenState();
}

class _QuizScreenState extends ConsumerState<QuizScreen> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text(widget.title)),
      body: QuizContent(
        quizId: widget.quizId,
        courseId: widget.courseId,
        showTitle: false,
      ),
    );
  }
}

// NEW: Extracted quiz content without Scaffold
class QuizContent extends ConsumerStatefulWidget {
  final int quizId;
  final int? courseId;
  final bool showTitle;
  
  const QuizContent({
    super.key, 
    required this.quizId, 
    this.courseId,
    this.showTitle = false,
  });

  @override
  ConsumerState<QuizContent> createState() => _QuizContentState();
}

class _QuizContentState extends ConsumerState<QuizContent> {
  final Map<int, int> _answers = {};

  @override
  Widget build(BuildContext context) {
    final quiz = ref.watch(quizDetailProvider(widget.quizId));
    
    return quiz.when(
      loading: () => const Center(child: CircularProgressIndicator()),
      error: (e, _) => Center(child: Text('Erreur: $e')),
      data: (q) => Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          if (widget.showTitle) ...[
            Text(
              'Quiz ${q.title}',
              style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
          ],
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
                final error = result['error'] as String?;
                if (error != null) {
                  ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Erreur: ${result['message'] ?? error}')));
                } else {
                  ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Score: $percent%  ${passed ? 'Réussi' : 'Échoué'}')));
                }
                // Refresh lessons to unlock next if passed
                if (widget.courseId != null) {
                  // ignore: unused_result
                  ref.refresh(lessonsProvider(widget.courseId!));
                }
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
    );
  }
}