import React, { useState } from 'react';
import { Code2, Zap, FileText, CheckCircle, AlertTriangle, Download, Copy } from 'lucide-react';
import PineStrategyUpload from './PineStrategyUpload';

interface ConversionResult {
  success: boolean;
  strategy_name: string;
  python_code: string;
  conversion_timestamp: string;
  error?: string;
}

const PineConverterView: React.FC = () => {
  const [conversionResult, setConversionResult] = useState<ConversionResult | null>(null);
  const [isConverting, setIsConverting] = useState(false);

  const handleStrategyProcessed = (result: any) => {
    setConversionResult(result);
  };

  const copyToClipboard = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      // Could add a toast notification here
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  const downloadPythonFile = () => {
    if (!conversionResult) return;
    
    const blob = new Blob([conversionResult.python_code], { type: 'text/python' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${conversionResult.strategy_name.toLowerCase().replace(/\s+/g, '_')}.py`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">Pine Script Converter</h1>
          <p className="text-gray-400">Transform crypto Pine Script strategies to Python backtesting code</p>
        </div>
        <div className="flex items-center space-x-2 px-3 py-1.5 bg-green-500/20 border border-green-500/30 rounded-full">
          <div className="w-2 h-2 bg-green-400 rounded-full"></div>
          <span className="text-green-400 text-sm font-medium">Converter Online</span>
        </div>
      </div>

      {/* Features Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-gradient-to-br from-purple-500/20 to-pink-500/20 p-6 rounded-xl border border-gray-700/50">
          <Code2 className="h-8 w-8 text-purple-400 mb-3" />
          <h3 className="text-lg font-semibold text-white mb-2">Smart Parsing</h3>
          <p className="text-gray-300 text-sm">Advanced Pine Script v5 parser with pattern recognition</p>
        </div>
        
        <div className="bg-gradient-to-br from-blue-500/20 to-cyan-500/20 p-6 rounded-xl border border-gray-700/50">
          <Zap className="h-8 w-8 text-blue-400 mb-3" />
          <h3 className="text-lg font-semibold text-white mb-2">Fast Conversion</h3>
          <p className="text-gray-300 text-sm">Real-time conversion with immediate Python output</p>
        </div>
        
        <div className="bg-gradient-to-br from-green-500/20 to-teal-500/20 p-6 rounded-xl border border-gray-700/50">
          <FileText className="h-8 w-8 text-green-400 mb-3" />
          <h3 className="text-lg font-semibold text-white mb-2">Ready to Use</h3>
          <p className="text-gray-300 text-sm">Generated code works with crypto data and pandas runtime</p>
        </div>
      </div>

      {/* Main Conversion Interface */}
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">
        {/* Upload Section */}
        <div className="space-y-6">
          <div className="bg-gray-800/30 backdrop-blur-sm rounded-xl border border-gray-700/50 overflow-hidden">
            <div className="p-6 border-b border-gray-700/50">
              <h2 className="text-xl font-semibold text-white flex items-center">
                <Code2 className="mr-2 h-5 w-5" />
                Pine Script Input
              </h2>
            </div>
            <div className="p-6">
              <PineStrategyUpload onStrategyProcessed={handleStrategyProcessed} />
            </div>
          </div>

          {/* Supported Features */}
          <div className="bg-gray-800/30 backdrop-blur-sm rounded-xl p-6 border border-gray-700/50">
            <h3 className="text-lg font-semibold text-white mb-4">Currently Supported</h3>
            <div className="space-y-3">
              {[
                { feature: 'Crypto RSI Strategies', status: 'full', description: 'Complete RSI indicator support for crypto' },
                { feature: 'Input Parameters', status: 'full', description: 'Parameter extraction and ranges' },
                { feature: 'Basic Logic', status: 'full', description: 'Entry/exit conditions' },
                { feature: 'Moving Averages', status: 'partial', description: 'SMA, EMA support' },
                { feature: 'Complex Conditions', status: 'coming', description: 'Multi-condition logic' },
              ].map((item, index) => {
                const statusConfig = {
                  full: { color: 'text-green-400', bg: 'bg-green-500/20', icon: CheckCircle },
                  partial: { color: 'text-yellow-400', bg: 'bg-yellow-500/20', icon: AlertTriangle },
                  coming: { color: 'text-gray-400', bg: 'bg-gray-500/20', icon: AlertTriangle }
                };
                const config = statusConfig[item.status as keyof typeof statusConfig];
                const Icon = config.icon;
                
                return (
                  <div key={index} className="flex items-start space-x-3">
                    <div className={`p-1 rounded ${config.bg}`}>
                      <Icon className={`h-3 w-3 ${config.color}`} />
                    </div>
                    <div>
                      <div className="text-white text-sm font-medium">{item.feature}</div>
                      <div className="text-gray-400 text-xs">{item.description}</div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Results Section */}
        <div className="space-y-6">
          {conversionResult ? (
            <div className="bg-gray-800/30 backdrop-blur-sm rounded-xl border border-gray-700/50 overflow-hidden">
              <div className="p-6 border-b border-gray-700/50">
                <div className="flex items-center justify-between">
                  <h2 className="text-xl font-semibold text-white flex items-center">
                    <FileText className="mr-2 h-5 w-5" />
                    Python Output
                  </h2>
                  <div className="flex space-x-2">
                    <button
                      onClick={() => copyToClipboard(conversionResult.python_code)}
                      className="p-2 bg-gray-700/50 hover:bg-gray-600/50 rounded-lg transition-colors"
                      title="Copy to clipboard"
                    >
                      <Copy className="h-4 w-4 text-gray-400" />
                    </button>
                    <button
                      onClick={downloadPythonFile}
                      className="p-2 bg-blue-600/20 border border-blue-600/30 hover:bg-blue-600/30 rounded-lg transition-colors"
                      title="Download Python file"
                    >
                      <Download className="h-4 w-4 text-blue-400" />
                    </button>
                  </div>
                </div>
              </div>
              
              {conversionResult.success ? (
                <div className="p-6">
                  <div className="mb-4 p-3 bg-green-900/50 border border-green-700/50 rounded-lg">
                    <div className="flex items-center">
                      <CheckCircle className="h-5 w-5 text-green-400 mr-3" />
                      <div>
                        <div className="text-green-400 font-medium text-sm">Conversion Successful</div>
                        <div className="text-green-300 text-xs">
                          Strategy: {conversionResult.strategy_name} • {new Date(conversionResult.conversion_timestamp).toLocaleString()}
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  <div className="bg-gray-900/50 rounded-lg p-4 overflow-x-auto">
                    <pre className="text-sm text-green-400 font-mono whitespace-pre-wrap">
                      {conversionResult.python_code}
                    </pre>
                  </div>
                </div>
              ) : (
                <div className="p-6">
                  <div className="p-4 bg-red-900/50 border border-red-700/50 rounded-lg">
                    <div className="flex items-center">
                      <AlertTriangle className="h-5 w-5 text-red-400 mr-3" />
                      <div>
                        <div className="text-red-400 font-medium text-sm">Conversion Failed</div>
                        <div className="text-red-300 text-xs mt-1">{conversionResult.error}</div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="bg-gray-800/30 backdrop-blur-sm rounded-xl border border-gray-700/50 p-12">
              <div className="text-center">
                <div className="p-4 bg-gray-700/30 rounded-full w-16 h-16 mx-auto mb-4 flex items-center justify-center">
                  <FileText className="h-8 w-8 text-gray-400" />
                </div>
                <h3 className="text-lg font-medium text-white mb-2">Ready for Conversion</h3>
                <p className="text-gray-400 text-sm">Upload a Pine Script file to see the Python output here</p>
              </div>
            </div>
          )}

          {/* Conversion Tips */}
          <div className="bg-gray-800/30 backdrop-blur-sm rounded-xl p-6 border border-gray-700/50">
            <h3 className="text-lg font-semibold text-white mb-4">Conversion Tips</h3>
            <div className="space-y-3 text-sm">
              <div className="flex items-start space-x-2">
                <div className="w-1.5 h-1.5 bg-blue-400 rounded-full mt-1.5 flex-shrink-0"></div>
                <div className="text-gray-300">Use Pine Script v5 syntax for best results</div>
              </div>
              <div className="flex items-start space-x-2">
                <div className="w-1.5 h-1.5 bg-blue-400 rounded-full mt-1.5 flex-shrink-0"></div>
                <div className="text-gray-300">Include clear variable names and comments</div>
              </div>
              <div className="flex items-start space-x-2">
                <div className="w-1.5 h-1.5 bg-blue-400 rounded-full mt-1.5 flex-shrink-0"></div>
                <div className="text-gray-300">Define input parameters with proper ranges</div>
              </div>
              <div className="flex items-start space-x-2">
                <div className="w-1.5 h-1.5 bg-blue-400 rounded-full mt-1.5 flex-shrink-0"></div>
                <div className="text-gray-300">Simple strategies convert more accurately</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PineConverterView;