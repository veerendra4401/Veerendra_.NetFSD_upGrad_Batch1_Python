using Microsoft.AspNetCore.Mvc;
using ELearningAPI.DTOs;
using ELearningAPI.Services;

namespace ELearningAPI.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class ResultsController : ControllerBase
    {
        private readonly IResultService _resultService;

        public ResultsController(IResultService resultService)
        {
            _resultService = resultService;
        }

        /// <summary>
        /// GET /api/results/{userId} — Get results for a user
        /// </summary>
        [HttpGet("{userId}")]
        public async Task<ActionResult<IEnumerable<ResultResponseDto>>> GetByUserId(int userId)
        {
            var results = await _resultService.GetResultsByUserIdAsync(userId);
            return Ok(results);
        }
    }
}
