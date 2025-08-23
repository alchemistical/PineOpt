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

// API Endpoints - Epic 7: API Architecture Rationalization
export const API_ENDPOINTS = {
  // Epic 7 - Strategy Management (Consolidated)
  STRATEGIES: {
    LIST: '/api/v1/strategies/list',
    CREATE: '/api/v1/strategies',
    GET: (id: string) => `/api/v1/strategies/${id}`,
    UPDATE: (id: string) => `/api/v1/strategies/${id}`,
    DELETE: (id: string) => `/api/v1/strategies/${id}`,
    PARAMETERS: (id: string) => `/api/v1/strategies/${id}/parameters`,
    VALIDATE: (id: string) => `/api/v1/strategies/${id}/validate`,
    PROFILE: (id: string) => `/api/v1/strategies/${id}/profile`,
    STATS: '/api/v1/strategies/stats',
    
    // Legacy endpoints (will be deprecated)
    UPLOAD: '/api/strategies/upload',
  },
  
  // Epic 7 - Market Data (Consolidated)
  MARKET: {
    OVERVIEW: '/api/v1/market/overview',
    SYMBOLS: '/api/v1/market/symbols',
    TICKERS: '/api/v1/market/tickers',
    TICKER: (symbol: string) => `/api/v1/market/ticker/${symbol}`,
    OHLC: (symbol: string) => `/api/v1/market/ohlc/${symbol}`,
    STATUS: '/api/v1/market/status',
    
    // Futures endpoints
    FUTURES_PAIRS: '/api/v1/market/futures/pairs',
    FUTURES_SEARCH: '/api/v1/market/futures/search',
  },
  
  // Epic 7 - Health Check (Consolidated)
  HEALTH: {
    BASIC: '/api/health',
    DETAILED: '/api/v1/health/detailed',
    METRICS: '/api/v1/health/metrics',
  },
  
  // Legacy endpoints (Sprint 2 will consolidate these)
  CONVERSION: {
    HEALTH: '/api/intelligent-conversion/health',
    WORKING: '/api/intelligent-conversion/convert/working',
    HYE: '/api/intelligent-conversion/convert/hye',
    STRATEGY: (id: string) => `/api/intelligent-conversion/convert/strategy/${id}`,
    TEST: '/api/intelligent-conversion/test-conversion',
    INDICATORS: '/api/intelligent-conversion/indicators',
  },
  
  // Pine Script Conversion (Sprint 2 consolidation target)
  PINE: {
    CONVERT: '/api/convert-pine',
  },
  
  // Backtesting (Sprint 2 consolidation target) 
  BACKTEST: {
    RUN: '/api/backtests/run',
    REAL: '/api/real-backtest/convert-and-backtest',
  },
  
  // Parameters (Sprint 2 consolidation target)
  PARAMETERS: {
    STRATEGY: (id: string) => `/api/parameters/strategy/${id}`,
  },
  
  // Data Providers (Sprint 2 consolidation target)
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

// Validated Endpoints - Epic 7 Sprint 1
export const VALIDATED_ENDPOINTS = {
  // Epic 7 Sprint 1 - CONSOLIDATED AND TESTED ✅
  EPIC7_WORKING: [
    '/api/health',                          // Basic health check
    '/api/v1/health/',                      // Epic 7 health blueprint
    '/api/v1/health/detailed',              // Detailed system health
    '/api/v1/market/',                      // Market data info
    '/api/v1/market/overview',              // Live market overview
    '/api/v1/market/symbols',               // Trading symbols
    '/api/v1/market/tickers',               // Market tickers
    '/api/v1/market/ticker/BTC',            // Individual ticker
    '/api/v1/market/status',                // Market status
    '/api/v1/strategies/',                  // Strategy info
    '/api/v1/strategies/list',              // Strategy listing
    '/api/v1/strategies/stats',             // Strategy statistics
  ],
  
  // Legacy endpoints still working
  LEGACY_WORKING: [
    '/api/intelligent-conversion/health',
    '/api/strategies', 
    '/api/market/overview',
    '/api/intelligent-conversion/convert/working',
    '/api/intelligent-conversion/convert/hye',
    '/api/real-backtest/convert-and-backtest',
    '/api/backtests/run',
    '/api/intelligent-conversion/indicators'
  ],
  
  // These endpoints need attention (Sprint 2)
  NEEDS_WORK: [
    '/api/data/binance/symbols'  // Returns 404 - will be consolidated in Sprint 2
  ]
};

// Export configuration summary - Epic 7 Status
export const CONFIG_SUMMARY = {
  baseUrl: BASE_URL,
  environment: isDevelopment ? 'development' : 'production',
  epic: 'Epic 7: API Architecture Rationalization',
  sprint: 'Sprint 1 - Foundation & Consolidation',
  status: 'In Progress - Frontend Migration',
  
  // Epic 7 Progress
  consolidation: {
    completed: ['health', 'market_data', 'strategies'],
    inProgress: ['frontend_migration'],
    planned: ['conversions', 'backtests', 'parameters']
  },
  
  totalEndpoints: Object.keys(API_ENDPOINTS).reduce((total, category) => {
    const categoryEndpoints = API_ENDPOINTS[category as keyof typeof API_ENDPOINTS];
    return total + Object.keys(categoryEndpoints).length;
  }, 0),
  
  epic7Endpoints: VALIDATED_ENDPOINTS.EPIC7_WORKING.length,
  legacyEndpoints: VALIDATED_ENDPOINTS.LEGACY_WORKING.length,
  
  lastTested: new Date().toISOString(),
  lastUpdated: '2025-08-23T10:30:00.000Z'
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