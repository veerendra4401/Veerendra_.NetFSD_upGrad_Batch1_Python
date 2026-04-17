using Microsoft.AspNetCore.Mvc;
using Moq;
using ELearningAPI.Controllers;
using ELearningAPI.DTOs;
using ELearningAPI.Services;

namespace ELearningAPI.Tests
{
    /// <summary>
    /// API integration tests — validates status codes and response data
    /// </summary>
    public class ApiControllerTests
    {
        // ── Courses Controller Tests ─────────────────────

        [Fact]
        public async Task CoursesController_GetAll_Returns200WithData()
        {
            // Arrange
            var mockService = new Mock<ICourseService>();
            mockService.Setup(s => s.GetAllCoursesAsync())
                .ReturnsAsync(new List<CourseResponseDto>
                {
                    new CourseResponseDto { CourseId = 1, Title = "JS Basics" },
                    new CourseResponseDto { CourseId = 2, Title = "Advanced JS" }
                });

            var controller = new CoursesController(mockService.Object);

            // Act
            var actionResult = await controller.GetAll();

            // Assert
            var okResult = Assert.IsType<OkObjectResult>(actionResult.Result);
            Assert.Equal(200, okResult.StatusCode);
            var courses = Assert.IsAssignableFrom<IEnumerable<CourseResponseDto>>(okResult.Value);
            Assert.Equal(2, courses.Count());
        }

        [Fact]
        public async Task CoursesController_GetById_ExistingId_Returns200()
        {
            // Arrange
            var mockService = new Mock<ICourseService>();
            mockService.Setup(s => s.GetCourseByIdAsync(1))
                .ReturnsAsync(new CourseResponseDto { CourseId = 1, Title = "JS Basics" });

            var controller = new CoursesController(mockService.Object);

            // Act
            var actionResult = await controller.GetById(1);

            // Assert
            var okResult = Assert.IsType<OkObjectResult>(actionResult.Result);
            Assert.Equal(200, okResult.StatusCode);
            var course = Assert.IsType<CourseResponseDto>(okResult.Value);
            Assert.Equal("JS Basics", course.Title);
        }

        [Fact]
        public async Task CoursesController_GetById_NonExisting_Returns404()
        {
            // Arrange
            var mockService = new Mock<ICourseService>();
            mockService.Setup(s => s.GetCourseByIdAsync(999))
                .ReturnsAsync((CourseResponseDto?)null);

            var controller = new CoursesController(mockService.Object);

            // Act
            var actionResult = await controller.GetById(999);

            // Assert
            var notFoundResult = Assert.IsType<NotFoundObjectResult>(actionResult.Result);
            Assert.Equal(404, notFoundResult.StatusCode);
        }

        [Fact]
        public async Task CoursesController_Create_ValidData_Returns201()
        {
            // Arrange
            var mockService = new Mock<ICourseService>();
            var createDto = new CourseCreateDto
            {
                Title = "New Course",
                Description = "Test",
                CreatedBy = 1
            };

            mockService.Setup(s => s.CreateCourseAsync(It.IsAny<CourseCreateDto>()))
                .ReturnsAsync(new CourseResponseDto { CourseId = 3, Title = "New Course" });

            var controller = new CoursesController(mockService.Object);

            // Act
            var actionResult = await controller.Create(createDto);

            // Assert
            var createdResult = Assert.IsType<CreatedAtActionResult>(actionResult.Result);
            Assert.Equal(201, createdResult.StatusCode);
        }

        [Fact]
        public async Task CoursesController_Delete_NonExisting_Returns404()
        {
            // Arrange
            var mockService = new Mock<ICourseService>();
            mockService.Setup(s => s.DeleteCourseAsync(999))
                .ReturnsAsync(false);

            var controller = new CoursesController(mockService.Object);

            // Act
            var actionResult = await controller.Delete(999);

            // Assert
            var notFoundResult = Assert.IsType<NotFoundObjectResult>(actionResult);
            Assert.Equal(404, notFoundResult.StatusCode);
        }

        // ── Users Controller Tests ───────────────────────

        [Fact]
        public async Task UsersController_Register_ValidData_Returns201()
        {
            // Arrange
            var mockService = new Mock<IUserService>();
            var registerDto = new UserRegisterDto
            {
                FullName = "Test User",
                Email = "test@example.com",
                Password = "Password123!"
            };

            mockService.Setup(s => s.RegisterAsync(It.IsAny<UserRegisterDto>()))
                .ReturnsAsync(new UserResponseDto
                {
                    UserId = 4,
                    FullName = "Test User",
                    Email = "test@example.com"
                });

            var controller = new UsersController(mockService.Object);

            // Act
            var actionResult = await controller.Register(registerDto);

            // Assert
            var createdResult = Assert.IsType<CreatedAtActionResult>(actionResult.Result);
            Assert.Equal(201, createdResult.StatusCode);
        }

        [Fact]
        public async Task UsersController_Register_DuplicateEmail_Returns400()
        {
            // Arrange
            var mockService = new Mock<IUserService>();
            mockService.Setup(s => s.RegisterAsync(It.IsAny<UserRegisterDto>()))
                .ThrowsAsync(new InvalidOperationException("A user with this email already exists"));

            var controller = new UsersController(mockService.Object);
            var registerDto = new UserRegisterDto
            {
                FullName = "Test",
                Email = "john@example.com",
                Password = "Password123!"
            };

            // Act
            var actionResult = await controller.Register(registerDto);

            // Assert
            var badRequestResult = Assert.IsType<BadRequestObjectResult>(actionResult.Result);
            Assert.Equal(400, badRequestResult.StatusCode);
        }

        [Fact]
        public async Task UsersController_GetById_NonExisting_Returns404()
        {
            // Arrange
            var mockService = new Mock<IUserService>();
            mockService.Setup(s => s.GetByIdAsync(999))
                .ReturnsAsync((UserResponseDto?)null);

            var controller = new UsersController(mockService.Object);

            // Act
            var actionResult = await controller.GetById(999);

            // Assert
            var notFoundResult = Assert.IsType<NotFoundObjectResult>(actionResult.Result);
            Assert.Equal(404, notFoundResult.StatusCode);
        }

        // ── Quizzes Controller Tests ─────────────────────

        [Fact]
        public async Task QuizzesController_SubmitQuiz_InvalidQuiz_Returns404()
        {
            // Arrange
            var mockService = new Mock<IQuizService>();
            mockService.Setup(s => s.SubmitQuizAsync(999, It.IsAny<QuizSubmitDto>()))
                .ThrowsAsync(new KeyNotFoundException("Quiz with ID 999 not found"));

            var controller = new QuizzesController(mockService.Object);
            var submitDto = new QuizSubmitDto
            {
                UserId = 1,
                Answers = new Dictionary<int, string> { { 1, "A" } }
            };

            // Act
            var actionResult = await controller.SubmitQuiz(999, submitDto);

            // Assert
            var notFoundResult = Assert.IsType<NotFoundObjectResult>(actionResult.Result);
            Assert.Equal(404, notFoundResult.StatusCode);
        }

        [Fact]
        public async Task QuizzesController_SubmitQuiz_ValidSubmission_Returns200()
        {
            // Arrange
            var mockService = new Mock<IQuizService>();
            mockService.Setup(s => s.SubmitQuizAsync(1, It.IsAny<QuizSubmitDto>()))
                .ReturnsAsync(new ResultResponseDto
                {
                    ResultId = 1,
                    Score = 5,
                    TotalQuestions = 5,
                    Percentage = 100,
                    Grade = "A",
                    Passed = true
                });

            var controller = new QuizzesController(mockService.Object);
            var submitDto = new QuizSubmitDto
            {
                UserId = 1,
                Answers = new Dictionary<int, string>
                {
                    { 1, "A" }, { 2, "D" }, { 3, "C" }, { 4, "A" }, { 5, "A" }
                }
            };

            // Act
            var actionResult = await controller.SubmitQuiz(1, submitDto);

            // Assert
            var okResult = Assert.IsType<OkObjectResult>(actionResult.Result);
            Assert.Equal(200, okResult.StatusCode);
            var result = Assert.IsType<ResultResponseDto>(okResult.Value);
            Assert.True(result.Passed);
            Assert.Equal("A", result.Grade);
        }
    }
}
