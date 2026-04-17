function calculateGrade(percentage) {
    if (percentage >= 90) return 'A';
    if (percentage >= 80) return 'B';
    if (percentage >= 70) return 'C';
    if (percentage >= 60) return 'D';
    return 'F';
}

function calculatePercentage(score, total) {
    if (total === 0) return 0;
    return (score / total) * 100;
}

function determinePassFail(percentage) {
    return percentage >= 60;
}

// ── State variables ──────────────────────────────────────
let currentQuizId = null;
let currentQuizQuestions = [];
let apiCoursesData = [];

// ── Async function to load quiz data from API ────────────
async function loadQuizData() {
    try {
        showLoading();

        // Try API first
        try {
            // Get quizzes for course 1 (JavaScript Fundamentals)
            const quizzes = await ApiClient.getQuizzesByCourse(1);
            if (quizzes && quizzes.length > 0) {
                currentQuizId = quizzes[0].quizId;
                const questions = await ApiClient.getQuizQuestions(currentQuizId);
                hideLoading();
                currentQuizQuestions = questions;
                return questions;
            }
        } catch (apiError) {
            console.warn('API unavailable, using local data:', apiError.message);
        }

        // Fallback to local quizData
        const data = await new Promise((resolve) => {
            setTimeout(() => {
                resolve(quizData);
            }, 1500);
        });

        hideLoading();
        return data;
    } catch (error) {
        console.error('Error loading quiz:', error);
        hideLoading();
        showError('Failed to load quiz. Please try again.');
        return [];
    }
}

// Alternative async/await syntax for loading data from array
async function loadCourseDataAsync() {
    try {
        // Try API first
        try {
            const apiCourses = await ApiClient.getCourses();
            if (apiCourses && apiCourses.length > 0) {
                return apiCourses;
            }
        } catch (apiError) {
            console.warn('API unavailable, using local courses:', apiError.message);
        }

        // Fallback to local data
        return new Promise((resolve) => {
            setTimeout(() => {
                resolve(courses);
            }, 1000);
        });
    } catch (error) {
        console.error('Error loading courses:', error);
        return [];
    }
}

// DOM Manipulation - Render quiz
async function renderQuiz() {
    const quizContainer = document.getElementById('quizContainer');
    if (!quizContainer) return;

    try {
        const questions = await loadQuizData();
        const isApiData = questions.length > 0 && questions[0].questionId !== undefined;

        if (questions.length === 0) {
            quizContainer.innerHTML = '<p class="error">No questions available</p>';
            return;
        }

        let html = '<form id="quizForm">';

        questions.forEach((q, index) => {
            const qId = isApiData ? q.questionId : q.id;
            html += `
                <div class="question" data-question-id="${qId}">
                    <h3>Question ${index + 1}: ${isApiData ? q.questionText : q.question}</h3>
                    <div class="options">
            `;

            if (isApiData) {
                // API format: optionA, optionB, optionC, optionD
                const options = [
                    { label: 'A', text: q.optionA },
                    { label: 'B', text: q.optionB },
                    { label: 'C', text: q.optionC },
                    { label: 'D', text: q.optionD }
                ];
                options.forEach(opt => {
                    html += `
                        <label class="option">
                            <input type="radio" name="q${qId}" value="${opt.label}" required>
                            <span>${opt.text}</span>
                        </label>
                    `;
                });
            } else {
                // Local format: options array with index
                q.options.forEach((option, optIndex) => {
                    html += `
                        <label class="option">
                            <input type="radio" name="q${qId}" value="${optIndex}" required>
                            <span>${option}</span>
                        </label>
                    `;
                });
            }

            html += '</div></div>';
        });

        html += `
            <button type="submit" class="btn">Submit Quiz</button>
        </form>`;

        quizContainer.innerHTML = html;

        // Add submit event listener
        document.getElementById('quizForm').addEventListener('submit', handleQuizSubmit);

        // Add change event listeners for options
        document.querySelectorAll('input[type="radio"]').forEach(radio => {
            radio.addEventListener('change', handleOptionChange);
        });

    } catch (error) {
        console.error('Error rendering quiz:', error);
        quizContainer.innerHTML = '<p class="error">Failed to load quiz. Please refresh the page.</p>';
    }
}

// Handle quiz submission
async function handleQuizSubmit(event) {
    event.preventDefault();

    const form = event.target;
    const isApiMode = currentQuizId !== null && currentQuizQuestions.length > 0;

    if (isApiMode) {
        // API submission
        const answers = {};
        currentQuizQuestions.forEach(q => {
            const selected = form.querySelector(`input[name="q${q.questionId}"]:checked`);
            if (selected) {
                answers[q.questionId] = selected.value;
            }
        });

        // Validate all questions answered
        if (Object.keys(answers).length < currentQuizQuestions.length) {
            showError('Please answer all questions before submitting.');
            return;
        }

        try {
            const userId = StorageManager.getCurrentUserId();
            const result = await ApiClient.submitQuiz(currentQuizId, {
                userId: userId,
                answers: answers
            });

            // Also save locally for offline access
            StorageManager.saveQuizResult(
                result.score, result.totalQuestions,
                result.percentage, result.grade, result.passed
            );

            displayResults(result.score, result.totalQuestions,
                result.percentage, result.grade, result.passed);
        } catch (error) {
            console.error('API submission failed:', error);
            showError('Failed to submit quiz. Please try again.');
        }
    } else {
        // Local fallback submission
        const questions = quizData;

        const unanswered = [];
        questions.forEach(q => {
            const selected = form.querySelector(`input[name="q${q.id}"]:checked`);
            if (!selected) {
                unanswered.push(q.id);
            }
        });

        if (unanswered.length > 0) {
            showError(`Please answer all questions. Unanswered: ${unanswered.join(', ')}`);
            return;
        }

        let score = 0;
        questions.forEach(q => {
            const selected = form.querySelector(`input[name="q${q.id}"]:checked`);
            if (selected && parseInt(selected.value) === q.correct) {
                score++;
            }
        });

        const total = questions.length;
        const percentage = (score / total) * 100;
        const grade = calculateGrade(percentage);
        const passed = determinePassFail(percentage);

        StorageManager.saveQuizResult(score, total, percentage, grade, passed);
        displayResults(score, total, percentage, grade, passed);
    }
}

// Handle option change
function handleOptionChange(event) {
    const questionDiv = event.target.closest('.question');
    const options = questionDiv.querySelectorAll('.option');

    // Visual feedback for selected option
    options.forEach(opt => opt.classList.remove('selected'));
    event.target.closest('.option').classList.add('selected');
}

// Display quiz results
function displayResults(score, total, percentage, grade, passed) {
    const quizContainer = document.getElementById('quizContainer');
    const resultsContainer = document.getElementById('resultsContainer');

    if (resultsContainer) {
        let feedback;
        switch (grade) {
            case 'A':
                feedback = 'Excellent work! You\'re a JavaScript master!';
                break;
            case 'B':
                feedback = 'Good job! You have solid understanding.';
                break;
            case 'C':
                feedback = 'Fair effort. Keep practicing!';
                break;
            case 'D':
                feedback = 'You passed, but need more practice.';
                break;
            default:
                feedback = 'Don\'t give up! Review the material and try again.';
        }

        resultsContainer.innerHTML = `
            <div class="result-card">
                <h2>Quiz Results</h2>
                <div class="score">${score}/${total}</div>
                <div class="percentage">${typeof percentage === 'number' ? percentage.toFixed(1) : percentage}%</div>
                <div class="grade">Grade: ${grade}</div>
                <div class="${passed ? 'pass' : 'fail'}">
                    ${passed ? '✓ PASSED' : '✗ FAILED'}
                </div>
                <p class="feedback">${feedback}</p>
                <button class="btn" onclick="location.reload()">Try Again</button>
            </div>
        `;

        if (quizContainer) {
            quizContainer.style.display = 'none';
        }

        if (passed) {
            updateProgress();
        }
    }
}

// Helper functions
function showLoading() {
    const container = document.getElementById('quizContainer');
    if (container) {
        container.innerHTML = `
            <div class="loading">
                <div class="spinner"></div>
                <p>Loading quiz...</p>
            </div>
        `;
    }
}

function hideLoading() {
    // Loading removed when content is rendered
}

function showError(message) {
    const container = document.getElementById('quizContainer');
    if (container) {
        container.innerHTML = `<p class="error">${message}</p>`;
        container.style.display = 'block';
    }
}

// Update progress
function updateProgress() {
    const progress = StorageManager.getOverallProgress();
    const progressBar = document.getElementById('courseProgress');

    if (progressBar) {
        progressBar.value = progress.percentage / 100;
    }

    const dashboardStats = document.getElementById('dashboardStats');
    if (dashboardStats) {
        dashboardStats.innerHTML = `
            <p>Courses Completed: ${progress.completedCount}/${progress.totalCourses}</p>
            <p>Overall Progress: ${progress.percentage.toFixed(1)}%</p>
        `;
    }
}

// Initialize page based on current URL (only run in browser)
if (typeof document !== 'undefined') {
    document.addEventListener('DOMContentLoaded', () => {
        const path = window.location.pathname;
        const currentPage = path.split('/').pop() || 'dashboard.html';

        // ── Auth Guard ──────────────────────────────────────
        const userId = StorageManager.getCurrentUserId();
        const isAuthPage = currentPage === 'login.html' || currentPage === 'register.html';
        
        if (!userId && !isAuthPage && currentPage !== 'index.html') {
            window.location.href = 'login.html';
            return;
        }

        if (userId && isAuthPage) {
            window.location.href = 'dashboard.html';
            return;
        }

        // ── Dynamic Logout Link ──────────────────────────────
        if (userId) {
            const navUl = document.querySelector('nav ul');
            if (navUl && !document.getElementById('logoutLi')) {
                const logoutLi = document.createElement('li');
                logoutLi.id = 'logoutLi';
                logoutLi.innerHTML = '<a href="#" id="logoutBtn">Logout</a>';
                navUl.appendChild(logoutLi);
                
                document.getElementById('logoutBtn').addEventListener('click', (e) => {
                    e.preventDefault();
                    StorageManager.logout();
                });
            }
        }

        // ── Auth Page Handlers ──────────────────────────────
        if (currentPage === 'login.html') {
            const loginForm = document.getElementById('loginForm');
            if (loginForm) {
                loginForm.addEventListener('submit', handleLogin);
            }
        } else if (currentPage === 'register.html') {
            const registerForm = document.getElementById('registerForm');
            if (registerForm) {
                registerForm.addEventListener('submit', handleRegister);
            }
        }

        // Set current page in navigation
        document.querySelectorAll('nav a').forEach(link => {
            if (link.getAttribute('href') === currentPage) {
                link.setAttribute('aria-current', 'page');
            }
        });

        // Page-specific initialization
        if (path.includes('quiz.html')) {
            renderQuiz();
        } else if (path.includes('dashboard.html')) {
            initializeDashboard();
        } else if (path.includes('courses.html')) {
            initializeCourses();
        } else if (path.includes('profile.html')) {
            initializeProfile();
        }

        // Update progress on all pages
        updateProgress();
    });
}

// ── Login Handler ──────────────────────────────────────────
async function handleLogin(event) {
    event.preventDefault();
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const errorDiv = document.getElementById('loginError');

    try {
        const user = await ApiClient.loginUser({ email, password });
        StorageManager.setCurrentUserId(user.userId);
        StorageManager.saveUserProfile({
            name: user.fullName,
            email: user.email,
            joinDate: new Date(user.createdAt).toLocaleDateString(),
            avatar: '👤'
        });
        window.location.href = 'dashboard.html';
    } catch (error) {
        errorDiv.textContent = 'Invalid email or password';
        errorDiv.style.display = 'block';
    }
}

// ── Register Handler ───────────────────────────────────────
async function handleRegister(event) {
    event.preventDefault();
    const fullName = document.getElementById('fullName').value;
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const errorDiv = document.getElementById('registerError');

    try {
        await ApiClient.registerUser({ fullName, email, password });
        alert('Registration successful! Please login.');
        window.location.href = 'login.html';
    } catch (error) {
        errorDiv.textContent = error.message || 'Registration failed';
        errorDiv.style.display = 'block';
    }
}

// Dashboard initialization
async function initializeDashboard() {
    const dashboardContent = document.getElementById('dashboardContent');
    const userName = document.getElementById('userName');

    if (!dashboardContent) return;

    // Try to load user from API
    let userProfile = StorageManager.getUserProfile();
    try {
        const userId = StorageManager.getCurrentUserId();
        const apiUser = await ApiClient.getUserById(userId);
        if (apiUser) {
            userProfile = {
                name: apiUser.fullName,
                email: apiUser.email,
                joinDate: new Date(apiUser.createdAt).toLocaleString(undefined, { dateStyle: 'medium', timeStyle: 'short' }),
                avatar: '👤'
            };
        }
    } catch (e) {
        console.warn('API unavailable for user profile, using local data');
    }

    if (userName) {
        userName.textContent = userProfile.name.split(' ')[0];
    }

    const progress = StorageManager.getOverallProgress();

    // Try to load results from API
    let recentResults = StorageManager.getQuizResults().slice(-3);
    try {
        const userId = StorageManager.getCurrentUserId();
        const apiResults = await ApiClient.getResultsByUser(userId);
        if (apiResults && apiResults.length > 0) {
            recentResults = apiResults.slice(0, 3).map(r => ({
                date: r.attemptDate,
                score: r.score,
                total: r.totalQuestions,
                percentage: r.percentage,
                passed: r.passed
            }));
        }
    } catch (e) {
        console.warn('API unavailable for results, using local data');
    }

    let recentResultsHtml = '';
    recentResults.forEach(result => {
        recentResultsHtml += `
            <tr>
            <tr>
                <td>${new Date(result.date).toLocaleString(undefined, { dateStyle: 'short', timeStyle: 'short' })}</td>
                <td>${result.score}/${result.total}</td>
                <td>${typeof result.percentage === 'number' ? result.percentage.toFixed(1) : result.percentage}%</td>
                <td class="${result.passed ? 'pass' : 'fail'}">${result.passed ? 'Pass' : 'Fail'}</td>
            </tr>
        `;
    });

    dashboardContent.innerHTML = `
        <section class="dashboard-grid">
            <div class="course-card">
                <h3>Your Progress</h3>
                <progress id="courseProgress" value="${progress.percentage/100}" max="1"></progress>
                <div id="dashboardStats">
                    <p>Courses Completed: ${progress.completedCount}/${progress.totalCourses}</p>
                    <p>Overall Progress: ${progress.percentage.toFixed(1)}%</p>
                </div>
            </div>
            
            <div class="course-card">
                <h3>Quick Actions</h3>
                <ul class="lessons-list">
                    <li><a href="courses.html">Browse Courses</a></li>
                    <li><a href="quiz.html">Take a Quiz</a></li>
                    <li><a href="profile.html">View Profile</a></li>
                </ul>
            </div>
            
            <div class="course-card">
                <h3>Recent Quiz Results</h3>
                ${recentResults.length > 0 ? `
                    <table>
                        <thead>
                            <tr>
                                <th>Date</th>
                                <th>Score</th>
                                <th>Percentage</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${recentResultsHtml}
                        </tbody>
                    </table>
                ` : '<p>No quiz results yet. Take a quiz to see your progress!</p>'}
            </div>
        </section>
    `;
}

// Courses page initialization
async function initializeCourses() {
    const coursesContainer = document.getElementById('coursesContainer');
    if (!coursesContainer) return;

    // Try API first, fallback to local
    let courseList;
    let isApiData = false;
    try {
        courseList = await ApiClient.getCourses();
        isApiData = true;
        apiCoursesData = courseList;
    } catch (e) {
        console.warn('API unavailable, using local course data');
        courseList = courses;
    }

    const completedCourses = StorageManager.getCompletedCourses();

    let coursesHtml = '<div class="courses-flex">';

    courseList.forEach(course => {
        const courseId = isApiData ? course.courseId : course.id;
        const isCompleted = completedCourses.includes(courseId);
        const courseLevel = isApiData ? 'beginner' : course.level;
        const courseDuration = isApiData ? `${course.lessonCount * 2} hours` : course.duration;

        let lessonsHtml;
        if (isApiData && course.lessons) {
            lessonsHtml = course.lessons.map(l => `<li>${l.title}</li>`).join('');
        } else if (!isApiData && course.lessons) {
            lessonsHtml = course.lessons.map(lesson => `<li>${lesson}</li>`).join('');
        } else {
            lessonsHtml = '<li>No lessons available</li>';
        }

        coursesHtml += `
            <article class="course-card" data-level="${courseLevel}">
                <h3>${course.title}</h3>
                <p class="course-meta">
                    <span>Level: ${courseLevel}</span> | 
                    <span>Duration: ${courseDuration}</span>
                </p>
                <p>${course.description}</p>
                <h4>Lessons:</h4>
                <ol class="lessons-list">
                    ${lessonsHtml}
                </ol>
                ${isCompleted ? 
                    '<span class="completed-badge">✓ Completed</span>' : 
                    '<button class="btn mark-complete" data-course-id="' + courseId + '">Mark Complete</button>'
                }
            </article>
        `;
    });

    coursesHtml += '</div>';
    coursesContainer.innerHTML = coursesHtml;

    // Add event listeners for mark complete buttons
    document.querySelectorAll('.mark-complete').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const courseId = parseInt(e.target.dataset.courseId);
            StorageManager.markCourseCompleted(courseId);
            e.target.textContent = '✓ Completed';
            e.target.disabled = true;
            updateProgress();
        });
    });

    // Course table
    const courseTable = document.getElementById('courseTable');
    if (courseTable) {
        let tableHtml = `
            <table>
                <thead>
                    <tr>
                        <th>Course Title</th>
                        <th>Level</th>
                        <th>Duration</th>
                        <th>Lessons</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
        `;

        courseList.forEach(course => {
            const courseId = isApiData ? course.courseId : course.id;
            const isCompleted = completedCourses.includes(courseId);
            const courseLevel = isApiData ? 'beginner' : course.level;
            const lessonCount = isApiData ? course.lessonCount : course.lessons.length;
            const courseDuration = isApiData ? `${lessonCount * 2} hours` : course.duration;

            tableHtml += `
                <tr>
                    <td>${course.title}</td>
                    <td>${courseLevel}</td>
                    <td>${courseDuration}</td>
                    <td>${lessonCount} lessons</td>
                    <td>${isCompleted ? '✓ Completed' : 'In Progress'}</td>
                </tr>
            `;
        });

        tableHtml += '</tbody></table>';
        courseTable.innerHTML = tableHtml;
    }
}

// Profile page initialization
async function initializeProfile() {
    const profileContainer = document.getElementById('profileContainer');
    if (!profileContainer) return;

    // Try API first
    let userProfile = StorageManager.getUserProfile();
    try {
        const userId = StorageManager.getCurrentUserId();
        const apiUser = await ApiClient.getUserById(userId);
        if (apiUser) {
            userProfile = {
                name: apiUser.fullName,
                email: apiUser.email,
                joinDate: new Date(apiUser.createdAt).toLocaleString(undefined, { dateStyle: 'medium', timeStyle: 'short' }),
                avatar: '👤',
                userId: apiUser.userId
            };
            StorageManager.saveUserProfile(userProfile);
        }
    } catch (e) {
        console.warn('API unavailable for profile, using local data');
    }

    const completedCourses = StorageManager.getCompletedCourses();
    const quizResults = StorageManager.getQuizResults();

    // Try to load results from API
    let apiResults = [];
    try {
        const userId = StorageManager.getCurrentUserId();
        apiResults = await ApiClient.getResultsByUser(userId);
    } catch (e) {
        console.warn('API unavailable for results');
    }

    // Use API results if available, otherwise local
    const displayResults = apiResults.length > 0 ? apiResults : quizResults;
    const totalQuizzes = displayResults.length;
    const passedQuizzes = displayResults.filter(r => r.passed).length;
    const bestScore = displayResults.length > 0
        ? Math.max(...displayResults.map(r => r.percentage))
        : 0;

    // Get completed course details
    let completedCourseDetails = [];
    try {
        if (apiCoursesData.length > 0) {
            completedCourseDetails = apiCoursesData
                .filter(c => completedCourses.includes(c.courseId))
                .map(c => c.title);
        } else {
            completedCourseDetails = courses
                .filter(c => completedCourses.includes(c.id))
                .map(c => c.title);
        }
    } catch (e) {
        completedCourseDetails = courses
            .filter(c => completedCourses.includes(c.id))
            .map(c => c.title);
    }

    profileContainer.innerHTML = `
        <div class="dashboard-grid">
            <div class="course-card">
                <h3>Profile Information</h3>
                <div class="profile-avatar">${userProfile.avatar}</div>
                <p><strong>Name:</strong> <span id="profileName">${userProfile.name}</span></p>
                <p><strong>Email:</strong> <span id="profileEmail">${userProfile.email}</span></p>
                <p><strong>Member Since:</strong> ${userProfile.joinDate}</p>
                <button class="btn" id="editProfileBtn" onclick="toggleEditProfile()" style="margin-top: 1rem;">Edit Profile</button>
            </div>
            
            <div class="course-card">
                <h3>Learning Statistics</h3>
                <p><strong>Courses Completed:</strong> ${completedCourses.length}</p>
                <p><strong>Quizzes Taken:</strong> ${totalQuizzes}</p>
                <p><strong>Quizzes Passed:</strong> ${passedQuizzes}</p>
                <p><strong>Best Score:</strong> ${bestScore.toFixed(1)}%</p>
                <progress value="${passedQuizzes / (totalQuizzes || 1)}" max="1"></progress>
            </div>
            
            <div class="course-card">
                <h3>Completed Courses</h3>
                ${completedCourseDetails.length > 0 ? `
                    <ul class="lessons-list">
                        ${completedCourseDetails.map(title => `<li>${title}</li>`).join('')}
                    </ul>
                ` : '<p>No courses completed yet. Start learning!</p>'}
            </div>
        </div>
    `;
}

// Export for testing (Node environment)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { calculateGrade, calculatePercentage, determinePassFail };
}

// Profile editing functions
async function toggleEditProfile() {
    const profileName = document.getElementById('profileName');
    const profileEmail = document.getElementById('profileEmail');
    const editBtn = document.getElementById('editProfileBtn');

    if (profileName && profileEmail && editBtn) {
        const isEditing = profileName.contentEditable === 'true';

        if (isEditing) {
            // Save changes
            const userProfile = StorageManager.getUserProfile();
            userProfile.name = profileName.textContent;
            userProfile.email = profileEmail.textContent;
            StorageManager.saveUserProfile(userProfile);

            // Try to update via API
            try {
                const userId = StorageManager.getCurrentUserId();
                await ApiClient.updateUser(userId, {
                    fullName: profileName.textContent,
                    email: profileEmail.textContent
                });
            } catch (e) {
                console.warn('API update failed, saved locally only');
            }

            // Exit edit mode
            profileName.contentEditable = 'false';
            profileEmail.contentEditable = 'false';
            editBtn.textContent = 'Edit Profile';
            editBtn.classList.remove('btn-danger');

            alert('Profile updated successfully!');
        } else {
            // Enter edit mode
            profileName.contentEditable = 'true';
            profileEmail.contentEditable = 'true';
            profileName.focus();
            editBtn.textContent = 'Save Profile';
            editBtn.classList.add('btn-danger');
        }
    }
}