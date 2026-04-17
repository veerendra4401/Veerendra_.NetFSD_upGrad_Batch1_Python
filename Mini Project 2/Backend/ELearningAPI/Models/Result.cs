using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace ELearningAPI.Models
{
    public class Result
    {
        [Key]
        [DatabaseGenerated(DatabaseGeneratedOption.Identity)]
        public int ResultId { get; set; }

        public int UserId { get; set; }

        public int QuizId { get; set; }

        [Required]
        public int Score { get; set; }

        public DateTime AttemptDate { get; set; } = DateTime.UtcNow;

        // Navigation properties
        [ForeignKey("UserId")]
        public User? User { get; set; }

        [ForeignKey("QuizId")]
        public Quiz? Quiz { get; set; }
    }
}
