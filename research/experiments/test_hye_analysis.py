"""
Test the AI Strategy Analysis Agent on the HYE strategy
"""

import sys
from pathlib import Path
import json

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from research.ai_analysis.strategy_analysis_agent import StrategyAnalysisAgent

def test_hye_analysis():
    """Test AI analysis on HYE Pine Script"""
    
    # Load the HYE strategy
    hye_path = Path(__file__).parent.parent.parent / "examples" / "pine_scripts" / "hye.pine"
    
    if not hye_path.exists():
        print(f"❌ HYE strategy file not found at {hye_path}")
        return
    
    with open(hye_path, 'r') as f:
        hye_code = f.read()
    
    print(f"📖 Loaded HYE strategy ({len(hye_code)} characters)")
    print("🤖 Starting AI analysis...")
    
    # Initialize the AI agent
    agent = StrategyAnalysisAgent()
    
    # Analyze the strategy
    analysis = agent.analyze_strategy(hye_code, "HYE Combo Market Strategy")
    
    # Generate and display report
    report = agent.generate_analysis_report(analysis)
    print("\n" + "="*80)
    print(report)
    print("="*80)
    
    # Save analysis to JSON
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)
    
    analysis_file = output_dir / "hye_analysis.json"
    agent.save_analysis(analysis, str(analysis_file))
    
    report_file = output_dir / "hye_analysis_report.md"
    with open(report_file, 'w') as f:
        f.write(report)
    
    print(f"\n💾 Files saved:")
    print(f"   - Analysis: {analysis_file}")
    print(f"   - Report: {report_file}")
    
    # Print key insights
    print(f"\n🎯 Key Insights:")
    print(f"   - Strategy Type: {analysis.strategy_type}")
    print(f"   - Indicators Found: {len(analysis.indicators)}")
    print(f"   - Parameters Found: {len(analysis.parameters)}")
    print(f"   - Complexity Score: {analysis.complexity_assessment.get('overall_score', 0)}/10")
    print(f"   - Conversion Challenges: {len(analysis.conversion_challenges)}")
    
    if analysis.conversion_challenges:
        print(f"\n⚠️ Main Challenges:")
        for challenge in analysis.conversion_challenges[:3]:  # Show top 3
            print(f"   - {challenge}")
    
    return analysis

if __name__ == "__main__":
    analysis = test_hye_analysis()