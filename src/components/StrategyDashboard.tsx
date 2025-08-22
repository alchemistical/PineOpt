import React, { useState, useEffect } from 'react';
import StrategyUpload from './StrategyUpload';
import {
  BarChart3,
  Brain,
  Play,
  Upload,
  Settings,
  TrendingUp,
  TrendingDown,
  Activity,
  Clock,
  Target,
  Zap,
  Users,
  Calendar,
  Star,
  Filter,
  Search,
  Plus,
  MoreHorizontal,
  RefreshCw,
  Eye,
  Download,
  Trash2,
  Edit,
  Share2
} from 'lucide-react';

interface Strategy {
  id: string;
  name: string;
  description: string;
  author: string;
  version: string;
  language: 'python' | 'pine';
  validation_status: 'pending' | 'valid' | 'invalid' | 'error';
  file_size: number;
  parameters_count: number;
  dependencies_count: number;
  tags: string[];
  upload_count: number;
  backtest_count: number;
  created_at: string;
  updated_at: string;
  last_used: string | null;
  performance?: {
    total_return: number;
    sharpe_ratio: number;
    max_drawdown: number;
    win_rate: number;
  };
}

interface DashboardStats {
  total_strategies: number;
  valid_strategies: number;
  total_backtests: number;
  active_backtests: number;
  avg_performance: number;
  best_strategy: string;
}

interface StrategyDashboardProps {
  onStrategySelect?: (strategy: Strategy) => void;
  onRunBacktest?: (strategy: Strategy) => void;
}

const StrategyDashboard: React.FC<StrategyDashboardProps> = ({ 
  onStrategySelect, 
  onRunBacktest
}) => {
  const [strategies, setStrategies] = useState<Strategy[]>([]);
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedStrategies, setSelectedStrategies] = useState<Set<string>>(new Set());
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [sortBy, setSortBy] = useState<'name' | 'performance' | 'created_at' | 'last_used'>('created_at');
  const [filterStatus, setFilterStatus] = useState<string>('');
  const [searchQuery, setSearchQuery] = useState('');
  const [showUpload, setShowUpload] = useState(false);
  const [selectedStrategy, setSelectedStrategy] = useState<Strategy | null>(null);
  const [strategyProfile, setStrategyProfile] = useState<any>(null);
  const [profilingLoading, setProfilingLoading] = useState(false);
  const [showProfileModal, setShowProfileModal] = useState(false);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      
      // Load strategies
      const strategiesResponse = await fetch('http://localhost:5007/api/strategies?limit=50');
      const strategiesData = await strategiesResponse.json();
      
      if (strategiesData.success) {
        setStrategies(strategiesData.strategies);
        
        // Calculate real stats from the strategies data
        const realStats = {
          total_strategies: strategiesData.strategies.length,
          valid_strategies: strategiesData.strategies.filter((s: any) => s.validation_status === 'valid').length,
          total_backtests: strategiesData.strategies.reduce((sum: number, s: any) => sum + (s.backtest_count || 0), 0),
          active_backtests: 0, // No active backtests for now
          avg_performance: 0, // No performance data yet
          best_strategy: strategiesData.strategies[0]?.name || 'None'
        };
        
        setStats(realStats);
      }
      
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
      setStats({
        total_strategies: 0,
        valid_strategies: 0,
        total_backtests: 0,
        active_backtests: 0,
        avg_performance: 0,
        best_strategy: 'None'
      });
    } finally {
      setLoading(false);
    }
  };

  const filteredStrategies = strategies.filter(strategy => {
    const matchesSearch = strategy.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         strategy.description?.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         strategy.author.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus = !filterStatus || strategy.validation_status === filterStatus;
    return matchesSearch && matchesStatus;
  });

  const sortedStrategies = [...filteredStrategies].sort((a, b) => {
    switch (sortBy) {
      case 'name':
        return a.name.localeCompare(b.name);
      case 'performance':
        return (b.performance?.total_return || 0) - (a.performance?.total_return || 0);
      case 'last_used':
        return new Date(b.last_used || 0).getTime() - new Date(a.last_used || 0).getTime();
      default:
        return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
    }
  });

  const handleStrategyAction = async (strategyId: string, action: string) => {
    const strategy = strategies.find(s => s.id === strategyId);
    if (!strategy) return;

    switch (action) {
      case 'run':
        onRunBacktest?.(strategy);
        break;
      case 'profile':
        await handleGenerateProfile(strategy);
        break;
      case 'edit':
        // Handle edit
        break;
      case 'delete':
        if (confirm('Are you sure you want to delete this strategy?')) {
          try {
            await fetch(`http://localhost:5007/api/strategies/${strategyId}`, { method: 'DELETE' });
            setStrategies(prev => prev.filter(s => s.id !== strategyId));
          } catch (error) {
            console.error('Failed to delete strategy:', error);
          }
        }
        break;
    }
  };

  const handleGenerateProfile = async (strategy: Strategy) => {
    if (strategy.validation_status !== 'valid') {
      alert('Strategy must be valid to generate AI profile');
      return;
    }

    try {
      setProfilingLoading(true);
      setSelectedStrategy(strategy);
      setShowProfileModal(true);

      const response = await fetch(`http://localhost:5007/api/strategies/${strategy.id}/profile`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      });

      const data = await response.json();

      if (!response.ok || !data.success) {
        throw new Error(data.error || 'Failed to generate strategy profile');
      }

      setStrategyProfile(data.profile);
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to generate AI profile');
      setShowProfileModal(false);
    } finally {
      setProfilingLoading(false);
    }
  };

  const getPerformanceColor = (value: number) => {
    if (value > 0) return 'text-green-400';
    if (value < 0) return 'text-red-400';
    return 'text-gray-400';
  };

  const renderStatsCards = () => {
    if (!stats) return null;

    const cards = [
      {
        title: 'Total Strategies',
        value: stats.total_strategies,
        icon: BarChart3,
        color: 'bg-blue-500/20 text-blue-400'
      },
      {
        title: 'Valid Strategies',
        value: stats.valid_strategies,
        icon: Target,
        color: 'bg-green-500/20 text-green-400'
      },
      {
        title: 'Total Backtests',
        value: stats.total_backtests,
        icon: Activity,
        color: 'bg-purple-500/20 text-purple-400'
      },
      {
        title: 'Active Backtests',
        value: stats.active_backtests,
        icon: Clock,
        color: 'bg-yellow-500/20 text-yellow-400'
      }
    ];

    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {cards.map((card, index) => {
          const IconComponent = card.icon;
          return (
            <div key={index} className="bg-gray-800/30 backdrop-blur-sm rounded-xl p-6 border border-gray-700/50">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-400 text-sm font-medium">{card.title}</p>
                  <p className="text-2xl font-bold text-white mt-1">{card.value.toLocaleString()}</p>
                </div>
                <div className={`p-3 rounded-lg ${card.color}`}>
                  <IconComponent className="h-6 w-6" />
                </div>
              </div>
            </div>
          );
        })}
      </div>
    );
  };

  const renderStrategyCard = (strategy: Strategy) => {
    const isSelected = selectedStrategies.has(strategy.id);
    
    return (
      <div
        key={strategy.id}
        className={`bg-gray-800/30 backdrop-blur-sm rounded-xl p-6 border transition-all cursor-pointer group ${
          isSelected 
            ? 'border-blue-500/50 ring-1 ring-blue-500/25' 
            : 'border-gray-700/50 hover:border-gray-600/50'
        }`}
        onClick={() => onStrategySelect?.(strategy)}
      >
        {/* Header */}
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center space-x-3">
            <div className={`p-2 rounded-lg ${
              strategy.language === 'python' 
                ? 'bg-blue-500/20 text-blue-400' 
                : 'bg-green-500/20 text-green-400'
            }`}>
              {strategy.language === 'python' ? '🐍' : '🌲'}
            </div>
            <div>
              <h3 className="text-lg font-semibold text-white group-hover:text-blue-400 transition-colors">
                {strategy.name}
              </h3>
              <p className="text-sm text-gray-400">by {strategy.author}</p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <div className={`px-2 py-1 rounded text-xs font-medium ${
              strategy.validation_status === 'valid' ? 'bg-green-500/20 text-green-400' :
              strategy.validation_status === 'pending' ? 'bg-yellow-500/20 text-yellow-400' :
              strategy.validation_status === 'invalid' ? 'bg-red-500/20 text-red-400' :
              'bg-gray-500/20 text-gray-400'
            }`}>
              {strategy.validation_status}
            </div>
          </div>
        </div>

        {/* Description */}
        <p className="text-gray-300 text-sm mb-4 line-clamp-2">
          {strategy.description || 'No description provided'}
        </p>

        {/* Performance Metrics */}
        {strategy.performance && (
          <div className="grid grid-cols-2 gap-4 mb-4 p-3 bg-gray-700/20 rounded-lg">
            <div className="text-center">
              <div className={`text-sm font-bold ${getPerformanceColor(strategy.performance.total_return)}`}>
                {strategy.performance.total_return > 0 ? '+' : ''}{strategy.performance.total_return.toFixed(2)}%
              </div>
              <div className="text-xs text-gray-400">Return</div>
            </div>
            <div className="text-center">
              <div className="text-sm font-bold text-white">
                {strategy.performance.sharpe_ratio.toFixed(2)}
              </div>
              <div className="text-xs text-gray-400">Sharpe</div>
            </div>
            <div className="text-center">
              <div className="text-sm font-bold text-red-400">
                -{strategy.performance.max_drawdown.toFixed(2)}%
              </div>
              <div className="text-xs text-gray-400">Drawdown</div>
            </div>
            <div className="text-center">
              <div className="text-sm font-bold text-white">
                {strategy.performance.win_rate.toFixed(1)}%
              </div>
              <div className="text-xs text-gray-400">Win Rate</div>
            </div>
          </div>
        )}

        {/* Tags */}
        {strategy.tags.length > 0 && (
          <div className="flex flex-wrap gap-2 mb-4">
            {strategy.tags.slice(0, 3).map((tag, index) => (
              <span
                key={index}
                className="px-2 py-1 bg-blue-600/20 border border-blue-600/30 rounded text-blue-400 text-xs"
              >
                {tag}
              </span>
            ))}
            {strategy.tags.length > 3 && (
              <span className="px-2 py-1 bg-gray-600/20 border border-gray-600/30 rounded text-gray-400 text-xs">
                +{strategy.tags.length - 3}
              </span>
            )}
          </div>
        )}

        {/* Actions */}
        <div className="flex items-center justify-between pt-4 border-t border-gray-700/50">
          <div className="flex items-center space-x-2">
            <button
              onClick={(e) => {
                e.stopPropagation();
                handleStrategyAction(strategy.id, 'run');
              }}
              disabled={strategy.validation_status !== 'valid'}
              className="flex items-center space-x-1 px-3 py-1 bg-green-600/20 hover:bg-green-600/30 border border-green-600/30 rounded text-green-400 text-xs transition-colors disabled:opacity-50"
            >
              <Play className="h-3 w-3" />
              <span>Run</span>
            </button>
            
            <button
              onClick={(e) => {
                e.stopPropagation();
                handleStrategyAction(strategy.id, 'profile');
              }}
              disabled={strategy.validation_status !== 'valid'}
              className="flex items-center space-x-1 px-3 py-1 bg-purple-600/20 hover:bg-purple-600/30 border border-purple-600/30 rounded text-purple-400 text-xs transition-colors disabled:opacity-50"
            >
              <Brain className="h-3 w-3" />
              <span>Profile</span>
            </button>
          </div>

          <div className="flex items-center space-x-1">
            <button
              onClick={(e) => {
                e.stopPropagation();
                handleStrategyAction(strategy.id, 'edit');
              }}
              className="p-1 text-gray-400 hover:text-blue-400 transition-colors"
            >
              <Edit className="h-4 w-4" />
            </button>
            <button
              onClick={(e) => {
                e.stopPropagation();
                handleStrategyAction(strategy.id, 'delete');
              }}
              className="p-1 text-gray-400 hover:text-red-400 transition-colors"
            >
              <Trash2 className="h-4 w-4" />
            </button>
          </div>
        </div>

        {/* Metadata */}
        <div className="flex items-center justify-between pt-2 text-xs text-gray-500">
          <span>{strategy.backtest_count} backtests</span>
          <span>{new Date(strategy.created_at).toLocaleDateString()}</span>
        </div>
      </div>
    );
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <RefreshCw className="h-8 w-8 animate-spin text-blue-400 mx-auto mb-4" />
          <p className="text-gray-400">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900">
      {/* Header */}
      <div className="bg-gray-800/30 backdrop-blur-sm border-b border-gray-700/50 p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="p-2 bg-gradient-to-r from-purple-500 to-pink-600 rounded-lg">
              <BarChart3 className="h-6 w-6 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-white">Strategy Dashboard</h1>
              <p className="text-gray-400">Manage and monitor your trading strategies</p>
            </div>
          </div>
          
          <div className="flex items-center space-x-3">
            <button
              onClick={loadDashboardData}
              disabled={loading}
              className="flex items-center space-x-2 px-4 py-2 bg-gray-700/50 hover:bg-gray-600/50 rounded-lg transition-colors text-gray-300 hover:text-white disabled:opacity-50"
            >
              <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
              <span>Refresh</span>
            </button>
            
            <button
              onClick={() => setShowUpload(true)}
              className="flex items-center space-x-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
            >
              <Plus className="h-4 w-4" />
              <span>Upload Strategy</span>
            </button>
          </div>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="p-6">
        {renderStatsCards()}

        {/* Controls */}
        <div className="bg-gray-800/30 backdrop-blur-sm rounded-xl p-6 border border-gray-700/50 mb-6">
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-4 lg:space-y-0">
            {/* Search and Filters */}
            <div className="flex items-center space-x-4">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search strategies..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10 pr-4 py-2 bg-gray-700/50 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500 w-64"
                />
              </div>
              
              <select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
                className="px-3 py-2 bg-gray-700/50 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-blue-500"
              >
                <option value="">All Status</option>
                <option value="valid">Valid</option>
                <option value="pending">Pending</option>
                <option value="invalid">Invalid</option>
                <option value="error">Error</option>
              </select>
              
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as any)}
                className="px-3 py-2 bg-gray-700/50 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-blue-500"
              >
                <option value="created_at">Latest</option>
                <option value="name">Name</option>
                <option value="performance">Performance</option>
                <option value="last_used">Last Used</option>
              </select>
            </div>

            {/* View Controls */}
            <div className="flex items-center space-x-2">
              <button
                onClick={() => setViewMode('grid')}
                className={`p-2 rounded-lg transition-colors ${
                  viewMode === 'grid' 
                    ? 'bg-blue-600 text-white' 
                    : 'bg-gray-700/50 text-gray-400 hover:text-white'
                }`}
              >
                <BarChart3 className="h-4 w-4" />
              </button>
              <button
                onClick={() => setViewMode('list')}
                className={`p-2 rounded-lg transition-colors ${
                  viewMode === 'list' 
                    ? 'bg-blue-600 text-white' 
                    : 'bg-gray-700/50 text-gray-400 hover:text-white'
                }`}
              >
                <Activity className="h-4 w-4" />
              </button>
            </div>
          </div>
        </div>

        {/* Strategies Grid */}
        {sortedStrategies.length > 0 ? (
          <div className={`${
            viewMode === 'grid' 
              ? 'grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6' 
              : 'space-y-4'
          }`}>
            {sortedStrategies.map(renderStrategyCard)}
          </div>
        ) : (
          <div className="text-center py-12">
            <div className="p-4 bg-gray-700/30 rounded-full w-fit mx-auto mb-4">
              <BarChart3 className="h-8 w-8 text-gray-400" />
            </div>
            <h3 className="text-xl font-semibold text-white mb-2">
              {searchQuery || filterStatus ? 'No strategies found' : 'No strategies yet'}
            </h3>
            <p className="text-gray-400 mb-6">
              {searchQuery || filterStatus 
                ? 'Try adjusting your search or filters' 
                : 'Upload your first trading strategy to get started'
              }
            </p>
            <button
              onClick={() => setShowUpload(true)}
              className="flex items-center space-x-2 px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors mx-auto"
            >
              <Upload className="h-4 w-4" />
              <span>Upload Strategy</span>
            </button>
          </div>
        )}
      </div>
      
      {/* Upload Modal */}
      {showUpload && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-gray-800 rounded-xl w-full max-w-4xl max-h-[90vh] overflow-y-auto border border-gray-600">
            <StrategyUpload 
              onStrategyUploaded={(strategy) => {
                // Add the new strategy to the list
                setStrategies(prev => [strategy, ...prev]);
                setShowUpload(false);
                // Reload data to get updated stats
                loadDashboardData();
              }}
              onClose={() => setShowUpload(false)}
            />
          </div>
        </div>
      )}
      
      {/* AI Profile Modal - Reusing the same modal from StrategyLibrary */}
      {showProfileModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-gray-800 rounded-xl w-full max-w-4xl max-h-[90vh] overflow-y-auto border border-gray-600">
            {/* Modal Header */}
            <div className="flex items-center justify-between p-6 border-b border-gray-700">
              <div className="flex items-center space-x-3">
                <div className="p-2 bg-purple-600/20 rounded-lg">
                  <Brain className="h-5 w-5 text-purple-400" />
                </div>
                <div>
                  <h2 className="text-xl font-bold text-white">AI Strategy Profile</h2>
                  <p className="text-gray-400">{selectedStrategy?.name}</p>
                </div>
              </div>
              <button
                onClick={() => {
                  setShowProfileModal(false);
                  setStrategyProfile(null);
                  setSelectedStrategy(null);
                }}
                className="p-2 text-gray-400 hover:text-white transition-colors"
              >
                <X className="h-5 w-5" />
              </button>
            </div>
            
            {/* Modal Content */}
            <div className="p-6">
              {profilingLoading ? (
                <div className="flex flex-col items-center justify-center py-12 space-y-4">
                  <div className="relative">
                    <div className="p-4 bg-purple-600/20 rounded-full">
                      <Brain className="h-8 w-8 text-purple-400 animate-pulse" />
                    </div>
                    <div className="absolute inset-0 rounded-full border-2 border-purple-500/30 border-t-purple-500 animate-spin"></div>
                  </div>
                  <div className="text-center">
                    <h3 className="text-lg font-semibold text-white">Analyzing Strategy</h3>
                    <p className="text-gray-400">AI is profiling your trading algorithm...</p>
                  </div>
                </div>
              ) : strategyProfile ? (
                <div className="space-y-6">
                  {/* Quick Summary */}
                  <div className="bg-gray-700/30 rounded-lg p-6 border border-gray-600/50">
                    <h3 className="text-lg font-semibold text-white mb-4">Analysis Summary</h3>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      <div className="text-center">
                        <div className="text-xl font-bold text-blue-400">
                          {strategyProfile.analysis_summary?.strategy_type?.replace('_', ' ').toUpperCase() || 'UNKNOWN'}
                        </div>
                        <div className="text-sm text-gray-400">Strategy Type</div>
                      </div>
                      <div className="text-center">
                        <div className="text-xl font-bold text-green-400">
                          {strategyProfile.analysis_summary?.complexity_score || 0}/100
                        </div>
                        <div className="text-sm text-gray-400">Complexity</div>
                      </div>
                      <div className="text-center">
                        <div className="text-xl font-bold text-purple-400">
                          {strategyProfile.analysis_summary?.indicators_used?.length || 0}
                        </div>
                        <div className="text-sm text-gray-400">Indicators</div>
                      </div>
                      <div className="text-center">
                        <div className="text-xl font-bold text-yellow-400">
                          {strategyProfile.analysis_summary?.risk_level?.toUpperCase() || 'UNKNOWN'}
                        </div>
                        <div className="text-sm text-gray-400">Risk Level</div>
                      </div>
                    </div>
                  </div>

                  {/* AI Insights */}
                  {strategyProfile.ai_insights && (
                    <div className="bg-gray-700/30 rounded-lg p-6 border border-gray-600/50">
                      <h3 className="text-lg font-semibold text-white mb-4">AI Insights</h3>
                      <div className="space-y-4">
                        <div>
                          <h4 className="font-medium text-white mb-2">Summary</h4>
                          <p className="text-gray-300">{strategyProfile.ai_insights.summary}</p>
                        </div>
                        
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                          <div>
                            <h4 className="font-medium text-green-400 mb-2">Strengths</h4>
                            <ul className="space-y-1">
                              {(strategyProfile.ai_insights.strengths || []).map((strength: string, index: number) => (
                                <li key={index} className="text-sm text-gray-300">• {strength}</li>
                              ))}
                            </ul>
                          </div>
                          
                          <div>
                            <h4 className="font-medium text-red-400 mb-2">Weaknesses</h4>
                            <ul className="space-y-1">
                              {(strategyProfile.ai_insights.weaknesses || []).map((weakness: string, index: number) => (
                                <li key={index} className="text-sm text-gray-300">• {weakness}</li>
                              ))}
                            </ul>
                          </div>
                          
                          <div>
                            <h4 className="font-medium text-blue-400 mb-2">Recommendations</h4>
                            <ul className="space-y-1">
                              {(strategyProfile.ai_insights.recommendations || []).map((rec: string, index: number) => (
                                <li key={index} className="text-sm text-gray-300">• {rec}</li>
                              ))}
                            </ul>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Full Report */}
                  {strategyProfile.full_report && (
                    <div className="bg-gray-700/30 rounded-lg p-6 border border-gray-600/50">
                      <h3 className="text-lg font-semibold text-white mb-4">Detailed Report</h3>
                      <div className="bg-gray-900/50 rounded-lg p-4 max-h-64 overflow-y-auto">
                        <pre className="text-gray-300 text-sm whitespace-pre-wrap font-mono">
                          {strategyProfile.full_report}
                        </pre>
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-center py-12">
                  <div className="p-4 bg-red-600/20 rounded-full w-fit mx-auto mb-4">
                    <AlertCircle className="h-8 w-8 text-red-400" />
                  </div>
                  <h3 className="text-lg font-semibold text-white mb-2">Failed to Generate Profile</h3>
                  <p className="text-gray-400">Unable to analyze the strategy. Please try again.</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default StrategyDashboard;