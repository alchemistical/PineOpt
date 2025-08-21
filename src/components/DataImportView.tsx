import React, { useState } from 'react';
import { TrendingUp, Upload as UploadIcon, BarChart3, Download, Eye, Trash2, Globe, FileText } from 'lucide-react';
import FileUpload from './FileUpload';
import LightweightChart from './LightweightChart';
import CryptoFetchPanel from './CryptoFetchPanel';
import { parseCSV, parseExcel, convertToChartData } from '../utils/dataParser';
import { OHLCData, ParsedOHLCData } from '../types';

const DataImportView: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'upload' | 'tradingview'>('tradingview');
  const [chartData, setChartData] = useState<ParsedOHLCData[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string>('');
  const [fileName, setFileName] = useState<string>('');
  const [dataSource, setDataSource] = useState<'file' | 'tradingview'>('file');
  const [dataStats, setDataStats] = useState<{
    totalRecords: number;
    dateRange: { start: string; end: string } | null;
    priceRange: { min: number; max: number } | null;
  }>({
    totalRecords: 0,
    dateRange: null,
    priceRange: null,
  });

  const handleFileSelect = async (file: File) => {
    setIsLoading(true);
    setError('');
    setFileName(file.name);

    try {
      let rawData: OHLCData[];

      if (file.name.endsWith('.csv')) {
        rawData = await parseCSV(file);
      } else if (file.name.endsWith('.xlsx') || file.name.endsWith('.xls')) {
        rawData = await parseExcel(file);
      } else {
        throw new Error('Unsupported file format. Please use CSV or Excel files.');
      }

      if (rawData.length === 0) {
        throw new Error('No valid data found in the file.');
      }

      const processedData = convertToChartData(rawData);
      
      if (processedData.length === 0) {
        throw new Error('No valid OHLC records found. Please check your data format.');
      }

      setChartData(processedData);

      const prices = processedData.flatMap(item => [item.open, item.high, item.low, item.close]);
      const minPrice = Math.min(...prices);
      const maxPrice = Math.max(...prices);
      const startTime = new Date(processedData[0].time * 1000).toLocaleDateString();
      const endTime = new Date(processedData[processedData.length - 1].time * 1000).toLocaleDateString();

      setDataStats({
        totalRecords: processedData.length,
        dateRange: { start: startTime, end: endTime },
        priceRange: { min: minPrice, max: maxPrice },
      });

    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred while processing the file.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleTradingViewData = (data: ParsedOHLCData[], metadata: any) => {
    console.log('🔥 Data received in handleTradingViewData:', data);
    console.log('🔥 First 2 data points:', data.slice(0, 2));
    console.log('🔥 Metadata:', metadata);
    console.log('🔥 Data length:', data.length);
    
    setChartData(data);
    setDataSource('tradingview');
    setFileName(`${metadata.symbol} (${metadata.exchange}) - ${metadata.timeframe}`);
    
    if (data.length > 0) {
      const prices = data.flatMap(item => [item.open, item.high, item.low, item.close]);
      const minPrice = Math.min(...prices);
      const maxPrice = Math.max(...prices);
      const startTime = new Date(data[0].time * 1000).toLocaleDateString();
      const endTime = new Date(data[data.length - 1].time * 1000).toLocaleDateString();

      setDataStats({
        totalRecords: data.length,
        dateRange: { start: startTime, end: endTime },
        priceRange: { min: minPrice, max: maxPrice },
      });
      
      console.log('🔥 Chart data set successfully, length:', data.length);
    }
  };

  const clearData = () => {
    setChartData([]);
    setFileName('');
    setDataSource('file');
    setDataStats({ totalRecords: 0, dateRange: null, priceRange: null });
    setError('');
  };

  if (chartData.length === 0) {
    return (
      <div className="space-y-8">
        {/* Enhanced Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center p-4 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full mb-4">
            <TrendingUp className="h-8 w-8 text-white" />
          </div>
          <h1 className="text-4xl font-bold text-white mb-3 bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
            Live Charts & Data
          </h1>
          <p className="text-gray-400 text-lg max-w-2xl mx-auto">
            Visualize crypto market data with professional TradingView charts. Import files or fetch live data from exchanges.
          </p>
        </div>

        {/* Enhanced Responsive Tab Navigation */}
        <div className="flex justify-center mb-10">
          <div className="flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-2 bg-gray-800/30 backdrop-blur-sm rounded-xl p-2 border border-gray-700/50 w-full max-w-2xl">
            <button
              onClick={() => setActiveTab('tradingview')}
              className={`flex items-center justify-center sm:justify-start space-x-3 px-4 sm:px-6 py-3 rounded-lg text-sm font-medium transition-all duration-200 flex-1 ${
                activeTab === 'tradingview'
                  ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg'
                  : 'text-gray-400 hover:text-white hover:bg-gray-700/50'
              }`}
            >
              <Globe className="h-5 w-5 flex-shrink-0" />
              <div className="text-center sm:text-left">
                <div className="font-semibold">Live Crypto Data</div>
                <div className="text-xs opacity-75 hidden sm:block">Binance, TradingView</div>
              </div>
            </button>
            <button
              onClick={() => setActiveTab('upload')}
              className={`flex items-center justify-center sm:justify-start space-x-3 px-4 sm:px-6 py-3 rounded-lg text-sm font-medium transition-all duration-200 flex-1 ${
                activeTab === 'upload'
                  ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg'
                  : 'text-gray-400 hover:text-white hover:bg-gray-700/50'
              }`}
            >
              <FileText className="h-5 w-5 flex-shrink-0" />
              <div className="text-center sm:text-left">
                <div className="font-semibold">File Upload</div>
                <div className="text-xs opacity-75 hidden sm:block">CSV, Excel files</div>
              </div>
            </button>
          </div>
        </div>

        {/* Tab Content */}
        <div className="max-w-4xl mx-auto">
          {activeTab === 'tradingview' ? (
            <CryptoFetchPanel onDataFetched={handleTradingViewData} />
          ) : (
            <div className="bg-gradient-to-br from-gray-800/50 to-gray-900/50 backdrop-blur-sm rounded-2xl p-8 border border-gray-700/30 shadow-2xl">
              <div className="text-center mb-8">
                <div className="p-4 bg-gradient-to-r from-green-500/20 to-blue-500/20 rounded-2xl w-20 h-20 mx-auto mb-6 flex items-center justify-center border border-green-500/20">
                  <UploadIcon className="h-10 w-10 text-green-400" />
                </div>
                <h2 className="text-3xl font-bold text-white mb-3">
                  Import Trading Data
                </h2>
                <p className="text-gray-400 text-lg max-w-md mx-auto">
                  Upload CSV or Excel files containing OHLC data to create professional charts
                </p>
              </div>
              
              <FileUpload onFileSelect={handleFileSelect} isLoading={isLoading} />
              
              {error && (
                <div className="mt-6 p-6 bg-gradient-to-r from-red-900/30 to-red-800/30 border border-red-500/30 rounded-xl backdrop-blur-sm">
                  <div className="flex items-start space-x-4">
                    <div className="flex-shrink-0">
                      <div className="p-2 bg-red-500/20 rounded-full">
                        <svg className="h-6 w-6 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                        </svg>
                      </div>
                    </div>
                    <div>
                      <h3 className="font-semibold text-red-300 mb-1">Import Failed</h3>
                      <p className="text-red-200">{error}</p>
                    </div>
                  </div>
                </div>
              )}

              {/* Enhanced Help Section */}
              <div className="mt-8 bg-blue-900/20 backdrop-blur-sm rounded-xl p-6 border border-blue-500/20">
                <div className="flex items-center space-x-3 mb-4">
                  <div className="p-2 bg-blue-500/20 rounded-lg">
                    <FileText className="h-5 w-5 text-blue-400" />
                  </div>
                  <h3 className="text-xl font-semibold text-white">Data Format Guide</h3>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-3">
                    <h4 className="font-semibold text-blue-300 flex items-center space-x-2">
                      <div className="w-2 h-2 bg-blue-400 rounded-full"></div>
                      <span>Required Columns</span>
                    </h4>
                    <div className="space-y-2 text-sm">
                      <div className="flex items-center space-x-3 text-gray-300">
                        <code className="bg-gray-800 px-2 py-1 rounded text-blue-300">time/date</code>
                        <span>Timestamp or date</span>
                      </div>
                      <div className="flex items-center space-x-3 text-gray-300">
                        <code className="bg-gray-800 px-2 py-1 rounded text-green-300">open</code>
                        <span>Opening price</span>
                      </div>
                      <div className="flex items-center space-x-3 text-gray-300">
                        <code className="bg-gray-800 px-2 py-1 rounded text-green-300">high</code>
                        <span>Highest price</span>
                      </div>
                      <div className="flex items-center space-x-3 text-gray-300">
                        <code className="bg-gray-800 px-2 py-1 rounded text-red-300">low</code>
                        <span>Lowest price</span>
                      </div>
                      <div className="flex items-center space-x-3 text-gray-300">
                        <code className="bg-gray-800 px-2 py-1 rounded text-red-300">close</code>
                        <span>Closing price</span>
                      </div>
                      <div className="flex items-center space-x-3 text-gray-400">
                        <code className="bg-gray-800 px-2 py-1 rounded text-gray-400">volume</code>
                        <span>Trading volume (optional)</span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="space-y-3">
                    <h4 className="font-semibold text-blue-300 flex items-center space-x-2">
                      <div className="w-2 h-2 bg-blue-400 rounded-full"></div>
                      <span>Supported Formats</span>
                    </h4>
                    <div className="space-y-3 text-sm">
                      <div className="flex items-center space-x-3 text-gray-300">
                        <div className="p-1 bg-green-500/20 rounded">
                          <FileText className="h-4 w-4 text-green-400" />
                        </div>
                        <span>CSV files (.csv)</span>
                      </div>
                      <div className="flex items-center space-x-3 text-gray-300">
                        <div className="p-1 bg-green-500/20 rounded">
                          <FileText className="h-4 w-4 text-green-400" />
                        </div>
                        <span>Excel files (.xlsx, .xls)</span>
                      </div>
                      <div className="flex items-center space-x-3 text-gray-400">
                        <div className="p-1 bg-blue-500/20 rounded">
                          <TrendingUp className="h-4 w-4 text-blue-400" />
                        </div>
                        <span>TradingView exports</span>
                      </div>
                      <div className="flex items-center space-x-3 text-gray-400">
                        <div className="p-1 bg-blue-500/20 rounded">
                          <BarChart3 className="h-4 w-4 text-blue-400" />
                        </div>
                        <span>MetaTrader exports</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header with Actions */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">Chart Analysis</h1>
          <p className="text-gray-400">Dataset: {fileName}</p>
        </div>
        <div className="flex space-x-3">
          <button
            onClick={() => {/* TODO: Download data */}}
            className="flex items-center space-x-2 px-4 py-2 bg-gray-700/50 text-white rounded-lg hover:bg-gray-600/50 transition-colors"
          >
            <Download className="h-4 w-4" />
            <span>Export</span>
          </button>
          <button
            onClick={clearData}
            className="flex items-center space-x-2 px-4 py-2 bg-red-600/20 border border-red-600/30 text-red-400 rounded-lg hover:bg-red-600/30 transition-colors"
          >
            <Trash2 className="h-4 w-4" />
            <span>Clear</span>
          </button>
          <button
            onClick={clearData}
            className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <UploadIcon className="h-4 w-4" />
            <span>Upload New</span>
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-gray-800/30 backdrop-blur-sm p-4 rounded-lg border border-gray-700/50">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm font-medium text-gray-400">Total Records</h3>
              <p className="text-2xl font-bold text-white">{dataStats.totalRecords.toLocaleString()}</p>
            </div>
            <BarChart3 className="h-8 w-8 text-blue-400" />
          </div>
        </div>
        
        {dataStats.dateRange && (
          <div className="bg-gray-800/30 backdrop-blur-sm p-4 rounded-lg border border-gray-700/50">
            <h3 className="text-sm font-medium text-gray-400">Date Range</h3>
            <p className="text-sm text-white font-medium">
              {dataStats.dateRange.start}
            </p>
            <p className="text-sm text-white font-medium">
              {dataStats.dateRange.end}
            </p>
          </div>
        )}
        
        {dataStats.priceRange && (
          <>
            <div className="bg-gray-800/30 backdrop-blur-sm p-4 rounded-lg border border-gray-700/50">
              <h3 className="text-sm font-medium text-gray-400">Price Range</h3>
              <p className="text-lg text-white font-medium">
                ${dataStats.priceRange.min.toFixed(2)}
              </p>
              <p className="text-xs text-gray-400">Minimum</p>
            </div>
            <div className="bg-gray-800/30 backdrop-blur-sm p-4 rounded-lg border border-gray-700/50">
              <h3 className="text-sm font-medium text-gray-400">Maximum</h3>
              <p className="text-lg text-white font-medium">
                ${dataStats.priceRange.max.toFixed(2)}
              </p>
              <p className="text-xs text-gray-400">
                Range: ${(dataStats.priceRange.max - dataStats.priceRange.min).toFixed(2)}
              </p>
            </div>
          </>
        )}
      </div>

      {/* Chart */}
      <div className="bg-gray-800/30 backdrop-blur-sm rounded-xl border border-gray-700/50 overflow-hidden">
        <div className="p-4 border-b border-gray-700/50">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-white">Price Chart</h2>
            <div className="flex items-center space-x-2">
              <Eye className="h-4 w-4 text-gray-400" />
              <span className="text-sm text-gray-400">Interactive Chart</span>
            </div>
          </div>
        </div>
        <LightweightChart data={chartData} height={600} />
      </div>
    </div>
  );
};

export default DataImportView;