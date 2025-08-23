"""
Intelligent Pine Script to Python Converter
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
    """
    AI-powered converter that uses analysis results to generate accurate Python strategies
    """
    
    def __init__(self):
        self.indicator_lib = IndicatorLibrary()
        self.pine_helpers = PineScriptHelpers()
    
    def convert_strategy(self, pine_code: str, strategy_name: str, 
                        analysis: Optional[Dict[str, Any]] = None) -> ConversionResult:
        """
        Convert Pine Script strategy to Python using AI analysis
        
        Args:
            pine_code: Original Pine Script code
            strategy_name: Name of the strategy
            analysis: Pre-computed AI analysis (optional)
            
        Returns:
            ConversionResult with Python implementation
        """
        try:
            # Get analysis if not provided
            if analysis is None:
                if 'hye' in strategy_name.lower() or 'vwap' in pine_code.lower():
                    analyzer = HYEStrategyAnalyzer()
                    analysis = analyzer.analyze_hye_strategy(pine_code)
                else:
                    # TODO: Use general analyzer
                    analysis = {'strategy_name': strategy_name, 'conversion_roadmap': []}
            
            # Determine conversion approach based on analysis
            if self._is_hye_type_strategy(analysis):
                return self._convert_hye_strategy(pine_code, strategy_name, analysis)
            else:
                return self._convert_general_strategy(pine_code, strategy_name, analysis)
            
        except Exception as e:
            logger.error(f"Strategy conversion failed: {e}")
            return ConversionResult(
                success=False
                python_code=""
                error_message=str(e)
            )
    
    def _is_hye_type_strategy(self, analysis: Dict[str, Any]) -> bool:
        """Check if this is an HYE-type strategy"""
        return (analysis.get('vwap_system', {}).get('components', {}).get('found', 0) > 0 and
                analysis.get('momentum_system', {}).get('indicators', {}).get('tsv', {}).get('found', 0) > 0)
    
    def _convert_hye_strategy(self, pine_code: str, strategy_name: str, 
                            analysis: Dict[str, Any]) -> ConversionResult:
        """Convert HYE-type strategy with dual logic system"""
        
        logger.info(f"Converting HYE-type strategy: {strategy_name}")
        
        # Extract parameters from analysis
        parameters = self._extract_hye_parameters(analysis)
        
        # Generate Python code
        python_code = self._generate_hye_python_code(strategy_name, parameters, analysis)
        
        # Create metadata
        metadata = StrategyMetadata(
            name=strategy_name
            description="AI-converted HYE Combo Market Strategy with dual logic system"
            parameters=parameters
        )
        
        return ConversionResult(
            success=True
            python_code=python_code
            parameters=parameters
            metadata=metadata
            analysis_used=analysis
        )
    
    def _extract_hye_parameters(self, analysis: Dict[str, Any]) -> List[StrategyParameter]:
        """Extract parameters for HYE strategy from AI analysis"""
        parameters = []
        
        # VWAP periods
        vwap_periods = analysis.get('vwap_system', {}).get('periods', {})
        if vwap_periods:
            parameters.extend([
                StrategyParameter(
                    name='small_vwap_period'
                    default=vwap_periods.get('small', 8)
                    min_val=1
                    max_val=50
                    description='Small VWAP Period'
                )
                StrategyParameter(
                    name='big_vwap_period'
                    default=vwap_periods.get('big', 10)
                    min_val=1
                    max_val=50
                    description='Big VWAP Period'
                )
                StrategyParameter(
                    name='mean_vwap_period'
                    default=vwap_periods.get('mean', 50)
                    min_val=10
                    max_val=200
                    description='Mean VWAP Period'
                )
            ])
        
        # RSI parameters
        parameters.extend([
            StrategyParameter(
                name='rsi_period'
                default=14
                min_val=2
                max_val=50
                description='RSI Period'
            )
            StrategyParameter(
                name='rsi_ema_period'
                default=3
                min_val=1
                max_val=20
                description='RSI EMA Smoothing Period'
            )
            StrategyParameter(
                name='rsi_buy_level'
                default=50
                min_val=1
                max_val=100
                description='Maximum RSI Level for Buy'
            )
        ])
        
        # Ichimoku parameters
        ichimoku_params = analysis.get('parameters', {}).get('ichimoku_periods', {})
        if ichimoku_params:
            parameters.extend([
                StrategyParameter(
                    name='slow_tenkan_period'
                    default=int(ichimoku_params.get('slowtenkansenPeriod', '9'))
                    min_val=1
                    max_val=50
                    description='Slow Tenkan Sen Period'
                )
                StrategyParameter(
                    name='slow_kijun_period'
                    default=int(ichimoku_params.get('slowkijunsenPeriod', '13'))
                    min_val=1
                    max_val=50
                    description='Slow Kijun Sen Period'
                )
                StrategyParameter(
                    name='fast_tenkan_period'
                    default=int(ichimoku_params.get('fasttenkansenPeriod', '3'))
                    min_val=1
                    max_val=20
                    description='Fast Tenkan Sen Period'
                )
                StrategyParameter(
                    name='fast_kijun_period'
                    default=int(ichimoku_params.get('fastkijunsenPeriod', '7'))
                    min_val=1
                    max_val=20
                    description='Fast Kijun Sen Period'
                )
            ])
        
        # Bollinger Bands
        bb_params = analysis.get('parameters', {}).get('bollinger_bands', {})
        if bb_params:
            parameters.extend([
                StrategyParameter(
                    name='bb_length'
                    default=int(bb_params.get('BBlength', '20'))
                    min_val=5
                    max_val=100
                    description='Bollinger Bands Length'
                )
                StrategyParameter(
                    name='bb_multiplier'
                    default=float(bb_params.get('BBmult', '2.0'))
                    min_val=1.0
                    max_val=5.0
                    description='Bollinger Bands Multiplier'
                )
            ])
        
        # TSV parameters
        tsv_params = analysis.get('parameters', {}).get('tsv_settings', {})
        if tsv_params:
            parameters.extend([
                StrategyParameter(
                    name='tsv_length'
                    default=int(tsv_params.get('tsvlength', '20'))
                    min_val=5
                    max_val=100
                    description='TSV Length'
                )
                StrategyParameter(
                    name='tsv_ema_period'
                    default=int(tsv_params.get('tsvemaperiod', '7'))
                    min_val=1
                    max_val=50
                    description='TSV EMA Period'
                )
            ])
        
        # Vidya parameters
        vidya_params = analysis.get('parameters', {}).get('vidya_settings', {})
        if vidya_params:
            parameters.append(
                StrategyParameter(
                    name='vidya_length'
                    default=int(vidya_params.get('length', '20'))
                    min_val=5
                    max_val=100
                    description='Vidya Length'
                )
            )
        
        # Risk management
        parameters.extend([
            StrategyParameter(
                name='percent_below_to_buy'
                default=2.0
                min_val=0.1
                max_val=10.0
                description='Percent below VWAP to trigger buy'
            )
        ])
        
        return parameters
    
    def _generate_hye_python_code(self, strategy_name: str, 
                                parameters: List[StrategyParameter], 
                                analysis: Dict[str, Any]) -> str:
        """Generate Python code for HYE strategy"""
        
        # Extract parameter defaults for code generation
        param_defaults = {p.name: p.default for p in parameters}
        
        python_code = f'''"""
AI-Converted HYE Combo Market Strategy
Converted from Pine Script using intelligent analysis

Strategy Type: Dual-logic system combining mean reversion and trend hunting
- Mean Reversion: VWAP-based entries when price is below VWAP
- Trend Hunting: Multi-indicator momentum system with TSV, Vidya, Ichimoku

Original Analysis: {len(analysis.get('conversion_roadmap', []))} conversion steps identified
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
import logging

# Import our intelligent indicator library
from research.intelligent_converter.indicator_library import IndicatorLibrary, PineScriptHelpers
from shared.types.strategy import StrategySignals, StrategyParameter, StrategyMetadata

logger = logging.getLogger(__name__)

class {strategy_name.replace(' ', '').replace('-', '')}Strategy:
    """AI-Converted HYE Combo Market Strategy"""
    
    def __init__(self):
        self.name = "{strategy_name}"
        self.description = "Dual-logic strategy: VWAP mean reversion + momentum trend hunting"
        self.indicators = IndicatorLibrary()
        self.helpers = PineScriptHelpers()
    
    def get_parameters(self) -> List[StrategyParameter]:
        """Get strategy parameters"""
        return [
{self._generate_parameter_definitions(parameters)}
        ]
    
    def calculate_indicators(self, df: pd.DataFrame, params: Dict[str, Any]) -> Dict[str, pd.Series]:
        """Calculate all required indicators"""
        
        indicators = {{}}
        
        try:
            # 1. VWAP System (Mean Reversion)
            vwap_periods = {{
                'small': params.get('small_vwap_period', {param_defaults.get('small_vwap_period', 8)})
                'big': params.get('big_vwap_period', {param_defaults.get('big_vwap_period', 10)})
                'mean': params.get('mean_vwap_period', {param_defaults.get('mean_vwap_period', 50)})
            }}
            
            vwap_results = self.indicators.multi_period_vwap(df, vwap_periods)
            indicators['small_vwap'] = vwap_results['small'].values
            indicators['big_vwap'] = vwap_results['big'].values
            indicators['mean_vwap'] = vwap_results['mean'].values
            
            # Calculate buy threshold (percent below big VWAP)
            percent_below = params.get('percent_below_to_buy', {param_defaults.get('percent_below_to_buy', 2.0)})
            indicators['buy_threshold'] = indicators['big_vwap'] * (1 - percent_below / 100)
            
            # 2. RSI + EMA Smoothing
            rsi_result = self.indicators.rsi(df['close'], params.get('rsi_period', {param_defaults.get('rsi_period', 14)}))
            indicators['rsi'] = rsi_result.values
            
            rsi_ema_result = self.indicators.ema(indicators['rsi'], params.get('rsi_ema_period', {param_defaults.get('rsi_ema_period', 3)}))
            indicators['rsi_ema'] = rsi_ema_result.values
            
            # 3. TSV (Time Series Volume)
            tsv_result = self.indicators.tsv(df, params.get('tsv_length', {param_defaults.get('tsv_length', 20)}))
            indicators['tsv'] = tsv_result.values
            
            tsv_ema_result = self.indicators.ema(indicators['tsv'], params.get('tsv_ema_period', {param_defaults.get('tsv_ema_period', 7)}))
            indicators['tsv_ema'] = tsv_ema_result.values
            
            # 4. Vidya (Variable Index Dynamic Average)
            vidya_result = self.indicators.vidya(df['close'], params.get('vidya_length', {param_defaults.get('vidya_length', 20)}))
            indicators['vidya'] = vidya_result.values
            
            # 5. Ichimoku-style Components
            slow_ichimoku = self.indicators.ichimoku_components(
                df, 
                params.get('slow_tenkan_period', {param_defaults.get('slow_tenkan_period', 9)})
                params.get('slow_kijun_period', {param_defaults.get('slow_kijun_period', 13)})
            )
            indicators['slow_lead_line'] = slow_ichimoku['lead_line'].values
            
            fast_ichimoku = self.indicators.ichimoku_components(
                df
                params.get('fast_tenkan_period', {param_defaults.get('fast_tenkan_period', 3)})
                params.get('fast_kijun_period', {param_defaults.get('fast_kijun_period', 7)})
            )
            indicators['fast_lead_line'] = fast_ichimoku['lead_line'].values
            
            # 6. BB Lead Line (average of fast and slow lead lines)
            indicators['bb_lead_line'] = (indicators['fast_lead_line'] + indicators['slow_lead_line']) / 2
            
            # 7. Bollinger Bands on BB Lead Line
            bb_results = self.indicators.bollinger_bands(
                indicators['bb_lead_line']
                params.get('bb_length', {param_defaults.get('bb_length', 20)})
                params.get('bb_multiplier', {param_defaults.get('bb_multiplier', 2.0)})
            )
            indicators['bb_upper'] = bb_results['upper'].values
            indicators['bb_lower'] = bb_results['lower'].values
            indicators['bb_basis'] = bb_results['basis'].values
            
            return indicators
            
        except Exception as e:
            logger.error(f"Indicator calculation failed: {{e}}")
            return {{}}
    
    def generate_signals(self, df: pd.DataFrame, **params) -> StrategySignals:
        """Generate trading signals using dual-logic system"""
        
        # Calculate all indicators
        indicators = self.calculate_indicators(df, params)
        
        if not indicators:
            # Return empty signals if indicator calculation failed
            return StrategySignals(
                entries=pd.Series(False, index=df.index)
                exits=pd.Series(False, index=df.index)
            )
        
        # Initialize signal arrays
        long_entries = pd.Series(False, index=df.index)
        short_entries = pd.Series(False, index=df.index)
        long_exits = pd.Series(False, index=df.index)
        short_exits = pd.Series(False, index=df.index)
        
        # Get price data
        close = df['close']
        
        # Mean Reversion System Entry (BUY-M)
        # Condition: smallvwap crosses under buy_threshold AND rsi_ema < rsi_buy_level AND close < mean_vwap
        mean_reversion_entry = (
            self.helpers.crossunder(indicators['small_vwap'], indicators['buy_threshold']) &
            (indicators['rsi_ema'] < params.get('rsi_buy_level', {param_defaults.get('rsi_buy_level', 50)})) &
            (close < indicators['mean_vwap'])
        )
        
        # Mean Reversion System Exit
        # Condition: close > mean_vwap
        mean_reversion_exit = close > indicators['mean_vwap']
        
        # Trend Hunting System Entry (BUY-T)
        # Condition: fast_lead > fast_lead[1] AND slow_lead > slow_lead[1] AND tsv > 0 AND tsv > tsv_ema AND close > bb_upper AND close > vidya
        trend_hunting_entry = (
            (indicators['fast_lead_line'] > indicators['fast_lead_line'].shift(1)) &
            (indicators['slow_lead_line'] > indicators['slow_lead_line'].shift(1)) &
            (indicators['tsv'] > 0) &
            (indicators['tsv'] > indicators['tsv_ema']) &
            (close > indicators['bb_upper']) &
            (close > indicators['vidya'])
        )
        
        # Trend Hunting System Exit
        # Condition: (fast_lead < fast_lead[1] AND slow_lead < slow_lead[1])
        trend_hunting_exit = (
            (indicators['fast_lead_line'] < indicators['fast_lead_line'].shift(1)) &
            (indicators['slow_lead_line'] < indicators['slow_lead_line'].shift(1))
        )
        
        # Combine entry signals (either system can trigger)
        long_entries = mean_reversion_entry | trend_hunting_entry
        
        # Combine exit signals (either system can trigger)
        long_exits = mean_reversion_exit | trend_hunting_exit
        
        # No short signals for this strategy
        entries = long_entries
        exits = long_exits
        
        return StrategySignals(entries=entries, exits=exits)

# Strategy metadata
STRATEGY_NAME = "{strategy_name}"

PARAM_DEFINITIONS = [
{self._generate_parameter_definitions(parameters, indent="    ")}
]

def build_signals(df: pd.DataFrame, **params) -> StrategySignals:
    """Main entry point for strategy execution"""
    strategy = {strategy_name.replace(' ', '').replace('-', '')}Strategy()
    return strategy.generate_signals(df, **params)

METADATA = StrategyMetadata(
    name=STRATEGY_NAME
    description="AI-converted HYE Combo Market Strategy with dual logic system"
    parameters=PARAM_DEFINITIONS
)
'''
        
        return python_code
    
    def _generate_parameter_definitions(self, parameters: List[StrategyParameter], 
                                      indent: str = "            ") -> str:
        """Generate parameter definition code"""
        param_lines = []
        
        for param in parameters:
            param_line = f"""{indent}StrategyParameter(
{indent}    name='{param.name}'
{indent}    default={param.default}
{indent}    min_val={param.min_val}
{indent}    max_val={param.max_val}
{indent}    description='{param.description}'
{indent})"""
            param_lines.append(param_line)
        
        return ',\n'.join(param_lines)
    
    def _convert_general_strategy(self, pine_code: str, strategy_name: str
                                analysis: Dict[str, Any]) -> ConversionResult:
        """Convert general Pine Script strategy (non-HYE type)"""
        
        # For now, return a basic template
        # TODO: Implement general conversion logic
        
        python_code = f'''"""
AI-Converted Strategy: {strategy_name}
Basic template - requires manual refinement
"""

import pandas as pd
import numpy as np
from shared.types.strategy import StrategySignals, StrategyParameter, StrategyMetadata

def build_signals(df: pd.DataFrame, **params) -> StrategySignals:
    """Basic strategy template"""
    
    # Initialize empty signals
    entries = pd.Series(False, index=df.index)
    exits = pd.Series(False, index=df.index)
    
    # TODO: Implement strategy logic based on Pine Script analysis
    
    return StrategySignals(entries=entries, exits=exits)

METADATA = StrategyMetadata(
    name="{strategy_name}"
    description="AI-converted strategy (basic template)"
    parameters=[]
)
'''
        
        return ConversionResult(
            success=True
            python_code=python_code
            parameters=[]
            metadata=StrategyMetadata(
                name=strategy_name
                description="Basic converted strategy"
                parameters=[]
            )
        )

# Example usage and testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Test with HYE strategy
    hye_path = Path(__file__).parent.parent.parent / "examples" / "pine_scripts" / "hye.pine"
    
    if hye_path.exists():
        with open(hye_path, 'r') as f:
            hye_code = f.read()
        
        converter = IntelligentConverter()
        result = converter.convert_strategy(hye_code, "HYE Combo Strategy")
        
        if result.success:
            print("✅ Conversion successful!")
            print(f"Parameters found: {len(result.parameters)}")
            print(f"Code length: {len(result.python_code)} characters")
            
            # Save the converted strategy
            output_path = Path(__file__).parent / "output" / "hye_converted.py"
            output_path.parent.mkdir(exist_ok=True)
            
            with open(output_path, 'w') as f:
                f.write(result.python_code)
            
            print(f"💾 Saved converted strategy to: {output_path}")
        else:
            print(f"❌ Conversion failed: {result.error_message}")
    else:
        print("❌ HYE strategy file not found")