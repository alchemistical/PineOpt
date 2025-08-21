"""Pine Script technical analysis function adapters."""

import pandas as pd
import numpy as np
from typing import Optional, Union


def sma(series: pd.Series, length: int) -> pd.Series:
    """Pine ta.sma() - Simple Moving Average."""
    return series.rolling(window=length, min_periods=1).mean()


def ema(series: pd.Series, length: int) -> pd.Series:
    """Pine ta.ema() - Exponential Moving Average."""
    return series.ewm(span=length, adjust=False).mean()


def rsi(series: pd.Series, length: int = 14) -> pd.Series:
    """Pine ta.rsi() - Relative Strength Index."""
    delta = series.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    
    avg_gain = gain.ewm(span=length, adjust=False).mean()
    avg_loss = loss.ewm(span=length, adjust=False).mean()
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def stdev(series: pd.Series, length: int) -> pd.Series:
    """Pine ta.stdev() - Standard Deviation."""
    return series.rolling(window=length, min_periods=1).std()


def atr(high: pd.Series, low: pd.Series, close: pd.Series, length: int = 14) -> pd.Series:
    """Pine ta.atr() - Average True Range."""
    tr1 = high - low
    tr2 = (high - close.shift(1)).abs()
    tr3 = (low - close.shift(1)).abs()
    
    true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    return true_range.ewm(span=length, adjust=False).mean()


def highest(series: pd.Series, length: int) -> pd.Series:
    """Pine ta.highest() - Highest value over length."""
    return series.rolling(window=length, min_periods=1).max()


def lowest(series: pd.Series, length: int) -> pd.Series:
    """Pine ta.lowest() - Lowest value over length."""
    return series.rolling(window=length, min_periods=1).min()


def crossover(series1: pd.Series, series2: pd.Series) -> pd.Series:
    """Pine ta.crossover() - series1 crosses above series2."""
    current = series1 > series2
    previous = series1.shift(1) <= series2.shift(1)
    return current & previous


def crossunder(series1: pd.Series, series2: pd.Series) -> pd.Series:
    """Pine ta.crossunder() - series1 crosses below series2."""
    current = series1 < series2  
    previous = series1.shift(1) >= series2.shift(1)
    return current & previous


def cross(series1: pd.Series, series2: pd.Series) -> pd.Series:
    """Pine ta.cross() - series1 crosses series2 in either direction."""
    return crossover(series1, series2) | crossunder(series1, series2)


def wma(series: pd.Series, length: int) -> pd.Series:
    """Pine ta.wma() - Weighted Moving Average."""
    weights = np.arange(1, length + 1)
    
    def weighted_mean(x):
        if len(x) < length:
            return np.nan
        return np.average(x[-length:], weights=weights)
    
    return series.rolling(window=length, min_periods=length).apply(weighted_mean, raw=True)


def rma(series: pd.Series, length: int) -> pd.Series:
    """Pine ta.rma() - Running Moving Average (Wilder's smoothing)."""
    alpha = 1.0 / length
    return series.ewm(alpha=alpha, adjust=False).mean()


def macd(series: pd.Series, fast_length: int = 12, slow_length: int = 26, signal_length: int = 9):
    """Pine ta.macd() - MACD indicator."""
    fast_ema = ema(series, fast_length)
    slow_ema = ema(series, slow_length)
    macd_line = fast_ema - slow_ema
    signal_line = ema(macd_line, signal_length)
    histogram = macd_line - signal_line
    
    return macd_line, signal_line, histogram


def bb(series: pd.Series, length: int = 20, mult: float = 2.0):
    """Pine ta.bb() - Bollinger Bands."""
    basis = sma(series, length)
    dev = stdev(series, length) * mult
    upper = basis + dev
    lower = basis - dev
    
    return basis, upper, lower


def bbw(series: pd.Series, length: int = 20, mult: float = 2.0) -> pd.Series:
    """Pine ta.bbw() - Bollinger Bands Width."""
    basis, upper, lower = bb(series, length, mult)
    return (upper - lower) / basis


def percent_b(series: pd.Series, length: int = 20, mult: float = 2.0) -> pd.Series:
    """Calculate %B (position within Bollinger Bands)."""
    basis, upper, lower = bb(series, length, mult)
    return (series - lower) / (upper - lower)


def donchian(high: pd.Series, low: pd.Series, length: int = 20):
    """Donchian Channels - highest high and lowest low."""
    upper = highest(high, length)
    lower = lowest(low, length)
    basis = (upper + lower) / 2
    return basis, upper, lower