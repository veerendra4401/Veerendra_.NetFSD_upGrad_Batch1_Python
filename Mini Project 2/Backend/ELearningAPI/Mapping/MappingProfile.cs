using AutoMapper;
using ELearningAPI.Models;
using ELearningAPI.DTOs;

namespace ELearningAPI.Mapping
{
    public class MappingProfile : Profile
    {
        public MappingProfile()
        {
            // ── User Mappings ──────────────────────────
            CreateMap<User, UserResponseDto>();
            CreateMap<UserRegisterDto, User>()
                .ForMember(dest => dest.PasswordHash, opt => opt.Ignore()); // Handled in service
            CreateMap<UserUpdateDto, User>()
                .ForMember(dest => dest.PasswordHash, opt => opt.Ignore())
                .ForMember(dest => dest.UserId, opt => opt.Ignore())
                .ForMember(dest => dest.CreatedAt, opt => opt.Ignore());

            // ── Course Mappings ────────────────────────
            CreateMap<Course, CourseResponseDto>()
                .ForMember(dest => dest.CreatorName,
                    opt => opt.MapFrom(src => src.Creator != null ? src.Creator.FullName : ""))
                .ForMember(dest => dest.LessonCount,
                    opt => opt.MapFrom(src => src.Lessons.Count))
                .ForMember(dest => dest.QuizCount,
                    opt => opt.MapFrom(src => src.Quizzes.Count));
            CreateMap<CourseCreateDto, Course>();
            CreateMap<CourseUpdateDto, Course>()
                .ForMember(dest => dest.CourseId, opt => opt.Ignore())
                .ForMember(dest => dest.CreatedBy, opt => opt.Ignore())
                .ForMember(dest => dest.CreatedAt, opt => opt.Ignore());

            // ── Lesson Mappings ────────────────────────
            CreateMap<Lesson, LessonResponseDto>();
            CreateMap<LessonCreateDto, Lesson>();
            CreateMap<LessonUpdateDto, Lesson>()
                .ForMember(dest => dest.LessonId, opt => opt.Ignore())
                .ForMember(dest => dest.CourseId, opt => opt.Ignore());

            // ── Quiz Mappings ──────────────────────────
            CreateMap<Quiz, QuizResponseDto>()
                .ForMember(dest => dest.QuestionCount,
                    opt => opt.MapFrom(src => src.Questions.Count));
            CreateMap<QuizCreateDto, Quiz>();

            // ── Question Mappings ──────────────────────
            CreateMap<Question, QuestionResponseDto>();
            CreateMap<Question, QuestionWithAnswerDto>();
            CreateMap<QuestionCreateDto, Question>();

            // ── Result Mappings ────────────────────────
            CreateMap<Result, ResultResponseDto>()
                .ForMember(dest => dest.UserName,
                    opt => opt.MapFrom(src => src.User != null ? src.User.FullName : ""))
                .ForMember(dest => dest.QuizTitle,
                    opt => opt.MapFrom(src => src.Quiz != null ? src.Quiz.Title : ""))
                .ForMember(dest => dest.TotalQuestions, opt => opt.Ignore())
                .ForMember(dest => dest.Percentage, opt => opt.Ignore())
                .ForMember(dest => dest.Grade, opt => opt.Ignore())
                .ForMember(dest => dest.Passed, opt => opt.Ignore());
        }
    }
}
