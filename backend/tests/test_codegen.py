#!/usr/bin/env python3
"""Test Pine code generation."""

from pine2py.codegen.emit import convert_simple_rsi_strategy

print("🧪 Testing Pine Code Generation")
print("=" * 40)

try:
    # Generate RSI strategy
    python_code = convert_simple_rsi_strategy()
    
    print("✅ Code generation successful!")
    print("\n📝 Generated Python Strategy:")
    print("-" * 40)
    print(python_code)
    print("-" * 40)
    
    # Test if generated code is valid Python
    try:
        compile(python_code, '<generated>', 'exec')
        print("\n✅ Generated code compiles successfully!")
    except SyntaxError as e:
        print(f"\n❌ Syntax error in generated code: {e}")
    
except Exception as e:
    print(f"❌ Code generation failed: {e}")

print("\n🎯 Next: Test with real OHLC data")