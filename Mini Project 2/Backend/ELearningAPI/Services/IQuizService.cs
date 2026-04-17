using ELearningAPI.DTOs;

namespace ELearningAPI.Services
{
    public interface IQuizService
    {
        Task<IEnumerable<QuizResponseDto>> GetQuizzesByCourseIdAsync(int courseId);
        Task<QuizResponseDto> CreateQuizAsync(QuizCreateDto dto);
        Task<IEnumerable<QuestionResponseDto>> GetQuestionsByQuizIdAsync(int quizId);
        Task<QuestionResponseDto> CreateQuestionAsync(QuestionCreateDto dto);
        Task<ResultResponseDto> SubmitQuizAsync(int quizId, QuizSubmitDto dto);
    }
}
