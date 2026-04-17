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
    /// Tests for Course CRUD operations
    /// </summary>
    public class CourseServiceTests
    {
        private readonly Mock<ICourseRepository> _mockCourseRepo;
        private readonly IMapper _mapper;
        private readonly CourseService _courseService;

        public CourseServiceTests()
        {
            _mockCourseRepo = new Mock<ICourseRepository>();

            var mapperConfig = new MapperConfiguration(cfg =>
            {
                cfg.AddProfile<MappingProfile>();
            });
            _mapper = mapperConfig.CreateMapper();

            _courseService = new CourseService(_mockCourseRepo.Object, _mapper);
        }

        [Fact]
        public async Task GetAllCourses_ReturnsAllCourses()
        {
            // Arrange
            var courses = new List<Course>
            {
                new Course
                {
                    CourseId = 1,
                    Title = "JavaScript Fundamentals",
                    Description = "Learn JS basics",
                    CreatedBy = 1,
                    Creator = new User { UserId = 1, FullName = "John Doe" },
                    Lessons = new List<Lesson>(),
                    Quizzes = new List<Quiz>()
                },
                new Course
                {
                    CourseId = 2,
                    Title = "Advanced JavaScript",
                    Description = "Advanced JS concepts",
                    CreatedBy = 1,
                    Creator = new User { UserId = 1, FullName = "John Doe" },
                    Lessons = new List<Lesson>(),
                    Quizzes = new List<Quiz>()
                }
            };

            _mockCourseRepo.Setup(r => r.GetAllWithDetailsAsync())
                .ReturnsAsync(courses);

            // Act
            var result = await _courseService.GetAllCoursesAsync();

            // Assert
            var courseList = result.ToList();
            Assert.Equal(2, courseList.Count);
            Assert.Equal("JavaScript Fundamentals", courseList[0].Title);
            Assert.Equal("Advanced JavaScript", courseList[1].Title);
        }

        [Fact]
        public async Task GetCourseById_ExistingId_ReturnsCourse()
        {
            // Arrange
            var course = new Course
            {
                CourseId = 1,
                Title = "JavaScript Fundamentals",
                Description = "Learn JS basics",
                CreatedBy = 1,
                Creator = new User { UserId = 1, FullName = "John Doe" },
                Lessons = new List<Lesson>
                {
                    new Lesson { LessonId = 1, Title = "Intro", OrderIndex = 1 }
                },
                Quizzes = new List<Quiz>()
            };

            _mockCourseRepo.Setup(r => r.GetByIdWithDetailsAsync(1))
                .ReturnsAsync(course);

            // Act
            var result = await _courseService.GetCourseByIdAsync(1);

            // Assert
            Assert.NotNull(result);
            Assert.Equal("JavaScript Fundamentals", result!.Title);
            Assert.Equal(1, result.LessonCount);
            Assert.Equal("John Doe", result.CreatorName);
        }

        [Fact]
        public async Task GetCourseById_NonExistingId_ReturnsNull()
        {
            // Arrange
            _mockCourseRepo.Setup(r => r.GetByIdWithDetailsAsync(999))
                .ReturnsAsync((Course?)null);

            // Act
            var result = await _courseService.GetCourseByIdAsync(999);

            // Assert
            Assert.Null(result);
        }

        [Fact]
        public async Task CreateCourse_ValidInput_ReturnsCreatedCourse()
        {
            // Arrange
            var createDto = new CourseCreateDto
            {
                Title = "New Course",
                Description = "A new test course",
                CreatedBy = 1
            };

            _mockCourseRepo.Setup(r => r.AddAsync(It.IsAny<Course>()))
                .Returns(Task.CompletedTask);
            _mockCourseRepo.Setup(r => r.SaveChangesAsync())
                .Returns(Task.CompletedTask);
            _mockCourseRepo.Setup(r => r.GetByIdWithDetailsAsync(It.IsAny<int>()))
                .ReturnsAsync(new Course
                {
                    CourseId = 4,
                    Title = "New Course",
                    Description = "A new test course",
                    CreatedBy = 1,
                    Creator = new User { UserId = 1, FullName = "John" },
                    Lessons = new List<Lesson>(),
                    Quizzes = new List<Quiz>()
                });

            // Act
            var result = await _courseService.CreateCourseAsync(createDto);

            // Assert
            Assert.NotNull(result);
            Assert.Equal("New Course", result.Title);
            _mockCourseRepo.Verify(r => r.AddAsync(It.IsAny<Course>()), Times.Once);
            _mockCourseRepo.Verify(r => r.SaveChangesAsync(), Times.Once);
        }

        [Fact]
        public async Task UpdateCourse_ExistingId_ReturnsUpdatedCourse()
        {
            // Arrange
            var existingCourse = new Course
            {
                CourseId = 1,
                Title = "Old Title",
                Description = "Old desc",
                CreatedBy = 1
            };

            var updateDto = new CourseUpdateDto
            {
                Title = "Updated Title",
                Description = "Updated description"
            };

            _mockCourseRepo.Setup(r => r.GetByIdAsync(1))
                .ReturnsAsync(existingCourse);
            _mockCourseRepo.Setup(r => r.SaveChangesAsync())
                .Returns(Task.CompletedTask);
            _mockCourseRepo.Setup(r => r.GetByIdWithDetailsAsync(1))
                .ReturnsAsync(new Course
                {
                    CourseId = 1,
                    Title = "Updated Title",
                    Description = "Updated description",
                    CreatedBy = 1,
                    Creator = new User { UserId = 1, FullName = "John" },
                    Lessons = new List<Lesson>(),
                    Quizzes = new List<Quiz>()
                });

            // Act
            var result = await _courseService.UpdateCourseAsync(1, updateDto);

            // Assert
            Assert.NotNull(result);
            Assert.Equal("Updated Title", result!.Title);
        }

        [Fact]
        public async Task DeleteCourse_ExistingId_ReturnsTrue()
        {
            // Arrange
            var course = new Course { CourseId = 1, Title = "Delete Me" };
            _mockCourseRepo.Setup(r => r.GetByIdAsync(1))
                .ReturnsAsync(course);
            _mockCourseRepo.Setup(r => r.SaveChangesAsync())
                .Returns(Task.CompletedTask);

            // Act
            var result = await _courseService.DeleteCourseAsync(1);

            // Assert
            Assert.True(result);
            _mockCourseRepo.Verify(r => r.Delete(course), Times.Once);
        }

        [Fact]
        public async Task DeleteCourse_NonExistingId_ReturnsFalse()
        {
            // Arrange
            _mockCourseRepo.Setup(r => r.GetByIdAsync(999))
                .ReturnsAsync((Course?)null);

            // Act
            var result = await _courseService.DeleteCourseAsync(999);

            // Assert
            Assert.False(result);
        }
    }
}
