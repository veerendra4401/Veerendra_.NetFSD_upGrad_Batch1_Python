using ELearningAPI.DTOs;

namespace ELearningAPI.Services
{
    public interface IResultService
    {
        Task<IEnumerable<ResultResponseDto>> GetResultsByUserIdAsync(int userId);
    }
}
