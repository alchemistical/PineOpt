import React, { useState, useMemo } from 'react';
import {
  TrendingUp,
  TrendingDown,
  BarChart3,
  PieChart,
  Target,
  DollarSign,
  Percent,
  Calendar,
  Activity,
  AlertTriangle,
  CheckCircle,
  Clock,
  Zap,
  Download,
  RefreshCw,
  Maximize2,
  Eye,
  X
} from 'lucide-react';
import LightweightChart from './LightweightChart';

interface BacktestTrade {
  id: string;
  timestamp: string;
  side: 'long' | 'short';
  entry_price: number;
  exit_price: number;
  quantity: number;
  pnl: number;
  pnl_percentage: number;
  duration_hours: number;
  entry_reason: string;
  exit_reason: string;
}

interface BacktestMetrics {
  total_return: number;
  total_return_percentage: number;
  annualized_return: number;
  max_drawdown: number;
  sharpe_ratio: number;
  sortino_ratio: number;
  win_rate: number;
  profit_factor: number;
  total_trades: number;
  winning_trades: number;
  losing_trades: number;
  avg_win: number;
  avg_loss: number;
  largest_win: number;
  largest_loss: number;
  avg_trade_duration: number;
  volatility: number;
  var_95: number;
  calmar_ratio: number;
  sterling_ratio: number;
}

interface BacktestResult {
  id: string;
  strategy_id: string;
  strategy_name: string;
  start_date: string;
  end_date: string;
  initial_capital: number;
  final_capital: number;
  status: 'completed' | 'running' | 'failed' | 'cancelled';
  metrics: BacktestMetrics;
  trades: BacktestTrade[];
  equity_curve: { timestamp: string; value: number }[];
  drawdown_curve: { timestamp: string; value: number }[];
  price_data: { timestamp: string; open: number; high: number; low: number; close: number; volume: number }[];
  created_at: string;
  execution_time_ms: number;
}

interface BacktestResultsProps {
  result: BacktestResult;
  onClose?: () => void;
}

const BacktestResults: React.FC<BacktestResultsProps> = ({ result, onClose }) => {
  const [activeTab, setActiveTab] = useState<'overview' | 'trades' | 'charts' | 'analysis'>('overview');
  const [chartView, setChartView] = useState<'equity' | 'drawdown' | 'price'>('equity');
  const [expandedChart, setExpandedChart] = useState(false);

  const performanceMetrics = useMemo(() => {
    const { metrics } = result;
    return [
      {
        label: 'Total Return',
        value: `$${metrics.total_return.toLocaleString()}`,
        percentage: `${metrics.total_return_percentage.toFixed(2)}%`,
        color: metrics.total_return >= 0 ? 'text-green-400' : 'text-red-400',
        icon: metrics.total_return >= 0 ? TrendingUp : TrendingDown
      },
      {
        label: 'Annualized Return',
        value: `${metrics.annualized_return.toFixed(2)}%`,
        color: metrics.annualized_return >= 0 ? 'text-green-400' : 'text-red-400',
        icon: BarChart3
      },
      {
        label: 'Max Drawdown',
        value: `${metrics.max_drawdown.toFixed(2)}%`,
        color: 'text-red-400',
        icon: TrendingDown
      },
      {
        label: 'Sharpe Ratio',
        value: metrics.sharpe_ratio.toFixed(3),
        color: metrics.sharpe_ratio >= 1 ? 'text-green-400' : metrics.sharpe_ratio >= 0 ? 'text-yellow-400' : 'text-red-400',
        icon: Target
      },
      {
        label: 'Win Rate',
        value: `${metrics.win_rate.toFixed(1)}%`,
        color: metrics.win_rate >= 50 ? 'text-green-400' : 'text-red-400',
        icon: CheckCircle
      },
      {
        label: 'Profit Factor',
        value: metrics.profit_factor.toFixed(2),
        color: metrics.profit_factor >= 1.5 ? 'text-green-400' : metrics.profit_factor >= 1 ? 'text-yellow-400' : 'text-red-400',
        icon: DollarSign
      }
    ];
  }, [result.metrics]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'text-green-400 bg-green-400/20';
      case 'running': return 'text-yellow-400 bg-yellow-400/20';
      case 'failed': return 'text-red-400 bg-red-400/20';
      case 'cancelled': return 'text-gray-400 bg-gray-400/20';
      default: return 'text-gray-400 bg-gray-400/20';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return CheckCircle;
      case 'running': return RefreshCw;
      case 'failed': return AlertTriangle;
      case 'cancelled': return X;
      default: return AlertTriangle;
    }
  };

  const formatDuration = (hours: number) => {
    if (hours < 1) return `${Math.round(hours * 60)}m`;
    if (hours < 24) return `${Math.round(hours)}h`;
    return `${Math.round(hours / 24)}d`;
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(value);
  };

  const renderOverview = () => (
    <div className="space-y-6">
      {/* Performance Metrics Grid */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        {performanceMetrics.map((metric, index) => {
          const IconComponent = metric.icon;
          return (
            <div key={index} className="bg-gray-700/30 rounded-lg p-4 border border-gray-600/50">
              <div className="flex items-center justify-between mb-2">
                <IconComponent className={`h-4 w-4 ${metric.color}`} />
                <span className="text-xs text-gray-400">{metric.label}</span>
              </div>
              <div className={`text-lg font-bold ${metric.color}`}>
                {metric.value}
              </div>
              {metric.percentage && (
                <div className="text-xs text-gray-400">{metric.percentage}</div>
              )}
            </div>
          );
        })}
      </div>

      {/* Summary Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-gray-700/30 rounded-lg p-6 border border-gray-600/50">
          <h3 className="text-lg font-semibold text-white mb-4 flex items-center space-x-2">
            <Activity className="h-5 w-5 text-blue-400" />
            <span>Trading Statistics</span>
          </h3>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-400">Total Trades</span>
              <span className="text-white font-medium">{result.metrics.total_trades}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Winning Trades</span>
              <span className="text-green-400 font-medium">{result.metrics.winning_trades}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Losing Trades</span>
              <span className="text-red-400 font-medium">{result.metrics.losing_trades}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Average Win</span>
              <span className="text-green-400 font-medium">{formatCurrency(result.metrics.avg_win)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Average Loss</span>
              <span className="text-red-400 font-medium">{formatCurrency(result.metrics.avg_loss)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Average Trade Duration</span>
              <span className="text-white font-medium">{formatDuration(result.metrics.avg_trade_duration)}</span>
            </div>
          </div>
        </div>

        <div className="bg-gray-700/30 rounded-lg p-6 border border-gray-600/50">
          <h3 className="text-lg font-semibold text-white mb-4 flex items-center space-x-2">
            <Target className="h-5 w-5 text-purple-400" />
            <span>Risk Metrics</span>
          </h3>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-400">Volatility</span>
              <span className="text-white font-medium">{(result.metrics.volatility * 100).toFixed(2)}%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Value at Risk (95%)</span>
              <span className="text-red-400 font-medium">{formatCurrency(result.metrics.var_95)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Sortino Ratio</span>
              <span className="text-white font-medium">{result.metrics.sortino_ratio.toFixed(3)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Calmar Ratio</span>
              <span className="text-white font-medium">{result.metrics.calmar_ratio.toFixed(3)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Sterling Ratio</span>
              <span className="text-white font-medium">{result.metrics.sterling_ratio.toFixed(3)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Largest Loss</span>
              <span className="text-red-400 font-medium">{formatCurrency(result.metrics.largest_loss)}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderTrades = () => (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-white">Trade History</h3>
        <button className="flex items-center space-x-2 px-4 py-2 bg-blue-600/20 border border-blue-600/30 rounded text-blue-400 text-sm hover:bg-blue-600/30 transition-colors">
          <Download className="h-4 w-4" />
          <span>Export CSV</span>
        </button>
      </div>
      
      <div className="bg-gray-700/30 rounded-lg border border-gray-600/50 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-gray-800/50 border-b border-gray-600/50">
              <tr>
                <th className="text-left p-3 text-gray-400 font-medium">Date</th>
                <th className="text-left p-3 text-gray-400 font-medium">Side</th>
                <th className="text-right p-3 text-gray-400 font-medium">Entry</th>
                <th className="text-right p-3 text-gray-400 font-medium">Exit</th>
                <th className="text-right p-3 text-gray-400 font-medium">Qty</th>
                <th className="text-right p-3 text-gray-400 font-medium">P&L</th>
                <th className="text-right p-3 text-gray-400 font-medium">%</th>
                <th className="text-right p-3 text-gray-400 font-medium">Duration</th>
                <th className="text-left p-3 text-gray-400 font-medium">Reason</th>
              </tr>
            </thead>
            <tbody>
              {result.trades.map((trade) => (
                <tr key={trade.id} className="border-b border-gray-700/50 hover:bg-gray-600/20">
                  <td className="p-3 text-gray-300">
                    {new Date(trade.timestamp).toLocaleDateString()}
                  </td>
                  <td className="p-3">
                    <span className={`px-2 py-1 rounded text-xs font-medium ${
                      trade.side === 'long' 
                        ? 'bg-green-600/20 text-green-400' 
                        : 'bg-red-600/20 text-red-400'
                    }`}>
                      {trade.side.toUpperCase()}
                    </span>
                  </td>
                  <td className="p-3 text-right text-gray-300 font-mono">
                    ${trade.entry_price.toFixed(2)}
                  </td>
                  <td className="p-3 text-right text-gray-300 font-mono">
                    ${trade.exit_price.toFixed(2)}
                  </td>
                  <td className="p-3 text-right text-gray-300 font-mono">
                    {trade.quantity.toFixed(4)}
                  </td>
                  <td className={`p-3 text-right font-mono ${
                    trade.pnl >= 0 ? 'text-green-400' : 'text-red-400'
                  }`}>
                    {formatCurrency(trade.pnl)}
                  </td>
                  <td className={`p-3 text-right font-mono ${
                    trade.pnl_percentage >= 0 ? 'text-green-400' : 'text-red-400'
                  }`}>
                    {trade.pnl_percentage.toFixed(2)}%
                  </td>
                  <td className="p-3 text-right text-gray-300">
                    {formatDuration(trade.duration_hours)}
                  </td>
                  <td className="p-3 text-gray-400 text-xs">
                    {trade.exit_reason}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );

  const renderCharts = () => (
    <div className="space-y-6">
      {/* Chart Controls */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <h3 className="text-lg font-semibold text-white">Performance Charts</h3>
          <div className="flex items-center space-x-2">
            {['equity', 'drawdown', 'price'].map((view) => (
              <button
                key={view}
                onClick={() => setChartView(view as any)}
                className={`px-3 py-1 rounded text-sm transition-colors ${
                  chartView === view
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-700/50 text-gray-400 hover:text-white hover:bg-gray-600/50'
                }`}
              >
                {view === 'equity' && 'Equity Curve'}
                {view === 'drawdown' && 'Drawdown'}
                {view === 'price' && 'Price Chart'}
              </button>
            ))}
          </div>
        </div>
        <button
          onClick={() => setExpandedChart(!expandedChart)}
          className="p-2 text-gray-400 hover:text-white transition-colors"
        >
          <Maximize2 className="h-4 w-4" />
        </button>
      </div>

      {/* Chart Display */}
      <div className={`bg-gray-700/30 rounded-lg border border-gray-600/50 ${
        expandedChart ? 'h-[80vh]' : 'h-96'
      }`}>
        <div className="p-4 h-full">
          {chartView === 'price' ? (
            <LightweightChart 
              data={result.price_data.map(d => ({
                timestamp: d.timestamp,
                open: d.open,
                high: d.high,
                low: d.low,
                close: d.close,
                volume: d.volume
              }))}
              height={expandedChart ? window.innerHeight * 0.75 : 320}
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center text-gray-400">
              <div className="text-center">
                <BarChart3 className="h-12 w-12 mx-auto mb-2 opacity-50" />
                <p>{chartView === 'equity' ? 'Equity curve' : 'Drawdown chart'} visualization</p>
                <p className="text-sm">Chart implementation in progress</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );

  const StatusIcon = getStatusIcon(result.status);

  return (
    <div className="min-h-screen bg-gray-900">
      {/* Header */}
      <div className="bg-gray-800/30 backdrop-blur-sm border-b border-gray-700/50 p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="p-2 bg-gradient-to-r from-green-500 to-blue-600 rounded-lg">
              <TrendingUp className="h-5 w-5 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white">Backtest Results</h1>
              <p className="text-gray-400">{result.strategy_name}</p>
            </div>
            <div className={`flex items-center space-x-2 px-3 py-1 rounded ${getStatusColor(result.status)}`}>
              <StatusIcon className="h-4 w-4" />
              <span className="text-sm font-medium capitalize">{result.status}</span>
            </div>
          </div>
          
          {onClose && (
            <button
              onClick={onClose}
              className="p-2 text-gray-400 hover:text-white transition-colors"
            >
              <X className="h-5 w-5" />
            </button>
          )}
        </div>
        
        {/* Basic Info */}
        <div className="mt-4 grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div>
            <span className="text-gray-400">Period:</span>
            <span className="ml-2 text-white">
              {new Date(result.start_date).toLocaleDateString()} - {new Date(result.end_date).toLocaleDateString()}
            </span>
          </div>
          <div>
            <span className="text-gray-400">Initial Capital:</span>
            <span className="ml-2 text-white font-medium">{formatCurrency(result.initial_capital)}</span>
          </div>
          <div>
            <span className="text-gray-400">Final Capital:</span>
            <span className={`ml-2 font-medium ${
              result.final_capital >= result.initial_capital ? 'text-green-400' : 'text-red-400'
            }`}>
              {formatCurrency(result.final_capital)}
            </span>
          </div>
          <div>
            <span className="text-gray-400">Execution Time:</span>
            <span className="ml-2 text-white">{result.execution_time_ms}ms</span>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-700/50">
        <div className="px-6">
          <div className="flex space-x-8">
            {[
              { id: 'overview', label: 'Overview', icon: BarChart3 },
              { id: 'trades', label: 'Trades', icon: Activity },
              { id: 'charts', label: 'Charts', icon: TrendingUp },
              { id: 'analysis', label: 'Analysis', icon: Zap }
            ].map((tab) => {
              const IconComponent = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as any)}
                  className={`flex items-center space-x-2 py-4 px-2 border-b-2 transition-colors ${
                    activeTab === tab.id
                      ? 'border-blue-500 text-blue-400'
                      : 'border-transparent text-gray-400 hover:text-white'
                  }`}
                >
                  <IconComponent className="h-4 w-4" />
                  <span className="font-medium">{tab.label}</span>
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="p-6">
        {activeTab === 'overview' && renderOverview()}
        {activeTab === 'trades' && renderTrades()}
        {activeTab === 'charts' && renderCharts()}
        {activeTab === 'analysis' && (
          <div className="text-center py-12">
            <Zap className="h-12 w-12 mx-auto mb-4 text-gray-400 opacity-50" />
            <h3 className="text-lg font-semibold text-white mb-2">Advanced Analysis</h3>
            <p className="text-gray-400">Statistical analysis and insights coming soon</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default BacktestResults;