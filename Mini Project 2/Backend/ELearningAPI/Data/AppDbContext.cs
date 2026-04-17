using Microsoft.EntityFrameworkCore;
using ELearningAPI.Models;

namespace ELearningAPI.Data
{
    public class AppDbContext : DbContext
    {
        public AppDbContext(DbContextOptions<AppDbContext> options) : base(options)
        {
        }

        public DbSet<User> Users { get; set; }
        public DbSet<Course> Courses { get; set; }
        public DbSet<Lesson> Lessons { get; set; }
        public DbSet<Quiz> Quizzes { get; set; }
        public DbSet<Question> Questions { get; set; }
        public DbSet<Result> Results { get; set; }

        protected override void OnModelCreating(ModelBuilder modelBuilder)
        {
            base.OnModelCreating(modelBuilder);

            // ── Standardize UTC handling (Fix inappropriate timings) ──
            foreach (var entityType in modelBuilder.Model.GetEntityTypes())
            {
                var properties = entityType.GetProperties()
                    .Where(p => p.ClrType == typeof(DateTime) || p.ClrType == typeof(DateTime?));

                foreach (var property in properties)
                {
                    property.SetValueConverter(new Microsoft.EntityFrameworkCore.Storage.ValueConversion.ValueConverter<DateTime, DateTime>(
                        v => v.Kind == DateTimeKind.Utc ? v : DateTime.SpecifyKind(v, DateTimeKind.Utc),
                        v => DateTime.SpecifyKind(v, DateTimeKind.Utc)));
                }
            }

            // ── User ──────────────────────────────────
            modelBuilder.Entity<User>(entity =>
            {
                entity.HasKey(u => u.UserId);
                entity.HasIndex(u => u.Email).IsUnique();
                entity.Property(u => u.FullName).IsRequired().HasMaxLength(100);
                entity.Property(u => u.Email).IsRequired().HasMaxLength(200);
                entity.Property(u => u.PasswordHash).IsRequired().HasMaxLength(256);
                entity.Property(u => u.CreatedAt)
                      .HasColumnType("datetime")
                      .HasDefaultValueSql("CURRENT_TIMESTAMP");
            });

            // ── Course ────────────────────────────────
            modelBuilder.Entity<Course>(entity =>
            {
                entity.HasKey(c => c.CourseId);
                entity.Property(c => c.Title).IsRequired().HasMaxLength(200);
                entity.Property(c => c.Description).HasColumnType("text");
                entity.Property(c => c.CreatedAt)
                      .HasColumnType("datetime")
                      .HasDefaultValueSql("CURRENT_TIMESTAMP");

                // One User → Many Courses
                entity.HasOne(c => c.Creator)
                      .WithMany(u => u.Courses)
                      .HasForeignKey(c => c.CreatedBy)
                      .OnDelete(DeleteBehavior.Restrict);
            });

            // ── Lesson ────────────────────────────────
            modelBuilder.Entity<Lesson>(entity =>
            {
                entity.HasKey(l => l.LessonId);
                entity.Property(l => l.Title).IsRequired().HasMaxLength(200);
                entity.Property(l => l.Content).HasColumnType("text");
                entity.Property(l => l.OrderIndex).IsRequired();

                // One Course → Many Lessons
                entity.HasOne(l => l.Course)
                      .WithMany(c => c.Lessons)
                      .HasForeignKey(l => l.CourseId)
                      .OnDelete(DeleteBehavior.Cascade);
            });

            // ── Quiz ──────────────────────────────────
            modelBuilder.Entity<Quiz>(entity =>
            {
                entity.HasKey(q => q.QuizId);
                entity.Property(q => q.Title).IsRequired().HasMaxLength(200);

                // One Course → Many Quizzes
                entity.HasOne(q => q.Course)
                      .WithMany(c => c.Quizzes)
                      .HasForeignKey(q => q.CourseId)
                      .OnDelete(DeleteBehavior.Cascade);
            });

            // ── Question ──────────────────────────────
            modelBuilder.Entity<Question>(entity =>
            {
                entity.HasKey(q => q.QuestionId);
                entity.Property(q => q.QuestionText).IsRequired().HasColumnType("text");
                entity.Property(q => q.OptionA).IsRequired().HasMaxLength(500);
                entity.Property(q => q.OptionB).IsRequired().HasMaxLength(500);
                entity.Property(q => q.OptionC).IsRequired().HasMaxLength(500);
                entity.Property(q => q.OptionD).IsRequired().HasMaxLength(500);
                entity.Property(q => q.CorrectAnswer).IsRequired().HasMaxLength(1);

                // One Quiz → Many Questions
                entity.HasOne(q => q.Quiz)
                      .WithMany(qz => qz.Questions)
                      .HasForeignKey(q => q.QuizId)
                      .OnDelete(DeleteBehavior.Cascade);
            });

            // ── Result ────────────────────────────────
            modelBuilder.Entity<Result>(entity =>
            {
                entity.HasKey(r => r.ResultId);
                entity.Property(r => r.Score).IsRequired();
                entity.Property(r => r.AttemptDate)
                      .HasColumnType("datetime")
                      .HasDefaultValueSql("CURRENT_TIMESTAMP");

                // One User → Many Results
                entity.HasOne(r => r.User)
                      .WithMany(u => u.Results)
                      .HasForeignKey(r => r.UserId)
                      .OnDelete(DeleteBehavior.Cascade);

                // One Quiz → Many Results
                entity.HasOne(r => r.Quiz)
                      .WithMany(qz => qz.Results)
                      .HasForeignKey(r => r.QuizId)
                      .OnDelete(DeleteBehavior.Cascade);
            });
        }
    }
}
