import { useState, useCallback } from 'react';
import { PASSING_SCORE, QUESTION_TRANSITION_DELAY } from '../constants/examConstants';

export const useExamState = (questions) => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [answers, setAnswers] = useState(Array(questions.length).fill(null));
  const [flagged, setFlagged] = useState(Array(questions.length).fill(false));
  const [examStarted, setExamStarted] = useState(false);
  const [finished, setFinished] = useState(false);
  const [score, setScore] = useState(0);
  const [showConfetti, setShowConfetti] = useState(false);
  const [isTransitioning, setIsTransitioning] = useState(false);

  const resetExamState = useCallback((newQuestions = null) => {
    const questionsArray = newQuestions || questions;
    setCurrentIndex(0);
    setAnswers(Array(questionsArray.length).fill(null));
    setFlagged(Array(questionsArray.length).fill(false));
    setExamStarted(false);
    setFinished(false);
    setScore(0);
    setShowConfetti(false);
    setIsTransitioning(false);
  }, [questions]);

  const handleSelect = useCallback((option) => {
    const newAnswers = [...answers];
    newAnswers[currentIndex] = option;
    setAnswers(newAnswers);
  }, [answers, currentIndex]);

  const navigateToQuestion = useCallback((index) => {
    if (index >= 0 && index < questions.length) {
      setIsTransitioning(true);
      setTimeout(() => {
        setCurrentIndex(index);
        setIsTransitioning(false);
      }, QUESTION_TRANSITION_DELAY);
    }
  }, [questions.length]);

  const handleNext = useCallback(() => {
    navigateToQuestion(currentIndex + 1);
  }, [currentIndex, navigateToQuestion]);

  const handlePrev = useCallback(() => {
    navigateToQuestion(currentIndex - 1);
  }, [currentIndex, navigateToQuestion]);

  const toggleFlag = useCallback(() => {
    const newFlagged = [...flagged];
    newFlagged[currentIndex] = !newFlagged[currentIndex];
    setFlagged(newFlagged);
  }, [flagged, currentIndex]);

  const calculateScore = useCallback(() => {
    const correctAnswers = answers.filter((answer, index) => 
      answer === questions[index].answer
    ).length;
    return Math.round((correctAnswers / questions.length) * 100);
  }, [answers, questions]);

  const finishExam = useCallback(() => {
    const scorePercent = calculateScore();
    setScore(scorePercent);
    setFinished(true);
    
    if (scorePercent >= PASSING_SCORE) {
      setShowConfetti(true);
    }
  }, [calculateScore]);

  const answeredCount = answers.filter(a => a !== null).length;
  const correctCount = answers.filter((answer, index) => answer === questions[index].answer).length;
  const incorrectCount = questions.length - correctCount;
  const isPassed = score >= PASSING_SCORE;

  return {
    // State
    currentIndex,
    answers,
    flagged,
    examStarted,
    finished,
    score,
    showConfetti,
    isTransitioning,
    
    // Computed values
    answeredCount,
    correctCount,
    incorrectCount,
    isPassed,
    
    // Actions
    setCurrentIndex,
    setExamStarted,
    setFinished,
    setShowConfetti,
    resetExamState,
    handleSelect,
    handleNext,
    handlePrev,
    toggleFlag,
    finishExam,
    navigateToQuestion
  };
}; 