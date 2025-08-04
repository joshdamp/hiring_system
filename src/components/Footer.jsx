import React from 'react';
import { Box, Typography, Container, Grid } from '@mui/material';

function Footer() {
  return (
    <Box
      component="footer"
      sx={{
        py: 3,
        px: 0,
        mt: 'auto',
        background: 'linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 100%)',
        borderTop: '2px solid #d4af37',
        width: '100%',
      }}
    >
      <Container maxWidth={false} sx={{ px: 4 }}>
        <Grid container spacing={3} alignItems="center">
          <Grid item xs={12} md={4}>
            <Typography 
              variant="body2" 
              sx={{ 
                color: '#d4af37',
                fontWeight: 600,
                fontSize: '0.9rem',
              }}
            >
              🏆 Premium Assessment Platform
            </Typography>
          </Grid>
          <Grid item xs={12} md={4}>
            <Typography 
              variant="body2" 
              align="center"
              sx={{ 
                color: 'rgba(255, 255, 255, 0.8)',
                fontWeight: 400,
                fontSize: '0.9rem',
              }}
            >
              © 2025 Automated Hiring System. All rights reserved.
            </Typography>
          </Grid>
          <Grid item xs={12} md={4}>
            <Typography 
              variant="body2" 
              align="right"
              sx={{ 
                color: '#d4af37',
                fontWeight: 500,
                fontSize: '0.9rem',
              }}
            >
              Powered by AI & Data Science ⚡
            </Typography>
          </Grid>
        </Grid>
      </Container>
    </Box>
  );
}

export default Footer;
