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

// Async function to simulate loading quiz data
async function loadQuizData() {
    try {
        showLoading();
        
        // Simulate async loading with Promise and setTimeout
        const data = await new Promise((resolve) => {
            setTimeout(() => {
                resolve(quizData);
            }, 1500); // 1.5 second delay to simulate network request
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
        
        if (questions.length === 0) {
            quizContainer.innerHTML = '<p class="error">No questions available</p>';
            return;
        }
        
        let html = '<form id="quizForm">';
        
        questions.forEach((q, index) => {
            html += `
                <div class="question" data-question-id="${q.id}">
                    <h3>Question ${index + 1}: ${q.question}</h3>
                    <div class="options">
            `;
            
            q.options.forEach((option, optIndex) => {
                html += `
                    <label class="option">
                        <input type="radio" name="q${q.id}" value="${optIndex}" required>
                        <span>${option}</span>
                    </label>
                `;
            });
            
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
function handleQuizSubmit(event) {
    event.preventDefault();
    
    const form = event.target;
    const questions = quizData; // Using imported quizData
    
    // Validate all questions are answered
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
    
    // Calculate score
    questions.forEach(q => {
        const selected = form.querySelector(`input[name="q${q.id}"]:checked`);
        if (selected && parseInt(selected.value) === q.correct) {
            score++;
        }
    });
    
    // Calculate percentage
    const total = questions.length;
    const percentage = (score / total) * 100;
    
    // Calculate grade using helper
    const grade = calculateGrade(percentage);
    
    // Determine pass/fail using helper
    const passed = determinePassFail(percentage);
    
    // Save results
    StorageManager.saveQuizResult(score, total, percentage, grade, passed);
    
    // Display results
    displayResults(score, total, percentage, grade, passed);
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
        // Performance feedback using switch
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
                <div class="percentage">${percentage.toFixed(1)}%</div>
                <div class="grade">Grade: ${grade}</div>
                <div class="${passed ? 'pass' : 'fail'}">
                    ${passed ? '✓ PASSED' : '✗ FAILED'}
                </div>
                <p class="feedback">${feedback}</p>
                <button class="btn" onclick="location.reload()">Try Again</button>
            </div>
        `;
        
        // Hide quiz form
        if (quizContainer) {
            quizContainer.style.display = 'none';
        }
        
        // Update progress if passed
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
        // Keep the container visible so user can see the error
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
    
    // Update dashboard if on dashboard page
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
        
        // Set current page in navigation
        const currentPage = path.split('/').pop() || 'dashboard.html';
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

// Dashboard initialization
function initializeDashboard() {
    const dashboardContent = document.getElementById('dashboardContent');
    const userName = document.getElementById('userName');
    
    if (!dashboardContent) return;
    
    // Set user name
    const userProfile = StorageManager.getUserProfile();
    if (userName) {
        userName.textContent = userProfile.name.split(' ')[0]; // Show first name
    }
    
    const progress = StorageManager.getOverallProgress();
    const recentResults = StorageManager.getQuizResults().slice(-3);
    
    let recentResultsHtml = '';
    recentResults.forEach(result => {
        recentResultsHtml += `
            <tr>
                <td>${new Date(result.date).toLocaleDateString()}</td>
                <td>${result.score}/${result.total}</td>
                <td>${result.percentage.toFixed(1)}%</td>
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
function initializeCourses() {
    const coursesContainer = document.getElementById('coursesContainer');
    if (!coursesContainer) return;
    
    const completedCourses = StorageManager.getCompletedCourses();
    
    let coursesHtml = '<div class="courses-flex">';
    
    courses.forEach(course => {
        const isCompleted = completedCourses.includes(course.id);
        const lessonsHtml = course.lessons.map(lesson => `<li>${lesson}</li>`).join('');
        
        coursesHtml += `
            <article class="course-card" data-level="${course.level}">
                <h3>${course.title}</h3>
                <p class="course-meta">
                    <span>Level: ${course.level}</span> | 
                    <span>Duration: ${course.duration}</span>
                </p>
                <p>${course.description}</p>
                <h4>Lessons:</h4>
                <ol class="lessons-list">
                    ${lessonsHtml}
                </ol>
                ${isCompleted ? 
                    '<span class="completed-badge">✓ Completed</span>' : 
                    '<button class="btn mark-complete" data-course-id="' + course.id + '">Mark Complete</button>'
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
        
        courses.forEach(course => {
            const isCompleted = completedCourses.includes(course.id);
            tableHtml += `
                <tr>
                    <td>${course.title}</td>
                    <td>${course.level}</td>
                    <td>${course.duration}</td>
                    <td>${course.lessons.length} lessons</td>
                    <td>${isCompleted ? '✓ Completed' : 'In Progress'}</td>
                </tr>
            `;
        });
        
        tableHtml += '</tbody></table>';
        courseTable.innerHTML = tableHtml;
    }
}

// Profile page initialization
function initializeProfile() {
    const profileContainer = document.getElementById('profileContainer');
    if (!profileContainer) return;
    
    const userProfile = StorageManager.getUserProfile();
    const completedCourses = StorageManager.getCompletedCourses();
    const quizResults = StorageManager.getQuizResults();
    
    // Calculate stats
    const totalQuizzes = quizResults.length;
    const passedQuizzes = quizResults.filter(r => r.passed).length;
    const bestScore = quizResults.length > 0 
        ? Math.max(...quizResults.map(r => r.percentage)) 
        : 0;
    
    // Get completed course details
    const completedCourseDetails = courses
        .filter(c => completedCourses.includes(c.id))
        .map(c => c.title);
    
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
function toggleEditProfile() {
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
            
            // Exit edit mode
            profileName.contentEditable = 'false';
            profileEmail.contentEditable = 'false';
            editBtn.textContent = 'Edit Profile';
            editBtn.classList.remove('btn-danger');
            
            // Show confirmation
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