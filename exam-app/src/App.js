import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { Box, AppBar, Toolbar, Typography, Tabs, Tab, Snackbar, Alert } from '@mui/material';
import ExamApp from './components/ExamApp';
import ExamGenerator from './components/ExamGenerator';
import { useLocation } from 'react-router-dom';

function NavTabs() {
  const location = useLocation();
  const currentPath = location.pathname;
  
  return (
    <Tabs 
      value={currentPath} 
      textColor="inherit"
      indicatorColor="secondary"
      sx={{ ml: 2 }}
    >
      <Tab 
        label="Take Exam" 
        value="/" 
        component={Link} 
        to="/"
        sx={{ color: 'white', fontWeight: 'medium' }}
      />
      <Tab 
        label="Create Exam" 
        value="/create" 
        component={Link} 
        to="/create"
        sx={{ color: 'white', fontWeight: 'medium' }}
      />
    </Tabs>
  );
}

function App() {
  const [notification, setNotification] = useState(null);
  
  // Kiểm tra xem có thông báo mới từ quá trình lưu bài kiểm tra không
  useEffect(() => {
    const savedExam = sessionStorage.getItem('savedExam');
    if (savedExam) {
      try {
        const examData = JSON.parse(savedExam);
        setNotification({
          message: `Bài kiểm tra "${examData.title}" đã được thêm thành công!`,
          type: 'success'
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
    <Router>
      <Box sx={{ flexGrow: 1 }}>
        <AppBar position="static" elevation={4}>
          <Toolbar>
            <Typography variant="h5" component="div" sx={{ fontWeight: 'bold' }}>
              Exam Hub
            </Typography>
            <NavTabs />
          </Toolbar>
        </AppBar>
        
        <Box sx={{ py: 2 }}>
          <Routes>
            <Route path="/" element={<ExamApp />} />
            <Route path="/create" element={<ExamGenerator />} />
          </Routes>
        </Box>
        
        {notification && (
          <Snackbar 
            open={true} 
            autoHideDuration={6000} 
            onClose={handleCloseNotification}
            anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
          >
            <Alert 
              onClose={handleCloseNotification} 
              severity={notification.type || 'info'} 
              sx={{ width: '100%' }}
            >
              {notification.message}
            </Alert>
          </Snackbar>
        )}
      </Box>
    </Router>
  );
}

export default App;
