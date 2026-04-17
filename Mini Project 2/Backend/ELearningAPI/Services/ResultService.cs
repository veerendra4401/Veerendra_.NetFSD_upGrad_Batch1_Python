using AutoMapper;
using ELearningAPI.DTOs;
using ELearningAPI.Repositories;

namespace ELearningAPI.Services
{
    public class ResultService : IResultService
    {
        private readonly IResultRepository _resultRepository;
        private readonly IMapper _mapper;

        public ResultService(IResultRepository resultRepository, IMapper mapper)
        {
            _resultRepository = resultRepository;
            _mapper = mapper;
        }

        public async Task<IEnumerable<ResultResponseDto>> GetResultsByUserIdAsync(int userId)
        {
            var results = await _resultRepository.GetResultsWithDetailsAsync(userId);

            var responseDtos = new List<ResultResponseDto>();

            foreach (var result in results)
            {
                var dto = _mapper.Map<ResultResponseDto>(result);
                
                // Calculate computed fields
                int totalQuestions = result.Quiz?.Questions?.Count ?? 0;
                dto.TotalQuestions = totalQuestions;
                dto.Percentage = totalQuestions > 0
                    ? Math.Round((double)result.Score / totalQuestions * 100, 1)
                    : 0;
                dto.Grade = CalculateGrade(dto.Percentage);
                dto.Passed = dto.Percentage >= 60;

                responseDtos.Add(dto);
            }

            return responseDtos;
        }

        private static string CalculateGrade(double percentage)
        {
            if (percentage >= 90) return "A";
            if (percentage >= 80) return "B";
            if (percentage >= 70) return "C";
            if (percentage >= 60) return "D";
            return "F";
        }
    }
}
