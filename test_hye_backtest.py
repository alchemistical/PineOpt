#!/usr/bin/env python3
"""Test the HYE strategy with real backtesting"""

import sys
sys.path.append('.')

from research.backtest.backtest_engine import BacktestEngine
from api.market_data_service import MarketDataService
import pandas as pd
import json

def test_hye_strategy():
    """Test HYE strategy with real market data"""
    print("🚀 Testing HYE Strategy Implementation")
    
    # Load the HYE strategy
    exec(open('hye_strategy_implementation.py').read(), globals())
    
    # Initialize services
    market_service = MarketDataService()
    backtest_engine = BacktestEngine()
    
    print("📊 Loading market data...")
    
    # Load BTCUSDT data for testing
    try:
        df = backtest_engine.load_market_data(
            symbol="BTCUSDT",
            timeframe="1h", 
            start_date="2024-01-01",
            end_date="2024-02-01",
            n_bars=500
        )
        
        print(f"✅ Loaded {len(df)} bars of BTCUSDT data")
        print(f"Date range: {df.index[0]} to {df.index[-1]}")
        
        # Test signal generation
        print("\n🔍 Testing signal generation...")
        signals = build_signals(df)
        
        entry_count = signals.entries.sum()
        exit_count = signals.exits.sum()
        print(f"✅ Generated {entry_count} entry signals and {exit_count} exit signals")
        
        if entry_count == 0:
            print("⚠️  No entry signals generated - strategy may be too restrictive")
            return False
        
        # Run backtest
        print("\n🎯 Running backtest...")
        backtest_config = {
            'initial_balance': 10000,
            'position_size': 0.1,  # 10% of balance per trade
            'commission': 0.001,   # 0.1% commission
            'start_date': '2024-01-01',
            'end_date': '2024-02-01'
        }
        
        # Create a simple strategy wrapper
        def strategy_func(df, **params):
            return build_signals(df, **params)
        
        results = backtest_engine.run_backtest(
            strategy_func,
            "BTCUSDT", 
            "1h",
            backtest_config
        )
        
        print(f"✅ Backtest completed!")
        print(f"Final Balance: ${results['final_balance']:.2f}")
        print(f"Total Return: {results['total_return']:.2%}")
        print(f"Total Trades: {results['total_trades']}")
        print(f"Win Rate: {results['win_rate']:.1%}")
        print(f"Max Drawdown: {results['max_drawdown']:.2%}")
        print(f"Sharpe Ratio: {results['sharpe_ratio']:.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_hye_strategy()
    if success:
        print("\n🎉 HYE Strategy test completed successfully!")
    else:
        print("\n💥 HYE Strategy test failed!")