# Financial Literacy for Youth

A gamified web platform designed to teach young adults personal finance through interactive simulations, quizzes, AI mentorship, and budgeting tools.

## Features Built

- **Interactive Financial Quizzes**: Test knowledge on compound interest, emergency funds, and investing. Awards XP for correct answers.
- **Spending Tracker**: A digital ledger to log expenses. Features Chart.js data visualizations (Pie chart breakdown and Month-to-Month bar charts).
- **Gamification Engine**: A comprehensive LocalStorage-backed XP and Leveling system. Level up based on platform engagement, complete with animated UI celebrations and coin rewards.
- **Financial Simulations**: 
  - **First Salary**: Interactive sliders to practice the 50/30/20 budgeting rule.
  - **Investment Simulator**: A Chart.js projection visualizing the differences between Fixed Deposits, Mutual Funds, and Stocks over 10 years.
- **AI Finance Mentor**: A sleek chat interface simulating an AI assistant that offers tailored advice on tracking expenses, investing for beginners, and saving logic.
- **Leaderboard**: A dynamic ranking system comparing the user's XP against simulated peers, showcasing tier-based UI highlights. 
- **Premium UI Dashboard**: Built with a sleek, dark mode glassmorphism aesthetic mimicking modern fintech startups.

## Tech Stack

- **Frontend Core**: HTML5, CSS3, ES6 JavaScript (No frameworks required)
- **Styling**: TailwindCSS (via CDN), Custom CSS (Animations, Variables, Glassmorphism)
- **Icons**: FontAwesome 6
- **Data Visualization**: Chart.js
- **Animations**: AOS (Animate On Scroll)
- **Data Storage**: Client-side `LocalStorage` (Simulating a Persistent Backend)

## Project Structure

```text
/financial-literacy-platform
├── index.html           # Landing Page
├── login.html           # Authentication Page (Mock Google Login)
├── dashboard.html       # Main User Dashboard
├── quiz.html            # MCQ Interactive Module
├── simulation.html      # Salary Budgeting & Investing Math
├── spending-tracker.html# Expense Logging & Visualization
├── leaderboard.html     # XP Sorting & Ranking
├── ai-mentor.html       # Chatbot Interface
├── /css
│   └── styles.css       # Platform Styling overrides & themes
├── /js
│   ├── auth.js          # Handles Sessions & Login Streaks
│   ├── gamification.js  # Global XP API & Level Up Overlay System
│   ├── dashboard.js     # Hydrates dashboard counters & widgets
│   ├── quiz.js          # Manages questioning & scoring
│   ├── simulation.js    # Logic for compounding interest & salary validation
│   ├── expenses.js      # CRUD ops & Chart rendering
│   ├── leaderboard.js   # Interleaves Mock data with active user data
│   └── ai-mentor.js     # Conversational static mapping handler
└── /assets              # Ready for media deposits
```

## How to Run Locally

Since this project utilizes native web technologies and avoids build steps (like Webpack or Vite), you can run it entirely without NodeJS or heavy toolchains. 

1. **Clone the repository** (or copy the generated folder)
2. **Launch a local server**. If you use VS Code, install the `Live Server` extension and click "Go Live" from the `index.html` file.
    - Alternatively, using Python: `python -m http.server 8000`
3. Navigate to `http://localhost:8000` or the port provided.
4. From the landing page, click **Login with Google** to drop a mock session token into your LocalStorage and access the Dashboard.

## Notes on Architecture

- **State Management**: `js/gamification.js` acts as a global singleton bridging different modules. Whenever a user completes a quiz (`quiz.js`) or tracks their first expense (`expenses.js`), they call `window.finlitGamification.addXP()`, which natively syncs the updated numbers securely into LocalStorage.
- **Extensibility**: The AI Mentor explicitly utilizes `generateMockResponse()`. If deploying to production, this function simply needs to be replaced with a `fetch()` request posting to a Gemini API or OpenAI proxy.
