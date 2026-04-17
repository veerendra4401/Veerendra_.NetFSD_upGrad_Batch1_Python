using Microsoft.EntityFrameworkCore;
using ELearningAPI.Data;
using ELearningAPI.Models;

namespace ELearningAPI.Repositories
{
    public class LessonRepository : Repository<Lesson>, ILessonRepository
    {
        public LessonRepository(AppDbContext context) : base(context)
        {
        }

        public async Task<IEnumerable<Lesson>> GetLessonsByCourseIdAsync(int courseId)
        {
            return await _context.Lessons
                .AsNoTracking()
                .Where(l => l.CourseId == courseId)
                .OrderBy(l => l.OrderIndex)
                .ToListAsync();
        }
    }
}
