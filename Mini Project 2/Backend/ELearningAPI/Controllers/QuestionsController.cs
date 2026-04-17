using Microsoft.AspNetCore.Mvc;
using ELearningAPI.DTOs;
using ELearningAPI.Services;

namespace ELearningAPI.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class QuestionsController : ControllerBase
    {
        private readonly IQuizService _quizService;

        public QuestionsController(IQuizService quizService)
        {
            _quizService = quizService;
        }

        /// <summary>
        /// POST /api/questions — Create a new question
        /// </summary>
        [HttpPost]
        public async Task<ActionResult<QuestionResponseDto>> Create([FromBody] QuestionCreateDto dto)
        {
            if (!ModelState.IsValid)
                return BadRequest(ModelState);

            var question = await _quizService.CreateQuestionAsync(dto);
            return CreatedAtAction(nameof(Create), new { id = question.QuestionId }, question);
        }
    }
}
