using ELearningAPI.Models;
using BCrypt.Net;

namespace ELearningAPI.Data
{
    public static class DbSeeder
    {
        public static void Seed(AppDbContext context)
        {
            // Ensure the database is created
            context.Database.EnsureCreated();

            // Skip if data already exists
            if (context.Users.Any())
                return;

            // ── Seed Users ──────────────────────────────
            var users = new List<User>
            {
                new User
                {
                    FullName = "John Doe",
                    Email = "john@example.com",
                    PasswordHash = BCrypt.Net.BCrypt.HashPassword("Password123!"),
                    CreatedAt = DateTime.UtcNow
                },
                new User
                {
                    FullName = "Jane Smith",
                    Email = "jane@example.com",
                    PasswordHash = BCrypt.Net.BCrypt.HashPassword("Password456!"),
                    CreatedAt = DateTime.UtcNow
                },
                new User
                {
                    FullName = "Admin User",
                    Email = "admin@elearning.com",
                    PasswordHash = BCrypt.Net.BCrypt.HashPassword("Admin123!"),
                    CreatedAt = DateTime.UtcNow
                }
            };

            context.Users.AddRange(users);
            context.SaveChanges();

            // ── Seed Courses (matching existing courses.js) ──
            var courses = new List<Course>
            {
                new Course
                {
                    Title = "JavaScript Fundamentals",
                    Description = "Learn the basics of JavaScript programming language",
                    CreatedBy = users[0].UserId,
                    CreatedAt = DateTime.UtcNow
                },
                new Course
                {
                    Title = "Advanced JavaScript",
                    Description = "Master advanced JavaScript concepts and patterns",
                    CreatedBy = users[0].UserId,
                    CreatedAt = DateTime.UtcNow
                },
                new Course
                {
                    Title = "Bootstrap for Beginners",
                    Description = "Build modern web applications with Bootstrap",
                    CreatedBy = users[1].UserId,
                    CreatedAt = DateTime.UtcNow
                }
            };

            context.Courses.AddRange(courses);
            context.SaveChanges();

            // ── Seed Lessons (matching existing courses.js lessons) ──
            var lessons = new List<Lesson>
            {
                // JavaScript Fundamentals lessons
                new Lesson { CourseId = courses[0].CourseId, Title = "Introduction to JavaScript", Content = "Learn what JavaScript is and how it powers the web. JavaScript is a high-level, interpreted programming language that is one of the core technologies of the World Wide Web.", OrderIndex = 1 },
                new Lesson { CourseId = courses[0].CourseId, Title = "Variables and Data Types", Content = "Understand var, let, const, and JavaScript data types including strings, numbers, booleans, objects, arrays, null, and undefined.", OrderIndex = 2 },
                new Lesson { CourseId = courses[0].CourseId, Title = "Functions and Scope", Content = "Learn about function declarations, expressions, arrow functions, and how scope works in JavaScript including block, function, and global scope.", OrderIndex = 3 },
                new Lesson { CourseId = courses[0].CourseId, Title = "Arrays and Objects", Content = "Master working with arrays and objects, including array methods like map, filter, reduce, and object destructuring.", OrderIndex = 4 },
                new Lesson { CourseId = courses[0].CourseId, Title = "Loops and Iteration", Content = "Learn for loops, while loops, do-while, for...in, for...of, and iteration protocols.", OrderIndex = 5 },
                new Lesson { CourseId = courses[0].CourseId, Title = "DOM Manipulation", Content = "Learn how to interact with the Document Object Model to create dynamic web pages using querySelector, event listeners, and element manipulation.", OrderIndex = 6 },

                // Advanced JavaScript lessons
                new Lesson { CourseId = courses[1].CourseId, Title = "Closures and Prototypes", Content = "Deep dive into closures, lexical scoping, prototype chain, and prototypal inheritance in JavaScript.", OrderIndex = 1 },
                new Lesson { CourseId = courses[1].CourseId, Title = "Async Programming", Content = "Understand the event loop, call stack, callback queue, and how asynchronous operations work in JavaScript.", OrderIndex = 2 },
                new Lesson { CourseId = courses[1].CourseId, Title = "Promises and Callbacks", Content = "Master Promises, async/await, Promise chaining, error handling, and converting callback-based code to Promises.", OrderIndex = 3 },
                new Lesson { CourseId = courses[1].CourseId, Title = "ES6+ Features", Content = "Learn modern JavaScript features: template literals, destructuring, spread/rest operators, modules, classes, and symbols.", OrderIndex = 4 },
                new Lesson { CourseId = courses[1].CourseId, Title = "Design Patterns", Content = "Implement common design patterns in JavaScript: Module, Observer, Singleton, Factory, and Decorator patterns.", OrderIndex = 5 },
                new Lesson { CourseId = courses[1].CourseId, Title = "Performance Optimization", Content = "Learn techniques for optimizing JavaScript performance: debouncing, throttling, lazy loading, memoization, and web workers.", OrderIndex = 6 },

                // Bootstrap for Beginners lessons
                new Lesson { CourseId = courses[2].CourseId, Title = "What is Bootstrap", Content = "Introduction to Bootstrap CSS framework, its history, and why it's the most popular front-end framework.", OrderIndex = 1 },
                new Lesson { CourseId = courses[2].CourseId, Title = "Why use Bootstrap", Content = "Benefits of using Bootstrap: responsive design, mobile-first approach, cross-browser compatibility, and rapid prototyping.", OrderIndex = 2 },
                new Lesson { CourseId = courses[2].CourseId, Title = "Grid System", Content = "Master the 12-column grid system, breakpoints, containers, rows, columns, and responsive layout techniques.", OrderIndex = 3 },
                new Lesson { CourseId = courses[2].CourseId, Title = "Bootstrap Components", Content = "Learn to use Bootstrap components: navbars, cards, modals, carousels, alerts, badges, and buttons.", OrderIndex = 4 },
                new Lesson { CourseId = courses[2].CourseId, Title = "Bootstrap Classes", Content = "Understand utility classes for spacing, typography, colors, display, flexbox, and positioning.", OrderIndex = 5 },
                new Lesson { CourseId = courses[2].CourseId, Title = "Forms", Content = "Build responsive forms with Bootstrap form controls, validation, input groups, and custom form elements.", OrderIndex = 6 }
            };

            context.Lessons.AddRange(lessons);
            context.SaveChanges();

            // ── Seed Quizzes (matching existing quiz-data.js) ──
            var quizzes = new List<Quiz>
            {
                new Quiz
                {
                    CourseId = courses[0].CourseId,
                    Title = "JavaScript Fundamentals Quiz"
                },
                new Quiz
                {
                    CourseId = courses[1].CourseId,
                    Title = "Advanced JavaScript Quiz"
                },
                new Quiz
                {
                    CourseId = courses[2].CourseId,
                    Title = "Bootstrap Basics Quiz"
                }
            };

            context.Quizzes.AddRange(quizzes);
            context.SaveChanges();

            // ── Seed Questions (matching existing quiz-data.js) ──
            var questions = new List<Question>
            {
                // JavaScript Fundamentals Quiz questions
                new Question
                {
                    QuizId = quizzes[0].QuizId,
                    QuestionText = "What is JavaScript?",
                    OptionA = "A programming language",
                    OptionB = "A markup language",
                    OptionC = "A styling language",
                    OptionD = "A database language",
                    CorrectAnswer = "A"
                },
                new Question
                {
                    QuizId = quizzes[0].QuizId,
                    QuestionText = "Which keyword is used to declare a variable in JavaScript?",
                    OptionA = "var",
                    OptionB = "let",
                    OptionC = "const",
                    OptionD = "All of the above",
                    CorrectAnswer = "D"
                },
                new Question
                {
                    QuizId = quizzes[0].QuizId,
                    QuestionText = "What is the output of typeof null?",
                    OptionA = "null",
                    OptionB = "undefined",
                    OptionC = "object",
                    OptionD = "number",
                    CorrectAnswer = "C"
                },
                new Question
                {
                    QuizId = quizzes[0].QuizId,
                    QuestionText = "Which method adds elements to the end of an array?",
                    OptionA = "push()",
                    OptionB = "pop()",
                    OptionC = "shift()",
                    OptionD = "unshift()",
                    CorrectAnswer = "A"
                },
                new Question
                {
                    QuizId = quizzes[0].QuizId,
                    QuestionText = "What is a closure in JavaScript?",
                    OptionA = "A function with access to its outer scope",
                    OptionB = "A way to close browser window",
                    OptionC = "A type of loop",
                    OptionD = "An error handling method",
                    CorrectAnswer = "A"
                },

                // Advanced JavaScript Quiz questions
                new Question
                {
                    QuizId = quizzes[1].QuizId,
                    QuestionText = "What does the 'this' keyword refer to in an arrow function?",
                    OptionA = "The function itself",
                    OptionB = "The global object",
                    OptionC = "The enclosing lexical context",
                    OptionD = "undefined",
                    CorrectAnswer = "C"
                },
                new Question
                {
                    QuizId = quizzes[1].QuizId,
                    QuestionText = "What is the purpose of async/await in JavaScript?",
                    OptionA = "To make code run faster",
                    OptionB = "To handle asynchronous operations more cleanly",
                    OptionC = "To create new threads",
                    OptionD = "To prevent errors",
                    CorrectAnswer = "B"
                },
                new Question
                {
                    QuizId = quizzes[1].QuizId,
                    QuestionText = "Which design pattern restricts a class to a single instance?",
                    OptionA = "Factory",
                    OptionB = "Observer",
                    OptionC = "Singleton",
                    OptionD = "Decorator",
                    CorrectAnswer = "C"
                },
                new Question
                {
                    QuizId = quizzes[1].QuizId,
                    QuestionText = "What is event delegation?",
                    OptionA = "Deleting events",
                    OptionB = "Assigning events to parent elements",
                    OptionC = "Creating custom events",
                    OptionD = "Preventing event bubbling",
                    CorrectAnswer = "B"
                },
                new Question
                {
                    QuizId = quizzes[1].QuizId,
                    QuestionText = "What does Promise.all() do?",
                    OptionA = "Executes promises sequentially",
                    OptionB = "Returns the first resolved promise",
                    OptionC = "Waits for all promises to resolve",
                    OptionD = "Cancels all promises",
                    CorrectAnswer = "C"
                },

                // Bootstrap Quiz questions
                new Question
                {
                    QuizId = quizzes[2].QuizId,
                    QuestionText = "How many columns does the Bootstrap grid system have?",
                    OptionA = "6",
                    OptionB = "10",
                    OptionC = "12",
                    OptionD = "16",
                    CorrectAnswer = "C"
                },
                new Question
                {
                    QuizId = quizzes[2].QuizId,
                    QuestionText = "Which Bootstrap class creates a responsive container?",
                    OptionA = ".wrapper",
                    OptionB = ".container",
                    OptionC = ".responsive",
                    OptionD = ".box",
                    CorrectAnswer = "B"
                },
                new Question
                {
                    QuizId = quizzes[2].QuizId,
                    QuestionText = "Which class is used for a primary button in Bootstrap?",
                    OptionA = ".btn-main",
                    OptionB = ".btn-blue",
                    OptionC = ".btn-primary",
                    OptionD = ".button-primary",
                    CorrectAnswer = "C"
                },
                new Question
                {
                    QuizId = quizzes[2].QuizId,
                    QuestionText = "What is Bootstrap's mobile-first approach?",
                    OptionA = "Only works on mobile",
                    OptionB = "Designs for small screens first, then scales up",
                    OptionC = "Requires mobile testing",
                    OptionD = "Uses mobile-specific CSS",
                    CorrectAnswer = "B"
                },
                new Question
                {
                    QuizId = quizzes[2].QuizId,
                    QuestionText = "Which Bootstrap breakpoint prefix is for medium devices?",
                    OptionA = "sm",
                    OptionB = "md",
                    OptionC = "lg",
                    OptionD = "xl",
                    CorrectAnswer = "B"
                }
            };

            context.Questions.AddRange(questions);
            context.SaveChanges();

            // ── Seed some sample Results ──
            var results = new List<Result>
            {
                new Result
                {
                    UserId = users[0].UserId,
                    QuizId = quizzes[0].QuizId,
                    Score = 4,
                    AttemptDate = DateTime.UtcNow.AddDays(-5)
                },
                new Result
                {
                    UserId = users[0].UserId,
                    QuizId = quizzes[1].QuizId,
                    Score = 3,
                    AttemptDate = DateTime.UtcNow.AddDays(-3)
                },
                new Result
                {
                    UserId = users[1].UserId,
                    QuizId = quizzes[0].QuizId,
                    Score = 5,
                    AttemptDate = DateTime.UtcNow.AddDays(-2)
                }
            };

            context.Results.AddRange(results);
            context.SaveChanges();
        }
    }
}
