using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace ELearningAPI.Models
{
    public class Quiz
    {
        [Key]
        [DatabaseGenerated(DatabaseGeneratedOption.Identity)]
        public int QuizId { get; set; }

        public int CourseId { get; set; }

        [Required]
        [MaxLength(200)]
        public string Title { get; set; } = string.Empty;

        // Navigation properties
        [ForeignKey("CourseId")]
        public Course? Course { get; set; }

        public ICollection<Question> Questions { get; set; } = new List<Question>();
        public ICollection<Result> Results { get; set; } = new List<Result>();
    }
}
