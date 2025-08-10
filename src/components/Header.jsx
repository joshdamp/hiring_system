import React from 'react';
import { AppBar, Toolbar, Typography, Box } from '@mui/material';
import { PsychologyOutlined } from '@mui/icons-material';
import { motion } from 'framer-motion';

function Header() {
  return (
    <AppBar 
      position="static" 
      elevation={0}
      sx={{
        background: 'linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 100%)',
        borderBottom: '1px solid rgba(212, 175, 55, 0.2)',
        backdropFilter: 'blur(20px)',
      }}
    >
      <Toolbar sx={{ justifyContent: 'center', py: 2 }}>
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          style={{ display: 'flex', alignItems: 'center', gap: '16px' }}
        >
          <PsychologyOutlined sx={{ fontSize: 36, color: '#d4af37' }} />
          <Box>
            <Typography 
              variant="h5" 
              component="h1" 
              sx={{ 
                fontWeight: 700, 
                color: '#ffffff',
                letterSpacing: '-0.5px',
                fontFamily: '"Playfair Display", Georgia, serif',
                background: 'linear-gradient(135deg, #d4af37 0%, #f4e4a1 100%)',
                backgroundClip: 'text',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
              }}
            >
              Automated Hiring System
            </Typography>
            <Typography 
              variant="body2" 
              sx={{ 
                color: 'rgba(255, 255, 255, 0.7)',
                fontWeight: 400,
                textAlign: 'center',
                fontSize: '0.9rem',
              }}
            >
              Professional Talent Assessment
            </Typography>
          </Box>
        </motion.div>
      </Toolbar>
    </AppBar>
  );
}

export default Header;
