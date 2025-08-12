import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Typography,
  Card,
  CardContent,
  Button,
  Box,
  Radio,
  RadioGroup,
  FormControlLabel,
  LinearProgress,
  Alert,
  Chip,
  Paper,
  Grid,
} from '@mui/material';
import {
  PsychologyOutlined,
  TimerOutlined,
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import { useUser } from '../context/UserContext';
import { apiService } from '../services/api';
import ProgressStepper from '../components/ProgressStepper';
import LoadingPage from '../components/LoadingPage';

const themeColors = {
  'Strategic': '#d4af37',     // Gold theme
  'Executing': '#d4af37',     // Gold theme
  'Influencing': '#d4af37',   // Gold theme  
  'Relationship': '#d4af37'   // Gold theme
};

function InitialAssessment() {
  const navigate = useNavigate();
  const { state, actions } = useUser();
  const [questions, setQuestions] = useState([]);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [responses, setResponses] = useState({});
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [timeElapsed, setTimeElapsed] = useState(0);

  // Timer effect
  useEffect(() => {
    const timer = setInterval(() => {
      setTimeElapsed(prev => prev + 1);
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  // Load questions on component mount
  useEffect(() => {
    loadQuestions();
  }, []);

  const loadQuestions = async () => {
    try {
      setLoading(true);
      console.log('Loading questions...');
      const questionsData = await apiService.getFixedQuestions();
      console.log('Questions loaded:', questionsData);
      
      if (!questionsData || questionsData.length === 0) {
        throw new Error('No questions received from API');
      }
      
      setQuestions(questionsData);
      actions.setQuestions('fixed', questionsData);
    } catch (error) {
      console.error('Error loading questions:', error);
      setError('Failed to load questions. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleResponseChange = (event) => {
    const questionId = questions[currentQuestionIndex].QuestionID;
    const response = parseInt(event.target.value);
    
    console.log(`Response for ${questionId}: ${response}`);
    
    setResponses(prev => ({
      ...prev,
      [questionId]: response,
    }));
  };

  const handleNext = () => {
    if (currentQuestionIndex < questions.length - 1) {
      setCurrentQuestionIndex(prev => prev + 1);
    } else {
      handleSubmit();
    }
  };

  const handlePrevious = () => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex(prev => prev - 1);
    }
  };

  const handleSubmit = async () => {
    try {
      setSubmitting(true);
      
      // Format responses for API
      const formattedResponses = Object.entries(responses).map(([questionId, response]) => ({
        questionId,
        response,
        timestamp: new Date().toISOString(),
      }));
      
      console.log('Submitting responses:', formattedResponses);
      
      // Submit responses to backend
      await apiService.submitInitialResponses(state.userInfo.userId, formattedResponses);
      
      // Update context
      actions.setResponses('initial', formattedResponses);
      actions.setCurrentStep(2);
      
      // Navigate to summary
      navigate('/summary');
    } catch (error) {
      console.error('Error submitting responses:', error);
      setError('Failed to submit responses. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const progress = ((currentQuestionIndex + 1) / questions.length) * 100;
  const currentQuestion = questions[currentQuestionIndex];
  const currentResponse = currentQuestion ? responses[currentQuestion.QuestionID] : null;
  const themeColor = currentQuestion ? themeColors[currentQuestion.Theme] || '#1976d2' : '#1976d2';

  if (loading) {
    return <LoadingPage message="Loading your personalized assessment..." />;
  }

  if (error) {
    return (
      <Container maxWidth="md">
        <Alert severity="error" sx={{ mt: 4 }}>
          {error}
          <Button
            variant="outlined"
            size="small"
            onClick={loadQuestions}
            sx={{ ml: 2 }}
          >
            Retry
          </Button>
        </Alert>
      </Container>
    );
  }

  if (!questions || questions.length === 0) {
    return (
      <Container maxWidth="md">
        <Alert severity="warning" sx={{ mt: 4 }}>
          No questions available. Please check your connection and try again.
        </Alert>
      </Container>
    );
  }

  const cardVariants = {
    enter: { opacity: 0, x: 100 },
    center: { opacity: 1, x: 0 },
    exit: { opacity: 0, x: -100 },
  };

  return (
    <Container maxWidth="lg">
      <ProgressStepper activeStep={1} />
      
      {/* Header */}
      <Card sx={{ mb: 3, borderRadius: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <PsychologyOutlined sx={{ fontSize: 32, color: 'primary.main', mr: 2 }} />
              <Box>
                <Typography variant="h5" sx={{ fontWeight: 600 }}>
                  Mirror Assessment
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Question {currentQuestionIndex + 1} of {questions.length}
                </Typography>
              </Box>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <Chip
                icon={<TimerOutlined />}
                label={formatTime(timeElapsed)}
                color="primary"
                variant="outlined"
              />
              {/* Category chip removed for first 20 questions as requested */}
            </Box>
          </Box>
          
          <LinearProgress
            variant="determinate"
            value={progress}
            sx={{
              height: 10,
              borderRadius: 5,
              backgroundColor: 'grey.200',
              '& .MuiLinearProgress-bar': {
                borderRadius: 5,
                backgroundColor: themeColor,
              },
            }}
          />
        </CardContent>
      </Card>

      {/* Question Card */}
      <AnimatePresence mode="wait">
        {currentQuestion && (
          <motion.div
            key={currentQuestionIndex}
            variants={cardVariants}
            initial="enter"
            animate="center"
            exit="exit"
            transition={{ duration: 0.3 }}
          >
            <Card sx={{ borderRadius: 3, boxShadow: 3 }}>
              <CardContent sx={{ p: 4 }}>
                
                {/* Horizontal Likert Scale Layout */}
                <Paper elevation={2} sx={{ p: 4, bgcolor: '#f8f9fa' }}>
                  <Typography variant="h6" align="center" sx={{ mb: 4, color: '#333333', fontWeight: 'bold' }}>
                    Which statement describes you better?
                  </Typography>
                  
                  <RadioGroup
                    value={currentResponse || ''}
                    onChange={handleResponseChange}
                    sx={{ width: '100%' }}
                  >
                    <Box sx={{ 
                      display: 'flex', 
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      gap: 2
                    }}>
                      {/* Left Statement */}
                      <Box sx={{ flex: '0 0 35%', textAlign: 'left' }}>
                        <Typography variant="body1" sx={{ 
                          fontSize: '1rem', 
                          fontWeight: 500, 
                          color: '#333333',
                          fontStyle: 'italic'
                        }}>
                          "{currentQuestion.LeftStatement}"
                        </Typography>
                      </Box>
                      
                      {/* Scale options - Circles */}
                      <Box sx={{ 
                        flex: '0 0 30%',
                        display: 'flex', 
                        justifyContent: 'space-between', 
                        alignItems: 'center',
                        px: 1
                      }}>
                        {[
                          { value: '1', position: 'far-left' },
                          { value: '2', position: 'left' },
                          { value: '3', position: 'center' },
                          { value: '4', position: 'right' },
                          { value: '5', position: 'far-right' }
                        ].map((option) => (
                          <FormControlLabel
                            key={option.value}
                            value={option.value}
                            control={
                              <Radio 
                                sx={{ 
                                  color: '#d4af37',
                                  '&.Mui-checked': {
                                    color: '#d4af37',
                                  },
                                  transform: 'scale(1.4)',
                                  p: 1
                                }} 
                              />
                            }
                            label=""
                            sx={{ 
                              margin: 0,
                              '& .MuiFormControlLabel-label': {
                                display: 'none'
                              }
                            }}
                          />
                        ))}
                      </Box>
                      
                      {/* Right Statement */}
                      <Box sx={{ flex: '0 0 35%', textAlign: 'right' }}>
                        <Typography variant="body1" sx={{ 
                          fontSize: '1rem', 
                          fontWeight: 500, 
                          color: '#333333',
                          fontStyle: 'italic'
                        }}>
                          "{currentQuestion.RightStatement}"
                        </Typography>
                      </Box>
                    </Box>
                  </RadioGroup>
                </Paper>

                {/* Navigation Buttons */}
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 4 }}>
                  <Button
                    variant="outlined"
                    onClick={handlePrevious}
                    disabled={currentQuestionIndex === 0}
                    sx={{ minWidth: 100 }}
                  >
                    Previous
                  </Button>
                  
                  <Button
                    variant="contained"
                    onClick={handleNext}
                    disabled={!currentResponse || submitting}
                    sx={{ 
                      minWidth: 150,
                      backgroundColor: themeColor,
                      '&:hover': {
                        backgroundColor: themeColor,
                        opacity: 0.9
                      }
                    }}
                  >
                    {submitting ? 'Submitting...' : 
                     currentQuestionIndex === questions.length - 1 ? 'Complete Assessment' : 'Next Question'}
                  </Button>
                </Box>
              </CardContent>
            </Card>
          </motion.div>
        )}
      </AnimatePresence>

    </Container>
  );
}

export default InitialAssessment;