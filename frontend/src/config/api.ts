/**
 * API Configuration
 * Centralized configuration for all API endpoints to prevent port/URL issues
 */

// Base Configuration
export const API_CONFIG = {
  // Development Configuration
  DEV: {
    BASE_URL: 'http://localhost:5007',
    FRONTEND_URL: 'http://localhost:3000',
  },
  
  // Production Configuration (when deployed)
  PROD: {
    BASE_URL: process.env.REACT_APP_API_URL || 'https://your-domain.com/api',
    FRONTEND_URL: process.env.REACT_APP_FRONTEND_URL || 'https://your-domain.com',
  }
};

// Current Environment
const isDevelopment = process.env.NODE_ENV === 'development';
const currentConfig = isDevelopment ? API_CONFIG.DEV : API_CONFIG.PROD;

export const BASE_URL = currentConfig.BASE_URL;

// API Endpoints
export const API_ENDPOINTS = {
  // Strategy Management
  STRATEGIES: {
    LIST: '/api/strategies',
    UPLOAD: '/api/strategies/upload',
    DELETE: (id: string) => `/api/strategies/${id}`,
    PROFILE: (id: string) => `/api/strategies/${id}/profile`,
  },
  
  // AI Conversion
  CONVERSION: {
    HEALTH: '/api/intelligent-conversion/health',
    WORKING: '/api/intelligent-conversion/convert/working',
    HYE: '/api/intelligent-conversion/convert/hye',
    STRATEGY: (id: string) => `/api/intelligent-conversion/convert/strategy/${id}`,
    TEST: '/api/intelligent-conversion/test-conversion',
    INDICATORS: '/api/intelligent-conversion/indicators',
  },
  
  // Pine Script Conversion
  PINE: {
    CONVERT: '/api/convert-pine',
  },
  
  // Backtesting
  BACKTEST: {
    RUN: '/api/backtests/run',
    REAL: '/api/real-backtest/convert-and-backtest',
  },
  
  // Market Data
  MARKET: {
    OVERVIEW: '/api/market/overview',
  },
  
  // Parameters
  PARAMETERS: {
    STRATEGY: (id: string) => `/api/parameters/strategy/${id}`,
  },
  
  // Data Providers
  DATA: {
    BINANCE_SYMBOLS: '/api/data/binance/symbols',
    BINANCE_KLINES: '/api/data/binance/klines',
  }
};

// Helper Functions
export const getFullUrl = (endpoint: string): string => {
  return `${BASE_URL}${endpoint}`;
};

export const buildApiUrl = (endpointPath: string): string => {
  return getFullUrl(endpointPath);
};

// API Request Headers
export const API_HEADERS = {
  'Content-Type': 'application/json',
  'Accept': 'application/json',
};

// Timeout Configuration
export const API_TIMEOUT = 30000; // 30 seconds

// Validated Endpoints (from test suite)
export const VALIDATED_ENDPOINTS = {
  // These endpoints have been tested and verified as working
  WORKING: [
    '/api/intelligent-conversion/health',
    '/api/strategies', 
    '/api/market/overview',
    '/api/intelligent-conversion/convert/working',
    '/api/intelligent-conversion/convert/hye',
    '/api/real-backtest/convert-and-backtest',
    '/api/backtests/run',
    '/api/intelligent-conversion/indicators'
  ],
  
  // These endpoints need attention
  NEEDS_WORK: [
    '/api/data/binance/symbols'  // Returns 404
  ]
};

// Export configuration summary
export const CONFIG_SUMMARY = {
  baseUrl: BASE_URL,
  environment: isDevelopment ? 'development' : 'production',
  totalEndpoints: Object.keys(API_ENDPOINTS).reduce((total, category) => {
    const categoryEndpoints = API_ENDPOINTS[category as keyof typeof API_ENDPOINTS];
    return total + Object.keys(categoryEndpoints).length;
  }, 0),
  validatedEndpoints: VALIDATED_ENDPOINTS.WORKING.length,
  lastTested: new Date().toISOString(),
};

export default {
  API_CONFIG,
  BASE_URL,
  API_ENDPOINTS,
  getFullUrl,
  buildApiUrl,
  API_HEADERS,
  API_TIMEOUT,
  VALIDATED_ENDPOINTS,
  CONFIG_SUMMARY
};