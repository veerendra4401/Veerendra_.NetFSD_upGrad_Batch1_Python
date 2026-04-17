using Microsoft.EntityFrameworkCore;
using ELearningAPI.Data;
using ELearningAPI.Models;

namespace ELearningAPI.Repositories
{
    public class CourseRepository : Repository<Course>, ICourseRepository
    {
        public CourseRepository(AppDbContext context) : base(context)
        {
        }

        /// <summary>
        /// Get all courses with eager loading of Creator, Lessons, and Quizzes
        /// </summary>
        public async Task<IEnumerable<Course>> GetAllWithDetailsAsync()
        {
            return await _context.Courses
                .AsNoTracking()
                .Include(c => c.Creator)
                .Include(c => c.Lessons.OrderBy(l => l.OrderIndex))
                .Include(c => c.Quizzes)
                .OrderBy(c => c.CourseId)
                .ToListAsync();
        }

        /// <summary>
        /// Get a single course with all related data
        /// </summary>
        public async Task<Course?> GetByIdWithDetailsAsync(int id)
        {
            return await _context.Courses
                .Include(c => c.Creator)
                .Include(c => c.Lessons.OrderBy(l => l.OrderIndex))
                .Include(c => c.Quizzes)
                .FirstOrDefaultAsync(c => c.CourseId == id);
        }
    }
}
