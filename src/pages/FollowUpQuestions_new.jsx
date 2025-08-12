import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Typography,
  Card,
  CardContent,
  Button,
  Box,
  TextField,
  LinearProgress,
  Alert,
  Chip,
} from '@mui/material';
import {
  QuestionAnswerOutlined,
  AutoAwesomeOutlined,
  TimerOutlined,
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import { useUser } from '../context/UserContext';
import { apiService } from '../services/api';
import ProgressStepper from '../components/ProgressStepper';
import LoadingPage from '../components/LoadingPage';

function FollowUpQuestions({ round = 1 }) {
  const navigate = useNavigate();
  const { state, actions } = useUser();
  const [questions, setQuestions] = useState([]);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [responses, setResponses] = useState({});
  const [firstChoices, setFirstChoices] = useState({});  // For Chapter 2 dual selection
  const [secondChoices, setSecondChoices] = useState({}); // For Chapter 2 dual selection
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
  }, [round]);

  const loadQuestions = async () => {
    try {
      setLoading(true);
      
      // Safety check for userId
      if (!state.userInfo?.userId) {
        setError('User information is missing. Please restart the assessment.');
        return;
      }
      
      const questionsData = await apiService.getFollowUpQuestions(state.userInfo.userId, round);
      console.log('Follow-up questions data:', questionsData);
      setQuestions(questionsData);
      actions.setQuestions(`followUp${round}`, questionsData);
      
      // Reset question index when new questions are loaded
      setCurrentQuestionIndex(0);
      
      // Reset response states for new round
      setResponses({});
      if (round === 1) {
        setFirstChoices({});
        setSecondChoices({});
      }
    } catch (error) {
      console.error('Error loading follow-up questions:', error);
      setError('Failed to load personalized questions. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleResponseChange = (event) => {
    const questionId = questions[currentQuestionIndex].QuestionID;
    const response = event.target.value;
    
    setResponses(prev => ({
      ...prev,
      [questionId]: response,
    }));
  };

  const handleChoiceSelect = (choice) => {
    const questionId = questions[currentQuestionIndex].QuestionID;
    
    console.log('DEBUG: Choice select:', { choice, questionId });
    
    if (round === 1) {
      // For Chapter 2 dual selection
      if (!firstChoices[questionId]) {
        console.log('Setting first choice:', choice);
        setFirstChoices(prev => ({
          ...prev,
          [questionId]: choice,
        }));
      } else if (!secondChoices[questionId] && firstChoices[questionId] !== choice) {
        console.log('Setting second choice:', choice);
        setSecondChoices(prev => ({
          ...prev,
          [questionId]: choice,
        }));
      }
    }
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
      
      let formattedResponses;
      
      if (round === 1) {
        // Format Chapter 2 responses (dual choice)
        formattedResponses = Object.keys(firstChoices).map(questionId => ({
          questionId,
          firstChoice: firstChoices[questionId] || null,
          secondChoice: secondChoices[questionId] || null,
          timestamp: new Date().toISOString(),
        }));
      } else {
        // Format Chapter 3 responses (text responses)
        formattedResponses = Object.entries(responses).map(([questionId, response]) => ({
          questionId,
          response,
          timestamp: new Date().toISOString(),
        }));
      }
      
      console.log('Submitting follow-up responses:', formattedResponses);
      
      // Submit responses to backend
      await apiService.submitFollowUpResponses(state.userInfo.userId, formattedResponses, round);
      
      // Update context
      actions.setResponses(`followUp${round}`, formattedResponses);
      
      // Navigate to next phase
      if (round === 1) {
        actions.setCurrentStep(4);
        navigate('/follow-up-2');
      } else {
        actions.setCurrentStep(5);
        navigate('/final-summary');
      }
    } catch (error) {
      console.error('Error submitting follow-up responses:', error);
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
  
  // Check if current question can proceed
  const canProceed = () => {
    if (!currentQuestion) return false;
    
    if (round === 1) {
      // Chapter 2: Need both first and second choices
      const questionId = currentQuestion.QuestionID;
      return firstChoices[questionId] && secondChoices[questionId];
    } else {
      // Chapter 3: Need text response
      const questionId = currentQuestion.QuestionID;
      return responses[questionId] && responses[questionId].trim().length > 0;
    }
  };

  if (loading) {
    return <LoadingPage message={`Loading Chapter ${round + 1} questions...`} />;
  }

  if (error) {
    return (
      <Container maxWidth="md">
        <ProgressStepper activeStep={round + 2} />
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
        <ProgressStepper activeStep={round + 2} />
        <Alert severity="warning" sx={{ mt: 4 }}>
          No questions available for Chapter {round + 1}. Please check your connection and try again.
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
      <ProgressStepper activeStep={round + 2} />
      
      {/* Header */}
      <Card sx={{ mb: 3, borderRadius: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <QuestionAnswerOutlined sx={{ fontSize: 32, color: 'primary.main', mr: 2 }} />
              <Box>
                <Typography variant="h5" sx={{ fontWeight: 600 }}>
                  Chapter {round + 1} - {round === 1 ? 'Dual Choice Assessment' : 'Deep Dive Questions'}
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
                backgroundColor: '#d4af37',
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
                
                <Typography variant="h6" sx={{ mb: 3, color: '#d4af37', textAlign: 'center' }}>
                  {currentQuestion.Prompt || currentQuestion.QuestionText}
                </Typography>

                {round === 1 ? (
                  // Chapter 2: Multiple choice with dual selection
                  <Box>
                    {/* Enhanced Instructions for Chapter 2 */}
                    <Box sx={{ 
                      backgroundColor: '#f5f5dc', 
                      p: 3, 
                      borderRadius: 2,
                      mb: 4,
                      border: '2px solid',
                      borderColor: '#d4af37',
                      boxShadow: '0 4px 12px rgba(212, 175, 55, 0.3)'
                    }}>
                      <Typography variant="body1" sx={{ 
                        color: '#8b4513', 
                        fontWeight: 600,
                        fontSize: '1.1rem',
                        textAlign: 'center'
                      }}>
                        📋 <strong>Instructions:</strong> Select TWO choices - your FIRST most likely reaction, then your SECOND most likely reaction. This reveals which strengths you naturally use in real situations.
                      </Typography>
                    </Box>
                    
                    {/* Options for dual selection */}
                    {['Option1', 'Option2', 'Option3', 'Option4'].map((optionKey, index) => {
                      const optionText = currentQuestion[optionKey];
                      if (!optionText) return null;
                      
                      const questionId = currentQuestion.QuestionID;
                      const isFirstChoice = firstChoices[questionId] === optionText;
                      const isSecondChoice = secondChoices[questionId] === optionText;
                      const isSelected = isFirstChoice || isSecondChoice;
                      
                      return (
                        <Card
                          key={optionKey}
                          sx={{
                            mb: 2,
                            cursor: 'pointer',
                            border: '2px solid',
                            borderColor: isSelected ? '#d4af37' : 'transparent',
                            backgroundColor: isSelected ? 'rgba(212, 175, 55, 0.1)' : 'white',
                            '&:hover': {
                              borderColor: '#d4af37',
                              backgroundColor: 'rgba(212, 175, 55, 0.05)',
                            },
                          }}
                          onClick={() => handleChoiceSelect(optionText)}
                        >
                          <CardContent>
                            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                              <Typography variant="body1" sx={{ flex: 1, color: '#333333' }}>
                                {String.fromCharCode(65 + index)}. {optionText}
                              </Typography>
                              {isFirstChoice && (
                                <Chip
                                  label="1st Choice"
                                  size="small"
                                  sx={{
                                    backgroundColor: '#d4af37',
                                    color: 'white',
                                    fontWeight: 'bold',
                                  }}
                                />
                              )}
                              {isSecondChoice && (
                                <Chip
                                  label="2nd Choice"
                                  size="small"
                                  sx={{
                                    backgroundColor: '#8b4513',
                                    color: 'white',
                                    fontWeight: 'bold',
                                  }}
                                />
                              )}
                            </Box>
                          </CardContent>
                        </Card>
                      );
                    })}
                  </Box>
                ) : (
                  // Chapter 3: Text response
                  <Box>
                    <TextField
                      fullWidth
                      multiline
                      rows={4}
                      placeholder="Share your thoughts and experiences..."
                      value={responses[currentQuestion.QuestionID] || ''}
                      onChange={handleResponseChange}
                      sx={{
                        mb: 3,
                        '& .MuiOutlinedInput-root': {
                          '&:hover fieldset': {
                            borderColor: '#d4af37',
                          },
                          '&.Mui-focused fieldset': {
                            borderColor: '#d4af37',
                          },
                        },
                      }}
                    />
                  </Box>
                )}

                {/* Chapter Information */}
                <Box sx={{ 
                  backgroundColor: '#f5f5dc', 
                  p: 2, 
                  borderRadius: 2,
                  mt: 3,
                  border: '1px solid',
                  borderColor: '#d4af37'
                }}>
                  <Typography variant="body2" sx={{ color: '#8b4513', fontWeight: 500 }}>
                    💡 <strong>Chapter {round + 1}:</strong> {round === 1 ? 
                      'Situational judgment - understand how you naturally respond to workplace scenarios.' : 
                      'Personal reflection - share your experiences and perspectives in detail.'}
                  </Typography>
                </Box>

                {/* Navigation Buttons */}
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 4 }}>
                  <Button
                    variant="outlined"
                    onClick={handlePrevious}
                    disabled={currentQuestionIndex === 0}
                    sx={{ 
                      minWidth: 100,
                      borderColor: '#d4af37',
                      color: '#d4af37',
                      '&:hover': {
                        borderColor: '#8b4513',
                        backgroundColor: 'rgba(212, 175, 55, 0.1)',
                      },
                    }}
                  >
                    Previous
                  </Button>
                  
                  <Button
                    variant="contained"
                    onClick={handleNext}
                    disabled={!canProceed() || submitting}
                    sx={{ 
                      minWidth: 150,
                      backgroundColor: '#d4af37',
                      color: '#0a0a0a',
                      fontWeight: 600,
                      '&:hover': {
                        backgroundColor: '#8b4513',
                      },
                      '&:disabled': {
                        backgroundColor: '#ddd6c7',
                        color: '#8b4513',
                      },
                    }}
                  >
                    {submitting ? 'Submitting...' : 
                     currentQuestionIndex === questions.length - 1 ? 
                       (round === 1 ? 'Proceed to Chapter 3' : 'Complete Assessment') : 'Next Question'}
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

export default FollowUpQuestions;
