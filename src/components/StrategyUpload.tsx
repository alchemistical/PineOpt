import React, { useState, useCallback, useRef } from 'react';
import { 
  Upload, 
  CheckCircle, 
  AlertCircle, 
  X, 
  FileText, 
  Code, 
  Loader, 
  AlertTriangle,
  Info,
  Tag,
  User,
  FileCode
} from 'lucide-react';

interface ValidationResult {
  type: string;
  status: 'pass' | 'fail' | 'warning' | 'error';
  message: string;
  line_number?: number;
  column_number?: number;
  details?: any;
}

interface ValidationSummary {
  total_checks: number;
  passed: number;
  failed: number;
  warnings: number;
  errors: number;
  is_valid: boolean;
  has_warnings: boolean;
  by_type: Record<string, ValidationResult[]>;
}

interface UploadedStrategy {
  id: string;
  name: string;
  language: 'python' | 'pine';
  validation_status: 'pending' | 'valid' | 'invalid' | 'error';
  file_size: number;
  parameters: Record<string, any>;
  dependencies: string[];
  tags: string[];
}

interface StrategyUploadProps {
  onStrategyUploaded?: (strategy: UploadedStrategy) => void;
  onClose?: () => void;
}

const StrategyUpload: React.FC<StrategyUploadProps> = ({ onStrategyUploaded, onClose }) => {
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [uploadResult, setUploadResult] = useState<{
    strategy: UploadedStrategy;
    validation: ValidationSummary;
  } | null>(null);
  const [error, setError] = useState<string | null>(null);
  
  // Form fields
  const [strategyName, setStrategyName] = useState('');
  const [description, setDescription] = useState('');
  const [author, setAuthor] = useState('');
  const [tags, setTags] = useState('');
  
  const fileInputRef = useRef<HTMLInputElement>(null);
  
  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);
  
  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);
  
  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    
    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      handleFileSelection(files[0]);
    }
  }, []);
  
  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      handleFileSelection(files[0]);
    }
  };
  
  const handleFileSelection = (file: File) => {
    // Validate file
    const allowedExtensions = ['.py', '.pine'];
    const fileExtension = '.' + file.name.split('.').pop()?.toLowerCase();
    
    if (!allowedExtensions.includes(fileExtension)) {
      setError(`Invalid file type. Allowed: ${allowedExtensions.join(', ')}`);
      return;
    }
    
    if (file.size > 10 * 1024 * 1024) { // 10MB
      setError('File too large. Maximum size: 10MB');
      return;
    }
    
    setUploadedFile(file);
    setError(null);
    
    // Auto-fill strategy name if not set
    if (!strategyName) {
      const nameWithoutExt = file.name.replace(/\.[^/.]+$/, '');
      setStrategyName(nameWithoutExt);
    }
  };
  
  const handleUpload = async () => {
    if (!uploadedFile) return;
    
    setIsUploading(true);
    setError(null);
    
    try {
      const formData = new FormData();
      formData.append('file', uploadedFile);
      formData.append('name', strategyName || uploadedFile.name.replace(/\.[^/.]+$/, ''));
      formData.append('description', description);
      formData.append('author', author || 'Unknown');
      formData.append('tags', tags);
      
      const response = await fetch('http://localhost:5007/api/strategies/upload', {
        method: 'POST',
        body: formData
      });
      
      const data = await response.json();
      
      if (!response.ok || !data.success) {
        throw new Error(data.error || 'Upload failed');
      }
      
      setUploadResult({
        strategy: data.strategy,
        validation: data.validation
      });
      
      // Notify parent component
      if (onStrategyUploaded) {
        onStrategyUploaded(data.strategy);
      }
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed');
    } finally {
      setIsUploading(false);
    }
  };
  
  const resetForm = () => {
    setUploadedFile(null);
    setUploadResult(null);
    setError(null);
    setStrategyName('');
    setDescription('');
    setAuthor('');
    setTags('');
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };
  
  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'pass':
        return <CheckCircle className="h-4 w-4 text-green-400" />;
      case 'fail':
        return <AlertCircle className="h-4 w-4 text-red-400" />;
      case 'warning':
        return <AlertTriangle className="h-4 w-4 text-yellow-400" />;
      case 'error':
        return <AlertCircle className="h-4 w-4 text-red-500" />;
      default:
        return <Info className="h-4 w-4 text-blue-400" />;
    }
  };
  
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pass':
        return 'border-green-500/30 bg-green-500/10';
      case 'fail':
        return 'border-red-500/30 bg-red-500/10';
      case 'warning':
        return 'border-yellow-500/30 bg-yellow-500/10';
      case 'error':
        return 'border-red-600/30 bg-red-600/10';
      default:
        return 'border-blue-500/30 bg-blue-500/10';
    }
  };
  
  if (uploadResult) {
    return (
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-gradient-to-r from-green-500 to-blue-600 rounded-lg">
              <CheckCircle className="h-5 w-5 text-white" />
            </div>
            <div>
              <h3 className="text-xl font-semibold text-white">Strategy Uploaded Successfully</h3>
              <p className="text-gray-400">Validation completed</p>
            </div>
          </div>
          <div className="flex space-x-2">
            <button
              onClick={resetForm}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
            >
              Upload Another
            </button>
            {onClose && (
              <button
                onClick={onClose}
                className="p-2 text-gray-400 hover:text-white transition-colors"
              >
                <X className="h-5 w-5" />
              </button>
            )}
          </div>
        </div>
        
        {/* Strategy Info */}
        <div className="bg-gray-800/30 backdrop-blur-sm rounded-xl p-6 border border-gray-700/50">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="text-lg font-medium text-white mb-4">Strategy Details</h4>
              <div className="space-y-3">
                <div>
                  <span className="text-gray-400 text-sm">Name:</span>
                  <p className="text-white font-medium">{uploadResult.strategy.name}</p>
                </div>
                <div>
                  <span className="text-gray-400 text-sm">Language:</span>
                  <p className="text-white font-medium capitalize">{uploadResult.strategy.language}</p>
                </div>
                <div>
                  <span className="text-gray-400 text-sm">File Size:</span>
                  <p className="text-white font-medium">{(uploadResult.strategy.file_size / 1024).toFixed(1)} KB</p>
                </div>
                <div>
                  <span className="text-gray-400 text-sm">Status:</span>
                  <div className="flex items-center space-x-2">
                    {getStatusIcon(uploadResult.strategy.validation_status)}
                    <span className="text-white capitalize">{uploadResult.strategy.validation_status}</span>
                  </div>
                </div>
              </div>
            </div>
            
            <div>
              <h4 className="text-lg font-medium text-white mb-4">Validation Summary</h4>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-400">Total Checks:</span>
                  <span className="text-white font-medium">{uploadResult.validation.total_checks}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-green-400">Passed:</span>
                  <span className="text-green-400 font-medium">{uploadResult.validation.passed}</span>
                </div>
                {uploadResult.validation.warnings > 0 && (
                  <div className="flex justify-between">
                    <span className="text-yellow-400">Warnings:</span>
                    <span className="text-yellow-400 font-medium">{uploadResult.validation.warnings}</span>
                  </div>
                )}
                {uploadResult.validation.failed > 0 && (
                  <div className="flex justify-between">
                    <span className="text-red-400">Failed:</span>
                    <span className="text-red-400 font-medium">{uploadResult.validation.failed}</span>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
        
        {/* Validation Details */}
        {Object.keys(uploadResult.validation.by_type).length > 0 && (
          <div className="bg-gray-800/30 backdrop-blur-sm rounded-xl p-6 border border-gray-700/50">
            <h4 className="text-lg font-medium text-white mb-4">Validation Details</h4>
            <div className="space-y-4">
              {Object.entries(uploadResult.validation.by_type).map(([type, results]) => (
                <div key={type}>
                  <h5 className="text-md font-medium text-gray-300 mb-2 capitalize">{type} Validation</h5>
                  <div className="space-y-2">
                    {results.map((result, index) => (
                      <div
                        key={index}
                        className={`p-3 rounded-lg border ${getStatusColor(result.status)}`}
                      >
                        <div className="flex items-start space-x-2">
                          {getStatusIcon(result.status)}
                          <div className="flex-1">
                            <p className="text-white text-sm">{result.message}</p>
                            {result.line && (
                              <p className="text-gray-400 text-xs mt-1">Line {result.line}</p>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  }
  
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg">
            <Upload className="h-5 w-5 text-white" />
          </div>
          <div>
            <h3 className="text-xl font-semibold text-white">Upload Strategy</h3>
            <p className="text-gray-400">Upload Python or Pine Script trading strategies</p>
          </div>
        </div>
        {onClose && (
          <button
            onClick={onClose}
            className="p-2 text-gray-400 hover:text-white transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        )}
      </div>
      
      {/* File Upload Area */}
      <div
        className={`relative border-2 border-dashed rounded-xl p-8 transition-colors ${
          isDragging
            ? 'border-blue-400 bg-blue-400/10'
            : 'border-gray-600 hover:border-gray-500'
        }`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".py,.pine"
          onChange={handleFileInputChange}
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
        />
        
        <div className="text-center">
          {uploadedFile ? (
            <div className="space-y-4">
              <div className="p-3 bg-gray-700/50 rounded-lg inline-flex items-center space-x-3">
                {uploadedFile.name.endsWith('.py') ? (
                  <FileCode className="h-8 w-8 text-blue-400" />
                ) : (
                  <FileText className="h-8 w-8 text-green-400" />
                )}
                <div className="text-left">
                  <p className="text-white font-medium">{uploadedFile.name}</p>
                  <p className="text-gray-400 text-sm">
                    {(uploadedFile.size / 1024).toFixed(1)} KB • {uploadedFile.name.endsWith('.py') ? 'Python' : 'Pine Script'}
                  </p>
                </div>
                <button
                  onClick={() => setUploadedFile(null)}
                  className="p-1 text-gray-400 hover:text-red-400 transition-colors"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              <div className="p-4 bg-gray-700/30 rounded-full w-fit mx-auto">
                <Upload className="h-8 w-8 text-gray-400" />
              </div>
              <div>
                <h4 className="text-lg font-medium text-white mb-2">Drop your strategy file here</h4>
                <p className="text-gray-400 mb-4">
                  or <span className="text-blue-400 cursor-pointer">click to browse</span>
                </p>
                <p className="text-gray-500 text-sm">
                  Supports Python (.py) and Pine Script (.pine) files up to 10MB
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
      
      {/* Strategy Metadata Form */}
      {uploadedFile && (
        <div className="bg-gray-800/30 backdrop-blur-sm rounded-xl p-6 border border-gray-700/50">
          <h4 className="text-lg font-medium text-white mb-4">Strategy Information</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-gray-300 text-sm font-medium mb-2">
                <User className="h-4 w-4 inline mr-1" />
                Strategy Name
              </label>
              <input
                type="text"
                value={strategyName}
                onChange={(e) => setStrategyName(e.target.value)}
                placeholder="Enter strategy name"
                className="w-full px-3 py-2 bg-gray-700/50 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
              />
            </div>
            
            <div>
              <label className="block text-gray-300 text-sm font-medium mb-2">
                <User className="h-4 w-4 inline mr-1" />
                Author
              </label>
              <input
                type="text"
                value={author}
                onChange={(e) => setAuthor(e.target.value)}
                placeholder="Your name"
                className="w-full px-3 py-2 bg-gray-700/50 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
              />
            </div>
            
            <div className="md:col-span-2">
              <label className="block text-gray-300 text-sm font-medium mb-2">
                <FileText className="h-4 w-4 inline mr-1" />
                Description
              </label>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Describe your strategy..."
                rows={3}
                className="w-full px-3 py-2 bg-gray-700/50 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500 resize-none"
              />
            </div>
            
            <div className="md:col-span-2">
              <label className="block text-gray-300 text-sm font-medium mb-2">
                <Tag className="h-4 w-4 inline mr-1" />
                Tags (comma-separated)
              </label>
              <input
                type="text"
                value={tags}
                onChange={(e) => setTags(e.target.value)}
                placeholder="rsi, momentum, scalping"
                className="w-full px-3 py-2 bg-gray-700/50 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
              />
            </div>
          </div>
        </div>
      )}
      
      {/* Error Display */}
      {error && (
        <div className="bg-red-500/20 border border-red-500/30 rounded-lg p-4">
          <div className="flex items-center space-x-2">
            <AlertCircle className="h-5 w-5 text-red-400" />
            <p className="text-red-400">{error}</p>
          </div>
        </div>
      )}
      
      {/* Upload Button */}
      {uploadedFile && (
        <div className="flex justify-end">
          <button
            onClick={handleUpload}
            disabled={isUploading}
            className="flex items-center space-x-2 px-6 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-600/50 text-white rounded-lg transition-colors"
          >
            {isUploading ? (
              <>
                <Loader className="h-4 w-4 animate-spin" />
                <span>Uploading & Validating...</span>
              </>
            ) : (
              <>
                <Upload className="h-4 w-4" />
                <span>Upload Strategy</span>
              </>
            )}
          </button>
        </div>
      )}
    </div>
  );
};

export default StrategyUpload;