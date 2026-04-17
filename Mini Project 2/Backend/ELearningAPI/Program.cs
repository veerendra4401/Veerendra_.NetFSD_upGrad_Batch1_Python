using Microsoft.EntityFrameworkCore;
using ELearningAPI.Data;
using ELearningAPI.Models;
using ELearningAPI.Repositories;
using ELearningAPI.Services;

var builder = WebApplication.CreateBuilder(args);

// ── Database (MySQL via Pomelo) ────────────────────────────
var connectionString = builder.Configuration.GetConnectionString("DefaultConnection");
var serverVersion = new MySqlServerVersion(new Version(8, 0, 36));

builder.Services.AddDbContext<AppDbContext>(options =>
    options.UseMySql(connectionString, serverVersion, mysqlOptions =>
    {
        mysqlOptions.EnableRetryOnFailure(
            maxRetryCount: 3,
            maxRetryDelay: TimeSpan.FromSeconds(5),
            errorNumbersToAdd: null);
    }));

// ── AutoMapper ─────────────────────────────────────────────
builder.Services.AddAutoMapper(typeof(Program));

// ── Repositories (DI) ──────────────────────────────────────
builder.Services.AddScoped(typeof(IRepository<>), typeof(Repository<>));
builder.Services.AddScoped<ICourseRepository, CourseRepository>();
builder.Services.AddScoped<IQuizRepository, QuizRepository>();
builder.Services.AddScoped<IUserRepository, UserRepository>();
builder.Services.AddScoped<ILessonRepository, LessonRepository>();
builder.Services.AddScoped<IResultRepository, ResultRepository>();
builder.Services.AddScoped<IStatisticRepository, StatisticRepository>();

// ── Services (DI) ──────────────────────────────────────────
builder.Services.AddScoped<ICourseService, CourseService>();
builder.Services.AddScoped<IQuizService, QuizService>();
builder.Services.AddScoped<IUserService, UserService>();
builder.Services.AddScoped<ILessonService, LessonService>();
builder.Services.AddScoped<IResultService, ResultService>();

// ── Controllers & Swagger ──────────────────────────────────
builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

// ── CORS (allow frontend) ─────────────────────────────────
builder.Services.AddCors(options =>
{
    options.AddPolicy("AllowAll", policy =>
    {
        policy.AllowAnyOrigin()
              .AllowAnyMethod()
              .AllowAnyHeader();
    });
});

var app = builder.Build();

// ── Seed Database ──────────────────────────────────────────
using (var scope = app.Services.CreateScope())
{
    var context = scope.ServiceProvider.GetRequiredService<AppDbContext>();
    
    // Apply pending migrations or create database
    context.Database.EnsureCreated();
    
    // Seed data
    DbSeeder.Seed(context);
}

// ── Middleware Pipeline ────────────────────────────────────
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

app.UseCors("AllowAll");

// Serve frontend static files from wwwroot
app.UseDefaultFiles();
app.UseStaticFiles();

app.UseAuthorization();
app.MapControllers();

// Fallback to index.html for SPA routing
app.MapFallbackToFile("index.html");

app.Run();

// Make Program class accessible for integration tests
public partial class Program { }
