import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { Box, AppBar, Toolbar, Typography, Tabs, Tab, Snackbar, Alert, IconButton } from '@mui/material';
import { Brightness4, Brightness7 } from '@mui/icons-material';
import ExamApp from './components/ExamApp';
import ExamGenerator from './components/ExamGenerator';
import { ThemeContextProvider, useTheme } from './contexts/ThemeContext';
import { motion } from 'framer-motion';
import { useLocation } from 'react-router-dom';

function NavTabs() {
  const location = useLocation();
  const currentPath = location.pathname;
  const { isDarkMode, toggleDarkMode } = useTheme();
  
  return (
    <Box sx={{ display: 'flex', alignItems: 'center', ml: 2, flexGrow: 1 }}>
    <Tabs 
      value={currentPath} 
      textColor="inherit"
      indicatorColor="secondary"
        sx={{ flexGrow: 1 }}
    >
      <Tab 
        label="Take Exam" 
        value="/" 
        component={Link} 
        to="/"
          sx={{ color: 'inherit', fontWeight: 'medium' }}
      />
      <Tab 
        label="Create Exam" 
        value="/create" 
        component={Link} 
        to="/create"
          sx={{ color: 'inherit', fontWeight: 'medium' }}
      />
    </Tabs>
      
      {/* Dark Mode Toggle */}
      <motion.div
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
      >
        <IconButton 
          onClick={toggleDarkMode} 
          color="inherit"
          sx={{ 
            ml: 2,
            transition: 'all 0.3s ease-in-out',
            '&:hover': {
              backgroundColor: 'rgba(255, 255, 255, 0.1)',
            }
          }}
        >
          {isDarkMode ? <Brightness7 /> : <Brightness4 />}
        </IconButton>
      </motion.div>
    </Box>
  );
}

function AppContent() {
  const [notification, setNotification] = useState(null);
  
  // Kiểm tra xem có thông báo mới từ quá trình lưu bài kiểm tra không
  useEffect(() => {
    const savedExam = sessionStorage.getItem('savedExam');
    if (savedExam) {
      try {
        const examData = JSON.parse(savedExam);
        setNotification({
          message: `🎉 Bài kiểm tra "${examData.title}" đã được thêm thành công vào hệ thống!`,
          type: 'success',
          details: `ID: ${examData.examId} | File: ${examData.fileName}`
        });
        sessionStorage.removeItem('savedExam');
      } catch (e) {
        console.error('Lỗi khi đọc thông tin bài kiểm tra đã lưu:', e);
      }
    }
  }, []);
  
  const handleCloseNotification = () => {
    setNotification(null);
  };
  
  return (
    <Box sx={{ flexGrow: 1, minHeight: '100vh' }}>
      <motion.div
        initial={{ y: -20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5 }}
      >
        <AppBar 
          position="static" 
          elevation={4} 
          sx={{ 
            backgroundColor: '#1976d2',
            '&.MuiAppBar-root': {
              backgroundColor: '#1976d2',
            }
          }}
        >
          <Toolbar>
            <motion.div
              whileHover={{ scale: 1.05 }}
              transition={{ type: "spring", stiffness: 300 }}
            >
            <Typography variant="h5" component="div" sx={{ fontWeight: 'bold' }}>
              Exam Hub
            </Typography>
            </motion.div>
            <NavTabs />
          </Toolbar>
        </AppBar>
      </motion.div>
        
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.6, delay: 0.2 }}
      >
        <Box sx={{ py: 2 }}>
          <Routes>
            <Route path="/" element={<ExamApp />} />
            <Route path="/create" element={<ExamGenerator />} />
          </Routes>
        </Box>
      </motion.div>
        
        {notification && (
        <motion.div
          initial={{ y: -100, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          exit={{ y: -100, opacity: 0 }}
          transition={{ duration: 0.4, type: "spring", stiffness: 300 }}
        >
          <Snackbar 
            open={true} 
            autoHideDuration={8000} 
            onClose={handleCloseNotification}
            anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
          >
            <Alert 
              onClose={handleCloseNotification} 
              severity={notification.type || 'info'} 
              variant="filled"
              sx={{ 
                width: '100%',
                fontSize: '1.1rem',
                fontWeight: 'medium',
                '& .MuiAlert-message': {
                  display: 'flex',
                  flexDirection: 'column',
                  gap: 0.5
                }
              }}
            >
              <Box>
              {notification.message}
              </Box>
              {notification.details && (
                <Box sx={{ fontSize: '0.85rem', opacity: 0.9 }}>
                  {notification.details}
                </Box>
              )}
            </Alert>
          </Snackbar>
        </motion.div>
        )}
      </Box>
  );
}

function App() {
  return (
    <ThemeContextProvider>
      <Router>
        <AppContent />
    </Router>
    </ThemeContextProvider>
  );
}

export default App;
