using Microsoft.AspNetCore.Mvc;
using ELearningAPI.Repositories;
using ELearningAPI.DTOs;
using AutoMapper;

namespace ELearningAPI.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class StatisticsController : ControllerBase
    {
        private readonly IStatisticRepository _statRepository;
        private readonly IMapper _mapper;

        public StatisticsController(IStatisticRepository statRepository, IMapper mapper)
        {
            _statRepository = statRepository;
            _mapper = mapper;
        }

        /// <summary>
        /// GET /api/statistics/course-stats — Aggregation Example (GROUP BY, COUNT, AVG)
        /// </summary>
        [HttpGet("course-stats")]
        public async Task<ActionResult<IEnumerable<CourseStatDto>>> GetCourseStats()
        {
            var stats = await _statRepository.GetCourseStatisticsAsync();
            return Ok(stats);
        }

        /// <summary>
        /// GET /api/statistics/top-performers — Subquery Example (Above platform average)
        /// </summary>
        [HttpGet("top-performers")]
        public async Task<ActionResult<IEnumerable<UserResponseDto>>> GetTopPerformers()
        {
            var users = await _statRepository.GetTopPerformersAsync();
            return Ok(_mapper.Map<IEnumerable<UserResponseDto>>(users));
        }

        /// <summary>
        /// GET /api/statistics/activity — UNION Example (Set Operators)
        /// </summary>
        [HttpGet("activity")]
        public async Task<ActionResult<IEnumerable<PlatformActivityDto>>> GetPlatformActivity()
        {
            var activity = await _statRepository.GetRecentPlatformActivityAsync();
            return Ok(activity);
        }
    }
}
