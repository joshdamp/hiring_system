import React, { createContext, useContext, useReducer } from 'react';

const UserContext = createContext();

// Initial state
const initialState = {
  userInfo: {
    userId: null,
    name: '',
    age: '',
    experience: '',
    consent: false,
  },
  currentStep: 0,
  responses: {
    initial: [],
    followUp1: [],
    followUp2: [],
  },
  questions: {
    fixed: [],
    followUp1: [],
    followUp2: [],
  },
  summaries: {
    initial: '',
    followUp1: '',
    final: '',
  },
  loading: false,
  error: null,
};

// Action types
const ActionTypes = {
  SET_USER_INFO: 'SET_USER_INFO',
  SET_CURRENT_STEP: 'SET_CURRENT_STEP',
  SET_RESPONSES: 'SET_RESPONSES',
  SET_QUESTIONS: 'SET_QUESTIONS',
  SET_SUMMARY: 'SET_SUMMARY',
  SET_LOADING: 'SET_LOADING',
  SET_ERROR: 'SET_ERROR',
  RESET_STATE: 'RESET_STATE',
  ADD_RESPONSE: 'ADD_RESPONSE',
};

// Reducer function
function userReducer(state, action) {
  switch (action.type) {
    case ActionTypes.SET_USER_INFO:
      return {
        ...state,
        userInfo: { ...state.userInfo, ...action.payload },
      };
    case ActionTypes.SET_CURRENT_STEP:
      return {
        ...state,
        currentStep: action.payload,
      };
    case ActionTypes.SET_RESPONSES:
      return {
        ...state,
        responses: {
          ...state.responses,
          [action.payload.type]: action.payload.responses,
        },
      };
    case ActionTypes.ADD_RESPONSE:
      return {
        ...state,
        responses: {
          ...state.responses,
          [action.payload.type]: [
            ...state.responses[action.payload.type],
            action.payload.response,
          ],
        },
      };
    case ActionTypes.SET_QUESTIONS:
      return {
        ...state,
        questions: {
          ...state.questions,
          [action.payload.type]: action.payload.questions,
        },
      };
    case ActionTypes.SET_SUMMARY:
      return {
        ...state,
        summaries: {
          ...state.summaries,
          [action.payload.type]: action.payload.summary,
        },
      };
    case ActionTypes.SET_LOADING:
      return {
        ...state,
        loading: action.payload,
      };
    case ActionTypes.SET_ERROR:
      return {
        ...state,
        error: action.payload,
      };
    case ActionTypes.RESET_STATE:
      return initialState;
    default:
      return state;
  }
}

// Provider component
export function UserProvider({ children }) {
  const [state, dispatch] = useReducer(userReducer, initialState);

  // Action creators
  const actions = {
    setUserInfo: (userInfo) => {
      dispatch({ type: ActionTypes.SET_USER_INFO, payload: userInfo });
    },
    setCurrentStep: (step) => {
      dispatch({ type: ActionTypes.SET_CURRENT_STEP, payload: step });
    },
    setResponses: (type, responses) => {
      dispatch({ type: ActionTypes.SET_RESPONSES, payload: { type, responses } });
    },
    addResponse: (type, response) => {
      dispatch({ type: ActionTypes.ADD_RESPONSE, payload: { type, response } });
    },
    setQuestions: (type, questions) => {
      dispatch({ type: ActionTypes.SET_QUESTIONS, payload: { type, questions } });
    },
    setSummary: (type, summary) => {
      dispatch({ type: ActionTypes.SET_SUMMARY, payload: { type, summary } });
    },
    setLoading: (loading) => {
      dispatch({ type: ActionTypes.SET_LOADING, payload: loading });
    },
    setError: (error) => {
      dispatch({ type: ActionTypes.SET_ERROR, payload: error });
    },
    resetState: () => {
      dispatch({ type: ActionTypes.RESET_STATE });
    },
  };

  return (
    <UserContext.Provider value={{ state, actions }}>
      {children}
    </UserContext.Provider>
  );
}

// Custom hook to use the context
export function useUser() {
  const context = useContext(UserContext);
  if (context === undefined) {
    throw new Error('useUser must be used within a UserProvider');
  }
  return context;
}

export { ActionTypes };
