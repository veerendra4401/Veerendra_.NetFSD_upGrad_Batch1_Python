const { calculateGrade, calculatePercentage, determinePassFail } = require('./Backend/ELearningAPI/wwwroot/script.js');

describe('E-Learning Logic Tests', () => {
    
    // 1. Grade calculation logic
    test('calculateGrade should return correct grades for different percentages', () => {
        expect(calculateGrade(95)).toBe('A');
        expect(calculateGrade(85)).toBe('B');
        expect(calculateGrade(75)).toBe('C');
        expect(calculateGrade(65)).toBe('D');
        expect(calculateGrade(55)).toBe('F');
    });

    // 2. Score percentage calculation
    test('calculatePercentage should return correct percentage', () => {
        expect(calculatePercentage(8, 10)).toBe(80);
        expect(calculatePercentage(5, 10)).toBe(50);
        expect(calculatePercentage(0, 10)).toBe(0);
        expect(calculatePercentage(10, 10)).toBe(100);
        expect(calculatePercentage(5, 0)).toBe(0); // Testing edge case from code
    });

    // 3. Pass/Fail determination logic
    test('determinePassFail should return true if score >= 60%', () => {
        expect(determinePassFail(60)).toBe(true);
        expect(determinePassFail(75)).toBe(true);
        expect(determinePassFail(59)).toBe(false);
        expect(determinePassFail(0)).toBe(false);
    });
});
