import React, { useState, useCallback } from 'react';
import { Upload, FileText, Code, Settings, Save, CheckCircle, AlertCircle, Loader } from 'lucide-react';

interface PineStrategyData {
  name: string;
  description: string;
  content: string;
  fileName: string;
}

interface PineStrategyUploadProps {
  onStrategyProcessed?: (result: any) => void;
}

const PineStrategyUpload: React.FC<PineStrategyUploadProps> = ({ onStrategyProcessed }) => {
  const [strategy, setStrategy] = useState<PineStrategyData | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string>('');
  const [successMessage, setSuccessMessage] = useState<string>('');
  const [convertedOutput, setConvertedOutput] = useState<string>('');

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    
    const files = Array.from(e.dataTransfer.files);
    const pineFile = files.find(f => 
      f.name.endsWith('.pine') || 
      f.name.endsWith('.txt') || 
      f.type === 'text/plain'
    );
    
    if (pineFile) {
      handleFileRead(pineFile);
    } else {
      setError('Please upload a .pine or .txt file containing Pine Script code.');
    }
  }, []);

  const handleFileInput = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      handleFileRead(file);
    }
  }, []);

  const handleFileRead = async (file: File) => {
    setIsUploading(true);
    setError('');
    setSuccessMessage('');
    
    try {
      const content = await file.text();
      
      // Extract strategy name from file name or content
      const baseName = file.name.replace(/\.(pine|txt)$/i, '');
      let strategyName = baseName;
      
      // Try to extract strategy name from Pine script
      const strategyMatch = content.match(/strategy\s*\(\s*["']([^"']+)["']/i);
      if (strategyMatch) {
        strategyName = strategyMatch[1];
      }

      setStrategy({
        name: strategyName,
        description: `Converted from ${file.name}`,
        content: content.trim(),
        fileName: file.name
      });
      
      setSuccessMessage('Pine script uploaded successfully!');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to read the Pine script file.');
    } finally {
      setIsUploading(false);
    }
  };

  const handleAttributeChange = (field: keyof Pick<PineStrategyData, 'name' | 'description'>, value: string) => {
    if (strategy) {
      setStrategy({ ...strategy, [field]: value });
    }
  };

  const handleConvert = async () => {
    if (!strategy) return;
    
    setIsProcessing(true);
    setError('');
    setSuccessMessage('');
    setConvertedOutput('');

    try {
      // Call the Pine2Py conversion pipeline
      const response = await fetch('/api/convert-pine', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          pine_code: strategy.content,
          strategy_name: strategy.name,
          description: strategy.description
        }),
      });

      if (!response.ok) {
        throw new Error(`Conversion failed: ${response.statusText}`);
      }

      const result = await response.json();
      setConvertedOutput(result.python_code);
      setSuccessMessage('Pine script converted successfully!');
      
      if (onStrategyProcessed) {
        onStrategyProcessed(result);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Conversion pipeline failed.');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleSaveToDatabase = async () => {
    if (!strategy || !convertedOutput) return;
    
    setIsProcessing(true);
    setError('');

    try {
      const response = await fetch('http://localhost:5001/api/strategies', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: strategy.name,
          description: strategy.description,
          pine_source: strategy.content,
          python_code: convertedOutput,
          created_at: new Date().toISOString()
        }),
      });

      if (!response.ok) {
        throw new Error(`Save failed: ${response.statusText}`);
      }

      const savedStrategy = await response.json();
      setSuccessMessage(`Strategy '${strategy.name}' saved successfully! ID: ${savedStrategy.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save strategy to database.');
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Upload Section */}
      <div className="bg-gray-800 rounded-lg p-6">
        <h2 className="text-xl font-semibold text-white mb-4 flex items-center">
          <Code className="mr-2 h-5 w-5" />
          Pine Script Strategy Upload
        </h2>
        
        {!strategy ? (
          <div
            className="border-2 border-dashed border-gray-600 rounded-lg p-8 text-center hover:border-gray-500 transition-colors"
            onDragOver={handleDragOver}
            onDrop={handleDrop}
          >
            <div className="space-y-4">
              <Upload className="mx-auto h-12 w-12 text-gray-400" />
              <div>
                <h3 className="text-lg font-semibold text-white mb-2">
                  Upload Pine Script
                </h3>
                <p className="text-gray-400 mb-4">
                  Drag and drop your .pine or .txt file here, or click to browse
                </p>
                <div className="flex justify-center space-x-4 mb-4">
                  <div className="flex items-center space-x-1 text-sm text-gray-500">
                    <FileText className="h-4 w-4" />
                    <span>.pine</span>
                  </div>
                  <div className="flex items-center space-x-1 text-sm text-gray-500">
                    <FileText className="h-4 w-4" />
                    <span>.txt</span>
                  </div>
                </div>
                <input
                  type="file"
                  accept=".pine,.txt,text/plain"
                  onChange={handleFileInput}
                  disabled={isUploading}
                  className="hidden"
                  id="pine-file-upload"
                />
                <label
                  htmlFor="pine-file-upload"
                  className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 cursor-pointer disabled:opacity-50"
                >
                  {isUploading ? (
                    <>
                      <Loader className="mr-2 h-4 w-4 animate-spin" />
                      Loading...
                    </>
                  ) : (
                    'Choose File'
                  )}
                </label>
              </div>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="flex items-center space-x-2 text-green-400">
              <CheckCircle className="h-5 w-5" />
              <span>Pine script loaded: {strategy.fileName}</span>
            </div>
            
            <div className="bg-gray-700 rounded-lg p-4">
              <pre className="text-sm text-gray-300 overflow-x-auto max-h-32">
                {strategy.content.slice(0, 200)}
                {strategy.content.length > 200 && '...'}
              </pre>
            </div>
            
            <button
              onClick={() => setStrategy(null)}
              className="text-sm text-blue-400 hover:text-blue-300"
            >
              Upload different file
            </button>
          </div>
        )}
      </div>

      {/* Strategy Attributes Form */}
      {strategy && (
        <div className="bg-gray-800 rounded-lg p-6">
          <h2 className="text-xl font-semibold text-white mb-4 flex items-center">
            <Settings className="mr-2 h-5 w-5" />
            Strategy Attributes
          </h2>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Strategy Name
              </label>
              <input
                type="text"
                value={strategy.name}
                onChange={(e) => handleAttributeChange('name', e.target.value)}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-blue-500"
                placeholder="Enter strategy name"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Description
              </label>
              <textarea
                value={strategy.description}
                onChange={(e) => handleAttributeChange('description', e.target.value)}
                rows={3}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-blue-500"
                placeholder="Enter strategy description"
              />
            </div>
          </div>
        </div>
      )}

      {/* Action Buttons */}
      {strategy && (
        <div className="flex space-x-4">
          <button
            onClick={handleConvert}
            disabled={isProcessing || !strategy.name.trim()}
            className="flex items-center px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isProcessing ? (
              <>
                <Loader className="mr-2 h-4 w-4 animate-spin" />
                Converting...
              </>
            ) : (
              <>
                <Code className="mr-2 h-4 w-4" />
                Convert to Python
              </>
            )}
          </button>

          {convertedOutput && (
            <button
              onClick={handleSaveToDatabase}
              disabled={isProcessing}
              className="flex items-center px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isProcessing ? (
                <>
                  <Loader className="mr-2 h-4 w-4 animate-spin" />
                  Saving...
                </>
              ) : (
                <>
                  <Save className="mr-2 h-4 w-4" />
                  Save to Database
                </>
              )}
            </button>
          )}
        </div>
      )}

      {/* Converted Output */}
      {convertedOutput && (
        <div className="bg-gray-800 rounded-lg p-6">
          <h2 className="text-xl font-semibold text-white mb-4">
            Converted Python Strategy
          </h2>
          <div className="bg-gray-900 rounded-lg p-4 overflow-x-auto">
            <pre className="text-sm text-green-400">
              {convertedOutput}
            </pre>
          </div>
        </div>
      )}

      {/* Status Messages */}
      {error && (
        <div className="p-4 bg-red-900 border border-red-700 rounded-lg">
          <div className="flex items-center">
            <AlertCircle className="h-5 w-5 text-red-400 mr-3" />
            <div>
              <h3 className="text-sm font-medium text-red-400">Error</h3>
              <div className="mt-1 text-sm text-red-300">{error}</div>
            </div>
          </div>
        </div>
      )}

      {successMessage && (
        <div className="p-4 bg-green-900 border border-green-700 rounded-lg">
          <div className="flex items-center">
            <CheckCircle className="h-5 w-5 text-green-400 mr-3" />
            <div>
              <h3 className="text-sm font-medium text-green-400">Success</h3>
              <div className="mt-1 text-sm text-green-300">{successMessage}</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PineStrategyUpload;