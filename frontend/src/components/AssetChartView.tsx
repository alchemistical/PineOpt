import React, { useState, useEffect } from 'react';
import { ArrowLeft, Calendar, RefreshCw, Download, TrendingUp, BarChart3, Maximize2 } from 'lucide-react';
import LightweightChart from './LightweightChart';
import { ParsedOHLCData } from '../types';

interface AssetChartViewProps {
  symbol: string;
  startDate: string;
  endDate: string;
  onBack: () => void;
}

const AssetChartView: React.FC<AssetChartViewProps> = ({ symbol, startDate, endDate, onBack }) => {
  const [chartData, setChartData] = useState<ParsedOHLCData[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string>('');
  const [timeframe, setTimeframe] = useState('1d');
  const [dataStats, setDataStats] = useState({
    totalRecords: 0,
    priceRange: { min: 0, max: 0 },
    latestPrice: 0,
    change: 0,
    changePercent: 0
  });

  useEffect(() => {
    fetchChartData();
  }, [symbol, startDate, endDate, timeframe]);

  const fetchChartData = async () => {
    setIsLoading(true);
    setError('');

    try {
      // Calculate limit based on date range and timeframe
      const start = new Date(startDate);
      const end = new Date(endDate);
      const diffDays = Math.ceil((end.getTime() - start.getTime()) / (1000 * 60 * 60 * 24));
      
      let limit: number;
      let interval: string = timeframe;
      
      switch (timeframe) {
        case '1h': limit = Math.min(diffDays * 24, 1500); break;
        case '4h': limit = Math.min(diffDays * 6, 1500); break;
        case '1d': limit = Math.min(diffDays, 1500); break;
        case '1w': limit = Math.min(Math.ceil(diffDays / 7), 500); break;
        default: limit = Math.min(diffDays, 1500);
      }

      // Use the futures API for historical data
      const response = await fetch(`/api/futures/klines/${symbol}?interval=${interval}&limit=${limit}&start_time=${startDate}&end_time=${endDate}`);
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to fetch chart data');
      }

      if (!data.success || !data.data || data.data.length === 0) {
        throw new Error('No data available for the selected parameters');
      }

      // Convert to chart data format and filter by date range
      const chartData: ParsedOHLCData[] = data.data
        .map((item: any) => ({
          time: Math.floor(item.time / 1000), // Convert milliseconds to seconds for LightweightChart
          open: parseFloat(item.open),
          high: parseFloat(item.high),
          low: parseFloat(item.low),
          close: parseFloat(item.close),
          volume: parseFloat(item.volume || '0')
        }))
        .filter((item: ParsedOHLCData) => {
          const itemDate = new Date(item.time * 1000);
          return itemDate >= start && itemDate <= end;
        });

      if (chartData.length === 0) {
        throw new Error('No data available for the selected date range');
      }

      setChartData(chartData);

      // Calculate statistics
      const prices = chartData.flatMap(item => [item.open, item.high, item.low, item.close]);
      const minPrice = Math.min(...prices);
      const maxPrice = Math.max(...prices);
      const latestPrice = chartData[chartData.length - 1]?.close || 0;
      const firstPrice = chartData[0]?.open || 0;
      const change = latestPrice - firstPrice;
      const changePercent = firstPrice > 0 ? (change / firstPrice) * 100 : 0;

      setDataStats({
        totalRecords: chartData.length,
        priceRange: { min: minPrice, max: maxPrice },
        latestPrice,
        change,
        changePercent
      });

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch chart data');
    } finally {
      setIsLoading(false);
    }
  };

  const timeframes = [
    { value: '1h', label: '1H' },
    { value: '4h', label: '4H' },
    { value: '1d', label: '1D' },
    { value: '1w', label: '1W' }
  ];

  const formatPrice = (price: number) => {
    if (price < 1) return `$${price.toFixed(6)}`;
    if (price < 100) return `$${price.toFixed(4)}`;
    return `$${price.toLocaleString(undefined, { maximumFractionDigits: 2 })}`;
  };

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-4 lg:space-y-0">
        <div className="flex items-center space-x-4">
          <button
            onClick={onBack}
            className="flex items-center space-x-2 px-3 py-2 bg-gray-700/50 hover:bg-gray-600/50 text-gray-300 rounded-lg transition-colors"
          >
            <ArrowLeft className="h-4 w-4" />
            <span>Back to Screener</span>
          </button>
          
          <div>
            <h1 className="text-3xl font-bold text-white flex items-center">
              <BarChart3 className="h-8 w-8 mr-3 text-blue-400" />
              {symbol}
            </h1>
            <p className="text-gray-400">
              {formatDate(startDate)} - {formatDate(endDate)}
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={fetchChartData}
            disabled={isLoading}
            className="flex items-center space-x-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {/* Stats Bar */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        <div className="bg-gray-800/30 backdrop-blur-sm p-4 rounded-lg border border-gray-700/50">
          <div className="text-sm text-gray-400 mb-1">Latest Price</div>
          <div className="text-xl font-bold text-white">
            {formatPrice(dataStats.latestPrice)}
          </div>
        </div>
        
        <div className="bg-gray-800/30 backdrop-blur-sm p-4 rounded-lg border border-gray-700/50">
          <div className="text-sm text-gray-400 mb-1">Period Change</div>
          <div className={`text-xl font-bold ${dataStats.change >= 0 ? 'text-green-400' : 'text-red-400'}`}>
            {dataStats.change >= 0 ? '+' : ''}{formatPrice(Math.abs(dataStats.change))}
          </div>
          <div className={`text-xs ${dataStats.changePercent >= 0 ? 'text-green-400' : 'text-red-400'}`}>
            {dataStats.changePercent >= 0 ? '+' : ''}{dataStats.changePercent.toFixed(2)}%
          </div>
        </div>
        
        <div className="bg-gray-800/30 backdrop-blur-sm p-4 rounded-lg border border-gray-700/50">
          <div className="text-sm text-gray-400 mb-1">Period High</div>
          <div className="text-xl font-bold text-green-400">
            {formatPrice(dataStats.priceRange.max)}
          </div>
        </div>
        
        <div className="bg-gray-800/30 backdrop-blur-sm p-4 rounded-lg border border-gray-700/50">
          <div className="text-sm text-gray-400 mb-1">Period Low</div>
          <div className="text-xl font-bold text-red-400">
            {formatPrice(dataStats.priceRange.min)}
          </div>
        </div>
        
        <div className="bg-gray-800/30 backdrop-blur-sm p-4 rounded-lg border border-gray-700/50">
          <div className="text-sm text-gray-400 mb-1">Data Points</div>
          <div className="text-xl font-bold text-blue-400">
            {dataStats.totalRecords.toLocaleString()}
          </div>
        </div>
      </div>

      {/* Controls */}
      <div className="bg-gray-800/30 backdrop-blur-sm rounded-xl p-4 border border-gray-700/50">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center space-x-2">
            <span className="text-sm text-gray-300">Timeframe:</span>
            <div className="flex bg-gray-700/50 rounded-lg p-1">
              {timeframes.map(tf => (
                <button
                  key={tf.value}
                  onClick={() => setTimeframe(tf.value)}
                  className={`px-3 py-1.5 text-sm rounded transition-all ${
                    timeframe === tf.value
                      ? 'bg-blue-600 text-white shadow-lg'
                      : 'text-gray-400 hover:text-white hover:bg-gray-600/50'
                  }`}
                >
                  {tf.label}
                </button>
              ))}
            </div>
          </div>

          <div className="flex items-center space-x-2 text-sm text-gray-400">
            <Calendar className="h-4 w-4" />
            <span>
              {Math.round((new Date(endDate).getTime() - new Date(startDate).getTime()) / (1000 * 60 * 60 * 24))} days
            </span>
          </div>
        </div>
      </div>

      {/* Chart */}
      {error ? (
        <div className="bg-gray-800/30 backdrop-blur-sm rounded-xl p-12 border border-red-500/30 text-center">
          <div className="text-red-400 mb-2">⚠️ Chart Error</div>
          <div className="text-gray-300">{error}</div>
          <button
            onClick={fetchChartData}
            className="mt-4 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
          >
            Try Again
          </button>
        </div>
      ) : (
        <div className="bg-gray-800/30 backdrop-blur-sm rounded-xl border border-gray-700/50 overflow-hidden">
          {isLoading && (
            <div className="p-6 text-center">
              <div className="flex items-center justify-center space-x-2 text-gray-400">
                <RefreshCw className="h-5 w-5 animate-spin" />
                <span>Loading chart data...</span>
              </div>
            </div>
          )}
          
          {!isLoading && chartData.length > 0 && (
            <LightweightChart data={chartData} height={700} />
          )}
          
          {!isLoading && chartData.length === 0 && !error && (
            <div className="p-12 text-center text-gray-400">
              No chart data available
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default AssetChartView;