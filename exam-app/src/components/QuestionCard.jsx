import React from 'react';
import { 
  Box, 
  Typography, 
  RadioGroup, 
  FormControlLabel, 
  Radio, 
  Paper, 
  Divider, 
  IconButton, 
  Tooltip 
} from '@mui/material';
import { Flag as FlagIcon } from '@mui/icons-material';
import { motion } from 'framer-motion';
import MathRenderer from './MathRenderer';

const QuestionCard = ({ 
  question, 
  currentIndex, 
  selectedAnswer, 
  flagged, 
  isTransitioning,
  onSelect, 
  onToggleFlag 
}) => {
  return (
    <motion.div
      key={currentIndex}
      initial={{ opacity: 0, x: isTransitioning ? 20 : 0 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
      transition={{ duration: 0.3 }}
    >
      <Paper elevation={3} sx={{ p: 3, mb: 2 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1.5 }}>
          <Typography variant="h6" fontWeight="medium">
            Q{currentIndex + 1}. <MathRenderer>{question.question}</MathRenderer>
          </Typography>
          <Tooltip title={flagged ? "Remove flag" : "Flag for review"}>
            <motion.div
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
            >
              <IconButton onClick={onToggleFlag} color={flagged ? "warning" : "default"}>
                <FlagIcon />
              </IconButton>
            </motion.div>
          </Tooltip>
        </Box>
        
        <Divider sx={{ mb: 2 }} />
        
        <RadioGroup 
          value={selectedAnswer || ''} 
          onChange={(e) => onSelect(e.target.value)}
        >
          {question.options.map((opt, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.1 }}
            >
              <Paper 
                elevation={1} 
                sx={{ 
                  mb: 1.5, 
                  borderRadius: 2,
                  transition: 'all 0.2s',
                  '&:hover': {
                    bgcolor: (theme) => theme.palette.mode === 'dark' 
                      ? 'rgba(255, 255, 255, 0.05)' 
                      : 'rgba(0, 0, 0, 0.04)',
                    transform: 'translateY(-1px)'
                  }
                }}
              >
                <FormControlLabel
                  value={opt.label}
                  control={<Radio />}
                  label={
                    <Box sx={{ p: 0.5 }}>
                      <Typography variant="body2">
                        <strong>{opt.label}.</strong> <MathRenderer>{opt.text}</MathRenderer>
                      </Typography>
                    </Box>
                  }
                  sx={{ 
                    display: 'flex', 
                    width: '100%', 
                    m: 0, 
                    p: 0.5
                  }}
                />
              </Paper>
            </motion.div>
          ))}
        </RadioGroup>
      </Paper>
    </motion.div>
  );
};

export default QuestionCard; 