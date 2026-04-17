using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace ELearningAPI.Models
{
    public class Question
    {
        [Key]
        [DatabaseGenerated(DatabaseGeneratedOption.Identity)]
        public int QuestionId { get; set; }

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
        public string CorrectAnswer { get; set; } = string.Empty; // A, B, C, or D

        // Navigation property
        [ForeignKey("QuizId")]
        public Quiz? Quiz { get; set; }
    }
}
