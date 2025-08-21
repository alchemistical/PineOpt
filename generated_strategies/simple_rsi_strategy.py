# Generated from Pine Script
# Conversion date: 2025-08-21T18:44:25.474408

import pandas as pd
import numpy as np
from pine2py.runtime import ta, nz, change, crossover, crossunder
from shared.types.strategy import StrategySignals, StrategyParameter, StrategyMetadata

STRATEGY_NAME = "Simple RSI Strategy"

# Strategy Parameters
PARAMS = {
    'rsi_length': 14,
    'rsi_overbought': 70.0,
    'rsi_oversold': 30.0,
}

PARAM_DEFINITIONS = [
    StrategyParameter(
        name='rsi_length',
        default=14,
        min_val=1,
        max_val=100,
        description='RSI Length',
    ),
    StrategyParameter(
        name='rsi_overbought',
        default=70.0,
        min_val=50,
        max_val=100,
        description='RSI Overbought',
    ),
    StrategyParameter(
        name='rsi_oversold',
        default=30.0,
        min_val=0,
        max_val=50,
        description='RSI Oversold',
    ),
]

def build_signals(df: pd.DataFrame, **params) -> StrategySignals:
    """Build trading signals from OHLC data."""
    
    # Extract OHLC series
    open_prices = df['open']
    high_prices = df['high']
    low_prices = df['low']
    close_prices = df['close']
    
    # Apply parameter defaults
    final_params = PARAMS.copy()
    final_params.update(params)
    
    # Initialize signals
    long_entries = pd.Series(False, index=df.index)
    short_entries = pd.Series(False, index=df.index)
    long_exits = pd.Series(False, index=df.index)
    short_exits = pd.Series(False, index=df.index)
    
    # Convert Pine logic to Python
    rsi_length = final_params.get('rsi_length', 14)
    rsi_value = ta.rsi(close_prices, rsi_length)
    rsi_oversold = final_params.get('rsi_oversold', 30)
    long_entries = crossover(rsi_value, rsi_oversold)
    rsi_overbought = final_params.get('rsi_overbought', 70)
    short_entries = crossunder(rsi_value, rsi_overbought)
    
    return StrategySignals(
        entries=long_entries | short_entries,
        exits=long_exits | short_exits
    )

# Strategy metadata
METADATA = StrategyMetadata(
    name='Simple RSI Strategy',
    parameters=PARAM_DEFINITIONS
)