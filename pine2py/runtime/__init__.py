"""Pine Script runtime adapters for pandas operations."""

# Import all series operations
from .series import (
    nz, na, change, crossover, crossunder, cross,
    highest, lowest, valuewhen, barssince,
    pine_max, pine_min, pine_abs, pine_sum
)

# Import all technical analysis functions
from .ta_adapters import (
    sma, ema, rsi, stdev, atr,
    wma, rma, macd, bb, bbw, percent_b,
    donchian
)

# Create ta namespace for compatibility
class TANamespace:
    """Technical analysis namespace to match Pine ta.* calls."""
    
    # Moving averages
    sma = staticmethod(sma)
    ema = staticmethod(ema)  
    wma = staticmethod(wma)
    rma = staticmethod(rma)
    
    # Oscillators
    rsi = staticmethod(rsi)
    macd = staticmethod(macd)
    
    # Volatility
    stdev = staticmethod(stdev)
    atr = staticmethod(atr)
    bb = staticmethod(bb)
    bbw = staticmethod(bbw)
    
    # Price levels
    highest = staticmethod(highest)
    lowest = staticmethod(lowest)
    donchian = staticmethod(donchian)
    
    # Crossovers
    crossover = staticmethod(crossover)
    crossunder = staticmethod(crossunder)
    cross = staticmethod(cross)


# Create ta instance
ta = TANamespace()

# Create math namespace for Pine math.* functions
class MathNamespace:
    """Math namespace to match Pine math.* calls."""
    
    max = staticmethod(pine_max)
    min = staticmethod(pine_min)
    abs = staticmethod(pine_abs)
    sum = staticmethod(pine_sum)


# Create math instance  
math = MathNamespace()

__all__ = [
    'nz', 'na', 'change', 'crossover', 'crossunder', 'cross',
    'highest', 'lowest', 'valuewhen', 'barssince',
    'ta', 'math'
]