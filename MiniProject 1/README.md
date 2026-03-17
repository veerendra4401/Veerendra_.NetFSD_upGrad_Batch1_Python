# Multi-Page E-Learning Platform (Frontend)

A fully client-side multi-page web application for online learning with courses, quizzes, progress tracking, and learner profiles. Built with HTML5, CSS3, and vanilla JavaScript without requiring a backend server.

## 📋 Project Overview

This e-learning platform allows users to:
- Browse and explore available courses
- Attempt quizzes with instant feedback
- Track their learning progress
- Manage their learner profile
- View comprehensive learning statistics
- Persist all data using Web Storage (localStorage)

## 🎯 Core Features Implemented

### 1. **Application Pages (4 Pages)**
- **Dashboard** (`dashboard.html`) - Overview of available courses and learning progress
- **Courses** (`courses.html`) - Detailed course list with lessons and completion status
- **Quiz** (`quiz.html`) - Dynamic quiz with instant results and feedback
- **Profile** (`profile.html`) - Learner details, statistics, and completed courses

### 2. **HTML Structure**
✅ Semantic layout using `<header>`, `<nav>`, `<main>`, `<section>`, `<footer>`
✅ Course list displayed using HTML `<table>` elements
✅ Ordered lesson lists using `<ol>` for hierarchical content
✅ Breadcrumb navigation on all pages with `<ol>` lists
✅ Nested navigation structure with relative path linking
✅ `<nav>` menu present on all pages
✅ Proper ARIA labels for accessibility
✅ `<progress>` element for course completion visualization

### 3. **CSS Features**
✅ **CSS Grid Layout** - Dashboard with `grid-template-columns: repeat(auto-fit, minmax(300px, 1fr))`
✅ **Flexbox Layout** - Course cards with responsive flex containers
✅ **Advanced Selectors** - Attribute selectors, pseudo-classes (`:hover`, `:focus`), combinators
✅ **Responsive Design** - Media queries for tablets (768px) and mobile (480px)
✅ **Modern Styling** - Gradients, transitions, animations, and box-shadows
✅ **Accessibility** - Focus states, keyboard navigation support

**CSS Features Used:**
- CSS Grid: `.dashboard-grid` with auto-fit columns
- Flexbox: `.courses-flex` with wrap and gap
- Pseudo-classes: `:hover`, `:focus`, `:active`, `:nth-child()`, `:first-child`, `:last-child`
- Combinators: `>`, `+`, ` ` (space)
- Attribute selectors: `[data-level]`, `[aria-current="page"]`
- Gradients: Linear and radial gradients with CSS variables
- Media Queries: Two breakpoints (768px, 480px)

### 4. **JavaScript Features**

#### A. Arrays & Objects
```javascript
// Course data stored as JavaScript objects
const courses = [
    { id: 1, title: "JavaScript Fundamentals", ... },
    { id: 2, title: "Advanced JavaScript", ... }
];

// Quiz questions in array of objects
const quizData = [
    { id: 1, question: "...", options: [...], correct: 0 }
];
```

#### B. Control Flow
✅ **If-else** for grade calculation (calculateGrade function)
✅ **Switch statement** for performance feedback messages

```javascript
function calculateGrade(percentage) {
    if (percentage >= 90) return 'A';
    if (percentage >= 80) return 'B';
    // ... more conditions
}

switch (grade) {
    case 'A':
        feedback = 'Excellent work!';
        break;
    // ... more cases
}
```

#### C. DOM Manipulation
✅ Dynamically generate quiz questions
✅ Dynamically render answer options
✅ Display results section after submission
✅ Update progress bars in real-time
✅ Add/remove CSS classes for visual feedback

#### D. Asynchronous JavaScript
✅ **Promise-based loading** - Quiz data loading simulation
✅ **async/await syntax** - loadQuizData() function
✅ **setTimeout()** - Simulates 1.5-second network delay

```javascript
async function loadQuizData() {
    const data = await new Promise((resolve) => {
        setTimeout(() => {
            resolve(quizData);
        }, 1500);
    });
    return data;
}
```

#### E. Web Storage
✅ **localStorage** used for persistent data storage:
- Quiz results (scores, grades, dates)
- Completed courses
- User profile information
- Overall learning progress

```javascript
class StorageManager {
    static saveQuizResult(score, total, percentage, grade, passed) { ... }
    static getQuizResults() { ... }
    static markCourseCompleted(courseId) { ... }
    static getSaveUserProfile(profile) { ... }
}
```

#### F. Events
✅ **onclick events** - Quiz submission button
✅ **onchange events** - Option selection with visual feedback
✅ **event.preventDefault()** - Form validation
✅ **addEventListener()** - Dynamic event binding

#### G. Progress Element
✅ HTML5 `<progress>` element shows:
- Course completion percentage
- Quiz pass rate
- Overall learning progress

### 5. **Testing**

All test cases pass with Jest (11 tests):

✅ **Grade Calculation Logic**
- Returns 'A' for percentage >= 90
- Returns 'B' for percentage 80-89
- Returns 'C' for percentage 70-79
- Returns 'D' for percentage 60-69
- Returns 'F' for percentage < 60

✅ **Percentage Calculation Logic**
- Correctly calculates percentage (score/total * 100)
- Handles zero total without division errors
- Rounds to correct decimal places

✅ **Pass/Fail Determination Logic**
- Returns true for percentage >= 60
- Returns false for percentage < 60
- Handles edge cases (59.9, 60.0)

Run tests with:
```bash
npm test
```

## 🚀 Getting Started

### Prerequisites
- Modern web browser (Chrome, Firefox, Safari, Edge)
- Node.js 12+ (for running tests)
- npm (for installing dependencies)

### Installation

1. Install dependencies:
```bash
npm install
```

2. Open in browser:
```bash
# Open index.html directly in your browser
start index.html
# or use a local server
python -m http.server 8000
# Then visit http://localhost:8000
```

### Running Tests

```bash
npm test
```

## 📁 Project Structure

```
├── index.html                 # Entry point (redirects to dashboard)
├── dashboard.html            # Dashboard page
├── courses.html             # Courses page
├── quiz.html                # Quiz page
├── profile.html             # Profile page
├── style.css                # Main stylesheet
├── script.js                # Main application logic
├── courses.js               # Course data
├── quiz-data.js             # Quiz questions data
├── storage.js               # Web Storage management
├── package.json             # npm configuration
└── tests/
    └── quiz-logic.test.js   # Jest test cases
```

## 🎨 Design Features

### Color Palette
- Primary: (#2c3e50) with gradient
- Secondary: (#3f34db) with gradient
- Success: (#27ae60)
- Danger: (#e74c3c)
- Warning: (#f39c12)

### Responsive Breakpoints
- **Desktop**: > 768px
- **Tablet**: 480px - 768px
- **Mobile**: < 480px

### Accessibility Features
- Semantic HTML elements
- ARIA labels and roles
- Focus states for keyboard navigation
- Screen reader friendly text
- Proper color contrast ratios

## 🔧 Key Functions

### Application Logic (`script.js`)

```javascript
// Grading functions
calculateGrade(percentage)        // Returns letter grade
calculatePercentage(score, total) // Calculates percentage
determinePassFail(percentage)     // Returns pass/fail status

// Quiz functions
loadQuizData()                  // Async load quiz data
renderQuiz()                    // Dynamically render quiz questions
handleQuizSubmit(event)         // Handle form submission
displayResults(...)             // Show quiz results

// Dashboard functions
initializeDashboard()           // Initialize dashboard page
initializeCourses()             // Initialize courses page
initializeProfile()             // Initialize profile page

// Storage functions (storage.js)
StorageManager.saveQuizResult()
StorageManager.getQuizResults()
StorageManager.markCourseCompleted()
StorageManager.getUserProfile()
```

## 💾 Web Storage Structure

### Quiz Results
```json
{
  "score": 4,
  "total": 5,
  "percentage": 80,
  "grade": "B",
  "passed": true,
  "date": "2024-03-17T10:30:00.000Z"
}
```

### User Profile
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "joinDate": "2024-01-01",
  "avatar": "👤"
}
```

### Completed Courses
```json
[1, 3]  // Array of course IDs
```

## 🎓 Course Data

The platform includes 3 sample courses:

1. **JavaScript Fundamentals** (Beginner)
   - 6 lessons covering basics
   
2. **Advanced JavaScript** (Advanced)
   - 6 lessons covering advanced concepts
   
3. **React for Beginners** (Intermediate)
   - 6 lessons covering React

## 📊 Features Completion Checklist

### Functional Requirements
- [x] Multi-page navigation with relative paths
- [x] Semantic HTML5 structure
- [x] Breadcrumb navigation on all pages
- [x] Course list with HTML table
- [x] Lessons with ordered lists
- [x] Quiz with dynamic questions
- [x] Progress tracking
- [x] Profile management

### CSS Requirements
- [x] CSS Grid layout for dashboard
- [x] Flexbox layout for course cards
- [x] Advanced selectors (attribute, pseudo-classes, combinators)
- [x] Responsive design with media queries
- [x] Mobile-friendly layout

### JavaScript Requirements
- [x] Arrays and objects for data storage
- [x] If-else for grade calculation
- [x] Switch statement for feedback
- [x] DOM manipulation for dynamic rendering
- [x] Promise and async/await
- [x] setTimeout() for async simulation
- [x] Web Storage (localStorage)
- [x] Event handling (onclick, onchange)
- [x] Progress element

### Testing Requirements
- [x] Jest test suite with 11 test cases
- [x] Grade calculation tests
- [x] Percentage calculation tests
- [x] Pass/fail determination tests
- [x] All tests passing

## 🐛 Browser Support

- Chrome 60+
- Firefox 55+
- Safari 12+
- Edge 79+

## 📝 Notes

- All data persists in browser's localStorage
- No backend server required
- Responsive design works on all screen sizes
- Accessibility features for keyboard navigation
- Performance optimized with CSS animations and transitions

## 👨‍💻 Code Quality

- Clean, organized code with meaningful variable names
- Comprehensive comments and documentation
- Semantic HTML for better accessibility
- CSS organized with logical grouping
- Modular JavaScript functions
- Error handling and validation

## 🎯 Future Enhancements

- Add more quiz questions with difficulty levels
- Implement course ratings and reviews
- Add social features for peer learning
- Export progress reports
- Add dark mode toggle
- Implement course search and filtering
- Add certificates of completion

## 📄 License

This project is part of the UpGrad Mini Project 1 training program.

---

**Last Updated**: March 17, 2024
**Version**: 1.0.0