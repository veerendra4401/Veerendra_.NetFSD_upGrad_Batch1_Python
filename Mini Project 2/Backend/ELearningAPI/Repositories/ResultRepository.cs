using Microsoft.EntityFrameworkCore;
using ELearningAPI.Data;
using ELearningAPI.Models;

namespace ELearningAPI.Repositories
{
    public class ResultRepository : Repository<Result>, IResultRepository
    {
        public ResultRepository(AppDbContext context) : base(context)
        {
        }

        public async Task<IEnumerable<Result>> GetResultsByUserIdAsync(int userId)
        {
            return await _context.Results
                .AsNoTracking()
                .Where(r => r.UserId == userId)
                .OrderByDescending(r => r.AttemptDate)
                .ToListAsync();
        }

        public async Task<IEnumerable<Result>> GetResultsWithDetailsAsync(int userId)
        {
            return await _context.Results
                .AsNoTracking()
                .Include(r => r.User)
                .Include(r => r.Quiz)
                    .ThenInclude(q => q!.Questions)
                .Where(r => r.UserId == userId)
                .OrderByDescending(r => r.AttemptDate)
                .ToListAsync();
        }
    }
}
