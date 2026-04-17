using System.ComponentModel.DataAnnotations;

namespace ELearningAPI.DTOs
{
    // ── Question DTOs ──────────────────────────

    public class QuestionCreateDto
    {
        [Required]
        public int QuizId { get; set; }

        [Required]
        public string QuestionText { get; set; } = string.Empty;

        [Required]
        [MaxLength(500)]
        public string OptionA { get; set; } = string.Empty;

        [Required]
        [MaxLength(500)]
        public string OptionB { get; set; } = string.Empty;

        [Required]
        [MaxLength(500)]
        public string OptionC { get; set; } = string.Empty;

        [Required]
        [MaxLength(500)]
        public string OptionD { get; set; } = string.Empty;

        [Required]
        [MaxLength(1)]
        [RegularExpression("[ABCD]", ErrorMessage = "CorrectAnswer must be A, B, C, or D")]
        public string CorrectAnswer { get; set; } = string.Empty;
    }

    public class QuestionResponseDto
    {
        public int QuestionId { get; set; }
        public int QuizId { get; set; }
        public string QuestionText { get; set; } = string.Empty;
        public string OptionA { get; set; } = string.Empty;
        public string OptionB { get; set; } = string.Empty;
        public string OptionC { get; set; } = string.Empty;
        public string OptionD { get; set; } = string.Empty;
        // Note: CorrectAnswer is intentionally excluded from response DTO
        // to prevent answer exposure to the client
    }

    // Used internally for quiz scoring (includes correct answer)
    public class QuestionWithAnswerDto
    {
        public int QuestionId { get; set; }
        public string CorrectAnswer { get; set; } = string.Empty;
    }
}
