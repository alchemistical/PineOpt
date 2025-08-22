"""
AI-Powered Pine Script Analysis Agent
Deeply analyzes Pine Script code to understand algorithm structure and logic
"""

import re
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import ast
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class IndicatorAnalysis:
    """Analysis of a specific indicator"""
    name: str
    type: str  # 'builtin', 'custom', 'compound'
    parameters: Dict[str, Any]
    inputs: List[str]  # What data it uses (close, high, low, etc.)
    outputs: List[str]  # What values it produces
    purpose: str  # What role it plays in the strategy

@dataclass
class ParameterAnalysis:
    """Analysis of a strategy parameter"""
    name: str
    default_value: Any
    data_type: str
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    description: str = ""
    category: str = ""  # 'indicator', 'risk', 'timing', etc.

@dataclass
class LogicFlowAnalysis:
    """Analysis of strategy logic flow"""
    entry_conditions: List[str]
    exit_conditions: List[str]
    signal_combinations: Dict[str, str]
    logic_type: str  # 'trend_following', 'mean_reversion', 'hybrid'
    complexity_score: int  # 1-10

@dataclass
class StrategyAnalysis:
    """Complete analysis of Pine Script strategy"""
    name: str
    description: str
    strategy_type: str
    indicators: Dict[str, IndicatorAnalysis]
    parameters: Dict[str, ParameterAnalysis]
    logic_flow: LogicFlowAnalysis
    data_requirements: List[str]
    timeframe_compatibility: List[str]
    complexity_assessment: Dict[str, Any]
    conversion_challenges: List[str]
    analysis_timestamp: str

class StrategyAnalysisAgent:
    """AI agent for analyzing Pine Script strategies"""
    
    def __init__(self):
        self.builtin_indicators = self._load_builtin_indicators()
        self.pine_functions = self._load_pine_functions()
        self.analysis_patterns = self._load_analysis_patterns()
    
    def analyze_strategy(self, pine_code: str, filename: str = "strategy") -> StrategyAnalysis:
        """
        Perform comprehensive analysis of Pine Script strategy
        """
        logger.info(f"🤖 Starting AI analysis of {filename}")
        
        # Clean and prepare code
        cleaned_code = self._preprocess_code(pine_code)
        
        # Extract basic info
        name, description, strategy_type = self._extract_basic_info(cleaned_code)
        
        # Analyze indicators
        indicators = self._analyze_indicators(cleaned_code)
        
        # Extract parameters
        parameters = self._extract_parameters(cleaned_code)
        
        # Analyze logic flow
        logic_flow = self._analyze_logic_flow(cleaned_code, indicators)
        
        # Assess complexity and conversion challenges
        complexity = self._assess_complexity(cleaned_code, indicators, logic_flow)
        challenges = self._identify_conversion_challenges(cleaned_code, indicators)
        
        # Data requirements
        data_reqs = self._determine_data_requirements(indicators)
        timeframes = self._analyze_timeframe_compatibility(cleaned_code)
        
        analysis = StrategyAnalysis(
            name=name,
            description=description,
            strategy_type=strategy_type,
            indicators=indicators,
            parameters=parameters,
            logic_flow=logic_flow,
            data_requirements=data_reqs,
            timeframe_compatibility=timeframes,
            complexity_assessment=complexity,
            conversion_challenges=challenges,
            analysis_timestamp=datetime.now().isoformat()
        )
        
        logger.info(f"✅ Analysis complete: {len(indicators)} indicators, {len(parameters)} parameters")
        return analysis
    
    def _preprocess_code(self, pine_code: str) -> str:
        """Clean and normalize Pine Script code"""
        # Remove comments but preserve structure
        lines = []
        for line in pine_code.split('\n'):
            # Remove line comments but keep the line structure
            if '//' in line:
                line = line.split('//')[0]
            lines.append(line.rstrip())
        
        return '\n'.join(lines)
    
    def _extract_basic_info(self, code: str) -> Tuple[str, str, str]:
        """Extract strategy name, description, and type"""
        name = "Unknown Strategy"
        description = ""
        strategy_type = "hybrid"
        
        # Look for strategy() declaration
        strategy_match = re.search(r'strategy\s*\(\s*["\']([^"\']+)["\']', code)
        if strategy_match:
            name = strategy_match.group(1)
        
        # Look for title in strategy declaration
        title_match = re.search(r'title\s*=\s*["\']([^"\']+)["\']', code)
        if title_match:
            name = title_match.group(1)
            
        # Extract description from comments
        desc_patterns = [
            r'//\s*Description:\s*(.+)',
            r'//\s*Strategy:\s*(.+)',
            r'//\s*(.+strategy.+)',
        ]
        
        for pattern in desc_patterns:
            match = re.search(pattern, code, re.IGNORECASE)
            if match:
                description = match.group(1).strip()
                break
        
        # Determine strategy type based on indicators used
        if any(indicator in code.lower() for indicator in ['vwap', 'mean', 'reversion']):
            if any(indicator in code.lower() for indicator in ['trend', 'momentum', 'tsv']):
                strategy_type = "hybrid"  # Mean reversion + trend following
            else:
                strategy_type = "mean_reversion"
        elif any(indicator in code.lower() for indicator in ['trend', 'momentum', 'ma']):
            strategy_type = "trend_following"
        
        return name, description, strategy_type
    
    def _analyze_indicators(self, code: str) -> Dict[str, IndicatorAnalysis]:
        """Identify and analyze all indicators used"""
        indicators = {}
        
        # Define indicator patterns
        indicator_patterns = {
            'rsi': {
                'pattern': r'rsi\s*\(\s*([^,\)]+)(?:,\s*([^)]+))?\s*\)',
                'type': 'momentum',
                'inputs': ['close'],
                'outputs': ['rsi_value'],
                'purpose': 'Momentum oscillator for overbought/oversold conditions'
            },
            'vwap': {
                'pattern': r'vwap\s*\(\s*([^)]*)\s*\)',
                'type': 'volume',
                'inputs': ['hlc3', 'volume'],
                'outputs': ['vwap_line'],
                'purpose': 'Volume weighted average price for mean reversion'
            },
            'sma': {
                'pattern': r'sma\s*\(\s*([^,]+),\s*([^)]+)\s*\)',
                'type': 'trend',
                'inputs': ['source'],
                'outputs': ['ma_line'],
                'purpose': 'Simple moving average for trend identification'
            },
            'ema': {
                'pattern': r'ema\s*\(\s*([^,]+),\s*([^)]+)\s*\)',
                'type': 'trend',
                'inputs': ['source'],
                'outputs': ['ma_line'],
                'purpose': 'Exponential moving average for trend identification'
            },
            'bb': {
                'pattern': r'bb\s*\(\s*([^,]+),\s*([^,]+),\s*([^)]+)\s*\)',
                'type': 'volatility',
                'inputs': ['source'],
                'outputs': ['bb_upper', 'bb_middle', 'bb_lower'],
                'purpose': 'Bollinger Bands for volatility and mean reversion'
            },
            'tsv': {
                'pattern': r'tsv|time.*series.*volume',
                'type': 'volume',
                'inputs': ['close', 'volume'],
                'outputs': ['tsv_value'],
                'purpose': 'Time Series Volume for trend confirmation'
            }
        }
        
        # Search for each indicator pattern
        for ind_name, ind_config in indicator_patterns.items():
            matches = re.finditer(ind_config['pattern'], code, re.IGNORECASE)
            
            for i, match in enumerate(matches):
                key = f"{ind_name}_{i}" if i > 0 else ind_name
                
                # Extract parameters from the match
                parameters = {}
                if match.groups():
                    groups = match.groups()
                    if ind_name == 'rsi':
                        parameters['source'] = groups[0] if groups[0] else 'close'
                        parameters['length'] = groups[1] if len(groups) > 1 and groups[1] else '14'
                    elif ind_name in ['sma', 'ema']:
                        parameters['source'] = groups[0]
                        parameters['length'] = groups[1]
                    elif ind_name == 'bb':
                        parameters['source'] = groups[0]
                        parameters['length'] = groups[1]
                        parameters['multiplier'] = groups[2]
                
                indicators[key] = IndicatorAnalysis(
                    name=ind_name.upper(),
                    type=ind_config['type'],
                    parameters=parameters,
                    inputs=ind_config['inputs'],
                    outputs=ind_config['outputs'],
                    purpose=ind_config['purpose']
                )
        
        # Look for actual custom indicators (complex calculations only)
        custom_patterns = [
            r'(\w+)\s*=\s*(?:ta\.)?(\w+)\s*\([^)]*(?:high|low|close|open|volume)[^)]*\)',  # Complex ta calls
            r'(\w+)\s*=\s*(?:sma|ema|rsi|vwap|bb)\s*\(',  # Direct indicator calls
        ]
        
        # Filter out simple assignments and parameters
        excluded_names = {
            'source', 'length', 'period', 'title', 'start', 'end', 'color', 'style',
            'input', 'var', 'if', 'else', 'and', 'or', 'not', 'true', 'false',
            'high', 'low', 'close', 'open', 'volume', 'hlc3', 'ohlc4', 'hl2'
        }
        
        for pattern in custom_patterns:
            matches = re.finditer(pattern, code)
            for match in matches:
                var_name = match.group(1)
                if (var_name not in indicators and 
                    len(var_name) > 2 and 
                    var_name.lower() not in excluded_names and
                    not any(excluded in var_name.lower() for excluded in excluded_names)):
                    
                    # Only add if it looks like a real indicator
                    if any(term in match.group(0).lower() for term in ['sma', 'ema', 'rsi', 'vwap', 'bb', 'ta.']):
                        indicators[var_name] = IndicatorAnalysis(
                            name=var_name,
                            type='custom',
                            parameters={},
                            inputs=['price_data'],
                            outputs=[var_name],
                            purpose='Custom indicator calculation'
                        )
        
        return indicators
    
    def _extract_parameters(self, code: str) -> Dict[str, ParameterAnalysis]:
        """Extract strategy parameters and their configurations"""
        parameters = {}
        
        # Look for input declarations
        input_patterns = [
            r'(\w+)\s*=\s*input\s*\(\s*([^,)]+)(?:,\s*title\s*=\s*["\']([^"\']*)["\'])?',
            r'(\w+)\s*=\s*input\.(\w+)\s*\(\s*([^,)]+)(?:,\s*title\s*=\s*["\']([^"\']*)["\'])?',
            r'(\w+)\s*=\s*input\s*\(\s*([^,)]+)(?:.*title\s*=\s*["\']([^"\']*)["\'])?',
        ]
        
        for pattern in input_patterns:
            matches = re.finditer(pattern, code)
            for match in matches:
                param_name = match.group(1)
                default_value = match.group(2).strip()
                title = match.group(3) if len(match.groups()) >= 3 else ""
                
                # Clean default value
                default_value = default_value.strip('\'"')
                
                # Determine data type
                data_type = "string"
                if default_value.replace('.', '').replace('-', '').isdigit():
                    data_type = "float" if '.' in default_value else "int"
                elif default_value.lower() in ['true', 'false']:
                    data_type = "bool"
                
                # Categorize parameter
                category = "general"
                if any(term in param_name.lower() for term in ['length', 'period']):
                    category = "indicator"
                elif any(term in param_name.lower() for term in ['risk', 'stop', 'target']):
                    category = "risk"
                elif any(term in param_name.lower() for term in ['color', 'style']):
                    category = "display"
                
                parameters[param_name] = ParameterAnalysis(
                    name=param_name,
                    default_value=default_value,
                    data_type=data_type,
                    description=title,
                    category=category
                )
        
        return parameters
    
    def _analyze_logic_flow(self, code: str, indicators: Dict[str, IndicatorAnalysis]) -> LogicFlowAnalysis:
        """Analyze the trading logic and signal generation"""
        entry_conditions = []
        exit_conditions = []
        signal_combinations = {}
        
        # Look for strategy.entry and strategy.close calls
        entry_pattern = r'strategy\.entry\s*\([^)]*\)'
        exit_pattern = r'strategy\.(?:close|exit)\s*\([^)]*\)'
        
        entry_matches = re.findall(entry_pattern, code)
        exit_matches = re.findall(exit_pattern, code)
        
        # Extract conditions from if statements before entry/exit calls
        lines = code.split('\n')
        for i, line in enumerate(lines):
            if 'strategy.entry' in line or 'strategy.close' in line:
                # Look backwards for condition
                for j in range(i-1, max(0, i-10), -1):
                    if 'if ' in lines[j]:
                        condition = lines[j].strip()
                        if 'strategy.entry' in line:
                            entry_conditions.append(condition)
                        else:
                            exit_conditions.append(condition)
                        break
        
        # Determine logic type based on indicators and conditions
        logic_type = "hybrid"
        if any('vwap' in ind.lower() for ind in indicators.keys()):
            if any('trend' in ind.lower() or 'momentum' in ind.lower() for ind in indicators.keys()):
                logic_type = "hybrid"
            else:
                logic_type = "mean_reversion"
        elif any('ma' in ind.lower() or 'trend' in ind.lower() for ind in indicators.keys()):
            logic_type = "trend_following"
        
        # Calculate complexity score
        complexity = min(10, len(indicators) + len(entry_conditions) + len(exit_conditions))
        
        return LogicFlowAnalysis(
            entry_conditions=entry_conditions,
            exit_conditions=exit_conditions,
            signal_combinations=signal_combinations,
            logic_type=logic_type,
            complexity_score=complexity
        )
    
    def _assess_complexity(self, code: str, indicators: Dict[str, IndicatorAnalysis], 
                          logic_flow: LogicFlowAnalysis) -> Dict[str, Any]:
        """Assess the complexity of the strategy"""
        return {
            "indicator_count": len(indicators),
            "logic_complexity": logic_flow.complexity_score,
            "lines_of_code": len(code.split('\n')),
            "custom_functions": len(re.findall(r'^\s*\w+\s*\([^)]*\)\s*=>', code, re.MULTILINE)),
            "overall_score": min(10, len(indicators) + logic_flow.complexity_score // 2)
        }
    
    def _identify_conversion_challenges(self, code: str, indicators: Dict[str, IndicatorAnalysis]) -> List[str]:
        """Identify potential challenges in converting to Python"""
        challenges = []
        
        # Check for complex Pine Script features
        if 'security(' in code:
            challenges.append("Multi-timeframe analysis - requires data handling")
        
        if 'var ' in code:
            challenges.append("Variable state management across bars")
            
        if 'array.' in code or 'matrix.' in code:
            challenges.append("Advanced data structures")
        
        # Check for custom indicators
        custom_indicators = [ind for ind in indicators.values() if ind.type == 'custom']
        if len(custom_indicators) > 2:
            challenges.append(f"Multiple custom indicators ({len(custom_indicators)})")
        
        # Check for complex logic
        if code.count('if ') > 5:
            challenges.append("Complex conditional logic")
        
        return challenges
    
    def _determine_data_requirements(self, indicators: Dict[str, IndicatorAnalysis]) -> List[str]:
        """Determine what market data is needed"""
        requirements = set(['close'])  # Always need close price
        
        for indicator in indicators.values():
            requirements.update(indicator.inputs)
        
        # Map Pine Script terms to standard terms
        mapping = {
            'hlc3': 'typical_price',
            'ohlc4': 'average_price',
            'hl2': 'median_price'
        }
        
        final_reqs = []
        for req in requirements:
            final_reqs.append(mapping.get(req, req))
        
        return sorted(list(set(final_reqs)))
    
    def _analyze_timeframe_compatibility(self, code: str) -> List[str]:
        """Determine compatible timeframes"""
        # Default timeframes
        timeframes = ["1h", "4h", "1d"]
        
        # If strategy uses volume heavily, shorter timeframes might be better
        if code.lower().count('volume') > 3:
            timeframes = ["5m", "15m", "1h", "4h"]
        
        # If strategy is very simple, it can work on longer timeframes
        if len(code.split('\n')) < 50:
            timeframes.extend(["1w", "1M"])
        
        return timeframes
    
    def _load_builtin_indicators(self) -> Dict[str, Any]:
        """Load Pine Script built-in indicators"""
        return {
            'rsi': {'params': ['source', 'length'], 'category': 'momentum'},
            'sma': {'params': ['source', 'length'], 'category': 'trend'},
            'ema': {'params': ['source', 'length'], 'category': 'trend'},
            'vwap': {'params': ['source'], 'category': 'volume'},
            'bb': {'params': ['source', 'length', 'mult'], 'category': 'volatility'}
        }
    
    def _load_pine_functions(self) -> Dict[str, Any]:
        """Load Pine Script function signatures"""
        return {
            'crossover': 'bool',
            'crossunder': 'bool',
            'rising': 'bool',
            'falling': 'bool',
            'highest': 'series',
            'lowest': 'series'
        }
    
    def _load_analysis_patterns(self) -> Dict[str, Any]:
        """Load pattern recognition for analysis"""
        return {
            'mean_reversion': ['vwap', 'mean', 'revert', 'oversold', 'overbought'],
            'trend_following': ['trend', 'momentum', 'breakout', 'crossover'],
            'momentum': ['rsi', 'macd', 'stoch', 'momentum'],
            'volatility': ['bb', 'atr', 'volatility', 'bands']
        }
    
    def save_analysis(self, analysis: StrategyAnalysis, output_path: str):
        """Save analysis to JSON file"""
        analysis_dict = asdict(analysis)
        
        with open(output_path, 'w') as f:
            json.dump(analysis_dict, f, indent=2, default=str)
        
        logger.info(f"💾 Analysis saved to {output_path}")
    
    def generate_analysis_report(self, analysis: StrategyAnalysis) -> str:
        """Generate human-readable analysis report"""
        report = f"""
# Strategy Analysis Report: {analysis.name}

## Overview
- **Strategy Type**: {analysis.strategy_type}
- **Description**: {analysis.description}
- **Complexity Score**: {analysis.complexity_assessment.get('overall_score', 0)}/10

## Indicators Analysis ({len(analysis.indicators)} found)
"""
        
        for name, indicator in analysis.indicators.items():
            report += f"""
### {name} ({indicator.name})
- **Type**: {indicator.type}
- **Purpose**: {indicator.purpose}
- **Parameters**: {indicator.parameters}
- **Inputs**: {', '.join(indicator.inputs)}
"""
        
        report += f"""
## Parameters ({len(analysis.parameters)} found)
"""
        
        for name, param in analysis.parameters.items():
            report += f"- **{name}**: {param.data_type} = {param.default_value} ({param.category})\n"
        
        report += f"""
## Logic Flow
- **Type**: {analysis.logic_flow.logic_type}
- **Entry Conditions**: {len(analysis.logic_flow.entry_conditions)}
- **Exit Conditions**: {len(analysis.logic_flow.exit_conditions)}
- **Complexity**: {analysis.logic_flow.complexity_score}/10

## Data Requirements
{', '.join(analysis.data_requirements)}

## Conversion Challenges
"""
        
        for challenge in analysis.conversion_challenges:
            report += f"- {challenge}\n"
        
        report += f"""
## Timeframe Compatibility
{', '.join(analysis.timeframe_compatibility)}

---
*Analysis completed at {analysis.analysis_timestamp}*
        """
        
        return report.strip()

# Example usage and testing
if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    agent = StrategyAnalysisAgent()
    
    # Test with a sample Pine Script
    sample_code = '''
    //@version=5
    strategy("Sample RSI Strategy", overlay=false)
    
    length = input(14, title="RSI Length")
    overbought = input(70, title="Overbought Level")
    oversold = input(30, title="Oversold Level")
    
    rsi_value = rsi(close, length)
    
    if rsi_value < oversold
        strategy.entry("Long", strategy.long)
    
    if rsi_value > overbought
        strategy.close("Long")
    '''
    
    analysis = agent.analyze_strategy(sample_code, "sample_strategy")
    report = agent.generate_analysis_report(analysis)
    print(report)