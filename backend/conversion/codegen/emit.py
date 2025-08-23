"""Pine Script to Python code generation."""

from typing import Dict, Any, List
from datetime import datetime
import textwrap


class PythonCodeGenerator:
    """Generate Python code from Pine Script patterns."""
    
    def __init__(self):
        self.imports = set()
        self.parameters = {}
        self.variables = {}
        self.signals = {}
    
    def generate_strategy_module(self, 
                               strategy_name: str,
                               parameters: Dict[str, Any],
                               pine_logic: str) -> str:
        """Generate complete Python strategy module."""
        
        # Standard imports
        code_parts = [
            "# Generated from Pine Script",
            f"# Conversion date: {datetime.now().isoformat()}",
            "",
            "import pandas as pd",
            "import numpy as np", 
            "from pine2py.runtime import ta, nz, change, crossover, crossunder",
            "from shared.types.strategy import StrategySignals, StrategyParameter, StrategyMetadata",
            "",
            f'STRATEGY_NAME = "{strategy_name}"',
            "",
            "# Strategy Parameters",
            self._generate_parameters(parameters),
            "",
            "def build_signals(df: pd.DataFrame, **params) -> StrategySignals:",
            "    \"\"\"Build trading signals from OHLC data.\"\"\"",
            "    ",
            "    # Extract OHLC series",
            "    open_prices = df['open']",
            "    high_prices = df['high']", 
            "    low_prices = df['low']",
            "    close_prices = df['close']",
            "    ",
            "    # Apply parameter defaults",
            "    final_params = PARAMS.copy()",
            "    final_params.update(params)",
            "    ",
            self._generate_logic(pine_logic),
            "    ",
            "    return StrategySignals(",
            "        entries=long_entries | short_entries,",
            "        exits=long_exits | short_exits",
            "    )",
            "",
            "# Strategy metadata",
            "METADATA = StrategyMetadata(",
            f"    name='{strategy_name}',",
            "    parameters=PARAM_DEFINITIONS",
            ")"
        ]
        
        return "\n".join(code_parts)
    
    def _generate_parameters(self, params: Dict[str, Any]) -> str:
        """Generate parameter definitions."""
        param_lines = ["PARAMS = {"]
        param_def_lines = ["PARAM_DEFINITIONS = ["]
        
        for name, config in params.items():
            default = config.get('default', 0)
            param_lines.append(f"    '{name}': {default},")
            
            param_def_lines.append(f"    StrategyParameter(")
            param_def_lines.append(f"        name='{name}',")
            param_def_lines.append(f"        default={default},")
            if 'min' in config:
                param_def_lines.append(f"        min_val={config['min']},")
            if 'max' in config:
                param_def_lines.append(f"        max_val={config['max']},")
            if 'title' in config:
                param_def_lines.append(f"        description='{config['title']}',")
            param_def_lines.append(f"    ),")
        
        param_lines.append("}")
        param_def_lines.append("]")
        
        return "\n".join(param_lines + [""] + param_def_lines)
    
    def _generate_logic(self, pine_logic: str) -> str:
        """Generate Python logic from Pine patterns."""
        # This is a simple pattern-based converter for MVP
        python_lines = [
            "    # Initialize signals",
            "    long_entries = pd.Series(False, index=df.index)",
            "    short_entries = pd.Series(False, index=df.index)", 
            "    long_exits = pd.Series(False, index=df.index)",
            "    short_exits = pd.Series(False, index=df.index)",
            "    ",
            "    # Convert Pine logic to Python",
        ]
        
        # Basic pattern matching for common Pine patterns
        if "ta.rsi" in pine_logic:
            python_lines.extend([
                "    rsi_length = final_params.get('rsi_length', 14)",
                "    rsi_value = ta.rsi(close_prices, rsi_length)",
            ])
        
        if "ta.crossover" in pine_logic and "rsi_value" in pine_logic:
            python_lines.extend([
                "    rsi_oversold = final_params.get('rsi_oversold', 30)",
                "    long_entries = crossover(rsi_value, rsi_oversold)",
            ])
        
        if "ta.crossunder" in pine_logic and "rsi_value" in pine_logic:
            python_lines.extend([
                "    rsi_overbought = final_params.get('rsi_overbought', 70)",
                "    short_entries = crossunder(rsi_value, rsi_overbought)",
            ])
        
        return "\n".join(python_lines)


def convert_simple_rsi_strategy() -> str:
    """Generate a simple RSI strategy for testing."""
    generator = PythonCodeGenerator()
    
    parameters = {
        'rsi_length': {'default': 14, 'min': 1, 'max': 100, 'title': 'RSI Length'},
        'rsi_overbought': {'default': 70.0, 'min': 50, 'max': 100, 'title': 'RSI Overbought'},
        'rsi_oversold': {'default': 30.0, 'min': 0, 'max': 50, 'title': 'RSI Oversold'}
    }
    
    pine_logic = '''
    rsi_value = ta.rsi(close, rsi_length)
    long_condition = ta.crossover(rsi_value, rsi_oversold)
    short_condition = ta.crossunder(rsi_value, rsi_overbought)
    '''
    
    return generator.generate_strategy_module(
        strategy_name="Simple RSI Strategy",
        parameters=parameters,
        pine_logic=pine_logic
    )