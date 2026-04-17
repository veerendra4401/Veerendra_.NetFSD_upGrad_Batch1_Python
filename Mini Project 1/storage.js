class StorageManager {
    // Store quiz results
    static saveQuizResult(score, total, percentage, grade, passed) {
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
        localStorage.setItem('quizResults', JSON.stringify(results));
        
        return quizResult;
    }
    
    // Get all quiz results
    static getQuizResults() {
        const results = localStorage.getItem('quizResults');
        return results ? JSON.parse(results) : [];
    }
    
    // Store completed course
    static markCourseCompleted(courseId) {
        const completed = this.getCompletedCourses();
        if (!completed.includes(courseId)) {
            completed.push(courseId);
            localStorage.setItem('completedCourses', JSON.stringify(completed));
        }
    }
    
    // Get completed courses
    static getCompletedCourses() {
        const completed = localStorage.getItem('completedCourses');
        return completed ? JSON.parse(completed) : [];
    }
    
    // Store user profile
    static saveUserProfile(profile) {
        localStorage.setItem('userProfile', JSON.stringify(profile));
    }
    
    // Get user profile
    static getUserProfile() {
        const profile = localStorage.getItem('userProfile');
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
        return {
            completedCount: completed.length,
            totalCourses: courses.length,
            percentage: (completed.length / courses.length) * 100
        };
    }
}