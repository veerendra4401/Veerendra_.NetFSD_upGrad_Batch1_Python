using System.ComponentModel.DataAnnotations;

namespace ELearningAPI.DTOs
{
    // ── Lesson DTOs ────────────────────────────

    public class LessonCreateDto
    {
        [Required]
        public int CourseId { get; set; }

        [Required]
        [MaxLength(200)]
        public string Title { get; set; } = string.Empty;

        public string Content { get; set; } = string.Empty;

        [Required]
        public int OrderIndex { get; set; }
    }

    public class LessonUpdateDto
    {
        [Required]
        [MaxLength(200)]
        public string Title { get; set; } = string.Empty;

        public string Content { get; set; } = string.Empty;

        [Required]
        public int OrderIndex { get; set; }
    }

    public class LessonResponseDto
    {
        public int LessonId { get; set; }
        public int CourseId { get; set; }
        public string Title { get; set; } = string.Empty;
        public string Content { get; set; } = string.Empty;
        public int OrderIndex { get; set; }
    }
}
