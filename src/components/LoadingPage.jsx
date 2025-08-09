import React from 'react';
import { Box, CircularProgress, Typography } from '@mui/material';
import { motion } from 'framer-motion';

function LoadingPage({ message = "Processing your assessment..." }) {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '60vh',
        gap: '2rem',
      }}
    >
      <motion.div
        animate={{ rotate: 360 }}
        transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
      >
        <CircularProgress size={60} thickness={4} />
      </motion.div>
      
      <Box textAlign="center">
        <Typography variant="h6" color="text.primary" gutterBottom>
          {message}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          This will only take a moment...
        </Typography>
      </Box>
    </motion.div>
  );
}

export default LoadingPage;
