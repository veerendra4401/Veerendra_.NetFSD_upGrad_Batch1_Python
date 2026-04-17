using ELearningAPI.DTOs;

namespace ELearningAPI.Services
{
    public interface ICourseService
    {
        Task<IEnumerable<CourseResponseDto>> GetAllCoursesAsync();
        Task<CourseResponseDto?> GetCourseByIdAsync(int id);
        Task<CourseResponseDto> CreateCourseAsync(CourseCreateDto dto);
        Task<CourseResponseDto?> UpdateCourseAsync(int id, CourseUpdateDto dto);
        Task<bool> DeleteCourseAsync(int id);
    }
}
