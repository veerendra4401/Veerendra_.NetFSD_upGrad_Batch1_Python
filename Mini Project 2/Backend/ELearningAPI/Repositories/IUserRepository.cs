using ELearningAPI.Models;

namespace ELearningAPI.Repositories
{
    public interface IUserRepository : IRepository<User>
    {
        Task<User?> GetByEmailAsync(string email);
    }
}
