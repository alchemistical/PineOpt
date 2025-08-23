import React, { useState, useEffect } from 'react';
import { 
  Library,
  Search,
  Filter,
  Plus,
  FileCode,
  FileText,
  CheckCircle,
  AlertTriangle,
  AlertCircle,
  X,
  Calendar,
  User,
  Tag,
  BarChart3,
  Play,
  Edit,
  Trash2,
  Loader,
  RefreshCw,
  Download,
  Brain,
  TrendingUp,
  Shield,
  Zap,
  Target,
  Activity
} from 'lucide-react';

import StrategyUpload from './StrategyUpload';

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
}

interface StrategyProfile {
  strategy_id: string;
  analysis_summary: {
    strategy_type: string;
    complexity_score: number;
    lines_of_code: number;
    indicators_used: string[];
    risk_level: string;
    trading_frequency: string;
  };
  technical_analysis: {
    indicators_detected: string[];
    signal_types: string[];
    has_risk_management: boolean;
    has_stop_loss: boolean;
    has_position_sizing: boolean;
  };
  ai_insights: {
    summary: string;
    strengths: string[];
    weaknesses: string[];
    recommendations: string[];
    market_suitability: string;
  };
  full_report: string;
  generated_at: string;
}

interface StrategyLibraryProps {
  onStrategySelect?: (strategy: Strategy) => void;
  onRunBacktest?: (strategy: Strategy) => void;
}

const StrategyLibrary: React.FC<StrategyLibraryProps> = ({ onStrategySelect, onRunBacktest }) => {
  const [strategies, setStrategies] = useState<Strategy[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showUpload, setShowUpload] = useState(false);
  
  // AI Profiling state
  const [selectedStrategy, setSelectedStrategy] = useState<Strategy | null>(null);
  const [strategyProfile, setStrategyProfile] = useState<StrategyProfile | null>(null);
  const [profilingLoading, setProfilingLoading] = useState(false);
  const [showProfileModal, setShowProfileModal] = useState(false);
  
  // Filters
  const [searchQuery, setSearchQuery] = useState('');
  const [languageFilter, setLanguageFilter] = useState<string>('');
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [authorFilter, setAuthorFilter] = useState<string>('');
  const [tagFilter, setTagFilter] = useState<string>('');
  
  // Pagination
  const [currentPage, setCurrentPage] = useState(0);
  const [hasMore, setHasMore] = useState(true);
  
  const loadStrategies = async (reset = false) => {
    try {
      setLoading(true);
      if (reset) {
        setCurrentPage(0);
        setStrategies([]);
      }
      
      const params = new URLSearchParams();
      if (searchQuery) params.append('search', searchQuery);
      if (languageFilter) params.append('language', languageFilter);
      if (statusFilter) params.append('validation_status', statusFilter);
      if (authorFilter) params.append('author', authorFilter);
      if (tagFilter) params.append('tags', tagFilter);
      params.append('limit', '20');
      params.append('offset', (reset ? 0 : currentPage * 20).toString());
      
      const response = await fetch(`http://localhost:5007/api/v1/strategies/list?${params}`);
      const data = await response.json();
      
      if (!response.ok || data.status !== 'success') {
        throw new Error(data.error || 'Failed to load strategies');
      }
      
      if (reset) {
        setStrategies(data.strategies);
      } else {
        setStrategies(prev => [...prev, ...data.strategies]);
      }
      
      setHasMore(data.pagination?.has_more || false);
      setError(null);
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load strategies');
    } finally {
      setLoading(false);
    }
  };
  
  useEffect(() => {
    loadStrategies(true);
  }, [searchQuery, languageFilter, statusFilter, authorFilter, tagFilter]);
  
  const handleLoadMore = () => {
    if (!loading && hasMore) {
      setCurrentPage(prev => prev + 1);
      loadStrategies(false);
    }
  };
  
  const handleDeleteStrategy = async (strategyId: string) => {
    if (!confirm('Are you sure you want to delete this strategy?')) {
      return;
    }
    
    try {
      const response = await fetch(`http://localhost:5007/api/v1/strategies/${strategyId}`, {
        method: 'DELETE'
      });
      
      const data = await response.json();
      
      if (!response.ok || data.status !== 'success') {
        throw new Error(data.error || 'Failed to delete strategy');
      }
      
      // Remove from local state
      setStrategies(prev => prev.filter(s => s.id !== strategyId));
      
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to delete strategy');
    }
  };
  
  const handleStrategyUploaded = (strategy: any) => {
    // Add to the top of the list
    setStrategies(prev => [strategy, ...prev]);
    setShowUpload(false);
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

      const response = await fetch(`http://localhost:5007/api/v1/strategies/${strategy.id}/profile`, {
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

  const handleRunBacktest = async (strategy: Strategy) => {
    if (strategy.validation_status !== 'valid') {
      alert('Strategy must be valid to run backtests');
      return;
    }

    try {
      // Call the parent callback if provided
      onRunBacktest?.(strategy);
      
      // For now, show a confirmation that the backtest is initiated
      const shouldRun = confirm(
        `Run backtest for "${strategy.name}"?\n\n` +
        `This will execute the strategy against historical data.\n` +
        `Default settings:\n` +
        `• Start Date: 2023-01-01\n` +
        `• End Date: 2024-01-01\n` +
        `• Initial Capital: $10,000\n\n` +
        `Click OK to proceed.`
      );

      if (shouldRun) {
        // Log the backtest request for development
        console.log('Backtest requested for strategy:', {
          id: strategy.id,
          name: strategy.name,
          language: strategy.language,
          validation_status: strategy.validation_status
        });

        alert(
          `Backtest initiated for "${strategy.name}"!\n\n` +
          `The strategy is now being executed against historical data. ` +
          `Results will be available in the backtesting dashboard once complete.\n\n` +
          `Note: This is a demonstration. In production, this would trigger ` +
          `the actual backtesting engine.`
        );

        // Update backtest count optimistically
        setStrategies(prev => prev.map(s => 
          s.id === strategy.id 
            ? { ...s, backtest_count: s.backtest_count + 1, last_used: new Date().toISOString() }
            : s
        ));
      }
    } catch (error) {
      console.error('Backtest error:', error);
      alert(`Error starting backtest: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  };

  const handleEditStrategy = (strategy: Strategy) => {
    try {
      // For now, show the strategy details in a simple dialog
      const details = `
Strategy: ${strategy.name}
Author: ${strategy.author}
Language: ${strategy.language}
Status: ${strategy.validation_status}
Created: ${new Date(strategy.created_at).toLocaleString()}
Parameters: ${strategy.parameters_count}
Dependencies: ${strategy.dependencies_count}
Backtests: ${strategy.backtest_count}

Description: ${strategy.description || 'No description provided'}

Tags: ${strategy.tags.join(', ') || 'No tags'}
      `;
      
      const shouldEdit = confirm(`Strategy Details:\n\n${details}\n\nWould you like to open the editing interface?`);
      
      if (shouldEdit) {
        // Call the parent callback if provided
        onStrategySelect?.(strategy);
        alert('Strategy editing interface will open in the Strategy Dashboard. This feature is being developed.');
      }
    } catch (error) {
      console.error('Edit strategy error:', error);
      alert('Error opening strategy editor');
    }
  };
  
  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'valid':
        return <CheckCircle className="h-4 w-4 text-green-400" />;
      case 'invalid':
        return <AlertCircle className="h-4 w-4 text-red-400" />;
      case 'pending':
        return <Loader className="h-4 w-4 text-yellow-400 animate-spin" />;
      case 'error':
        return <AlertTriangle className="h-4 w-4 text-red-500" />;
      default:
        return <AlertTriangle className="h-4 w-4 text-gray-400" />;
    }
  };
  
  const getLanguageIcon = (language: string) => {
    return language === 'python' ? 
      <FileCode className="h-4 w-4 text-blue-400" /> : 
      <FileText className="h-4 w-4 text-green-400" />;
  };
  
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };
  
  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };
  
  if (showUpload) {
    return (
      <StrategyUpload
        onStrategyUploaded={handleStrategyUploaded}
        onClose={() => setShowUpload(false)}
      />
    );
  }
  
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center space-y-4 sm:space-y-0">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-gradient-to-r from-purple-500 to-pink-600 rounded-lg">
            <Library className="h-5 w-5 text-white" />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-white">Strategy Library</h1>
            <p className="text-gray-400">Manage and organize your trading algorithms</p>
          </div>
        </div>
        
        <div className="flex items-center space-x-3">
          <button
            onClick={() => loadStrategies(true)}
            disabled={loading}
            className="flex items-center space-x-2 px-4 py-2 bg-gray-700/50 hover:bg-gray-600/50 rounded-lg transition-all text-gray-300 hover:text-white disabled:opacity-50"
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
      
      {/* Filters */}
      <div className="bg-gray-800/30 backdrop-blur-sm rounded-xl p-6 border border-gray-700/50">
        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4">
          {/* Search */}
          <div className="lg:col-span-2">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search strategies..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 bg-gray-700/50 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
              />
            </div>
          </div>
          
          {/* Language Filter */}
          <div>
            <select
              value={languageFilter}
              onChange={(e) => setLanguageFilter(e.target.value)}
              className="w-full px-3 py-2 bg-gray-700/50 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-blue-500"
            >
              <option value="">All Languages</option>
              <option value="python">Python</option>
              <option value="pine">Pine Script</option>
            </select>
          </div>
          
          {/* Status Filter */}
          <div>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="w-full px-3 py-2 bg-gray-700/50 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-blue-500"
            >
              <option value="">All Status</option>
              <option value="valid">Valid</option>
              <option value="invalid">Invalid</option>
              <option value="pending">Pending</option>
              <option value="error">Error</option>
            </select>
          </div>
          
          {/* Author Filter */}
          <div>
            <input
              type="text"
              placeholder="Author..."
              value={authorFilter}
              onChange={(e) => setAuthorFilter(e.target.value)}
              className="w-full px-3 py-2 bg-gray-700/50 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
            />
          </div>
          
          {/* Tag Filter */}
          <div>
            <input
              type="text"
              placeholder="Tag..."
              value={tagFilter}
              onChange={(e) => setTagFilter(e.target.value)}
              className="w-full px-3 py-2 bg-gray-700/50 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
            />
          </div>
        </div>
      </div>
      
      {/* Error Display */}
      {error && (
        <div className="bg-red-500/20 border border-red-500/30 rounded-lg p-4">
          <div className="flex items-center space-x-2">
            <AlertCircle className="h-5 w-5 text-red-400" />
            <p className="text-red-400">{error}</p>
          </div>
        </div>
      )}
      
      {/* Strategy Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
        {strategies.map((strategy) => (
          <div
            key={strategy.id}
            className="bg-gray-800/30 backdrop-blur-sm rounded-xl p-6 border border-gray-700/50 hover:border-gray-600/50 transition-all cursor-pointer group"
            onClick={() => onStrategySelect?.(strategy)}
          >
            {/* Header */}
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center space-x-2">
                {getLanguageIcon(strategy.language)}
                <h3 className="text-lg font-semibold text-white group-hover:text-blue-400 transition-colors">
                  {strategy.name}
                </h3>
              </div>
              <div className="flex items-center space-x-1">
                {getStatusIcon(strategy.validation_status)}
              </div>
            </div>
            
            {/* Description */}
            <p className="text-gray-400 text-sm mb-4 line-clamp-2">
              {strategy.description || 'No description provided'}
            </p>
            
            {/* Metadata */}
            <div className="space-y-2 mb-4 text-xs">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-1 text-gray-500">
                  <User className="h-3 w-3" />
                  <span>{strategy.author}</span>
                </div>
                <span className="text-gray-500 capitalize">{strategy.language}</span>
              </div>
              
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-1 text-gray-500">
                  <Calendar className="h-3 w-3" />
                  <span>{formatDate(strategy.created_at)}</span>
                </div>
                <span className="text-gray-500">{formatFileSize(strategy.file_size)}</span>
              </div>
              
              <div className="flex items-center justify-between">
                <span className="text-gray-500">
                  {strategy.parameters_count} params, {strategy.dependencies_count} deps
                </span>
                <span className="text-gray-500">
                  {strategy.backtest_count} backtests
                </span>
              </div>
            </div>
            
            {/* Tags */}
            {strategy.tags.length > 0 && (
              <div className="mb-4">
                <div className="flex flex-wrap gap-1">
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
              </div>
            )}
            
            {/* Actions */}
            <div className="flex items-center justify-between pt-4 border-t border-gray-700/50">
              <div className="flex items-center space-x-2">
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    handleRunBacktest(strategy);
                  }}
                  disabled={strategy.validation_status !== 'valid'}
                  className="flex items-center space-x-1 px-3 py-1 bg-green-600/20 hover:bg-green-600/30 border border-green-600/30 rounded text-green-400 text-xs transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <Play className="h-3 w-3" />
                  <span>Run</span>
                </button>
                
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    handleEditStrategy(strategy);
                  }}
                  className="flex items-center space-x-1 px-3 py-1 bg-blue-600/20 hover:bg-blue-600/30 border border-blue-600/30 rounded text-blue-400 text-xs transition-colors"
                >
                  <Edit className="h-3 w-3" />
                  <span>Edit</span>
                </button>
                
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    handleGenerateProfile(strategy);
                  }}
                  disabled={strategy.validation_status !== 'valid'}
                  className="flex items-center space-x-1 px-3 py-1 bg-purple-600/20 hover:bg-purple-600/30 border border-purple-600/30 rounded text-purple-400 text-xs transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <Brain className="h-3 w-3" />
                  <span>AI Profile</span>
                </button>
              </div>
              
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  handleDeleteStrategy(strategy.id);
                }}
                className="p-1 text-gray-500 hover:text-red-400 transition-colors"
              >
                <Trash2 className="h-3 w-3" />
              </button>
            </div>
          </div>
        ))}
      </div>
      
      {/* Empty State */}
      {strategies.length === 0 && !loading && (
        <div className="text-center py-12">
          <div className="p-4 bg-gray-700/30 rounded-full w-fit mx-auto mb-4">
            <Library className="h-8 w-8 text-gray-400" />
          </div>
          <h3 className="text-xl font-semibold text-white mb-2">No Strategies Found</h3>
          <p className="text-gray-400 mb-6">
            {searchQuery || languageFilter || statusFilter || authorFilter || tagFilter
              ? 'Try adjusting your filters or search query'
              : 'Upload your first trading strategy to get started'
            }
          </p>
          <button
            onClick={() => setShowUpload(true)}
            className="flex items-center space-x-2 px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors mx-auto"
          >
            <Plus className="h-4 w-4" />
            <span>Upload Strategy</span>
          </button>
        </div>
      )}
      
      {/* Load More */}
      {hasMore && strategies.length > 0 && (
        <div className="text-center">
          <button
            onClick={handleLoadMore}
            disabled={loading}
            className="flex items-center space-x-2 px-6 py-3 bg-gray-700/50 hover:bg-gray-600/50 text-gray-300 hover:text-white rounded-lg transition-colors mx-auto disabled:opacity-50"
          >
            {loading ? (
              <>
                <Loader className="h-4 w-4 animate-spin" />
                <span>Loading...</span>
              </>
            ) : (
              <>
                <Download className="h-4 w-4" />
                <span>Load More</span>
              </>
            )}
          </button>
        </div>
      )}
      
      {/* AI Profiling Modal */}
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
            <div className="p-6 space-y-6">
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
                <>
                  {/* Analysis Summary */}
                  <div className="bg-gray-700/30 rounded-lg p-6 border border-gray-600/50">
                    <h3 className="text-lg font-semibold text-white mb-4 flex items-center space-x-2">
                      <BarChart3 className="h-5 w-5 text-blue-400" />
                      <span>Analysis Summary</span>
                    </h3>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      <div className="text-center">
                        <div className="text-2xl font-bold text-blue-400">
                          {strategyProfile.analysis_summary.strategy_type.replace('_', ' ').toUpperCase()}
                        </div>
                        <div className="text-sm text-gray-400">Strategy Type</div>
                      </div>
                      <div className="text-center">
                        <div className="text-2xl font-bold text-green-400">
                          {strategyProfile.analysis_summary.complexity_score}/100
                        </div>
                        <div className="text-sm text-gray-400">Complexity</div>
                      </div>
                      <div className="text-center">
                        <div className="text-2xl font-bold text-purple-400">
                          {strategyProfile.analysis_summary.lines_of_code}
                        </div>
                        <div className="text-sm text-gray-400">Lines of Code</div>
                      </div>
                      <div className="text-center">
                        <div className={`text-2xl font-bold ${
                          strategyProfile.analysis_summary.risk_level === 'low' ? 'text-green-400' :
                          strategyProfile.analysis_summary.risk_level === 'medium' ? 'text-yellow-400' :
                          'text-red-400'
                        }`}>
                          {strategyProfile.analysis_summary.risk_level.toUpperCase()}
                        </div>
                        <div className="text-sm text-gray-400">Risk Level</div>
                      </div>
                    </div>
                  </div>

                  {/* Technical Analysis */}
                  <div className="bg-gray-700/30 rounded-lg p-6 border border-gray-600/50">
                    <h3 className="text-lg font-semibold text-white mb-4 flex items-center space-x-2">
                      <TrendingUp className="h-5 w-5 text-green-400" />
                      <span>Technical Analysis</span>
                    </h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div>
                        <h4 className="font-medium text-white mb-2">Indicators Used</h4>
                        <div className="flex flex-wrap gap-2">
                          {strategyProfile.technical_analysis.indicators_detected.map((indicator, index) => (
                            <span
                              key={index}
                              className="px-3 py-1 bg-blue-600/20 border border-blue-600/30 rounded text-blue-400 text-sm"
                            >
                              {indicator}
                            </span>
                          ))}
                        </div>
                      </div>
                      <div>
                        <h4 className="font-medium text-white mb-2">Risk Management</h4>
                        <div className="space-y-2">
                          <div className="flex items-center justify-between">
                            <span className="text-gray-400">Stop Loss</span>
                            <div className="flex items-center space-x-1">
                              {strategyProfile.technical_analysis.has_stop_loss ? 
                                <CheckCircle className="h-4 w-4 text-green-400" /> :
                                <AlertCircle className="h-4 w-4 text-red-400" />
                              }
                              <span className={strategyProfile.technical_analysis.has_stop_loss ? 'text-green-400' : 'text-red-400'}>
                                {strategyProfile.technical_analysis.has_stop_loss ? 'Yes' : 'No'}
                              </span>
                            </div>
                          </div>
                          <div className="flex items-center justify-between">
                            <span className="text-gray-400">Position Sizing</span>
                            <div className="flex items-center space-x-1">
                              {strategyProfile.technical_analysis.has_position_sizing ? 
                                <CheckCircle className="h-4 w-4 text-green-400" /> :
                                <AlertCircle className="h-4 w-4 text-red-400" />
                              }
                              <span className={strategyProfile.technical_analysis.has_position_sizing ? 'text-green-400' : 'text-red-400'}>
                                {strategyProfile.technical_analysis.has_position_sizing ? 'Yes' : 'No'}
                              </span>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* AI Insights */}
                  <div className="bg-gray-700/30 rounded-lg p-6 border border-gray-600/50">
                    <h3 className="text-lg font-semibold text-white mb-4 flex items-center space-x-2">
                      <Zap className="h-5 w-5 text-yellow-400" />
                      <span>AI Insights</span>
                    </h3>
                    
                    {/* Summary */}
                    <div className="mb-6">
                      <h4 className="font-medium text-white mb-2">Summary</h4>
                      <p className="text-gray-300">{strategyProfile.ai_insights.summary}</p>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                      {/* Strengths */}
                      <div>
                        <h4 className="font-medium text-white mb-2 flex items-center space-x-1">
                          <Shield className="h-4 w-4 text-green-400" />
                          <span>Strengths</span>
                        </h4>
                        <ul className="space-y-2">
                          {strategyProfile.ai_insights.strengths.map((strength, index) => (
                            <li key={index} className="flex items-start space-x-2">
                              <CheckCircle className="h-4 w-4 text-green-400 mt-0.5 flex-shrink-0" />
                              <span className="text-gray-300 text-sm">{strength}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                      
                      {/* Weaknesses */}
                      <div>
                        <h4 className="font-medium text-white mb-2 flex items-center space-x-1">
                          <AlertTriangle className="h-4 w-4 text-red-400" />
                          <span>Weaknesses</span>
                        </h4>
                        <ul className="space-y-2">
                          {strategyProfile.ai_insights.weaknesses.map((weakness, index) => (
                            <li key={index} className="flex items-start space-x-2">
                              <AlertCircle className="h-4 w-4 text-red-400 mt-0.5 flex-shrink-0" />
                              <span className="text-gray-300 text-sm">{weakness}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                      
                      {/* Recommendations */}
                      <div>
                        <h4 className="font-medium text-white mb-2 flex items-center space-x-1">
                          <Target className="h-4 w-4 text-blue-400" />
                          <span>Recommendations</span>
                        </h4>
                        <ul className="space-y-2">
                          {strategyProfile.ai_insights.recommendations.map((recommendation, index) => (
                            <li key={index} className="flex items-start space-x-2">
                              <Activity className="h-4 w-4 text-blue-400 mt-0.5 flex-shrink-0" />
                              <span className="text-gray-300 text-sm">{recommendation}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>
                    
                    {/* Market Suitability */}
                    <div className="mt-6 p-4 bg-blue-600/10 border border-blue-600/20 rounded-lg">
                      <h4 className="font-medium text-white mb-2">Market Suitability</h4>
                      <p className="text-blue-300">{strategyProfile.ai_insights.market_suitability}</p>
                    </div>
                  </div>

                  {/* Full Report */}
                  <div className="bg-gray-700/30 rounded-lg p-6 border border-gray-600/50">
                    <h3 className="text-lg font-semibold text-white mb-4 flex items-center space-x-2">
                      <FileText className="h-5 w-5 text-gray-400" />
                      <span>Detailed Report</span>
                    </h3>
                    <div className="bg-gray-900/50 rounded-lg p-4 max-h-64 overflow-y-auto">
                      <pre className="text-gray-300 text-sm whitespace-pre-wrap font-mono">
                        {strategyProfile.full_report}
                      </pre>
                    </div>
                  </div>
                </>
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

export default StrategyLibrary;