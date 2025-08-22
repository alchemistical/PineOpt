"""
Intelligent Pine Script to Python Converter - Fixed Version
Uses AI analysis to generate accurate Python strategy implementations
"""

import sys
from pathlib import Path
import json
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import pandas as pd
import numpy as np

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from research.ai_analysis.advanced_hye_analyzer import HYEStrategyAnalyzer
from research.intelligent_converter.indicator_library import IndicatorLibrary, PineScriptHelpers
from shared.types.strategy import StrategySignals, StrategyParameter, StrategyMetadata

logger = logging.getLogger(__name__)

@dataclass
class ConversionResult:
    """Result of Pine Script to Python conversion"""
    success: bool
    python_code: str
    strategy_class: Optional[type] = None
    parameters: List[StrategyParameter] = None
    metadata: StrategyMetadata = None
    error_message: Optional[str] = None
    analysis_used: Optional[Dict[str, Any]] = None

class IntelligentConverter:
    """AI-powered converter that uses analysis results to generate accurate Python strategies"""
    
    def __init__(self):
        self.indicator_lib = IndicatorLibrary()
        self.pine_helpers = PineScriptHelpers()
    
    def convert_hye_strategy(self, pine_code: str, strategy_name: str = "HYEStrategy") -> ConversionResult:
        """Convert HYE strategy using AI analysis"""
        try:
            # Get HYE analysis
            analyzer = HYEStrategyAnalyzer()
            analysis = analyzer.analyze_hye_strategy(pine_code)
            
            # Extract parameters
            parameters = self._extract_hye_parameters(analysis)
            
            # Generate Python code
            python_code = self._generate_simple_hye_code(strategy_name, parameters)
            
            return ConversionResult(
                success=True,
                python_code=python_code,
                parameters=parameters,
                analysis_used=analysis
            )
            
        except Exception as e:
            logger.error(f"HYE conversion failed: {e}")
            return ConversionResult(
                success=False,
                python_code="",
                error_message=str(e)
            )
    
    def _extract_hye_parameters(self, analysis: Dict[str, Any]) -> List[StrategyParameter]:
        """Extract parameters for HYE strategy from analysis"""
        parameters = []
        
        # Get all extracted parameters from analysis
        all_params = analysis.get('parameters', {}).get('all_parameters', [])
        
        # Parameter mapping with proper types and ranges
        param_mapping = {
            'source': {'min': None, 'max': None, 'type': 'string'},
            'smallcumulativePeriod': {'min': 1, 'max': 50, 'type': 'int'},
            'bigcumulativePeriod': {'min': 1, 'max': 50, 'type': 'int'},
            'meancumulativePeriod': {'min': 10, 'max': 200, 'type': 'int'},
            'percentBelowToBuy': {'min': 0.1, 'max': 10.0, 'type': 'float'},
            'rsiPeriod': {'min': 2, 'max': 50, 'type': 'int'},
            'rsiEmaPeriod': {'min': 1, 'max': 20, 'type': 'int'},
            'rsiLevelforBuy': {'min': 10, 'max': 90, 'type': 'int'}
        }
        
        for param in all_params:
            var_name = param['variable_name']
            if var_name in param_mapping:
                mapping = param_mapping[var_name]
                
                # Convert parameter names to Python-friendly format
                python_name = self._convert_pine_param_name(var_name)
                
                param_obj = StrategyParameter(
                    name=python_name,
                    default=param['default_value'],
                    min_val=mapping.get('min'),
                    max_val=mapping.get('max'),
                    description=param['title']
                )
                parameters.append(param_obj)
        
        print(f"   ✅ Created {len(parameters)} strategy parameters")
        
        return parameters
    
    def _convert_pine_param_name(self, pine_name: str) -> str:
        """Convert Pine Script parameter name to Python-friendly name"""
        conversions = {
            'smallcumulativePeriod': 'small_vwap_period',
            'bigcumulativePeriod': 'big_vwap_period', 
            'meancumulativePeriod': 'mean_vwap_period',
            'percentBelowToBuy': 'percent_below_to_buy',
            'rsiPeriod': 'rsi_period',
            'rsiEmaPeriod': 'rsi_ema_period',
            'rsiLevelforBuy': 'rsi_level_for_buy',
            'source': 'source'
        }
        return conversions.get(pine_name, pine_name.lower())
    
    def _generate_simple_hye_code(self, strategy_name: str, parameters: List[StrategyParameter]) -> str:
        """Generate simplified HYE Python code"""
        
        param_defaults = {p.name: p.default for p in parameters}
        
        return f'''"""
AI-Converted HYE Combo Market Strategy
Simplified version focusing on core VWAP + RSI logic
"""

import pandas as pd
import numpy as np
from typing import Dict, Any
from research.intelligent_converter.indicator_library import IndicatorLibrary, PineScriptHelpers
from shared.types.strategy import StrategySignals, StrategyParameter, StrategyMetadata

class {strategy_name.replace(' ', '')}:
    """AI-Converted HYE strategy with core logic"""
    
    def __init__(self):
        self.indicators = IndicatorLibrary()
        self.helpers = PineScriptHelpers()
    
    def build_signals(self, df: pd.DataFrame, **params) -> StrategySignals:
        """Generate trading signals"""
        
        # Get parameters with defaults (exact names from HYE Pine Script)
        source = params.get('source', 'close')  # Source for RSI
        small_vwap_period = params.get('small_vwap_period', {param_defaults.get('small_vwap_period', 8)})
        big_vwap_period = params.get('big_vwap_period', {param_defaults.get('big_vwap_period', 10)})
        mean_vwap_period = params.get('mean_vwap_period', {param_defaults.get('mean_vwap_period', 50)})
        rsi_period = params.get('rsi_period', {param_defaults.get('rsi_period', 2)})  # HYE uses 2
        rsi_ema_period = params.get('rsi_ema_period', {param_defaults.get('rsi_ema_period', 5)})  # HYE uses 5
        rsi_level_for_buy = params.get('rsi_level_for_buy', {param_defaults.get('rsi_level_for_buy', 30)})  # Max RSI level
        percent_below_to_buy = params.get('percent_below_to_buy', {param_defaults.get('percent_below_to_buy', 2.0)})
        
        # Calculate VWAP indicators (exact HYE implementation)
        # Small VWAP: 8-period VWAP
        small_vwap = self.indicators.vwap(df, small_vwap_period).values
        
        # Big VWAP: 10-period VWAP  
        big_vwap = self.indicators.vwap(df, big_vwap_period).values
        
        # Mean VWAP: 50-period VWAP
        mean_vwap = self.indicators.vwap(df, mean_vwap_period).values
        
        # RSI calculation with EMA smoothing (exact HYE logic)
        source_data = df[source] if source in df.columns else df['close']
        rsi_value = self.indicators.rsi(source_data, rsi_period).values
        rsi_ema = self.indicators.ema(rsi_value, rsi_ema_period).values
        
        # Buy MA calculation: ((100 - percentBelowToBuy) / 100) * bigvwapValue[0]
        # In Pine Script, [0] refers to current bar, so we use the current big_vwap value
        buy_threshold_multiplier = (100 - percent_below_to_buy) / 100
        buy_ma = buy_threshold_multiplier * big_vwap
        
        # Position tracking (simplified)
        # In Pine Script: notInTrade = strategy.position_size <= 0
        # We'll use a simple approach for now
        
        # Entry conditions (exact HYE logic):
        # if(crossunder(smallvwapValue, buyMA) and rsiEMA < rsiLevelforBuy and close < meanvwapValue and notInTrade)
        entries = (
            self.helpers.crossunder(small_vwap, buy_ma) &
            (rsi_ema < rsi_level_for_buy) &
            (df['close'] < mean_vwap)
            # Note: notInTrade condition handled by backtest engine
        )
        
        # Exit conditions (exact HYE logic):
        # if(close > meanvwapValue)
        exits = df['close'] > mean_vwap
        
        return StrategySignals(entries=entries, exits=exits)

# Strategy configuration
STRATEGY_NAME = "{strategy_name}"

PARAM_DEFINITIONS = [
{self._format_parameters(parameters)}
]

def build_signals(df: pd.DataFrame, **params) -> StrategySignals:
    """Main entry point"""
    strategy = {strategy_name.replace(' ', '')}()
    return strategy.build_signals(df, **params)

METADATA = StrategyMetadata(
    name=STRATEGY_NAME,
    description="HYE Combo Market Strategy - VWAP Mean Reversion with RSI filtering",
    parameters=PARAM_DEFINITIONS
)
'''
    
    def _format_parameters(self, parameters: List[StrategyParameter]) -> str:
        """Format parameter definitions for code"""
        lines = []
        for param in parameters:
            # Handle string defaults properly
            if isinstance(param.default, str):
                default_val = f"'{param.default}'"
            else:
                default_val = param.default
                
            lines.append(f"""    StrategyParameter(
        name='{param.name}',
        default={default_val},
        min_val={param.min_val},
        max_val={param.max_val},
        description='{param.description}'
    )""")
        return ',\n'.join(lines)

# Test function
def test_hye_conversion():
    """Test the HYE conversion"""
    hye_path = Path(__file__).parent.parent.parent / "examples" / "pine_scripts" / "hye.pine"
    
    if not hye_path.exists():
        print("❌ HYE file not found")
        return
    
    with open(hye_path, 'r') as f:
        hye_code = f.read()
    
    converter = IntelligentConverter()
    result = converter.convert_hye_strategy(hye_code)
    
    if result.success:
        print("✅ HYE conversion successful!")
        print(f"Parameters: {len(result.parameters)}")
        
        # Save output
        output_path = Path(__file__).parent / "output" / "hye_converted.py"
        output_path.parent.mkdir(exist_ok=True)
        
        with open(output_path, 'w') as f:
            f.write(result.python_code)
        
        print(f"💾 Saved to: {output_path}")
        return result
    else:
        print(f"❌ Conversion failed: {result.error_message}")
        return None

if __name__ == "__main__":
    test_hye_conversion()