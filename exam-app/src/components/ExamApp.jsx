import React, { useState, useEffect } from 'react';
import { 
  Box, Button, Container, Typography, Paper, Grid, 
  Card, Divider, CircularProgress,
  Select, MenuItem, FormControl, InputLabel
} from '@mui/material';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import CancelIcon from '@mui/icons-material/Cancel';
import NavigateNextIcon from '@mui/icons-material/NavigateNext';
import NavigateBeforeIcon from '@mui/icons-material/NavigateBefore';
import { motion, AnimatePresence } from 'framer-motion';

// Import from centralized data management
import { getExamTypes, getQuestions } from '../data';
import { useExamTimer } from '../hooks/useExamTimer';
import { useExamState } from '../hooks/useExamState';

// Import components
import MathRenderer from './MathRenderer';
import LoadingSpinner from './LoadingSpinner';
import ConfettiCelebration from './ConfettiCelebration';
import ExamHeader from './ExamHeader';
import QuestionCard from './QuestionCard';
import QuestionNavigator from './QuestionNavigator';
import { PASSING_SCORE } from '../constants/examConstants';

export default function ExamApp() {
  const [examType, setExamType] = useState('default');
  const [questions, setQuestions] = useState(getQuestions('default'));
  const [loading, setLoading] = useState(false);
  const [examTypes, setExamTypes] = useState(getExamTypes());
  const [reviewIncorrectOnly, setReviewIncorrectOnly] = useState(false);

  // Custom hooks for exam state and timer
  const examState = useExamState(questions);
  const timer = useExamTimer(examState.finishExam, questions.length);
  

  
  // Load different question sets based on selection
  const handleExamTypeChange = (event) => {
    const selectedExam = event.target.value;
    setExamType(selectedExam);
    setLoading(true);
    
    try {
      const newQuestions = getQuestions(selectedExam);
      setQuestions(newQuestions);
      examState.resetExamState(newQuestions);
    } catch (error) {
      console.error("Error loading questions:", error);
      alert("Failed to load exam questions. Please try again.");
    } finally {
      setLoading(false);
    }
  };
  
  const startExam = () => {
    examState.setExamStarted(true);
    timer.resetTimer();
  };

  const confirmFinish = () => {
    if (window.confirm('Are you sure you want to end the exam and see your results?')) {
      examState.finishExam();
    }
  };

  // Thêm useEffect để tải lại danh sách bài kiểm tra mỗi khi component được render
  useEffect(() => {
    const refreshExamTypes = () => {
      try {
        const updated = getExamTypes();
        setExamTypes(updated);
      } catch (error) {
        console.error("Lỗi khi làm mới danh sách bài kiểm tra:", error);
      }
    };
    
    refreshExamTypes();
  }, []);

  if (examState.finished) {
    const { score, correctCount, incorrectCount, isPassed } = examState;
    
    return (
      <>
        <ConfettiCelebration 
          show={examState.showConfetti} 
          onComplete={() => examState.setShowConfetti(false)}
          score={score}
          isPassed={isPassed}
        />
        
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <Container maxWidth="md" sx={{ mt: 4, mb: 8 }}>
            <Card sx={{ 
              mb: 4, 
              p: 3, 
              textAlign: 'center', 
              bgcolor: isPassed 
                ? (theme) => theme.palette.mode === 'dark' ? '#1b5e20' : '#e8f5e9'
                : (theme) => theme.palette.mode === 'dark' ? '#b71c1c' : '#ffebee',
              color: (theme) => theme.palette.text.primary
            }}>
          <Typography 
            variant="h4" 
            gutterBottom 
            fontWeight="bold"
            sx={{
              color: (theme) => theme.palette.mode === 'dark' ? '#ffffff' : theme.palette.primary.main
            }}
          >
            Exam Results
          </Typography>
          
          <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', mb: 2 }}>
            <CircularProgress 
              variant="determinate" 
              value={score} 
              size={120} 
              thickness={5} 
              sx={{ color: isPassed ? 'success.main' : 'error.main' }}
            />
            <Box
              sx={{
                position: 'absolute',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <Typography variant="h4" fontWeight="bold">
                {score}%
              </Typography>
            </Box>
          </Box>
          
          <Typography variant="h5" sx={{ mt: 2, mb: 1 }}>
            {isPassed ? 'Congratulations! You passed!' : 'Try again. You did not pass.'}
          </Typography>
          
          <Typography variant="body1">
            You answered {correctCount} out of {questions.length} questions correctly.
          </Typography>
          
          <Typography variant="body2" sx={{ mt: 1 }}>
            Passing score: {PASSING_SCORE}%
          </Typography>
        </Card>

        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mt: 4, mb: 3 }}>
          <Typography variant="h5">
            Review Your Answers
          </Typography>
          <Box sx={{ display: 'flex', gap: 2 }}>
            <Button 
              variant={!reviewIncorrectOnly ? "contained" : "outlined"}
              onClick={() => setReviewIncorrectOnly(false)}
              size="medium"
            >
              All Questions
            </Button>
            <Button 
              variant={reviewIncorrectOnly ? "contained" : "outlined"}
              color="error"
              onClick={() => setReviewIncorrectOnly(true)}
              size="medium"
            >
              Incorrect Only ({incorrectCount})
            </Button>
          </Box>
        </Box>
        
        {reviewIncorrectOnly && incorrectCount === 0 ? (
          <Paper sx={{ 
            p: 3, 
            textAlign: 'center', 
            bgcolor: (theme) => theme.palette.mode === 'dark' ? '#1b5e20' : 'success.light',
            color: (theme) => theme.palette.text.primary
          }}>
            <CheckCircleIcon color="success" sx={{ fontSize: 48, mb: 2 }} />
            <Typography variant="h6" gutterBottom>
              Perfect Score! 🎉
            </Typography>
            <Typography variant="body1">
              You answered all questions correctly. There are no incorrect answers to review.
            </Typography>
          </Paper>
        ) : (
          questions
            .map((q, idx) => ({ ...q, originalIndex: idx }))
            .filter((q, idx) => !reviewIncorrectOnly || examState.answers[q.originalIndex] !== q.answer)
            .map((q, displayIdx) => {
            const idx = q.originalIndex;
            const isCorrect = examState.answers[idx] === q.answer;
          
          return (
            <Paper 
              key={q.id} 
              sx={{ 
                p: 3, 
                mb: 3, 
                borderLeft: isCorrect ? '5px solid #4caf50' : '5px solid #f44336',
                bgcolor: (theme) => theme.palette.background.paper,
                color: (theme) => theme.palette.text.primary
              }}
              elevation={3}
            >
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <Typography variant="h6" sx={{ flexGrow: 1 }}>
                  Q{idx + 1}. <MathRenderer>{q.question}</MathRenderer>
                </Typography>
                {isCorrect ? (
                  <CheckCircleIcon color="success" sx={{ ml: 1 }} />
                ) : (
                  <CancelIcon color="error" sx={{ ml: 1 }} />
                )}
              </Box>
              
              <Divider sx={{ my: 2 }} />
              
              <Grid container spacing={2}>
                {q.options.map((opt) => (
                  <Grid item xs={12} key={opt.label}>
                    <Paper 
                      sx={{ 
                        p: 1.5, 
                        bgcolor: (theme) => {
                          if (examState.answers[idx] === opt.label && q.answer === opt.label) {
                            return theme.palette.mode === 'dark' ? '#1b5e20' : '#e8f5e9';
                          }
                          if (examState.answers[idx] === opt.label && q.answer !== opt.label) {
                            return theme.palette.mode === 'dark' ? '#b71c1c' : '#ffebee';
                          }
                          if (examState.answers[idx] !== opt.label && q.answer === opt.label) {
                            return theme.palette.mode === 'dark' ? '#0d47a1' : '#e3f2fd';
                          }
                          return theme.palette.background.paper;
                        },
                        color: (theme) => theme.palette.text.primary
                      }}
                    >
                      <Typography>
                        {opt.label}. <MathRenderer>{opt.text}</MathRenderer>
                        {examState.answers[idx] === opt.label && q.answer === opt.label && 
                          <CheckCircleIcon fontSize="small" color="success" sx={{ ml: 1, verticalAlign: 'middle' }} />
                        }
                        {examState.answers[idx] === opt.label && q.answer !== opt.label && 
                          <CancelIcon fontSize="small" color="error" sx={{ ml: 1, verticalAlign: 'middle' }} />
                        }
                        {examState.answers[idx] !== opt.label && q.answer === opt.label && 
                          <CheckCircleIcon fontSize="small" color="primary" sx={{ ml: 1, verticalAlign: 'middle' }} />
                        }
                      </Typography>
                    </Paper>
                  </Grid>
                ))}
              </Grid>
              
              <Box sx={{ 
                mt: 2, 
                p: 2, 
                bgcolor: (theme) => theme.palette.mode === 'dark' ? '#2e2e2e' : '#f8f9fa',
                borderRadius: 1,
                color: (theme) => theme.palette.text.primary
              }}>
                <Typography variant="body1" sx={{ fontWeight: 'bold', mb: 1 }}>
                  Explanation:
                </Typography>
                <Typography variant="body2" paragraph>
                  <strong>EN:</strong> <MathRenderer>{q.explanation.en}</MathRenderer>
                </Typography>
                <Typography variant="body2">
                  <strong>VI:</strong> <MathRenderer>{q.explanation.vi}</MathRenderer>
                </Typography>
              </Box>
            </Paper>
          );
        }))}
        
        <Box sx={{ textAlign: 'center', mt: 4, display: 'flex', gap: 2, justifyContent: 'center' }}>
          <Button 
            variant="contained" 
            size="large"
            onClick={() => {
              // Reset để làm lại exam hiện tại
              examState.resetExamState();
              examState.setExamStarted(true);
              timer.resetTimer();
            }}
          >
            Take This Exam Again
          </Button>
          <Button 
            variant="outlined" 
            size="large"
            onClick={() => {
              // Reset về trang chọn exam
              examState.resetExamState();
            }}
          >
            Choose Exam
          </Button>
        </Box>
      </Container>
    </motion.div>
  </>
);
  }

  // Welcome screen with exam selection
  if (!examState.examStarted) {
    return (
      <Container maxWidth="md" sx={{ mt: 8 }}>
        <Paper elevation={3} sx={{ p: 4, textAlign: 'center' }}>
          <Typography variant="h4" component="h1" gutterBottom color="primary">
            Exam Hub - Practice Tests
          </Typography>
          
          <Typography variant="body1" paragraph sx={{ mb: 4 }}>
            Welcome to Exam Hub. Select an exam type from the list below and click Start when you're ready.
          </Typography>
          
          <FormControl fullWidth sx={{ mb: 4 }}>
            <InputLabel id="exam-select-label">Select Exam</InputLabel>
            <Select
              labelId="exam-select-label"
              id="exam-select"
              value={examType}
              label="Select Exam"
              onChange={handleExamTypeChange}
              disabled={loading}
              MenuProps={{
                PaperProps: {
                  style: {
                    maxHeight: 400,
                    overflow: 'auto'
                  }
                }
              }}
            >
              {examTypes.map((type) => (
                <MenuItem key={type.value} value={type.value}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', width: '100%' }}>
                    <Typography variant="body1">{type.label}</Typography>
                    <Typography variant="body2" color="text.secondary">
                      {type.questionCount} câu - {type.durationText}
                    </Typography>
                  </Box>
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          
          {loading ? (
            <LoadingSpinner message="Loading exam questions..." />
          ) : (
            <Button 
              variant="contained" 
              color="primary" 
              size="large"
              onClick={startExam}
            >
              Start Exam
            </Button>
          )}
        </Paper>
      </Container>
    );
  }

  const q = questions[examState.currentIndex];
  const progress = (examState.currentIndex / questions.length) * 100;

      return (
    <Container maxWidth="lg" sx={{ mt: 2, mb: 2 }}>
      <Paper elevation={3} sx={{ p: 2, mb: 2 }}>
        <ExamHeader 
          minutes={timer.minutes}
          seconds={timer.seconds}
          isLowTime={timer.isLowTime}
          isVeryLowTime={timer.isVeryLowTime}
          progress={progress}
          currentIndex={examState.currentIndex}
          totalQuestions={questions.length}
          answeredCount={examState.answeredCount}
        />
      </Paper>
      
      <AnimatePresence mode="wait">
        <QuestionCard 
          question={q}
          currentIndex={examState.currentIndex}
          selectedAnswer={examState.answers[examState.currentIndex]}
          flagged={examState.flagged[examState.currentIndex]}
          isTransitioning={examState.isTransitioning}
          onSelect={examState.handleSelect}
          onToggleFlag={examState.toggleFlag}
        />
      </AnimatePresence>
      
      <Paper elevation={3}>
        <QuestionNavigator 
          questions={questions}
          answers={examState.answers}
          flagged={examState.flagged}
          currentIndex={examState.currentIndex}
          onNavigateToQuestion={examState.navigateToQuestion}
        />
      </Paper>
      
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 1 }}>
        <motion.div
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          <Button 
            variant="outlined" 
            startIcon={<NavigateBeforeIcon />}
            disabled={examState.currentIndex === 0} 
            onClick={examState.handlePrev}
            size="medium"
          >
            Previous
          </Button>
        </motion.div>
        
        <motion.div
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          <Button 
            variant="contained" 
            color="error"
            onClick={confirmFinish}
            size="medium"
          >
            End Exam
          </Button>
        </motion.div>
        
        {examState.currentIndex === questions.length - 1 ? (
          <motion.div
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <Button 
              variant="contained" 
              color="success"
              onClick={confirmFinish}
              size="medium"
            >
              Finish Exam
            </Button>
          </motion.div>
        ) : (
          <motion.div
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <Button 
              variant="contained" 
              endIcon={<NavigateNextIcon />}
              onClick={examState.handleNext}
              size="medium"
            >
              Next
            </Button>
          </motion.div>
        )}
      </Box>
    </Container>
  );
}
