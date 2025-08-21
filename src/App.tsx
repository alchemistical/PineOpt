import React, { useState } from 'react';

// Simple test component first
const TestComponent: React.FC = () => (
  <div style={{ color: 'white', backgroundColor: '#111', padding: '20px', minHeight: '100vh' }}>
    <h1>🎉 React App Loading Test</h1>
    <p>If you see this, React is working!</p>
    <button onClick={() => alert('Button works!')} style={{ padding: '10px', margin: '10px', backgroundColor: '#3b82f6', color: 'white', border: 'none', borderRadius: '4px' }}>
      Test Button
    </button>
  </div>
);

import DashboardLayout, { DashboardView } from './components/DashboardLayout';
import OverviewDashboard from './components/OverviewDashboard';
import DataImportView from './components/DataImportView';
import PineConverterView from './components/PineConverterView';
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
  // Test: Try just the basic dashboard layout without complex components
  const [currentView, setCurrentView] = useState<DashboardView>('overview');

  // Test one component at a time
  const renderView = () => {
    switch (currentView) {
      case 'overview':
        // Test: Try loading OverviewDashboard first
        return <OverviewDashboard onNavigate={setCurrentView} />;
      case 'data':
        // Test: Try loading DataImportView gradually
        try {
          return <DataImportView />;
        } catch (error) {
          return (
            <div style={{ color: 'red', padding: '20px' }}>
              <h2>DataImportView Error:</h2>
              <p>{String(error)}</p>
            </div>
          );
        }
      case 'converter':
        return <PineConverterView />;
      case 'strategies':
        return <StrategiesView />;
      case 'analytics':
        return <AnalyticsView />;
      case 'settings':
        return <SettingsView />;
      default:
        return <OverviewDashboard onNavigate={setCurrentView} />;
    }
  };

  return (
    <DashboardLayout 
      currentView={currentView} 
      onViewChange={setCurrentView}
    >
      {renderView()}
    </DashboardLayout>
  );
}

export default App;