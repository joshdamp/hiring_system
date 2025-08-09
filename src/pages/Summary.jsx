import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Typography,
  Card,
  CardContent,
  Button,
  Box,
  Alert,
  Chip,
  Divider,
} from '@mui/material';
import {
  AssessmentOutlined,
  PersonOutlined,
  TrendingUpOutlined,
  EmojiEventsOutlined,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { useUser } from '../context/UserContext';
import { apiService } from '../services/api';
import ProgressStepper from '../components/ProgressStepper';
import LoadingPage from '../components/LoadingPage';

function Summary() {
  const navigate = useNavigate();
  const { state, actions } = useUser();
  const [summary, setSummary] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [proceeding, setProceeding] = useState(false);

  useEffect(() => {
    loadSummary();
  }, []);

  const loadSummary = async () => {
    try {
      setLoading(true);
      const summaryData = await apiService.getInitialSummary(state.userInfo.userId);
      setSummary(summaryData.summary);
      actions.setSummary('initial', summaryData.summary);
    } catch (error) {
      console.error('Error loading summary:', error);
      setError('Failed to generate your personality summary. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleProceed = async () => {
    try {
      setProceeding(true);
      actions.setCurrentStep(3);
      navigate('/follow-up-1');
    } catch (error) {
      console.error('Error proceeding:', error);
      setError('Failed to proceed. Please try again.');
    } finally {
      setProceeding(false);
    }
  };

  const handleSaveAndExit = async () => {
    try {
      // Save current session state
      // This could involve saving to localStorage or making an API call
      navigate('/');
    } catch (error) {
      console.error('Error saving session:', error);
    }
  };

  if (loading) {
    return <LoadingPage message="Analyzing your responses and generating insights..." />;
  }

  if (error) {
    return (
      <Container maxWidth="md">
        <ProgressStepper activeStep={2} />
        <Alert severity="error" sx={{ mt: 4 }}>
          {error}
          <Button
            variant="outlined"
            size="small"
            onClick={loadSummary}
            sx={{ ml: 2 }}
          >
            Retry
          </Button>
        </Alert>
      </Container>
    );
  }

  const containerVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: { duration: 0.5, staggerChildren: 0.1 },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 },
  };

  return (
    <Container maxWidth="md">
      <motion.div
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        <ProgressStepper activeStep={2} />
        
        {/* Header */}
        <motion.div variants={itemVariants}>
          <Card sx={{ mb: 3, borderRadius: 3, background: 'linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%)' }}>
            <CardContent sx={{ textAlign: 'center', py: 4 }}>
              <EmojiEventsOutlined sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
              <Typography variant="h4" gutterBottom sx={{ fontWeight: 600 }}>
                Initial Assessment Complete!
              </Typography>
              <Typography variant="body1" color="text.secondary">
                Based on your responses, we've created your initial personality profile.
              </Typography>
            </CardContent>
          </Card>
        </motion.div>

        {/* Personality Summary */}
        <motion.div variants={itemVariants}>
          <Card sx={{ mb: 4, borderRadius: 3, boxShadow: 3 }}>
            <CardContent sx={{ p: 4 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
                <AssessmentOutlined sx={{ fontSize: 24, color: 'primary.main', mr: 2 }} />
                <Typography variant="h6" sx={{ fontWeight: 600 }}>
                  Your Personality Profile
                </Typography>
              </Box>
              
              <Typography 
                variant="body1" 
                sx={{ 
                  lineHeight: 1.8,
                  fontSize: '1.1rem',
                  color: 'text.primary',
                  mb: 3,
                }}
              >
                {summary || "You demonstrate a balanced approach to challenges and show strong analytical thinking. Your responses indicate someone who values both independence and collaboration, with a natural inclination toward problem-solving. You tend to be methodical in your approach while remaining adaptable to changing circumstances."}
              </Typography>

              <Divider sx={{ my: 3 }} />

              <Box sx={{ 
                backgroundColor: 'info.light', 
                p: 3, 
                borderRadius: 2,
                border: '1px solid',
                borderColor: 'info.main',
              }}>
                <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
                  <TrendingUpOutlined sx={{ mr: 1 }} />
                  What's Next?
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  To create a more detailed and accurate profile, we'll ask you some personalized 
                  follow-up questions based on your initial responses. This will help us understand 
                  your unique strengths and working style even better.
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </motion.div>

        {/* Action Buttons */}
        <motion.div variants={itemVariants}>
          <Card sx={{ borderRadius: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                Ready to proceed to follow-up questions?
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                The next phase will ask 12 personalized questions to refine your profile further.
                This should take about 5-7 minutes.
              </Typography>
              
              <Box sx={{ display: 'flex', gap: 2, justifyContent: 'space-between' }}>
                <Button
                  variant="outlined"
                  size="large"
                  onClick={handleSaveAndExit}
                  sx={{ px: 4 }}
                >
                  Save & Exit
                </Button>
                
                <Button
                  variant="contained"
                  size="large"
                  onClick={handleProceed}
                  disabled={proceeding}
                  sx={{
                    px: 4,
                    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                    '&:hover': {
                      background: 'linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%)',
                    },
                  }}
                >
                  {proceeding ? 'Preparing Questions...' : 'Continue to Follow-up Questions'}
                </Button>
              </Box>
            </CardContent>
          </Card>
        </motion.div>
      </motion.div>
    </Container>
  );
}

export default Summary;
