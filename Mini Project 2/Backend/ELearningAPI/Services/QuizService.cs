using AutoMapper;
using ELearningAPI.DTOs;
using ELearningAPI.Models;
using ELearningAPI.Repositories;

namespace ELearningAPI.Services
{
    public class QuizService : IQuizService
    {
        private readonly IQuizRepository _quizRepository;
        private readonly IRepository<Question> _questionRepository;
        private readonly IResultRepository _resultRepository;
        private readonly IMapper _mapper;

        public QuizService(
            IQuizRepository quizRepository,
            IRepository<Question> questionRepository,
            IResultRepository resultRepository,
            IMapper mapper)
        {
            _quizRepository = quizRepository;
            _questionRepository = questionRepository;
            _resultRepository = resultRepository;
            _mapper = mapper;
        }

        public async Task<IEnumerable<QuizResponseDto>> GetQuizzesByCourseIdAsync(int courseId)
        {
            var quizzes = await _quizRepository.GetQuizzesByCourseIdAsync(courseId);
            return _mapper.Map<IEnumerable<QuizResponseDto>>(quizzes);
        }

        public async Task<QuizResponseDto> CreateQuizAsync(QuizCreateDto dto)
        {
            var quiz = _mapper.Map<Quiz>(dto);
            await _quizRepository.AddAsync(quiz);
            await _quizRepository.SaveChangesAsync();

            var created = await _quizRepository.GetQuizWithQuestionsAsync(quiz.QuizId);
            return _mapper.Map<QuizResponseDto>(created!);
        }

        public async Task<IEnumerable<QuestionResponseDto>> GetQuestionsByQuizIdAsync(int quizId)
        {
            var quiz = await _quizRepository.GetQuizWithQuestionsAsync(quizId);
            if (quiz == null)
                throw new KeyNotFoundException($"Quiz with ID {quizId} not found");

            return _mapper.Map<IEnumerable<QuestionResponseDto>>(quiz.Questions);
        }

        public async Task<QuestionResponseDto> CreateQuestionAsync(QuestionCreateDto dto)
        {
            var question = _mapper.Map<Question>(dto);
            await _questionRepository.AddAsync(question);
            await _questionRepository.SaveChangesAsync();
            return _mapper.Map<QuestionResponseDto>(question);
        }

        /// <summary>
        /// Submit quiz answers and calculate score
        /// </summary>
        public async Task<ResultResponseDto> SubmitQuizAsync(int quizId, QuizSubmitDto dto)
        {
            var quiz = await _quizRepository.GetQuizWithQuestionsAsync(quizId);
            if (quiz == null)
                throw new KeyNotFoundException($"Quiz with ID {quizId} not found");

            if (quiz.Questions.Count == 0)
                throw new InvalidOperationException("Quiz has no questions");

            // Calculate score
            int score = 0;
            int totalQuestions = quiz.Questions.Count;

            foreach (var question in quiz.Questions)
            {
                if (dto.Answers.TryGetValue(question.QuestionId, out var answer))
                {
                    if (answer.Equals(question.CorrectAnswer, StringComparison.OrdinalIgnoreCase))
                    {
                        score++;
                    }
                }
            }

            // Calculate percentage and grade
            double percentage = totalQuestions > 0 ? (double)score / totalQuestions * 100 : 0;
            string grade = CalculateGrade(percentage);
            bool passed = percentage >= 60;

            // Save result
            var result = new Result
            {
                UserId = dto.UserId,
                QuizId = quizId,
                Score = score,
                AttemptDate = DateTime.UtcNow
            };

            await _resultRepository.AddAsync(result);
            await _resultRepository.SaveChangesAsync();

            // Return response
            return new ResultResponseDto
            {
                ResultId = result.ResultId,
                UserId = dto.UserId,
                QuizId = quizId,
                QuizTitle = quiz.Title,
                Score = score,
                TotalQuestions = totalQuestions,
                Percentage = Math.Round(percentage, 1),
                Grade = grade,
                Passed = passed,
                AttemptDate = result.AttemptDate
            };
        }

        /// <summary>
        /// Grade calculation matching frontend logic
        /// </summary>
        private static string CalculateGrade(double percentage)
        {
            if (percentage >= 90) return "A";
            if (percentage >= 80) return "B";
            if (percentage >= 70) return "C";
            if (percentage >= 60) return "D";
            return "F";
        }
    }
}
