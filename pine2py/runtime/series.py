"""Pine Script series operations adapted for pandas."""

import pandas as pd
import numpy as np
from typing import Union, Optional


def nz(series: pd.Series, replacement: Union[float, int] = 0) -> pd.Series:
    """Pine nz() function - replace NaN values."""
    return series.fillna(replacement)


def na(series: pd.Series) -> pd.Series:
    """Pine na() function - check for NaN values."""
    return series.isna()


def change(series: pd.Series, length: int = 1) -> pd.Series:
    """Pine change() function - difference from N bars ago."""
    return series - series.shift(length)


def crossover(series1: pd.Series, series2: pd.Series) -> pd.Series:
    """Pine crossover() - series1 crosses above series2."""
    current = series1 > series2
    previous = series1.shift(1) <= series2.shift(1)
    return current & previous


def crossunder(series1: pd.Series, series2: pd.Series) -> pd.Series:
    """Pine crossunder() - series1 crosses below series2."""
    current = series1 < series2
    previous = series1.shift(1) >= series2.shift(1)
    return current & previous


def cross(series1: pd.Series, series2: pd.Series) -> pd.Series:
    """Pine cross() - series1 crosses series2 in either direction."""
    return crossover(series1, series2) | crossunder(series1, series2)


def highest(series: pd.Series, length: int) -> pd.Series:
    """Pine highest() - highest value in last N bars."""
    return series.rolling(window=length, min_periods=1).max()


def lowest(series: pd.Series, length: int) -> pd.Series:
    """Pine lowest() - lowest value in last N bars."""
    return series.rolling(window=length, min_periods=1).min()


def valuewhen(condition: pd.Series, source: pd.Series, occurrence: int = 0) -> pd.Series:
    """Pine valuewhen() - value when condition was true N occurrences ago."""
    # Find indices where condition is True
    true_indices = condition[condition].index
    
    if len(true_indices) == 0:
        return pd.Series(np.nan, index=source.index)
    
    result = pd.Series(np.nan, index=source.index)
    
    for i, idx in enumerate(source.index):
        # Find the occurrence-th true condition before current index
        prior_trues = true_indices[true_indices <= idx]
        if len(prior_trues) > occurrence:
            value_idx = prior_trues[-(occurrence + 1)]
            result.iloc[i] = source.loc[value_idx]
    
    return result


def barssince(condition: pd.Series) -> pd.Series:
    """Pine barssince() - bars since condition was true."""
    result = pd.Series(np.nan, index=condition.index)
    bars_count = 0
    
    for i, (idx, val) in enumerate(condition.items()):
        if val:
            bars_count = 0
        else:
            bars_count += 1
        result.iloc[i] = bars_count
    
    return result


def pine_max(val1: Union[pd.Series, float], val2: Union[pd.Series, float]) -> pd.Series:
    """Pine math.max() function."""
    return np.maximum(val1, val2)


def pine_min(val1: Union[pd.Series, float], val2: Union[pd.Series, float]) -> pd.Series:
    """Pine math.min() function."""
    return np.minimum(val1, val2)


def pine_abs(series: pd.Series) -> pd.Series:
    """Pine math.abs() function.""" 
    return series.abs()


def pine_sum(series: pd.Series, length: int) -> pd.Series:
    """Pine math.sum() function - rolling sum."""
    return series.rolling(window=length, min_periods=1).sum()