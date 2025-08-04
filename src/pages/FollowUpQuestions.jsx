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
      setQuestions(questionsData);
      actions.setQuestions(`followUp${round}`, questionsData);
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
      const formattedResponses = Object.entries(responses).map(([questionId, response]) => ({
        questionId,
        response,
        timestamp: new Date().toISOString(),
      }));
      
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
  const currentResponse = currentQuestion ? (responses[currentQuestion.QuestionID] || '') : '';
  const allQuestionsAnswered = questions.length > 0 && questions.every(q => responses[q.QuestionID]?.trim());

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
              <Chip
                label={`${Math.round(progress)}% Complete`}
                color="primary"
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
                <Box sx={{ display: 'flex', alignItems: 'flex-start', mb: 4 }}>
                  <QuestionAnswerOutlined 
                    sx={{ fontSize: 24, color: 'primary.main', mr: 2, mt: 1 }} 
                  />
                  <Typography variant="h6" sx={{ flex: 1, fontWeight: 500 }}>
                    {currentQuestion.QuestionText}
                  </Typography>
                </Box>

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
                  <Typography variant="body2" color="text.secondary">
                    💡 <strong>Tip:</strong> Provide specific examples and detailed explanations. 
                    The more thoughtful your response, the more accurate your final profile will be.
                  </Typography>
                </Box>

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
                        disabled={!currentResponse || !currentResponse.trim()}
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
        )}
      </AnimatePresence>

      {/* Quick Navigation */}
      <Card sx={{ mt: 3, borderRadius: 3 }}>
        <CardContent>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            Question Progress
          </Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
            {questions.map((_, index) => (
              <Button
                key={index}
                size="small"
                variant={index === currentQuestionIndex ? 'contained' : 'outlined'}
                color={responses[questions[index]?.QuestionID]?.trim() ? 'success' : 'primary'}
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
            ))}
          </Box>
        </CardContent>
      </Card>
    </Container>
  );
}

export default FollowUpQuestions;
