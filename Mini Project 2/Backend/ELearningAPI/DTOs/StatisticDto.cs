namespace ELearningAPI.DTOs
{
    public class CourseStatDto
    {
        public int CourseId { get; set; }
        public string Title { get; set; } = string.Empty;
        public int LessonCount { get; set; }
        public double AverageQuizScore { get; set; }
        public int TotalAttempts { get; set; }
    }

    public class PlatformActivityDto
    {
        public string ActivityType { get; set; } = string.Empty; // "Course" or "Quiz"
        public string Title { get; set; } = string.Empty;
        public DateTime Date { get; set; }
        public string Details { get; set; } = string.Empty;
    }
}
