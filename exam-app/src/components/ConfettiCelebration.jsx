import React, { useEffect, useState } from 'react';
import Confetti from 'react-confetti';
import { motion, AnimatePresence } from 'framer-motion';
import { Box, Typography } from '@mui/material';

const ConfettiCelebration = ({ show, onComplete, score, isPassed }) => {
  const [windowSize, setWindowSize] = useState({
    width: window.innerWidth,
    height: Math.max(window.innerHeight, document.documentElement.scrollHeight),
  });

  useEffect(() => {
    const handleResize = () => {
      setWindowSize({
        width: window.innerWidth,
        height: Math.max(window.innerHeight, document.documentElement.scrollHeight),
      });
    };

    window.addEventListener('resize', handleResize);
    window.addEventListener('scroll', handleResize); // Update on scroll too
    return () => {
      window.removeEventListener('resize', handleResize);
      window.removeEventListener('scroll', handleResize);
    };
  }, []);

  useEffect(() => {
    if (show && isPassed) {
      const timer = setTimeout(() => {
        if (onComplete) onComplete();
      }, 3000); // Confetti chạy 3 giây để giảm lag

      return () => clearTimeout(timer);
    }
  }, [show, isPassed, onComplete]);

  if (!show || !isPassed) return null;

  return (
    <>
      {/* Confetti Effect */}
      <div style={{ 
        position: 'fixed', 
        top: 0, 
        left: 0, 
        width: '100%', 
        height: '100%', 
        pointerEvents: 'none',
        zIndex: 999
      }}>
        <Confetti
          width={windowSize.width}
          height={windowSize.height}
          numberOfPieces={100}
          recycle={false}
          gravity={0.3}
          wind={0.01}
          initialVelocityY={20}
          confettiSource={{
            x: 0,
            y: 0,
            w: windowSize.width,
            h: 0
          }}
          colors={[
            '#f43f5e',
            '#06b6d4', 
            '#8b5cf6',
            '#10b981',
            '#f59e0b',
            '#ef4444',
          ]}
        />
      </div>

            {/* Minimal Success Notification */}
      <AnimatePresence>
        <motion.div
          initial={{ y: -100, opacity: 0 }}
          animate={{ y: 20, opacity: 1 }}
          exit={{ y: -100, opacity: 0 }}
          transition={{ duration: 0.4, ease: "easeOut" }}
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            display: 'flex',
            justifyContent: 'center',
            paddingTop: '20px',
            zIndex: 1000,
            pointerEvents: 'none',
          }}
        >
          <Box
            sx={{
              background: (theme) => theme.palette.background.paper,
              border: (theme) => `1px solid ${theme.palette.divider}`,
              borderRadius: '12px',
              padding: '1rem 1.5rem',
              color: (theme) => theme.palette.text.primary,
              boxShadow: (theme) => theme.palette.mode === 'dark'
                ? '0 8px 32px rgba(0,0,0,0.6)'
                : '0 8px 32px rgba(0,0,0,0.12)',
              display: 'flex',
              alignItems: 'center',
              gap: 1.5,
              minWidth: '300px',
              maxWidth: '400px',
              pointerEvents: 'auto',
            }}
          >
            {/* Success Icon */}
            <Box
              sx={{
                width: '40px',
                height: '40px',
                borderRadius: '50%',
                background: 'linear-gradient(45deg, #4caf50, #66bb6a)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                flexShrink: 0,
              }}
            >
              <Typography variant="h6">✓</Typography>
            </Box>

            {/* Content */}
            <Box sx={{ flexGrow: 1 }}>
              <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 0.5 }}>
                Exam Completed!
              </Typography>
              <Typography variant="body2" sx={{ opacity: 0.7 }}>
                Score: {score}% • {score >= 70 ? 'Passed' : 'Failed'}
              </Typography>
            </Box>

            {/* Close Button */}
            <motion.button
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
              onClick={onComplete}
              style={{
                background: 'none',
                border: 'none',
                width: '32px',
                height: '32px',
                borderRadius: '8px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                cursor: 'pointer',
                color: 'inherit',
                opacity: 0.6,
              }}
            >
              ✕
            </motion.button>
          </Box>
        </motion.div>
      </AnimatePresence>
    </>
  );
};

export default ConfettiCelebration; 