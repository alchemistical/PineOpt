import React, { useState } from 'react';

// New CryptoLab Pro imports
import CryptoLabLayout, { CryptoLabView } from './components/CryptoLabLayout';
import CryptoLabDashboard from './components/CryptoLabDashboard';
import StrategyLibrary from './components/StrategyLibrary';
import StrategyDashboard from './components/StrategyDashboard';
import BacktestResults from './components/BacktestResults';
import ExecutionMonitor from './components/ExecutionMonitor';
import DataImportView from './components/DataImportView';
import { Settings, FileText, Activity, Wrench } from 'lucide-react';

// Placeholder components for upcoming features
const StrategiesView: React.FC = () => (
  <div className="space-y-6">
    <div className="flex items-center justify-between">
      <div>
        <h1 className="text-3xl font-bold text-white mb-2">Strategy Database</h1>
        <p className="text-gray-400">Manage and organize your converted trading strategies</p>
      </div>
    </div>
    
    <div className="bg-gray-800/30 backdrop-blur-sm rounded-xl border border-gray-700/50 p-12">
      <div className="text-center">
        <FileText className="h-16 w-16 text-gray-400 mx-auto mb-4" />
        <h2 className="text-xl font-semibold text-white mb-2">Strategy Management</h2>
        <p className="text-gray-400 mb-6">View, edit, and organize your converted Pine Script strategies</p>
        <div className="inline-flex items-center px-4 py-2 bg-yellow-500/20 border border-yellow-500/30 rounded-lg">
          <Wrench className="h-4 w-4 text-yellow-400 mr-2" />
          <span className="text-yellow-400 text-sm">Coming Soon</span>
        </div>
      </div>
    </div>
  </div>
);

const AnalyticsView: React.FC = () => (
  <div className="space-y-6">
    <div className="flex items-center justify-between">
      <div>
        <h1 className="text-3xl font-bold text-white mb-2">Trading Analytics</h1>
        <p className="text-gray-400">Backtest and analyze your trading strategies</p>
      </div>
    </div>
    
    <div className="bg-gray-800/30 backdrop-blur-sm rounded-xl border border-gray-700/50 p-12">
      <div className="text-center">
        <Activity className="h-16 w-16 text-gray-400 mx-auto mb-4" />
        <h2 className="text-xl font-semibold text-white mb-2">Backtesting Engine</h2>
        <p className="text-gray-400 mb-6">Test your strategies against historical data with comprehensive metrics</p>
        <div className="inline-flex items-center px-4 py-2 bg-yellow-500/20 border border-yellow-500/30 rounded-lg">
          <Wrench className="h-4 w-4 text-yellow-400 mr-2" />
          <span className="text-yellow-400 text-sm">Coming Soon</span>
        </div>
      </div>
    </div>
  </div>
);

const SettingsView: React.FC = () => (
  <div className="space-y-6">
    <div className="flex items-center justify-between">
      <div>
        <h1 className="text-3xl font-bold text-white mb-2">Settings</h1>
        <p className="text-gray-400">Configure your platform preferences</p>
      </div>
    </div>
    
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div className="bg-gray-800/30 backdrop-blur-sm rounded-xl p-6 border border-gray-700/50">
        <h3 className="text-lg font-semibold text-white mb-4">General Settings</h3>
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-gray-300">Dark Mode</span>
            <div className="w-12 h-6 bg-blue-600 rounded-full relative cursor-pointer">
              <div className="w-5 h-5 bg-white rounded-full absolute right-0.5 top-0.5"></div>
            </div>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-gray-300">Auto-save Strategies</span>
            <div className="w-12 h-6 bg-blue-600 rounded-full relative cursor-pointer">
              <div className="w-5 h-5 bg-white rounded-full absolute right-0.5 top-0.5"></div>
            </div>
          </div>
        </div>
      </div>
      
      <div className="bg-gray-800/30 backdrop-blur-sm rounded-xl p-6 border border-gray-700/50">
        <h3 className="text-lg font-semibold text-white mb-4">API Configuration</h3>
        <div className="space-y-4">
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-green-400 rounded-full"></div>
            <span className="text-gray-300 text-sm">Flask API Server: Online</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-green-400 rounded-full"></div>
            <span className="text-gray-300 text-sm">Database: Connected</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-blue-400 rounded-full"></div>
            <span className="text-gray-300 text-sm">Port: 5001</span>
          </div>
        </div>
      </div>
    </div>
  </div>
);

function App() {
  const [currentView, setCurrentView] = useState<CryptoLabView>('dashboard');
  const [selectedStrategy, setSelectedStrategy] = useState<any>(null);

  const renderView = () => {
    switch (currentView) {
      case 'dashboard':
        return <CryptoLabDashboard onNavigate={setCurrentView} />;
      
      case 'development':
        return <StrategyDashboard 
          onStrategySelect={setSelectedStrategy}
          onRunBacktest={(strategy) => {
            setSelectedStrategy(strategy);
            setCurrentView('backtesting');
          }}
        />;
      
      case 'backtesting':
        if (selectedStrategy) {
          // Mock backtest result for demonstration
          const mockBacktestResult = {
            id: 'demo-backtest',
            strategy_id: selectedStrategy.id,
            strategy_name: selectedStrategy.name,
            start_date: '2023-01-01',
            end_date: '2024-01-01',
            initial_capital: 10000,
            final_capital: 12500,
            status: 'completed' as const,
            metrics: {
              total_return: 2500,
              total_return_percentage: 25.0,
              annualized_return: 25.0,
              max_drawdown: -8.5,
              sharpe_ratio: 1.85,
              sortino_ratio: 2.12,
              win_rate: 68.2,
              profit_factor: 1.75,
              total_trades: 45,
              winning_trades: 31,
              losing_trades: 14,
              avg_win: 120.50,
              avg_loss: -65.30,
              largest_win: 450.75,
              largest_loss: -180.25,
              avg_trade_duration: 18.5,
              volatility: 0.15,
              var_95: -250.0,
              calmar_ratio: 2.94,
              sterling_ratio: 2.56
            },
            trades: [],
            equity_curve: [],
            drawdown_curve: [],
            price_data: [],
            created_at: new Date().toISOString(),
            execution_time_ms: 1250
          };
          
          return <BacktestResults 
            result={mockBacktestResult} 
            onClose={() => setCurrentView('development')}
          />;
        } else {
          return (
            <div className="p-6 text-center">
              <h2 className="text-xl font-bold text-white mb-4">Backtesting Lab</h2>
              <p className="text-slate-400">Select a strategy from the Development section to run backtests.</p>
            </div>
          );
        }
      
      case 'execution':
        return <ExecutionMonitor />;
      
      case 'market-data':
        return <DataImportView />;
      
      case 'research':
        return <StrategyLibrary 
          onStrategySelect={setSelectedStrategy}
          onRunBacktest={(strategy) => {
            setSelectedStrategy(strategy);
            setCurrentView('backtesting');
          }}
        />;
      
      case 'settings':
        return <SettingsView />;
      
      default:
        return <CryptoLabDashboard />;
    }
  };

  return (
    <CryptoLabLayout 
      currentView={currentView} 
      onViewChange={setCurrentView}
    >
      {renderView()}
    </CryptoLabLayout>
  );
}

export default App;