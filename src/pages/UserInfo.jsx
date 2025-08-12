import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Typography,
  Card,
  CardContent,
  TextField,
  Button,
  Box,
  FormControlLabel,
  Checkbox,
  Alert,
  InputAdornment,
} from '@mui/material';
import {
  PersonOutlined,
  CakeOutlined,
  WorkOutlined,
  SecurityOutlined,
  EmailOutlined,
  PhoneOutlined,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { useUser } from '../context/UserContext';
import { apiService } from '../services/api';
import ProgressStepper from '../components/ProgressStepper';

function UserInfo() {
  const navigate = useNavigate();
  const { state, actions } = useUser();
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    age: '',
    experience: '',
    phone: '',
    consent: false,
  });
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);

  const handleChange = (field) => (event) => {
    const value = field === 'consent' ? event.target.checked : event.target.value;
    setFormData(prev => ({
      ...prev,
      [field]: value,
    }));
    
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({
        ...prev,
        [field]: '',
      }));
    }
  };

  const validateForm = () => {
    const newErrors = {};
    
    if (!formData.name.trim()) {
      newErrors.name = 'Name is required';
    } else if (formData.name.trim().length < 2) {
      newErrors.name = 'Name must be at least 2 characters';
    }

    if (!formData.email.trim()) {
      newErrors.email = 'Email is required';
    } else if (!/^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/.test(formData.email)) {
      newErrors.email = 'Please enter a valid email address';
    }
    
    if (!formData.age) {
      newErrors.age = 'Age is required';
    } else if (isNaN(formData.age) || formData.age < 18 || formData.age > 100) {
      newErrors.age = 'Please enter a valid age between 18 and 100';
    }
    
    if (!formData.experience) {
      newErrors.experience = 'Years of experience is required';
    } else if (isNaN(formData.experience) || formData.experience < 0 || formData.experience > 50) {
      newErrors.experience = 'Please enter valid years of experience (0-50)';
    } else if (parseInt(formData.experience) > parseInt(formData.age)) {
      newErrors.experience = 'Years of experience cannot be greater than your age';
    }

    if (!formData.phone.trim()) {
      newErrors.phone = 'Phone number is required';
    } else if (!/^\+?[\d\s\-\(\)]{10,15}$/.test(formData.phone.replace(/\s/g, ''))) {
      newErrors.phone = 'Please enter a valid phone number';
    }
    
    if (!formData.consent) {
      newErrors.consent = 'You must agree to data processing to continue';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    
    if (!validateForm()) {
      return;
    }
    
    setLoading(true);
    actions.setLoading(true);
    
    try {
      // Create user in backend
      const userData = {
        name: formData.name.trim(),
        email: formData.email.trim(),
        age: parseInt(formData.age),
        experience: parseInt(formData.experience),
        phone: formData.phone.trim(),
        consent: formData.consent,
      };
      
      const response = await apiService.createUser(userData);
      
      // Update context with user info including generated userId
      actions.setUserInfo({
        ...userData,
        userId: response.userId,
      });
      
      actions.setCurrentStep(1);
      
      // Navigate to assessment
      navigate('/assessment');
    } catch (error) {
      console.error('Error creating user:', error);
      setErrors({
        submit: 'Failed to save your information. Please try again.',
      });
    } finally {
      setLoading(false);
      actions.setLoading(false);
    }
  };

  const containerVariants = {
    hidden: { opacity: 0, x: 50 },
    visible: {
      opacity: 1,
      x: 0,
      transition: { duration: 0.5 },
    },
    exit: {
      opacity: 0,
      x: -50,
      transition: { duration: 0.3 },
    },
  };

  return (
    <Container maxWidth="md">
      <motion.div
        variants={containerVariants}
        initial="hidden"
        animate="visible"
        exit="exit"
      >
        <ProgressStepper activeStep={0} />
        
        <Card sx={{ borderRadius: 3, boxShadow: 3 }}>
          <CardContent sx={{ p: 4 }}>
            <Box textAlign="center" sx={{ mb: 4 }}>
              <PersonOutlined sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
              <Typography variant="h4" component="h1" gutterBottom sx={{ fontWeight: 600 }}>
                Personal Information
              </Typography>
              <Typography variant="body1" color="text.secondary">
                Please provide some basic information to get started with your personalized assessment.
              </Typography>
            </Box>

            {errors.submit && (
              <Alert severity="error" sx={{ mb: 3 }}>
                {errors.submit}
              </Alert>
            )}

            <Box component="form" onSubmit={handleSubmit} noValidate>
              <TextField
                fullWidth
                label="Full Name"
                value={formData.name}
                onChange={handleChange('name')}
                error={!!errors.name}
                helperText={errors.name}
                margin="normal"
                required
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <PersonOutlined color="action" />
                    </InputAdornment>
                  ),
                }}
                sx={{ mb: 3 }}
              />

              <TextField
                fullWidth
                label="Email Address"
                type="email"
                value={formData.email}
                onChange={handleChange('email')}
                error={!!errors.email}
                helperText={errors.email}
                margin="normal"
                required
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <EmailOutlined color="action" />
                    </InputAdornment>
                  ),
                }}
                sx={{ mb: 3 }}
              />

              <TextField
                fullWidth
                label="Age"
                type="number"
                value={formData.age}
                onChange={handleChange('age')}
                error={!!errors.age}
                helperText={errors.age}
                margin="normal"
                required
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <CakeOutlined color="action" />
                    </InputAdornment>
                  ),
                }}
                inputProps={{
                  min: 18,
                  max: 100,
                }}
                sx={{ mb: 3 }}
              />

              <TextField
                fullWidth
                label="Years of Professional Experience"
                type="number"
                value={formData.experience}
                onChange={handleChange('experience')}
                error={!!errors.experience}
                helperText={errors.experience}
                margin="normal"
                required
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <WorkOutlined color="action" />
                    </InputAdornment>
                  ),
                }}
                inputProps={{
                  min: 0,
                  max: 50,
                }}
                sx={{ mb: 3 }}
              />

              <TextField
                fullWidth
                label="Phone Number"
                type="tel"
                value={formData.phone}
                onChange={handleChange('phone')}
                error={!!errors.phone}
                helperText={errors.phone}
                margin="normal"
                required
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <PhoneOutlined color="action" />
                    </InputAdornment>
                  ),
                }}
                sx={{ mb: 3 }}
              />

              <Card sx={{ backgroundColor: 'background.default', mb: 3 }}>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'flex-start', mb: 2 }}>
                    <SecurityOutlined color="primary" sx={{ mr: 2, mt: 0.5 }} />
                    <Box>
                      <Typography variant="h6" gutterBottom>
                        Data Privacy & Consent
                      </Typography>
                      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                        Your data will be securely stored and used only for assessment purposes. 
                        We implement enterprise-grade security measures to protect your privacy.
                      </Typography>
                      <FormControlLabel
                        control={
                          <Checkbox
                            checked={formData.consent}
                            onChange={handleChange('consent')}
                            color="primary"
                          />
                        }
                        label="I agree to data processing and privacy terms"
                        sx={{
                          color: errors.consent ? 'error.main' : 'inherit',
                        }}
                      />
                      {errors.consent && (
                        <Typography variant="caption" color="error" display="block">
                          {errors.consent}
                        </Typography>
                      )}
                    </Box>
                  </Box>
                </CardContent>
              </Card>

              <Box sx={{ display: 'flex', gap: 2, justifyContent: 'space-between' }}>
                <Button
                  variant="outlined"
                  size="large"
                  onClick={() => navigate('/')}
                  sx={{ px: 4 }}
                >
                  Back
                </Button>
                <Button
                  type="submit"
                  variant="contained"
                  size="large"
                  disabled={loading}
                  sx={{
                    px: 4,
                    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                    '&:hover': {
                      background: 'linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%)',
                    },
                  }}
                >
                  {loading ? 'Saving...' : 'Continue to Assessment'}
                </Button>
              </Box>
            </Box>
          </CardContent>
        </Card>
      </motion.div>
    </Container>
  );
}

export default UserInfo;
