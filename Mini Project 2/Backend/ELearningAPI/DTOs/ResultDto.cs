using System.ComponentModel.DataAnnotations;

namespace ELearningAPI.DTOs
{
    // ── Result DTOs ────────────────────────────

    public class QuizSubmitDto
    {
        [Required]
        public int UserId { get; set; }

        [Required]
        public Dictionary<int, string> Answers { get; set; } = new();
        // Key: QuestionId, Value: selected answer (A, B, C, or D)
    }

    public class ResultResponseDto
    {
        public int ResultId { get; set; }
        public int UserId { get; set; }
        public string UserName { get; set; } = string.Empty;
        public int QuizId { get; set; }
        public string QuizTitle { get; set; } = string.Empty;
        public int Score { get; set; }
        public int TotalQuestions { get; set; }
        public double Percentage { get; set; }
        public string Grade { get; set; } = string.Empty;
        public bool Passed { get; set; }
        public DateTime AttemptDate { get; set; }
    }
}
