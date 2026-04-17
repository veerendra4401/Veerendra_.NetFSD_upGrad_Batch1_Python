using Moq;
using AutoMapper;
using ELearningAPI.DTOs;
using ELearningAPI.Models;
using ELearningAPI.Repositories;
using ELearningAPI.Services;
using ELearningAPI.Mapping;

namespace ELearningAPI.Tests
{
    /// <summary>
    /// Tests for Quiz submission scoring, LINQ filtering, and exception handling
    /// </summary>
    public class QuizServiceTests
    {
        private readonly Mock<IQuizRepository> _mockQuizRepo;
        private readonly Mock<IRepository<Question>> _mockQuestionRepo;
        private readonly Mock<IResultRepository> _mockResultRepo;
        private readonly IMapper _mapper;
        private readonly QuizService _quizService;

        public QuizServiceTests()
        {
            _mockQuizRepo = new Mock<IQuizRepository>();
            _mockQuestionRepo = new Mock<IRepository<Question>>();
            _mockResultRepo = new Mock<IResultRepository>();

            var mapperConfig = new MapperConfiguration(cfg =>
            {
                cfg.AddProfile<MappingProfile>();
            });
            _mapper = mapperConfig.CreateMapper();

            _quizService = new QuizService(
                _mockQuizRepo.Object,
                _mockQuestionRepo.Object,
                _mockResultRepo.Object,
                _mapper);
        }

        [Fact]
        public async Task SubmitQuiz_AllCorrect_Returns100Percent()
        {
            // Arrange
            var quiz = CreateSampleQuiz();
            _mockQuizRepo.Setup(r => r.GetQuizWithQuestionsAsync(1))
                .ReturnsAsync(quiz);
            _mockResultRepo.Setup(r => r.AddAsync(It.IsAny<Result>()))
                .Returns(Task.CompletedTask);
            _mockResultRepo.Setup(r => r.SaveChangesAsync())
                .Returns(Task.CompletedTask);

            var submitDto = new QuizSubmitDto
            {
                UserId = 1,
                Answers = new Dictionary<int, string>
                {
                    { 1, "A" },
                    { 2, "D" },
                    { 3, "C" }
                }
            };

            // Act
            var result = await _quizService.SubmitQuizAsync(1, submitDto);

            // Assert
            Assert.Equal(3, result.Score);
            Assert.Equal(3, result.TotalQuestions);
            Assert.Equal(100.0, result.Percentage);
            Assert.Equal("A", result.Grade);
            Assert.True(result.Passed);
        }

        [Fact]
        public async Task SubmitQuiz_NoneCorrect_Returns0Percent()
        {
            // Arrange
            var quiz = CreateSampleQuiz();
            _mockQuizRepo.Setup(r => r.GetQuizWithQuestionsAsync(1))
                .ReturnsAsync(quiz);
            _mockResultRepo.Setup(r => r.AddAsync(It.IsAny<Result>()))
                .Returns(Task.CompletedTask);
            _mockResultRepo.Setup(r => r.SaveChangesAsync())
                .Returns(Task.CompletedTask);

            var submitDto = new QuizSubmitDto
            {
                UserId = 1,
                Answers = new Dictionary<int, string>
                {
                    { 1, "B" },
                    { 2, "A" },
                    { 3, "D" }
                }
            };

            // Act
            var result = await _quizService.SubmitQuizAsync(1, submitDto);

            // Assert
            Assert.Equal(0, result.Score);
            Assert.Equal(0.0, result.Percentage);
            Assert.Equal("F", result.Grade);
            Assert.False(result.Passed);
        }

        [Fact]
        public async Task SubmitQuiz_PartialCorrect_ReturnsCorrectScore()
        {
            // Arrange
            var quiz = CreateSampleQuiz();
            _mockQuizRepo.Setup(r => r.GetQuizWithQuestionsAsync(1))
                .ReturnsAsync(quiz);
            _mockResultRepo.Setup(r => r.AddAsync(It.IsAny<Result>()))
                .Returns(Task.CompletedTask);
            _mockResultRepo.Setup(r => r.SaveChangesAsync())
                .Returns(Task.CompletedTask);

            var submitDto = new QuizSubmitDto
            {
                UserId = 1,
                Answers = new Dictionary<int, string>
                {
                    { 1, "A" }, // Correct
                    { 2, "A" }, // Wrong (correct is D)
                    { 3, "C" }  // Correct
                }
            };

            // Act
            var result = await _quizService.SubmitQuizAsync(1, submitDto);

            // Assert
            Assert.Equal(2, result.Score);
            Assert.Equal(66.7, result.Percentage);
            Assert.Equal("D", result.Grade);
            Assert.True(result.Passed);
        }

        [Fact]
        public async Task SubmitQuiz_InvalidQuizId_ThrowsKeyNotFoundException()
        {
            // Arrange
            _mockQuizRepo.Setup(r => r.GetQuizWithQuestionsAsync(999))
                .ReturnsAsync((Quiz?)null);

            var submitDto = new QuizSubmitDto
            {
                UserId = 1,
                Answers = new Dictionary<int, string> { { 1, "A" } }
            };

            // Act & Assert
            await Assert.ThrowsAsync<KeyNotFoundException>(
                () => _quizService.SubmitQuizAsync(999, submitDto));
        }

        [Fact]
        public async Task SubmitQuiz_EmptyQuiz_ThrowsInvalidOperationException()
        {
            // Arrange
            var emptyQuiz = new Quiz
            {
                QuizId = 2,
                Title = "Empty Quiz",
                Questions = new List<Question>()
            };

            _mockQuizRepo.Setup(r => r.GetQuizWithQuestionsAsync(2))
                .ReturnsAsync(emptyQuiz);

            var submitDto = new QuizSubmitDto
            {
                UserId = 1,
                Answers = new Dictionary<int, string>()
            };

            // Act & Assert
            await Assert.ThrowsAsync<InvalidOperationException>(
                () => _quizService.SubmitQuizAsync(2, submitDto));
        }

        [Fact]
        public async Task GetQuizzesByCourseId_ReturnsFilteredQuizzes()
        {
            // Arrange — LINQ filtering test
            var quizzes = new List<Quiz>
            {
                new Quiz
                {
                    QuizId = 1,
                    CourseId = 1,
                    Title = "JS Quiz",
                    Questions = new List<Question>
                    {
                        new Question { QuestionId = 1, QuestionText = "Q1" }
                    }
                }
            };

            _mockQuizRepo.Setup(r => r.GetQuizzesByCourseIdAsync(1))
                .ReturnsAsync(quizzes);

            // Act
            var result = await _quizService.GetQuizzesByCourseIdAsync(1);

            // Assert
            var quizList = result.ToList();
            Assert.Single(quizList);
            Assert.Equal("JS Quiz", quizList[0].Title);
            Assert.Equal(1, quizList[0].QuestionCount);
        }

        [Fact]
        public async Task GetQuestions_InvalidQuizId_ThrowsKeyNotFoundException()
        {
            // Arrange
            _mockQuizRepo.Setup(r => r.GetQuizWithQuestionsAsync(999))
                .ReturnsAsync((Quiz?)null);

            // Act & Assert
            await Assert.ThrowsAsync<KeyNotFoundException>(
                () => _quizService.GetQuestionsByQuizIdAsync(999));
        }

        [Fact]
        public async Task CreateQuestion_ValidInput_ReturnsCreatedQuestion()
        {
            // Arrange
            var dto = new QuestionCreateDto
            {
                QuizId = 1,
                QuestionText = "Test Question",
                OptionA = "A",
                OptionB = "B",
                OptionC = "C",
                OptionD = "D",
                CorrectAnswer = "A"
            };

            _mockQuestionRepo.Setup(r => r.AddAsync(It.IsAny<Question>()))
                .Returns(Task.CompletedTask);
            _mockQuestionRepo.Setup(r => r.SaveChangesAsync())
                .Returns(Task.CompletedTask);

            // Act
            var result = await _quizService.CreateQuestionAsync(dto);

            // Assert
            Assert.NotNull(result);
            Assert.Equal("Test Question", result.QuestionText);
        }

        // ── Helper to create a sample quiz for tests ──
        private static Quiz CreateSampleQuiz()
        {
            return new Quiz
            {
                QuizId = 1,
                CourseId = 1,
                Title = "JavaScript Quiz",
                Questions = new List<Question>
                {
                    new Question
                    {
                        QuestionId = 1,
                        QuestionText = "What is JavaScript?",
                        OptionA = "A programming language",
                        OptionB = "A markup language",
                        OptionC = "A styling language",
                        OptionD = "A database language",
                        CorrectAnswer = "A"
                    },
                    new Question
                    {
                        QuestionId = 2,
                        QuestionText = "Variable declaration keyword?",
                        OptionA = "var",
                        OptionB = "let",
                        OptionC = "const",
                        OptionD = "All of the above",
                        CorrectAnswer = "D"
                    },
                    new Question
                    {
                        QuestionId = 3,
                        QuestionText = "typeof null?",
                        OptionA = "null",
                        OptionB = "undefined",
                        OptionC = "object",
                        OptionD = "number",
                        CorrectAnswer = "C"
                    }
                }
            };
        }
    }
}
