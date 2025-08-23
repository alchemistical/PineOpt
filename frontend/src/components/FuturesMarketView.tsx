import React, { useState, useEffect } from 'react';
import { TrendingUp, Search, Filter, Loader, RefreshCw, BarChart3, DollarSign, Activity, ArrowUpRight, ArrowDownRight } from 'lucide-react';
import AdvancedChart from './AdvancedChart';

export interface FuturesPair {
  symbol: string;
  baseAsset: string;
  quoteAsset: string;
  price: number;
  change24h: number;
  volume24h: number;
  quoteVolume24h: number;
  high24h: number;
  low24h: number;
  status: string;
}

interface FuturesMarketViewProps {
  onPairSelect?: (pair: FuturesPair) => void;
}

const FuturesMarketView: React.FC<FuturesMarketViewProps> = ({ onPairSelect }) => {
  const [pairs, setPairs] = useState<FuturesPair[]>([]);
  const [selectedPair, setSelectedPair] = useState<FuturesPair | null>(null);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState<'volume' | 'price' | 'change'>('volume');
  const [showChart, setShowChart] = useState(false);

  const fetchFuturesPairs = async (refresh = false) => {
    try {
      setLoading(true);
      const response = await fetch(`/api/futures/pairs?limit=100&sort=${sortBy}&refresh=${refresh}`);
      const data = await response.json();
      
      if (data.success) {
        setPairs(data.data);
        if (data.data.length > 0 && !selectedPair) {
          setSelectedPair(data.data[0]);
        }
      } else {
        console.error('Failed to fetch futures pairs:', data.error);
      }
    } catch (error) {
      console.error('Error fetching futures pairs:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFuturesPairs();
  }, [sortBy]);

  const filteredPairs = pairs.filter(pair => 
    pair.symbol.toLowerCase().includes(searchQuery.toLowerCase()) ||
    pair.baseAsset.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handlePairClick = (pair: FuturesPair) => {
    setSelectedPair(pair);
    setShowChart(true);
    onPairSelect?.(pair);
  };

  const formatPrice = (price: number) => {
    if (price >= 1000) return price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    if (price >= 1) return price.toFixed(4);
    if (price >= 0.01) return price.toFixed(6);
    return price.toFixed(8);
  };

  const formatVolume = (volume: number) => {
    if (volume >= 1e9) return `${(volume / 1e9).toFixed(1)}B`;
    if (volume >= 1e6) return `${(volume / 1e6).toFixed(1)}M`;
    if (volume >= 1e3) return `${(volume / 1e3).toFixed(1)}K`;
    return volume.toFixed(0);
  };

  const formatChange = (change: number) => {
    const color = change >= 0 ? 'text-green-400' : 'text-red-400';
    const icon = change >= 0 ? <ArrowUpRight className="h-3 w-3" /> : <ArrowDownRight className="h-3 w-3" />;
    return (
      <div className={`flex items-center space-x-1 ${color}`}>
        {icon}
        <span>{Math.abs(change).toFixed(2)}%</span>
      </div>
    );
  };

  if (showChart && selectedPair) {
    return (
      <div className="h-full">
        <AdvancedChart 
          symbol={selectedPair.symbol}
          onBack={() => setShowChart(false)}
        />
      </div>
    );
  }

  return (
    <div className="space-y-6 h-full">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center space-y-4 sm:space-y-0">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg">
            <BarChart3 className="h-5 w-5 text-white" />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-white">Futures Markets</h1>
            <p className="text-gray-400">USDT Perpetual Contracts • Binance</p>
          </div>
        </div>
        
        <div className="flex items-center space-x-3">
          <button
            onClick={() => fetchFuturesPairs(true)}
            disabled={loading}
            className="flex items-center space-x-2 px-4 py-2 bg-gray-700/50 hover:bg-gray-600/50 rounded-lg transition-all text-gray-300 hover:text-white disabled:opacity-50"
          >
            <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {/* Search and Filter Controls */}
      <div className="flex flex-col sm:flex-row space-y-4 sm:space-y-0 sm:space-x-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search pairs (e.g., BTC, ETH, SOL...)"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 bg-gray-800/50 border border-gray-700/50 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500/50 focus:ring-1 focus:ring-blue-500/20"
          />
        </div>
        
        <div className="flex items-center space-x-2">
          <Filter className="h-4 w-4 text-gray-400" />
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as 'volume' | 'price' | 'change')}
            className="px-3 py-2 bg-gray-800/50 border border-gray-700/50 rounded-lg text-white focus:outline-none focus:border-blue-500/50"
          >
            <option value="volume">Volume</option>
            <option value="price">Price</option>
            <option value="change">Change %</option>
          </select>
        </div>
      </div>

      {/* Market Overview Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-gray-800/30 backdrop-blur-sm p-4 rounded-xl border border-gray-700/30">
          <div className="flex items-center justify-between mb-2">
            <span className="text-gray-400 text-xs uppercase tracking-wide">Total Pairs</span>
            <BarChart3 className="h-4 w-4 text-blue-400" />
          </div>
          <div className="text-white font-bold text-xl">{pairs.length}</div>
        </div>
        
        <div className="bg-gray-800/30 backdrop-blur-sm p-4 rounded-xl border border-gray-700/30">
          <div className="flex items-center justify-between mb-2">
            <span className="text-gray-400 text-xs uppercase tracking-wide">24h Volume</span>
            <DollarSign className="h-4 w-4 text-green-400" />
          </div>
          <div className="text-white font-bold text-xl">
            ${formatVolume(pairs.reduce((sum, pair) => sum + pair.quoteVolume24h, 0))}
          </div>
        </div>
        
        <div className="bg-gray-800/30 backdrop-blur-sm p-4 rounded-xl border border-gray-700/30">
          <div className="flex items-center justify-between mb-2">
            <span className="text-gray-400 text-xs uppercase tracking-wide">Gainers</span>
            <TrendingUp className="h-4 w-4 text-green-400" />
          </div>
          <div className="text-green-400 font-bold text-xl">
            {pairs.filter(p => p.change24h > 0).length}
          </div>
        </div>
        
        <div className="bg-gray-800/30 backdrop-blur-sm p-4 rounded-xl border border-gray-700/30">
          <div className="flex items-center justify-between mb-2">
            <span className="text-gray-400 text-xs uppercase tracking-wide">Losers</span>
            <Activity className="h-4 w-4 text-red-400" />
          </div>
          <div className="text-red-400 font-bold text-xl">
            {pairs.filter(p => p.change24h < 0).length}
          </div>
        </div>
      </div>

      {/* Pairs Table */}
      <div className="bg-gray-800/30 backdrop-blur-sm rounded-xl border border-gray-700/50 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="bg-gray-900/50 border-b border-gray-700/50">
                <th className="text-left px-6 py-4 text-gray-300 font-medium">Pair</th>
                <th className="text-right px-6 py-4 text-gray-300 font-medium">Price</th>
                <th className="text-right px-6 py-4 text-gray-300 font-medium">24h Change</th>
                <th className="text-right px-6 py-4 text-gray-300 font-medium hidden md:table-cell">24h High</th>
                <th className="text-right px-6 py-4 text-gray-300 font-medium hidden md:table-cell">24h Low</th>
                <th className="text-right px-6 py-4 text-gray-300 font-medium">Volume (USDT)</th>
                <th className="text-right px-6 py-4 text-gray-300 font-medium">Action</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan={7} className="text-center py-12">
                    <div className="flex items-center justify-center space-x-2">
                      <Loader className="h-5 w-5 animate-spin text-blue-400" />
                      <span className="text-gray-400">Loading futures pairs...</span>
                    </div>
                  </td>
                </tr>
              ) : filteredPairs.length === 0 ? (
                <tr>
                  <td colSpan={7} className="text-center py-12 text-gray-400">
                    No pairs found matching your search
                  </td>
                </tr>
              ) : (
                filteredPairs.slice(0, 50).map((pair) => (
                  <tr
                    key={pair.symbol}
                    className="border-b border-gray-700/30 hover:bg-gray-700/20 transition-colors cursor-pointer"
                    onClick={() => handlePairClick(pair)}
                  >
                    <td className="px-6 py-4">
                      <div className="flex items-center space-x-3">
                        <div className="flex flex-col">
                          <span className="text-white font-medium">{pair.symbol}</span>
                          <span className="text-gray-400 text-xs">{pair.baseAsset}/USDT</span>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <span className="text-white font-mono">${formatPrice(pair.price)}</span>
                    </td>
                    <td className="px-6 py-4 text-right">
                      {formatChange(pair.change24h)}
                    </td>
                    <td className="px-6 py-4 text-right hidden md:table-cell">
                      <span className="text-gray-300 font-mono">${formatPrice(pair.high24h)}</span>
                    </td>
                    <td className="px-6 py-4 text-right hidden md:table-cell">
                      <span className="text-gray-300 font-mono">${formatPrice(pair.low24h)}</span>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <span className="text-gray-300 font-mono">${formatVolume(pair.quoteVolume24h)}</span>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handlePairClick(pair);
                        }}
                        className="px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white text-sm rounded transition-colors"
                      >
                        Chart
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {filteredPairs.length > 50 && (
        <div className="text-center text-gray-400 text-sm">
          Showing top 50 results. Use search to find specific pairs.
        </div>
      )}
    </div>
  );
};

export default FuturesMarketView;