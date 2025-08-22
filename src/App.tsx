import React, { useState } from 'react';

// New CryptoLab Pro imports
import CryptoLabLayout, { CryptoLabView } from './components/CryptoLabLayout';
import CryptoLabDashboard from './components/CryptoLabDashboard';
import StrategyLibrary from './components/StrategyLibrary';
import StrategyDashboard from './components/StrategyDashboard';
import BacktestPage from './components/BacktestPage';
import ExecutionMonitor from './components/ExecutionMonitor';
import DataImportView from './components/DataImportView';
import AIStrategyDashboard from './components/AIStrategyDashboard';
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
        return <AIStrategyDashboard />;
      
      case 'backtesting':
        return <BacktestPage onBack={() => setCurrentView('development')} />;
      
      case 'execution':
        return <ExecutionMonitor />;
      
      case 'market-data':
        return <DataImportView />;
      
      case 'research':
        return <StrategyLibrary 
          onStrategySelect={setSelectedStrategy}
          onRunBacktest={() => setCurrentView('backtesting')}
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