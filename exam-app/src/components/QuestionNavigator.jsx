import React from 'react';
import { Box, Typography, Divider, Button } from '@mui/material';

const QuestionNavigator = ({ 
  questions, 
  answers, 
  flagged, 
  currentIndex, 
  onNavigateToQuestion 
}) => {
  return (
    <Box sx={{ p: 1.5, mb: 2 }}>
      <Typography variant="body1" align="center" sx={{ mb: 1, fontWeight: 'medium' }}>
        Question Navigator
      </Typography>
      
      <Divider sx={{ mb: 1.5 }} />
      
      <Box sx={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(14, 1fr)', 
        gridTemplateRows: 'repeat(5, auto)',
        gap: 0.8,
        mb: 1.5
      }}>
        {questions.map((_, idx) => (
          <Button
            key={idx}
            variant="contained"
            size="small"
            onClick={() => onNavigateToQuestion(idx)}
            sx={{
              minWidth: '32px',
              height: '32px',
              p: 0,
              fontSize: '0.8rem',
              fontWeight: 'bold',
              backgroundColor: 
                currentIndex === idx ? 'primary.main' :
                flagged[idx] ? 'warning.main' :
                answers[idx] ? 'success.main' : 
                (theme) => theme.palette.mode === 'dark' ? '#424242' : '#e0e0e0',
              color: (theme) => {
                if (currentIndex === idx) return '#ffffff';
                if (flagged[idx]) return '#000000';
                if (answers[idx]) return '#ffffff';
                return theme.palette.mode === 'dark' ? '#ffffff' : '#000000';
              },
              border: (theme) => currentIndex === idx 
                ? `2px solid ${theme.palette.primary.dark}` 
                : 'none',
              '&:hover': {
                transform: 'scale(1.05)',
                boxShadow: (theme) => theme.shadows[4],
              },
              transition: 'all 0.2s ease-in-out'
            }}
          >
            {idx + 1}
          </Button>
        ))}
      </Box>
    </Box>
  );
};

export default QuestionNavigator; 