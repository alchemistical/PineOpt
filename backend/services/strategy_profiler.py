"""
Epic 5 Enhanced: AI-Powered Strategy Analysis & Profiling System
Automatically generates comprehensive reports on strategy functionality and behavior
"""

import ast
import re
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

@dataclass
class StrategyProfile:
    """Comprehensive strategy analysis profile"""
    
    # Basic Information
    strategy_id: str
    name: str
    language: str
    author: str
    
    # Code Analysis
    complexity_score: float = 0.0
    lines_of_code: int = 0
    functions_count: int = 0
    imports_count: int = 0
    
    # Strategy Classification
    strategy_type: str = "unknown"  # trend_following, mean_reversion, momentum, arbitrage, etc.
    trading_style: str = "unknown"  # scalping, swing, position, algorithmic
    time_horizon: str = "unknown"   # intraday, short_term, medium_term, long_term
    
    # Technical Analysis Components
    indicators_used: List[str] = field(default_factory=list)
    signal_types: List[str] = field(default_factory=list)  # crossover, threshold, pattern, etc.
    data_requirements: List[str] = field(default_factory=list)  # OHLC, volume, etc.
    
    # Risk & Money Management
    has_stop_loss: bool = False
    has_take_profit: bool = False
    has_position_sizing: bool = False
    has_risk_management: bool = False
    
    # Strategy Logic Analysis
    entry_conditions: List[str] = field(default_factory=list)
    exit_conditions: List[str] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    # AI Analysis
    ai_summary: str = ""
    ai_strengths: List[str] = field(default_factory=list)
    ai_weaknesses: List[str] = field(default_factory=list)
    ai_recommendations: List[str] = field(default_factory=list)
    ai_market_suitability: str = ""
    
    # Performance Expectations
    expected_win_rate: Optional[float] = None
    expected_risk_level: str = "medium"  # low, medium, high
    expected_frequency: str = "medium"   # low, medium, high
    
    # Generated Report
    full_report: str = ""
    analysis_timestamp: datetime = field(default_factory=datetime.now)

class StrategyCodeAnalyzer:
    """Analyzes strategy code structure and functionality"""
    
    def __init__(self):
        # Technical indicator patterns
        self.indicator_patterns = {
            'RSI': [r'rsi', r'relative.*strength', r'RSI'],
            'SMA': [r'sma', r'simple.*moving.*average', r'rolling.*mean'],
            'EMA': [r'ema', r'exponential.*moving.*average', r'ewm'],
            'MACD': [r'macd', r'moving.*average.*convergence', r'MACD'],
            'Bollinger': [r'bollinger', r'bb', r'bands'],
            'Stochastic': [r'stochastic', r'stoch', r'%k', r'%d'],
            'ATR': [r'atr', r'average.*true.*range', r'ATR'],
            'ADX': [r'adx', r'average.*directional', r'ADX'],
            'Williams': [r'williams', r'%r', r'WR'],
            'CCI': [r'cci', r'commodity.*channel', r'CCI'],
            'Momentum': [r'momentum', r'roc', r'rate.*change'],
            'Volume': [r'volume', r'obv', r'vwap', r'mfi'],
            'Fibonacci': [r'fibonacci', r'fib', r'retracement'],
            'Pivot': [r'pivot', r'support', r'resistance']
        }
        
        # Strategy type patterns
        self.strategy_type_patterns = {
            'trend_following': [
                r'trend', r'momentum', r'breakout', r'moving.*average.*cross',
                r'ma.*cross', r'ema.*cross', r'follow.*trend'
            ],
            'mean_reversion': [
                r'mean.*reversion', r'reversal', r'oversold', r'overbought',
                r'bollinger.*reversion', r'rsi.*reversion', r'contrarian'
            ],
            'momentum': [
                r'momentum', r'rsi.*momentum', r'macd.*momentum', r'price.*momentum',
                r'strong.*move', r'acceleration'
            ],
            'scalping': [
                r'scalp', r'short.*term', r'quick.*profit', r'small.*move',
                r'tick', r'minute', r'second'
            ],
            'arbitrage': [
                r'arbitrage', r'spread', r'pair.*trading', r'statistical.*arbitrage',
                r'price.*difference'
            ],
            'grid': [
                r'grid', r'martingale', r'pyramid', r'averaging.*down',
                r'scale.*in', r'scale.*out'
            ]
        }
    
    def analyze_code(self, source_code: str, strategy_name: str = "") -> Dict[str, Any]:
        """Comprehensive code analysis"""
        try:
            # Parse AST
            tree = ast.parse(source_code)
            
            # Basic metrics
            lines_of_code = len([line for line in source_code.split('\n') if line.strip()])
            
            # Analyze AST
            analyzer = CodeVisitor()
            analyzer.visit(tree)
            
            # Detect indicators
            indicators = self._detect_indicators(source_code)
            
            # Classify strategy type
            strategy_type = self._classify_strategy_type(source_code, strategy_name)
            
            # Analyze signal logic
            signals = self._analyze_signal_logic(source_code)
            
            # Check risk management
            risk_features = self._analyze_risk_management(source_code)
            
            # Calculate complexity
            complexity = self._calculate_complexity(analyzer, lines_of_code)
            
            return {
                'lines_of_code': lines_of_code,
                'functions_count': len(analyzer.functions),
                'imports_count': len(analyzer.imports),
                'complexity_score': complexity,
                'functions': analyzer.functions,
                'imports': analyzer.imports,
                'variables': analyzer.variables,
                'indicators_used': indicators,
                'strategy_type': strategy_type,
                'signal_analysis': signals,
                'risk_management': risk_features,
                'has_parameters': len(analyzer.parameters) > 0,
                'parameters': analyzer.parameters
            }
            
        except Exception as e:
            logger.error(f"Code analysis failed: {e}")
            return {'error': str(e)}
    
    def _detect_indicators(self, code: str) -> List[str]:
        """Detect technical indicators in code"""
        code_lower = code.lower()
        detected = []
        
        for indicator, patterns in self.indicator_patterns.items():
            for pattern in patterns:
                if re.search(pattern, code_lower):
                    detected.append(indicator)
                    break
        
        return detected
    
    def _classify_strategy_type(self, code: str, name: str = "") -> str:
        """Classify strategy type based on code and name"""
        text = (code + " " + name).lower()
        
        scores = {}
        for strategy_type, patterns in self.strategy_type_patterns.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, text))
                score += matches
            scores[strategy_type] = score
        
        if max(scores.values()) > 0:
            return max(scores, key=scores.get)
        
        return "unknown"
    
    def _analyze_signal_logic(self, code: str) -> Dict[str, Any]:
        """Analyze entry/exit signal logic"""
        signals = {
            'entry_signals': [],
            'exit_signals': [],
            'signal_types': []
        }
        
        # Look for common signal patterns
        if re.search(r'cross.*over|crosses.*above|>\s*', code.lower()):
            signals['signal_types'].append('crossover')
        
        if re.search(r'cross.*under|crosses.*below|<\s*', code.lower()):
            signals['signal_types'].append('crossunder')
        
        if re.search(r'>\s*\d+|\d+\s*<|threshold|level', code.lower()):
            signals['signal_types'].append('threshold')
        
        # Look for entry/exit patterns
        entry_patterns = [r'buy', r'long', r'enter', r'entry', r'entries']
        exit_patterns = [r'sell', r'short', r'exit', r'close', r'exits']
        
        for pattern in entry_patterns:
            if re.search(pattern, code.lower()):
                signals['entry_signals'].append(pattern)
        
        for pattern in exit_patterns:
            if re.search(pattern, code.lower()):
                signals['exit_signals'].append(pattern)
        
        return signals
    
    def _analyze_risk_management(self, code: str) -> Dict[str, bool]:
        """Detect risk management features"""
        code_lower = code.lower()
        
        return {
            'has_stop_loss': bool(re.search(r'stop.*loss|sl|stop_loss', code_lower)),
            'has_take_profit': bool(re.search(r'take.*profit|tp|take_profit', code_lower)),
            'has_position_sizing': bool(re.search(r'position.*size|quantity|amount', code_lower)),
            'has_risk_management': bool(re.search(r'risk|drawdown|max.*loss', code_lower))
        }
    
    def _calculate_complexity(self, analyzer, lines_of_code: int) -> float:
        """Calculate strategy complexity score (0-100)"""
        complexity = 0
        
        # Base complexity from lines of code
        complexity += min(lines_of_code / 10, 20)  # Max 20 points for LOC
        
        # Function complexity
        complexity += min(len(analyzer.functions) * 5, 15)  # Max 15 points
        
        # Import complexity
        complexity += min(len(analyzer.imports) * 2, 10)  # Max 10 points
        
        # Control flow complexity
        complexity += min(len(analyzer.if_statements) * 3, 15)  # Max 15 points
        complexity += min(len(analyzer.loops) * 5, 20)  # Max 20 points
        
        # Variable complexity
        complexity += min(len(analyzer.variables) * 1, 20)  # Max 20 points
        
        return min(complexity, 100)

class CodeVisitor(ast.NodeVisitor):
    """AST visitor to analyze code structure"""
    
    def __init__(self):
        self.functions = []
        self.imports = []
        self.variables = []
        self.parameters = []
        self.if_statements = []
        self.loops = []
        self.assignments = []
    
    def visit_FunctionDef(self, node):
        self.functions.append(node.name)
        
        # Extract parameters
        for arg in node.args.args:
            self.parameters.append(arg.arg)
        
        self.generic_visit(node)
    
    def visit_Import(self, node):
        for alias in node.names:
            self.imports.append(alias.name)
    
    def visit_ImportFrom(self, node):
        if node.module:
            for alias in node.names:
                self.imports.append(f"{node.module}.{alias.name}")
    
    def visit_Assign(self, node):
        for target in node.targets:
            if isinstance(target, ast.Name):
                self.variables.append(target.id)
        self.assignments.append(node)
        self.generic_visit(node)
    
    def visit_If(self, node):
        self.if_statements.append(node)
        self.generic_visit(node)
    
    def visit_For(self, node):
        self.loops.append(node)
        self.generic_visit(node)
    
    def visit_While(self, node):
        self.loops.append(node)
        self.generic_visit(node)

class AIStrategyAnalyzer:
    """AI-powered strategy analysis using LLM"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        # For now, we'll create rule-based analysis
        # Later can integrate with OpenAI/Anthropic APIs
    
    def generate_analysis(self, profile: StrategyProfile, code_analysis: Dict[str, Any]) -> StrategyProfile:
        """Generate comprehensive AI analysis"""
        
        # Generate summary
        profile.ai_summary = self._generate_summary(profile, code_analysis)
        
        # Analyze strengths and weaknesses
        profile.ai_strengths = self._analyze_strengths(profile, code_analysis)
        profile.ai_weaknesses = self._analyze_weaknesses(profile, code_analysis)
        
        # Generate recommendations
        profile.ai_recommendations = self._generate_recommendations(profile, code_analysis)
        
        # Assess market suitability
        profile.ai_market_suitability = self._assess_market_suitability(profile)
        
        # Generate full report
        profile.full_report = self._generate_full_report(profile)
        
        return profile
    
    def _generate_summary(self, profile: StrategyProfile, analysis: Dict[str, Any]) -> str:
        """Generate strategy summary"""
        indicators = ", ".join(profile.indicators_used) if profile.indicators_used else "basic price action"
        
        summary = f"""
This is a {profile.strategy_type} strategy implemented in {profile.language} with {profile.complexity_score:.0f}/100 complexity score.

The strategy utilizes {len(profile.indicators_used)} technical indicators: {indicators}.

Key characteristics:
- {profile.lines_of_code} lines of code with {profile.functions_count} functions
- Signal generation based on {', '.join(analysis.get('signal_analysis', {}).get('signal_types', ['price action']))}
- {'Includes' if profile.has_risk_management else 'Lacks'} risk management features
- Estimated trading frequency: {profile.expected_frequency}
        """.strip()
        
        return summary
    
    def _analyze_strengths(self, profile: StrategyProfile, analysis: Dict[str, Any]) -> List[str]:
        """Identify strategy strengths"""
        strengths = []
        
        if profile.complexity_score > 70:
            strengths.append("Sophisticated algorithm with advanced logic")
        elif profile.complexity_score > 40:
            strengths.append("Well-structured strategy with good complexity balance")
        else:
            strengths.append("Simple and easy to understand implementation")
        
        if len(profile.indicators_used) > 3:
            strengths.append("Multi-indicator approach reduces false signals")
        elif len(profile.indicators_used) > 0:
            strengths.append("Uses established technical indicators")
        
        if profile.has_risk_management:
            strengths.append("Includes risk management features")
        
        if profile.has_stop_loss:
            strengths.append("Implements stop-loss protection")
        
        if profile.has_position_sizing:
            strengths.append("Includes position sizing logic")
        
        if profile.strategy_type != "unknown":
            strengths.append(f"Clear {profile.strategy_type} strategy classification")
        
        # Add more based on code analysis
        signal_types = analysis.get('signal_analysis', {}).get('signal_types', [])
        if len(signal_types) > 1:
            strengths.append("Multiple signal confirmation methods")
        
        return strengths
    
    def _analyze_weaknesses(self, profile: StrategyProfile, analysis: Dict[str, Any]) -> List[str]:
        """Identify potential weaknesses"""
        weaknesses = []
        
        if not profile.has_risk_management:
            weaknesses.append("No explicit risk management detected")
        
        if not profile.has_stop_loss:
            weaknesses.append("Missing stop-loss protection")
        
        if not profile.has_position_sizing:
            weaknesses.append("No position sizing strategy detected")
        
        if len(profile.indicators_used) == 0:
            weaknesses.append("Relies solely on price action without technical indicators")
        elif len(profile.indicators_used) > 5:
            weaknesses.append("Over-optimization risk with too many indicators")
        
        if profile.complexity_score < 20:
            weaknesses.append("May be overly simplistic for complex market conditions")
        elif profile.complexity_score > 80:
            weaknesses.append("High complexity may lead to over-fitting")
        
        if profile.strategy_type == "unknown":
            weaknesses.append("Unclear strategy classification may indicate mixed signals")
        
        return weaknesses
    
    def _generate_recommendations(self, profile: StrategyProfile, analysis: Dict[str, Any]) -> List[str]:
        """Generate improvement recommendations"""
        recommendations = []
        
        if not profile.has_risk_management:
            recommendations.append("Add risk management rules (max drawdown, position limits)")
        
        if not profile.has_stop_loss:
            recommendations.append("Implement stop-loss mechanisms to limit downside risk")
        
        if len(profile.indicators_used) < 2:
            recommendations.append("Consider adding confirmation indicators to reduce false signals")
        
        if profile.strategy_type == "trend_following":
            recommendations.append("Test performance in sideways markets and consider range filters")
        elif profile.strategy_type == "mean_reversion":
            recommendations.append("Validate effectiveness in trending markets")
        
        if profile.complexity_score > 70:
            recommendations.append("Consider simplification to avoid over-fitting")
        
        recommendations.append("Backtest across multiple market conditions and timeframes")
        recommendations.append("Implement walk-forward analysis for robust validation")
        
        return recommendations
    
    def _assess_market_suitability(self, profile: StrategyProfile) -> str:
        """Assess which market conditions suit this strategy"""
        suitability = []
        
        if profile.strategy_type == "trend_following":
            suitability.append("Strong trending markets")
            suitability.append("High volatility periods")
        elif profile.strategy_type == "mean_reversion":
            suitability.append("Range-bound markets")
            suitability.append("Low to medium volatility")
        elif profile.strategy_type == "momentum":
            suitability.append("Markets with strong directional moves")
        elif profile.strategy_type == "scalping":
            suitability.append("High-frequency trading environments")
            suitability.append("Low spread markets")
        
        if "RSI" in profile.indicators_used:
            suitability.append("Works well in oversold/overbought conditions")
        
        if "MACD" in profile.indicators_used:
            suitability.append("Effective in trending markets with momentum shifts")
        
        return "; ".join(suitability) if suitability else "General market conditions"
    
    def _generate_full_report(self, profile: StrategyProfile) -> str:
        """Generate comprehensive analysis report"""
        report = f"""
# Strategy Analysis Report: {profile.name}

**Generated on:** {profile.analysis_timestamp.strftime('%Y-%m-%d %H:%M:%S')}
**Author:** {profile.author}
**Language:** {profile.language}

## Executive Summary
{profile.ai_summary}

## Technical Analysis

### Strategy Classification
- **Type:** {profile.strategy_type.title().replace('_', ' ')}
- **Trading Style:** {profile.trading_style.title()}
- **Time Horizon:** {profile.time_horizon.title()}
- **Risk Level:** {profile.expected_risk_level.title()}

### Code Metrics
- **Lines of Code:** {profile.lines_of_code}
- **Functions:** {profile.functions_count}
- **Complexity Score:** {profile.complexity_score:.1f}/100
- **Technical Indicators:** {len(profile.indicators_used)}

### Technical Indicators Used
{chr(10).join(f"- {indicator}" for indicator in profile.indicators_used) if profile.indicators_used else "- Price action only"}

### Signal Logic
**Entry Conditions:**
{chr(10).join(f"- {condition}" for condition in profile.entry_conditions) if profile.entry_conditions else "- Basic price-based entries"}

**Exit Conditions:**
{chr(10).join(f"- {condition}" for condition in profile.exit_conditions) if profile.exit_conditions else "- Basic price-based exits"}

### Risk Management Features
- **Stop Loss:** {'✅ Implemented' if profile.has_stop_loss else '❌ Not detected'}
- **Take Profit:** {'✅ Implemented' if profile.has_take_profit else '❌ Not detected'}
- **Position Sizing:** {'✅ Implemented' if profile.has_position_sizing else '❌ Not detected'}
- **Risk Controls:** {'✅ Present' if profile.has_risk_management else '❌ Missing'}

## Strengths
{chr(10).join(f"✅ {strength}" for strength in profile.ai_strengths)}

## Potential Weaknesses
{chr(10).join(f"⚠️ {weakness}" for weakness in profile.ai_weaknesses)}

## Recommendations
{chr(10).join(f"🔧 {rec}" for rec in profile.ai_recommendations)}

## Market Suitability
**Best suited for:** {profile.ai_market_suitability}

## Performance Expectations
- **Expected Win Rate:** {f"{profile.expected_win_rate:.1f}%" if profile.expected_win_rate else "To be determined through backtesting"}
- **Trading Frequency:** {profile.expected_frequency.title()}
- **Risk Level:** {profile.expected_risk_level.title()}

---
*This analysis was generated using Epic 5 AI Strategy Profiler. Always validate findings through comprehensive backtesting.*
        """.strip()
        
        return report

class StrategyProfiler:
    """Main strategy profiling system"""
    
    def __init__(self, ai_api_key: str = None):
        self.code_analyzer = StrategyCodeAnalyzer()
        self.ai_analyzer = AIStrategyAnalyzer(ai_api_key)
        logger.info("Strategy Profiler initialized")
    
    def profile_strategy(self, strategy_id: str, name: str, source_code: str, 
                        language: str = "python", author: str = "Unknown") -> StrategyProfile:
        """Generate comprehensive strategy profile"""
        
        logger.info(f"Profiling strategy: {name}")
        
        # Initialize profile
        profile = StrategyProfile(
            strategy_id=strategy_id,
            name=name,
            language=language,
            author=author
        )
        
        # Analyze code structure
        code_analysis = self.code_analyzer.analyze_code(source_code, name)
        
        if 'error' in code_analysis:
            logger.error(f"Code analysis failed: {code_analysis['error']}")
            profile.ai_summary = f"Code analysis failed: {code_analysis['error']}"
            return profile
        
        # Populate profile from code analysis
        profile.lines_of_code = code_analysis.get('lines_of_code', 0)
        profile.functions_count = code_analysis.get('functions_count', 0)
        profile.imports_count = code_analysis.get('imports_count', 0)
        profile.complexity_score = code_analysis.get('complexity_score', 0.0)
        profile.indicators_used = code_analysis.get('indicators_used', [])
        profile.strategy_type = code_analysis.get('strategy_type', 'unknown')
        profile.parameters = code_analysis.get('parameters', {})
        
        # Extract risk management features
        risk_features = code_analysis.get('risk_management', {})
        profile.has_stop_loss = risk_features.get('has_stop_loss', False)
        profile.has_take_profit = risk_features.get('has_take_profit', False)
        profile.has_position_sizing = risk_features.get('has_position_sizing', False)
        profile.has_risk_management = any(risk_features.values())
        
        # Set expectations based on analysis
        profile.expected_frequency = self._estimate_frequency(profile)
        profile.expected_risk_level = self._estimate_risk_level(profile)
        
        # Generate AI analysis
        profile = self.ai_analyzer.generate_analysis(profile, code_analysis)
        
        logger.info(f"Strategy profiling completed for: {name}")
        return profile
    
    def _estimate_frequency(self, profile: StrategyProfile) -> str:
        """Estimate trading frequency based on strategy characteristics"""
        if profile.strategy_type == "scalping":
            return "high"
        elif profile.strategy_type in ["momentum", "breakout"]:
            return "medium"
        elif profile.strategy_type in ["trend_following", "mean_reversion"]:
            return "low"
        else:
            return "medium"
    
    def _estimate_risk_level(self, profile: StrategyProfile) -> str:
        """Estimate risk level based on strategy features"""
        risk_score = 0
        
        # Risk factors
        if not profile.has_stop_loss:
            risk_score += 2
        if not profile.has_risk_management:
            risk_score += 2
        if profile.strategy_type == "scalping":
            risk_score += 1
        if len(profile.indicators_used) == 0:
            risk_score += 1
        if profile.complexity_score > 80:
            risk_score += 1
        
        if risk_score >= 4:
            return "high"
        elif risk_score >= 2:
            return "medium"
        else:
            return "low"
    
    def save_profile(self, profile: StrategyProfile, file_path: str = None) -> str:
        """Save strategy profile to file"""
        if not file_path:
            file_path = f"strategy_profile_{profile.strategy_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Convert profile to dictionary for JSON serialization
        profile_dict = {
            'strategy_id': profile.strategy_id,
            'name': profile.name,
            'language': profile.language,
            'author': profile.author,
            'complexity_score': profile.complexity_score,
            'lines_of_code': profile.lines_of_code,
            'functions_count': profile.functions_count,
            'imports_count': profile.imports_count,
            'strategy_type': profile.strategy_type,
            'trading_style': profile.trading_style,
            'time_horizon': profile.time_horizon,
            'indicators_used': profile.indicators_used,
            'signal_types': profile.signal_types,
            'has_stop_loss': profile.has_stop_loss,
            'has_take_profit': profile.has_take_profit,
            'has_position_sizing': profile.has_position_sizing,
            'has_risk_management': profile.has_risk_management,
            'ai_summary': profile.ai_summary,
            'ai_strengths': profile.ai_strengths,
            'ai_weaknesses': profile.ai_weaknesses,
            'ai_recommendations': profile.ai_recommendations,
            'ai_market_suitability': profile.ai_market_suitability,
            'expected_win_rate': profile.expected_win_rate,
            'expected_risk_level': profile.expected_risk_level,
            'expected_frequency': profile.expected_frequency,
            'full_report': profile.full_report,
            'analysis_timestamp': profile.analysis_timestamp.isoformat()
        }
        
        with open(file_path, 'w') as f:
            json.dump(profile_dict, f, indent=2)
        
        logger.info(f"Strategy profile saved to: {file_path}")
        return file_path