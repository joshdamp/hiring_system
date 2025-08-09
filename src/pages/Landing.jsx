import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Typography,
  Button,
  Card,
  CardContent,
  Box,
  Grid,
  Chip,
} from '@mui/material';
import {
  PsychologyOutlined,
  AssessmentOutlined,
  PersonOutlined,
  TrendingUpOutlined,
  SecurityOutlined,
  TimerOutlined,
} from '@mui/icons-material';
import { motion } from 'framer-motion';

function Landing() {
  const navigate = useNavigate();

  const features = [
    {
      icon: <PsychologyOutlined sx={{ fontSize: 40 }} />,
      title: 'AI-Powered Assessment',
      description: 'Advanced psychometric evaluation using machine learning algorithms',
    },
    {
      icon: <PersonOutlined sx={{ fontSize: 40 }} />,
      title: 'Personalized Experience',
      description: 'Adaptive questions tailored to your unique profile and responses',
    },
    {
      icon: <AssessmentOutlined sx={{ fontSize: 40 }} />,
      title: 'Comprehensive Analysis',
      description: 'Detailed insights into 34 key personality and professional traits',
    },
    {
      icon: <SecurityOutlined sx={{ fontSize: 40 }} />,
      title: 'Secure & Private',
      description: 'Your data is protected with enterprise-grade security measures',
    },
    {
      icon: <TimerOutlined sx={{ fontSize: 40 }} />,
      title: 'Quick & Efficient',
      description: 'Complete assessment in 15-20 minutes with instant results',
    },
    {
      icon: <TrendingUpOutlined sx={{ fontSize: 40 }} />,
      title: 'Predictive Insights',
      description: 'Accurate matching with role requirements and team dynamics',
    },
  ];

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        duration: 0.5,
        staggerChildren: 0.1,
      },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: { duration: 0.5 },
    },
  };

  return (
    <Container maxWidth="lg">
      <motion.div
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        {/* Hero Section */}
        <motion.div variants={itemVariants}>
          <Box textAlign="center" sx={{ mb: 8 }}>
            <Typography
              variant="h1"
              component="h1"
              gutterBottom
              sx={{
                fontWeight: 700,
                background: 'linear-gradient(135deg, #d4af37 0%, #f4e4a1 100%)',
                backgroundClip: 'text',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                mb: 3,
                fontFamily: '"Playfair Display", Georgia, serif',
              }}
            >
              Welcome to the Future of Hiring
            </Typography>
            <Typography
              variant="h5"
              color="text.secondary"
              sx={{ mb: 4, maxWidth: '700px', mx: 'auto', fontSize: '1.25rem' }}
            >
              Discover your unique professional profile through our advanced
              psychometric assessment powered by artificial intelligence.
            </Typography>
            <Button
              variant="contained"
              size="large"
              onClick={() => navigate('/user-info')}
              className="btn-primary"
              sx={{
                py: 2,
                px: 4,
                fontSize: '1.1rem',
                fontWeight: 600,
                borderRadius: 3,
                background: 'linear-gradient(135deg, #d4af37 0%, #b8941f 100%)',
                color: 'black',
                textTransform: 'uppercase',
                letterSpacing: '0.5px',
                '&:hover': {
                  background: 'linear-gradient(135deg, #b8941f 0%, #d4af37 100%)',
                  transform: 'translateY(-2px)',
                  boxShadow: '0 4px 20px rgba(212, 175, 55, 0.3)',
                },
              }}
            >
              Start Your Assessment
            </Button>
          </Box>
        </motion.div>

        {/* Features Grid */}
        <motion.div variants={itemVariants}>
          <Typography
            variant="h3"
            component="h2"
            textAlign="center"
            gutterBottom
            sx={{ 
              mb: 6, 
              fontWeight: 600,
              color: '#d4af37',
              fontFamily: '"Playfair Display", Georgia, serif',
            }}
          >
            Why Choose Our Assessment Platform?
          </Typography>
          <Grid container spacing={4} sx={{ mb: 8 }}>
            {features.map((feature, index) => (
              <Grid item xs={12} md={6} lg={4} key={index}>
                <motion.div
                  variants={itemVariants}
                  whileHover={{ y: -5 }}
                  transition={{ duration: 0.2 }}
                >
                  <Card
                    className="modern-card"
                    sx={{
                      height: '100%',
                      borderRadius: 4,
                      background: 'rgba(26, 26, 26, 0.8)',
                      backdropFilter: 'blur(20px)',
                      border: '1px solid rgba(212, 175, 55, 0.2)',
                      transition: 'all 0.3s ease',
                      '&:hover': {
                        borderColor: '#d4af37',
                        boxShadow: '0 4px 20px rgba(212, 175, 55, 0.3)',
                        transform: 'translateY(-4px)',
                      },
                    }}
                  >
                    <CardContent sx={{ p: 3, textAlign: 'center' }}>
                      <Box
                        sx={{
                          color: '#d4af37',
                          mb: 2,
                          display: 'flex',
                          justifyContent: 'center',
                        }}
                      >
                        {feature.icon}
                      </Box>
                      <Typography
                        variant="h6"
                        gutterBottom
                        sx={{ 
                          fontWeight: 600,
                          color: '#ffffff',
                          mb: 2,
                        }}
                      >
                        {feature.title}
                      </Typography>
                      <Typography 
                        variant="body2" 
                        sx={{ 
                          color: '#e8e8e8',
                          lineHeight: 1.6,
                        }}
                      >
                        {feature.description}
                      </Typography>
                    </CardContent>
                  </Card>
                </motion.div>
              </Grid>
            ))}
          </Grid>
        </motion.div>

        {/* Process Overview */}
        <motion.div variants={itemVariants}>
          <Card
            sx={{
              p: 4,
              mb: 6,
              borderRadius: 3,
              background: 'linear-gradient(135deg, rgba(212, 175, 55, 0.05) 0%, rgba(244, 228, 161, 0.05) 100%)',
              border: '1px solid',
              borderColor: '#d4af37',
            }}
          >
            <Typography
              variant="h5"
              component="h3"
              textAlign="center"
              gutterBottom
              sx={{ mb: 4, fontWeight: 600 }}
            >
              Assessment Process
            </Typography>
            <Grid container spacing={3}>
              <Grid item xs={12} sm={6} md={3}>
                <Box textAlign="center">
                  <Typography variant="h6" sx={{ color: '#d4af37' }} gutterBottom>
                    Step 1
                  </Typography>
                  <Typography variant="body2">
                    Provide basic information and consent
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Box textAlign="center">
                  <Typography variant="h6" sx={{ color: '#d4af37' }} gutterBottom>
                    Step 2
                  </Typography>
                  <Typography variant="body2">
                    Complete initial psychometric assessment
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Box textAlign="center">
                  <Typography variant="h6" sx={{ color: '#d4af37' }} gutterBottom>
                    Step 3
                  </Typography>
                  <Typography variant="body2">
                    Answer personalized follow-up questions
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Box textAlign="center">
                  <Typography variant="h6" sx={{ color: '#d4af37' }} gutterBottom>
                    Step 4
                  </Typography>
                  <Typography variant="body2">
                    Receive detailed personality insights
                  </Typography>
                </Box>
              </Grid>
            </Grid>
          </Card>
        </motion.div>
      </motion.div>
    </Container>
  );
}

export default Landing;
