import React, { useState, useEffect } from 'react';
import { 
  Settings, 
  Play, 
  RotateCcw, 
  Save, 
  ChevronDown,
  ChevronUp,
  AlertCircle,
  CheckCircle,
  Info,
  Sliders
} from 'lucide-react';

interface StrategyParameter {
  name: string;
  default: number | string | boolean;
  min_val?: number;
  max_val?: number;
  step?: number;
  options?: string[];
  description?: string;
}

interface ParameterValue {
  name: string;
  value: number | string | boolean;
  isValid: boolean;
  errorMessage?: string;
}

interface ParameterInterfaceProps {
  strategy: {
    id: string;
    name: string;
    parameters: StrategyParameter[];
  };
  onParametersChange: (parameters: Record<string, any>) => void;
  onRunBacktest: (parameters: Record<string, any>) => void;
  isLoading?: boolean;
}

const ParameterInterface: React.FC<ParameterInterfaceProps> = ({
  strategy,
  onParametersChange,
  onRunBacktest,
  isLoading = false
}) => {
  const [parameterValues, setParameterValues] = useState<Record<string, ParameterValue>>({});
  const [expandedCategories, setExpandedCategories] = useState<Record<string, boolean>>({});
  const [hasChanges, setHasChanges] = useState(false);

  // Initialize parameter values with defaults
  useEffect(() => {
    const initialValues: Record<string, ParameterValue> = {};
    
    strategy.parameters.forEach(param => {
      initialValues[param.name] = {
        name: param.name,
        value: param.default,
        isValid: true
      };
    });
    
    setParameterValues(initialValues);
    
    // Auto-expand first category
    const categories = getParameterCategories();
    if (categories.length > 0) {
      setExpandedCategories({ [categories[0]]: true });
    }
  }, [strategy.parameters]);

  // Notify parent of parameter changes
  useEffect(() => {
    const paramObj: Record<string, any> = {};
    Object.values(parameterValues).forEach(param => {
      paramObj[param.name] = param.value;
    });
    onParametersChange(paramObj);
  }, [parameterValues, onParametersChange]);

  const getParameterCategories = (): string[] => {
    const categories = new Set<string>();
    strategy.parameters.forEach(param => {
      if (param.name.includes('vwap')) {
        categories.add('VWAP Settings');
      } else if (param.name.includes('rsi')) {
        categories.add('Momentum Indicators');
      } else if (param.name.includes('tsv')) {
        categories.add('Volume Indicators');
      } else if (param.name.includes('bb') || param.name.includes('bollinger')) {
        categories.add('Volatility Indicators');
      } else if (param.name.includes('tenkan') || param.name.includes('kijun')) {
        categories.add('Trend Indicators');
      } else if (param.name.includes('risk') || param.name.includes('percent')) {
        categories.add('Risk Management');
      } else {
        categories.add('General Settings');
      }
    });
    return Array.from(categories);
  };

  const getParametersForCategory = (category: string): StrategyParameter[] => {
    return strategy.parameters.filter(param => {
      switch (category) {
        case 'VWAP Settings':
          return param.name.includes('vwap');
        case 'Momentum Indicators':
          return param.name.includes('rsi');
        case 'Volume Indicators':
          return param.name.includes('tsv');
        case 'Volatility Indicators':
          return param.name.includes('bb') || param.name.includes('bollinger');
        case 'Trend Indicators':
          return param.name.includes('tenkan') || param.name.includes('kijun');
        case 'Risk Management':
          return param.name.includes('risk') || param.name.includes('percent');
        default:
          return !param.name.includes('vwap') && !param.name.includes('rsi') && 
                 !param.name.includes('tsv') && !param.name.includes('bb') &&
                 !param.name.includes('tenkan') && !param.name.includes('kijun') &&
                 !param.name.includes('risk') && !param.name.includes('percent');
      }
    });
  };

  const validateParameter = (param: StrategyParameter, value: any): { isValid: boolean; errorMessage?: string } => {
    if (typeof param.default === 'number') {
      const numValue = Number(value);
      
      if (isNaN(numValue)) {
        return { isValid: false, errorMessage: 'Must be a valid number' };
      }
      
      if (param.min_val !== undefined && numValue < param.min_val) {
        return { isValid: false, errorMessage: `Must be at least ${param.min_val}` };
      }
      
      if (param.max_val !== undefined && numValue > param.max_val) {
        return { isValid: false, errorMessage: `Must be at most ${param.max_val}` };
      }
    }
    
    return { isValid: true };
  };

  const handleParameterChange = (paramName: string, value: any) => {
    const param = strategy.parameters.find(p => p.name === paramName);
    if (!param) return;

    const validation = validateParameter(param, value);
    
    setParameterValues(prev => ({
      ...prev,
      [paramName]: {
        name: paramName,
        value: value,
        isValid: validation.isValid,
        errorMessage: validation.errorMessage
      }
    }));
    
    setHasChanges(true);
  };

  const resetToDefaults = () => {
    const resetValues: Record<string, ParameterValue> = {};
    
    strategy.parameters.forEach(param => {
      resetValues[param.name] = {
        name: param.name,
        value: param.default,
        isValid: true
      };
    });
    
    setParameterValues(resetValues);
    setHasChanges(false);
  };

  const handleRunBacktest = () => {
    const paramObj: Record<string, any> = {};
    Object.values(parameterValues).forEach(param => {
      paramObj[param.name] = param.value;
    });
    onRunBacktest(paramObj);
  };

  const toggleCategory = (category: string) => {
    setExpandedCategories(prev => ({
      ...prev,
      [category]: !prev[category]
    }));
  };

  const formatParameterName = (name: string): string => {
    return name
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  const renderParameterInput = (param: StrategyParameter) => {
    const currentValue = parameterValues[param.name];
    const hasError = currentValue && !currentValue.isValid;

    if (typeof param.default === 'boolean') {
      return (
        <div className="flex items-center space-x-2">
          <input
            type="checkbox"
            id={param.name}
            checked={currentValue?.value as boolean || false}
            onChange={(e) => handleParameterChange(param.name, e.target.checked)}
            className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500"
          />
          <label htmlFor={param.name} className="text-sm text-gray-300">
            {formatParameterName(param.name)}
          </label>
        </div>
      );
    }

    if (param.options) {
      return (
        <select
          value={currentValue?.value as string || ''}
          onChange={(e) => handleParameterChange(param.name, e.target.value)}
          className={`w-full px-3 py-2 bg-gray-700 border rounded-lg text-white focus:ring-2 focus:ring-blue-500 ${
            hasError ? 'border-red-500' : 'border-gray-600'
          }`}
        >
          {param.options.map(option => (
            <option key={option} value={option}>
              {option}
            </option>
          ))}
        </select>
      );
    }

    return (
      <div className="relative">
        <input
          type={typeof param.default === 'number' ? 'number' : 'text'}
          value={currentValue?.value as string || ''}
          onChange={(e) => handleParameterChange(param.name, e.target.value)}
          step={param.step || (typeof param.default === 'number' ? 'any' : undefined)}
          min={param.min_val}
          max={param.max_val}
          className={`w-full px-3 py-2 bg-gray-700 border rounded-lg text-white focus:ring-2 focus:ring-blue-500 ${
            hasError ? 'border-red-500' : 'border-gray-600'
          }`}
          placeholder={`Default: ${param.default}`}
        />
        {hasError && (
          <div className="absolute right-2 top-2">
            <AlertCircle className="h-4 w-4 text-red-500" />
          </div>
        )}
      </div>
    );
  };

  const allParametersValid = Object.values(parameterValues).every(param => param.isValid);

  return (
    <div className="bg-gray-800 rounded-xl border border-gray-600 overflow-hidden">
      {/* Header */}
      <div className="bg-gray-700 px-6 py-4 border-b border-gray-600">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <Sliders className="h-6 w-6 text-blue-400" />
            <div>
              <h2 className="text-xl font-semibold text-white">Parameter Configuration</h2>
              <p className="text-gray-400 text-sm">{strategy.name} • {strategy.parameters.length} parameters</p>
            </div>
          </div>
          
          <div className="flex items-center space-x-3">
            <button
              onClick={resetToDefaults}
              disabled={!hasChanges}
              className="flex items-center space-x-2 px-3 py-2 text-gray-400 hover:text-white disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <RotateCcw className="h-4 w-4" />
              <span className="text-sm">Reset</span>
            </button>
            
            <button
              onClick={handleRunBacktest}
              disabled={isLoading || !allParametersValid}
              className="flex items-center space-x-2 px-6 py-2 bg-green-600 hover:bg-green-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white font-medium rounded-lg transition-colors"
            >
              <Play className="h-4 w-4" />
              <span>{isLoading ? 'Running...' : 'Run Backtest'}</span>
            </button>
          </div>
        </div>
      </div>

      {/* Parameter Categories */}
      <div className="p-6 space-y-4 max-h-96 overflow-y-auto">
        {getParameterCategories().map(category => {
          const categoryParams = getParametersForCategory(category);
          const isExpanded = expandedCategories[category];
          
          return (
            <div key={category} className="border border-gray-700 rounded-lg">
              <button
                onClick={() => toggleCategory(category)}
                className="w-full flex items-center justify-between p-4 text-left hover:bg-gray-700/50 transition-colors"
              >
                <div className="flex items-center space-x-3">
                  <span className="text-white font-medium">{category}</span>
                  <span className="text-gray-400 text-sm">({categoryParams.length} parameters)</span>
                </div>
                {isExpanded ? (
                  <ChevronUp className="h-5 w-5 text-gray-400" />
                ) : (
                  <ChevronDown className="h-5 w-5 text-gray-400" />
                )}
              </button>
              
              {isExpanded && (
                <div className="px-4 pb-4 space-y-4 border-t border-gray-700">
                  {categoryParams.map(param => {
                    const currentValue = parameterValues[param.name];
                    const hasError = currentValue && !currentValue.isValid;
                    
                    return (
                      <div key={param.name} className="space-y-2">
                        <div className="flex items-center justify-between">
                          <label className="block text-sm font-medium text-gray-300">
                            {formatParameterName(param.name)}
                          </label>
                          {param.description && (
                            <div className="group relative">
                              <Info className="h-4 w-4 text-gray-500 cursor-help" />
                              <div className="absolute right-0 bottom-6 bg-gray-900 text-white text-xs rounded-lg px-2 py-1 opacity-0 group-hover:opacity-100 transition-opacity z-10 whitespace-nowrap">
                                {param.description}
                              </div>
                            </div>
                          )}
                        </div>
                        
                        {renderParameterInput(param)}
                        
                        {/* Parameter info */}
                        <div className="flex items-center justify-between text-xs text-gray-500">
                          <span>
                            Default: {String(param.default)}
                            {param.min_val !== undefined && param.max_val !== undefined && 
                              ` • Range: ${param.min_val}-${param.max_val}`
                            }
                          </span>
                          {currentValue && (
                            <div className="flex items-center space-x-1">
                              {currentValue.isValid ? (
                                <CheckCircle className="h-3 w-3 text-green-500" />
                              ) : (
                                <AlertCircle className="h-3 w-3 text-red-500" />
                              )}
                            </div>
                          )}
                        </div>
                        
                        {hasError && (
                          <p className="text-red-500 text-xs">{currentValue.errorMessage}</p>
                        )}
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Status Bar */}
      <div className="bg-gray-700 px-6 py-3 border-t border-gray-600">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4 text-sm">
            <span className="text-gray-400">
              Parameters: {Object.keys(parameterValues).length}
            </span>
            <span className={`flex items-center space-x-1 ${allParametersValid ? 'text-green-400' : 'text-red-400'}`}>
              {allParametersValid ? (
                <CheckCircle className="h-4 w-4" />
              ) : (
                <AlertCircle className="h-4 w-4" />
              )}
              <span>{allParametersValid ? 'All Valid' : 'Has Errors'}</span>
            </span>
          </div>
          
          {hasChanges && (
            <span className="text-yellow-400 text-sm flex items-center space-x-1">
              <Settings className="h-4 w-4" />
              <span>Unsaved Changes</span>
            </span>
          )}
        </div>
      </div>
    </div>
  );
};

export default ParameterInterface;