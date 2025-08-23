import React, { useState } from 'react';
import { ArrowLeft } from 'lucide-react';
import BacktestInterface from './BacktestInterface';
import BacktestResults from './BacktestResults';

interface BacktestPageProps {
  onBack?: () => void;
}

const BacktestPage: React.FC<BacktestPageProps> = ({ onBack }) => {
  const [currentView, setCurrentView] = useState<'configure' | 'results'>('configure');
  const [backtestResult, setBacktestResult] = useState<any>(null);
  const [backtestConfig, setBacktestConfig] = useState<any>(null);

  const handleBacktestStart = (config: any) => {
    console.log('🚀 Starting backtest with config:', config);
    setBacktestConfig(config);
    // Don't switch views yet - wait for results
  };

  const handleResultsReady = (result: any) => {
    console.log('✅ Backtest results ready:', result);
    setBacktestResult(result);
    setCurrentView('results');
  };

  const handleBackToConfig = () => {
    setCurrentView('configure');
    setBacktestResult(null);
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Header */}
      <div className="border-b border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between py-4">
            <div className="flex items-center space-x-4">
              {onBack && (
                <button
                  onClick={onBack}
                  className="flex items-center space-x-2 text-gray-400 hover:text-white transition-colors"
                >
                  <ArrowLeft className="h-5 w-5" />
                  <span>Back</span>
                </button>
              )}
              <div>
                <h1 className="text-2xl font-bold">
                  {currentView === 'configure' ? 'Configure Backtest' : 'Backtest Results'}
                </h1>
                <p className="text-gray-400 mt-1">
                  {currentView === 'configure' 
                    ? 'Select strategy, trading pair, and timeframe to run backtest'
                    : 'Analysis of strategy performance on historical data'
                  }
                </p>
              </div>
            </div>

            {/* Navigation */}
            {currentView === 'results' && (
              <button
                onClick={handleBackToConfig}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors"
              >
                New Backtest
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {currentView === 'configure' ? (
          <BacktestInterface
            onBacktestStart={handleBacktestStart}
            onResultsReady={handleResultsReady}
          />
        ) : (
          backtestResult && (
            <BacktestResults
              result={backtestResult}
              onClose={handleBackToConfig}
            />
          )
        )}
      </div>
    </div>
  );
};

export default BacktestPage;