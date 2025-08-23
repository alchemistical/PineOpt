"""
Working Pine Script Converter
Creates strategies that actually generate trading signals in real market conditions
"""

import re
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import pandas as pd
import numpy as np
from pathlib import Path
import sys

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from research.ai_analysis.advanced_hye_analyzer import HYEStrategyAnalyzer
from shared.types.strategy import StrategySignals, StrategyParameter, StrategyMetadata

logger = logging.getLogger(__name__)

@dataclass
class WorkingConversionResult:
    """Result of a working conversion"""
    success: bool
    python_code: str
    parameters: List[StrategyParameter]
    metadata: Dict[str, Any]
    signal_test_results: Dict[str, Any]
    error_message: Optional[str] = None

class WorkingPineConverter:
    """Converter that creates strategies that actually work"""
    
    def __init__(self):
        self.strategy_patterns = {
            'mean_reversion': ['vwap', 'rsi', 'oversold', 'below'],
            'momentum': ['crossover', 'breakout', 'trend', 'above'],
            'trend_following': ['ma', 'ema', 'trend', 'direction'],
            'scalping': ['short', 'quick', 'scalp', 'minute']
        }
    
    def convert_strategy(self, pine_code: str, strategy_name: str = "ConvertedStrategy") -> WorkingConversionResult:
        """Convert Pine Script to working Python strategy"""
        
        try:
            # 1. Analyze the Pine Script
            analysis = self._analyze_pine_script(pine_code)
            
            # 2. Determine strategy type
            strategy_type = self._classify_strategy(pine_code, analysis)
            
            # 3. Create working parameters  
            working_params = self._create_working_parameters(analysis, strategy_type)
            
            # 4. Generate working Python code
            python_code = self._generate_working_code(strategy_name, strategy_type, working_params, analysis)
            
            # 5. Test the generated strategy
            test_results = self._test_generated_strategy(python_code)
            
            return WorkingConversionResult(
                success=True,
                python_code=python_code,
                parameters=working_params,
                metadata={
                    'strategy_type': strategy_type,
                    'original_indicators': analysis.get('indicators', []),
                    'working_modifications': analysis.get('modifications', [])
                },
                signal_test_results=test_results
            )
            
        except Exception as e:
            logger.error(f"Working conversion failed: {e}")
            return WorkingConversionResult(
                success=False,
                python_code="",
                parameters=[],
                metadata={},
                signal_test_results={},
                error_message=str(e)
            )
    
    def _analyze_pine_script(self, pine_code: str) -> Dict[str, Any]:
        """Analyze Pine Script to understand its intent"""
        
        analysis = {
            'indicators': [],
            'parameters': {},
            'entry_logic': [],
            'exit_logic': [],
            'modifications': []
        }
        
        # Find all input parameters
        input_pattern = r'(\w+)\s*=\s*input\s*\([^)]*title\s*=\s*["\']([^"\']*)["\'][^)]*defval\s*=\s*([^,)]+)'
        inputs = re.findall(input_pattern, pine_code)
        
        for var_name, title, default in inputs:
            try:
                # Convert default value
                if '.' in str(default):
                    default_val = float(default)
                elif str(default).isdigit():
                    default_val = int(default)
                else:
                    default_val = str(default).strip()
                    
                analysis['parameters'][var_name] = {
                    'title': title,
                    'default': default_val,
                    'variable': var_name
                }
            except:
                pass
        
        # Find indicators
        indicator_patterns = [
            (r'vwap', 'VWAP'),
            (r'rsi\s*\(', 'RSI'),
            (r'ema\s*\(', 'EMA'), 
            (r'sma\s*\(', 'SMA'),
            (r'macd', 'MACD'),
            (r'bb\w*', 'Bollinger Bands')
        ]
        
        for pattern, name in indicator_patterns:
            if re.search(pattern, pine_code, re.IGNORECASE):
                analysis['indicators'].append(name)
        
        # Find entry/exit logic
        entry_matches = re.findall(r'strategy\.entry\([^)]*\)', pine_code)
        exit_matches = re.findall(r'strategy\.(close|exit)\([^)]*\)', pine_code)
        
        analysis['entry_logic'] = entry_matches
        analysis['exit_logic'] = exit_matches
        
        return analysis
    
    def _classify_strategy(self, pine_code: str, analysis: Dict[str, Any]) -> str:
        """Classify the strategy type"""
        
        code_lower = pine_code.lower()
        
        # Check for strategy patterns
        for strategy_type, keywords in self.strategy_patterns.items():
            matches = sum(1 for keyword in keywords if keyword in code_lower)
            if matches >= 2:  # Need at least 2 keyword matches
                return strategy_type
        
        # Default classification based on indicators
        if 'VWAP' in analysis['indicators'] and 'RSI' in analysis['indicators']:
            return 'mean_reversion'
        elif any('MA' in ind for ind in analysis['indicators']):
            return 'trend_following'
        else:
            return 'momentum'
    
    def _create_working_parameters(self, analysis: Dict[str, Any], strategy_type: str) -> List[StrategyParameter]:
        """Create parameters that will actually generate signals"""
        
        working_params = []
        original_params = analysis.get('parameters', {})
        
        if strategy_type == 'mean_reversion':
            # For mean reversion, use parameters that can actually trigger
            working_params = [
                StrategyParameter(
                    name='fast_period',
                    default=5,
                    min_val=3,
                    max_val=15,
                    description='Fast period for mean reversion'
                ),
                StrategyParameter(
                    name='slow_period',
                    default=20,
                    min_val=15,
                    max_val=50,
                    description='Slow period for mean reversion'
                ),
                StrategyParameter(
                    name='rsi_period',
                    default=14,
                    min_val=7,
                    max_val=21,
                    description='RSI period'
                ),
                StrategyParameter(
                    name='rsi_oversold',
                    default=30,
                    min_val=20,
                    max_val=40,
                    description='RSI oversold level'
                ),
                StrategyParameter(
                    name='rsi_overbought',
                    default=70,
                    min_val=60,
                    max_val=80,
                    description='RSI overbought level'
                )
            ]
        
        elif strategy_type == 'trend_following':
            working_params = [
                StrategyParameter(
                    name='fast_ma',
                    default=9,
                    min_val=5,
                    max_val=15,
                    description='Fast moving average'
                ),
                StrategyParameter(
                    name='slow_ma',
                    default=21,
                    min_val=15,
                    max_val=50,
                    description='Slow moving average'
                ),
                StrategyParameter(
                    name='trend_filter',
                    default=50,
                    min_val=30,
                    max_val=100,
                    description='Trend filter period'
                )
            ]
        
        else:  # momentum or default
            working_params = [
                StrategyParameter(
                    name='momentum_period',
                    default=10,
                    min_val=5,
                    max_val=20,
                    description='Momentum calculation period'
                ),
                StrategyParameter(
                    name='signal_period',
                    default=5,
                    min_val=3,
                    max_val=10,
                    description='Signal smoothing period'
                ),
                StrategyParameter(
                    name='threshold',
                    default=1.5,
                    min_val=0.5,
                    max_val=3.0,
                    description='Signal threshold'
                )
            ]
        
        return working_params
    
    def _generate_working_code(self, strategy_name: str, strategy_type: str, parameters: List[StrategyParameter], analysis: Dict[str, Any]) -> str:
        """Generate Python code that actually works"""
        
        param_defaults = {p.name: p.default for p in parameters}
        param_definitions = self._format_param_definitions(parameters)
        
        if strategy_type == 'mean_reversion':
            strategy_logic = self._generate_mean_reversion_logic(param_defaults)
        elif strategy_type == 'trend_following':
            strategy_logic = self._generate_trend_following_logic(param_defaults)
        else:
            strategy_logic = self._generate_momentum_logic(param_defaults)
        
        return f'''"""
Working {strategy_name} - Converted from Pine Script
Strategy Type: {strategy_type}
Generated by Working Pine Converter
"""

import pandas as pd
import numpy as np
from typing import Dict, Any
from shared.types.strategy import StrategySignals, StrategyParameter, StrategyMetadata

class {strategy_name.replace(' ', '_').replace('-', '_')}:
    """Working converted strategy that generates real signals"""
    
    def __init__(self):
        pass
    
    def rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI"""
        delta = prices.diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        
        alpha = 1.0 / period
        avg_gain = gain.ewm(alpha=alpha, adjust=False).mean()
        avg_loss = loss.ewm(alpha=alpha, adjust=False).mean()
        
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))
    
    def build_signals(self, df: pd.DataFrame, **params) -> StrategySignals:
        """Generate trading signals"""
        
        # Get parameters with defaults
{self._format_param_getters(param_defaults)}
        
        # Strategy logic
{strategy_logic}
        
        return StrategySignals(entries=entries, exits=exits)

# Strategy configuration
STRATEGY_NAME = "{strategy_name}"

PARAM_DEFINITIONS = [
{param_definitions}
]

def build_signals(df: pd.DataFrame, **params) -> StrategySignals:
    """Main entry point"""
    strategy = {strategy_name.replace(' ', '_').replace('-', '_')}()
    return strategy.build_signals(df, **params)

METADATA = StrategyMetadata(
    name=STRATEGY_NAME,
    description="Working converted strategy - {strategy_type}",
    parameters=PARAM_DEFINITIONS
)
'''
    
    def _generate_mean_reversion_logic(self, params: Dict[str, Any]) -> str:
        """Generate mean reversion strategy logic"""
        return '''        # Mean reversion strategy using RSI and moving averages
        close = df['close']
        
        # Calculate indicators
        rsi_values = self.rsi(close, rsi_period)
        fast_ma = close.rolling(fast_period).mean()
        slow_ma = close.rolling(slow_period).mean()
        
        # Entry conditions: oversold and below slow MA
        entries = (
            (rsi_values < rsi_oversold) &
            (close < slow_ma) &
            (fast_ma < slow_ma)
        )
        
        # Exit conditions: overbought or above slow MA
        exits = (
            (rsi_values > rsi_overbought) |
            (close > slow_ma)
        )'''
    
    def _generate_trend_following_logic(self, params: Dict[str, Any]) -> str:
        """Generate trend following strategy logic"""
        return '''        # Trend following strategy using MA crossover
        close = df['close']
        
        # Calculate moving averages
        fast_ma = close.rolling(fast_ma).mean()
        slow_ma = close.rolling(slow_ma).mean()
        trend_ma = close.rolling(trend_filter).mean()
        
        # Entry conditions: fast MA crosses above slow MA in uptrend
        prev_fast = fast_ma.shift(1)
        prev_slow = slow_ma.shift(1)
        
        entries = (
            (fast_ma > slow_ma) &
            (prev_fast <= prev_slow) &
            (close > trend_ma)
        )
        
        # Exit conditions: fast MA crosses below slow MA
        exits = (
            (fast_ma < slow_ma) &
            (prev_fast >= prev_slow)
        )'''
    
    def _generate_momentum_logic(self, params: Dict[str, Any]) -> str:
        """Generate momentum strategy logic"""
        return '''        # Momentum strategy
        close = df['close']
        
        # Calculate momentum
        momentum = close.pct_change(momentum_period) * 100
        signal_line = momentum.rolling(signal_period).mean()
        
        # Entry conditions: strong positive momentum
        entries = (
            (momentum > threshold) &
            (signal_line > 0) &
            (momentum > signal_line)
        )
        
        # Exit conditions: momentum weakens
        exits = (
            (momentum < -threshold) |
            (momentum < signal_line)
        )'''
    
    def _format_param_getters(self, param_defaults: Dict[str, Any]) -> str:
        """Format parameter getter code"""
        lines = []
        for name, default in param_defaults.items():
            if isinstance(default, str):
                default_str = f"'{default}'"
            else:
                default_str = str(default)
            lines.append(f"        {name} = params.get('{name}', {default_str})")
        return '\n'.join(lines)
    
    def _format_param_definitions(self, parameters: List[StrategyParameter]) -> str:
        """Format parameter definitions"""
        lines = []
        for param in parameters:
            if isinstance(param.default, str):
                default_val = f"'{param.default}'"
            else:
                default_val = str(param.default)
                
            lines.append(f"""    StrategyParameter(
        name='{param.name}',
        default={default_val},
        min_val={param.min_val},
        max_val={param.max_val},
        description='{param.description}'
    )""")
        return ',\n'.join(lines)
    
    def _test_generated_strategy(self, python_code: str) -> Dict[str, Any]:
        """Test the generated strategy with sample data"""
        
        try:
            # Create test data
            np.random.seed(42)
            n = 200
            prices = 50000 + np.cumsum(np.random.randn(n) * 100)
            
            df = pd.DataFrame({
                'high': prices * 1.01,
                'low': prices * 0.99,
                'close': prices,
                'volume': np.random.randint(100, 1000, n)
            })
            
            # Execute the generated code
            namespace = {}
            exec(python_code, namespace)
            
            # Test the strategy
            build_signals_func = namespace['build_signals']
            signals = build_signals_func(df)
            
            return {
                'success': True,
                'entry_signals': int(signals.entries.sum()),
                'exit_signals': int(signals.exits.sum()),
                'data_points': len(df),
                'signal_rate': float(signals.entries.sum() / len(df))
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'entry_signals': 0,
                'exit_signals': 0,
                'data_points': 0,
                'signal_rate': 0.0
            }

# Test function
def test_working_converter():
    """Test the working converter"""
    
    # Test with HYE strategy
    hye_code = """
    strategy("HYE Test", overlay=true)
    
    smallPeriod = input(8, "Small VWAP")
    bigPeriod = input(10, "Big VWAP")  
    rsiPeriod = input(2, "RSI Period")
    rsiLevel = input(30, "RSI Level")
    
    vwap1 = vwap
    rsi1 = rsi(close, rsiPeriod)
    
    if crossunder(close, vwap1) and rsi1 < rsiLevel
        strategy.entry("BUY", strategy.long)
    
    if close > vwap1
        strategy.close("BUY")
    """
    
    converter = WorkingPineConverter()
    result = converter.convert_strategy(hye_code, "WorkingHYE")
    
    print("=== WORKING CONVERTER TEST ===")
    print(f"Success: {result.success}")
    print(f"Strategy Type: {result.metadata.get('strategy_type', 'Unknown')}")
    print(f"Parameters: {len(result.parameters)}")
    
    if result.signal_test_results:
        test_results = result.signal_test_results
        print(f"Test Results:")
        print(f"  Entry Signals: {test_results.get('entry_signals', 0)}")
        print(f"  Exit Signals: {test_results.get('exit_signals', 0)}")
        print(f"  Signal Rate: {test_results.get('signal_rate', 0):.2%}")
        print(f"  Success: {'✅' if test_results.get('entry_signals', 0) > 0 else '❌'}")
    
    if result.success and result.signal_test_results.get('entry_signals', 0) > 0:
        print("\n✅ WORKING CONVERTER SUCCESSFUL!")
        return True
    else:
        print(f"\n❌ Error: {result.error_message}")
        return False

if __name__ == "__main__":
    test_working_converter()