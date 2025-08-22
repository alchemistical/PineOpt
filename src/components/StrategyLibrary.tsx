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
  Download
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

interface StrategyLibraryProps {
  onStrategySelect?: (strategy: Strategy) => void;
  onRunBacktest?: (strategy: Strategy) => void;
}

const StrategyLibrary: React.FC<StrategyLibraryProps> = ({ onStrategySelect, onRunBacktest }) => {
  const [strategies, setStrategies] = useState<Strategy[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showUpload, setShowUpload] = useState(false);
  
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
      
      const response = await fetch(`/api/strategies?${params}`);
      const data = await response.json();
      
      if (!response.ok || !data.success) {
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
      const response = await fetch(`/api/strategies/${strategyId}`, {
        method: 'DELETE'
      });
      
      const data = await response.json();
      
      if (!response.ok || !data.success) {
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
                    onRunBacktest?.(strategy);
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
                    // TODO: Open edit modal
                  }}
                  className="flex items-center space-x-1 px-3 py-1 bg-blue-600/20 hover:bg-blue-600/30 border border-blue-600/30 rounded text-blue-400 text-xs transition-colors"
                >
                  <Edit className="h-3 w-3" />
                  <span>Edit</span>
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
    </div>
  );
};

export default StrategyLibrary;