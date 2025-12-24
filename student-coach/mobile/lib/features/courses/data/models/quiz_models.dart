class QuizSummary {
  final int id;
  final String title;
  final int passThreshold;
  QuizSummary({required this.id, required this.title, required this.passThreshold});
}

class QuizQuestionModel {
  final int id;
  final String prompt;
  final List<String> options;
  final int points;
  QuizQuestionModel({
    required this.id,
    required this.prompt,
    required this.options,
    required this.points,
  });
}

class QuizDetail {
  final int id;
  final String title;
  final String description;
  final int passThreshold;
  final List<QuizQuestionModel> questions;
  QuizDetail({
    required this.id,
    required this.title,
    required this.description,
    required this.passThreshold,
    required this.questions,
  });
}
