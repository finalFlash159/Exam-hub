import React, { useState, useEffect, useCallback } from 'react';
import { 
  Box, Button, Container, Typography, RadioGroup, FormControlLabel, 
  Radio, Paper, Grid, LinearProgress, Chip, Card, 
  Divider, CircularProgress, IconButton, Tooltip,
  Select, MenuItem, FormControl, InputLabel
} from '@mui/material';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import CancelIcon from '@mui/icons-material/Cancel';
import TimerIcon from '@mui/icons-material/Timer';
import NavigateNextIcon from '@mui/icons-material/NavigateNext';
import NavigateBeforeIcon from '@mui/icons-material/NavigateBefore';
import FlagIcon from '@mui/icons-material/Flag';

// Import from centralized data management
import { getExamTypes, getQuestions } from '../data';

const TOTAL_TIME = 120 * 60; // 120 minutes in seconds
const PASSING_SCORE = 70; // 70% to pass

export default function ExamApp() {
  const [examType, setExamType] = useState('default');
  const [questions, setQuestions] = useState(getQuestions('default'));
  const [loading, setLoading] = useState(false);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [answers, setAnswers] = useState(Array(questions.length).fill(null));
  const [flagged, setFlagged] = useState(Array(questions.length).fill(false));
  const [timeLeft, setTimeLeft] = useState(TOTAL_TIME);
  const [examStarted, setExamStarted] = useState(false);
  const [score, setScore] = useState(0);
  const [finished, setFinished] = useState(false);
  const [examTypes, setExamTypes] = useState(getExamTypes());
  
  // Định nghĩa handleFinish sử dụng useCallback để tránh lỗi
  const handleFinish = useCallback(() => {
    // Calculate score
    const correctAnswers = answers.filter((answer, index) => 
      answer === questions[index].answer
    ).length;
    const scorePercent = Math.round((correctAnswers / questions.length) * 100);
    setScore(scorePercent);
    setFinished(true);
  }, [answers, questions]);
  
  // Load different question sets based on selection
  const handleExamTypeChange = (event) => {
    const selectedExam = event.target.value;
    setExamType(selectedExam);
    setLoading(true);
    
    try {
      const newQuestions = getQuestions(selectedExam);
      setQuestions(newQuestions);
      setAnswers(Array(newQuestions.length).fill(null));
      setFlagged(Array(newQuestions.length).fill(false));
      setCurrentIndex(0);
      setExamStarted(false);
    } catch (error) {
      console.error("Error loading questions:", error);
      alert("Failed to load exam questions. Please try again.");
    } finally {
      setLoading(false);
    }
  };
  
  const startExam = () => {
    setExamStarted(true);
    setTimeLeft(TOTAL_TIME);
  };

  useEffect(() => {
    if (timeLeft <= 0) {
      handleFinish();
      return;
    }
    const timer = setInterval(() => setTimeLeft((t) => t - 1), 1000);
    return () => clearInterval(timer);
  }, [timeLeft, handleFinish]);

  const handleSelect = (option) => {
    const newAnswers = [...answers];
    newAnswers[currentIndex] = option;
    setAnswers(newAnswers);
  };

  const handleNext = () => {
    if (currentIndex < questions.length - 1) setCurrentIndex((i) => i + 1);
  };
  
  const handlePrev = () => {
    if (currentIndex > 0) setCurrentIndex((i) => i - 1);
  };

  const toggleFlag = () => {
    const newFlagged = [...flagged];
    newFlagged[currentIndex] = !newFlagged[currentIndex];
    setFlagged(newFlagged);
  };

  const confirmFinish = () => {
    if (window.confirm('Are you sure you want to end the exam and see your results?')) {
      handleFinish();
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

  if (finished) {
    const isPassed = score >= PASSING_SCORE;
    const correctCount = answers.filter((answer, index) => answer === questions[index].answer).length;
    
    return (
      <Container maxWidth="md" sx={{ mt: 4, mb: 8 }}>
        <Card sx={{ mb: 4, p: 3, textAlign: 'center', bgcolor: isPassed ? '#e8f5e9' : '#ffebee' }}>
          <Typography variant="h4" gutterBottom color="primary" fontWeight="bold">
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

        <Typography variant="h5" gutterBottom sx={{ mt: 4, mb: 3 }}>
          Review Your Answers
        </Typography>
        
        {questions.map((q, idx) => {
          const isCorrect = answers[idx] === q.answer;
          
          return (
            <Paper 
              key={q.id} 
              sx={{ 
                p: 3, 
                mb: 3, 
                borderLeft: isCorrect ? '5px solid #4caf50' : '5px solid #f44336'
              }}
              elevation={3}
            >
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <Typography variant="h6" sx={{ flexGrow: 1 }}>
                  Q{idx + 1}. {q.question}
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
                        bgcolor: 
                          answers[idx] === opt.label && q.answer === opt.label ? '#e8f5e9' :
                          answers[idx] === opt.label && q.answer !== opt.label ? '#ffebee' :
                          answers[idx] !== opt.label && q.answer === opt.label ? '#e3f2fd' : 
                          'white'
                      }}
                    >
                      <Typography>
                        {opt.label}. {opt.text}
                        {answers[idx] === opt.label && q.answer === opt.label && 
                          <CheckCircleIcon fontSize="small" color="success" sx={{ ml: 1, verticalAlign: 'middle' }} />
                        }
                        {answers[idx] === opt.label && q.answer !== opt.label && 
                          <CancelIcon fontSize="small" color="error" sx={{ ml: 1, verticalAlign: 'middle' }} />
                        }
                        {answers[idx] !== opt.label && q.answer === opt.label && 
                          <CheckCircleIcon fontSize="small" color="primary" sx={{ ml: 1, verticalAlign: 'middle' }} />
                        }
                      </Typography>
                    </Paper>
                  </Grid>
                ))}
              </Grid>
              
              <Box sx={{ mt: 2, p: 2, bgcolor: '#f8f9fa', borderRadius: 1 }}>
                <Typography variant="body1" sx={{ fontWeight: 'bold', mb: 1 }}>
                  Explanation:
                </Typography>
                <Typography variant="body2" paragraph>
                  <strong>EN:</strong> {q.explanation.en}
                </Typography>
                <Typography variant="body2">
                  <strong>VI:</strong> {q.explanation.vi}
                </Typography>
              </Box>
            </Paper>
          );
        })}
        
        <Box sx={{ textAlign: 'center', mt: 4 }}>
          <Button 
            variant="contained" 
            size="large"
            onClick={() => window.location.reload()}
          >
            Take Exam Again
          </Button>
        </Box>
      </Container>
    );
  }

  // Welcome screen with exam selection
  if (!examStarted) {
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
            >
              {examTypes.map((type) => (
                <MenuItem key={type.value} value={type.value}>
                  {type.label}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          
          {loading ? (
            <CircularProgress />
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

  const q = questions[currentIndex];
  const minutes = Math.floor(timeLeft / 60);
  const seconds = timeLeft % 60;
  const progress = (currentIndex / questions.length) * 100;
  const answeredCount = answers.filter(a => a !== null).length;

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h4" color="primary" fontWeight="bold">
            Certification Practice Exam
          </Typography>
          <Chip 
            icon={<TimerIcon />}
            label={`${minutes}:${seconds.toString().padStart(2, '0')}`}
            color={timeLeft < 300 ? "error" : timeLeft < 600 ? "warning" : "primary"}
            variant="filled"
            size="large"
          />
        </Box>
        
        <LinearProgress 
          variant="determinate" 
          value={progress} 
          sx={{ height: 10, borderRadius: 5, mb: 2 }}
        />
        
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
          <Chip 
            label={`Question ${currentIndex + 1} of ${questions.length}`} 
            color="primary" 
            variant="outlined"
          />
          <Chip 
            label={`Answered: ${answeredCount}/${questions.length}`}
            color={answeredCount === questions.length ? "success" : "default"}
            variant="outlined"
          />
        </Box>
      </Paper>
      
      <Paper elevation={3} sx={{ p: 4, mb: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6" fontWeight="medium">
            Q{currentIndex + 1}. {q.question}
          </Typography>
          <Tooltip title={flagged[currentIndex] ? "Remove flag" : "Flag for review"}>
            <IconButton onClick={toggleFlag} color={flagged[currentIndex] ? "warning" : "default"}>
              <FlagIcon />
            </IconButton>
          </Tooltip>
        </Box>
        
        <Divider sx={{ mb: 3 }} />
        
        <RadioGroup 
          value={answers[currentIndex] || ''} 
          onChange={(e) => handleSelect(e.target.value)}
        >
          {q.options.map((opt, i) => (
            <Paper 
              key={i} 
              elevation={1} 
              sx={{ 
                mb: 2, 
                borderRadius: 2,
                transition: 'all 0.2s',
                '&:hover': {
                  bgcolor: '#f5f5f5',
                  transform: 'translateY(-2px)'
                }
              }}
            >
              <FormControlLabel
                value={opt.label}
                control={<Radio />}
                label={
                  <Box sx={{ p: 1 }}>
                    <Typography><strong>{opt.label}.</strong> {opt.text}</Typography>
                  </Box>
                }
                sx={{ 
                  display: 'flex', 
                  width: '100%', 
                  m: 0, 
                  p: 1
                }}
              />
            </Paper>
          ))}
        </RadioGroup>
      </Paper>
      
      <Paper elevation={3} sx={{ p: 2, mb: 3 }}>
        <Typography variant="h6" align="center" gutterBottom>
          Question Navigator
        </Typography>
        
        <Divider sx={{ mb: 2 }} />
        
        <Box sx={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(14, 1fr)', 
          gridTemplateRows: 'repeat(5, auto)',
          gap: 1,
          mb: 2
        }}>
          {questions.map((_, idx) => (
            <Button
              key={idx}
              variant="contained"
              size="small"
              onClick={() => setCurrentIndex(idx)}
              sx={{
                minWidth: '36px',
                height: '36px',
                p: 0,
                backgroundColor: 
                  currentIndex === idx ? 'primary.main' :
                  flagged[idx] ? 'warning.main' :
                  answers[idx] ? 'success.main' : 
                  'grey.300',
                color: 'white',
                '&:hover': {
                  backgroundColor: 
                    currentIndex === idx ? 'primary.dark' :
                    flagged[idx] ? 'warning.dark' :
                    answers[idx] ? 'success.dark' : 
                    'grey.400',
                }
              }}
            >
              {idx + 1}
            </Button>
          ))}
        </Box>
        
        <Box sx={{ 
          display: 'flex', 
          justifyContent: 'space-between', 
          flexWrap: 'wrap',
          mt: 2 
        }}>
          <Box sx={{ display: 'flex', alignItems: 'center', mr: 3, mb: 1 }}>
            <Box sx={{ width: 20, height: 20, bgcolor: 'success.main', mr: 1, borderRadius: 1 }}></Box>
            <Typography variant="body2">Answered</Typography>
          </Box>
          <Box sx={{ display: 'flex', alignItems: 'center', mr: 3, mb: 1 }}>
            <Box sx={{ width: 20, height: 20, bgcolor: 'primary.main', mr: 1, borderRadius: 1 }}></Box>
            <Typography variant="body2">Current</Typography>
          </Box>
          <Box sx={{ display: 'flex', alignItems: 'center', mr: 3, mb: 1 }}>
            <Box sx={{ width: 20, height: 20, bgcolor: 'warning.main', mr: 1, borderRadius: 1 }}></Box>
            <Typography variant="body2">Flagged</Typography>
          </Box>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
            <Box sx={{ width: 20, height: 20, bgcolor: 'grey.300', mr: 1, borderRadius: 1 }}></Box>
            <Typography variant="body2">Unanswered</Typography>
          </Box>
        </Box>
      </Paper>
      
      <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
        <Button 
          variant="outlined" 
          startIcon={<NavigateBeforeIcon />}
          disabled={currentIndex === 0} 
          onClick={handlePrev}
          size="large"
        >
          Previous
        </Button>
        
        <Button 
          variant="contained" 
          color="error"
          onClick={confirmFinish}
          size="large"
        >
          End Exam
        </Button>
        
        {currentIndex === questions.length - 1 ? (
          <Button 
            variant="contained" 
            color="success"
            onClick={confirmFinish}
            size="large"
          >
            Finish Exam
          </Button>
        ) : (
          <Button 
            variant="contained" 
            endIcon={<NavigateNextIcon />}
            onClick={handleNext}
            size="large"
          >
            Next
          </Button>
        )}
      </Box>
    </Container>
  );
}
