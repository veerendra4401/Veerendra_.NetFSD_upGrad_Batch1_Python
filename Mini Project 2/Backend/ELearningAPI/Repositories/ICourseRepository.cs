using ELearningAPI.Models;

namespace ELearningAPI.Repositories
{
    public interface ICourseRepository : IRepository<Course>
    {
        Task<IEnumerable<Course>> GetAllWithDetailsAsync();
        Task<Course?> GetByIdWithDetailsAsync(int id);
    }
}
