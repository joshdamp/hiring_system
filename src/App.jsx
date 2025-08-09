// Updated version 1.0.1 - Force deployment trigger
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { motion, AnimatePresence } from 'framer-motion';

// Components
import Header from './components/Header';
import Footer from './components/Footer';
import Landing from './pages/Landing';
import UserInfo from './pages/UserInfo';
import InitialAssessment from './pages/InitialAssessment';
import Summary from './pages/Summary';
import FollowUpQuestions from './pages/FollowUpQuestions';
import FinalSummary from './pages/FinalSummary';
import LoadingPage from './components/LoadingPage';

// Context
import { UserProvider } from './context/UserContext';

// Modern Black/Gold/White Theme
const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#d4af37',
      light: '#f4e4a1',
      dark: '#b8941f',
      contrastText: '#0a0a0a',
    },
    secondary: {
      main: '#1a1a1a',
      light: '#2a2a2a',
      dark: '#0a0a0a',
      contrastText: '#ffffff',
    },
    background: {
      default: '#0a0a0a',
      paper: 'rgba(26, 26, 26, 0.8)',
    },
    text: {
      primary: '#ffffff',
      secondary: '#e8e8e8',
    },
    success: {
      main: '#d4af37',
    },
    error: {
      main: '#ff6b6b',
    },
    warning: {
      main: '#f59e0b',
    },
    info: {
      main: '#d4af37',
    },
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontSize: 'clamp(2.5rem, 5vw, 4rem)',
      fontWeight: 700,
      lineHeight: 1.2,
      fontFamily: '"Playfair Display", Georgia, serif',
    },
    h2: {
      fontSize: 'clamp(2rem, 4vw, 3rem)',
      fontWeight: 600,
      lineHeight: 1.2,
      fontFamily: '"Playfair Display", Georgia, serif',
    },
    h3: {
      fontSize: 'clamp(1.5rem, 3vw, 2rem)',
      fontWeight: 600,
      lineHeight: 1.2,
      fontFamily: '"Playfair Display", Georgia, serif',
    },
    h4: {
      fontSize: '1.25rem',
      fontWeight: 600,
      lineHeight: 1.4,
    },
    body1: {
      fontSize: '1.1rem',
      lineHeight: 1.7,
    },
    body2: {
      fontSize: '1rem',
      lineHeight: 1.6,
    },
  },
  shape: {
    borderRadius: 16,
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'uppercase',
          borderRadius: 12,
          padding: '16px 32px',
          fontSize: '1rem',
          fontWeight: 600,
          letterSpacing: '0.5px',
          boxShadow: 'none',
          '&:hover': {
            boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
          },
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          background: 'rgba(26, 26, 26, 0.8)',
          backdropFilter: 'blur(20px)',
          border: '1px solid rgba(212, 175, 55, 0.2)',
          borderRadius: 16,
          boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
          '&:hover': {
            transform: 'translateY(-4px)',
            boxShadow: '0 4px 20px rgba(212, 175, 55, 0.3)',
            borderColor: '#d4af37',
          },
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            borderRadius: 12,
            backgroundColor: 'rgba(42, 42, 42, 0.8)',
            '& fieldset': {
              borderColor: 'rgba(212, 175, 55, 0.3)',
            },
            '&:hover fieldset': {
              borderColor: 'rgba(212, 175, 55, 0.5)',
            },
            '&.Mui-focused fieldset': {
              borderColor: '#d4af37',
            },
          },
          '& .MuiInputLabel-root': {
            color: 'rgba(255, 255, 255, 0.7)',
          },
          '& .MuiInputBase-input': {
            color: '#ffffff',
          },
        },
      },
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <UserProvider>
        <Router>
          <div className="app-container">
            <Header />
            <main className="main-content">
              <AnimatePresence mode="wait">
                <Routes>
                  <Route path="/" element={<Landing />} />
                  <Route path="/user-info" element={<UserInfo />} />
                  <Route path="/assessment" element={<InitialAssessment />} />
                  <Route path="/summary" element={<Summary />} />
                  <Route path="/follow-up-1" element={<FollowUpQuestions round={1} />} />
                  <Route path="/follow-up-2" element={<FollowUpQuestions round={2} />} />
                  <Route path="/final-summary" element={<FinalSummary />} />
                  <Route path="/loading" element={<LoadingPage />} />
                </Routes>
              </AnimatePresence>
            </main>
            <Footer />
          </div>
        </Router>
      </UserProvider>
    </ThemeProvider>
  );
}

export default App;
