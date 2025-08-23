#!/usr/bin/env python3
"""Simple test of HYE strategy with synthetic data"""

import sys
sys.path.append('.')
import pandas as pd
import numpy as np

def test_hye_strategy_simple():
    """Test HYE strategy with synthetic market data"""
    print("🚀 Testing HYE Strategy with Synthetic Data")
    
    # Load the HYE strategy
    exec(open('hye_strategy_implementation.py').read(), globals())
    
    # Create realistic synthetic OHLCV data
    print("📊 Creating synthetic market data...")
    
    np.random.seed(42)
    n_periods = 1000
    
    # Generate price series with trend and volatility
    base_price = 50000  # Starting price like BTC
    
    # Generate returns with some autocorrelation (trending behavior)
    returns = np.random.randn(n_periods) * 0.02  # 2% daily volatility
    trend = np.sin(np.linspace(0, 4*np.pi, n_periods)) * 0.001  # Gentle sine wave trend
    returns += trend
    
    # Create cumulative price
    prices = base_price * (1 + returns).cumprod()
    
    # Generate OHLC data
    data = []
    for i in range(n_periods):
        close_price = prices[i]
        
        # Generate realistic OHLC around close
        volatility = abs(returns[i]) * close_price
        high = close_price + volatility * np.random.uniform(0, 1)
        low = close_price - volatility * np.random.uniform(0, 1)
        
        if i == 0:
            open_price = base_price
        else:
            open_price = prices[i-1] * (1 + np.random.randn() * 0.005)  # Gap
        
        # Ensure OHLC relationships
        high = max(high, open_price, close_price)
        low = min(low, open_price, close_price)
        
        volume = int(np.random.lognormal(10, 0.5))  # Lognormal volume
        
        data.append({
            'open': open_price,
            'high': high,
            'low': low,
            'close': close_price,
            'volume': volume
        })
    
    # Create DataFrame
    dates = pd.date_range('2024-01-01', periods=n_periods, freq='1h')
    df = pd.DataFrame(data, index=dates)
    
    print(f"✅ Created {len(df)} bars of synthetic data")
    print(f"Price range: ${df['close'].min():.0f} - ${df['close'].max():.0f}")
    print(f"Date range: {df.index[0]} to {df.index[-1]}")
    
    # Test signal generation
    print("\n🔍 Testing signal generation...")
    signals = build_signals(df)
    
    entry_count = signals.entries.sum()
    exit_count = signals.exits.sum()
    print(f"✅ Generated {entry_count} entry signals and {exit_count} exit signals")
    
    # Analyze signals
    entry_dates = df.index[signals.entries]
    exit_dates = df.index[signals.exits]
    
    print(f"\n📈 Signal Analysis:")
    print(f"Entry rate: {entry_count / len(df):.2%}")
    print(f"Exit rate: {exit_count / len(df):.2%}")
    
    if entry_count > 0:
        print(f"First entry: {entry_dates[0]}")
        print(f"Last entry: {entry_dates[-1]}")
        
        # Show entry prices
        entry_prices = df.loc[signals.entries, 'close']
        print(f"Entry price range: ${entry_prices.min():.0f} - ${entry_prices.max():.0f}")
        
        # Simple performance calculation
        if exit_count > 0:
            # Match entries and exits
            trades = []
            position = False
            entry_price = None
            
            for i in range(len(df)):
                if signals.entries.iloc[i] and not position:
                    entry_price = df.iloc[i]['close']
                    position = True
                elif signals.exits.iloc[i] and position:
                    exit_price = df.iloc[i]['close']
                    return_pct = (exit_price - entry_price) / entry_price
                    trades.append(return_pct)
                    position = False
            
            if trades:
                avg_return = np.mean(trades)
                win_rate = np.mean([t > 0 for t in trades])
                print(f"\n💰 Trade Performance:")
                print(f"Total trades: {len(trades)}")
                print(f"Average return: {avg_return:.2%}")
                print(f"Win rate: {win_rate:.1%}")
                print(f"Best trade: {max(trades):.2%}")
                print(f"Worst trade: {min(trades):.2%}")
    
    print("\n🎉 HYE Strategy test completed successfully!")
    return True

if __name__ == "__main__":
    test_hye_strategy_simple()