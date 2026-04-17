using Microsoft.AspNetCore.Mvc;
using ELearningAPI.DTOs;
using ELearningAPI.Services;

namespace ELearningAPI.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class UsersController : ControllerBase
    {
        private readonly IUserService _userService;

        public UsersController(IUserService userService)
        {
            _userService = userService;
        }

        /// <summary>
        /// POST /api/users/register — Register a new user
        /// </summary>
        [HttpPost("register")]
        public async Task<ActionResult<UserResponseDto>> Register([FromBody] UserRegisterDto dto)
        {
            if (!ModelState.IsValid)
                return BadRequest(ModelState);

            try
            {
                var user = await _userService.RegisterAsync(dto);
                return CreatedAtAction(nameof(GetById), new { id = user.UserId }, user);
            }
            catch (InvalidOperationException ex)
            {
                return BadRequest(new { message = ex.Message });
            }
        }

        /// <summary>
        /// POST /api/users/login — Authenticate a user
        /// </summary>
        [HttpPost("login")]
        public async Task<ActionResult<UserResponseDto>> Login([FromBody] UserLoginDto dto)
        {
            if (!ModelState.IsValid)
                return BadRequest(ModelState);

            try
            {
                var user = await _userService.LoginAsync(dto);
                return Ok(user);
            }
            catch (UnauthorizedAccessException ex)
            {
                return Unauthorized(new { message = ex.Message });
            }
        }

        /// <summary>
        /// GET /api/users/{id} — Get user by ID
        /// </summary>
        [HttpGet("{id}")]
        public async Task<ActionResult<UserResponseDto>> GetById(int id)
        {
            var user = await _userService.GetByIdAsync(id);
            if (user == null)
                return NotFound(new { message = $"User with ID {id} not found" });

            return Ok(user);
        }

        /// <summary>
        /// PUT /api/users/{id} — Update user profile
        /// </summary>
        [HttpPut("{id}")]
        public async Task<ActionResult<UserResponseDto>> Update(int id, [FromBody] UserUpdateDto dto)
        {
            if (!ModelState.IsValid)
                return BadRequest(ModelState);

            var user = await _userService.UpdateAsync(id, dto);
            if (user == null)
                return NotFound(new { message = $"User with ID {id} not found" });

            return Ok(user);
        }
    }
}
