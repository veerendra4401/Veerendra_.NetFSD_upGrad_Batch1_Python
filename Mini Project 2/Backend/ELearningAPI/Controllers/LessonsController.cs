using Microsoft.AspNetCore.Mvc;
using ELearningAPI.DTOs;
using ELearningAPI.Services;

namespace ELearningAPI.Controllers
{
    [ApiController]
    [Route("api")]
    public class LessonsController : ControllerBase
    {
        private readonly ILessonService _lessonService;

        public LessonsController(ILessonService lessonService)
        {
            _lessonService = lessonService;
        }

        /// <summary>
        /// GET /api/courses/{courseId}/lessons — Get lessons for a course
        /// </summary>
        [HttpGet("courses/{courseId}/lessons")]
        public async Task<ActionResult<IEnumerable<LessonResponseDto>>> GetByCourseId(int courseId)
        {
            var lessons = await _lessonService.GetLessonsByCourseIdAsync(courseId);
            return Ok(lessons);
        }

        /// <summary>
        /// POST /api/lessons — Create a new lesson
        /// </summary>
        [HttpPost("lessons")]
        public async Task<ActionResult<LessonResponseDto>> Create([FromBody] LessonCreateDto dto)
        {
            if (!ModelState.IsValid)
                return BadRequest(ModelState);

            try
            {
                var lesson = await _lessonService.CreateLessonAsync(dto);
                return CreatedAtAction(nameof(GetByCourseId),
                    new { courseId = lesson.CourseId }, lesson);
            }
            catch (KeyNotFoundException ex)
            {
                return NotFound(new { message = ex.Message });
            }
        }

        /// <summary>
        /// PUT /api/lessons/{id} — Update a lesson
        /// </summary>
        [HttpPut("lessons/{id}")]
        public async Task<ActionResult<LessonResponseDto>> Update(int id, [FromBody] LessonUpdateDto dto)
        {
            if (!ModelState.IsValid)
                return BadRequest(ModelState);

            var lesson = await _lessonService.UpdateLessonAsync(id, dto);
            if (lesson == null)
                return NotFound(new { message = $"Lesson with ID {id} not found" });

            return Ok(lesson);
        }

        /// <summary>
        /// DELETE /api/lessons/{id} — Delete a lesson
        /// </summary>
        [HttpDelete("lessons/{id}")]
        public async Task<ActionResult> Delete(int id)
        {
            var deleted = await _lessonService.DeleteLessonAsync(id);
            if (!deleted)
                return NotFound(new { message = $"Lesson with ID {id} not found" });

            return Ok(new { message = "Lesson deleted successfully" });
        }
    }
}
