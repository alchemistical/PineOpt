import React, { useEffect, useRef, useState } from 'react';
import { createChart, IChartApi, CandlestickData, Time, ColorType, CandlestickSeries } from 'lightweight-charts';
import { TrendingUp, Maximize2, RotateCcw, Activity } from 'lucide-react';
import { ParsedOHLCData } from '../types';

interface LightweightChartProps {
  data: ParsedOHLCData[];
  height?: number;
}

const LightweightChart: React.FC<LightweightChartProps> = ({ data, height = 600 }) => {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const [isChartReady, setIsChartReady] = useState(false);
  const [chartStyle, setChartStyle] = useState<'candles' | 'area'>('candles');

  useEffect(() => {
    if (!chartContainerRef.current || !data.length) return;

    // Create chart
    const chart = createChart(chartContainerRef.current, {
      width: chartContainerRef.current.clientWidth,
      height: height - 120, // Leave space for controls
      layout: {
        background: { type: ColorType.Solid, color: '#111827' },
        textColor: '#9CA3AF',
      },
      grid: {
        vertLines: { color: '#374151' },
        horzLines: { color: '#374151' },
      },
      crosshair: {
        mode: 0, // Normal crosshair mode
      },
      rightPriceScale: {
        borderColor: '#4B5563',
      },
      timeScale: {
        borderColor: '#4B5563',
        timeVisible: true,
        secondsVisible: false,
      },
    });

    // Add candlestick series - correct API for lightweight-charts v5
    const candlestickSeries = chart.addSeries(CandlestickSeries, {
      upColor: '#22c55e',
      downColor: '#ef4444',
      borderDownColor: '#ef4444',
      borderUpColor: '#22c55e',
      wickDownColor: '#ef4444',
      wickUpColor: '#22c55e',
    });

    // Convert data format for lightweight-charts
    const chartData: CandlestickData<Time>[] = data.map(item => ({
      time: item.time as Time,
      open: item.open,
      high: item.high,
      low: item.low,
      close: item.close,
    }));

    // Set data
    candlestickSeries.setData(chartData);

    // Fit content
    chart.timeScale().fitContent();

    // Chart is ready
    setIsChartReady(true);

    // Store references
    chartRef.current = chart;

    // Handle resize
    const handleResize = () => {
      if (chartContainerRef.current) {
        chart.applyOptions({
          width: chartContainerRef.current.clientWidth,
        });
      }
    };

    window.addEventListener('resize', handleResize);

    // Cleanup
    return () => {
      window.removeEventListener('resize', handleResize);
      chart.remove();
    };
  }, [data, height]);

  if (!data.length) {
    return (
      <div className="w-full bg-gradient-to-br from-gray-800 to-gray-900 rounded-xl p-6 border border-gray-700/50" style={{ height }}>
        <div className="flex flex-col items-center justify-center h-full text-center space-y-4">
          <div className="p-4 bg-gray-700/30 rounded-full">
            <TrendingUp className="h-8 w-8 text-gray-400" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-gray-300 mb-2">No Chart Data</h3>
            <p className="text-gray-500 text-sm">Upload OHLC data or fetch crypto data to visualize charts</p>
          </div>
        </div>
      </div>
    );
  }

  // Calculate statistics
  const allPrices = data.flatMap(d => [d.open, d.high, d.low, d.close]);
  const minPrice = Math.min(...allPrices);
  const maxPrice = Math.max(...allPrices);
  const priceRange = maxPrice - minPrice;
  const latestClose = data[data.length - 1]?.close;

  return (
    <div className="w-full bg-gradient-to-br from-gray-800 to-gray-900 rounded-xl p-6 border border-gray-700/50 shadow-2xl">
      {/* Responsive Header with Controls */}
      <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center space-y-4 sm:space-y-0 mb-6">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg">
            <TrendingUp className="h-5 w-5 text-white" />
          </div>
          <div>
            <h3 className="text-xl font-semibold text-white">
              OHLC Chart
            </h3>
            <p className="text-sm text-gray-400">
              {data.length.toLocaleString()} records • {isChartReady ? 'Live' : 'Loading...'}
            </p>
          </div>
        </div>
        
        {/* Responsive Chart Controls */}
        <div className="flex items-center justify-between sm:justify-end space-x-2">
          <div className="flex bg-gray-700/50 rounded-lg p-1">
            <button
              onClick={() => setChartStyle('candles')}
              className={`px-2 sm:px-3 py-1.5 text-xs rounded transition-all ${
                chartStyle === 'candles' 
                  ? 'bg-blue-600 text-white shadow-lg' 
                  : 'text-gray-400 hover:text-white hover:bg-gray-600/50'
              }`}
            >
              Candles
            </button>
            <button
              onClick={() => setChartStyle('area')}
              className={`px-2 sm:px-3 py-1.5 text-xs rounded transition-all ${
                chartStyle === 'area' 
                  ? 'bg-blue-600 text-white shadow-lg' 
                  : 'text-gray-400 hover:text-white hover:bg-gray-600/50'
              }`}
            >
              Area
            </button>
          </div>
          
          <div className="flex space-x-1 sm:space-x-2">
            <button
              onClick={() => chartRef.current?.timeScale().fitContent()}
              className="p-2 bg-gray-700/50 hover:bg-gray-600/50 rounded-lg transition-all text-gray-400 hover:text-white"
              title="Fit to content"
            >
              <Maximize2 className="h-3 w-3 sm:h-4 sm:w-4" />
            </button>
            
            <button
              onClick={() => chartRef.current?.timeScale().resetTimeScale()}
              className="p-2 bg-gray-700/50 hover:bg-gray-600/50 rounded-lg transition-all text-gray-400 hover:text-white"
              title="Reset zoom"
            >
              <RotateCcw className="h-3 w-3 sm:h-4 sm:w-4" />
            </button>
          </div>
        </div>
      </div>
      
      {/* Chart Container */}
      <div className="relative">
        {!isChartReady && (
          <div className="absolute inset-0 flex items-center justify-center bg-gray-900/80 rounded-lg backdrop-blur-sm z-10">
            <div className="flex items-center space-x-3 text-gray-400">
              <Activity className="h-5 w-5 animate-pulse" />
              <span className="text-sm">Loading chart...</span>
            </div>
          </div>
        )}
        <div className="border border-gray-600/50 rounded-lg bg-gray-900 overflow-hidden shadow-inner">
          <div ref={chartContainerRef} style={{ width: '100%', height: height - 160 }} />
        </div>
      </div>
      
      {/* Enhanced Statistics Panel */}
      <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-gray-800/50 backdrop-blur-sm p-4 rounded-lg border border-gray-700/30 hover:border-gray-600/50 transition-all">
          <div className="flex items-center justify-between mb-2">
            <span className="text-gray-400 text-xs uppercase tracking-wide">Latest Close</span>
            <div className="w-2 h-2 bg-blue-400 rounded-full animate-pulse"></div>
          </div>
          <div className="text-white font-bold text-xl">
            ${latestClose?.toFixed(2)}
          </div>
          <div className="text-xs text-gray-500 mt-1">Current price</div>
        </div>
        
        <div className="bg-gray-800/50 backdrop-blur-sm p-4 rounded-lg border border-gray-700/30 hover:border-green-600/30 transition-all">
          <div className="flex items-center justify-between mb-2">
            <span className="text-gray-400 text-xs uppercase tracking-wide">High</span>
            <div className="w-2 h-2 bg-green-400 rounded-full"></div>
          </div>
          <div className="text-green-400 font-bold text-xl">
            ${maxPrice.toFixed(2)}
          </div>
          <div className="text-xs text-gray-500 mt-1">Highest price</div>
        </div>
        
        <div className="bg-gray-800/50 backdrop-blur-sm p-4 rounded-lg border border-gray-700/30 hover:border-red-600/30 transition-all">
          <div className="flex items-center justify-between mb-2">
            <span className="text-gray-400 text-xs uppercase tracking-wide">Low</span>
            <div className="w-2 h-2 bg-red-400 rounded-full"></div>
          </div>
          <div className="text-red-400 font-bold text-xl">
            ${minPrice.toFixed(2)}
          </div>
          <div className="text-xs text-gray-500 mt-1">Lowest price</div>
        </div>
        
        <div className="bg-gray-800/50 backdrop-blur-sm p-4 rounded-lg border border-gray-700/30 hover:border-purple-600/30 transition-all">
          <div className="flex items-center justify-between mb-2">
            <span className="text-gray-400 text-xs uppercase tracking-wide">Range</span>
            <div className="w-2 h-2 bg-purple-400 rounded-full"></div>
          </div>
          <div className="text-purple-400 font-bold text-xl">
            ${priceRange.toFixed(2)}
          </div>
          <div className="text-xs text-gray-500 mt-1">Price spread</div>
        </div>
      </div>
    </div>
  );
};

export default LightweightChart;