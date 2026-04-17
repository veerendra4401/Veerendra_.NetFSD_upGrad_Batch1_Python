using ELearningAPI.DTOs;

namespace ELearningAPI.Services
{
    public interface ILessonService
    {
        Task<IEnumerable<LessonResponseDto>> GetLessonsByCourseIdAsync(int courseId);
        Task<LessonResponseDto> CreateLessonAsync(LessonCreateDto dto);
        Task<LessonResponseDto?> UpdateLessonAsync(int id, LessonUpdateDto dto);
        Task<bool> DeleteLessonAsync(int id);
    }
}
