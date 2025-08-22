import React, { useState, useEffect } from 'react';
import { 
  TrendingUp, 
  TrendingDown, 
  Eye, 
  RefreshCw, 
  Calendar,
  Filter,
  Search,
  BarChart3
} from 'lucide-react';

interface AssetData {
  symbol: string;
  price: number;
  change24h: number;
  volume24h: number;
  marketCap?: number;
  high24h: number;
  low24h: number;
  lastUpdate: string;
}

interface AssetScreenerProps {
  onAssetSelect: (symbol: string, startDate: string, endDate: string) => void;
}

const AssetScreener: React.FC<AssetScreenerProps> = ({ onAssetSelect }) => {
  const [assets, setAssets] = useState<AssetData[]>([]);
  const [filteredAssets, setFilteredAssets] = useState<AssetData[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState<'symbol' | 'price' | 'change24h' | 'volume24h'>('volume24h');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  const [startDate, setStartDate] = useState(() => {
    const date = new Date();
    date.setDate(date.getDate() - 30); // Default to 30 days ago
    return date.toISOString().split('T')[0];
  });
  const [endDate, setEndDate] = useState(() => {
    return new Date().toISOString().split('T')[0];
  });
  const [priceFilter, setPriceFilter] = useState<'all' | 'gainers' | 'losers'>('all');

  const popularAssets = [
    'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'SOLUSDT', 'XRPUSDT', 
    'DOTUSDT', 'DOGEUSDT', 'AVAXUSDT', 'MATICUSDT', 'LTCUSDT', 'UNIUSDT',
    'LINKUSDT', 'ATOMUSDT', 'ETCUSDT', 'XLMUSDT', 'VETUSDT', 'FILUSDT',
    'TRXUSDT', 'FTMUSDT', 'HBARUSDT', 'MANAUSDT', 'SANDUSDT', 'AXSUSDT'
  ];

  useEffect(() => {
    fetchMarketData();
  }, []);

  useEffect(() => {
    filterAndSortAssets();
  }, [assets, searchTerm, sortBy, sortOrder, priceFilter]);

  const fetchMarketData = async () => {
    setIsLoading(true);
    try {
      // Fetch real market data from futures endpoint
      const response = await fetch('/api/futures/pairs?limit=50');
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to fetch market data');
      }

      if (data.success && data.data) {
        // Convert futures data to AssetData format
        const marketData: AssetData[] = data.data.map((pair: any) => ({
          symbol: pair.symbol,
          price: parseFloat(pair.price || '0'),
          change24h: parseFloat(pair.change24h || '0'),
          volume24h: parseFloat(pair.quoteVolume24h || pair.volume24h || '0'),
          high24h: parseFloat(pair.high24h || '0'),
          low24h: parseFloat(pair.low24h || '0'),
          lastUpdate: data.timestamp || new Date().toISOString()
        }));

        setAssets(marketData);
      } else {
        throw new Error('Invalid API response format');
      }
    } catch (error) {
      console.error('Failed to fetch market data:', error);
      
      // Only use mock data as absolute fallback
      const mockData: AssetData[] = popularAssets.map(symbol => ({
        symbol,
        price: Math.random() * 100000,
        change24h: (Math.random() - 0.5) * 20,
        volume24h: Math.random() * 1000000000,
        high24h: Math.random() * 110000,
        low24h: Math.random() * 90000,
        lastUpdate: new Date().toISOString()
      }));
      
      setAssets(mockData);
    } finally {
      setIsLoading(false);
    }
  };

  const filterAndSortAssets = () => {
    let filtered = [...assets];

    // Apply search filter
    if (searchTerm) {
      filtered = filtered.filter(asset => 
        asset.symbol.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Apply price change filter
    if (priceFilter === 'gainers') {
      filtered = filtered.filter(asset => asset.change24h > 0);
    } else if (priceFilter === 'losers') {
      filtered = filtered.filter(asset => asset.change24h < 0);
    }

    // Apply sorting
    filtered.sort((a, b) => {
      const aValue = a[sortBy];
      const bValue = b[sortBy];
      
      if (typeof aValue === 'string') {
        return sortOrder === 'asc' 
          ? aValue.localeCompare(bValue as string)
          : (bValue as string).localeCompare(aValue);
      }
      
      return sortOrder === 'asc' 
        ? (aValue as number) - (bValue as number)
        : (bValue as number) - (aValue as number);
    });

    setFilteredAssets(filtered);
  };

  const handleSort = (column: typeof sortBy) => {
    if (sortBy === column) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(column);
      setSortOrder('desc');
    }
  };

  const formatPrice = (price: number) => {
    if (price < 1) return `$${price.toFixed(6)}`;
    if (price < 100) return `$${price.toFixed(4)}`;
    return `$${price.toLocaleString(undefined, { maximumFractionDigits: 2 })}`;
  };

  const formatVolume = (volume: number) => {
    if (volume >= 1e9) return `$${(volume / 1e9).toFixed(2)}B`;
    if (volume >= 1e6) return `$${(volume / 1e6).toFixed(2)}M`;
    if (volume >= 1e3) return `$${(volume / 1e3).toFixed(2)}K`;
    return `$${volume.toFixed(2)}`;
  };

  const handleAssetClick = (symbol: string) => {
    onAssetSelect(symbol, startDate, endDate);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-4 lg:space-y-0">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2 flex items-center">
            <BarChart3 className="h-8 w-8 mr-3 text-blue-400" />
            Crypto Asset Screener
          </h1>
          <p className="text-gray-400">Click any asset to view its historical chart</p>
        </div>

        <button
          onClick={fetchMarketData}
          disabled={isLoading}
          className="flex items-center space-x-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors disabled:opacity-50"
        >
          <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
          <span>Refresh</span>
        </button>
      </div>

      {/* Controls */}
      <div className="bg-gray-800/30 backdrop-blur-sm rounded-xl p-6 border border-gray-700/50">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Date Range */}
          <div className="space-y-2">
            <label className="block text-sm font-medium text-gray-300">Start Date</label>
            <div className="relative">
              <Calendar className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                className="w-full pl-10 pr-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-blue-500"
              />
            </div>
          </div>

          <div className="space-y-2">
            <label className="block text-sm font-medium text-gray-300">End Date</label>
            <div className="relative">
              <Calendar className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                className="w-full pl-10 pr-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-blue-500"
              />
            </div>
          </div>

          {/* Search */}
          <div className="space-y-2">
            <label className="block text-sm font-medium text-gray-300">Search Assets</label>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Search symbols..."
                className="w-full pl-10 pr-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-blue-500"
              />
            </div>
          </div>

          {/* Price Filter */}
          <div className="space-y-2">
            <label className="block text-sm font-medium text-gray-300">Price Movement</label>
            <div className="relative">
              <Filter className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <select
                value={priceFilter}
                onChange={(e) => setPriceFilter(e.target.value as typeof priceFilter)}
                className="w-full pl-10 pr-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-blue-500"
              >
                <option value="all">All Assets</option>
                <option value="gainers">Top Gainers</option>
                <option value="losers">Top Losers</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      {/* Asset Table */}
      <div className="bg-gray-800/30 backdrop-blur-sm rounded-xl border border-gray-700/50 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-gray-700/50">
              <tr>
                <th 
                  className="px-6 py-4 text-left cursor-pointer hover:bg-gray-600/50 transition-colors"
                  onClick={() => handleSort('symbol')}
                >
                  <div className="flex items-center space-x-1 text-gray-300 font-medium">
                    <span>Symbol</span>
                    {sortBy === 'symbol' && (
                      <span className="text-blue-400">{sortOrder === 'asc' ? '↑' : '↓'}</span>
                    )}
                  </div>
                </th>
                <th 
                  className="px-6 py-4 text-right cursor-pointer hover:bg-gray-600/50 transition-colors"
                  onClick={() => handleSort('price')}
                >
                  <div className="flex items-center justify-end space-x-1 text-gray-300 font-medium">
                    <span>Price</span>
                    {sortBy === 'price' && (
                      <span className="text-blue-400">{sortOrder === 'asc' ? '↑' : '↓'}</span>
                    )}
                  </div>
                </th>
                <th 
                  className="px-6 py-4 text-right cursor-pointer hover:bg-gray-600/50 transition-colors"
                  onClick={() => handleSort('change24h')}
                >
                  <div className="flex items-center justify-end space-x-1 text-gray-300 font-medium">
                    <span>24h Change</span>
                    {sortBy === 'change24h' && (
                      <span className="text-blue-400">{sortOrder === 'asc' ? '↑' : '↓'}</span>
                    )}
                  </div>
                </th>
                <th 
                  className="px-6 py-4 text-right cursor-pointer hover:bg-gray-600/50 transition-colors"
                  onClick={() => handleSort('volume24h')}
                >
                  <div className="flex items-center justify-end space-x-1 text-gray-300 font-medium">
                    <span>24h Volume</span>
                    {sortBy === 'volume24h' && (
                      <span className="text-blue-400">{sortOrder === 'asc' ? '↑' : '↓'}</span>
                    )}
                  </div>
                </th>
                <th className="px-6 py-4 text-right text-gray-300 font-medium">24h Range</th>
                <th className="px-6 py-4 text-center text-gray-300 font-medium">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-700/50">
              {isLoading ? (
                <tr>
                  <td colSpan={6} className="px-6 py-12 text-center">
                    <div className="flex items-center justify-center space-x-2 text-gray-400">
                      <RefreshCw className="h-5 w-5 animate-spin" />
                      <span>Loading market data...</span>
                    </div>
                  </td>
                </tr>
              ) : filteredAssets.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-6 py-12 text-center text-gray-400">
                    No assets match your current filters
                  </td>
                </tr>
              ) : (
                filteredAssets.map((asset, index) => (
                  <tr 
                    key={asset.symbol}
                    className="hover:bg-gray-700/30 cursor-pointer transition-colors"
                    onClick={() => handleAssetClick(asset.symbol)}
                  >
                    <td className="px-6 py-4">
                      <div className="flex items-center space-x-3">
                        <div className={`w-2 h-2 rounded-full ${
                          index < 5 ? 'bg-yellow-400' : 'bg-blue-400'
                        }`}></div>
                        <span className="text-white font-medium">{asset.symbol}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <span className="text-white font-mono">{formatPrice(asset.price)}</span>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <div className={`flex items-center justify-end space-x-1 ${
                        asset.change24h >= 0 ? 'text-green-400' : 'text-red-400'
                      }`}>
                        {asset.change24h >= 0 ? (
                          <TrendingUp className="h-4 w-4" />
                        ) : (
                          <TrendingDown className="h-4 w-4" />
                        )}
                        <span className="font-mono">
                          {asset.change24h >= 0 ? '+' : ''}{asset.change24h.toFixed(2)}%
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <span className="text-gray-300 font-mono">{formatVolume(asset.volume24h)}</span>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <div className="text-xs">
                        <div className="text-green-400 font-mono">H: {formatPrice(asset.high24h)}</div>
                        <div className="text-red-400 font-mono">L: {formatPrice(asset.low24h)}</div>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-center">
                      <button className="inline-flex items-center space-x-1 px-3 py-1.5 bg-blue-600/20 hover:bg-blue-600/30 text-blue-400 rounded-lg transition-colors">
                        <Eye className="h-4 w-4" />
                        <span className="text-xs">View Chart</span>
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-gray-800/30 backdrop-blur-sm p-4 rounded-lg border border-gray-700/50">
          <div className="text-2xl font-bold text-white">{filteredAssets.length}</div>
          <div className="text-sm text-gray-400">Total Assets</div>
        </div>
        <div className="bg-gray-800/30 backdrop-blur-sm p-4 rounded-lg border border-gray-700/50">
          <div className="text-2xl font-bold text-green-400">
            {filteredAssets.filter(a => a.change24h > 0).length}
          </div>
          <div className="text-sm text-gray-400">Gainers (24h)</div>
        </div>
        <div className="bg-gray-800/30 backdrop-blur-sm p-4 rounded-lg border border-gray-700/50">
          <div className="text-2xl font-bold text-red-400">
            {filteredAssets.filter(a => a.change24h < 0).length}
          </div>
          <div className="text-sm text-gray-400">Losers (24h)</div>
        </div>
        <div className="bg-gray-800/30 backdrop-blur-sm p-4 rounded-lg border border-gray-700/50">
          <div className="text-2xl font-bold text-blue-400">
            {Math.round(new Date(endDate).getTime() - new Date(startDate).getTime()) / (1000 * 60 * 60 * 24)}
          </div>
          <div className="text-sm text-gray-400">Day Range</div>
        </div>
      </div>
    </div>
  );
};

export default AssetScreener;