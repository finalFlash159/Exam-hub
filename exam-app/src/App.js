import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { Box, AppBar, Toolbar, Typography, Button, Container, Tabs, Tab } from '@mui/material';
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
      </Box>
    </Router>
  );
}

export default App;
