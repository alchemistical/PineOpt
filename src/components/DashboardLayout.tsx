import React, { useState } from 'react';
import { 
  BarChart3, 
  Code2, 
  Database, 
  TrendingUp, 
  Settings,
  Home,
  FileText,
  Activity,
  Zap,
  ArrowRight,
  Library
} from 'lucide-react';

export type DashboardView = 'overview' | 'data' | 'futures' | 'converter' | 'strategies' | 'library' | 'analytics' | 'settings';

interface DashboardLayoutProps {
  currentView: DashboardView;
  onViewChange: (view: DashboardView) => void;
  children: React.ReactNode;
}

const DashboardLayout: React.FC<DashboardLayoutProps> = ({ 
  currentView, 
  onViewChange, 
  children 
}) => {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  const navigationItems = [
    { 
      id: 'overview', 
      label: 'Overview', 
      icon: Home, 
      description: 'Crypto strategy lab overview' 
    },
    { 
      id: 'futures', 
      label: 'Futures Markets', 
      icon: BarChart3, 
      description: 'USDT perpetual contracts with advanced charts' 
    },
    { 
      id: 'data', 
      label: 'Data Import', 
      icon: Database, 
      description: 'Import & manage historical data' 
    },
    { 
      id: 'converter', 
      label: 'Pine Converter', 
      icon: Code2, 
      description: 'Convert Pine Script to Python' 
    },
    { 
      id: 'library', 
      label: 'Strategy Library', 
      icon: Library, 
      description: 'Upload and manage trading strategies' 
    },
    { 
      id: 'strategies', 
      label: 'Backtesting', 
      icon: FileText, 
      description: 'Run strategy backtests and analysis' 
    },
    { 
      id: 'analytics', 
      label: 'Analytics', 
      icon: Activity, 
      description: 'Trading analytics and backtesting' 
    },
    { 
      id: 'settings', 
      label: 'Settings', 
      icon: Settings, 
      description: 'Configuration and preferences' 
    }
  ] as const;

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 text-white">
      {/* Header */}
      <header className="bg-gray-800/50 backdrop-blur-xl border-b border-gray-700/50 px-6 py-4 sticky top-0 z-50">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg">
                <BarChart3 className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                  PineOpt
                </h1>
                <p className="text-xs text-gray-400">Crypto Strategy Lab</p>
              </div>
            </div>
            
            {/* Breadcrumb */}
            <div className="hidden md:flex items-center space-x-2 text-sm text-gray-400">
              <ArrowRight className="h-4 w-4" />
              <span className="capitalize">{currentView}</span>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="flex items-center space-x-3">
            <button className="p-2 bg-gray-700/50 hover:bg-gray-600/50 rounded-lg transition-colors">
              <Zap className="h-4 w-4 text-yellow-400" />
            </button>
            <div className="w-8 h-8 bg-gradient-to-r from-green-400 to-blue-500 rounded-full flex items-center justify-center text-xs font-semibold">
              U
            </div>
          </div>
        </div>
      </header>

      <div className="flex">
        {/* Sidebar */}
        <aside className={`${
          sidebarCollapsed ? 'w-20' : 'w-72'
        } bg-gray-800/30 backdrop-blur-xl border-r border-gray-700/50 min-h-[calc(100vh-80px)] transition-all duration-300 sticky top-20`}>
          <div className="p-4">
            {/* Collapse Toggle */}
            <button
              onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
              className="w-full mb-6 p-2 text-xs text-gray-400 hover:text-white transition-colors text-right"
            >
              {sidebarCollapsed ? '→' : '←'}
            </button>

            {/* Navigation */}
            <nav className="space-y-2">
              {navigationItems.map((item) => {
                const Icon = item.icon;
                const isActive = currentView === item.id;
                
                return (
                  <button
                    key={item.id}
                    onClick={() => onViewChange(item.id as DashboardView)}
                    className={`w-full flex items-center space-x-3 p-3 rounded-lg transition-all duration-200 ${
                      isActive 
                        ? 'bg-gradient-to-r from-blue-500/20 to-purple-500/20 border border-blue-500/30 text-white' 
                        : 'hover:bg-gray-700/30 text-gray-300 hover:text-white'
                    }`}
                    title={sidebarCollapsed ? item.label : ''}
                  >
                    <Icon className={`h-5 w-5 flex-shrink-0 ${isActive ? 'text-blue-400' : ''}`} />
                    {!sidebarCollapsed && (
                      <div className="text-left">
                        <div className="font-medium text-sm">{item.label}</div>
                        <div className="text-xs text-gray-400 mt-0.5">{item.description}</div>
                      </div>
                    )}
                  </button>
                );
              })}
            </nav>
          </div>
        </aside>

        {/* Main Content */}
        <main className="flex-1 min-h-[calc(100vh-80px)]">
          <div className="p-6">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
};

export default DashboardLayout;