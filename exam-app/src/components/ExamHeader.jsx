import React from 'react';
import { Box, Typography, LinearProgress, Chip } from '@mui/material';
import { Timer as TimerIcon } from '@mui/icons-material';
import { motion } from 'framer-motion';

const ExamHeader = ({ 
  minutes, 
  seconds, 
  isLowTime, 
  isVeryLowTime, 
  progress, 
  currentIndex, 
  totalQuestions, 
  answeredCount 
}) => {
  const timeDisplay = `${minutes}:${seconds.toString().padStart(2, '0')}`;
  const timerColor = isLowTime ? "error" : isVeryLowTime ? "warning" : "primary";

  return (
    <Box sx={{ mb: 2 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
        <Typography variant="h5" color="primary" fontWeight="bold">
          Certification Practice Exam
        </Typography>
        <Chip 
          icon={<TimerIcon />}
          label={timeDisplay}
          color={timerColor}
          variant="filled"
          size="medium"
        />
      </Box>
      
      <motion.div
        initial={{ width: 0 }}
        animate={{ width: '100%' }}
        transition={{ duration: 0.5 }}
      >
        <LinearProgress 
          variant="determinate" 
          value={progress} 
          sx={{ 
            height: 8, 
            borderRadius: 4, 
            mb: 1,
            '& .MuiLinearProgress-bar': {
              transition: 'transform 0.6s ease-in-out',
            }
          }}
        />
      </motion.div>
      
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
        <Chip 
          label={`Question ${currentIndex + 1} of ${totalQuestions}`} 
          color="primary" 
          variant="outlined"
          size="small"
        />
        <Chip 
          label={`Answered: ${answeredCount}/${totalQuestions}`}
          color={answeredCount === totalQuestions ? "success" : "default"}
          variant="outlined"
          size="small"
        />
      </Box>
    </Box>
  );
};

export default ExamHeader; 