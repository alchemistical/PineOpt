# Epic 8 Component Refactoring Guide

**Specific Migration Instructions for Existing Components**

---

## **Overview**

This guide provides detailed instructions for refactoring existing PineOpt components to work with the new Epic 8 unified navigation system. Each component migration includes before/after code examples, integration steps, and testing requirements.

---

## **Component Migration Priority Matrix**

### **Critical Priority (Week 1)**
1. **CryptoLabDashboard.tsx** - Main dashboard component
2. **CryptoLabLayout.tsx** - Remove and replace functionality
3. **DashboardLayout.tsx** - Remove and replace functionality

### **High Priority (Week 2)**
4. **StrategyDashboard.tsx** - Strategy management interface
5. **StrategyLibrary.tsx** - Strategy library component
6. **App.tsx** - Main routing configuration

### **Medium Priority (Weeks 3-4)**
7. All remaining dashboard and strategy components
8. Chart and data visualization components
9. Settings and configuration components

---

## **1. CryptoLabDashboard Component Migration**

### **Current State Analysis**
**File:** `src/components/CryptoLabDashboard.tsx`
- **Lines of Code:** 525+ lines
- **Key Features:** Portfolio overview, market data, strategy performance, quick actions
- **Dependencies:** Uses navigation callbacks and Epic 7 API integration
- **API Endpoints:** `/api/v1/strategies/list`, `/api/v1/market/overview`

### **Migration Strategy**

#### **Step 1: Remove Layout Dependencies**
```tsx
// BEFORE: CryptoLabDashboard with navigation props
interface CryptoLabDashboardProps {
  onNavigate?: (view: string) => void;  // ❌ Remove this
}

// AFTER: Clean component without navigation concerns
interface CryptoLabDashboardProps {
  // Navigation handled by UnifiedLayout
}
```

#### **Step 2: Update Navigation Calls**
```tsx
// BEFORE: Using callback prop
const handleQuickAction = (action: string) => {
  onNavigate?.(action);  // ❌ Remove this
};

// AFTER: Using React Router
import { useNavigate } from 'react-router-dom';

const CryptoLabDashboard: React.FC<CryptoLabDashboardProps> = () => {
  const navigate = useNavigate();
  
  const handleQuickAction = (action: string) => {
    // ✅ Direct navigation with new routing structure
    switch (action) {
      case 'research':
        navigate('/strategies/ai-tools');
        break;
      case 'backtesting':
        navigate('/testing/backtesting');
        break;
      case 'development':
        navigate('/strategies/builder');
        break;
      case 'execution':
        navigate('/execution/trading');
        break;
    }
  };
```

#### **Step 3: Update Quick Actions Integration**
```tsx
// BEFORE: Hardcoded navigation callbacks
<button 
  onClick={() => onNavigate?.('research')}
  className="p-6 bg-gradient-to-r from-blue-600/20 to-purple-600/20..."
>

// AFTER: Integrated with new routing system
<button 
  onClick={() => navigate('/strategies/ai-tools')}
  className="p-6 bg-gradient-to-r from-blue-600/20 to-purple-600/20..."
>
```

#### **Step 4: Enhanced Integration with App Store**
```tsx
// AFTER: Enhanced with Epic 8 state management
import { useAppStore } from '../store/appStore';

const CryptoLabDashboard: React.FC = () => {
  const navigate = useNavigate();
  const { 
    strategies, 
    marketData, 
    loadStrategies, 
    loadMarketData,
    user: { dashboardWidgets, preferredLayout }
  } = useAppStore();
  
  // ... rest of component logic
};
```

### **Complete Refactored Component**
```tsx
// src/components/dashboard/DashboardOverview.tsx (renamed and refactored)
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAppStore } from '../../store/appStore';
import {
  TrendingUp, TrendingDown, Activity, Target, Brain, Zap,
  DollarSign, Percent, Clock, Users, ArrowUpRight, ArrowDownRight,
  Plus, Play, Pause, BarChart3, LineChart, PieChart, Bell,
  AlertCircle, CheckCircle, RefreshCw, Sparkles, Bot, Database, Cpu
} from 'lucide-react';

// Keep all existing interfaces
interface MarketData {
  symbol: string;
  price: number;
  change: number;
  changePercent: number;
  volume: number;
  marketCap?: number;
}

interface PortfolioSummary {
  totalValue: number;
  dayChange: number;
  dayChangePercent: number;
  realizedPnL: number;
  unrealizedPnL: number;
  positions: number;
  activeStrategies: number;
}

interface StrategyPerformance {
  id: string;
  name: string;
  status: 'running' | 'paused' | 'stopped';
  pnl: number;
  pnlPercent: number;
  trades: number;
  winRate: number;
  lastActivity: string;
}

interface RecentActivity {
  id: string;
  type: 'trade' | 'backtest' | 'strategy' | 'alert';
  message: string;
  timestamp: string;
  status: 'success' | 'warning' | 'error' | 'info';
}

const DashboardOverview: React.FC = () => {
  const navigate = useNavigate();
  const { 
    strategies, 
    marketData, 
    loadStrategies, 
    loadMarketData,
    user: { dashboardWidgets, preferredLayout }
  } = useAppStore();
  
  // Keep all existing state logic
  const [localMarketData, setMarketData] = useState<MarketData[]>([]);
  const [portfolio, setPortfolio] = useState<PortfolioSummary | null>(null);
  const [strategyPerformance, setStrategies] = useState<StrategyPerformance[]>([]);
  const [activities, setActivities] = useState<RecentActivity[]>([]);
  const [loading, setLoading] = useState(true);

  // Keep existing useEffect and data loading logic
  useEffect(() => {
    loadDashboardData();
    const interval = setInterval(loadDashboardData, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadDashboardData = async () => {
    try {
      // Keep all existing data loading logic
      // ... (same as current implementation)
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  // Keep all existing helper functions
  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(value);
  };

  // Updated navigation handlers
  const handleQuickAction = (action: string) => {
    switch (action) {
      case 'research':
        navigate('/strategies/ai-tools');
        break;
      case 'backtesting':
        navigate('/testing/backtesting');
        break;
      case 'development':
        navigate('/strategies/builder');
        break;
      case 'execution':
        navigate('/execution/trading');
        break;
      default:
        navigate(`/${action}`);
    }
  };

  // Keep existing loading state
  if (loading) {
    return (
      <div className="p-6 flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <RefreshCw className="h-8 w-8 animate-spin text-blue-400 mx-auto mb-4" />
          <p className="text-slate-400">Loading market data...</p>
        </div>
      </div>
    );
  }

  // Keep all existing JSX structure, just update navigation calls
  return (
    <div className="p-6 space-y-6">
      {/* Keep all existing JSX - just update onClick handlers */}
      {/* Quick Stats - same as before */}
      {/* Market Overview - same as before */}
      {/* Recent Activity - same as before */}
      {/* Strategy Performance - same as before */}
      
      {/* Updated Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <button 
          onClick={() => handleQuickAction('research')}
          className="p-6 bg-gradient-to-r from-blue-600/20 to-purple-600/20 border border-blue-500/30 rounded-xl hover:from-blue-600/30 hover:to-purple-600/30 transition-all text-left"
        >
          <div className="flex items-center space-x-3">
            <Brain className="h-8 w-8 text-blue-400" />
            <div>
              <h3 className="font-medium text-white">AI Strategy Analyzer</h3>
              <p className="text-sm text-slate-400">Get AI insights on your strategies</p>
            </div>
          </div>
        </button>
        
        <button 
          onClick={() => handleQuickAction('backtesting')}
          className="p-6 bg-gradient-to-r from-green-600/20 to-emerald-600/20 border border-green-500/30 rounded-xl hover:from-green-600/30 hover:to-emerald-600/30 transition-all text-left"
        >
          <div className="flex items-center space-x-3">
            <BarChart3 className="h-8 w-8 text-green-400" />
            <div>
              <h3 className="font-medium text-white">Run Backtest</h3>
              <p className="text-sm text-slate-400">Test strategies on historical data</p>
            </div>
          </div>
        </button>
        
        <button 
          onClick={() => handleQuickAction('development')}
          className="p-6 bg-gradient-to-r from-purple-600/20 to-pink-600/20 border border-purple-500/30 rounded-xl hover:from-purple-600/30 hover:to-pink-600/30 transition-all text-left"
        >
          <div className="flex items-center space-x-3">
            <Zap className="h-8 w-8 text-purple-400" />
            <div>
              <h3 className="font-medium text-white">Strategy Builder</h3>
              <p className="text-sm text-slate-400">Create new trading algorithms</p>
            </div>
          </div>
        </button>
        
        <button 
          onClick={() => handleQuickAction('execution')}
          className="p-6 bg-gradient-to-r from-orange-600/20 to-red-600/20 border border-orange-500/30 rounded-xl hover:from-orange-600/30 hover:to-red-600/30 transition-all text-left"
        >
          <div className="flex items-center space-x-3">
            <Target className="h-8 w-8 text-orange-400" />
            <div>
              <h3 className="font-medium text-white">Live Trading</h3>
              <p className="text-sm text-slate-400">Execute strategies in real-time</p>
            </div>
          </div>
        </button>
      </div>
    </div>
  );
};

export default DashboardOverview;
```

---

## **2. StrategyDashboard Component Migration**

### **Current State Analysis**
**File:** `src/components/StrategyDashboard.tsx`
- **Lines of Code:** 750+ lines
- **Key Features:** Strategy management, AI profiling, backtesting integration
- **Dependencies:** Navigation callbacks, modal systems
- **Complex State:** Strategy selection, profiling modals, upload forms

### **Migration Strategy**

#### **Step 1: Remove Layout Wrapper**
```tsx
// BEFORE: Component handles its own layout
const StrategyDashboard: React.FC<StrategyDashboardProps> = ({ 
  onStrategySelect, 
  onRunBacktest
}) => {
  return (
    <div className="min-h-screen bg-gray-900">
      {/* Header */}
      <div className="bg-gray-800/30 backdrop-blur-sm border-b border-gray-700/50 p-6">
        {/* ... header content */}
      </div>
      
      {/* Main content */}
      <div className="p-6">
        {/* ... dashboard content */}
      </div>
    </div>
  );
};

// AFTER: Clean component that works within UnifiedLayout
const StrategyManagement: React.FC = () => {
  return (
    <div className="space-y-6">
      {/* Remove layout wrapper, content only */}
      {/* ... dashboard content */}
    </div>
  );
};
```

#### **Step 2: Update Modal Management**
```tsx
// BEFORE: Local modal state management
const [showUpload, setShowUpload] = useState(false);
const [showProfileModal, setShowProfileModal] = useState(false);

// Modal rendered inline
{showUpload && (
  <div className="fixed inset-0 bg-black/50 backdrop-blur-sm...">
    <StrategyUpload />
  </div>
)}

// AFTER: Global modal management with Epic 8 patterns
import { useModalStore } from '../../store/modalStore';

const StrategyManagement: React.FC = () => {
  const { openModal, closeModal } = useModalStore();
  
  const handleUploadStrategy = () => {
    openModal({
      type: 'strategy-upload',
      props: {
        onSuccess: (strategy) => {
          // Handle successful upload
          setStrategies(prev => [strategy, ...prev]);
          closeModal();
        }
      }
    });
  };
};
```

#### **Step 3: Enhanced Navigation Integration**
```tsx
// BEFORE: Callback-based navigation
interface StrategyDashboardProps {
  onStrategySelect?: (strategy: Strategy) => void;
  onRunBacktest?: (strategy: Strategy) => void;
}

// AFTER: Direct navigation with routing
import { useNavigate } from 'react-router-dom';
import { useAppStore } from '../../store/appStore';

const StrategyManagement: React.FC = () => {
  const navigate = useNavigate();
  const { openTab } = useAppStore();
  
  const handleStrategySelect = (strategy: Strategy) => {
    // Open strategy in workspace tab
    openTab({
      id: `strategy-${strategy.id}`,
      label: strategy.name,
      type: 'strategy',
      data: strategy,
      path: `/strategies/builder?id=${strategy.id}`
    });
    
    navigate(`/strategies/builder?id=${strategy.id}`);
  };
  
  const handleRunBacktest = (strategy: Strategy) => {
    // Navigate to backtesting with pre-loaded strategy
    navigate(`/testing/backtesting?strategy=${strategy.id}`);
  };
};
```

---

## **3. StrategyLibrary Component Migration**

### **Current State Analysis**
**File:** `src/components/StrategyLibrary.tsx`
- **Lines of Code:** 870+ lines
- **Key Features:** Strategy browsing, filtering, AI profiling, file management
- **Complex Features:** Pagination, search, modal management
- **API Integration:** Heavy use of Epic 7 strategy endpoints

### **Migration Strategy**

#### **Step 1: Integrate with Unified Search**
```tsx
// BEFORE: Local search state
const [searchQuery, setSearchQuery] = useState('');
const [languageFilter, setLanguageFilter] = useState<string>('');
const [statusFilter, setStatusFilter] = useState<string>('');

// AFTER: Integrated with global search and filters
import { useSearchStore } from '../../store/searchStore';

const StrategyLibrary: React.FC = () => {
  const {
    searchQuery,
    setSearchQuery,
    filters,
    updateFilter,
    clearFilters
  } = useSearchStore();
  
  // Enhanced search with global state persistence
};
```

#### **Step 2: Modal System Migration**
```tsx
// BEFORE: Complex inline modal management
{showProfileModal && (
  <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4 z-50">
    <div className="bg-gray-800 rounded-xl w-full max-w-4xl max-h-[90vh] overflow-y-auto border border-gray-600">
      {/* Complex modal content */}
    </div>
  </div>
)}

// AFTER: Simplified modal with global management
import { useModal } from '../../hooks/useModal';

const StrategyLibrary: React.FC = () => {
  const { openModal } = useModal();
  
  const handleGenerateProfile = (strategy: Strategy) => {
    openModal('strategy-profile', {
      strategy,
      onComplete: (profile) => {
        // Handle profile completion
      }
    });
  };
};
```

#### **Step 3: Enhanced Data Management**
```tsx
// BEFORE: Local data fetching and state
const [strategies, setStrategies] = useState<Strategy[]>([]);
const [loading, setLoading] = useState(true);

const loadStrategies = async (reset = false) => {
  try {
    setLoading(true);
    // ... fetch logic
  } catch (err) {
    setError(err);
  } finally {
    setLoading(false);
  }
};

// AFTER: Enhanced with Epic 8 data management
import { useQuery, useInfiniteQuery } from '@tanstack/react-query';
import { useAppStore } from '../../store/appStore';

const StrategyLibrary: React.FC = () => {
  const { searchQuery, filters } = useSearchStore();
  
  // Enhanced data fetching with React Query
  const {
    data,
    isLoading,
    error,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
  } = useInfiniteQuery({
    queryKey: ['strategies', searchQuery, filters],
    queryFn: ({ pageParam = 0 }) => fetchStrategies({
      page: pageParam,
      search: searchQuery,
      ...filters
    }),
    getNextPageParam: (lastPage) => lastPage.nextCursor
  });
  
  const strategies = data?.pages.flatMap(page => page.strategies) ?? [];
};
```

---

## **4. Layout Component Removal**

### **CryptoLabLayout.tsx Removal Process**

#### **Step 1: Extract Reusable Components**
```tsx
// BEFORE: Monolithic layout component
const CryptoLabLayout: React.FC<CryptoLabLayoutProps> = ({ 
  currentView, 
  onViewChange, 
  children 
}) => {
  // 330+ lines of navigation logic
};

// AFTER: Extract useful parts to Epic 8 components
// 1. Extract market status indicator
export const MarketStatusIndicator = () => (
  <div className="flex items-center space-x-2 px-3 py-1.5 bg-green-500/20 border border-green-500/30 rounded-lg">
    <Activity className="h-4 w-4 text-green-400 animate-pulse" />
    <span className="text-green-400 text-sm font-medium">Markets Open</span>
  </div>
);

// 2. Extract user menu
export const UserMenu = () => (
  <button className="flex items-center space-x-2 p-2 text-slate-400 hover:text-white transition-colors rounded-lg hover:bg-slate-700/30">
    <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
      <User className="h-4 w-4 text-white" />
    </div>
    <span className="hidden md:block text-sm font-medium text-white">Developer</span>
  </button>
);

// 3. Extract notification bell
export const NotificationBell = () => {
  const [notifications] = useState(3);
  
  return (
    <button className="relative p-2 text-slate-400 hover:text-white transition-colors rounded-lg hover:bg-slate-700/30">
      <Bell className="h-5 w-5" />
      {notifications > 0 && (
        <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full px-1.5 py-0.5">
          {notifications}
        </span>
      )}
    </button>
  );
};
```

#### **Step 2: Migration Script**
```bash
#!/bin/bash
# migrate-layout-components.sh

echo "🔄 Starting CryptoLabLayout migration..."

# 1. Extract reusable components
mkdir -p src/components/common
mkdir -p src/components/header

# 2. Move useful components
echo "📦 Extracting reusable components..."
cat > src/components/header/MarketStatusIndicator.tsx << 'EOF'
// Extracted market status component
EOF

cat > src/components/header/UserMenu.tsx << 'EOF'
// Extracted user menu component  
EOF

cat > src/components/header/NotificationBell.tsx << 'EOF'
// Extracted notification bell component
EOF

# 3. Update imports in existing components
echo "🔄 Updating imports..."
find src/components -name "*.tsx" -exec sed -i '' 's/CryptoLabLayout/UnifiedLayout/g' {} \;

# 4. Remove old layout files
echo "🗑️ Removing old layout components..."
rm src/components/CryptoLabLayout.tsx
rm src/components/DashboardLayout.tsx

echo "✅ Layout migration complete!"
```

---

## **5. App.tsx Routing Migration**

### **Current State Analysis**
```tsx
// BEFORE: Complex routing with multiple layout systems
const App: React.FC = () => {
  const [currentView, setCurrentView] = useState<CryptoLabView>('dashboard');
  const [dashboardView, setDashboardView] = useState<DashboardView>('overview');
  
  return (
    <div className="App">
      {/* Conditional layout rendering */}
      {usesCryptoLabLayout ? (
        <CryptoLabLayout currentView={currentView} onViewChange={setCurrentView}>
          {/* Conditional component rendering */}
        </CryptoLabLayout>
      ) : (
        <DashboardLayout currentView={dashboardView} onViewChange={setDashboardView}>
          {/* Different conditional component rendering */}
        </DashboardLayout>
      )}
    </div>
  );
};
```

### **Migration to Unified Routing**
```tsx
// AFTER: Clean routing with single layout system
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import UnifiedLayout from './components/layouts/UnifiedLayout';
import ErrorBoundary from './components/common/ErrorBoundary';

// Import all page components
import DashboardOverview from './components/dashboard/DashboardOverview';
import PortfolioView from './components/dashboard/PortfolioView';
import StrategyLibrary from './components/strategies/StrategyLibrary';
// ... other imports

const App: React.FC = () => {
  return (
    <ErrorBoundary>
      <Router>
        <Routes>
          <Route path="/" element={<UnifiedLayout />}>
            {/* Default redirect */}
            <Route index element={<Navigate to="/dashboard/overview" replace />} />
            
            {/* Dashboard routes */}
            <Route path="dashboard">
              <Route index element={<Navigate to="/dashboard/overview" replace />} />
              <Route path="overview" element={<DashboardOverview />} />
              <Route path="portfolio" element={<PortfolioView />} />
              <Route path="alerts" element={<AlertsView />} />
            </Route>
            
            {/* Strategy routes */}
            <Route path="strategies">
              <Route index element={<Navigate to="/strategies/library" replace />} />
              <Route path="library" element={<StrategyLibrary />} />
              <Route path="builder" element={<StrategyBuilder />} />
              <Route path="converter" element={<PineConverter />} />
              <Route path="ai-tools" element={<AITools />} />
            </Route>
            
            {/* ... other routes */}
          </Route>
          
          {/* 404 handling */}
          <Route path="*" element={<Navigate to="/dashboard/overview" replace />} />
        </Routes>
      </Router>
    </ErrorBoundary>
  );
};

export default App;
```

---

## **6. Testing Strategy for Refactored Components**

### **Unit Testing Updates**
```tsx
// src/components/__tests__/DashboardOverview.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import DashboardOverview from '../dashboard/DashboardOverview';

const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate,
}));

const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } }
  });
  
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        {children}
      </BrowserRouter>
    </QueryClientProvider>
  );
};

describe('DashboardOverview', () => {
  beforeEach(() => {
    mockNavigate.mockClear();
  });

  test('renders dashboard overview with market data', async () => {
    render(<DashboardOverview />, { wrapper: TestWrapper });
    
    await waitFor(() => {
      expect(screen.getByText('Portfolio Value')).toBeInTheDocument();
    });
  });

  test('navigates to correct routes when quick actions are clicked', () => {
    render(<DashboardOverview />, { wrapper: TestWrapper });
    
    const aiStrategyButton = screen.getByText('AI Strategy Analyzer');
    fireEvent.click(aiStrategyButton);
    
    expect(mockNavigate).toHaveBeenCalledWith('/strategies/ai-tools');
  });

  test('loads market data from Epic 7 APIs', async () => {
    // Mock Epic 7 API responses
    global.fetch = jest.fn()
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          status: 'success',
          strategies: []
        })
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          status: 'success',
          market_overview: { tickers: {} }
        })
      });

    render(<DashboardOverview />, { wrapper: TestWrapper });
    
    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith('http://localhost:5007/api/v1/strategies/list?limit=20');
    });
  });
});
```

### **Integration Testing**
```tsx
// src/components/__tests__/NavigationIntegration.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import App from '../App';

describe('Navigation Integration', () => {
  test('unified layout navigation works correctly', () => {
    render(
      <MemoryRouter initialEntries={['/']}>
        <App />
      </MemoryRouter>
    );
    
    // Should redirect to dashboard overview
    expect(window.location.pathname).toBe('/dashboard/overview');
  });

  test('primary navigation updates secondary navigation', () => {
    render(
      <MemoryRouter initialEntries={['/strategies/library']}>
        <App />
      </MemoryRouter>
    );
    
    // Should show strategy section with library page active
    expect(screen.getByText('Strategy Lab')).toHaveClass('text-blue-400');
    expect(screen.getByText('Strategy Library')).toHaveClass('text-blue-400');
  });

  test('breadcrumb navigation reflects current location', () => {
    render(
      <MemoryRouter initialEntries={['/strategies/ai-tools']}>
        <App />
      </MemoryRouter>
    );
    
    expect(screen.getByText('Strategy Lab')).toBeInTheDocument();
    expect(screen.getByText('AI Analysis')).toBeInTheDocument();
  });
});
```

### **E2E Testing with Cypress**
```typescript
// cypress/e2e/epic-8-navigation.cy.ts
describe('Epic 8 Navigation', () => {
  beforeEach(() => {
    cy.visit('/');
  });

  it('should navigate through unified layout correctly', () => {
    // Should start at dashboard overview
    cy.url().should('include', '/dashboard/overview');
    cy.contains('Portfolio Value').should('be.visible');

    // Navigate to strategy lab
    cy.get('[data-testid="nav-strategies"]').click();
    cy.url().should('include', '/strategies/library');
    cy.contains('Strategy Library').should('be.visible');

    // Use secondary navigation
    cy.get('[data-testid="nav-strategy-builder"]').click();
    cy.url().should('include', '/strategies/builder');
    cy.contains('Strategy Builder').should('be.visible');

    // Test breadcrumb navigation
    cy.get('[data-testid="breadcrumb-strategies"]').click();
    cy.url().should('include', '/strategies');
  });

  it('should handle quick actions correctly', () => {
    // Test AI analyzer quick action
    cy.get('[data-testid="quick-action-ai-analyzer"]').click();
    cy.url().should('include', '/strategies/ai-tools');

    // Test backtesting quick action
    cy.visit('/dashboard/overview');
    cy.get('[data-testid="quick-action-backtest"]').click();
    cy.url().should('include', '/testing/backtesting');
  });

  it('should preserve state during navigation', () => {
    // Set up some state
    cy.visit('/strategies/library');
    cy.get('[data-testid="search-input"]').type('momentum');
    
    // Navigate away and back
    cy.get('[data-testid="nav-dashboard"]').click();
    cy.get('[data-testid="nav-strategies"]').click();
    
    // State should be preserved
    cy.get('[data-testid="search-input"]').should('have.value', 'momentum');
  });
});
```

---

## **7. Performance Considerations**

### **Bundle Size Optimization**
```tsx
// BEFORE: All components imported statically
import CryptoLabDashboard from './components/CryptoLabDashboard';
import StrategyDashboard from './components/StrategyDashboard';
import StrategyLibrary from './components/StrategyLibrary';

// AFTER: Lazy loading for better performance
import { lazy, Suspense } from 'react';

const DashboardOverview = lazy(() => import('./components/dashboard/DashboardOverview'));
const StrategyLibrary = lazy(() => import('./components/strategies/StrategyLibrary'));
const StrategyManagement = lazy(() => import('./components/strategies/StrategyManagement'));

// Wrap in suspense
const LazyRoute: React.FC<{ component: React.ComponentType }> = ({ component: Component }) => (
  <Suspense fallback={<LoadingSpinner />}>
    <Component />
  </Suspense>
);
```

### **Memory Optimization**
```tsx
// Cleanup subscriptions and intervals
useEffect(() => {
  const interval = setInterval(loadData, 30000);
  const unsubscribe = subscribeToMarketData(handleMarketUpdate);
  
  return () => {
    clearInterval(interval);
    unsubscribe();
  };
}, []);
```

### **Component Optimization**
```tsx
// Memoize expensive calculations
const expensiveData = useMemo(() => {
  return strategies.map(strategy => ({
    ...strategy,
    performance: calculatePerformanceMetrics(strategy.backtests)
  }));
}, [strategies]);

// Memoize callbacks to prevent unnecessary re-renders
const handleStrategySelect = useCallback((strategy: Strategy) => {
  navigate(`/strategies/builder?id=${strategy.id}`);
}, [navigate]);
```

---

## **8. Rollback Procedures**

### **Emergency Rollback Plan**
```bash
#!/bin/bash
# rollback-epic-8.sh

echo "🚨 Starting Epic 8 rollback..."

# 1. Switch to backup branch
git checkout epic-7-backup

# 2. Create rollback branch
git checkout -b epic-8-rollback-$(date +%Y%m%d)

# 3. Cherry-pick essential fixes only
git cherry-pick <essential-fix-commits>

# 4. Deploy rollback version
npm run build
npm run deploy:rollback

echo "✅ Rollback complete. Epic 7 state restored."
```

### **Feature Flag Rollback**
```tsx
// Gradual rollback with feature flags
const useEpic8Features = () => {
  const [enabled, setEnabled] = useState(
    localStorage.getItem('epic8-enabled') === 'true' || 
    process.env.REACT_APP_EPIC8_ENABLED === 'true'
  );
  
  return { 
    unifiedLayout: enabled,
    newNavigation: enabled,
    enhancedSearch: enabled
  };
};

// Conditional rendering based on feature flags
const App: React.FC = () => {
  const { unifiedLayout } = useEpic8Features();
  
  if (!unifiedLayout) {
    // Fallback to Epic 7 layout
    return <LegacyApp />;
  }
  
  return <UnifiedApp />;
};
```

---

This comprehensive refactoring guide ensures a smooth migration from the current dual-layout system to the unified Epic 8 navigation experience while maintaining all existing functionality and improving the overall user experience.