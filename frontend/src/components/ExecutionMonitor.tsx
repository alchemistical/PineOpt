import React, { useState, useEffect, useRef } from 'react';
import {
  Activity,
  Play,
  Square,
  Pause,
  AlertCircle,
  CheckCircle,
  Clock,
  TrendingUp,
  TrendingDown,
  DollarSign,
  Target,
  Zap,
  RefreshCw,
  Settings,
  Eye,
  EyeOff,
  Volume2,
  VolumeX
} from 'lucide-react';

interface ExecutionOrder {
  id: string;
  strategy_id: string;
  strategy_name: string;
  side: 'buy' | 'sell';
  symbol: string;
  quantity: number;
  price: number;
  order_type: 'market' | 'limit' | 'stop' | 'stop_limit';
  status: 'pending' | 'filled' | 'partially_filled' | 'cancelled' | 'rejected';
  timestamp: string;
  filled_quantity: number;
  avg_fill_price: number;
  commission: number;
}

interface ExecutionPosition {
  id: string;
  strategy_id: string;
  strategy_name: string;
  symbol: string;
  side: 'long' | 'short';
  quantity: number;
  avg_price: number;
  current_price: number;
  unrealized_pnl: number;
  unrealized_pnl_percentage: number;
  market_value: number;
  timestamp: string;
}

interface ExecutionMetrics {
  total_pnl: number;
  total_pnl_percentage: number;
  active_positions: number;
  pending_orders: number;
  filled_orders_today: number;
  commission_paid_today: number;
  win_rate_today: number;
  largest_position: number;
}

interface StrategyStatus {
  id: string;
  name: string;
  status: 'running' | 'paused' | 'stopped' | 'error';
  pnl: number;
  pnl_percentage: number;
  positions: number;
  orders: number;
  last_signal: string;
  last_activity: string;
}

interface ExecutionMonitorProps {
  onStrategyControl?: (strategyId: string, action: 'start' | 'pause' | 'stop') => void;
}

const ExecutionMonitor: React.FC<ExecutionMonitorProps> = ({ onStrategyControl }) => {
  const [activeTab, setActiveTab] = useState<'overview' | 'orders' | 'positions' | 'strategies'>('overview');
  const [orders, setOrders] = useState<ExecutionOrder[]>([]);
  const [positions, setPositions] = useState<ExecutionPosition[]>([]);
  const [strategies, setStrategies] = useState<StrategyStatus[]>([]);
  const [metrics, setMetrics] = useState<ExecutionMetrics | null>(null);
  const [isLive, setIsLive] = useState(true);
  const [soundEnabled, setSoundEnabled] = useState(true);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const intervalRef = useRef<NodeJS.Timeout>();

  useEffect(() => {
    if (autoRefresh && isLive) {
      intervalRef.current = setInterval(loadExecutionData, 2000); // Refresh every 2 seconds
      loadExecutionData();
    }
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [autoRefresh, isLive]);

  const loadExecutionData = async () => {
    try {
      // In a real implementation, these would be actual API calls
      const mockData = generateMockData();
      setOrders(mockData.orders);
      setPositions(mockData.positions);
      setStrategies(mockData.strategies);
      setMetrics(mockData.metrics);
    } catch (error) {
      console.error('Failed to load execution data:', error);
    }
  };

  const generateMockData = () => {
    // Mock data generator for demonstration
    const strategies: StrategyStatus[] = [
      {
        id: '1',
        name: 'Mean Reversion Strategy',
        status: 'running',
        pnl: 1250.50,
        pnl_percentage: 2.45,
        positions: 3,
        orders: 1,
        last_signal: 'BUY AAPL',
        last_activity: new Date(Date.now() - 30000).toISOString()
      },
      {
        id: '2',
        name: 'Momentum Strategy',
        status: 'paused',
        pnl: -340.20,
        pnl_percentage: -0.68,
        positions: 1,
        orders: 0,
        last_signal: 'SELL TSLA',
        last_activity: new Date(Date.now() - 300000).toISOString()
      }
    ];

    const positions: ExecutionPosition[] = [
      {
        id: '1',
        strategy_id: '1',
        strategy_name: 'Mean Reversion Strategy',
        symbol: 'AAPL',
        side: 'long',
        quantity: 100,
        avg_price: 150.25,
        current_price: 152.80,
        unrealized_pnl: 255.00,
        unrealized_pnl_percentage: 1.70,
        market_value: 15280.00,
        timestamp: new Date().toISOString()
      }
    ];

    const orders: ExecutionOrder[] = [
      {
        id: '1',
        strategy_id: '1',
        strategy_name: 'Mean Reversion Strategy',
        side: 'buy',
        symbol: 'MSFT',
        quantity: 50,
        price: 280.50,
        order_type: 'limit',
        status: 'pending',
        timestamp: new Date().toISOString(),
        filled_quantity: 0,
        avg_fill_price: 0,
        commission: 0
      }
    ];

    const metrics: ExecutionMetrics = {
      total_pnl: 910.30,
      total_pnl_percentage: 1.82,
      active_positions: positions.length,
      pending_orders: orders.filter(o => o.status === 'pending').length,
      filled_orders_today: 12,
      commission_paid_today: 24.50,
      win_rate_today: 66.7,
      largest_position: 15280.00
    };

    return { strategies, positions, orders, metrics };
  };

  const handleStrategyControl = (strategyId: string, action: 'start' | 'pause' | 'stop') => {
    onStrategyControl?.(strategyId, action);
    
    // Update local state optimistically
    setStrategies(prev => prev.map(s => 
      s.id === strategyId 
        ? { ...s, status: action === 'start' ? 'running' : action === 'pause' ? 'paused' : 'stopped' }
        : s
    ));
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running': return 'text-green-400 bg-green-400/20';
      case 'paused': return 'text-yellow-400 bg-yellow-400/20';
      case 'stopped': return 'text-gray-400 bg-gray-400/20';
      case 'error': return 'text-red-400 bg-red-400/20';
      case 'filled': return 'text-green-400 bg-green-400/20';
      case 'pending': return 'text-yellow-400 bg-yellow-400/20';
      case 'cancelled': return 'text-gray-400 bg-gray-400/20';
      case 'rejected': return 'text-red-400 bg-red-400/20';
      default: return 'text-gray-400 bg-gray-400/20';
    }
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
      {/* Key Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {metrics && [
          {
            label: 'Total P&L',
            value: formatCurrency(metrics.total_pnl),
            percentage: `${metrics.total_pnl_percentage.toFixed(2)}%`,
            color: metrics.total_pnl >= 0 ? 'text-green-400' : 'text-red-400',
            icon: metrics.total_pnl >= 0 ? TrendingUp : TrendingDown
          },
          {
            label: 'Active Positions',
            value: metrics.active_positions.toString(),
            color: 'text-blue-400',
            icon: Target
          },
          {
            label: 'Pending Orders',
            value: metrics.pending_orders.toString(),
            color: 'text-yellow-400',
            icon: Clock
          },
          {
            label: 'Win Rate Today',
            value: `${metrics.win_rate_today.toFixed(1)}%`,
            color: metrics.win_rate_today >= 50 ? 'text-green-400' : 'text-red-400',
            icon: CheckCircle
          }
        ].map((metric, index) => {
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

      {/* Strategy Status */}
      <div className="bg-gray-700/30 rounded-lg p-6 border border-gray-600/50">
        <h3 className="text-lg font-semibold text-white mb-4 flex items-center space-x-2">
          <Activity className="h-5 w-5 text-blue-400" />
          <span>Strategy Status</span>
        </h3>
        <div className="space-y-3">
          {strategies.map((strategy) => (
            <div key={strategy.id} className="flex items-center justify-between p-4 bg-gray-600/20 rounded-lg">
              <div className="flex items-center space-x-4">
                <div className={`px-3 py-1 rounded text-xs font-medium ${getStatusColor(strategy.status)}`}>
                  {strategy.status.toUpperCase()}
                </div>
                <div>
                  <div className="font-medium text-white">{strategy.name}</div>
                  <div className="text-sm text-gray-400">
                    {strategy.positions} positions • {strategy.orders} orders
                  </div>
                </div>
              </div>
              <div className="flex items-center space-x-4">
                <div className="text-right">
                  <div className={`font-medium ${
                    strategy.pnl >= 0 ? 'text-green-400' : 'text-red-400'
                  }`}>
                    {formatCurrency(strategy.pnl)}
                  </div>
                  <div className="text-sm text-gray-400">
                    {strategy.pnl_percentage.toFixed(2)}%
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => handleStrategyControl(strategy.id, 'start')}
                    disabled={strategy.status === 'running'}
                    className="p-2 text-green-400 hover:text-green-300 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <Play className="h-4 w-4" />
                  </button>
                  <button
                    onClick={() => handleStrategyControl(strategy.id, 'pause')}
                    disabled={strategy.status !== 'running'}
                    className="p-2 text-yellow-400 hover:text-yellow-300 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <Pause className="h-4 w-4" />
                  </button>
                  <button
                    onClick={() => handleStrategyControl(strategy.id, 'stop')}
                    disabled={strategy.status === 'stopped'}
                    className="p-2 text-red-400 hover:text-red-300 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <Square className="h-4 w-4" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-900">
      {/* Header */}
      <div className="bg-gray-800/30 backdrop-blur-sm border-b border-gray-700/50 p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className={`p-2 rounded-lg ${
              isLive ? 'bg-green-500/20 text-green-400' : 'bg-gray-500/20 text-gray-400'
            }`}>
              <Activity className={`h-5 w-5 ${isLive ? 'animate-pulse' : ''}`} />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white">Execution Monitor</h1>
              <p className="text-gray-400">
                {isLive ? 'Live trading session' : 'Trading session paused'}
              </p>
            </div>
          </div>
          
          <div className="flex items-center space-x-3">
            <button
              onClick={() => setSoundEnabled(!soundEnabled)}
              className={`p-2 rounded-lg transition-colors ${
                soundEnabled 
                  ? 'bg-blue-600/20 text-blue-400' 
                  : 'bg-gray-600/20 text-gray-400'
              }`}
            >
              {soundEnabled ? <Volume2 className="h-4 w-4" /> : <VolumeX className="h-4 w-4" />}
            </button>
            
            <button
              onClick={() => setAutoRefresh(!autoRefresh)}
              className={`p-2 rounded-lg transition-colors ${
                autoRefresh 
                  ? 'bg-green-600/20 text-green-400' 
                  : 'bg-gray-600/20 text-gray-400'
              }`}
            >
              <RefreshCw className={`h-4 w-4 ${autoRefresh && isLive ? 'animate-spin' : ''}`} />
            </button>
            
            <button
              onClick={() => setIsLive(!isLive)}
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors ${
                isLive
                  ? 'bg-red-600 hover:bg-red-700 text-white'
                  : 'bg-green-600 hover:bg-green-700 text-white'
              }`}
            >
              {isLive ? <Square className="h-4 w-4" /> : <Play className="h-4 w-4" />}
              <span>{isLive ? 'Stop' : 'Start'}</span>
            </button>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-700/50">
        <div className="px-6">
          <div className="flex space-x-8">
            {[
              { id: 'overview', label: 'Overview', icon: Activity },
              { id: 'orders', label: 'Orders', icon: Clock },
              { id: 'positions', label: 'Positions', icon: Target },
              { id: 'strategies', label: 'Strategies', icon: Zap }
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
        {activeTab === 'orders' && (
          <div className="text-center py-12">
            <Clock className="h-12 w-12 mx-auto mb-4 text-gray-400 opacity-50" />
            <h3 className="text-lg font-semibold text-white mb-2">Order Management</h3>
            <p className="text-gray-400">Detailed order tracking and management interface</p>
          </div>
        )}
        {activeTab === 'positions' && (
          <div className="text-center py-12">
            <Target className="h-12 w-12 mx-auto mb-4 text-gray-400 opacity-50" />
            <h3 className="text-lg font-semibold text-white mb-2">Position Tracking</h3>
            <p className="text-gray-400">Real-time position monitoring and P&L tracking</p>
          </div>
        )}
        {activeTab === 'strategies' && (
          <div className="text-center py-12">
            <Zap className="h-12 w-12 mx-auto mb-4 text-gray-400 opacity-50" />
            <h3 className="text-lg font-semibold text-white mb-2">Strategy Management</h3>
            <p className="text-gray-400">Control and monitor strategy execution parameters</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default ExecutionMonitor;