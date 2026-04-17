using ELearningAPI.Models;

namespace ELearningAPI.Repositories
{
    public interface ILessonRepository : IRepository<Lesson>
    {
        Task<IEnumerable<Lesson>> GetLessonsByCourseIdAsync(int courseId);
    }
}
