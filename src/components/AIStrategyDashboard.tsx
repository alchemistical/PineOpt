import React, { useState, useEffect } from 'react';
import { 
  Upload, 
  Brain, 
  Zap,
  Play, 
  TrendingUp,
  BarChart3,
  DollarSign,
  Clock,
  Target,
  CheckCircle2,
  AlertCircle,
  Loader2,
  Settings,
  Code,
  Sparkles,
  Bot,
  Activity,
  Cpu,
  Database,
  Eye,
  Sliders
} from 'lucide-react';

interface ConversionResult {
  success: boolean;
  python_code?: string;
  parameters?: Array<{
    name: string;
    default: number | string | boolean;
    min_val?: number;
    max_val?: number;
    description?: string;
  }>;
  analysis_summary?: {
    parameters_extracted: number;
    indicators_found: number;
    conversion_steps: number;
    vwap_periods?: Record<string, number>;
  };
  error?: string;
}

interface BacktestResult {
  success: boolean;
  backtest_results?: {
    symbol: string;
    timeframe: string;
    data_points: number;
    date_range: {
      start: string;
      end: string;
    };
    results: {
      initial_capital: number;
      final_value: number;
      total_return_pct: number;
      total_trades: number;
      win_rate_pct: number;
      sharpe_ratio: number;
      max_drawdown_pct: number;
      volatility_pct: number;
      signals_generated: {
        total_entry_signals: number;
        total_exit_signals: number;
      };
      trades: Array<{
        type: string;
        timestamp: string;
        price: number;
        quantity: number;
        value: number;
      }>;
      equity_curve: Array<{
        timestamp: string;
        equity: number;
        position: number;
        cash: number;
      }>;
    };
  };
  conversion_summary?: {
    parameters_extracted: number;
    indicators_found: number;
    conversion_steps: number;
  };
  error?: string;
}

const AIStrategyDashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'upload' | 'convert' | 'backtest' | 'results'>('upload');
  const [pineCode, setPineCode] = useState('');
  const [strategyName, setStrategyName] = useState('');
  const [isConverting, setIsConverting] = useState(false);
  const [isBacktesting, setIsBacktesting] = useState(false);
  const [conversionResult, setConversionResult] = useState<ConversionResult | null>(null);
  const [backtestResult, setBacktestResult] = useState<BacktestResult | null>(null);
  const [customParameters, setCustomParameters] = useState<Record<string, any>>({});
  const [isSaving, setIsSaving] = useState(false);
  const [saveMessage, setSaveMessage] = useState<string>('');

  // Backtest configuration
  const [symbol, setSymbol] = useState('BTCUSDT');
  const [timeframe, setTimeframe] = useState('1h');
  const [startDate, setStartDate] = useState('2024-01-01');
  const [endDate, setEndDate] = useState('2024-12-31');
  const [initialCapital, setInitialCapital] = useState(10000);

  const availablePairs = [
    { symbol: 'BTCUSDT', name: 'Bitcoin/USDT', icon: '₿' },
    { symbol: 'ETHUSDT', name: 'Ethereum/USDT', icon: 'Ξ' },
    { symbol: 'SOLUSDT', name: 'Solana/USDT', icon: '◎' },
    { symbol: 'ADAUSDT', name: 'Cardano/USDT', icon: '♠' },
    { symbol: 'DOTUSDT', name: 'Polkadot/USDT', icon: '●' },
    { symbol: 'LINKUSDT', name: 'Chainlink/USDT', icon: '🔗' },
    { symbol: 'MATICUSDT', name: 'Polygon/USDT', icon: '⬢' },
    { symbol: 'AVAXUSDT', name: 'Avalanche/USDT', icon: '🔺' }
  ];

  const timeframes = [
    { id: '15m', name: '15 Minutes', recommended: true },
    { id: '1h', name: '1 Hour', recommended: true },
    { id: '4h', name: '4 Hours', recommended: true },
    { id: '1d', name: '1 Day', recommended: true }
  ];

  const sampleStrategies = [
    {
      name: 'HYE Combo Market Strategy',
      description: 'VWAP Mean Reversion + Trend Hunter with 16 parameters',
      code: `// @version=4
strategy("HYE Combo Market [Strategy] (Vwap Mean Reversion + Trend Hunter)", overlay = true)

//Strategy inputs
source = input(title = "Source", defval = close, group = "Mean Reversion Strategy Inputs")
smallcumulativePeriod = input(title = "Small VWAP", defval = 8, group = "Mean Reversion Strategy Inputs")
bigcumulativePeriod = input(title = "Big VWAP", defval = 10, group = "Mean Reversion Strategy Inputs")
meancumulativePeriod = input(title = "Mean VWAP", defval = 50, group = "Mean Reversion Strategy Inputs")
percentBelowToBuy = input(title = "Percent below to buy %", defval = 2, group = "Mean Reversion Strategy Inputs")
rsiPeriod = input(title = "Rsi Period", defval = 2, group = "Mean Reversion Strategy Inputs")
rsiEmaPeriod = input(title = "Rsi Ema Period", defval = 5, group = "Mean Reversion Strategy Inputs")
rsiLevelforBuy = input(title = "Maximum Rsi Level for Buy", defval = 30, group = "Mean Reversion Strategy Inputs")

// Mean Reversion Logic
typicalPriceS = (high + low + close) / 3
typicalPriceVolumeS = typicalPriceS * volume
cumulativeTypicalPriceVolumeS = sum(typicalPriceVolumeS, smallcumulativePeriod)
cumulativeVolumeS = sum(volume, smallcumulativePeriod)
smallvwapValue = cumulativeTypicalPriceVolumeS / cumulativeVolumeS

rsiValue = rsi(source, rsiPeriod)
rsiEMA = ema(rsiValue, rsiEmaPeriod)
buyMA = ((100 - percentBelowToBuy) / 100) * smallvwapValue[0]

if(crossunder(smallvwapValue, buyMA) and rsiEMA < rsiLevelforBuy)
    strategy.entry("BUY-M", strategy.long)

if(close > smallvwapValue)
    strategy.close("BUY-M")`
    },
    {
      name: 'Simple RSI Strategy',
      description: 'Basic RSI oversold/overbought strategy',
      code: `// @version=4
strategy("Simple RSI Strategy", overlay=false)

rsi_period = input(14, title="RSI Period")
rsi_oversold = input(30, title="RSI Oversold")
rsi_overbought = input(70, title="RSI Overbought")

rsi_val = rsi(close, rsi_period)

if rsi_val < rsi_oversold
    strategy.entry("Long", strategy.long)

if rsi_val > rsi_overbought
    strategy.close("Long")`
    },
    {
      name: 'VWAP Mean Reversion',
      description: 'Buy below VWAP, sell above',
      code: `// @version=4
strategy("VWAP Mean Reversion", overlay=true)

vwap_period = input(20, title="VWAP Period")
deviation_pct = input(2.0, title="Deviation %")

vwap_val = vwap
buy_level = vwap_val * (1 - deviation_pct / 100)

if close < buy_level
    strategy.entry("Long", strategy.long)

if close > vwap_val
    strategy.close("Long")`
    }
  ];

  const convertStrategy = async () => {
    if (!pineCode.trim()) {
      alert('Please enter Pine Script code');
      return;
    }

    setIsConverting(true);
    setConversionResult(null);

    try {
      const response = await fetch('http://127.0.0.1:5007/api/intelligent-conversion/convert/hye', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          pine_code: pineCode,
          strategy_name: strategyName || 'ConvertedStrategy'
        }),
      });

      const result = await response.json();
      setConversionResult(result);
      
      if (result.success) {
        // Initialize custom parameters with defaults
        const defaultParams: Record<string, any> = {};
        result.parameters?.forEach(param => {
          defaultParams[param.name] = param.default;
        });
        setCustomParameters(defaultParams);
        setActiveTab('convert');
      }
    } catch (error) {
      setConversionResult({
        success: false,
        error: `Conversion failed: ${error}`
      });
    } finally {
      setIsConverting(false);
    }
  };

  const runBacktest = async () => {
    if (!conversionResult?.success) {
      alert('Please convert a strategy first');
      return;
    }

    setIsBacktesting(true);
    setBacktestResult(null);

    try {
      const response = await fetch('http://127.0.0.1:5007/api/real-backtest/convert-and-backtest', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          pine_code: pineCode,
          strategy_name: strategyName || 'ConvertedStrategy',
          symbol,
          timeframe,
          start_date: startDate,
          end_date: endDate,
          initial_capital: initialCapital,
          custom_parameters: customParameters
        }),
      });

      const result = await response.json();
      setBacktestResult(result);
      
      if (result.success) {
        setActiveTab('results');
      }
    } catch (error) {
      setBacktestResult({
        success: false,
        error: `Backtest failed: ${error}`
      });
    } finally {
      setIsBacktesting(false);
    }
  };

  const saveStrategy = async () => {
    if (!conversionResult?.success || !conversionResult.python_code) {
      alert('Please convert a strategy first');
      return;
    }

    setIsSaving(true);
    setSaveMessage('');

    try {
      const response = await fetch('http://localhost:5007/api/strategies', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: strategyName || 'Converted Strategy',
          description: `AI-converted Pine Script strategy`,
          pine_source: pineCode,
          python_code: conversionResult.python_code,
          parameters: JSON.stringify(customParameters),
          created_at: new Date().toISOString()
        }),
      });

      if (!response.ok) {
        throw new Error(`Save failed: ${response.statusText}`);
      }

      const savedStrategy = await response.json();
      setSaveMessage(`Strategy '${strategyName}' saved successfully! ID: ${savedStrategy.id}`);
    } catch (error) {
      setSaveMessage(`Failed to save strategy: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setIsSaving(false);
    }
  };

  const loadSampleStrategy = (sample: typeof sampleStrategies[0]) => {
    setPineCode(sample.code);
    setStrategyName(sample.name);
    setConversionResult(null);
    setBacktestResult(null);
    setCustomParameters({});
    setSaveMessage('');
    setActiveTab('upload');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-blue-900">
      {/* Header */}
      <div className="bg-gray-800 border-b border-gray-700">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="flex items-center space-x-2">
                <Bot className="h-8 w-8 text-blue-400" />
                <Sparkles className="h-6 w-6 text-yellow-400" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-white">AI Strategy Lab</h1>
                <p className="text-gray-400 text-sm">Intelligent Pine Script to Python Conversion & Real Data Backtesting</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2 text-green-400">
                <Database className="h-4 w-4" />
                <span className="text-sm">Real Market Data</span>
              </div>
              <div className="flex items-center space-x-2 text-blue-400">
                <Cpu className="h-4 w-4" />
                <span className="text-sm">AI Powered</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="max-w-7xl mx-auto px-6 py-4">
        <div className="flex space-x-4 mb-6">
          {[
            { id: 'upload', label: '1. Upload Strategy', icon: Upload },
            { id: 'convert', label: '2. AI Analysis', icon: Brain },
            { id: 'backtest', label: '3. Configure Backtest', icon: Settings },
            { id: 'results', label: '4. Results', icon: BarChart3 }
          ].map(tab => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            const isCompleted = 
              (tab.id === 'upload' && pineCode) ||
              (tab.id === 'convert' && conversionResult?.success) ||
              (tab.id === 'backtest' && backtestResult) ||
              (tab.id === 'results' && backtestResult?.success);

            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`flex items-center space-x-2 px-4 py-3 rounded-lg font-medium transition-all ${
                  isActive 
                    ? 'bg-blue-600 text-white shadow-lg' 
                    : isCompleted
                      ? 'bg-green-600/20 text-green-400 hover:bg-green-600/30'
                      : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                }`}
              >
                <Icon className="h-4 w-4" />
                <span>{tab.label}</span>
                {isCompleted && <CheckCircle2 className="h-4 w-4" />}
              </button>
            );
          })}
        </div>

        {/* Tab Content */}
        <div className="grid grid-cols-12 gap-6">
          
          {/* Main Content */}
          <div className="col-span-8">
            
            {/* Upload Tab */}
            {activeTab === 'upload' && (
              <div className="bg-gray-800 rounded-xl border border-gray-600 p-6">
                <div className="flex items-center space-x-3 mb-6">
                  <Upload className="h-6 w-6 text-blue-400" />
                  <h2 className="text-xl font-semibold text-white">Upload Pine Script Strategy</h2>
                </div>

                {/* Sample Strategies */}
                <div className="mb-6">
                  <h3 className="text-sm font-medium text-gray-300 mb-3">Quick Start - Sample Strategies</h3>
                  <div className="grid grid-cols-1 gap-3">
                    {sampleStrategies.map((sample, index) => (
                      <button
                        key={index}
                        onClick={() => loadSampleStrategy(sample)}
                        className="text-left p-4 bg-gray-700 rounded-lg hover:bg-gray-600 transition-colors border border-gray-600"
                      >
                        <div className="flex items-center justify-between">
                          <div>
                            <h4 className="text-white font-medium">{sample.name}</h4>
                            <p className="text-gray-400 text-sm">{sample.description}</p>
                          </div>
                          <Eye className="h-4 w-4 text-gray-400" />
                        </div>
                      </button>
                    ))}
                  </div>
                </div>

                {/* Strategy Input */}
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Strategy Name (optional)
                    </label>
                    <input
                      type="text"
                      value={strategyName}
                      onChange={(e) => setStrategyName(e.target.value)}
                      placeholder="My Custom Strategy"
                      className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Pine Script Code
                    </label>
                    <textarea
                      value={pineCode}
                      onChange={(e) => {
                        setPineCode(e.target.value);
                        // Clear previous results when code changes
                        if (conversionResult || backtestResult) {
                          setConversionResult(null);
                          setBacktestResult(null);
                          setCustomParameters({});
                        }
                      }}
                      placeholder="// @version=4&#10;strategy(&quot;My Strategy&quot;, overlay=true)&#10;&#10;// Your strategy logic here..."
                      rows={12}
                      className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white font-mono text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                    />
                  </div>

                  <button
                    onClick={convertStrategy}
                    disabled={isConverting || !pineCode.trim()}
                    className="w-full flex items-center justify-center space-x-2 py-3 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 disabled:from-gray-600 disabled:to-gray-700 disabled:cursor-not-allowed text-white font-medium rounded-lg transition-all"
                  >
                    {isConverting ? (
                      <>
                        <Loader2 className="h-4 w-4 animate-spin" />
                        <span>Converting with AI...</span>
                      </>
                    ) : (
                      <>
                        <Brain className="h-4 w-4" />
                        <span>Convert with AI</span>
                        <Sparkles className="h-4 w-4" />
                      </>
                    )}
                  </button>
                </div>
              </div>
            )}

            {/* Convert Tab */}
            {activeTab === 'convert' && conversionResult && (
              <div className="space-y-6">
                {conversionResult.success ? (
                  <>
                    {/* Analysis Summary */}
                    <div className="bg-gradient-to-r from-green-600/20 to-blue-600/20 rounded-xl border border-green-500/30 p-6">
                      <div className="flex items-center space-x-3 mb-4">
                        <CheckCircle2 className="h-6 w-6 text-green-400" />
                        <h2 className="text-xl font-semibold text-white">AI Analysis Complete</h2>
                      </div>
                      
                      <div className="grid grid-cols-3 gap-4 mb-4">
                        <div className="text-center p-4 bg-gray-800/50 rounded-lg">
                          <div className="text-2xl font-bold text-blue-400">
                            {conversionResult.analysis_summary?.parameters_extracted || 0}
                          </div>
                          <div className="text-sm text-gray-300">Parameters Extracted</div>
                        </div>
                        <div className="text-center p-4 bg-gray-800/50 rounded-lg">
                          <div className="text-2xl font-bold text-purple-400">
                            {conversionResult.analysis_summary?.indicators_found || 0}
                          </div>
                          <div className="text-sm text-gray-300">Indicators Found</div>
                        </div>
                        <div className="text-center p-4 bg-gray-800/50 rounded-lg">
                          <div className="text-2xl font-bold text-yellow-400">
                            {conversionResult.analysis_summary?.conversion_steps || 0}
                          </div>
                          <div className="text-sm text-gray-300">Conversion Steps</div>
                        </div>
                      </div>

                      {conversionResult.analysis_summary?.vwap_periods && (
                        <div className="bg-gray-800/30 rounded-lg p-4">
                          <h3 className="text-sm font-medium text-gray-300 mb-2">VWAP Periods Detected</h3>
                          <div className="flex space-x-4 text-sm">
                            {Object.entries(conversionResult.analysis_summary.vwap_periods).map(([key, value]) => (
                              <span key={key} className="text-blue-400">
                                {key}: {value}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>

                    {/* Parameter Configuration */}
                    {conversionResult.parameters && conversionResult.parameters.length > 0 && (
                      <div className="bg-gray-800 rounded-xl border border-gray-600 p-6">
                        <div className="flex items-center space-x-3 mb-4">
                          <Sliders className="h-6 w-6 text-blue-400" />
                          <h3 className="text-lg font-semibold text-white">Strategy Parameters</h3>
                        </div>

                        <div className="grid grid-cols-2 gap-4">
                          {conversionResult.parameters.map(param => (
                            <div key={param.name} className="space-y-2">
                              <label className="block text-sm font-medium text-gray-300">
                                {param.name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                                {param.description && (
                                  <span className="text-gray-500 text-xs ml-2">({param.description})</span>
                                )}
                              </label>
                              <input
                                type="number"
                                value={customParameters[param.name] || param.default}
                                onChange={(e) => setCustomParameters(prev => ({
                                  ...prev,
                                  [param.name]: parseFloat(e.target.value) || param.default
                                }))}
                                min={param.min_val}
                                max={param.max_val}
                                step="any"
                                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-blue-500"
                              />
                              <div className="text-xs text-gray-500 flex justify-between">
                                <span>Default: {String(param.default)}</span>
                                {param.min_val !== undefined && param.max_val !== undefined && (
                                  <span>Range: {param.min_val} - {param.max_val}</span>
                                )}
                              </div>
                            </div>
                          ))}
                        </div>

                        <div className="mt-6 space-y-3">
                          <div className="flex space-x-3">
                            <button
                              onClick={saveStrategy}
                              disabled={isSaving}
                              className="flex-1 flex items-center justify-center space-x-2 py-3 bg-green-600 hover:bg-green-700 disabled:bg-green-600/50 text-white font-medium rounded-lg transition-colors"
                            >
                              {isSaving ? (
                                <>
                                  <Loader2 className="h-4 w-4 animate-spin" />
                                  <span>Saving...</span>
                                </>
                              ) : (
                                <>
                                  <Database className="h-4 w-4" />
                                  <span>Save Strategy</span>
                                </>
                              )}
                            </button>
                            <button
                              onClick={() => setActiveTab('backtest')}
                              className="flex-1 flex items-center justify-center space-x-2 py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors"
                            >
                              <Settings className="h-4 w-4" />
                              <span>Configure Backtest</span>
                            </button>
                          </div>
                          
                          {saveMessage && (
                            <div className={`p-3 rounded-lg ${
                              saveMessage.includes('successfully') 
                                ? 'bg-green-600/20 border border-green-500/30 text-green-400'
                                : 'bg-red-600/20 border border-red-500/30 text-red-400'
                            }`}>
                              {saveMessage}
                            </div>
                          )}
                        </div>
                      </div>
                    )}
                  </>
                ) : (
                  <div className="bg-red-600/20 rounded-xl border border-red-500/30 p-6">
                    <div className="flex items-center space-x-3">
                      <AlertCircle className="h-6 w-6 text-red-400" />
                      <div>
                        <h3 className="text-lg font-semibold text-red-400">Conversion Failed</h3>
                        <p className="text-red-300">{conversionResult.error}</p>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Backtest Tab */}
            {activeTab === 'backtest' && (
              <div className="bg-gray-800 rounded-xl border border-gray-600 p-6">
                <div className="flex items-center space-x-3 mb-6">
                  <Settings className="h-6 w-6 text-blue-400" />
                  <h2 className="text-xl font-semibold text-white">Configure Real Data Backtest</h2>
                </div>

                <div className="grid grid-cols-2 gap-6">
                  {/* Trading Pair */}
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-3">Trading Pair</label>
                    <div className="grid grid-cols-2 gap-2">
                      {availablePairs.map(pair => (
                        <button
                          key={pair.symbol}
                          onClick={() => setSymbol(pair.symbol)}
                          className={`p-3 rounded-lg border transition-all ${
                            symbol === pair.symbol
                              ? 'border-blue-500 bg-blue-600/20 text-blue-400'
                              : 'border-gray-600 bg-gray-700 text-gray-300 hover:border-gray-500'
                          }`}
                        >
                          <div className="flex items-center space-x-2">
                            <span className="text-lg">{pair.icon}</span>
                            <div className="text-left">
                              <div className="font-medium text-sm">{pair.symbol}</div>
                              <div className="text-xs text-gray-400">{pair.name.split('/')[0]}</div>
                            </div>
                          </div>
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Timeframe */}
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-3">Timeframe</label>
                    <div className="space-y-2">
                      {timeframes.map(tf => (
                        <button
                          key={tf.id}
                          onClick={() => setTimeframe(tf.id)}
                          className={`w-full p-3 rounded-lg border transition-all flex items-center justify-between ${
                            timeframe === tf.id
                              ? 'border-blue-500 bg-blue-600/20 text-blue-400'
                              : 'border-gray-600 bg-gray-700 text-gray-300 hover:border-gray-500'
                          }`}
                        >
                          <span>{tf.name}</span>
                          {tf.recommended && <span className="text-xs bg-green-600/20 text-green-400 px-2 py-1 rounded">Recommended</span>}
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Date Range */}
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">Start Date</label>
                    <input
                      type="date"
                      value={startDate}
                      onChange={(e) => setStartDate(e.target.value)}
                      className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-blue-500"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">End Date</label>
                    <input
                      type="date"
                      value={endDate}
                      onChange={(e) => setEndDate(e.target.value)}
                      className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-blue-500"
                    />
                  </div>

                  {/* Initial Capital */}
                  <div className="col-span-2">
                    <label className="block text-sm font-medium text-gray-300 mb-2">Initial Capital (USDT)</label>
                    <input
                      type="number"
                      value={initialCapital}
                      onChange={(e) => setInitialCapital(parseFloat(e.target.value) || 10000)}
                      min={100}
                      step={100}
                      className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                </div>

                <button
                  onClick={runBacktest}
                  disabled={isBacktesting || !conversionResult?.success}
                  className="mt-6 w-full flex items-center justify-center space-x-2 py-4 bg-gradient-to-r from-green-600 to-blue-600 hover:from-green-700 hover:to-blue-700 disabled:from-gray-600 disabled:to-gray-700 disabled:cursor-not-allowed text-white font-medium rounded-lg transition-all text-lg"
                >
                  {isBacktesting ? (
                    <>
                      <Loader2 className="h-5 w-5 animate-spin" />
                      <span>Running Backtest with Real Data...</span>
                    </>
                  ) : (
                    <>
                      <Play className="h-5 w-5" />
                      <span>Run Real Data Backtest</span>
                      <Activity className="h-5 w-5" />
                    </>
                  )}
                </button>
              </div>
            )}

            {/* Results Tab */}
            {activeTab === 'results' && backtestResult && (
              <div className="space-y-6">
                {backtestResult.success && backtestResult.backtest_results ? (
                  <>
                    {/* Performance Overview */}
                    <div className="bg-gradient-to-r from-green-600/20 to-blue-600/20 rounded-xl border border-green-500/30 p-6">
                      <div className="flex items-center space-x-3 mb-6">
                        <TrendingUp className="h-6 w-6 text-green-400" />
                        <h2 className="text-xl font-semibold text-white">Backtest Results</h2>
                        <div className="text-sm text-gray-400">
                          {backtestResult.backtest_results.symbol} • {backtestResult.backtest_results.timeframe} • 
                          {backtestResult.backtest_results.data_points} data points
                        </div>
                      </div>

                      <div className="grid grid-cols-4 gap-4">
                        <div className="bg-gray-800/50 rounded-lg p-4 text-center">
                          <div className={`text-2xl font-bold ${
                            (backtestResult.backtest_results?.results?.total_return_pct || 0) >= 0 ? 'text-green-400' : 'text-red-400'
                          }`}>
                            {(backtestResult.backtest_results?.results?.total_return_pct || 0).toFixed(2)}%
                          </div>
                          <div className="text-sm text-gray-300">Total Return</div>
                        </div>

                        <div className="bg-gray-800/50 rounded-lg p-4 text-center">
                          <div className="text-2xl font-bold text-blue-400">
                            {(backtestResult.backtest_results?.results?.sharpe_ratio || 0).toFixed(3)}
                          </div>
                          <div className="text-sm text-gray-300">Sharpe Ratio</div>
                        </div>

                        <div className="bg-gray-800/50 rounded-lg p-4 text-center">
                          <div className="text-2xl font-bold text-yellow-400">
                            {(backtestResult.backtest_results?.results?.max_drawdown_pct || 0).toFixed(2)}%
                          </div>
                          <div className="text-sm text-gray-300">Max Drawdown</div>
                        </div>

                        <div className="bg-gray-800/50 rounded-lg p-4 text-center">
                          <div className="text-2xl font-bold text-purple-400">
                            {(backtestResult.backtest_results?.results?.win_rate_pct || 0).toFixed(1)}%
                          </div>
                          <div className="text-sm text-gray-300">Win Rate</div>
                        </div>
                      </div>

                      <div className="grid grid-cols-2 gap-4 mt-4">
                        <div className="bg-gray-800/30 rounded-lg p-4">
                          <div className="flex items-center justify-between">
                            <span className="text-gray-300">Total Trades</span>
                            <span className="text-white font-medium">{backtestResult.backtest_results?.results?.total_trades || 0}</span>
                          </div>
                        </div>

                        <div className="bg-gray-800/30 rounded-lg p-4">
                          <div className="flex items-center justify-between">
                            <span className="text-gray-300">Final Value</span>
                            <span className="text-white font-medium">
                              ${(backtestResult.backtest_results?.results?.final_value || 0).toLocaleString()}
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Trading Activity */}
                    <div className="bg-gray-800 rounded-xl border border-gray-600 p-6">
                      <h3 className="text-lg font-semibold text-white mb-4 flex items-center space-x-2">
                        <Target className="h-5 w-5 text-blue-400" />
                        <span>Trading Activity</span>
                      </h3>

                      <div className="grid grid-cols-2 gap-4 mb-4">
                        <div className="bg-gray-700/50 rounded-lg p-4">
                          <div className="text-center">
                            <div className="text-xl font-bold text-green-400">
                              {backtestResult.backtest_results?.results?.signals_generated?.total_entry_signals || 0}
                            </div>
                            <div className="text-sm text-gray-300">Entry Signals</div>
                          </div>
                        </div>

                        <div className="bg-gray-700/50 rounded-lg p-4">
                          <div className="text-center">
                            <div className="text-xl font-bold text-red-400">
                              {backtestResult.backtest_results?.results?.signals_generated?.total_exit_signals || 0}
                            </div>
                            <div className="text-sm text-gray-300">Exit Signals</div>
                          </div>
                        </div>
                      </div>

                      {/* Recent Trades */}
                      {(backtestResult.backtest_results?.results?.trades?.length || 0) > 0 && (
                        <div>
                          <h4 className="text-sm font-medium text-gray-300 mb-2">Recent Trades</h4>
                          <div className="space-y-2 max-h-40 overflow-y-auto">
                            {(backtestResult.backtest_results?.results?.trades || []).slice(-5).map((trade, index) => (
                              <div key={index} className="bg-gray-700/30 rounded p-3 text-sm">
                                <div className="flex justify-between items-center">
                                  <span className={`font-medium ${trade.type === 'buy' ? 'text-green-400' : 'text-red-400'}`}>
                                    {trade.type.toUpperCase()}
                                  </span>
                                  <span className="text-gray-300">${trade.price.toFixed(2)}</span>
                                  <span className="text-gray-400 text-xs">
                                    {new Date(trade.timestamp).toLocaleDateString()}
                                  </span>
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </>
                ) : (
                  <div className="bg-red-600/20 rounded-xl border border-red-500/30 p-6">
                    <div className="flex items-center space-x-3">
                      <AlertCircle className="h-6 w-6 text-red-400" />
                      <div>
                        <h3 className="text-lg font-semibold text-red-400">Backtest Failed</h3>
                        <p className="text-red-300">{backtestResult.error}</p>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Sidebar */}
          <div className="col-span-4 space-y-6">
            
            {/* System Status */}
            <div className="bg-gray-800 rounded-xl border border-gray-600 p-4">
              <h3 className="text-lg font-semibold text-white mb-3 flex items-center space-x-2">
                <Activity className="h-5 w-5 text-green-400" />
                <span>System Status</span>
              </h3>
              
              <div className="space-y-2 text-sm">
                <div className="flex items-center justify-between">
                  <span className="text-gray-300">AI Conversion</span>
                  <div className="flex items-center space-x-1">
                    <div className="h-2 w-2 bg-green-400 rounded-full"></div>
                    <span className="text-green-400">Online</span>
                  </div>
                </div>
                
                <div className="flex items-center justify-between">
                  <span className="text-gray-300">Real Data Feed</span>
                  <div className="flex items-center space-x-1">
                    <div className="h-2 w-2 bg-green-400 rounded-full"></div>
                    <span className="text-green-400">Connected</span>
                  </div>
                </div>

                <div className="flex items-center justify-between">
                  <span className="text-gray-300">Backtest Engine</span>
                  <div className="flex items-center space-x-1">
                    <div className="h-2 w-2 bg-green-400 rounded-full"></div>
                    <span className="text-green-400">Ready</span>
                  </div>
                </div>
              </div>
            </div>

            {/* AI Features */}
            <div className="bg-gradient-to-br from-purple-600/20 to-blue-600/20 rounded-xl border border-purple-500/30 p-4">
              <h3 className="text-lg font-semibold text-white mb-3 flex items-center space-x-2">
                <Sparkles className="h-5 w-5 text-purple-400" />
                <span>AI Features</span>
              </h3>
              
              <div className="space-y-3 text-sm">
                <div className="flex items-center space-x-2">
                  <CheckCircle2 className="h-4 w-4 text-green-400" />
                  <span className="text-gray-300">Smart Parameter Extraction</span>
                </div>
                
                <div className="flex items-center space-x-2">
                  <CheckCircle2 className="h-4 w-4 text-green-400" />
                  <span className="text-gray-300">Indicator Library Matching</span>
                </div>

                <div className="flex items-center space-x-2">
                  <CheckCircle2 className="h-4 w-4 text-green-400" />
                  <span className="text-gray-300">Logic Flow Analysis</span>
                </div>

                <div className="flex items-center space-x-2">
                  <CheckCircle2 className="h-4 w-4 text-green-400" />
                  <span className="text-gray-300">Real Data Validation</span>
                </div>
              </div>
            </div>

            {/* Market Data Info */}
            <div className="bg-gray-800 rounded-xl border border-gray-600 p-4">
              <h3 className="text-lg font-semibold text-white mb-3 flex items-center space-x-2">
                <Database className="h-5 w-5 text-blue-400" />
                <span>Market Data</span>
              </h3>
              
              <div className="space-y-2 text-sm">
                <div className="flex items-center justify-between">
                  <span className="text-gray-300">Data Source</span>
                  <span className="text-blue-400">Binance API</span>
                </div>
                
                <div className="flex items-center justify-between">
                  <span className="text-gray-300">Available Pairs</span>
                  <span className="text-blue-400">{availablePairs.length}</span>
                </div>

                <div className="flex items-center justify-between">
                  <span className="text-gray-300">Timeframes</span>
                  <span className="text-blue-400">{timeframes.length}</span>
                </div>

                <div className="flex items-center justify-between">
                  <span className="text-gray-300">Data Type</span>
                  <span className="text-green-400">Real-time OHLCV</span>
                </div>
              </div>
            </div>

          </div>
        </div>
      </div>
    </div>
  );
};

export default AIStrategyDashboard;