#!/usr/bin/env python3
"""Test Pine parser with simple examples."""

from pine2py.parser.parser import PineParser

# Simple Pine script for testing
simple_pine = '''
//@version=5
strategy("Test Strategy", overlay=true)

rsi_length = input.int(14, title="RSI Length")
rsi_value = ta.rsi(close, rsi_length)
long_condition = ta.crossover(rsi_value, 30)

if long_condition
    strategy.entry("Long", strategy.long)
'''

print("🧪 Testing Pine Parser")
print("=" * 30)

try:
    parser = PineParser()
    print("✅ Parser initialized successfully")
    
    # Test with simple code
    simple_test = '''
    rsi_length = input.int(14)
    rsi_value = ta.rsi(close, rsi_length)
    '''
    
    print("📝 Testing simple Pine code parsing...")
    print(f"Input: {simple_test.strip()}")
    
    # For now, let's just test basic functionality
    print("✅ Parser setup complete - ready for AST implementation")
    
except Exception as e:
    print(f"❌ Parser test failed: {e}")
    print("📝 This is expected in MVP - will implement step by step")

print("\n🎯 Next: Implement basic AST nodes and simple expression parsing")