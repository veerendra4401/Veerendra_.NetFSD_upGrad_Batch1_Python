using Microsoft.AspNetCore.Mvc;
using ELearningAPI.DTOs;
using ELearningAPI.Services;

namespace ELearningAPI.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class CoursesController : ControllerBase
    {
        private readonly ICourseService _courseService;

        public CoursesController(ICourseService courseService)
        {
            _courseService = courseService;
        }

        /// <summary>
        /// GET /api/courses — List all courses
        /// </summary>
        [HttpGet]
        public async Task<ActionResult<IEnumerable<CourseResponseDto>>> GetAll()
        {
            var courses = await _courseService.GetAllCoursesAsync();
            return Ok(courses);
        }

        /// <summary>
        /// GET /api/courses/{id} — Get course by ID
        /// </summary>
        [HttpGet("{id}")]
        public async Task<ActionResult<CourseResponseDto>> GetById(int id)
        {
            var course = await _courseService.GetCourseByIdAsync(id);
            if (course == null)
                return NotFound(new { message = $"Course with ID {id} not found" });

            return Ok(course);
        }

        /// <summary>
        /// POST /api/courses — Create a new course
        /// </summary>
        [HttpPost]
        public async Task<ActionResult<CourseResponseDto>> Create([FromBody] CourseCreateDto dto)
        {
            if (!ModelState.IsValid)
                return BadRequest(ModelState);

            var course = await _courseService.CreateCourseAsync(dto);
            return CreatedAtAction(nameof(GetById), new { id = course.CourseId }, course);
        }

        /// <summary>
        /// PUT /api/courses/{id} — Update a course
        /// </summary>
        [HttpPut("{id}")]
        public async Task<ActionResult<CourseResponseDto>> Update(int id, [FromBody] CourseUpdateDto dto)
        {
            if (!ModelState.IsValid)
                return BadRequest(ModelState);

            var course = await _courseService.UpdateCourseAsync(id, dto);
            if (course == null)
                return NotFound(new { message = $"Course with ID {id} not found" });

            return Ok(course);
        }

        /// <summary>
        /// DELETE /api/courses/{id} — Delete a course
        /// </summary>
        [HttpDelete("{id}")]
        public async Task<ActionResult> Delete(int id)
        {
            var deleted = await _courseService.DeleteCourseAsync(id);
            if (!deleted)
                return NotFound(new { message = $"Course with ID {id} not found" });

            return Ok(new { message = "Course deleted successfully" });
        }
    }
}
