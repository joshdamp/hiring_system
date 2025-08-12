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
      // Chapter 2: Dual selection logic
      const currentFirst = firstChoices[questionId];
      const currentSecond = secondChoices[questionId];
      
      console.log('DEBUG: Current choices:', { currentFirst, currentSecond });
      
      if (!currentFirst) {
        // Select first choice
        console.log('DEBUG: Setting first choice:', choice);
        setFirstChoices(prev => ({ ...prev, [questionId]: choice }));
      } else if (!currentSecond && choice !== currentFirst) {
        // Select second choice (different from first)
        console.log('DEBUG: Setting second choice:', choice);
        setSecondChoices(prev => ({ ...prev, [questionId]: choice }));
      } else if (choice === currentFirst) {
        // Clicking first choice again - clear it and move second to first
        console.log('DEBUG: Clearing first choice');
        setFirstChoices(prev => ({ ...prev, [questionId]: currentSecond || null }));
        setSecondChoices(prev => ({ ...prev, [questionId]: null }));
      } else if (choice === currentSecond) {
        // Clicking second choice again - clear it
        console.log('DEBUG: Clearing second choice');
        setSecondChoices(prev => ({ ...prev, [questionId]: null }));
      } else {
        // Selecting a third option - replace second choice
        console.log('DEBUG: Replacing second choice:', choice);
        setSecondChoices(prev => ({ ...prev, [questionId]: choice }));
      }
    } else {
      // Chapter 3: Single selection (existing logic)
      setResponses(prev => ({
        ...prev,
        [questionId]: choice,
      }));
    }
  };

  const handleNext = () => {
    if (currentQuestionIndex < questions.length - 1) {
      setCurrentQuestionIndex(prev => prev + 1);
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
      let formattedResponses;
      
      if (round === 1) {
        // Chapter 2: Format dual-choice responses
        formattedResponses = questions.map(q => {
          const firstChoice = firstChoices[q.QuestionID];
          const secondChoice = secondChoices[q.QuestionID];
          
          // Validate that both choices are made
          if (!firstChoice || !secondChoice) {
            throw new Error(`Please select both choices for question: ${q.Prompt}`);
          }
          
          return {
            questionId: q.QuestionID,
            firstChoice,
            secondChoice,
            timestamp: new Date().toISOString(),
          };
        });
      } else {
        // Chapter 3: Regular text responses
        formattedResponses = Object.entries(responses).map(([questionId, response]) => ({
          questionId,
          response,
          timestamp: new Date().toISOString(),
        }));
      }
      
      // Submit responses to backend
      await apiService.submitFollowUpResponses(
        state.userInfo.userId, 
        formattedResponses, 
        round
      );
      
      // Update context
      actions.setResponses(`followUp${round}`, formattedResponses);
      
      // Navigate based on round
      if (round === 1) {
        actions.setCurrentStep(4);
        navigate('/follow-up-2');
      } else {
        actions.setCurrentStep(5);
        navigate('/final-summary');
      }
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

  const progress = questions.length > 0 ? ((currentQuestionIndex + 1) / questions.length) * 100 : 0;
  const currentQuestion = questions[currentQuestionIndex];
  
  // Get current responses based on round
  let currentResponse;
  if (round === 1) {
    // Chapter 2: Use firstChoices and secondChoices
    currentResponse = {
      firstChoice: firstChoices[currentQuestion?.QuestionID],
      secondChoice: secondChoices[currentQuestion?.QuestionID]
    };
  } else {
    // Chapter 3: Use regular responses
    currentResponse = currentQuestion ? (responses[currentQuestion.QuestionID] || '') : '';
  }
  const allQuestionsAnswered = questions.length > 0 && questions.every(q => {
    if (round === 1) {
      // Chapter 2: Check if both choices are selected
      const firstChoice = firstChoices[q.QuestionID];
      const secondChoice = secondChoices[q.QuestionID];
      return firstChoice && secondChoice && firstChoice !== secondChoice;
    }
    // Chapter 3: Regular text response
    return responses[q.QuestionID]?.trim();
  });

  if (loading) {
    return <LoadingPage message={`Generating personalized questions for round ${round}...`} />;
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

  // Safety check: Don't render if no questions are loaded
  if (!loading && questions.length === 0) {
    return (
      <Container maxWidth="md">
        <Alert severity="warning" sx={{ mt: 4 }}>
          No questions available. Please try again.
          <Button
            variant="outlined"
            size="small"
            onClick={loadQuestions}
            sx={{ ml: 2 }}
          >
            Reload Questions
          </Button>
        </Alert>
      </Container>
    );
  }

  const cardVariants = {
    enter: { opacity: 0, x: 100 },
    center: { opacity: 1, x: 0 },
    exit: { opacity: 0, x: -100 },
  };

  const stepNumber = round === 1 ? 3 : 4;
  const expectedQuestions = round === 1 ? 12 : 4;

  return (
    <Container maxWidth="md">
      <ProgressStepper activeStep={stepNumber} />
      
      {/* Header */}
      <Card sx={{ mb: 3, borderRadius: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <AutoAwesomeOutlined sx={{ fontSize: 32, color: 'primary.main', mr: 2 }} />
              <Box>
                <Typography variant="h5" sx={{ fontWeight: 600 }}>
                  Follow-up Questions - Round {round}
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
              height: 8,
              borderRadius: 4,
              backgroundColor: 'grey.200',
              '& .MuiLinearProgress-bar': {
                borderRadius: 4,
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              },
            }}
          />
        </CardContent>
      </Card>

      {/* Info Card */}
      <Card sx={{ mb: 3, borderRadius: 3, backgroundColor: 'info.light' }}>
        <CardContent>
          <Typography variant="body2" color="info.dark">
            <strong>Personalized Questions:</strong> These questions are specifically generated 
            based on your previous responses to provide deeper insights into your personality and working style.
          </Typography>
        </CardContent>
      </Card>

      {/* Question Card */}
      <AnimatePresence mode="wait">
        {loading ? (
          <Card sx={{ p: 4, borderRadius: 3, textAlign: 'center' }}>
            <CircularProgress size={60} />
            <Typography variant="h6" sx={{ mt: 2 }}>Loading questions...</Typography>
          </Card>
        ) : questions.length === 0 ? (
          <Card sx={{ p: 4, borderRadius: 3, textAlign: 'center' }}>
            <Typography variant="h6" color="error">No questions available</Typography>
            <Typography variant="body2" color="text.secondary">
              Please try refreshing the page or contact support if this persists.
            </Typography>
          </Card>
        ) : currentQuestion ? (
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
                <Box sx={{ display: 'flex', alignItems: 'flex-start', mb: 4 }}>
                  <QuestionAnswerOutlined 
                    sx={{ fontSize: 24, color: 'primary.main', mr: 2, mt: 1 }} 
                  />
                  <Typography variant="h6" sx={{ flex: 1, fontWeight: 500 }}>
                    {currentQuestion.Prompt || currentQuestion.QuestionText || 'Question text not available'}
                  </Typography>
                </Box>

                {/* Render different input types based on question type */}
                {currentQuestion.Type === 'multiple_choice' ? (
                  // Chapter 2: Multiple choice options
                  <Box sx={{ mb: 4 }}>
                    {[currentQuestion.Option1, currentQuestion.Option2, currentQuestion.Option3, currentQuestion.Option4]
                      .filter(option => option) // Remove empty options
                      .map((option, index) => {
                      const choice = String.fromCharCode(65 + index); // A, B, C, D
                      let isFirstChoice = false;
                      let isSecondChoice = false;
                      let isSelected = false;
                      
                      if (round === 1) {
                        // Chapter 2: Dual selection - compare with choice letters
                        isFirstChoice = currentResponse.firstChoice === choice;
                        isSecondChoice = currentResponse.secondChoice === choice;
                        isSelected = isFirstChoice || isSecondChoice;
                      } else {
                        // Chapter 3: Single selection - compare with choice letters
                        isSelected = currentResponse === choice;
                      }
                      
                      return (
                        <Card 
                          key={choice}
                          sx={{ 
                            mb: 2, 
                            cursor: 'pointer',
                            border: isSelected ? '2px solid' : '2px solid',
                            borderColor: isSelected ? (isFirstChoice ? 'success.main' : 'primary.main') : '#DAA520',
                            backgroundColor: isSelected ? (isFirstChoice ? 'success.50' : 'primary.50') : 'rgba(26, 35, 126, 0.02)',
                            transition: 'all 0.2s ease',
                            '&:hover': {
                              borderColor: isSelected ? (isFirstChoice ? 'success.main' : 'primary.main') : '#DAA520',
                              backgroundColor: isSelected ? (isFirstChoice ? 'success.100' : 'primary.100') : 'rgba(26, 35, 126, 0.05)',
                            }
                          }}
                          onClick={() => handleChoiceSelect(choice)}
                        >
                          <CardContent sx={{ py: 2 }}>
                            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                                <Typography 
                                  variant="h6" 
                                  sx={{ 
                                    minWidth: 30,
                                    color: isSelected ? (isFirstChoice ? 'success.main' : 'primary.main') : 'text.secondary',
                                    fontWeight: isSelected ? 600 : 400
                                  }}
                                >
                                  {choice}.
                                </Typography>
                                <Typography 
                                  variant="body1" 
                                  sx={{ 
                                    ml: 2,
                                    color: isSelected ? (isFirstChoice ? 'success.dark' : 'primary.dark') : 'text.primary',
                                    fontWeight: isSelected ? 500 : 400
                                  }}
                                >
                                  {option}
                                </Typography>
                              </Box>
                              {round === 1 && isSelected && (
                                <Chip
                                  label={isFirstChoice ? "1st Choice" : "2nd Choice"}
                                  color={isFirstChoice ? "success" : "primary"}
                                  size="small"
                                  variant="filled"
                                />
                              )}
                            </Box>
                          </CardContent>
                        </Card>
                      );
                    })}
                    
                    
                    <Box sx={{ 
                      backgroundColor: 'grey.50', 
                      p: 2, 
                      borderRadius: 2,
                      mt: 3,
                    }}>
                      <Typography variant="body2" sx={{ color: '#333333' }}>
                        💡 <strong>Chapter {round + 1}:</strong> {round === 1 ? 
                          'Focus on your natural instincts - what would you actually do first, then second?' : 
                          'Provide specific examples and detailed explanations. The more thoughtful your response, the more accurate your final profile will be.'
                        }
                      </Typography>
                    </Box>
                  </Box>
                ) : (
                  // Chapter 3: Open-ended text response
                  <>
                    <TextField
                      fullWidth
                      multiline
                      rows={4}
                      value={currentResponse}
                      onChange={handleResponseChange}
                      placeholder="Please provide a detailed response..."
                      variant="outlined"
                      sx={{
                        mb: 4,
                        '& .MuiOutlinedInput-root': {
                          borderRadius: 2,
                        },
                      }}
                    />

                    <Box sx={{ 
                      backgroundColor: 'grey.50', 
                      p: 2, 
                      borderRadius: 2,
                      mb: 4,
                    }}>
                      <Typography variant="body2" sx={{ color: '#333333' }}>
                        💡 <strong>Chapter {round + 1}:</strong> Provide specific examples and detailed explanations. 
                        The more thoughtful your response, the more accurate your final profile will be.
                      </Typography>
                    </Box>
                  </>
                )}

                {/* Navigation Buttons */}
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Button
                    variant="outlined"
                    onClick={handlePrevious}
                    disabled={currentQuestionIndex === 0}
                    sx={{ px: 3 }}
                  >
                    Previous
                  </Button>
                  
                  <Box sx={{ display: 'flex', gap: 2 }}>
                    {currentQuestionIndex < questions.length - 1 ? (
                      <Button
                        variant="contained"
                        onClick={handleNext}
                        disabled={
                          round === 1 
                            ? !currentResponse.firstChoice || !currentResponse.secondChoice
                            : currentQuestion?.Type === 'open_ended' 
                              ? !currentResponse || !currentResponse.trim()
                              : !currentResponse
                        }
                        sx={{
                          px: 3,
                          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                        }}
                      >
                        Next
                      </Button>
                    ) : (
                      <Button
                        variant="contained"
                        onClick={handleSubmit}
                        disabled={!allQuestionsAnswered || submitting}
                        sx={{
                          px: 3,
                          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                        }}
                      >
                        {submitting 
                          ? 'Submitting...' 
                          : round === 1 
                            ? 'Continue to Final Round' 
                            : 'Complete Assessment'
                        }
                      </Button>
                    )}
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </motion.div>
        ) : (
          <Card sx={{ p: 4, borderRadius: 3, textAlign: 'center' }}>
            <Typography variant="h6" color="warning.main">Question not found</Typography>
            <Typography variant="body2" color="text.secondary">
              Current question index: {currentQuestionIndex}, Total questions: {questions.length}
            </Typography>
          </Card>
        )}
      </AnimatePresence>

      {/* Quick Navigation */}
      <Card sx={{ mt: 3, borderRadius: 3 }}>
        <CardContent>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            Question Progress
          </Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
            {questions.map((question, index) => {
              const response = responses[question?.QuestionID];
              const isAnswered = response && (
                question?.QuestionType === 'chapter_2_situational' 
                  ? response.trim() 
                  : response.trim()
              );
              
              return (
                <Button
                  key={index}
                  size="small"
                  variant={index === currentQuestionIndex ? 'contained' : 'outlined'}
                  color={isAnswered ? 'success' : 'primary'}
                  onClick={() => setCurrentQuestionIndex(index)}
                  sx={{
                    minWidth: 36,
                    width: 36,
                    height: 36,
                    p: 0,
                  }}
                >
                  {index + 1}
                </Button>
              );
            })}
          </Box>
        </CardContent>
      </Card>
    </Container>
  );
}

export default FollowUpQuestions;
