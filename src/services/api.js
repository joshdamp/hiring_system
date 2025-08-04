import axios from 'axios';

// Configure axios instance
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add any auth tokens or other headers here
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // Handle global errors here
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

// API endpoints
export const apiService = {
  // User management
  createUser: async (userData) => {
    const response = await api.post('/users', userData);
    return response.data;
  },

  // Questions
  getFixedQuestions: async () => {
    const response = await api.get('/questions/fixed');
    return response.data;
  },

  getFollowUpQuestions: async (userId, round) => {
    const response = await api.post(`/questions/follow-up/${round}`, { userId });
    return response.data;
  },

  // Responses
  submitInitialResponses: async (userId, responses) => {
    const response = await api.post('/responses/initial', { userId, responses });
    return response.data;
  },

  submitFollowUpResponses: async (userId, responses, round) => {
    const response = await api.post(`/responses/follow-up/${round}`, { 
      userId, 
      responses 
    });
    return response.data;
  },

  // Summaries
  getInitialSummary: async (userId) => {
    const response = await api.get(`/summary/initial/${userId}`);
    return response.data;
  },

  getFollowUpSummary: async (userId, round) => {
    const response = await api.get(`/summary/follow-up/${userId}/${round}`);
    return response.data;
  },

  getFinalSummary: async (userId) => {
    const response = await api.get(`/summary/final/${userId}`);
    return response.data;
  },

  // Final results
  getFinalResults: async (userId) => {
    const response = await api.get(`/results/${userId}`);
    return response.data;
  },

  // Health check
  healthCheck: async () => {
    const response = await api.get('/health');
    return response.data;
  },
};

export default api;
