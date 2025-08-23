import React, { useState, useRef } from 'react';
import { ZoomIn, ZoomOut, RotateCcw, TrendingUp } from 'lucide-react';
import { ParsedOHLCData } from '../types';

interface SimpleChartProps {
  data: ParsedOHLCData[];
  height?: number;
}

const SimpleChart: React.FC<SimpleChartProps> = ({ data, height = 600 }) => {
  const [zoom, setZoom] = useState(1);
  const [showLine, setShowLine] = useState(true);
  const [showCandles, setShowCandles] = useState(true);
  const svgRef = useRef<SVGSVGElement>(null);
  if (!data.length) {
    return (
      <div className="w-full bg-gray-800 rounded-lg p-4 flex items-center justify-center" style={{ height }}>
        <div className="text-gray-400">No data to display</div>
      </div>
    );
  }

  // Find min and max values for scaling
  const allPrices = data.flatMap(d => [d.open, d.high, d.low, d.close]);
  const minPrice = Math.min(...allPrices);
  const maxPrice = Math.max(...allPrices);
  const priceRange = maxPrice - minPrice;
  const padding = priceRange * 0.1;
  const chartMin = minPrice - padding;
  const chartMax = maxPrice + padding;
  const chartRange = chartMax - chartMin;

  const chartWidth = 800 * zoom;
  const chartHeight = height - 120; // Leave space for controls and labels

  // Create SVG path for close prices (simple line)
  const pathData = data.map((d, index) => {
    const x = (index / (data.length - 1)) * chartWidth;
    const y = chartHeight - ((d.close - chartMin) / chartRange) * chartHeight;
    return index === 0 ? `M ${x} ${y}` : `L ${x} ${y}`;
  }).join(' ');

  // Create candlesticks
  const candlesticks = data.map((d, index) => {
    const x = (index / (data.length - 1)) * chartWidth;
    const openY = chartHeight - ((d.open - chartMin) / chartRange) * chartHeight;
    const closeY = chartHeight - ((d.close - chartMin) / chartRange) * chartHeight;
    const highY = chartHeight - ((d.high - chartMin) / chartRange) * chartHeight;
    const lowY = chartHeight - ((d.low - chartMin) / chartRange) * chartHeight;
    
    const isGreen = d.close > d.open;
    const bodyTop = Math.min(openY, closeY);
    const bodyHeight = Math.abs(closeY - openY);

    return (
      <g key={index}>
        {/* Wick */}
        <line
          x1={x}
          y1={highY}
          x2={x}
          y2={lowY}
          stroke={isGreen ? '#22c55e' : '#ef4444'}
          strokeWidth="1"
        />
        {/* Body */}
        <rect
          x={x - 2}
          y={bodyTop}
          width="4"
          height={bodyHeight || 1}
          fill={isGreen ? '#22c55e' : '#ef4444'}
        />
      </g>
    );
  });

  // Create price labels
  const priceLabels = [];
  for (let i = 0; i <= 5; i++) {
    const price = chartMin + (chartRange * i / 5);
    const y = chartHeight - (i / 5) * chartHeight;
    priceLabels.push(
      <text
        key={i}
        x={chartWidth + 10}
        y={y + 4}
        className="text-xs fill-gray-400"
      >
        ${price.toFixed(2)}
      </text>
    );
  }

  return (
    <div className="w-full bg-gray-800 rounded-lg p-4">
      {/* Header with title and controls */}
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-white text-lg flex items-center gap-2">
          <TrendingUp className="h-5 w-5" />
          OHLC Chart ({data.length.toLocaleString()} records)
        </h3>
        
        {/* Chart Controls */}
        <div className="flex gap-2">
          <div className="flex gap-1">
            <button
              onClick={() => setShowCandles(!showCandles)}
              className={`px-3 py-1 text-xs rounded ${
                showCandles ? 'bg-blue-600 text-white' : 'bg-gray-700 text-gray-300'
              }`}
            >
              Candles
            </button>
            <button
              onClick={() => setShowLine(!showLine)}
              className={`px-3 py-1 text-xs rounded ${
                showLine ? 'bg-blue-600 text-white' : 'bg-gray-700 text-gray-300'
              }`}
            >
              Line
            </button>
          </div>
          
          <div className="flex gap-1">
            <button
              onClick={() => setZoom(Math.max(0.5, zoom - 0.25))}
              className="p-1 bg-gray-700 hover:bg-gray-600 rounded"
              disabled={zoom <= 0.5}
            >
              <ZoomOut className="h-4 w-4 text-gray-300" />
            </button>
            <button
              onClick={() => setZoom(Math.min(3, zoom + 0.25))}
              className="p-1 bg-gray-700 hover:bg-gray-600 rounded"
              disabled={zoom >= 3}
            >
              <ZoomIn className="h-4 w-4 text-gray-300" />
            </button>
            <button
              onClick={() => setZoom(1)}
              className="p-1 bg-gray-700 hover:bg-gray-600 rounded"
            >
              <RotateCcw className="h-4 w-4 text-gray-300" />
            </button>
          </div>
        </div>
      </div>
      
      {/* Chart Container */}
      <div className="overflow-x-auto border border-gray-600 rounded-lg bg-gray-900">
        <svg 
          ref={svgRef}
          width={chartWidth + 80} 
          height={chartHeight + 60} 
          className="bg-gray-900"
        >
          <defs>
            <linearGradient id="priceGradient" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="#3b82f6" stopOpacity="0.3" />
              <stop offset="100%" stopColor="#3b82f6" stopOpacity="0.1" />
            </linearGradient>
          </defs>
          
          {/* Background grid */}
          {[0, 1, 2, 3, 4, 5].map(i => (
            <g key={`grid-${i}`}>
              <line
                x1={0}
                y1={chartHeight - (i / 5) * chartHeight}
                x2={chartWidth}
                y2={chartHeight - (i / 5) * chartHeight}
                stroke="#374151"
                strokeWidth="1"
                opacity="0.2"
              />
            </g>
          ))}
          
          {/* Vertical grid lines */}
          {[0, 0.25, 0.5, 0.75, 1].map(ratio => (
            <line
              key={`vgrid-${ratio}`}
              x1={ratio * chartWidth}
              y1={0}
              x2={ratio * chartWidth}
              y2={chartHeight}
              stroke="#374151"
              strokeWidth="1"
              opacity="0.1"
            />
          ))}
          
          {/* Candlesticks */}
          {showCandles && candlesticks}
          
          {/* Close price line with area fill */}
          {showLine && (
            <g>
              <path
                d={`${pathData} L ${chartWidth} ${chartHeight} L 0 ${chartHeight} Z`}
                fill="url(#priceGradient)"
              />
              <path
                d={pathData}
                stroke="#3b82f6"
                strokeWidth="2"
                fill="none"
                opacity="0.8"
              />
            </g>
          )}
          
          {/* Price labels */}
          {priceLabels}
          
          {/* Date labels */}
          <text x={20} y={chartHeight + 25} className="text-xs fill-gray-400">
            {new Date(data[0]?.time * 1000).toLocaleDateString()}
          </text>
          <text x={chartWidth - 100} y={chartHeight + 25} className="text-xs fill-gray-400">
            {new Date(data[data.length - 1]?.time * 1000).toLocaleDateString()}
          </text>
          
          {/* Zoom indicator */}
          <text x={chartWidth / 2 - 30} y={chartHeight + 45} className="text-xs fill-gray-500">
            Zoom: {zoom}x
          </text>
        </svg>
      </div>
      
      {/* Statistics Panel */}
      <div className="mt-4 grid grid-cols-2 md:grid-cols-4 gap-4 text-sm bg-gray-900 p-4 rounded-lg">
        <div className="text-center">
          <div className="text-gray-400 text-xs">Latest Close</div>
          <div className="text-white font-semibold text-lg">
            ${data[data.length - 1]?.close.toFixed(2)}
          </div>
        </div>
        <div className="text-center">
          <div className="text-gray-400 text-xs">High</div>
          <div className="text-green-400 font-semibold text-lg">
            ${maxPrice.toFixed(2)}
          </div>
        </div>
        <div className="text-center">
          <div className="text-gray-400 text-xs">Low</div>
          <div className="text-red-400 font-semibold text-lg">
            ${minPrice.toFixed(2)}
          </div>
        </div>
        <div className="text-center">
          <div className="text-gray-400 text-xs">Range</div>
          <div className="text-blue-400 font-semibold text-lg">
            ${priceRange.toFixed(2)}
          </div>
        </div>
      </div>
    </div>
  );
};

export default SimpleChart;