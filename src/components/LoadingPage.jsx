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
        <CircularProgress 
          size={60} 
          thickness={4}
          sx={{
            color: '#d4af37',
            '& .MuiCircularProgress-circle': {
              strokeLinecap: 'round',
            },
          }}
        />
      </motion.div>
      
      <Box textAlign="center" className="modern-card" sx={{ p: 4, maxWidth: 400 }}>
        <Typography 
          variant="h6" 
          gutterBottom
          sx={{ 
            color: '#ffffff',
            fontWeight: 600,
            mb: 2,
          }}
        >
          {message}
        </Typography>
        <Typography 
          variant="body2" 
          sx={{ 
            color: 'rgba(255, 255, 255, 0.7)',
            fontSize: '1rem',
            lineHeight: 1.6,
          }}
        >
          This will only take a moment...
        </Typography>
      </Box>
    </motion.div>
  );
}

export default LoadingPage;
