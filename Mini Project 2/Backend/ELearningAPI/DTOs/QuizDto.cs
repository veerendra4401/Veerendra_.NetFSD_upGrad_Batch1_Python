using System.ComponentModel.DataAnnotations;

namespace ELearningAPI.DTOs
{
    // ── Quiz DTOs ──────────────────────────────

    public class QuizCreateDto
    {
        [Required]
        public int CourseId { get; set; }

        [Required]
        [MaxLength(200)]
        public string Title { get; set; } = string.Empty;
    }

    public class QuizResponseDto
    {
        public int QuizId { get; set; }
        public int CourseId { get; set; }
        public string Title { get; set; } = string.Empty;
        public int QuestionCount { get; set; }
        public List<QuestionResponseDto> Questions { get; set; } = new();
    }
}
