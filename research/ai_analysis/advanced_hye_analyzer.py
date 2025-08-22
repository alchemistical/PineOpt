"""
Advanced HYE Strategy Analyzer
Specialized analyzer for the HYE Combo Market Strategy
"""

import re
import json
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass

@dataclass
class HYEComponent:
    """Component of the HYE strategy"""
    name: str
    type: str  # 'indicator', 'signal', 'parameter', 'logic'
    description: str
    pine_code: str
    python_equivalent: str
    dependencies: List[str]

class HYEStrategyAnalyzer:
    """Specialized analyzer for HYE strategy"""
    
    def __init__(self):
        self.components = {}
        self.strategy_phases = {
            'mean_reversion': [],
            'trend_hunting': [],
            'risk_management': []
        }
    
    def analyze_hye_strategy(self, pine_code: str) -> Dict[str, Any]:
        """Comprehensive analysis of HYE strategy"""
        
        print("🔍 Analyzing HYE strategy components...")
        
        analysis = {
            'strategy_name': 'HYE Combo Market Strategy',
            'dual_logic_system': {},
            'core_indicators': {},
            'parameters': {},
            'vwap_system': {},
            'momentum_system': {},
            'entry_exit_logic': {},
            'conversion_roadmap': []
        }
        
        # 1. Analyze VWAP System (Mean Reversion)
        analysis['vwap_system'] = self._analyze_vwap_system(pine_code)
        
        # 2. Analyze Momentum System (Trend Hunting)
        analysis['momentum_system'] = self._analyze_momentum_system(pine_code)
        
        # 3. Extract Core Parameters
        analysis['parameters'] = self._extract_core_parameters(pine_code)
        
        # 4. Analyze Entry/Exit Logic
        analysis['entry_exit_logic'] = self._analyze_entry_exit_logic(pine_code)
        
        # 5. Generate Conversion Roadmap
        analysis['conversion_roadmap'] = self._generate_conversion_roadmap(analysis)
        
        return analysis
    
    def _analyze_vwap_system(self, code: str) -> Dict[str, Any]:
        """Analyze the VWAP-based mean reversion system"""
        print("   📊 Analyzing VWAP system...")
        
        vwap_analysis = {
            'purpose': 'Mean reversion trading based on Volume Weighted Average Price',
            'components': {},
            'logic': 'Buy when price is below VWAP by certain percentage'
        }
        
        # Find VWAP calculations
        vwap_patterns = [
            r'(small|big|mean)cumulativePeriod\s*=.*?(\d+)',
            r'cumulativeTypicalPrice.*?=.*?(.*)',
            r'cumulativeVolume.*?=.*?(.*)',
            r'buyMA\s*=.*?(.*)',
            r'percentBelowToBuy.*?=.*?(\d+\.?\d*)'
        ]
        
        vwap_components = []
        for pattern in vwap_patterns:
            matches = re.finditer(pattern, code, re.MULTILINE | re.DOTALL)
            for match in matches:
                vwap_components.append({
                    'match': match.group(0),
                    'type': 'vwap_calculation'
                })
        
        vwap_analysis['components']['found'] = len(vwap_components)
        vwap_analysis['components']['details'] = vwap_components[:5]  # First 5 for brevity
        
        # Extract VWAP periods from input variables
        period_matches = re.findall(r'(small|big|mean)cumulativePeriod\s*=\s*input\([^)]*defval\s*=\s*(\d+)', code)
        if period_matches:
            vwap_analysis['periods'] = {match[0]: int(match[1]) for match in period_matches}
        else:
            # Fallback: extract from variable assignments
            fallback_matches = re.findall(r'(small|big|mean)cumulativePeriod\s*=.*?(\d+)', code)
            if fallback_matches:
                vwap_analysis['periods'] = {match[0]: int(match[1]) for match in fallback_matches}
        
        return vwap_analysis
    
    def _analyze_momentum_system(self, code: str) -> Dict[str, Any]:
        """Analyze the momentum/trend hunting system"""
        print("   🚀 Analyzing momentum system...")
        
        momentum_analysis = {
            'purpose': 'Trend hunting using multiple momentum indicators',
            'indicators': {},
            'logic': 'Combine RSI, TSV, Vidya, and Ichimoku-style indicators'
        }
        
        # RSI System
        rsi_matches = re.findall(r'rsi\s*\([^)]+\)', code)
        if rsi_matches:
            momentum_analysis['indicators']['rsi'] = {
                'found': len(rsi_matches),
                'purpose': 'Momentum oscillator',
                'sample': rsi_matches[0] if rsi_matches else None
            }
        
        # TSV (Time Series Volume)
        tsv_matches = re.findall(r'tsv.*?=.*', code)
        if tsv_matches:
            momentum_analysis['indicators']['tsv'] = {
                'found': len(tsv_matches),
                'purpose': 'Volume-based momentum',
                'sample': tsv_matches[0] if tsv_matches else None
            }
        
        # Vidya (Variable Index Dynamic Average)
        vidya_matches = re.findall(r'cmo.*?=.*', code)  # CMO is part of Vidya
        if vidya_matches:
            momentum_analysis['indicators']['vidya'] = {
                'found': len(vidya_matches),
                'purpose': 'Adaptive moving average',
                'sample': vidya_matches[0] if vidya_matches else None
            }
        
        # Ichimoku-style components
        ichimoku_matches = re.findall(r'(tenkansen|kijunsen|leadLine).*?=.*', code)
        if ichimoku_matches:
            momentum_analysis['indicators']['ichimoku_style'] = {
                'found': len(ichimoku_matches),
                'purpose': 'Trend identification lines',
                'components': ichimoku_matches[:3]  # First 3 components
            }
        
        return momentum_analysis
    
    def _extract_core_parameters(self, code: str) -> Dict[str, Any]:
        """Extract the core configurable parameters from Pine Script input statements"""
        print("   ⚙️ Extracting parameters...")
        
        # Match Pine Script input() statements with proper parsing
        # Pattern: variable_name = input(title = "Title", defval = value, ...)
        input_pattern = r'(\w+)\s*=\s*input\s*\(\s*(?:title\s*=\s*["\']([^"\']*)["\']).{0,200}?(?:defval\s*=\s*([\w\d\.]+))'
        
        matches = re.findall(input_pattern, code, re.MULTILINE | re.DOTALL)
        
        extracted_params = {
            'mean_reversion_inputs': {},
            'trend_hunter_inputs': {},
            'all_parameters': []
        }
        
        for match in matches:
            var_name, title, default_val = match
            
            # Convert default value to appropriate type
            try:
                if '.' in default_val:
                    default_val = float(default_val)
                elif default_val.isdigit():
                    default_val = int(default_val)
                elif default_val == 'close':
                    default_val = 'close'  # Keep as string for source inputs
            except:
                pass  # Keep as string if conversion fails
            
            param_info = {
                'variable_name': var_name,
                'title': title,
                'default_value': default_val,
                'pine_code': f'{var_name} = input(title = "{title}", defval = {default_val})'
            }
            
            # Categorize parameters
            title_lower = title.lower()
            if any(word in title_lower for word in ['vwap', 'percent', 'rsi', 'mean reversion']):
                extracted_params['mean_reversion_inputs'][var_name] = param_info
            elif any(word in title_lower for word in ['tenkan', 'kijun', 'tsv', 'vidya', 'trend']):
                extracted_params['trend_hunter_inputs'][var_name] = param_info
            
            extracted_params['all_parameters'].append(param_info)
        
        print(f"   ✅ Found {len(extracted_params['all_parameters'])} parameters:")
        for param in extracted_params['all_parameters']:
            print(f"      - {param['variable_name']}: {param['title']} (default: {param['default_value']})")
        
        return extracted_params
    
    def _analyze_entry_exit_logic(self, code: str) -> Dict[str, Any]:
        """Analyze the trading logic"""
        print("   🎯 Analyzing entry/exit logic...")
        
        logic_analysis = {
            'entry_conditions': [],
            'exit_conditions': [],
            'dual_system_combination': 'Unknown'
        }
        
        # Look for strategy.entry calls
        entry_pattern = r'if\s+([^{]+)\s*strategy\.entry'
        entry_matches = re.findall(entry_pattern, code, re.MULTILINE)
        logic_analysis['entry_conditions'] = entry_matches
        
        # Look for strategy.close calls  
        exit_pattern = r'if\s+([^{]+)\s*strategy\.close'
        exit_matches = re.findall(exit_pattern, code, re.MULTILINE)
        logic_analysis['exit_conditions'] = exit_matches
        
        # Analyze how the two systems combine
        if 'vwap' in code.lower() and any(term in code.lower() for term in ['rsi', 'tsv', 'momentum']):
            logic_analysis['dual_system_combination'] = 'VWAP mean reversion + momentum confirmation'
        
        return logic_analysis
    
    def _generate_conversion_roadmap(self, analysis: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate a roadmap for converting to Python"""
        print("   🗺️ Generating conversion roadmap...")
        
        roadmap = [
            {
                'step': 1,
                'component': 'VWAP System',
                'task': 'Implement volume-weighted average price calculations',
                'complexity': 'Medium',
                'python_libs': 'pandas, numpy',
                'key_challenge': 'Cumulative volume calculations across different periods'
            },
            {
                'step': 2,
                'component': 'RSI + EMA',
                'task': 'Implement RSI with EMA smoothing',
                'complexity': 'Easy',
                'python_libs': 'ta-lib or custom implementation',
                'key_challenge': 'Parameter mapping and validation'
            },
            {
                'step': 3,
                'component': 'TSV (Time Series Volume)',
                'task': 'Implement volume-based momentum indicator',
                'complexity': 'Hard',
                'python_libs': 'Custom implementation required',
                'key_challenge': 'Understanding TSV calculation method'
            },
            {
                'step': 4,
                'component': 'Vidya (Variable Index Dynamic Average)',
                'task': 'Implement adaptive moving average with CMO',
                'complexity': 'Hard',
                'python_libs': 'Custom implementation',
                'key_challenge': 'CMO calculation and alpha adjustment'
            },
            {
                'step': 5,
                'component': 'Ichimoku-style Components',
                'task': 'Implement Tenkansen, Kijunsen, Lead Lines',
                'complexity': 'Medium',
                'python_libs': 'Custom implementation',
                'key_challenge': 'Fast and slow period calculations'
            },
            {
                'step': 6,
                'component': 'Signal Logic',
                'task': 'Combine all indicators into entry/exit signals',
                'complexity': 'Hard',
                'python_libs': 'pandas',
                'key_challenge': 'Replicating exact Pine Script logic flow'
            },
            {
                'step': 7,
                'component': 'Parameter Interface',
                'task': 'Create configurable parameters matching Pine Script',
                'complexity': 'Medium',
                'python_libs': 'pydantic for validation',
                'key_challenge': 'Parameter validation and ranges'
            }
        ]
        
        return roadmap
    
    def generate_implementation_plan(self, analysis: Dict[str, Any]) -> str:
        """Generate detailed implementation plan"""
        
        plan = f"""
# HYE Strategy Implementation Plan

## Strategy Overview
**Name**: {analysis['strategy_name']}
**Type**: Dual-logic system combining mean reversion and trend hunting
**Complexity**: High (7 major components)

## Core Systems Analysis

### 1. VWAP Mean Reversion System
- **Purpose**: {analysis['vwap_system']['purpose']}
- **Components Found**: {analysis['vwap_system']['components']['found']}
- **Key Logic**: {analysis['vwap_system']['logic']}

### 2. Momentum/Trend System  
- **Purpose**: {analysis['momentum_system']['purpose']}
- **Indicators**: {', '.join(analysis['momentum_system']['indicators'].keys())}
- **Key Logic**: {analysis['momentum_system']['logic']}

## Implementation Roadmap
"""
        
        for step in analysis['conversion_roadmap']:
            plan += f"""
### Step {step['step']}: {step['component']}
- **Task**: {step['task']}
- **Complexity**: {step['complexity']}
- **Libraries**: {step['python_libs']}
- **Challenge**: {step['key_challenge']}
"""
        
        plan += f"""
## Parameter Configuration
{len(analysis['parameters'])} parameter categories identified:
"""
        
        for category, params in analysis['parameters'].items():
            if params:  # Only show categories with parameters
                plan += f"- **{category.replace('_', ' ').title()}**: {len(params)} parameters\n"
        
        plan += f"""
## Next Steps
1. **Start with VWAP system** - Core mean reversion logic
2. **Implement RSI smoothing** - Easiest momentum indicator  
3. **Build TSV from scratch** - Most complex custom indicator
4. **Add Vidya adaptive MA** - Advanced momentum component
5. **Integrate Ichimoku-style lines** - Trend identification
6. **Combine all systems** - Signal generation logic
7. **Create parameter interface** - User configuration
8. **Validate with backtesting** - Ensure accuracy

## Success Criteria
- [ ] All 16+ parameters configurable
- [ ] VWAP calculations match Pine Script exactly
- [ ] RSI + EMA smoothing working
- [ ] TSV momentum indicator implemented
- [ ] Vidya adaptive average functional
- [ ] Entry/exit signals match Pine Script
- [ ] Backtest results validate accuracy
"""
        
        return plan

def analyze_hye_strategy_file():
    """Analyze the HYE strategy file"""
    from pathlib import Path
    
    hye_path = Path(__file__).parent.parent.parent / "examples" / "pine_scripts" / "hye.pine"
    
    if not hye_path.exists():
        print(f"❌ HYE strategy file not found at {hye_path}")
        return
    
    with open(hye_path, 'r') as f:
        hye_code = f.read()
    
    print(f"📖 Loaded HYE strategy ({len(hye_code)} characters)")
    
    analyzer = HYEStrategyAnalyzer()
    analysis = analyzer.analyze_hye_strategy(hye_code)
    
    # Generate implementation plan
    plan = analyzer.generate_implementation_plan(analysis)
    
    print("\n" + "="*80)
    print(plan)
    print("="*80)
    
    # Save analysis
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)
    
    with open(output_dir / "hye_detailed_analysis.json", 'w') as f:
        json.dump(analysis, f, indent=2, default=str)
    
    with open(output_dir / "hye_implementation_plan.md", 'w') as f:
        f.write(plan)
    
    print(f"\n💾 Analysis saved to:")
    print(f"   - {output_dir / 'hye_detailed_analysis.json'}")
    print(f"   - {output_dir / 'hye_implementation_plan.md'}")
    
    return analysis

if __name__ == "__main__":
    analyze_hye_strategy_file()