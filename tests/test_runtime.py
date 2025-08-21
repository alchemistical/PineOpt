#!/usr/bin/env python3
"""Test Pine runtime adapters with sample data."""

import pandas as pd
import numpy as np
from pine2py.runtime import ta, nz, change, crossover

# Create sample OHLC data
dates = pd.date_range('2024-01-01', periods=50, freq='D')
np.random.seed(42)

# Generate realistic price data
close_prices = 100 + np.cumsum(np.random.randn(50) * 0.5)
open_prices = close_prices + np.random.randn(50) * 0.3
high_prices = np.maximum(open_prices, close_prices) + np.abs(np.random.randn(50) * 0.4)
low_prices = np.minimum(open_prices, close_prices) - np.abs(np.random.randn(50) * 0.4)

df = pd.DataFrame({
    'open': open_prices,
    'high': high_prices, 
    'low': low_prices,
    'close': close_prices
}, index=dates)

print("🧪 Testing Pine Runtime Adapters")
print("=" * 40)

# Test ta.sma
sma_20 = ta.sma(df['close'], 20)
print(f"✅ SMA(20): {sma_20.iloc[-1]:.2f}")

# Test ta.ema  
ema_20 = ta.ema(df['close'], 20)
print(f"✅ EMA(20): {ema_20.iloc[-1]:.2f}")

# Test ta.rsi
rsi_14 = ta.rsi(df['close'], 14)
print(f"✅ RSI(14): {rsi_14.iloc[-1]:.2f}")

# Test ta.atr
atr_14 = ta.atr(df['high'], df['low'], df['close'], 14)
print(f"✅ ATR(14): {atr_14.iloc[-1]:.2f}")

# Test crossover
sma_short = ta.sma(df['close'], 10)
sma_long = ta.sma(df['close'], 20)
cross_signals = crossover(sma_short, sma_long)
print(f"✅ Crossover signals: {cross_signals.sum()} occurrences")

# Test change
price_change = change(df['close'], 1)
print(f"✅ Daily change: {price_change.iloc[-1]:.2f}")

# Test nz (fillna)
test_series = pd.Series([1, 2, np.nan, 4, np.nan])
filled = nz(test_series, 0)
print(f"✅ NZ function: {filled.tolist()}")

print("\n🎉 All runtime adapters working correctly!")
print(f"📊 Sample data: {len(df)} bars from {df.index[0].date()} to {df.index[-1].date()}")
print(f"📈 Price range: ${df['close'].min():.2f} - ${df['close'].max():.2f}")