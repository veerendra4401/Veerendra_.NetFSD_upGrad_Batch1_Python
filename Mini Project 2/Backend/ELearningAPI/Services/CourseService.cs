using AutoMapper;
using ELearningAPI.DTOs;
using ELearningAPI.Models;
using ELearningAPI.Repositories;

namespace ELearningAPI.Services
{
    public class CourseService : ICourseService
    {
        private readonly ICourseRepository _courseRepository;
        private readonly IMapper _mapper;

        public CourseService(ICourseRepository courseRepository, IMapper mapper)
        {
            _courseRepository = courseRepository;
            _mapper = mapper;
        }

        public async Task<IEnumerable<CourseResponseDto>> GetAllCoursesAsync()
        {
            var courses = await _courseRepository.GetAllWithDetailsAsync();
            return _mapper.Map<IEnumerable<CourseResponseDto>>(courses);
        }

        public async Task<CourseResponseDto?> GetCourseByIdAsync(int id)
        {
            var course = await _courseRepository.GetByIdWithDetailsAsync(id);
            if (course == null) return null;
            return _mapper.Map<CourseResponseDto>(course);
        }

        public async Task<CourseResponseDto> CreateCourseAsync(CourseCreateDto dto)
        {
            var course = _mapper.Map<Course>(dto);
            course.CreatedAt = DateTime.UtcNow;

            await _courseRepository.AddAsync(course);
            await _courseRepository.SaveChangesAsync();

            // Reload with details
            var created = await _courseRepository.GetByIdWithDetailsAsync(course.CourseId);
            return _mapper.Map<CourseResponseDto>(created!);
        }

        public async Task<CourseResponseDto?> UpdateCourseAsync(int id, CourseUpdateDto dto)
        {
            var course = await _courseRepository.GetByIdAsync(id);
            if (course == null) return null;

            _mapper.Map(dto, course);
            _courseRepository.Update(course);
            await _courseRepository.SaveChangesAsync();

            var updated = await _courseRepository.GetByIdWithDetailsAsync(id);
            return _mapper.Map<CourseResponseDto>(updated!);
        }

        public async Task<bool> DeleteCourseAsync(int id)
        {
            var course = await _courseRepository.GetByIdAsync(id);
            if (course == null) return false;

            _courseRepository.Delete(course);
            await _courseRepository.SaveChangesAsync();
            return true;
        }
    }
}
