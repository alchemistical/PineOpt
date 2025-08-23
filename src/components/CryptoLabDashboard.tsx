import React, { useState, useEffect } from 'react';
import {
  TrendingUp,
  TrendingDown,
  Activity,
  Target,
  Brain,
  Zap,
  DollarSign,
  Percent,
  Clock,
  Users,
  ArrowUpRight,
  ArrowDownRight,
  Plus,
  Play,
  Pause,
  BarChart3,
  LineChart,
  PieChart,
  Bell,
  AlertCircle,
  CheckCircle,
  RefreshCw,
  Sparkles,
  Bot,
  Database,
  Cpu
} from 'lucide-react';

interface MarketData {
  symbol: string;
  price: number;
  change: number;
  changePercent: number;
  volume: number;
  marketCap?: number;
}

interface PortfolioSummary {
  totalValue: number;
  dayChange: number;
  dayChangePercent: number;
  realizedPnL: number;
  unrealizedPnL: number;
  positions: number;
  activeStrategies: number;
}

interface StrategyPerformance {
  id: string;
  name: string;
  status: 'running' | 'paused' | 'stopped';
  pnl: number;
  pnlPercent: number;
  trades: number;
  winRate: number;
  lastActivity: string;
}

interface RecentActivity {
  id: string;
  type: 'trade' | 'backtest' | 'strategy' | 'alert';
  message: string;
  timestamp: string;
  status: 'success' | 'warning' | 'error' | 'info';
}

interface CryptoLabDashboardProps {
  onNavigate?: (view: string) => void;
}

const CryptoLabDashboard: React.FC<CryptoLabDashboardProps> = ({ onNavigate }) => {
  const [marketData, setMarketData] = useState<MarketData[]>([]);
  const [portfolio, setPortfolio] = useState<PortfolioSummary | null>(null);
  const [strategies, setStrategies] = useState<StrategyPerformance[]>([]);
  const [activities, setActivities] = useState<RecentActivity[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Load dashboard data
    loadDashboardData();
    
    // Set up real-time updates
    const interval = setInterval(loadDashboardData, 30000); // Update every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const loadDashboardData = async () => {
    try {
      // Load real strategies from our API - Epic 7
      const strategiesResponse = await fetch('http://localhost:5007/api/v1/strategies/list?limit=20');
      const strategiesData = await strategiesResponse.json();
      
      if (strategiesData.status === 'success') {
        const realStrategies = strategiesData.strategies;
        const validStrategies = realStrategies.filter((s: any) => s.validation_status === 'valid');
        
        // Calculate real portfolio metrics
        const totalStrategies = realStrategies.length;
        const validCount = validStrategies.length;
        const totalBacktests = realStrategies.reduce((sum: number, s: any) => sum + (s.backtest_count || 0), 0);
        
        setPortfolio({
          totalValue: 10000, // Starting capital
          dayChange: 0, // No real trading yet
          dayChangePercent: 0,
          realizedPnL: 0,
          unrealizedPnL: 0,
          positions: 0,
          activeStrategies: validCount
        });

        // Convert real strategies to dashboard format
        const dashboardStrategies: StrategyPerformance[] = validStrategies.slice(0, 6).map((strategy: any) => ({
          id: strategy.id,
          name: strategy.name,
          status: 'paused' as const, // All are paused since we're not live trading yet
          pnl: 0, // No real P&L yet
          pnlPercent: 0,
          trades: strategy.backtest_count || 0,
          winRate: 0, // No real trading data yet
          lastActivity: new Date(strategy.updated_at).toLocaleTimeString()
        }));
        
        setStrategies(dashboardStrategies);

        // Create real activities from strategy data
        const recentActivities: RecentActivity[] = realStrategies
          .sort((a: any, b: any) => new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime())
          .slice(0, 4)
          .map((strategy: any, index: number) => ({
            id: strategy.id,
            type: 'strategy' as const,
            message: `${strategy.name} uploaded by ${strategy.author}`,
            timestamp: new Date(strategy.created_at).toLocaleTimeString(),
            status: strategy.validation_status === 'valid' ? 'success' : 
                   strategy.validation_status === 'pending' ? 'warning' : 'error'
          }));

        setActivities(recentActivities);
      }

      // Load real market data from Binance API
      try {
        const marketResponse = await fetch('http://localhost:5007/api/v1/market/overview');
        const marketData = await marketResponse.json();
        
        if (marketData.status === 'success' && marketData.market_overview.tickers) {
          const realMarketData: MarketData[] = Object.entries(marketData.market_overview.tickers).map(([symbol, ticker]: [string, any]) => ({
            symbol: symbol,
            price: ticker.price,
            change: ticker.change,
            changePercent: ticker.change_percent,
            volume: ticker.volume
          }));
          
          setMarketData(realMarketData);
          console.log('✅ Real market data loaded:', realMarketData.length, 'pairs');
        } else {
          throw new Error('Failed to fetch real market data');
        }
      } catch (marketError) {
        console.warn('⚠️ Real market data failed, using fallback data:', marketError);
        // Fallback to basic data
        setMarketData([
          { symbol: 'BTC/USDT', price: 43250.50, change: 1250.30, changePercent: 2.98, volume: 28500000000 },
          { symbol: 'ETH/USDT', price: 2680.75, change: -45.20, changePercent: -1.66, volume: 15200000000 }
        ]);
      }

    } catch (error) {
      console.error('Failed to load dashboard data:', error);
      // Set fallback data on error
      setPortfolio({
        totalValue: 0,
        dayChange: 0,
        dayChangePercent: 0,
        realizedPnL: 0,
        unrealizedPnL: 0,
        positions: 0,
        activeStrategies: 0
      });
      setStrategies([]);
      setActivities([]);
      setMarketData([]);
    } finally {
      setLoading(false);
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

  const formatLargeNumber = (value: number) => {
    if (value >= 1e9) return `$${(value / 1e9).toFixed(1)}B`;
    if (value >= 1e6) return `$${(value / 1e6).toFixed(1)}M`;
    if (value >= 1e3) return `$${(value / 1e3).toFixed(1)}K`;
    return `$${value.toFixed(2)}`;
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running': return 'text-green-400 bg-green-400/20';
      case 'paused': return 'text-yellow-400 bg-yellow-400/20';
      case 'stopped': return 'text-gray-400 bg-gray-400/20';
      default: return 'text-gray-400 bg-gray-400/20';
    }
  };

  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'trade': return Target;
      case 'backtest': return BarChart3;
      case 'strategy': return Zap;
      case 'alert': return Bell;
      default: return Activity;
    }
  };

  const getActivityColor = (status: string) => {
    switch (status) {
      case 'success': return 'text-green-400';
      case 'warning': return 'text-yellow-400';
      case 'error': return 'text-red-400';
      default: return 'text-blue-400';
    }
  };

  if (loading) {
    return (
      <div className="p-6 flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <RefreshCw className="h-8 w-8 animate-spin text-blue-400 mx-auto mb-4" />
          <p className="text-slate-400">Loading market data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Quick Stats */}
      {portfolio && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="bg-slate-800/30 backdrop-blur-sm rounded-xl p-6 border border-slate-700/50">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-400 text-sm font-medium">Portfolio Value</p>
                <p className="text-2xl font-bold text-white mt-1">
                  {formatCurrency(portfolio.totalValue)}
                </p>
                <div className="flex items-center space-x-1 mt-2">
                  {portfolio.dayChangePercent >= 0 ? (
                    <ArrowUpRight className="h-4 w-4 text-green-400" />
                  ) : (
                    <ArrowDownRight className="h-4 w-4 text-red-400" />
                  )}
                  <span className={`text-sm font-medium ${
                    portfolio.dayChangePercent >= 0 ? 'text-green-400' : 'text-red-400'
                  }`}>
                    {portfolio.dayChangePercent.toFixed(2)}% today
                  </span>
                </div>
              </div>
              <div className="p-3 bg-blue-500/20 rounded-lg">
                <DollarSign className="h-6 w-6 text-blue-400" />
              </div>
            </div>
          </div>

          <div className="bg-slate-800/30 backdrop-blur-sm rounded-xl p-6 border border-slate-700/50">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-400 text-sm font-medium">Active Strategies</p>
                <p className="text-2xl font-bold text-white mt-1">{portfolio.activeStrategies}</p>
                <p className="text-sm text-slate-400 mt-2">{portfolio.positions} positions</p>
              </div>
              <div className="p-3 bg-purple-500/20 rounded-lg">
                <Zap className="h-6 w-6 text-purple-400" />
              </div>
            </div>
          </div>

          <div className="bg-slate-800/30 backdrop-blur-sm rounded-xl p-6 border border-slate-700/50">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-400 text-sm font-medium">Unrealized P&L</p>
                <p className={`text-2xl font-bold mt-1 ${
                  portfolio.unrealizedPnL >= 0 ? 'text-green-400' : 'text-red-400'
                }`}>
                  {formatCurrency(portfolio.unrealizedPnL)}
                </p>
                <p className="text-sm text-slate-400 mt-2">Open positions</p>
              </div>
              <div className="p-3 bg-green-500/20 rounded-lg">
                <TrendingUp className="h-6 w-6 text-green-400" />
              </div>
            </div>
          </div>

          <div className="bg-slate-800/30 backdrop-blur-sm rounded-xl p-6 border border-slate-700/50">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-400 text-sm font-medium">Realized P&L</p>
                <p className={`text-2xl font-bold mt-1 ${
                  portfolio.realizedPnL >= 0 ? 'text-green-400' : 'text-red-400'
                }`}>
                  {formatCurrency(portfolio.realizedPnL)}
                </p>
                <p className="text-sm text-slate-400 mt-2">This month</p>
              </div>
              <div className="p-3 bg-emerald-500/20 rounded-lg">
                <Target className="h-6 w-6 text-emerald-400" />
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Market Overview */}
        <div className="lg:col-span-2">
          <div className="bg-slate-800/30 backdrop-blur-sm rounded-xl p-6 border border-slate-700/50">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-semibold text-white">Market Overview</h3>
              <button className="flex items-center space-x-2 px-3 py-1.5 bg-slate-700/50 hover:bg-slate-700/70 rounded-lg text-sm text-slate-300 hover:text-white transition-colors">
                <RefreshCw className="h-4 w-4" />
                <span>Refresh</span>
              </button>
            </div>
            
            <div className="space-y-3">
              {marketData.map((coin) => (
                <div key={coin.symbol} className="flex items-center justify-between p-4 bg-slate-700/20 rounded-lg hover:bg-slate-700/30 transition-colors">
                  <div className="flex items-center space-x-4">
                    <div className="w-8 h-8 bg-gradient-to-r from-orange-500 to-yellow-500 rounded-full flex items-center justify-center">
                      <span className="text-white text-sm font-bold">
                        {coin.symbol.split('/')[0].substring(0, 2)}
                      </span>
                    </div>
                    <div>
                      <div className="font-medium text-white">{coin.symbol}</div>
                      <div className="text-sm text-slate-400">Vol: {formatLargeNumber(coin.volume)}</div>
                    </div>
                  </div>
                  
                  <div className="text-right">
                    <div className="font-medium text-white">{formatCurrency(coin.price)}</div>
                    <div className={`text-sm flex items-center space-x-1 ${
                      coin.changePercent >= 0 ? 'text-green-400' : 'text-red-400'
                    }`}>
                      {coin.changePercent >= 0 ? (
                        <TrendingUp className="h-3 w-3" />
                      ) : (
                        <TrendingDown className="h-3 w-3" />
                      )}
                      <span>{coin.changePercent.toFixed(2)}%</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Recent Activity */}
        <div>
          <div className="bg-slate-800/30 backdrop-blur-sm rounded-xl p-6 border border-slate-700/50">
            <h3 className="text-lg font-semibold text-white mb-6">Recent Activity</h3>
            
            <div className="space-y-4">
              {activities.map((activity) => {
                const IconComponent = getActivityIcon(activity.type);
                return (
                  <div key={activity.id} className="flex items-start space-x-3">
                    <div className={`p-2 rounded-lg ${activity.status === 'success' ? 'bg-green-500/20' :
                      activity.status === 'warning' ? 'bg-yellow-500/20' :
                      activity.status === 'error' ? 'bg-red-500/20' : 'bg-blue-500/20'
                    }`}>
                      <IconComponent className={`h-4 w-4 ${getActivityColor(activity.status)}`} />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm text-white">{activity.message}</p>
                      <p className="text-xs text-slate-400 mt-1">{activity.timestamp}</p>
                    </div>
                  </div>
                );
              })}
            </div>
            
            <button className="w-full mt-4 py-2 text-sm text-slate-400 hover:text-white transition-colors border border-slate-700/50 rounded-lg hover:bg-slate-700/20">
              View All Activity
            </button>
          </div>
        </div>
      </div>

      {/* Strategy Performance */}
      <div className="bg-slate-800/30 backdrop-blur-sm rounded-xl p-6 border border-slate-700/50">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-semibold text-white">Strategy Performance</h3>
          <div className="flex items-center space-x-2">
            <button className="flex items-center space-x-2 px-3 py-1.5 bg-blue-600 hover:bg-blue-700 rounded-lg text-sm text-white transition-colors">
              <Plus className="h-4 w-4" />
              <span>New Strategy</span>
            </button>
          </div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {strategies.map((strategy) => (
            <div key={strategy.id} className="bg-slate-700/20 rounded-lg p-4 hover:bg-slate-700/30 transition-colors">
              <div className="flex items-center justify-between mb-3">
                <h4 className="font-medium text-white truncate">{strategy.name}</h4>
                <span className={`px-2 py-1 rounded text-xs font-medium ${getStatusColor(strategy.status)}`}>
                  {strategy.status}
                </span>
              </div>
              
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-slate-400">P&L</span>
                  <span className={`text-sm font-medium ${
                    strategy.pnl >= 0 ? 'text-green-400' : 'text-red-400'
                  }`}>
                    {formatCurrency(strategy.pnl)} ({strategy.pnlPercent.toFixed(1)}%)
                  </span>
                </div>
                
                <div className="flex items-center justify-between">
                  <span className="text-sm text-slate-400">Win Rate</span>
                  <span className="text-sm text-white">{strategy.winRate.toFixed(1)}%</span>
                </div>
                
                <div className="flex items-center justify-between">
                  <span className="text-sm text-slate-400">Trades</span>
                  <span className="text-sm text-white">{strategy.trades}</span>
                </div>
                
                <div className="flex items-center justify-between">
                  <span className="text-sm text-slate-400">Last Activity</span>
                  <span className="text-sm text-slate-400">{strategy.lastActivity}</span>
                </div>
              </div>
              
              <div className="flex items-center space-x-2 mt-4">
                <button className="flex-1 py-1.5 px-3 bg-green-600/20 hover:bg-green-600/30 border border-green-600/30 rounded text-green-400 text-xs font-medium transition-colors">
                  <Play className="h-3 w-3 inline mr-1" />
                  Resume
                </button>
                <button className="flex-1 py-1.5 px-3 bg-yellow-600/20 hover:bg-yellow-600/30 border border-yellow-600/30 rounded text-yellow-400 text-xs font-medium transition-colors">
                  <Pause className="h-3 w-3 inline mr-1" />
                  Pause
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <button 
          onClick={() => onNavigate?.('research')}
          className="p-6 bg-gradient-to-r from-blue-600/20 to-purple-600/20 border border-blue-500/30 rounded-xl hover:from-blue-600/30 hover:to-purple-600/30 transition-all text-left"
        >
          <div className="flex items-center space-x-3">
            <Brain className="h-8 w-8 text-blue-400" />
            <div>
              <h3 className="font-medium text-white">AI Strategy Analyzer</h3>
              <p className="text-sm text-slate-400">Get AI insights on your strategies</p>
            </div>
          </div>
        </button>
        
        <button 
          onClick={() => onNavigate?.('backtesting')}
          className="p-6 bg-gradient-to-r from-green-600/20 to-emerald-600/20 border border-green-500/30 rounded-xl hover:from-green-600/30 hover:to-emerald-600/30 transition-all text-left"
        >
          <div className="flex items-center space-x-3">
            <BarChart3 className="h-8 w-8 text-green-400" />
            <div>
              <h3 className="font-medium text-white">Run Backtest</h3>
              <p className="text-sm text-slate-400">Test strategies on historical data</p>
            </div>
          </div>
        </button>
        
        <button 
          onClick={() => onNavigate?.('development')}
          className="p-6 bg-gradient-to-r from-purple-600/20 to-pink-600/20 border border-purple-500/30 rounded-xl hover:from-purple-600/30 hover:to-pink-600/30 transition-all text-left"
        >
          <div className="flex items-center space-x-3">
            <Zap className="h-8 w-8 text-purple-400" />
            <div>
              <h3 className="font-medium text-white">Strategy Builder</h3>
              <p className="text-sm text-slate-400">Create new trading algorithms</p>
            </div>
          </div>
        </button>
        
        <button 
          onClick={() => onNavigate?.('execution')}
          className="p-6 bg-gradient-to-r from-orange-600/20 to-red-600/20 border border-orange-500/30 rounded-xl hover:from-orange-600/30 hover:to-red-600/30 transition-all text-left"
        >
          <div className="flex items-center space-x-3">
            <Target className="h-8 w-8 text-orange-400" />
            <div>
              <h3 className="font-medium text-white">Live Trading</h3>
              <p className="text-sm text-slate-400">Execute strategies in real-time</p>
            </div>
          </div>
        </button>
      </div>
    </div>
  );
};

export default CryptoLabDashboard;