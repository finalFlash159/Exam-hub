import { useState, useEffect, useCallback } from 'react';
import { EXAM_TIME_SECONDS, getExamTimeSeconds, LOW_TIME_THRESHOLD, VERY_LOW_TIME_THRESHOLD } from '../constants/examConstants';

export const useExamTimer = (onTimeUp, questionCount = null) => {
  const getInitialTime = () => {
    if (questionCount) {
      return getExamTimeSeconds(questionCount);
    }
    return EXAM_TIME_SECONDS;
  };
  
  const [timeLeft, setTimeLeft] = useState(getInitialTime());

  const resetTimer = useCallback(() => {
    const initialTime = questionCount ? getExamTimeSeconds(questionCount) : EXAM_TIME_SECONDS;
    setTimeLeft(initialTime);
  }, [questionCount]);

  useEffect(() => {
    if (timeLeft <= 0) {
      onTimeUp();
      return;
    }
    
    const timer = setInterval(() => {
      setTimeLeft((t) => t - 1);
    }, 1000);
    
    return () => clearInterval(timer);
  }, [timeLeft, onTimeUp]);

  const minutes = Math.floor(timeLeft / 60);
  const seconds = timeLeft % 60;

  return {
    timeLeft,
    minutes,
    seconds,
    resetTimer,
    isLowTime: timeLeft < LOW_TIME_THRESHOLD,
    isVeryLowTime: timeLeft < VERY_LOW_TIME_THRESHOLD
  };
}; 