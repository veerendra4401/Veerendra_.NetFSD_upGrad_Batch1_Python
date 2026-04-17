using AutoMapper;
using ELearningAPI.DTOs;
using ELearningAPI.Models;
using ELearningAPI.Repositories;

namespace ELearningAPI.Services
{
    public class UserService : IUserService
    {
        private readonly IUserRepository _userRepository;
        private readonly IMapper _mapper;

        public UserService(IUserRepository userRepository, IMapper mapper)
        {
            _userRepository = userRepository;
            _mapper = mapper;
        }

        /// <summary>
        /// Register a new user with BCrypt password hashing
        /// </summary>
        public async Task<UserResponseDto> RegisterAsync(UserRegisterDto dto)
        {
            // Check for duplicate email
            var existing = await _userRepository.GetByEmailAsync(dto.Email);
            if (existing != null)
                throw new InvalidOperationException("A user with this email already exists");

            var user = _mapper.Map<User>(dto);
            // Hash password using BCrypt (NOT plain text)
            user.PasswordHash = BCrypt.Net.BCrypt.HashPassword(dto.Password);
            user.CreatedAt = DateTime.UtcNow;

            await _userRepository.AddAsync(user);
            await _userRepository.SaveChangesAsync();

            return _mapper.Map<UserResponseDto>(user);
        }

        /// <summary>
        /// Authenticate user by verifying hashed password
        /// </summary>
        public async Task<UserResponseDto> LoginAsync(UserLoginDto dto)
        {
            var user = await _userRepository.GetByEmailAsync(dto.Email);
            if (user == null)
                throw new UnauthorizedAccessException("Invalid email or password");

            // Verify the password using BCrypt
            bool isValid = BCrypt.Net.BCrypt.Verify(dto.Password, user.PasswordHash);
            if (!isValid)
                throw new UnauthorizedAccessException("Invalid email or password");

            return _mapper.Map<UserResponseDto>(user);
        }

        public async Task<UserResponseDto?> GetByIdAsync(int id)
        {
            var user = await _userRepository.GetByIdAsync(id);
            if (user == null) return null;
            return _mapper.Map<UserResponseDto>(user);
        }

        public async Task<UserResponseDto?> UpdateAsync(int id, UserUpdateDto dto)
        {
            var user = await _userRepository.GetByIdAsync(id);
            if (user == null) return null;

            _mapper.Map(dto, user);
            _userRepository.Update(user);
            await _userRepository.SaveChangesAsync();

            return _mapper.Map<UserResponseDto>(user);
        }
    }
}
