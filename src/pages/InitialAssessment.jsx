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
  FormControl,
  LinearProgress,
  Alert,
  Chip,
} from '@mui/material';
import {
  PsychologyOutlined,
  QuestionAnswerOutlined,
  TimerOutlined,
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import { useUser } from '../context/UserContext';
import { apiService } from '../services/api';
import ProgressStepper from '../components/ProgressStepper';
import LoadingPage from '../components/LoadingPage';

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
      const questionsData = await apiService.getFixedQuestions();
      
      // Shuffle questions for randomization
      const shuffledQuestions = [...questionsData].sort(() => Math.random() - 0.5);
      
      setQuestions(shuffledQuestions);
      actions.setQuestions('fixed', shuffledQuestions);
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
  const allQuestionsAnswered = questions.every(q => responses[q.QuestionID] !== undefined);

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

  const cardVariants = {
    enter: { opacity: 0, x: 100 },
    center: { opacity: 1, x: 0 },
    exit: { opacity: 0, x: -100 },
  };

  return (
    <Container maxWidth="md">
      <ProgressStepper activeStep={1} />
      
      {/* Header */}
      <Card sx={{ mb: 3, borderRadius: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <PsychologyOutlined sx={{ fontSize: 32, color: 'primary.main', mr: 2 }} />
              <Box>
                <Typography variant="h5" sx={{ fontWeight: 600 }}>
                  Psychometric Assessment
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
                    {currentQuestion.Prompt}
                  </Typography>
                </Box>

                <FormControl component="fieldset" fullWidth>
                  <RadioGroup
                    value={currentResponse || ''}
                    onChange={handleResponseChange}
                    sx={{ mt: 2 }}
                  >
                    <FormControlLabel
                      value="1"
                      control={<Radio />}
                      label={
                        <Typography variant="body1" sx={{ ml: 1 }}>
                          {currentQuestion.Option1}
                        </Typography>
                      }
                      sx={{
                        mb: 2,
                        p: 2,
                        borderRadius: 2,
                        border: '1px solid',
                        borderColor: currentResponse === 1 ? 'primary.main' : 'divider',
                        backgroundColor: currentResponse === 1 ? 'primary.light' : 'transparent',
                        '&:hover': {
                          backgroundColor: 'grey.50',
                        },
                      }}
                    />
                    <FormControlLabel
                      value="2"
                      control={<Radio />}
                      label={
                        <Typography variant="body1" sx={{ ml: 1 }}>
                          {currentQuestion.Option2}
                        </Typography>
                      }
                      sx={{
                        mb: 2,
                        p: 2,
                        borderRadius: 2,
                        border: '1px solid',
                        borderColor: currentResponse === 2 ? 'primary.main' : 'divider',
                        backgroundColor: currentResponse === 2 ? 'primary.light' : 'transparent',
                        '&:hover': {
                          backgroundColor: 'grey.50',
                        },
                      }}
                    />
                    <FormControlLabel
                      value="3"
                      control={<Radio />}
                      label={
                        <Typography variant="body1" sx={{ ml: 1 }}>
                          {currentQuestion.Option3}
                        </Typography>
                      }
                      sx={{
                        mb: 2,
                        p: 2,
                        borderRadius: 2,
                        border: '1px solid',
                        borderColor: currentResponse === 3 ? 'primary.main' : 'divider',
                        backgroundColor: currentResponse === 3 ? 'primary.light' : 'transparent',
                        '&:hover': {
                          backgroundColor: 'grey.50',
                        },
                      }}
                    />
                    <FormControlLabel
                      value="4"
                      control={<Radio />}
                      label={
                        <Typography variant="body1" sx={{ ml: 1 }}>
                          {currentQuestion.Option4}
                        </Typography>
                      }
                      sx={{
                        mb: 2,
                        p: 2,
                        borderRadius: 2,
                        border: '1px solid',
                        borderColor: currentResponse === 4 ? 'primary.main' : 'divider',
                        backgroundColor: currentResponse === 4 ? 'primary.light' : 'transparent',
                        '&:hover': {
                          backgroundColor: 'grey.50',
                        },
                      }}
                    />
                  </RadioGroup>
                </FormControl>

                {/* Navigation Buttons */}
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 4 }}>
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
                        disabled={!currentResponse}
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
                        {submitting ? 'Submitting...' : 'Complete Assessment'}
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
                color={responses[questions[index]?.QuestionID] ? 'success' : 'primary'}
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

export default InitialAssessment;
