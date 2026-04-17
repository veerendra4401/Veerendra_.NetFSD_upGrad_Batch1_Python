using Microsoft.EntityFrameworkCore;
using ELearningAPI.Data;
using ELearningAPI.Models;

namespace ELearningAPI.Repositories
{
    public class QuizRepository : Repository<Quiz>, IQuizRepository
    {
        public QuizRepository(AppDbContext context) : base(context)
        {
        }

        public async Task<IEnumerable<Quiz>> GetQuizzesByCourseIdAsync(int courseId)
        {
            return await _context.Quizzes
                .AsNoTracking()
                .Include(q => q.Questions)
                .Where(q => q.CourseId == courseId)
                .ToListAsync();
        }

        public async Task<Quiz?> GetQuizWithQuestionsAsync(int quizId)
        {
            return await _context.Quizzes
                .Include(q => q.Questions)
                .FirstOrDefaultAsync(q => q.QuizId == quizId);
        }
    }
}
