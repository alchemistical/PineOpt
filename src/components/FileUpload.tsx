import React, { useCallback } from 'react';
import { Upload, FileText, Table } from 'lucide-react';

interface FileUploadProps {
  onFileSelect: (file: File) => void;
  isLoading?: boolean;
}

const FileUpload: React.FC<FileUploadProps> = ({ onFileSelect, isLoading }) => {
  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    
    const files = Array.from(e.dataTransfer.files);
    const file = files.find(f => 
      f.name.endsWith('.csv') || 
      f.name.endsWith('.xlsx') || 
      f.name.endsWith('.xls')
    );
    
    if (file) {
      onFileSelect(file);
    }
  }, [onFileSelect]);

  const handleFileInput = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      onFileSelect(file);
    }
  }, [onFileSelect]);

  return (
    <div
      className="border-2 border-dashed border-gray-600 rounded-lg p-8 text-center hover:border-gray-500 transition-colors"
      onDragOver={handleDragOver}
      onDrop={handleDrop}
    >
      <div className="space-y-4">
        <Upload className="mx-auto h-12 w-12 text-gray-400" />
        <div>
          <h3 className="text-lg font-semibold text-white mb-2">
            Upload Crypto Data
          </h3>
          <p className="text-gray-400 mb-4">
            Drag and drop your crypto OHLC CSV or Excel file here, or click to browse
          </p>
          <div className="flex justify-center space-x-4 mb-4">
            <div className="flex items-center space-x-1 text-sm text-gray-500">
              <FileText className="h-4 w-4" />
              <span>CSV</span>
            </div>
            <div className="flex items-center space-x-1 text-sm text-gray-500">
              <Table className="h-4 w-4" />
              <span>Excel</span>
            </div>
          </div>
          <input
            type="file"
            accept=".csv,.xlsx,.xls"
            onChange={handleFileInput}
            disabled={isLoading}
            className="hidden"
            id="file-upload"
          />
          <label
            htmlFor="file-upload"
            className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 cursor-pointer disabled:opacity-50"
          >
            {isLoading ? 'Processing...' : 'Choose File'}
          </label>
        </div>
        <div className="text-xs text-gray-500">
          Expected columns: time/date, open, high, low, close, volume (optional)
        </div>
      </div>
    </div>
  );
};

export default FileUpload;