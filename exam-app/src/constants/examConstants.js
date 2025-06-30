// Exam timing constants
export const EXAM_TIME_MINUTES = 120;
export const EXAM_TIME_SECONDS = EXAM_TIME_MINUTES * 60;

// Dynamic exam timing based on number of questions
export const getExamDuration = (questionCount) => {
  if (questionCount <= 35) {
    return 60; // 60 minutes for ≤35 questions
  } else if (questionCount <= 50) {
    return 90; // 90 minutes for 35-50 questions
  } else {
    return 120; // 120 minutes for >50 questions
  }
};

export const getExamTimeSeconds = (questionCount) => {
  return getExamDuration(questionCount) * 60;
};

// Scoring constants
export const PASSING_SCORE = 70;

// UI constants
export const QUESTION_TRANSITION_DELAY = 150;
export const CONFETTI_DURATION = 3000;

// Navigation constants
export const QUESTIONS_PER_ROW = 14;
export const MAX_ROWS = 5;

// Timer warning thresholds
export const LOW_TIME_THRESHOLD = 300; // 5 minutes
export const VERY_LOW_TIME_THRESHOLD = 600; // 10 minutes 