import React, { useEffect, useRef, useState, useCallback } from 'react';
import { createChart, IChartApi, CandlestickData, Time, ColorType, CandlestickSeries, HistogramSeries, ISeriesApi, LineStyle } from 'lightweight-charts';
import { 
  ArrowLeft, 
  TrendingUp, 
  Maximize2, 
  RotateCcw, 
  Activity, 
  Settings,
  Volume,
  Crosshair,
  Grid,
  Zap,
  RefreshCw
} from 'lucide-react';

interface AdvancedChartProps {
  symbol: string;
  onBack?: () => void;
}

interface ChartData {
  time: number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

interface TimeframeOption {
  value: string;
  label: string;
  seconds: number;
}

interface HistoryOption {
  value: number;
  label: string;
}

const AdvancedChart: React.FC<AdvancedChartProps> = ({ symbol, onBack }) => {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const candlestickSeriesRef = useRef<ISeriesApi<"Candlestick"> | null>(null);
  const volumeSeriesRef = useRef<ISeriesApi<"Histogram"> | null>(null);
  
  const [isLoading, setIsLoading] = useState(true);
  const [chartData, setChartData] = useState<ChartData[]>([]);
  const [selectedTimeframe, setSelectedTimeframe] = useState('1h');
  const [selectedHistory, setSelectedHistory] = useState(500);
  const [showVolume, setShowVolume] = useState(true);
  const [showGrid, setShowGrid] = useState(true);
  const [currentPrice, setCurrentPrice] = useState<number | null>(null);
  const [priceChange, setPriceChange] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);

  const timeframes: TimeframeOption[] = [
    { value: '1m', label: '1m', seconds: 60 },
    { value: '5m', label: '5m', seconds: 300 },
    { value: '15m', label: '15m', seconds: 900 },
    { value: '30m', label: '30m', seconds: 1800 },
    { value: '1h', label: '1h', seconds: 3600 },
    { value: '4h', label: '4h', seconds: 14400 },
    { value: '1d', label: '1D', seconds: 86400 },
  ];

  const historyOptions: HistoryOption[] = [
    { value: 100, label: '100' },
    { value: 250, label: '250' },
    { value: 500, label: '500' },
    { value: 1000, label: '1K' },
    { value: 1500, label: '1.5K' },
  ];

  const fetchChartData = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      console.log(`🔄 Fetching ${selectedHistory} ${selectedTimeframe} candles for ${symbol}`);
      
      const response = await fetch(
        `/api/futures/klines/${symbol}?interval=${selectedTimeframe}&limit=${selectedHistory}`
      );
      
      const data = await response.json();
      
      if (!response.ok || !data.success) {
        throw new Error(data.error || `HTTP ${response.status}: Failed to fetch data`);
      }
      
      if (!data.data || data.data.length === 0) {
        throw new Error('No chart data available for this symbol');
      }
      
      console.log(`✅ Received ${data.data.length} candles for ${symbol}`);
      setChartData(data.data);
      
      // Calculate price change
      if (data.data.length >= 2) {
        const latest = data.data[data.data.length - 1];
        const previous = data.data[data.data.length - 2];
        setCurrentPrice(latest.close);
        setPriceChange(((latest.close - previous.close) / previous.close) * 100);
      }
      
    } catch (err) {
      console.error('❌ Error fetching chart data:', err);
      setError(err instanceof Error ? err.message : 'Failed to load chart data');
    } finally {
      setIsLoading(false);
    }
  }, [symbol, selectedTimeframe, selectedHistory]);

  // Initialize and update chart
  useEffect(() => {
    if (!chartContainerRef.current || chartData.length === 0) return;

    // Create chart with TradingView-like styling
    const chart = createChart(chartContainerRef.current, {
      width: chartContainerRef.current.clientWidth,
      height: 600,
      layout: {
        background: { type: ColorType.Solid, color: '#0B1426' },
        textColor: '#D1D5DB',
        fontSize: 12,
        fontFamily: 'Roboto, Ubuntu, sans-serif',
      },
      grid: {
        vertLines: { 
          color: showGrid ? '#1F2937' : 'transparent',
          style: LineStyle.Solid,
        },
        horzLines: { 
          color: showGrid ? '#1F2937' : 'transparent',
          style: LineStyle.Solid,
        },
      },
      crosshair: {
        mode: 1, // Magnet mode
        vertLine: {
          width: 1,
          color: '#4B5563',
          style: LineStyle.Dashed,
        },
        horzLine: {
          width: 1,
          color: '#4B5563',
          style: LineStyle.Dashed,
        },
      },
      rightPriceScale: {
        borderColor: '#374151',
        textColor: '#9CA3AF',
        scaleMargins: {
          top: 0.1,
          bottom: showVolume ? 0.3 : 0.1,
        },
      },
      timeScale: {
        borderColor: '#374151',
        textColor: '#9CA3AF',
        timeVisible: true,
        secondsVisible: selectedTimeframe.includes('s') || selectedTimeframe.includes('m'),
      },
      handleScroll: {
        mouseWheel: true,
        pressedMouseMove: true,
      },
      handleScale: {
        axisPressedMouseMove: true,
        mouseWheel: true,
        pinch: true,
      },
    });

    // Add candlestick series
    const candlestickSeries = chart.addSeries(CandlestickSeries, {
      upColor: '#10B981',
      downColor: '#EF4444',
      borderDownColor: '#EF4444',
      borderUpColor: '#10B981',
      wickDownColor: '#EF4444',
      wickUpColor: '#10B981',
      priceFormat: {
        type: 'price',
        precision: symbol.includes('BTC') ? 2 : 4,
        minMove: symbol.includes('BTC') ? 0.01 : 0.0001,
      },
    });

    // Add volume series if enabled
    let volumeSeries = null;
    if (showVolume) {
      volumeSeries = chart.addSeries(HistogramSeries, {
        color: '#374151',
        priceFormat: {
          type: 'volume',
        },
        priceScaleId: 'volume',
      });
      
      chart.priceScale('volume').applyOptions({
        scaleMargins: {
          top: 0.8,
          bottom: 0,
        },
      });
    }

    // Convert and set data
    const candleData: CandlestickData<Time>[] = chartData.map(item => ({
      time: item.time as Time,
      open: item.open,
      high: item.high,
      low: item.low,
      close: item.close,
    }));

    const volumeData = chartData.map(item => ({
      time: item.time as Time,
      value: item.volume,
      color: item.close >= item.open ? '#10B981' : '#EF4444',
    }));

    candlestickSeries.setData(candleData);
    if (volumeSeries) {
      volumeSeries.setData(volumeData);
    }

    // Fit content
    chart.timeScale().fitContent();

    // Store references
    chartRef.current = chart;
    candlestickSeriesRef.current = candlestickSeries;
    volumeSeriesRef.current = volumeSeries;

    // Handle resize
    const handleResize = () => {
      if (chartContainerRef.current) {
        chart.applyOptions({
          width: chartContainerRef.current.clientWidth,
        });
      }
    };

    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      chart.remove();
      chartRef.current = null;
      candlestickSeriesRef.current = null;
      volumeSeriesRef.current = null;
    };
  }, [chartData, showVolume, showGrid, symbol, selectedTimeframe]);

  // Fetch data when parameters change
  useEffect(() => {
    fetchChartData();
  }, [fetchChartData]);

  const handleTimeframeChange = (timeframe: string) => {
    setSelectedTimeframe(timeframe);
  };

  const handleHistoryChange = (history: number) => {
    setSelectedHistory(history);
  };

  const formatPrice = (price: number | null) => {
    if (price === null) return '---';
    if (price >= 1000) return price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    if (price >= 1) return price.toFixed(4);
    return price.toFixed(8);
  };

  const formatChange = (change: number | null) => {
    if (change === null) return { text: '---', color: 'text-gray-400' };
    const color = change >= 0 ? 'text-green-400' : 'text-red-400';
    return { text: `${change >= 0 ? '+' : ''}${change.toFixed(2)}%`, color };
  };

  return (
    <div className="space-y-6 h-full">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <button
            onClick={onBack}
            className="p-2 bg-gray-700/50 hover:bg-gray-600/50 rounded-lg transition-all text-gray-400 hover:text-white"
          >
            <ArrowLeft className="h-5 w-5" />
          </button>
          
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg">
              <TrendingUp className="h-5 w-5 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white">{symbol}</h1>
              <div className="flex items-center space-x-4 text-sm">
                <span className="text-white font-mono">
                  ${formatPrice(currentPrice)}
                </span>
                <span className={formatChange(priceChange).color}>
                  {formatChange(priceChange).text}
                </span>
              </div>
            </div>
          </div>
        </div>

        <button
          onClick={() => fetchChartData()}
          disabled={isLoading}
          className="flex items-center space-x-2 px-4 py-2 bg-gray-700/50 hover:bg-gray-600/50 rounded-lg transition-all text-gray-300 hover:text-white disabled:opacity-50"
        >
          <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
          <span>Refresh</span>
        </button>
      </div>

      {/* Chart Controls */}
      <div className="flex flex-col lg:flex-row space-y-4 lg:space-y-0 lg:space-x-6">
        {/* Timeframe Selector */}
        <div className="flex items-center space-x-2">
          <span className="text-gray-400 text-sm font-medium">Timeframe:</span>
          <div className="flex bg-gray-800/50 rounded-lg p-1">
            {timeframes.map((tf) => (
              <button
                key={tf.value}
                onClick={() => handleTimeframeChange(tf.value)}
                className={`px-3 py-1.5 text-sm rounded transition-all ${
                  selectedTimeframe === tf.value
                    ? 'bg-blue-600 text-white shadow-lg'
                    : 'text-gray-400 hover:text-white hover:bg-gray-600/50'
                }`}
              >
                {tf.label}
              </button>
            ))}
          </div>
        </div>

        {/* History Selector */}
        <div className="flex items-center space-x-2">
          <span className="text-gray-400 text-sm font-medium">Candles:</span>
          <div className="flex bg-gray-800/50 rounded-lg p-1">
            {historyOptions.map((option) => (
              <button
                key={option.value}
                onClick={() => handleHistoryChange(option.value)}
                className={`px-3 py-1.5 text-sm rounded transition-all ${
                  selectedHistory === option.value
                    ? 'bg-blue-600 text-white shadow-lg'
                    : 'text-gray-400 hover:text-white hover:bg-gray-600/50'
                }`}
              >
                {option.label}
              </button>
            ))}
          </div>
        </div>

        {/* Chart Options */}
        <div className="flex items-center space-x-2">
          <button
            onClick={() => setShowVolume(!showVolume)}
            className={`p-2 rounded-lg transition-all ${
              showVolume
                ? 'bg-blue-600 text-white'
                : 'bg-gray-700/50 text-gray-400 hover:text-white hover:bg-gray-600/50'
            }`}
            title="Toggle Volume"
          >
            <Volume className="h-4 w-4" />
          </button>

          <button
            onClick={() => setShowGrid(!showGrid)}
            className={`p-2 rounded-lg transition-all ${
              showGrid
                ? 'bg-blue-600 text-white'
                : 'bg-gray-700/50 text-gray-400 hover:text-white hover:bg-gray-600/50'
            }`}
            title="Toggle Grid"
          >
            <Grid className="h-4 w-4" />
          </button>

          <button
            onClick={() => chartRef.current?.timeScale().fitContent()}
            className="p-2 bg-gray-700/50 hover:bg-gray-600/50 rounded-lg transition-all text-gray-400 hover:text-white"
            title="Fit to content"
          >
            <Maximize2 className="h-4 w-4" />
          </button>

          <button
            onClick={() => chartRef.current?.timeScale().resetTimeScale()}
            className="p-2 bg-gray-700/50 hover:bg-gray-600/50 rounded-lg transition-all text-gray-400 hover:text-white"
            title="Reset zoom"
          >
            <RotateCcw className="h-4 w-4" />
          </button>
        </div>
      </div>

      {/* Chart Container */}
      <div className="relative bg-[#0B1426] rounded-xl border border-gray-600/50 overflow-hidden shadow-2xl">
        {error ? (
          <div className="flex items-center justify-center h-[600px] text-center">
            <div className="space-y-4">
              <div className="p-4 bg-red-500/20 rounded-full">
                <Zap className="h-8 w-8 text-red-400 mx-auto" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-red-400 mb-2">Chart Error</h3>
                <p className="text-gray-400 text-sm max-w-md">{error}</p>
                <button
                  onClick={() => fetchChartData()}
                  className="mt-4 px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors"
                >
                  Retry
                </button>
              </div>
            </div>
          </div>
        ) : isLoading ? (
          <div className="flex items-center justify-center h-[600px] bg-gradient-to-br from-gray-900 to-gray-800">
            <div className="flex items-center space-x-3 text-gray-400">
              <Activity className="h-6 w-6 animate-pulse" />
              <span>Loading {symbol} chart...</span>
            </div>
          </div>
        ) : (
          <div ref={chartContainerRef} className="w-full h-[600px]" />
        )}
      </div>

      {/* Chart Stats */}
      {chartData.length > 0 && !isLoading && !error && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-gray-800/30 backdrop-blur-sm p-4 rounded-lg border border-gray-700/30">
            <div className="text-gray-400 text-xs uppercase tracking-wide mb-2">Open</div>
            <div className="text-white font-mono text-lg">
              ${formatPrice(chartData[0]?.open)}
            </div>
          </div>
          
          <div className="bg-gray-800/30 backdrop-blur-sm p-4 rounded-lg border border-gray-700/30">
            <div className="text-gray-400 text-xs uppercase tracking-wide mb-2">High</div>
            <div className="text-green-400 font-mono text-lg">
              ${formatPrice(Math.max(...chartData.map(d => d.high)))}
            </div>
          </div>
          
          <div className="bg-gray-800/30 backdrop-blur-sm p-4 rounded-lg border border-gray-700/30">
            <div className="text-gray-400 text-xs uppercase tracking-wide mb-2">Low</div>
            <div className="text-red-400 font-mono text-lg">
              ${formatPrice(Math.min(...chartData.map(d => d.low)))}
            </div>
          </div>
          
          <div className="bg-gray-800/30 backdrop-blur-sm p-4 rounded-lg border border-gray-700/30">
            <div className="text-gray-400 text-xs uppercase tracking-wide mb-2">Close</div>
            <div className="text-white font-mono text-lg">
              ${formatPrice(chartData[chartData.length - 1]?.close)}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdvancedChart;