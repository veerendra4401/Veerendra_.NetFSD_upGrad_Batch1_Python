using ELearningAPI.DTOs;

namespace ELearningAPI.Services
{
    public interface IUserService
    {
        Task<UserResponseDto> RegisterAsync(UserRegisterDto dto);
        Task<UserResponseDto> LoginAsync(UserLoginDto dto);
        Task<UserResponseDto?> GetByIdAsync(int id);
        Task<UserResponseDto?> UpdateAsync(int id, UserUpdateDto dto);
    }
}
