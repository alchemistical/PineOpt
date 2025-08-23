import React, { useState } from 'react';
import { 
  Home,
  Zap,
  BarChart3,
  Target,
  TrendingUp,
  Database,
  Search,
  Settings,
  ChevronLeft,
  ChevronRight,
  Bell,
  User,
  Menu,
  X,
  Activity,
  Brain,
  Code2,
  LineChart,
  Shield,
  Cpu
} from 'lucide-react';

export type CryptoLabView = 
  | 'dashboard'
  | 'development' 
  | 'backtesting'
  | 'execution'
  | 'market-data'
  | 'research'
  | 'settings';

interface NavigationItem {
  id: CryptoLabView;
  label: string;
  icon: React.ComponentType<any>;
  description: string;
  badge?: number;
  subItems?: Array<{
    id: string;
    label: string;
    description: string;
  }>;
}

interface CryptoLabLayoutProps {
  currentView: CryptoLabView;
  onViewChange: (view: CryptoLabView) => void;
  children: React.ReactNode;
}

const CryptoLabLayout: React.FC<CryptoLabLayoutProps> = ({ 
  currentView, 
  onViewChange, 
  children 
}) => {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [notifications] = useState(3); // Mock notification count

  const navigationItems: NavigationItem[] = [
    {
      id: 'dashboard',
      label: 'Dashboard',
      icon: Home,
      description: 'Live market overview and portfolio summary',
      subItems: [
        { id: 'overview', label: 'Overview', description: 'Market snapshot and quick actions' },
        { id: 'portfolio', label: 'Portfolio', description: 'Current positions and P&L' },
        { id: 'alerts', label: 'Alerts', description: 'Market alerts and notifications' }
      ]
    },
    {
      id: 'development',
      label: 'Development',
      icon: Zap,
      description: 'Algorithm development environment',
      subItems: [
        { id: 'strategy-builder', label: 'Strategy Builder', description: 'Create and edit trading strategies' },
        { id: 'ai-analyzer', label: 'AI Analyzer', description: 'AI-powered strategy analysis' },
        { id: 'code-validator', label: 'Code Validator', description: 'Validate and secure strategies' },
        { id: 'templates', label: 'Templates', description: 'Pre-built strategy templates' }
      ]
    },
    {
      id: 'backtesting',
      label: 'Backtesting',
      icon: BarChart3,
      description: 'Strategy testing and optimization',
      subItems: [
        { id: 'backtest-manager', label: 'Backtest Manager', description: 'Configure and run backtests' },
        { id: 'results', label: 'Results Dashboard', description: 'Analyze backtest performance' },
        { id: 'optimization', label: 'Optimization', description: 'Parameter sweeps and optimization' },
        { id: 'comparison', label: 'Comparison', description: 'Compare strategy performance' }
      ]
    },
    {
      id: 'execution',
      label: 'Execution',
      icon: Target,
      description: 'Live trading and monitoring',
      badge: 2, // Active strategies
      subItems: [
        { id: 'paper-trading', label: 'Paper Trading', description: 'Risk-free live testing' },
        { id: 'live-execution', label: 'Live Trading', description: 'Real money execution' },
        { id: 'orders', label: 'Order Management', description: 'Monitor and control orders' },
        { id: 'positions', label: 'Position Tracking', description: 'Real-time position monitoring' }
      ]
    },
    {
      id: 'market-data',
      label: 'Market Data',
      icon: Database,
      description: 'Data feeds and connections',
      subItems: [
        { id: 'exchanges', label: 'Exchange Connections', description: 'Connect to cryptocurrency exchanges' },
        { id: 'feeds', label: 'Data Feeds', description: 'Real-time and historical data' },
        { id: 'alternative', label: 'Alternative Data', description: 'Social sentiment and on-chain data' },
        { id: 'quality', label: 'Data Quality', description: 'Validation and cleaning tools' }
      ]
    },
    {
      id: 'research',
      label: 'Research',
      icon: Search,
      description: 'Analytics and research tools',
      subItems: [
        { id: 'market-analysis', label: 'Market Analysis', description: 'Technical and fundamental analysis' },
        { id: 'portfolio-analytics', label: 'Portfolio Analytics', description: 'Performance attribution and risk' },
        { id: 'strategy-discovery', label: 'Strategy Discovery', description: 'AI-powered strategy suggestions' },
        { id: 'research-notes', label: 'Research Notes', description: 'Documentation and hypothesis tracking' }
      ]
    },
    {
      id: 'settings',
      label: 'Settings',
      icon: Settings,
      description: 'Platform configuration',
      subItems: [
        { id: 'api-keys', label: 'API Keys', description: 'Exchange API management' },
        { id: 'risk-preferences', label: 'Risk Preferences', description: 'Global risk settings' },
        { id: 'notifications', label: 'Notifications', description: 'Alert preferences' },
        { id: 'system', label: 'System', description: 'Platform customization' }
      ]
    }
  ];

  const currentItem = navigationItems.find(item => item.id === currentView);

  return (
    <div className="h-screen bg-slate-900 text-white flex overflow-hidden">
      {/* Mobile Menu Overlay */}
      {mobileMenuOpen && (
        <div 
          className="fixed inset-0 bg-black/50 backdrop-blur-sm z-40 lg:hidden"
          onClick={() => setMobileMenuOpen(false)}
        />
      )}

      {/* Sidebar */}
      <div className={`
        fixed lg:static inset-y-0 left-0 z-50 w-72 bg-slate-800/30 backdrop-blur-xl border-r border-slate-700/50
        transform transition-transform duration-300 ease-in-out
        ${mobileMenuOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
        ${sidebarCollapsed ? 'lg:w-20' : 'lg:w-72'}
      `}>
        {/* Sidebar Header */}
        <div className="flex items-center justify-between h-16 px-6 border-b border-slate-700/50">
          <div className={`flex items-center space-x-3 transition-opacity duration-200 ${
            sidebarCollapsed ? 'opacity-0 lg:opacity-100' : ''
          }`}>
            <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
              <Cpu className="h-5 w-5 text-white" />
            </div>
            {!sidebarCollapsed && (
              <div>
                <h1 className="text-lg font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                  CryptoLab Pro
                </h1>
                <p className="text-xs text-slate-400">Algorithm Development Platform</p>
              </div>
            )}
          </div>
          
          <button
            onClick={() => setMobileMenuOpen(false)}
            className="lg:hidden p-2 text-slate-400 hover:text-white transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 overflow-y-auto py-6">
          <div className="px-3 space-y-2">
            {navigationItems.map((item) => {
              const IconComponent = item.icon;
              const isActive = currentView === item.id;
              
              return (
                <div key={item.id}>
                  <button
                    onClick={() => {
                      onViewChange(item.id);
                      setMobileMenuOpen(false);
                    }}
                    className={`
                      w-full flex items-center px-3 py-3 rounded-lg transition-all duration-200
                      ${isActive 
                        ? 'bg-blue-600/20 text-blue-400 border border-blue-500/30' 
                        : 'text-slate-300 hover:text-white hover:bg-slate-700/30'
                      }
                      group
                    `}
                  >
                    <IconComponent className={`
                      h-5 w-5 transition-colors
                      ${isActive ? 'text-blue-400' : 'text-slate-400 group-hover:text-white'}
                    `} />
                    
                    {!sidebarCollapsed && (
                      <>
                        <div className="flex-1 ml-3 text-left">
                          <div className="flex items-center justify-between">
                            <span className="font-medium text-sm">{item.label}</span>
                            {item.badge && (
                              <span className="bg-red-500 text-white text-xs rounded-full px-2 py-0.5 min-w-[20px] text-center">
                                {item.badge}
                              </span>
                            )}
                          </div>
                          <p className="text-xs text-slate-400 mt-0.5 truncate">
                            {item.description}
                          </p>
                        </div>
                      </>
                    )}
                  </button>
                </div>
              );
            })}
          </div>
        </nav>

        {/* Sidebar Footer */}
        <div className="border-t border-slate-700/50 p-4">
          <div className="flex items-center justify-between">
            {!sidebarCollapsed && (
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 bg-slate-600 rounded-full flex items-center justify-center">
                  <User className="h-4 w-4 text-slate-300" />
                </div>
                <div className="text-sm">
                  <div className="font-medium text-white">Developer</div>
                  <div className="text-slate-400 text-xs">Pro Plan</div>
                </div>
              </div>
            )}
            
            <button
              onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
              className="hidden lg:block p-2 text-slate-400 hover:text-white transition-colors rounded-lg hover:bg-slate-700/30"
            >
              {sidebarCollapsed ? (
                <ChevronRight className="h-4 w-4" />
              ) : (
                <ChevronLeft className="h-4 w-4" />
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Header */}
        <header className="h-16 bg-slate-800/30 backdrop-blur-xl border-b border-slate-700/50 flex items-center justify-between px-6">
          <div className="flex items-center space-x-4">
            <button
              onClick={() => setMobileMenuOpen(true)}
              className="lg:hidden p-2 text-slate-400 hover:text-white transition-colors rounded-lg hover:bg-slate-700/30"
            >
              <Menu className="h-5 w-5" />
            </button>
            
            <div>
              <h2 className="text-xl font-bold text-white">
                {currentItem?.label || 'Dashboard'}
              </h2>
              <p className="text-sm text-slate-400">
                {currentItem?.description || 'Welcome to CryptoLab Pro'}
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-4">
            {/* Market Status */}
            <div className="hidden md:flex items-center space-x-2 px-3 py-1.5 bg-green-500/20 border border-green-500/30 rounded-lg">
              <Activity className="h-4 w-4 text-green-400 animate-pulse" />
              <span className="text-green-400 text-sm font-medium">Markets Open</span>
            </div>

            {/* Notifications */}
            <button className="relative p-2 text-slate-400 hover:text-white transition-colors rounded-lg hover:bg-slate-700/30">
              <Bell className="h-5 w-5" />
              {notifications > 0 && (
                <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full px-1.5 py-0.5 min-w-[18px] text-center">
                  {notifications}
                </span>
              )}
            </button>

            {/* User Menu */}
            <button className="flex items-center space-x-2 p-2 text-slate-400 hover:text-white transition-colors rounded-lg hover:bg-slate-700/30">
              <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                <User className="h-4 w-4 text-white" />
              </div>
              <span className="hidden md:block text-sm font-medium text-white">Developer</span>
            </button>
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 overflow-auto bg-slate-900">
          {children}
        </main>
      </div>
    </div>
  );
};

export default CryptoLabLayout;