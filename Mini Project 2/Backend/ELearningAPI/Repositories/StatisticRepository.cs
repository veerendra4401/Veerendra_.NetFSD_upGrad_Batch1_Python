using Microsoft.EntityFrameworkCore;
using ELearningAPI.Data;
using ELearningAPI.Models;
using ELearningAPI.DTOs;

namespace ELearningAPI.Repositories
{
    public class StatisticRepository : IStatisticRepository
    {
        private readonly AppDbContext _context;

        public StatisticRepository(AppDbContext context)
        {
            _context = context;
        }

        /// <summary>
        /// 1. Aggregation Requirements (GROUP BY, COUNT, AVG)
        /// Calculates per-course statistics using LINQ aggregation.
        /// </summary>
        public async Task<IEnumerable<CourseStatDto>> GetCourseStatisticsAsync()
        {
            return await _context.Courses
                .AsNoTracking()
                .Select(c => new CourseStatDto
                {
                    CourseId = c.CourseId,
                    Title = c.Title,
                    LessonCount = c.Lessons.Count(), // COUNT
                    TotalAttempts = c.Quizzes.SelectMany(q => q.Results).Count(), // COUNT
                    AverageQuizScore = c.Quizzes.SelectMany(q => q.Results).Any() 
                        ? c.Quizzes.SelectMany(q => q.Results).Average(r => r.Score) // AVG
                        : 0
                })
                .ToListAsync();
        }

        /// <summary>
        /// 2. Subquery Requirements
        /// Find users whose scores are higher than the overall platform average.
        /// </summary>
        public async Task<IEnumerable<User>> GetTopPerformersAsync()
        {
            // Calculating the platform average score as a scalar value (Subquery equivalent in EF Core)
            var platformAverage = await _context.Results.AnyAsync() 
                ? await _context.Results.AverageAsync(r => r.Score) 
                : 0;

            // Main query using the average as a filter
            return await _context.Users
                .AsNoTracking()
                .Where(u => u.Results.Any() && u.Results.Average(r => r.Score) > platformAverage)
                .ToListAsync();
        }

        /// <summary>
        /// 3. Set Operators Requirements (UNION)
        /// Combines recent course additions and recent quiz completions into a single feed.
        /// </summary>
        public async Task<IEnumerable<PlatformActivityDto>> GetRecentPlatformActivityAsync()
        {
            var recentCourses = _context.Courses
                .OrderByDescending(c => c.CreatedAt)
                .Take(5)
                .Select(c => new PlatformActivityDto
                {
                    ActivityType = "New Course Added",
                    Title = c.Title,
                    Date = c.CreatedAt,
                    Details = $"Created by {c.Creator.FullName}"
                });

            var recentResults = _context.Results
                .OrderByDescending(r => r.AttemptDate)
                .Take(5)
                .Select(r => new PlatformActivityDto
                {
                    ActivityType = "Quiz Attempted",
                    Title = r.Quiz.Title,
                    Date = r.AttemptDate,
                    Details = $"{r.User.FullName} scored {r.Score}"
                });

            // Using UNION set operator
            return await recentCourses
                .Union(recentResults)
                .OrderByDescending(a => a.Date)
                .ToListAsync();
        }
    }
}
