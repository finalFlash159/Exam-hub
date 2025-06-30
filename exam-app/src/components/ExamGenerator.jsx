import React, { useState, useEffect } from 'react';
import { 
  Box, Button, Container, Typography, Paper, LinearProgress, 
  TextField, FormControl, InputLabel, Select, MenuItem, Stepper, 
  Step, StepLabel, Alert, Chip, Divider
} from '@mui/material';
import UploadFileIcon from '@mui/icons-material/UploadFile';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import AutoFixHighIcon from '@mui/icons-material/AutoFixHigh';
import SaveAltIcon from '@mui/icons-material/SaveAlt';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';

// Backend URL - Railway production URL
const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'https://exam-hub-production-c8b2.up.railway.app';

export default function ExamGenerator() {
  const [activeStep, setActiveStep] = useState(0);
  const [file, setFile] = useState(null);
  const [fileId, setFileId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [examTitle, setExamTitle] = useState('');
  const [questionCount, setQuestionCount] = useState(10);
  const [generatedExam, setGeneratedExam] = useState(null);
  const [saveSuccess, setSaveSuccess] = useState(false);
  
  const steps = ['Upload Document', 'Configure Exam', 'Generate Questions', 'Review & Save'];
  
  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
      setError(null);
    }
  };
  
  // Check backend connectivity on component mount
  const [backendStatus, setBackendStatus] = useState('checking');
  
  useEffect(() => {
    const checkBackendStatus = async () => {
      try {
        const response = await fetch(`${BACKEND_URL}/health`, {
          method: 'GET',
          headers: {
            'Accept': 'application/json',
          },
          // Add these options to handle CORS issues
          mode: 'cors',
          credentials: 'omit'
        });
        
        if (response.ok) {
          setBackendStatus('connected');
        } else {
          setBackendStatus('error');
          setError('Backend server is running but returned an error');
        }
      } catch (err) {
        console.error('Backend connectivity check failed:', err);
        setBackendStatus('error');
        setError('Could not connect to backend server. Please ensure the Python backend is running.');
      }
    };
    
    checkBackendStatus();
  }, []);
  
  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file to upload.');
      return;
    }
    
    const formData = new FormData();
    formData.append('file', file);
    
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${BACKEND_URL}/api/upload`, {
        method: 'POST',
        body: formData,
        // Add these options to handle CORS issues
        mode: 'cors',
        credentials: 'omit',
      });
      

      
      if (!response.ok) {
        // Try to get error details from response
        let errorMessage;
        try {
          const errorData = await response.json();
          errorMessage = errorData.error || `Server error (${response.status})`;
        } catch (parseErr) {
          errorMessage = `Server error (${response.status})`;
        }
        throw new Error(errorMessage);
      }
      
      const data = await response.json();
      
      setFileId(data.file_id);
      setActiveStep(1); // Move to next step
    } catch (err) {
      console.error('Upload error:', err);
      setError(`Failed to upload: ${err.message || 'Network connection issue'}. Please make sure the backend server is running.`);
    } finally {
      setLoading(false);
    }
  };
  
  const handleGenerateExam = async () => {
    if (!fileId) {
      setError('No file uploaded. Please start over.');
      return;
    }
    
    if (!examTitle.trim()) {
      setError('Please provide an exam title');
      return;
    }
    
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${BACKEND_URL}/api/generate-exam`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          file_id: fileId,
          exam_title: examTitle,
          question_count: questionCount
        }),
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.error || 'Failed to generate exam');
      }
      
      setGeneratedExam(data.exam_data);
      setActiveStep(3); // Move to review step
    } catch (err) {
      setError(err.message || 'Error generating exam');
    } finally {
      setLoading(false);
    }
  };
  
  const handleSaveExam = async () => {
    if (!generatedExam) {
      setError('Không có dữ liệu bài kiểm tra để lưu');
      return;
    }
    
    setLoading(true);
    setError(null);
    
    try {
      // Gọi API để lưu bài kiểm tra vào hệ thống
      const response = await fetch(`${BACKEND_URL}/api/save-exam`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          exam_data: generatedExam
        }),
        mode: 'cors',
        credentials: 'omit',
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.detail || data.error || 'Không thể lưu bài kiểm tra');
      }
      
      // Đánh dấu save thành công
      setSaveSuccess(true);
      
      // Lưu thông tin vào sessionStorage để hiển thị thông báo
      sessionStorage.setItem('savedExam', JSON.stringify({
        title: generatedExam.title,
        examId: data.exam_id,
        fileName: data.file_name
      }));
      
      // Đợi 2 giây để user thấy thông báo thành công, sau đó redirect
      setTimeout(() => {
        window.location.href = '/';
      }, 2000);
      
    } catch (err) {
      setError(`Lỗi khi lưu vào hệ thống: ${err.message}`);
      console.error('Lỗi khi lưu bài kiểm tra:', err);
      
      // Tải xuống file JSON như là phương án dự phòng
      const examData = JSON.stringify(generatedExam, null, 2);
      const blob = new Blob([examData], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      
      link.href = url;
      link.download = `${examTitle.replace(/\s+/g, '_').toLowerCase()}.json`;
      document.body.appendChild(link);
      link.click();
      
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
      
      alert('Không thể lưu trực tiếp vào hệ thống. File JSON đã được tải xuống thay thế.');
    } finally {
      setLoading(false);
    }
  };
  
  const renderStep = () => {
    switch (activeStep) {
      case 0:
        return (
          <Box sx={{ py: 3 }}>
            <Typography variant="h6" gutterBottom align="center" sx={{ mb: 3 }}>
              Upload a document to generate exam questions
            </Typography>
            
            {backendStatus === 'error' && (
              <Alert 
                severity="error" 
                sx={{ mb: 3 }}
                action={
                  <Button color="inherit" size="small" onClick={() => window.location.reload()}>
                    RETRY
                  </Button>
                }
              >
                <Typography fontWeight="medium">Backend Connection Error</Typography>
                <Typography variant="body2">
                  Could not connect to the backend server. Make sure the Python server is running at {BACKEND_URL}
                </Typography>
              </Alert>
            )}
            
            <Box sx={{ 
              border: (theme) => `1px dashed ${theme.palette.divider}`,
              borderRadius: 2, 
              p: 4, 
              mb: 3, 
              textAlign: 'center',
              backgroundColor: (theme) => theme.palette.mode === 'dark' 
                ? 'rgba(255, 255, 255, 0.05)' 
                : 'rgba(0, 0, 0, 0.02)'
            }}>
              <input
                accept=".pdf,.docx"
                style={{ display: 'none' }}
                id="file-upload"
                type="file"
                onChange={handleFileChange}
              />
              <label htmlFor="file-upload">
                <Button
                  variant="contained"
                  component="span"
                  startIcon={<UploadFileIcon />}
                  fullWidth
                  size="large"
                  sx={{ 
                    mb: 2, 
                    py: 1.5
                  }}
                >
                  SELECT DOCUMENT (PDF OR DOCX)
                </Button>
              </label>
              
              {file && (
                <Alert 
                  icon={<CheckCircleIcon fontSize="inherit" />}
                  severity="success" 
                  sx={{ mt: 2, mb: 2 }}
                >
                  <Typography><strong>Selected file:</strong> {file.name}</Typography>
                </Alert>
              )}
              
              {!file && (
                <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
                  Select a PDF or DOCX file to continue
                </Typography>
              )}
            </Box>
            
            <Button
              variant="contained"
              color="success"
              onClick={handleUpload}
              disabled={!file || loading || backendStatus === 'error'}
              fullWidth
              size="large"
              startIcon={<CloudUploadIcon />}
              sx={{ 
                py: 1.5,
                boxShadow: 3
              }}
            >
              UPLOAD & PROCESS DOCUMENT
            </Button>
            
            {!file && (
              <Typography variant="body2" color="text.secondary" sx={{ mt: 2, textAlign: 'center' }}>
                Please select a document first
              </Typography>
            )}
          </Box>
        );
      case 1:
        return (
          <Box sx={{ py: 3 }}>
            <TextField
              label="Exam Title"
              variant="outlined"
              fullWidth
              value={examTitle}
              onChange={(e) => setExamTitle(e.target.value)}
              margin="normal"
              required
            />
            
            <FormControl fullWidth margin="normal">
              <InputLabel id="question-count-label">Number of Questions</InputLabel>
              <Select
                labelId="question-count-label"
                value={questionCount}
                label="Number of Questions"
                onChange={(e) => setQuestionCount(e.target.value)}
              >
                {[5, 10, 15, 20, 25, 30].map((count) => (
                  <MenuItem key={count} value={count}>
                    {count} questions
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 3 }}>
              <Button
                variant="outlined"
                onClick={() => setActiveStep(0)}
              >
                Back
              </Button>
              <Button
                variant="contained"
                color="primary"
                onClick={() => setActiveStep(2)}
                disabled={!examTitle.trim()}
              >
                Continue
              </Button>
            </Box>
          </Box>
        );
      case 2:
        return (
          <Box sx={{ py: 3, textAlign: 'center' }}>
            <Typography variant="h6" gutterBottom>
              Ready to Generate Exam Questions
            </Typography>
            
            <Box sx={{ my: 3 }}>
              <Typography variant="body1" gutterBottom>
                Title: {examTitle}
              </Typography>
              <Chip label={`${questionCount} Questions`} color="primary" sx={{ mr: 1 }} />
              <Chip label="AI-Generated" color="secondary" />
            </Box>
            
            <Typography variant="body2" color="text.secondary" paragraph sx={{ mb: 3 }}>
              We will use the document you uploaded along with Gemini AI to create multiple-choice questions based on the content.
            </Typography>
            
            <Button
              variant="contained"
              color="primary"
              startIcon={<AutoFixHighIcon />}
              onClick={handleGenerateExam}
              disabled={loading}
              size="large"
            >
              Generate Exam Questions
            </Button>
            
            <Box sx={{ mt: 2 }}>
              <Button
                variant="outlined"
                onClick={() => setActiveStep(1)}
                disabled={loading}
              >
                Back to Configuration
              </Button>
            </Box>
          </Box>
        );
      case 3:
        return (
          <Box sx={{ py: 3 }}>
            {saveSuccess ? (
              // Success State
              <Box sx={{ textAlign: 'center' }}>
                <CheckCircleIcon sx={{ fontSize: 80, color: 'success.main', mb: 2 }} />
                <Typography variant="h5" gutterBottom color="success.main">
                  Bài kiểm tra đã được lưu thành công!
                </Typography>
                <Typography variant="body1" sx={{ mb: 3 }}>
                  "{examTitle}" đã được thêm vào danh sách bài kiểm tra.
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Đang chuyển hướng về trang chủ...
                </Typography>
                <LinearProgress sx={{ mt: 2 }} color="success" />
              </Box>
            ) : (
              // Normal Review State
              <>
                <Typography variant="h6" gutterBottom>
                  Exam Generated Successfully!
                </Typography>
                
                <Box sx={{ 
                  my: 3, 
                  p: 3, 
                  bgcolor: (theme) => theme.palette.mode === 'dark' 
                    ? 'rgba(255, 255, 255, 0.05)' 
                    : 'rgba(0, 0, 0, 0.02)', 
                  borderRadius: 2,
                  border: (theme) => `1px solid ${theme.palette.divider}`
                }}>
                  <Typography variant="h5" gutterBottom>
                    {examTitle}
                  </Typography>
                  <Divider sx={{ my: 1 }} />
                  <Typography variant="body1">
                    {generatedExam?.questions?.length || questionCount} questions generated
                  </Typography>
                </Box>
                
                <Box sx={{ 
                  mb: 3, 
                  maxHeight: '300px', 
                  overflow: 'auto', 
                  p: 2, 
                  border: (theme) => `1px solid ${theme.palette.divider}`, 
                  borderRadius: 1,
                  bgcolor: (theme) => theme.palette.background.paper
                }}>
                  <Typography variant="subtitle1" gutterBottom>
                    Preview of questions:
                  </Typography>
                  
                  {generatedExam?.questions?.slice(0, 3).map((q, idx) => (
                    <Paper key={idx} sx={{ p: 2, mb: 2 }} elevation={1}>
                      <Typography variant="body1" gutterBottom>
                        <strong>Q{idx + 1}:</strong> {q.question}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Correct answer: Option {q.answer}
                      </Typography>
                    </Paper>
                  ))}
                  
                  {generatedExam?.questions?.length > 3 && (
                    <Typography variant="body2" color="text.secondary" align="center">
                      ... and {generatedExam.questions.length - 3} more questions
                    </Typography>
                  )}
                </Box>
                
                <Box sx={{ display: 'flex', justifyContent: 'center', mt: 3, gap: 2 }}>
                  <Button
                    variant="contained"
                    color="success"
                    startIcon={<SaveAltIcon />}
                    onClick={handleSaveExam}
                    size="large"
                    disabled={loading}
                  >
                    {loading ? 'Đang lưu vào hệ thống...' : 'Lưu vào hệ thống'}
                  </Button>
                </Box>
                
                <Typography variant="body2" color="text.secondary" align="center" sx={{ mt: 2 }}>
                  💡 Bài kiểm tra sẽ được thêm vào danh sách để có thể chọn từ trang chủ
                </Typography>
              </>
            )}
          </Box>
        );
      default:
        return <div>Unknown step</div>;
    }
  };
  
  return (
    <Container maxWidth="md" sx={{ mt: 4, mb: 8 }}>
      <Paper elevation={3} sx={{ p: 4, borderRadius: 2 }}>
        <Typography variant="h4" component="h1" align="center" gutterBottom color="primary" sx={{ fontWeight: 'bold', mb: 3 }}>
          Create Exam from Document
        </Typography>
        
        <Stepper activeStep={activeStep} sx={{ mb: 4 }} alternativeLabel>
          {steps.map((label) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>
        
        {loading && <LinearProgress sx={{ mb: 3 }} color="secondary" />}
        
        {error && (
          <Alert severity="error" sx={{ mb: 3, fontWeight: 'medium' }}>
            {error}
          </Alert>
        )}
        
        {renderStep()}
      </Paper>
    </Container>
  );
}
