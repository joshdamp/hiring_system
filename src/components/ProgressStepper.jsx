import React from 'react';
import { Stepper, Step, StepLabel, Box } from '@mui/material';
import { styled } from '@mui/material/styles';

const CustomStepper = styled(Stepper)(({ theme }) => ({
  background: 'rgba(26, 26, 26, 0.6)',
  backdropFilter: 'blur(10px)',
  borderRadius: '16px',
  padding: '24px',
  border: '1px solid rgba(212, 175, 55, 0.2)',
  '& .MuiStepConnector-root': {
    top: 22,
    '& .MuiStepConnector-line': {
      borderColor: 'rgba(212, 175, 55, 0.3)',
      borderTopWidth: 2,
    },
  },
  '& .MuiStepConnector-active .MuiStepConnector-line': {
    borderColor: '#d4af37',
  },
  '& .MuiStepConnector-completed .MuiStepConnector-line': {
    borderColor: '#d4af37',
  },
  '& .MuiStepLabel-root .Mui-completed': {
    color: '#d4af37',
  },
  '& .MuiStepLabel-root .Mui-active': {
    color: '#d4af37',
  },
  '& .MuiStepLabel-label': {
    color: '#ffffff',
    fontWeight: 500,
    fontSize: '0.9rem',
    '&.Mui-completed': {
      color: '#d4af37',
      fontWeight: 600,
    },
    '&.Mui-active': {
      color: '#d4af37',
      fontWeight: 600,
    },
  },
  '& .MuiStepIcon-root': {
    color: 'rgba(255, 255, 255, 0.3)',
    '&.Mui-active': {
      color: '#d4af37',
    },
    '&.Mui-completed': {
      color: '#d4af37',
    },
  },
}));

const steps = [
  'Personal Information',
  'Initial Assessment', 
  'Summary Review',
  'Follow-up Questions',
  'Final Assessment',
  'Results'
];

function ProgressStepper({ activeStep }) {
  // Ensure activeStep is within valid bounds and fix the overflow issue
  const validStep = Math.min(Math.max(0, activeStep), steps.length - 1);
  
  return (
    <Box sx={{ width: '100%', mb: 4 }}>
      <CustomStepper activeStep={validStep} alternativeLabel>
        {steps.map((label) => (
          <Step key={label}>
            <StepLabel>{label}</StepLabel>
          </Step>
        ))}
      </CustomStepper>
    </Box>
  );
}

export default ProgressStepper;
