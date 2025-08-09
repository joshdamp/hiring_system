import React from 'react';
import { Stepper, Step, StepLabel, Box } from '@mui/material';
import { styled } from '@mui/material/styles';

const CustomStepper = styled(Stepper)(({ theme }) => ({
  '& .MuiStepLabel-root .Mui-completed': {
    color: theme.palette.primary.main,
  },
  '& .MuiStepLabel-root .Mui-active': {
    color: theme.palette.primary.main,
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
  // Ensure activeStep is within valid bounds
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
