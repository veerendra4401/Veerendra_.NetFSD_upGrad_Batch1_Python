const { calculateGrade, calculatePercentage, determinePassFail } = require('../script.js');

// Test grade calculation
describe('Grade Calculation Logic', () => {
    test('should return A for percentage >= 90', () => {
        expect(calculateGrade(95)).toBe('A');
        expect(calculateGrade(90)).toBe('A');
    });

    test('should return B for percentage between 80 and 89', () => {
        expect(calculateGrade(85)).toBe('B');
        expect(calculateGrade(80)).toBe('B');
    });

    test('should return C for percentage between 70 and 79', () => {
        expect(calculateGrade(75)).toBe('C');
        expect(calculateGrade(70)).toBe('C');
    });

    test('should return D for percentage between 60 and 69', () => {
        expect(calculateGrade(65)).toBe('D');
        expect(calculateGrade(60)).toBe('D');
    });

    test('should return F for percentage < 60', () => {
        expect(calculateGrade(59)).toBe('F');
        expect(calculateGrade(0)).toBe('F');
    });
});

// Test percentage calculation
describe('Percentage Calculation Logic', () => {
    test('should calculate correct percentage', () => {
        expect(calculatePercentage(5, 10)).toBe(50);
        expect(calculatePercentage(10, 10)).toBe(100);
        expect(calculatePercentage(0, 10)).toBe(0);
    });

    test('should handle zero total', () => {
        expect(calculatePercentage(0, 0)).toBe(0);
    });

    test('should round to nearest decimal', () => {
        expect(calculatePercentage(3, 7)).toBeCloseTo(42.86, 2);
    });
});

// Test pass/fail determination
describe('Pass/Fail Determination Logic', () => {
    test('should return true for percentage >= 60', () => {
        expect(determinePassFail(60)).toBe(true);
        expect(determinePassFail(75)).toBe(true);
        expect(determinePassFail(100)).toBe(true);
    });

    test('should return false for percentage < 60', () => {
        expect(determinePassFail(59)).toBe(false);
        expect(determinePassFail(0)).toBe(false);
        expect(determinePassFail(30)).toBe(false);
    });

    test('should handle edge cases', () => {
        expect(determinePassFail(59.9)).toBe(false);
        expect(determinePassFail(60.0)).toBe(true);
    });
});

