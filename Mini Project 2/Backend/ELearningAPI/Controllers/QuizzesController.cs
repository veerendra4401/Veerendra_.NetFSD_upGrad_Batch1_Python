using Microsoft.AspNetCore.Mvc;
using ELearningAPI.DTOs;
using ELearningAPI.Services;

namespace ELearningAPI.Controllers
{
    [ApiController]
    [Route("api")]
    public class QuizzesController : ControllerBase
    {
        private readonly IQuizService _quizService;

        public QuizzesController(IQuizService quizService)
        {
            _quizService = quizService;
        }

        /// <summary>
        /// GET /api/quizzes/{courseId} — Get quizzes for a course
        /// </summary>
        [HttpGet("quizzes/{courseId}")]
        public async Task<ActionResult<IEnumerable<QuizResponseDto>>> GetByCourseId(int courseId)
        {
            var quizzes = await _quizService.GetQuizzesByCourseIdAsync(courseId);
            return Ok(quizzes);
        }

        /// <summary>
        /// POST /api/quizzes — Create a new quiz
        /// </summary>
        [HttpPost("quizzes")]
        public async Task<ActionResult<QuizResponseDto>> Create([FromBody] QuizCreateDto dto)
        {
            if (!ModelState.IsValid)
                return BadRequest(ModelState);

            var quiz = await _quizService.CreateQuizAsync(dto);
            return CreatedAtAction(nameof(GetByCourseId),
                new { courseId = quiz.CourseId }, quiz);
        }

        /// <summary>
        /// GET /api/quizzes/{quizId}/questions — Get questions for a quiz
        /// </summary>
        [HttpGet("quizzes/{quizId}/questions")]
        public async Task<ActionResult<IEnumerable<QuestionResponseDto>>> GetQuestions(int quizId)
        {
            try
            {
                var questions = await _quizService.GetQuestionsByQuizIdAsync(quizId);
                return Ok(questions);
            }
            catch (KeyNotFoundException ex)
            {
                return NotFound(new { message = ex.Message });
            }
        }

        /// <summary>
        /// POST /api/quizzes/{quizId}/submit — Submit quiz answers
        /// </summary>
        [HttpPost("quizzes/{quizId}/submit")]
        public async Task<ActionResult<ResultResponseDto>> SubmitQuiz(int quizId, [FromBody] QuizSubmitDto dto)
        {
            if (!ModelState.IsValid)
                return BadRequest(ModelState);

            try
            {
                var result = await _quizService.SubmitQuizAsync(quizId, dto);
                return Ok(result);
            }
            catch (KeyNotFoundException ex)
            {
                return NotFound(new { message = ex.Message });
            }
            catch (InvalidOperationException ex)
            {
                return BadRequest(new { message = ex.Message });
            }
        }
    }
}
