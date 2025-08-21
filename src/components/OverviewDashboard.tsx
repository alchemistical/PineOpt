import React, { useState, useEffect } from 'react';
import { 
  BarChart3, 
  Code2, 
  Database, 
  TrendingUp, 
  ArrowUpRight,
  Activity,
  FileText,
  Zap,
  CheckCircle,
  Clock,
  Users,
  Target
} from 'lucide-react';

interface FeatureCardProps {
  title: string;
  description: string;
  icon: React.ElementType;
  stats?: { label: string; value: string | number }[];
  status: 'active' | 'ready' | 'coming-soon';
  onClick: () => void;
  gradient: string;
}

const FeatureCard: React.FC<FeatureCardProps> = ({
  title,
  description,
  icon: Icon,
  stats,
  status,
  onClick,
  gradient
}) => {
  const statusConfig = {
    active: { color: 'text-green-400', bg: 'bg-green-500/20', text: 'Active' },
    ready: { color: 'text-blue-400', bg: 'bg-blue-500/20', text: 'Ready' },
    'coming-soon': { color: 'text-yellow-400', bg: 'bg-yellow-500/20', text: 'Coming Soon' }
  };

  return (
    <div 
      onClick={status !== 'coming-soon' ? onClick : undefined}
      className={`relative overflow-hidden rounded-xl bg-gradient-to-br ${gradient} p-6 transition-all duration-300 hover:scale-105 ${
        status !== 'coming-soon' ? 'cursor-pointer' : 'opacity-70'
      } border border-gray-700/50 backdrop-blur-sm`}
    >
      {/* Status Badge */}
      <div className={`absolute top-4 right-4 px-2 py-1 rounded-full text-xs font-medium ${statusConfig[status].bg} ${statusConfig[status].color}`}>
        {statusConfig[status].text}
      </div>

      {/* Icon */}
      <div className="mb-4">
        <Icon className="h-8 w-8 text-white" />
      </div>

      {/* Content */}
      <h3 className="text-xl font-semibold text-white mb-2">{title}</h3>
      <p className="text-gray-300 text-sm mb-4">{description}</p>

      {/* Stats */}
      {stats && (
        <div className="grid grid-cols-2 gap-4">
          {stats.map((stat, index) => (
            <div key={index}>
              <div className="text-2xl font-bold text-white">{stat.value}</div>
              <div className="text-xs text-gray-400">{stat.label}</div>
            </div>
          ))}
        </div>
      )}

      {/* Arrow */}
      {status !== 'coming-soon' && (
        <ArrowUpRight className="absolute bottom-4 right-4 h-5 w-5 text-white/60" />
      )}
    </div>
  );
};

interface QuickActionProps {
  label: string;
  description: string;
  icon: React.ElementType;
  onClick: () => void;
  variant: 'primary' | 'secondary';
}

const QuickAction: React.FC<QuickActionProps> = ({
  label,
  description,
  icon: Icon,
  onClick,
  variant
}) => {
  return (
    <button
      onClick={onClick}
      className={`w-full p-4 rounded-lg border transition-all duration-200 text-left ${
        variant === 'primary'
          ? 'bg-gradient-to-r from-blue-500/20 to-purple-500/20 border-blue-500/30 hover:from-blue-500/30 hover:to-purple-500/30'
          : 'bg-gray-800/30 border-gray-700/50 hover:bg-gray-700/30'
      }`}
    >
      <div className="flex items-start space-x-3">
        <Icon className={`h-5 w-5 mt-0.5 ${variant === 'primary' ? 'text-blue-400' : 'text-gray-400'}`} />
        <div>
          <div className="font-medium text-white text-sm">{label}</div>
          <div className="text-xs text-gray-400 mt-1">{description}</div>
        </div>
      </div>
    </button>
  );
};

interface OverviewDashboardProps {
  onNavigate: (view: string) => void;
}

const OverviewDashboard: React.FC<OverviewDashboardProps> = ({ onNavigate }) => {
  const [systemStats, setSystemStats] = useState({
    strategies: 0,
    datasets: 0,
    conversions: 0,
    uptime: '99.9%'
  });

  useEffect(() => {
    // Simulate loading system stats
    const timer = setTimeout(() => {
      setSystemStats({
        strategies: 3,
        datasets: 1,
        conversions: 5,
        uptime: '99.9%'
      });
    }, 1000);

    return () => clearTimeout(timer);
  }, []);

  const features = [
    {
      title: 'Live Crypto Data',
      description: 'Real-time crypto market data from Binance with OHLC charts and multiple timeframes.',
      icon: Database,
      stats: [
        { label: 'Datasets', value: systemStats.datasets },
        { label: 'Binance API', value: 'Live' }
      ],
      status: 'active' as const,
      gradient: 'from-blue-500/20 to-cyan-500/20',
      onClick: () => onNavigate('data')
    },
    {
      title: 'Pine Script Converter',
      description: 'Convert TradingView Pine Script crypto strategies to Python backtesting code.',
      icon: Code2,
      stats: [
        { label: 'Conversions', value: systemStats.conversions },
        { label: 'Success Rate', value: '95%' }
      ],
      status: 'active' as const,
      gradient: 'from-purple-500/20 to-pink-500/20',
      onClick: () => onNavigate('converter')
    },
    {
      title: 'Crypto Strategy Library',
      description: 'Manage and organize your converted crypto strategies with metadata and backtesting results.',
      icon: FileText,
      stats: [
        { label: 'Strategies', value: systemStats.strategies },
        { label: 'Categories', value: 'RSI, MA, Crypto' }
      ],
      status: 'ready' as const,
      gradient: 'from-green-500/20 to-teal-500/20',
      onClick: () => onNavigate('strategies')
    },
    {
      title: 'Crypto Backtesting',
      description: 'Test your converted Pine strategies against historical crypto data with performance metrics.',
      icon: Activity,
      status: 'coming-soon' as const,
      gradient: 'from-orange-500/20 to-red-500/20',
      onClick: () => {}
    },
    {
      title: 'Crypto Portfolio Analytics',
      description: 'Advanced crypto portfolio analysis with risk metrics and performance attribution.',
      icon: TrendingUp,
      status: 'coming-soon' as const,
      gradient: 'from-indigo-500/20 to-blue-500/20',
      onClick: () => {}
    },
    {
      title: 'Live Crypto Trading',
      description: 'Connect to crypto exchanges and execute strategies with risk management.',
      icon: Zap,
      status: 'coming-soon' as const,
      gradient: 'from-yellow-500/20 to-orange-500/20',
      onClick: () => {}
    }
  ];

  const quickActions = [
    {
      label: 'Fetch Crypto Data',
      description: 'Get live crypto data from Binance',
      icon: Database,
      variant: 'primary' as const,
      onClick: () => onNavigate('data')
    },
    {
      label: 'Convert Pine Script',
      description: 'Transform crypto Pine strategies to Python',
      icon: Code2,
      variant: 'primary' as const,
      onClick: () => onNavigate('converter')
    },
    {
      label: 'View Crypto Strategies',
      description: 'Browse converted crypto strategies',
      icon: FileText,
      variant: 'secondary' as const,
      onClick: () => onNavigate('strategies')
    },
    {
      label: 'System Settings',
      description: 'Configure preferences',
      icon: Target,
      variant: 'secondary' as const,
      onClick: () => onNavigate('settings')
    }
  ];

  return (
    <div className="space-y-8">
      {/* Welcome Section */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-blue-600/20 via-purple-600/20 to-pink-600/20 p-8 border border-gray-700/50">
        <div className="relative z-10">
          <h1 className="text-3xl font-bold text-white mb-2">
            Welcome to PineOpt
          </h1>
          <p className="text-gray-300 text-lg mb-6">
            Transform your crypto strategies with our comprehensive Pine Script to Python conversion platform
          </p>
          
          {/* System Status */}
          <div className="flex items-center space-x-6 text-sm">
            <div className="flex items-center space-x-2">
              <CheckCircle className="h-4 w-4 text-green-400" />
              <span className="text-gray-300">System Online</span>
            </div>
            <div className="flex items-center space-x-2">
              <Clock className="h-4 w-4 text-blue-400" />
              <span className="text-gray-300">Uptime: {systemStats.uptime}</span>
            </div>
            <div className="flex items-center space-x-2">
              <Users className="h-4 w-4 text-purple-400" />
              <span className="text-gray-300">Active Session</span>
            </div>
          </div>
        </div>
        
        {/* Background decoration */}
        <div className="absolute top-0 right-0 w-1/2 h-full opacity-10">
          <BarChart3 className="w-full h-full" />
        </div>
      </div>

      {/* Features Grid */}
      <div>
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-white">Platform Features</h2>
          <div className="flex items-center space-x-2 text-sm text-gray-400">
            <div className="w-2 h-2 bg-green-400 rounded-full"></div>
            <span>Active</span>
            <div className="w-2 h-2 bg-blue-400 rounded-full ml-4"></div>
            <span>Ready</span>
            <div className="w-2 h-2 bg-yellow-400 rounded-full ml-4"></div>
            <span>Coming Soon</span>
          </div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
          {features.map((feature, index) => (
            <FeatureCard key={index} {...feature} />
          ))}
        </div>
      </div>

      {/* Quick Actions */}
      <div>
        <h2 className="text-2xl font-bold text-white mb-6">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
          {quickActions.map((action, index) => (
            <QuickAction key={index} {...action} />
          ))}
        </div>
      </div>

      {/* Recent Activity */}
      <div className="bg-gray-800/30 backdrop-blur-sm rounded-xl p-6 border border-gray-700/50">
        <h2 className="text-xl font-semibold text-white mb-4">Recent Activity</h2>
        <div className="space-y-3">
          {[
            { action: 'Pine script converted', details: 'Crypto RSI Strategy → Python', time: '2 min ago', icon: Code2 },
            { action: 'Live data fetched', details: 'BTCUSDT 1h (1,000 bars) from Binance', time: '5 min ago', icon: Database },
            { action: 'Strategy saved', details: 'Crypto Momentum Strategy added to library', time: '8 min ago', icon: FileText }
          ].map((activity, index) => (
            <div key={index} className="flex items-center space-x-3 p-3 rounded-lg bg-gray-700/30">
              <activity.icon className="h-5 w-5 text-gray-400" />
              <div className="flex-1">
                <div className="text-white text-sm font-medium">{activity.action}</div>
                <div className="text-gray-400 text-xs">{activity.details}</div>
              </div>
              <div className="text-gray-500 text-xs">{activity.time}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default OverviewDashboard;