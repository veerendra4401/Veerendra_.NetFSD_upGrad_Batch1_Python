// ── API Configuration ──────────────────────────────────────
const API_BASE_URL = 'http://localhost:5208/api';

// ── API Client ─────────────────────────────────────────────
class ApiClient {
    static async request(endpoint, options = {}) {
        try {
            const response = await fetch(`${API_BASE_URL}${endpoint}`, {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...options
            });

            if (!response.ok) {
                const error = await response.json().catch(() => ({ message: response.statusText }));
                throw new Error(error.message || `HTTP ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.warn(`API request failed: ${endpoint}`, error.message);
            throw error;
        }
    }

    // ── Course APIs ────────────────────────────────────────
    static async getCourses() {
        return await this.request('/courses');
    }

    static async getCourseById(id) {
        return await this.request(`/courses/${id}`);
    }

    static async createCourse(data) {
        return await this.request('/courses', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    static async updateCourse(id, data) {
        return await this.request(`/courses/${id}`, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }

    static async deleteCourse(id) {
        return await this.request(`/courses/${id}`, {
            method: 'DELETE'
        });
    }

    // ── Lesson APIs ────────────────────────────────────────
    static async getLessonsByCourse(courseId) {
        return await this.request(`/courses/${courseId}/lessons`);
    }

    static async createLesson(data) {
        return await this.request('/lessons', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    static async updateLesson(id, data) {
        return await this.request(`/lessons/${id}`, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }

    static async deleteLesson(id) {
        return await this.request(`/lessons/${id}`, {
            method: 'DELETE'
        });
    }

    // ── Quiz APIs ──────────────────────────────────────────
    static async getQuizzesByCourse(courseId) {
        return await this.request(`/quizzes/${courseId}`);
    }

    static async getQuizQuestions(quizId) {
        return await this.request(`/quizzes/${quizId}/questions`);
    }

    static async submitQuiz(quizId, data) {
        return await this.request(`/quizzes/${quizId}/submit`, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    // ── User APIs ──────────────────────────────────────────
    static async registerUser(data) {
        return await this.request('/users/register', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    static async loginUser(data) {
        return await this.request('/users/login', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    static async getUserById(id) {
        return await this.request(`/users/${id}`);
    }

    static async updateUser(id, data) {
        return await this.request(`/users/${id}`, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }

    // ── Result APIs ────────────────────────────────────────
    static async getResultsByUser(userId) {
        return await this.request(`/results/${userId}`);
    }
}

// ── StorageManager (API-backed with localStorage fallback) ──
class StorageManager {
    // Current user ID (stored in localStorage)
    static getCurrentUserId() {
        return parseInt(localStorage.getItem('currentUserId')) || null;
    }

    static setCurrentUserId(id) {
        if (id) {
            localStorage.setItem('currentUserId', id.toString());
        } else {
            localStorage.removeItem('currentUserId');
        }
    }

    static logout() {
        const userId = this.getCurrentUserId();
        if (userId) {
            localStorage.removeItem(`userProfile_${userId}`);
        }
        localStorage.removeItem('currentUserId');
        window.location.href = 'login.html';
    }

    // Store quiz results locally (fallback + cache)
    static saveQuizResult(score, total, percentage, grade, passed) {
        const userId = this.getCurrentUserId();
        if (!userId) return null;

        const quizResult = {
            score,
            total,
            percentage,
            grade,
            passed,
            date: new Date().toISOString()
        };

        const results = this.getQuizResults();
        results.push(quizResult);
        localStorage.setItem(`quizResults_${userId}`, JSON.stringify(results));

        return quizResult;
    }

    // Get all quiz results from localStorage (cache)
    static getQuizResults() {
        const userId = this.getCurrentUserId();
        if (!userId) return [];

        const results = localStorage.getItem(`quizResults_${userId}`);
        return results ? JSON.parse(results) : [];
    }

    // Store completed course
    static markCourseCompleted(courseId) {
        const userId = this.getCurrentUserId();
        if (!userId) return;

        const completed = this.getCompletedCourses();
        if (!completed.includes(courseId)) {
            completed.push(courseId);
            localStorage.setItem(`completedCourses_${userId}`, JSON.stringify(completed));
        }
    }

    // Get completed courses
    static getCompletedCourses() {
        const userId = this.getCurrentUserId();
        if (!userId) return [];

        const completed = localStorage.getItem(`completedCourses_${userId}`);
        return completed ? JSON.parse(completed) : [];
    }

    // Store user profile
    static saveUserProfile(profile) {
        const userId = this.getCurrentUserId();
        if (userId) {
            localStorage.setItem(`userProfile_${userId}`, JSON.stringify(profile));
        }
    }

    // Get user profile (try API first, fallback to localStorage)
    static getUserProfile() {
        const userId = this.getCurrentUserId();
        if (!userId) return {
            name: 'Guest',
            email: 'guest@example.com',
            joinDate: new Date().toLocaleDateString(),
            avatar: '👤'
        };

        const profile = localStorage.getItem(`userProfile_${userId}`);
        return profile ? JSON.parse(profile) : {
            name: 'John Doe',
            email: 'john@example.com',
            joinDate: '2024-01-01',
            avatar: '👤'
        };
    }

    // Clear all storage
    static clearAll() {
        localStorage.clear();
    }

    // Get overall progress
    static getOverallProgress() {
        const completed = this.getCompletedCourses();
        const totalCourses = typeof courses !== 'undefined' ? courses.length : 3;
        return {
            completedCount: completed.length,
            totalCourses: totalCourses,
            percentage: (completed.length / totalCourses) * 100
        };
    }
}