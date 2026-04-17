using ELearningAPI.Models;

namespace ELearningAPI.Repositories
{
    public interface IResultRepository : IRepository<Result>
    {
        Task<IEnumerable<Result>> GetResultsByUserIdAsync(int userId);
        Task<IEnumerable<Result>> GetResultsWithDetailsAsync(int userId);
    }
}
