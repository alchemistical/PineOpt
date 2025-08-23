import React, { useState, useEffect } from 'react';
import { 
  Play, 
  Settings, 
  Calendar,
  TrendingUp,
  BarChart3,
  DollarSign,
  Clock,
  Zap,
  Target,
  AlertCircle,
  CheckCircle2,
  Loader2,
  RefreshCw,
  Sliders,
  Database
} from 'lucide-react';
import ParameterInterface from './ParameterInterface';

interface Strategy {
  id: string;
  name: string;
  description: string;
  author: string;
  parameters_count: number;
  validation_status: string;
  tags: string[];
  parameters?: StrategyParameter[];
}

interface StrategyParameter {
  name: string;
  default: number | string | boolean;
  min_val?: number;
  max_val?: number;
  step?: number;
  options?: string[];
  description?: string;
  type?: string;
}

interface BacktestConfig {
  strategy_id: string;
  symbol: string;
  exchange: string;
  timeframe: string;
  start_date: string;
  end_date: string;
  initial_balance: number;
  position_size_percent: number;
  commission: number;
  engine: 'pineopt' | 'jesse';
  strategy_parameters?: Record<string, any>;
}

interface EnhancedBacktestInterfaceProps {
  onBacktestStart?: (config: BacktestConfig) => void;
  onResultsReady?: (results: any) => void;
}

const EnhancedBacktestInterface: React.FC<EnhancedBacktestInterfaceProps> = ({
  onBacktestStart,
  onResultsReady
}) => {
  const [strategies, setStrategies] = useState<Strategy[]>([]);
  const [loading, setLoading] = useState(false);
  const [backtestRunning, setBacktestRunning] = useState(false);
  const [showParameterInterface, setShowParameterInterface] = useState(false);
  
  // Configuration state
  const [selectedStrategy, setSelectedStrategy] = useState<string>('');
  const [selectedStrategyData, setSelectedStrategyData] = useState<Strategy | null>(null);
  const [symbol, setSymbol] = useState('BTCUSDT');
  const [exchange, setExchange] = useState('BINANCE');
  const [timeframe, setTimeframe] = useState('1h');
  const [startDate, setStartDate] = useState('2024-01-01');
  const [endDate, setEndDate] = useState('2024-12-31');
  const [initialBalance, setInitialBalance] = useState(10000);
  const [positionSize, setPositionSize] = useState(10);
  const [commission, setCommission] = useState(0.1);
  const [engine, setEngine] = useState<'pineopt' | 'jesse'>('pineopt');
  const [strategyParameters, setStrategyParameters] = useState<Record<string, any>>({});

  const cryptoPairs = [
    'BTCUSDT', 'ETHUSDT', 'ADAUSDT', 'DOTUSDT', 'LINKUSDT', 'SOLUSDT',
    'MATICUSDT', 'AVAXUSDT', 'ATOMUSDT', 'ALGOUSDT', 'XRPUSDT', 'BNBUSDT'
  ];

  const timeframes = [
    { value: '1m', label: '1 Minute' },
    { value: '5m', label: '5 Minutes' },
    { value: '15m', label: '15 Minutes' },
    { value: '1h', label: '1 Hour' },
    { value: '4h', label: '4 Hours' },
    { value: '1d', label: '1 Day' },
    { value: '1w', label: '1 Week' }
  ];

  const exchanges = ['BINANCE', 'COINBASE', 'KRAKEN', 'BYBIT'];

  useEffect(() => {
    loadStrategies();
  }, []);

  useEffect(() => {
    if (selectedStrategy) {
      loadStrategyParameters(selectedStrategy);
    }
  }, [selectedStrategy]);

  const loadStrategies = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:5007/api/strategies');
      const data = await response.json();
      
      if (data.strategies) {
        const validStrategies = data.strategies.filter((s: Strategy) => 
          s.validation_status === 'valid'
        );
        setStrategies(validStrategies);
        
        // Auto-select HYE strategy if available
        const hyeStrategy = validStrategies.find((s: Strategy) => 
          s.name.toLowerCase().includes('hye')
        );
        if (hyeStrategy) {
          setSelectedStrategy(hyeStrategy.id);
        }
      }
    } catch (error) {
      console.error('Failed to load strategies:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadStrategyParameters = async (strategyId: string) => {
    try {
      const response = await fetch(`http://localhost:5007/api/parameters/strategy/${strategyId}`);
      const data = await response.json();
      
      if (data.success && data.parameters) {
        const strategy = strategies.find(s => s.id === strategyId);
        if (strategy) {
          const enhancedStrategy = {
            ...strategy,
            parameters: data.parameters
          };
          setSelectedStrategyData(enhancedStrategy);
          
          // Set default parameter values
          const defaultParams: Record<string, any> = {};
          data.parameters.forEach((param: StrategyParameter) => {
            defaultParams[param.name] = param.default;
          });
          setStrategyParameters(defaultParams);
        }
      }
    } catch (error) {
      console.error('Failed to load strategy parameters:', error);
      // Fallback to basic strategy data
      const strategy = strategies.find(s => s.id === strategyId);
      if (strategy) {
        setSelectedStrategyData(strategy);
      }
    }
  };

  const handleParametersChange = (parameters: Record<string, any>) => {
    setStrategyParameters(parameters);
  };

  const handleRunBacktest = async (customParameters?: Record<string, any>) => {
    if (!selectedStrategy) {
      alert('Please select a strategy');
      return;
    }

    const config: BacktestConfig = {
      strategy_id: selectedStrategy,
      symbol,
      exchange,
      timeframe,
      start_date: startDate,
      end_date: endDate,
      initial_balance: initialBalance,
      position_size_percent: positionSize,
      commission: commission / 100,
      engine,
      strategy_parameters: customParameters || strategyParameters
    };

    try {
      setBacktestRunning(true);
      
      if (onBacktestStart) {
        onBacktestStart(config);
      }

      // Enhanced backtest API call with strategy parameters
      const response = await fetch('http://localhost:5007/api/backtests/run', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          strategy_id: config.strategy_id,
          symbol: config.symbol,
          timeframe: config.timeframe,
          start_date: config.start_date,
          end_date: config.end_date,
          initial_capital: config.initial_balance,
          commission_rate: config.commission,
          slippage_rate: 0.0001,
          max_position_size_pct: config.position_size_percent,
          risk_per_trade_pct: 2.0,
          strategy_params: config.strategy_parameters || {}
        }),
      });

      if (!response.ok) {
        throw new Error(`Backtest failed: ${response.statusText}`);
      }

      const result = await response.json();
      
      if (onResultsReady && result.success) {
        // Transform API response
        const transformedResult = {
          id: result.backtest_id || 'backtest-' + Date.now(),
          strategy_id: config.strategy_id,
          strategy_name: selectedStrategyData?.name || 'Unknown Strategy',
          start_date: config.start_date,
          end_date: config.end_date,
          initial_capital: config.initial_balance,
          final_capital: config.initial_balance * (1 + (result.portfolio_metrics?.total_return_pct || 0) / 100),
          status: 'completed' as const,
          metrics: {
            total_return: result.portfolio_metrics?.total_return_pct ? (config.initial_balance * result.portfolio_metrics.total_return_pct / 100) : 0,
            total_return_percentage: result.portfolio_metrics?.total_return_pct || 0,
            annualized_return: result.portfolio_metrics?.annualized_return_pct || 0,
            max_drawdown: result.portfolio_metrics?.max_drawdown_pct || 0,
            sharpe_ratio: result.portfolio_metrics?.sharpe_ratio || 0,
            sortino_ratio: 0,
            win_rate: result.portfolio_metrics?.win_rate_pct || 0,
            profit_factor: result.portfolio_metrics?.profit_factor || 0,
            total_trades: result.portfolio_metrics?.total_trades || 0,
            winning_trades: 0,
            losing_trades: 0,
            avg_win: 0,
            avg_loss: 0,
            largest_win: 0,
            largest_loss: 0,
            avg_trade_duration: 0,
            volatility: result.portfolio_metrics?.volatility_pct || 0,
            var_95: result.risk_metrics?.var_95_pct || 0,
            calmar_ratio: 0,
            sterling_ratio: 0
          },
          trades: [],
          equity_curve: [],
          drawdown_curve: [],
          price_data: [],
          created_at: new Date().toISOString(),
          execution_time_ms: result.execution_time_seconds ? result.execution_time_seconds * 1000 : 0,
          strategy_parameters: config.strategy_parameters
        };
        
        onResultsReady(transformedResult);
      } else if (!result.success) {
        throw new Error(result.error || 'Backtest failed');
      }

    } catch (error) {
      console.error('Backtest failed:', error);
      alert(`Backtest failed: ${error}`);
    } finally {
      setBacktestRunning(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Strategy Selection */}
      <div className="bg-gray-800 rounded-xl border border-gray-600 overflow-hidden">
        <div className="bg-gray-700 px-6 py-4 border-b border-gray-600">
          <h2 className="text-xl font-semibold text-white flex items-center space-x-2">
            <BarChart3 className="h-6 w-6 text-blue-400" />
            <span>Enhanced Strategy Backtesting</span>
          </h2>
          <p className="text-gray-400 mt-1">
            AI-powered backtesting with dynamic parameter configuration
          </p>
        </div>

        <div className="p-6 space-y-6">
          {/* Strategy Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-3">
              Select Strategy
            </label>
            {loading ? (
              <div className="flex items-center space-x-2 text-gray-400">
                <Loader2 className="h-4 w-4 animate-spin" />
                <span>Loading strategies...</span>
              </div>
            ) : (
              <div className="space-y-2">
                <select
                  value={selectedStrategy}
                  onChange={(e) => setSelectedStrategy(e.target.value)}
                  className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="">Choose a strategy...</option>
                  {strategies.map((strategy) => (
                    <option key={strategy.id} value={strategy.id}>
                      {strategy.name} ({strategy.parameters_count || 0} parameters)
                    </option>
                  ))}
                </select>
                
                {selectedStrategyData && (
                  <div className="mt-3 p-3 bg-gray-700 rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="text-white font-medium">{selectedStrategyData.name}</h4>
                      <div className="flex items-center space-x-2">
                        <CheckCircle2 className="h-4 w-4 text-green-400" />
                        <span className="text-xs text-green-400">Valid</span>
                      </div>
                    </div>
                    <p className="text-gray-400 text-sm">{selectedStrategyData.description}</p>
                    <div className="flex items-center justify-between mt-2">
                      <div className="flex items-center space-x-4 text-xs text-gray-500">
                        <span>By {selectedStrategyData.author}</span>
                        <span>{selectedStrategyData.parameters?.length || 0} parameters</span>
                      </div>
                      
                      {selectedStrategyData.parameters && selectedStrategyData.parameters.length > 0 && (
                        <button
                          onClick={() => setShowParameterInterface(!showParameterInterface)}
                          className="flex items-center space-x-1 px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white text-xs rounded-lg transition-colors"
                        >
                          <Sliders className="h-3 w-3" />
                          <span>{showParameterInterface ? 'Hide' : 'Show'} Parameters</span>
                        </button>
                      )}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Parameter Interface */}
          {showParameterInterface && selectedStrategyData && selectedStrategyData.parameters && (
            <div className="border border-gray-600 rounded-lg p-1">
              <ParameterInterface
                strategy={{
                  id: selectedStrategyData.id,
                  name: selectedStrategyData.name,
                  parameters: selectedStrategyData.parameters
                }}
                onParametersChange={handleParametersChange}
                onRunBacktest={handleRunBacktest}
                isLoading={backtestRunning}
              />
            </div>
          )}

          {/* Market Configuration */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Trading Pair
              </label>
              <select
                value={symbol}
                onChange={(e) => setSymbol(e.target.value)}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-blue-500"
              >
                {cryptoPairs.map(pair => (
                  <option key={pair} value={pair}>{pair}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Exchange
              </label>
              <select
                value={exchange}
                onChange={(e) => setExchange(e.target.value)}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-blue-500"
              >
                {exchanges.map(ex => (
                  <option key={ex} value={ex}>{ex}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Timeframe
              </label>
              <select
                value={timeframe}
                onChange={(e) => setTimeframe(e.target.value)}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-blue-500"
              >
                {timeframes.map(tf => (
                  <option key={tf.value} value={tf.value}>{tf.label}</option>
                ))}
              </select>
            </div>
          </div>

          {/* Date Range & Risk Management */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Start Date
              </label>
              <input
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-blue-500"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                End Date
              </label>
              <input
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Initial Balance ($)
              </label>
              <input
                type="number"
                value={initialBalance}
                onChange={(e) => setInitialBalance(Number(e.target.value))}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-blue-500"
                min="100"
                step="100"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Commission (%)
              </label>
              <input
                type="number"
                value={commission}
                onChange={(e) => setCommission(Number(e.target.value))}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-blue-500"
                min="0"
                max="1"
                step="0.01"
              />
            </div>
          </div>

          {/* Engine Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-3">
              Backtest Engine
            </label>
            <div className="flex space-x-4">
              <button
                onClick={() => setEngine('pineopt')}
                className={`flex items-center space-x-2 px-4 py-3 rounded-lg border transition-colors ${
                  engine === 'pineopt' 
                    ? 'bg-blue-600 border-blue-500 text-white' 
                    : 'bg-gray-700 border-gray-600 text-gray-300 hover:bg-gray-600'
                }`}
              >
                <BarChart3 className="h-4 w-4" />
                <span>PineOpt AI</span>
              </button>
              
              <button
                onClick={() => setEngine('jesse')}
                className={`flex items-center space-x-2 px-4 py-3 rounded-lg border transition-colors ${
                  engine === 'jesse' 
                    ? 'bg-purple-600 border-purple-500 text-white' 
                    : 'bg-gray-700 border-gray-600 text-gray-300 hover:bg-gray-600'
                }`}
              >
                <Zap className="h-4 w-4" />
                <span>Jesse Pro</span>
              </button>
            </div>
          </div>

          {/* Run Button */}
          {!showParameterInterface && (
            <div className="flex justify-center pt-4">
              <button
                onClick={() => handleRunBacktest()}
                disabled={backtestRunning || !selectedStrategy}
                className="flex items-center space-x-2 px-8 py-3 bg-green-600 hover:bg-green-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white font-medium rounded-lg transition-colors"
              >
                {backtestRunning ? (
                  <>
                    <Loader2 className="h-5 w-5 animate-spin" />
                    <span>Running Backtest...</span>
                  </>
                ) : (
                  <>
                    <Play className="h-5 w-5" />
                    <span>Run Backtest</span>
                  </>
                )}
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default EnhancedBacktestInterface;