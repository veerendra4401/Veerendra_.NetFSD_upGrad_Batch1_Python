using ELearningAPI.Models;

namespace ELearningAPI.Repositories
{
    public interface IQuizRepository : IRepository<Quiz>
    {
        Task<IEnumerable<Quiz>> GetQuizzesByCourseIdAsync(int courseId);
        Task<Quiz?> GetQuizWithQuestionsAsync(int quizId);
    }
}
