using AutoMapper;
using ELearningAPI.DTOs;
using ELearningAPI.Models;
using ELearningAPI.Repositories;

namespace ELearningAPI.Services
{
    public class LessonService : ILessonService
    {
        private readonly ILessonRepository _lessonRepository;
        private readonly ICourseRepository _courseRepository;
        private readonly IMapper _mapper;

        public LessonService(
            ILessonRepository lessonRepository,
            ICourseRepository courseRepository,
            IMapper mapper)
        {
            _lessonRepository = lessonRepository;
            _courseRepository = courseRepository;
            _mapper = mapper;
        }

        public async Task<IEnumerable<LessonResponseDto>> GetLessonsByCourseIdAsync(int courseId)
        {
            var lessons = await _lessonRepository.GetLessonsByCourseIdAsync(courseId);
            return _mapper.Map<IEnumerable<LessonResponseDto>>(lessons);
        }

        public async Task<LessonResponseDto> CreateLessonAsync(LessonCreateDto dto)
        {
            // Validate course exists
            var course = await _courseRepository.GetByIdAsync(dto.CourseId);
            if (course == null)
                throw new KeyNotFoundException($"Course with ID {dto.CourseId} not found");

            var lesson = _mapper.Map<Lesson>(dto);
            await _lessonRepository.AddAsync(lesson);
            await _lessonRepository.SaveChangesAsync();

            return _mapper.Map<LessonResponseDto>(lesson);
        }

        public async Task<LessonResponseDto?> UpdateLessonAsync(int id, LessonUpdateDto dto)
        {
            var lesson = await _lessonRepository.GetByIdAsync(id);
            if (lesson == null) return null;

            _mapper.Map(dto, lesson);
            _lessonRepository.Update(lesson);
            await _lessonRepository.SaveChangesAsync();

            return _mapper.Map<LessonResponseDto>(lesson);
        }

        public async Task<bool> DeleteLessonAsync(int id)
        {
            var lesson = await _lessonRepository.GetByIdAsync(id);
            if (lesson == null) return false;

            _lessonRepository.Delete(lesson);
            await _lessonRepository.SaveChangesAsync();
            return true;
        }
    }
}
