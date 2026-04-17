using ELearningAPI.Models;
using ELearningAPI.DTOs;

namespace ELearningAPI.Repositories
{
    public interface IStatisticRepository
    {
        // 1. Aggregation (GROUP BY, COUNT, AVG)
        Task<IEnumerable<CourseStatDto>> GetCourseStatisticsAsync();

        // 2. Subqueries (Users scoring above platform average)
        Task<IEnumerable<User>> GetTopPerformersAsync();

        // 3. Set Operators (UNION: Recent courses + Recent quiz results)
        Task<IEnumerable<PlatformActivityDto>> GetRecentPlatformActivityAsync();
    }
}
