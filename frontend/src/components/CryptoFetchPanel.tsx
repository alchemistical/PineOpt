import React, { useState, useEffect } from 'react';
import { TrendingUp, Download, RefreshCw, Globe, AlertCircle, CheckCircle, Clock } from 'lucide-react';
import { ParsedOHLCData } from '../types';

interface CryptoFetchPanelProps {
  onDataFetched: (data: ParsedOHLCData[], metadata: any) => void;
}

interface CryptoProviderStatus {
  available: boolean;
  authenticated: boolean;
  message: string;
  provider?: string;
}

const CryptoFetchPanel: React.FC<CryptoFetchPanelProps> = ({ onDataFetched }) => {
  const [symbol, setSymbol] = useState('BTCUSDT');
  const [exchange, setExchange] = useState('BINANCE');
  const [timeframe, setTimeframe] = useState('1h');
  const [nBars, setNBars] = useState(1000);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string>('');
  const [success, setSuccess] = useState<string>('');
  const [status, setStatus] = useState<CryptoProviderStatus | null>(null);
  const [exchanges, setExchanges] = useState<string[]>([]);
  const [symbols, setSymbols] = useState<string[]>([]);

  // Check crypto provider status on mount
  useEffect(() => {
    checkCryptoStatus();
    loadExchanges();
  }, []);

  // Load popular symbols when exchange changes
  useEffect(() => {
    if (exchange) {
      loadSymbols(exchange);
    }
  }, [exchange]);

  const checkCryptoStatus = async () => {
    try {
      // Try new database health check first
      const response = await fetch('/api/db/health');
      if (response.ok) {
        const data = await response.json();
        if (data.success && data.status === 'healthy') {
          setStatus({
            available: true,
            authenticated: true,
            message: 'Database-powered crypto data ready',
            provider: 'PineOpt Database'
          });
          return;
        }
      }
      
      // Fallback to original crypto status
      const fallbackResponse = await fetch('/api/crypto/status');
      const fallbackData = await fallbackResponse.json();
      setStatus(fallbackData);
    } catch (err) {
      console.error('Failed to check crypto provider status:', err);
    }
  };

  const loadExchanges = async () => {
    try {
      const response = await fetch('/api/crypto/exchanges');
      if (response.ok) {
        const data = await response.json();
        setExchanges(data.exchanges || []);
      }
    } catch (err) {
      console.error('Failed to load crypto exchanges:', err);
    }
  };

  const loadSymbols = async (selectedExchange: string) => {
    try {
      const response = await fetch(`/api/crypto/symbols?exchange=${selectedExchange}`);
      if (response.ok) {
        const data = await response.json();
        setSymbols(data.symbols || []);
      }
    } catch (err) {
      console.error('Failed to load crypto symbols:', err);
    }
  };

  const fetchData = async () => {
    if (!symbol || !exchange) {
      setError('Please select both symbol and exchange');
      return;
    }

    setIsLoading(true);
    setError('');
    setSuccess('');

    try {
      const params = new URLSearchParams({
        symbol,
        exchange,
        timeframe,
        n_bars: nBars.toString()
      });

      const response = await fetch(`/api/crypto/ohlc?${params}`);
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to fetch data');
      }

      if (data.count === 0) {
        setError('No data available for the selected parameters');
        return;
      }

      // Convert to chart data format
      const chartData: ParsedOHLCData[] = data.ohlc.map((item: any) => ({
        time: new Date(item.time).getTime() / 1000, // Convert to Unix timestamp
        open: item.open,
        high: item.high,
        low: item.low,
        close: item.close,
        volume: item.volume
      }));

      onDataFetched(chartData, {
        symbol: data.symbol,
        exchange: data.exchange,
        timeframe: data.timeframe,
        count: data.count
      });

      setSuccess(`Successfully fetched ${data.count} bars for ${data.symbol} from ${data.exchange}`);

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch data');
    } finally {
      setIsLoading(false);
    }
  };

  const timeframes = [
    { value: '1m', label: '1 Minute' },
    { value: '5m', label: '5 Minutes' },
    { value: '15m', label: '15 Minutes' },
    { value: '30m', label: '30 Minutes' },
    { value: '1h', label: '1 Hour' },
    { value: '4h', label: '4 Hours' },
    { value: '1d', label: '1 Day' },
    { value: '1w', label: '1 Week' }
  ];

  if (!status) {
    return (
      <div className="bg-gray-800/30 backdrop-blur-sm rounded-xl p-6 border border-gray-700/50">
        <div className="animate-pulse flex items-center space-x-2">
          <RefreshCw className="h-4 w-4 text-gray-400 animate-spin" />
          <span className="text-gray-400">Checking TradingView status...</span>
        </div>
      </div>
    );
  }

  if (!status.available) {
    return (
      <div className="bg-gray-800/30 backdrop-blur-sm rounded-xl p-6 border border-gray-700/50">
        <div className="text-center">
          <AlertCircle className="h-12 w-12 text-yellow-400 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-white mb-2">Crypto Data Provider Unavailable</h3>
          <p className="text-gray-400 text-sm mb-4">{status.message}</p>
          <div className="bg-yellow-900/50 border border-yellow-700/50 rounded-lg p-3">
            <p className="text-yellow-300 text-sm">
              No crypto data providers are currently available. Please check the server configuration.
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Status Bar */}
      <div className="flex items-center justify-between p-4 bg-gradient-to-r from-green-500/20 to-blue-500/20 rounded-lg border border-green-500/30">
        <div className="flex items-center space-x-3">
          <Globe className="h-5 w-5 text-green-400" />
          <div>
            <div className="text-green-400 font-medium text-sm">Crypto Data Provider Active</div>
            <div className="text-green-300 text-xs">{status.message}</div>
          </div>
        </div>
        {status.authenticated ? (
          <div className="flex items-center space-x-2 text-green-400">
            <CheckCircle className="h-4 w-4" />
            <span className="text-sm">Authenticated</span>
          </div>
        ) : (
          <div className="flex items-center space-x-2 text-yellow-400">
            <Clock className="h-4 w-4" />
            <span className="text-sm">Guest Access</span>
          </div>
        )}
      </div>

      {/* Fetch Form */}
      <div className="bg-gray-800/30 backdrop-blur-sm rounded-xl p-6 border border-gray-700/50">
        <h3 className="text-lg font-semibold text-white mb-4 flex items-center">
          <TrendingUp className="mr-2 h-5 w-5" />
          Fetch Live Crypto Data
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          {/* Exchange Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Exchange</label>
            <select
              value={exchange}
              onChange={(e) => setExchange(e.target.value)}
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-blue-500"
            >
              {exchanges.map(ex => (
                <option key={ex} value={ex}>{ex}</option>
              ))}
            </select>
          </div>

          {/* Symbol Selection/Input */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Symbol</label>
            <div className="flex space-x-2">
              <input
                type="text"
                value={symbol}
                onChange={(e) => setSymbol(e.target.value.toUpperCase())}
                className="flex-1 px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-blue-500"
                placeholder="Enter symbol"
              />
              <select
                value={symbol}
                onChange={(e) => setSymbol(e.target.value)}
                className="px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-blue-500"
              >
                <option value="">Popular...</option>
                {symbols.map(sym => (
                  <option key={sym} value={sym}>{sym}</option>
                ))}
              </select>
            </div>
          </div>

          {/* Timeframe */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Timeframe</label>
            <select
              value={timeframe}
              onChange={(e) => setTimeframe(e.target.value)}
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-blue-500"
            >
              {timeframes.map(tf => (
                <option key={tf.value} value={tf.value}>{tf.label}</option>
              ))}
            </select>
          </div>

          {/* Number of Bars */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Number of Bars</label>
            <select
              value={nBars}
              onChange={(e) => setNBars(Number(e.target.value))}
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-blue-500"
            >
              <option value={100}>100 bars</option>
              <option value={500}>500 bars</option>
              <option value={1000}>1,000 bars</option>
              <option value={2500}>2,500 bars</option>
              <option value={5000}>5,000 bars</option>
            </select>
          </div>
        </div>

        {/* Fetch Button */}
        <button
          onClick={fetchData}
          disabled={isLoading || !symbol || !exchange}
          className="w-full flex items-center justify-center space-x-2 px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {isLoading ? (
            <>
              <RefreshCw className="h-4 w-4 animate-spin" />
              <span>Fetching Data...</span>
            </>
          ) : (
            <>
              <Download className="h-4 w-4" />
              <span>Fetch Crypto Data</span>
            </>
          )}
        </button>

        {/* Status Messages */}
        {error && (
          <div className="mt-4 p-3 bg-red-900/50 border border-red-700/50 rounded-lg">
            <div className="flex items-center">
              <AlertCircle className="h-4 w-4 text-red-400 mr-2" />
              <span className="text-red-300 text-sm">{error}</span>
            </div>
          </div>
        )}

        {success && (
          <div className="mt-4 p-3 bg-green-900/50 border border-green-700/50 rounded-lg">
            <div className="flex items-center">
              <CheckCircle className="h-4 w-4 text-green-400 mr-2" />
              <span className="text-green-300 text-sm">{success}</span>
            </div>
          </div>
        )}
      </div>

      {/* Info Panel */}
      <div className="bg-gray-800/30 backdrop-blur-sm rounded-xl p-6 border border-gray-700/50">
        <h4 className="text-sm font-semibold text-white mb-3">Usage Notes</h4>
        <div className="space-y-2 text-sm text-gray-400">
          <div className="flex items-start space-x-2">
            <div className="w-1.5 h-1.5 bg-blue-400 rounded-full mt-1.5 flex-shrink-0"></div>
            <div>Live crypto data is fetched from Binance and cached locally for performance</div>
          </div>
          <div className="flex items-start space-x-2">
            <div className="w-1.5 h-1.5 bg-blue-400 rounded-full mt-1.5 flex-shrink-0"></div>
            <div>Binance public API provides free access with reasonable rate limits</div>
          </div>
          <div className="flex items-start space-x-2">
            <div className="w-1.5 h-1.5 bg-blue-400 rounded-full mt-1.5 flex-shrink-0"></div>
            <div>Fetched data can be used for backtesting and Pine Script conversion</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CryptoFetchPanel;