"""
Epic 6: AI-Powered Strategy Analysis Engine
Intelligent Pine Script and Python strategy decomposition and feature extraction
"""

import re
import ast
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import pandas as pd

logger = logging.getLogger(__name__)

class StrategyType(Enum):
    TREND_FOLLOWING = "trend_following"
    MEAN_REVERSION = "mean_reversion"
    MOMENTUM = "momentum"
    ARBITRAGE = "arbitrage"
    MARKET_MAKING = "market_making"
    BREAKOUT = "breakout"
    SCALPING = "scalping"
    SWING_TRADING = "swing_trading"
    HYBRID = "hybrid"
    UNKNOWN = "unknown"

class TradingComponent(Enum):
    ENTRY_LOGIC = "entry_logic"
    EXIT_LOGIC = "exit_logic"
    STOP_LOSS = "stop_loss"
    TAKE_PROFIT = "take_profit"
    POSITION_SIZING = "position_sizing"
    RISK_MANAGEMENT = "risk_management"
    FILTERS = "filters"
    REGIME_DETECTION = "regime_detection"
    TIME_FILTERS = "time_filters"
    TECHNICAL_INDICATORS = "technical_indicators"
    MARKET_CONDITIONS = "market_conditions"

@dataclass
class StrategyParameter:
    """Represents a strategy parameter/setting"""
    name: str
    param_type: str  # int, float, bool, string
    default_value: Any
    min_value: Optional[Any] = None
    max_value: Optional[Any] = None
    step: Optional[float] = None
    title: Optional[str] = None
    group: Optional[str] = None
    tooltip: Optional[str] = None
    options: Optional[List[str]] = None  # For dropdown/selection parameters

@dataclass
class TradingLogic:
    """Represents extracted trading logic"""
    component: TradingComponent
    conditions: List[str]
    indicators_used: List[str]
    parameters_used: List[str]
    code_snippet: str
    logic_type: str  # 'long', 'short', 'both'
    priority: int = 1

@dataclass
class StrategyFeatures:
    """Complete strategy feature extraction results"""
    # Basic identification
    strategy_name: str
    strategy_type: StrategyType
    description: str
    
    # Parameters and settings
    parameters: List[StrategyParameter] = field(default_factory=list)
    
    # Trading components
    entry_logic: List[TradingLogic] = field(default_factory=list)
    exit_logic: List[TradingLogic] = field(default_factory=list)
    risk_management: List[TradingLogic] = field(default_factory=list)
    filters: List[TradingLogic] = field(default_factory=list)
    
    # Technical analysis
    indicators: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    timeframes: List[str] = field(default_factory=list)
    
    # Market conditions
    regime_detection: List[str] = field(default_factory=list)
    market_conditions: List[str] = field(default_factory=list)
    
    # UI and settings
    input_groups: Dict[str, List[str]] = field(default_factory=dict)
    plot_elements: List[Dict[str, Any]] = field(default_factory=list)
    
    # Metadata
    complexity_score: float = 0.0
    estimated_performance: Dict[str, Any] = field(default_factory=dict)
    conversion_confidence: float = 0.0

class AIStrategyAnalyzer:
    """
    AI-Powered Strategy Analysis Engine
    
    Analyzes Pine Script and Python strategies like a quantitative developer,
    extracting all trading components, logic patterns, and parameters.
    """
    
    def __init__(self):
        self.pine_patterns = self._load_pine_patterns()
        self.python_patterns = self._load_python_patterns()
        self.indicator_mappings = self._load_indicator_mappings()
        
    def _load_pine_patterns(self) -> Dict[str, List[str]]:
        """Load Pine Script pattern recognition rules"""
        return {
            'entry_patterns': [
                r'strategy\.entry\s*\(',
                r'if\s+.*\s*and\s+.*strategy\.position_size\s*==\s*0',
                r'longCondition\s*=\s*.*',
                r'shortCondition\s*=\s*.*',
                r'buy.*signal',
                r'sell.*signal'
            ],
            'exit_patterns': [
                r'strategy\.exit\s*\(',
                r'strategy\.close\s*\(',
                r'strategy\.close_all\s*\(',
                r'if\s+.*\s*and\s+strategy\.position_size\s*[!<>]=\s*0'
            ],
            'stop_loss_patterns': [
                r'stop\s*=\s*.*',
                r'stopLoss\s*=\s*.*',
                r'sl\s*=\s*.*',
                r'stop_loss\s*=\s*.*'
            ],
            'take_profit_patterns': [
                r'limit\s*=\s*.*',
                r'takeProfit\s*=\s*.*',
                r'tp\s*=\s*.*',
                r'take_profit\s*=\s*.*'
            ],
            'indicator_patterns': [
                r'ta\.(\w+)\s*\(',
                r'(\w+)\s*=\s*ta\.(\w+)\s*\(',
                r'sma\s*\(',
                r'ema\s*\(',
                r'rsi\s*\(',
                r'macd\s*\(',
                r'stoch\s*\(',
                r'bb\s*\(',
                r'atr\s*\('
            ],
            'parameter_patterns': [
                r'input\s*\.\s*(\w+)\s*\(',
                r'input\.(\w+)\s*\(',
                r'(\w+)\s*=\s*input\.',
            ],
            'regime_patterns': [
                r'adx\s*>\s*\d+',
                r'volatility',
                r'trend.*regime',
                r'market.*structure',
                r'bull.*market',
                r'bear.*market'
            ]
        }
    
    def _load_python_patterns(self) -> Dict[str, List[str]]:
        """Load Python strategy pattern recognition rules"""
        return {
            'entry_patterns': [
                r'entries\s*=\s*.*',
                r'long_entries\s*=\s*.*',
                r'short_entries\s*=\s*.*',
                r'entry_signals?\s*=\s*.*',
                r'buy.*condition',
                r'sell.*condition'
            ],
            'exit_patterns': [
                r'exits\s*=\s*.*',
                r'long_exits\s*=\s*.*',
                r'short_exits\s*=\s*.*',
                r'exit_signals?\s*=\s*.*'
            ],
            'indicator_patterns': [
                r'ta\.(\w+)\s*\(',
                r'(\w+)\s*=\s*ta\.(\w+)\s*\(',
                r'talib\.(\w+)\s*\(',
                r'pandas_ta\.(\w+)\s*\('
            ],
            'parameter_patterns': [
                r'(\w+)\s*=\s*params\.get\(',
                r'PARAMS\s*=\s*{.*}',
                r'def.*\*\*params'
            ]
        }
    
    def _load_indicator_mappings(self) -> Dict[str, Dict[str, Any]]:
        """Load technical indicator mappings and metadata"""
        return {
            'rsi': {
                'name': 'Relative Strength Index',
                'type': 'momentum',
                'default_period': 14,
                'range': [0, 100],
                'signals': ['overbought', 'oversold']
            },
            'sma': {
                'name': 'Simple Moving Average',
                'type': 'trend',
                'default_period': 20,
                'signals': ['trend_direction', 'crossover']
            },
            'ema': {
                'name': 'Exponential Moving Average', 
                'type': 'trend',
                'default_period': 12,
                'signals': ['trend_direction', 'crossover']
            },
            'macd': {
                'name': 'Moving Average Convergence Divergence',
                'type': 'momentum',
                'signals': ['signal_line_cross', 'zero_line_cross', 'histogram']
            },
            'bb': {
                'name': 'Bollinger Bands',
                'type': 'volatility',
                'signals': ['band_squeeze', 'band_break', 'mean_reversion']
            },
            'atr': {
                'name': 'Average True Range',
                'type': 'volatility',
                'signals': ['volatility_regime', 'stop_loss_sizing']
            },
            'stoch': {
                'name': 'Stochastic Oscillator',
                'type': 'momentum',
                'range': [0, 100],
                'signals': ['overbought', 'oversold']
            },
            'adx': {
                'name': 'Average Directional Index',
                'type': 'trend_strength',
                'range': [0, 100],
                'signals': ['trend_strength']
            }
        }
    
    def analyze_strategy(self, code: str, language: str = "pine") -> StrategyFeatures:
        """
        Main analysis method - analyzes strategy code like a quant developer
        
        Args:
            code: Strategy source code
            language: 'pine' or 'python'
            
        Returns:
            StrategyFeatures: Comprehensive feature extraction
        """
        logger.info(f"Starting AI strategy analysis for {language} code")
        
        # Initialize features
        features = StrategyFeatures(
            strategy_name=self._extract_strategy_name(code, language),
            strategy_type=StrategyType.UNKNOWN,
            description=self._extract_description(code, language)
        )
        
        # Extract all components
        features.parameters = self._extract_parameters(code, language)
        features.entry_logic = self._extract_entry_logic(code, language)
        features.exit_logic = self._extract_exit_logic(code, language)
        features.risk_management = self._extract_risk_management(code, language)
        features.filters = self._extract_filters(code, language)
        features.indicators = self._extract_indicators(code, language)
        features.timeframes = self._extract_timeframes(code, language)
        features.regime_detection = self._extract_regime_detection(code, language)
        features.market_conditions = self._extract_market_conditions(code, language)
        features.input_groups = self._extract_input_groups(code, language)
        features.plot_elements = self._extract_plot_elements(code, language)
        
        # Classify strategy type
        features.strategy_type = self._classify_strategy_type(features)
        
        # Calculate complexity and confidence scores
        features.complexity_score = self._calculate_complexity_score(features)
        features.conversion_confidence = self._calculate_conversion_confidence(features, language)
        
        # Estimate performance characteristics
        features.estimated_performance = self._estimate_performance(features)
        
        logger.info(f"Analysis complete: {features.strategy_type.value} strategy with {features.complexity_score:.2f} complexity")
        
        return features
    
    def _extract_strategy_name(self, code: str, language: str) -> str:
        """Extract strategy name from code"""
        if language == "pine":
            # Look for strategy() declaration
            match = re.search(r'strategy\s*\(\s*["\']([^"\']+)["\']', code)
            if match:
                return match.group(1)
        else:  # python
            # Look for STRATEGY_NAME or similar
            match = re.search(r'STRATEGY_NAME\s*=\s*["\']([^"\']+)["\']', code)
            if match:
                return match.group(1)
                
        return "Unknown Strategy"
    
    def _extract_description(self, code: str, language: str) -> str:
        """Extract strategy description"""
        # Look for comments at the beginning
        lines = code.split('\n')[:10]  # First 10 lines
        descriptions = []
        
        for line in lines:
            line = line.strip()
            if language == "pine" and line.startswith('//'):
                desc = line[2:].strip()
                if desc and not desc.startswith('@'):
                    descriptions.append(desc)
            elif language == "python" and (line.startswith('#') or '"""' in line):
                if line.startswith('#'):
                    descriptions.append(line[1:].strip())
                elif '"""' in line:
                    # Extract docstring content
                    match = re.search(r'"""([^"]+)"""', line)
                    if match:
                        descriptions.append(match.group(1).strip())
        
        return ' '.join(descriptions) if descriptions else "No description available"
    
    def _extract_parameters(self, code: str, language: str) -> List[StrategyParameter]:
        """Extract all strategy parameters and settings"""
        parameters = []
        
        if language == "pine":
            # Pine Script input patterns
            input_pattern = r'(\w+)\s*=\s*input\.(\w+)\s*\(\s*title\s*=\s*["\']([^"\']+)["\'].*?(?:defval\s*=\s*([^,\)]+)).*?(?:minval\s*=\s*([^,\)]+)).*?(?:maxval\s*=\s*([^,\)]+)).*?(?:group\s*=\s*["\']([^"\']+)["\'])?'
            
            for match in re.finditer(input_pattern, code, re.MULTILINE | re.DOTALL):
                param_name = match.group(1)
                param_type = match.group(2)
                title = match.group(3)
                default = match.group(4)
                min_val = match.group(5)
                max_val = match.group(6)
                group = match.group(7)
                
                # Convert types
                py_type = {
                    'int': 'int',
                    'float': 'float', 
                    'bool': 'bool',
                    'string': 'str'
                }.get(param_type, 'str')
                
                parameters.append(StrategyParameter(
                    name=param_name,
                    param_type=py_type,
                    default_value=self._parse_value(default, py_type),
                    min_value=self._parse_value(min_val, py_type) if min_val else None,
                    max_value=self._parse_value(max_val, py_type) if max_val else None,
                    title=title,
                    group=group
                ))
        
        else:  # python
            # Look for PARAMS dictionary or similar
            params_pattern = r'PARAMS\s*=\s*{([^}]+)}'
            match = re.search(params_pattern, code, re.MULTILINE | re.DOTALL)
            
            if match:
                params_content = match.group(1)
                # Parse individual parameters
                param_lines = re.findall(r'["\'](\w+)["\']\s*:\s*([^,\n]+)', params_content)
                
                for param_name, param_value in param_lines:
                    param_type = self._infer_type(param_value)
                    
                    parameters.append(StrategyParameter(
                        name=param_name,
                        param_type=param_type,
                        default_value=self._parse_value(param_value, param_type),
                        title=param_name.replace('_', ' ').title()
                    ))
        
        return parameters
    
    def _extract_entry_logic(self, code: str, language: str) -> List[TradingLogic]:
        """Extract entry logic and conditions"""
        entry_logic = []
        patterns = self.pine_patterns['entry_patterns'] if language == "pine" else self.python_patterns['entry_patterns']
        
        for pattern in patterns:
            matches = re.finditer(pattern, code, re.MULTILINE | re.IGNORECASE)
            for match in matches:
                # Extract the full line/block
                line_start = code.rfind('\n', 0, match.start()) + 1
                line_end = code.find('\n', match.end())
                if line_end == -1:
                    line_end = len(code)
                
                code_snippet = code[line_start:line_end].strip()
                
                # Analyze conditions
                conditions = self._extract_conditions(code_snippet)
                indicators = self._find_indicators_in_snippet(code_snippet)
                
                entry_logic.append(TradingLogic(
                    component=TradingComponent.ENTRY_LOGIC,
                    conditions=conditions,
                    indicators_used=indicators,
                    parameters_used=self._find_parameters_in_snippet(code_snippet),
                    code_snippet=code_snippet,
                    logic_type=self._determine_logic_type(code_snippet)
                ))
        
        return entry_logic
    
    def _extract_exit_logic(self, code: str, language: str) -> List[TradingLogic]:
        """Extract exit logic and conditions"""
        exit_logic = []
        patterns = self.pine_patterns['exit_patterns'] if language == "pine" else self.python_patterns['exit_patterns']
        
        for pattern in patterns:
            matches = re.finditer(pattern, code, re.MULTILINE | re.IGNORECASE)
            for match in matches:
                line_start = code.rfind('\n', 0, match.start()) + 1
                line_end = code.find('\n', match.end())
                if line_end == -1:
                    line_end = len(code)
                
                code_snippet = code[line_start:line_end].strip()
                
                exit_logic.append(TradingLogic(
                    component=TradingComponent.EXIT_LOGIC,
                    conditions=self._extract_conditions(code_snippet),
                    indicators_used=self._find_indicators_in_snippet(code_snippet),
                    parameters_used=self._find_parameters_in_snippet(code_snippet),
                    code_snippet=code_snippet,
                    logic_type=self._determine_logic_type(code_snippet)
                ))
        
        return exit_logic
    
    def _extract_risk_management(self, code: str, language: str) -> List[TradingLogic]:
        """Extract risk management logic"""
        risk_logic = []
        
        # Look for stop loss, take profit, position sizing
        sl_patterns = self.pine_patterns['stop_loss_patterns']
        tp_patterns = self.pine_patterns['take_profit_patterns']
        
        all_patterns = sl_patterns + tp_patterns
        
        for pattern in all_patterns:
            matches = re.finditer(pattern, code, re.MULTILINE | re.IGNORECASE)
            for match in matches:
                line_start = code.rfind('\n', 0, match.start()) + 1
                line_end = code.find('\n', match.end())
                if line_end == -1:
                    line_end = len(code)
                
                code_snippet = code[line_start:line_end].strip()
                
                # Determine component type
                component = TradingComponent.RISK_MANAGEMENT
                if any(p in pattern for p in ['stop', 'sl']):
                    component = TradingComponent.STOP_LOSS
                elif any(p in pattern for p in ['limit', 'tp', 'profit']):
                    component = TradingComponent.TAKE_PROFIT
                
                risk_logic.append(TradingLogic(
                    component=component,
                    conditions=self._extract_conditions(code_snippet),
                    indicators_used=self._find_indicators_in_snippet(code_snippet),
                    parameters_used=self._find_parameters_in_snippet(code_snippet),
                    code_snippet=code_snippet,
                    logic_type='both'
                ))
        
        return risk_logic
    
    def _extract_filters(self, code: str, language: str) -> List[TradingLogic]:
        """Extract trading filters (time, regime, market condition filters)"""
        filters = []
        
        # Time filters
        time_patterns = [
            r'time\s*>=\s*timestamp',
            r'dayofweek\s*[<>=!]+\s*\d+',
            r'hour\s*[<>=!]+\s*\d+',
            r'inDateRange',
            r'session\.'
        ]
        
        # Regime filters  
        regime_patterns = self.pine_patterns['regime_patterns']
        
        all_patterns = time_patterns + regime_patterns
        
        for pattern in all_patterns:
            matches = re.finditer(pattern, code, re.MULTILINE | re.IGNORECASE)
            for match in matches:
                line_start = code.rfind('\n', 0, match.start()) + 1
                line_end = code.find('\n', match.end())
                if line_end == -1:
                    line_end = len(code)
                
                code_snippet = code[line_start:line_end].strip()
                
                component = TradingComponent.TIME_FILTERS if 'time' in pattern or 'day' in pattern or 'hour' in pattern else TradingComponent.REGIME_DETECTION
                
                filters.append(TradingLogic(
                    component=component,
                    conditions=self._extract_conditions(code_snippet),
                    indicators_used=self._find_indicators_in_snippet(code_snippet),
                    parameters_used=self._find_parameters_in_snippet(code_snippet),
                    code_snippet=code_snippet,
                    logic_type='both'
                ))
        
        return filters
    
    def _extract_indicators(self, code: str, language: str) -> Dict[str, Dict[str, Any]]:
        """Extract all technical indicators used"""
        indicators = {}
        patterns = self.pine_patterns['indicator_patterns'] if language == "pine" else self.python_patterns['indicator_patterns']
        
        for pattern in patterns:
            matches = re.finditer(pattern, code, re.MULTILINE | re.IGNORECASE)
            for match in matches:
                if match.groups():
                    indicator_name = match.group(1).lower()
                    if indicator_name in self.indicator_mappings:
                        
                        # Extract parameters used with this indicator
                        line_start = code.rfind('\n', 0, match.start()) + 1
                        line_end = code.find('\n', match.end())
                        if line_end == -1:
                            line_end = len(code)
                        
                        code_snippet = code[line_start:line_end].strip()
                        params = self._extract_indicator_parameters(code_snippet, indicator_name)
                        
                        indicators[indicator_name] = {
                            **self.indicator_mappings[indicator_name],
                            'parameters_used': params,
                            'code_usage': code_snippet
                        }
        
        return indicators
    
    def _extract_timeframes(self, code: str, language: str) -> List[str]:
        """Extract timeframes used"""
        timeframes = []
        
        # Common timeframe patterns
        tf_patterns = [
            r'timeframe\s*=\s*["\']([^"\']+)["\']',
            r'request\.security.*["\']([^"\']+)["\']',
            r'["\'](\d+[mhdwMY])["\']'
        ]
        
        for pattern in tf_patterns:
            matches = re.finditer(pattern, code)
            for match in matches:
                tf = match.group(1)
                if tf not in timeframes:
                    timeframes.append(tf)
        
        return timeframes if timeframes else ['1h']  # Default timeframe
    
    def _extract_regime_detection(self, code: str, language: str) -> List[str]:
        """Extract regime detection logic"""
        regimes = []
        
        # Look for regime-related variables and conditions
        regime_keywords = [
            'trending', 'sideways', 'bull', 'bear', 'volatile', 'calm',
            'regime', 'market_state', 'environment', 'condition'
        ]
        
        for keyword in regime_keywords:
            if keyword.lower() in code.lower():
                regimes.append(keyword)
        
        return regimes
    
    def _extract_market_conditions(self, code: str, language: str) -> List[str]:
        """Extract market condition requirements"""
        conditions = []
        
        market_keywords = [
            'volume', 'spread', 'gap', 'overnight', 'session',
            'market_hours', 'liquidity', 'volatility'
        ]
        
        for keyword in market_keywords:
            if keyword.lower() in code.lower():
                conditions.append(keyword)
        
        return conditions
    
    def _extract_input_groups(self, code: str, language: str) -> Dict[str, List[str]]:
        """Extract UI input groups"""
        groups = {}
        
        if language == "pine":
            # Find all group= parameters
            group_pattern = r'group\s*=\s*["\']([^"\']+)["\']'
            matches = re.finditer(group_pattern, code)
            
            for match in matches:
                group_name = match.group(1)
                if group_name not in groups:
                    groups[group_name] = []
        
        return groups
    
    def _extract_plot_elements(self, code: str, language: str) -> List[Dict[str, Any]]:
        """Extract plot/visualization elements"""
        plots = []
        
        if language == "pine":
            # Find all plot() calls
            plot_pattern = r'plot\s*\(\s*([^,\)]+).*?(?:title\s*=\s*["\']([^"\']+)["\'])?.*?(?:color\s*=\s*([^,\)]+))?'
            matches = re.finditer(plot_pattern, code, re.MULTILINE | re.DOTALL)
            
            for match in matches:
                plots.append({
                    'variable': match.group(1).strip(),
                    'title': match.group(2) if match.group(2) else match.group(1).strip(),
                    'color': match.group(3) if match.group(3) else 'blue',
                    'type': 'line'
                })
        
        return plots
    
    def _classify_strategy_type(self, features: StrategyFeatures) -> StrategyType:
        """Classify strategy type based on extracted features"""
        
        # Analyze indicators and logic patterns
        indicator_types = []
        for indicator_name, indicator_info in features.indicators.items():
            indicator_types.append(indicator_info.get('type', 'unknown'))
        
        # Analyze entry/exit logic
        logic_patterns = []
        for logic in features.entry_logic + features.exit_logic:
            logic_patterns.extend(logic.conditions)
        
        # Classification logic
        trend_indicators = sum(1 for t in indicator_types if t == 'trend')
        momentum_indicators = sum(1 for t in indicator_types if t == 'momentum')
        volatility_indicators = sum(1 for t in indicator_types if t == 'volatility')
        
        # Pattern analysis
        logic_text = ' '.join(logic_patterns).lower()
        
        if trend_indicators >= 2 and ('crossover' in logic_text or 'above' in logic_text):
            return StrategyType.TREND_FOLLOWING
        elif momentum_indicators >= 2 and ('oversold' in logic_text or 'overbought' in logic_text):
            return StrategyType.MEAN_REVERSION
        elif 'breakout' in logic_text or 'break' in logic_text:
            return StrategyType.BREAKOUT
        elif volatility_indicators >= 1 and ('scalp' in features.description.lower()):
            return StrategyType.SCALPING
        elif len(features.timeframes) > 1:
            return StrategyType.HYBRID
        else:
            return StrategyType.MOMENTUM  # Default classification
    
    def _calculate_complexity_score(self, features: StrategyFeatures) -> float:
        """Calculate strategy complexity score (0-10)"""
        score = 0.0
        
        # Parameters complexity
        score += min(len(features.parameters) * 0.1, 2.0)
        
        # Logic complexity
        score += min(len(features.entry_logic) * 0.3, 2.0)
        score += min(len(features.exit_logic) * 0.3, 2.0)
        score += min(len(features.risk_management) * 0.2, 1.0)
        score += min(len(features.filters) * 0.2, 1.0)
        
        # Indicator complexity
        score += min(len(features.indicators) * 0.2, 2.0)
        
        return min(score, 10.0)
    
    def _calculate_conversion_confidence(self, features: StrategyFeatures, language: str) -> float:
        """Calculate confidence in successful conversion (0-1)"""
        confidence = 0.8  # Base confidence
        
        # Reduce confidence for complex strategies
        if features.complexity_score > 7:
            confidence -= 0.2
        
        # Reduce confidence for unknown indicators
        for indicator_name in features.indicators:
            if indicator_name not in self.indicator_mappings:
                confidence -= 0.1
        
        # Language-specific adjustments
        if language == "python":
            confidence += 0.1  # Python to Python is easier
        
        return max(0.0, min(1.0, confidence))
    
    def _estimate_performance(self, features: StrategyFeatures) -> Dict[str, Any]:
        """Estimate potential performance characteristics"""
        
        # Basic performance estimation based on strategy type
        performance = {
            'expected_sharpe': 0.5,
            'expected_drawdown': 0.15,
            'trade_frequency': 'medium',
            'market_suitability': ['trending'],
            'risk_level': 'medium'
        }
        
        # Adjust based on strategy type
        if features.strategy_type == StrategyType.TREND_FOLLOWING:
            performance.update({
                'expected_sharpe': 0.7,
                'expected_drawdown': 0.12,
                'market_suitability': ['trending', 'bull_market']
            })
        elif features.strategy_type == StrategyType.MEAN_REVERSION:
            performance.update({
                'expected_sharpe': 0.9,
                'expected_drawdown': 0.08,
                'trade_frequency': 'high',
                'market_suitability': ['sideways', 'volatile']
            })
        elif features.strategy_type == StrategyType.SCALPING:
            performance.update({
                'trade_frequency': 'very_high',
                'risk_level': 'high',
                'expected_drawdown': 0.05
            })
        
        # Adjust for complexity
        if features.complexity_score > 6:
            performance['expected_sharpe'] *= 1.1  # More complex might be better
            performance['risk_level'] = 'high'
        
        return performance
    
    # Helper methods
    def _parse_value(self, value_str: str, value_type: str) -> Any:
        """Parse string value to appropriate type"""
        if not value_str:
            return None
            
        value_str = value_str.strip()
        
        try:
            if value_type == 'int':
                return int(float(value_str))
            elif value_type == 'float':
                return float(value_str)
            elif value_type == 'bool':
                return value_str.lower() in ['true', '1', 'yes']
            else:
                return value_str.strip('"\'')
        except:
            return value_str
    
    def _infer_type(self, value_str: str) -> str:
        """Infer type from value string"""
        value_str = value_str.strip()
        
        if value_str.lower() in ['true', 'false']:
            return 'bool'
        elif '.' in value_str:
            try:
                float(value_str)
                return 'float'
            except:
                return 'str'
        else:
            try:
                int(value_str)
                return 'int'
            except:
                return 'str'
    
    def _extract_conditions(self, code_snippet: str) -> List[str]:
        """Extract trading conditions from code snippet"""
        conditions = []
        
        # Look for comparison operators and logical conditions
        condition_patterns = [
            r'(\w+)\s*[<>=!]+\s*(\w+|\d+\.?\d*)',
            r'(\w+)\s*and\s*(\w+)',
            r'(\w+)\s*or\s*(\w+)',
            r'crossover\s*\(\s*([^,]+),\s*([^)]+)\)',
            r'crossunder\s*\(\s*([^,]+),\s*([^)]+)\)'
        ]
        
        for pattern in condition_patterns:
            matches = re.finditer(pattern, code_snippet)
            for match in matches:
                conditions.append(match.group(0))
        
        return conditions
    
    def _find_indicators_in_snippet(self, code_snippet: str) -> List[str]:
        """Find indicators used in code snippet"""
        indicators = []
        
        for indicator_name in self.indicator_mappings.keys():
            if indicator_name in code_snippet.lower():
                indicators.append(indicator_name)
        
        return indicators
    
    def _find_parameters_in_snippet(self, code_snippet: str) -> List[str]:
        """Find parameters used in code snippet"""
        # Look for variable names that might be parameters
        param_pattern = r'\b([a-zA-Z_][a-zA-Z0-9_]*)\b'
        matches = re.finditer(param_pattern, code_snippet)
        
        parameters = []
        for match in matches:
            var_name = match.group(1)
            # Filter out common keywords/functions
            if var_name not in ['and', 'or', 'not', 'true', 'false', 'if', 'else', 'ta', 'strategy']:
                parameters.append(var_name)
        
        return list(set(parameters))  # Remove duplicates
    
    def _determine_logic_type(self, code_snippet: str) -> str:
        """Determine if logic is for long, short, or both positions"""
        snippet_lower = code_snippet.lower()
        
        if 'long' in snippet_lower or 'buy' in snippet_lower:
            return 'long'
        elif 'short' in snippet_lower or 'sell' in snippet_lower:
            return 'short'
        else:
            return 'both'
    
    def _extract_indicator_parameters(self, code_snippet: str, indicator_name: str) -> List[str]:
        """Extract parameters used with a specific indicator"""
        # Look for function call with parameters
        pattern = f'{indicator_name}\\s*\\(([^)]+)\\)'
        match = re.search(pattern, code_snippet)
        
        if match:
            params_str = match.group(1)
            # Split by comma and clean up
            params = [p.strip() for p in params_str.split(',')]
            return params
        
        return []

# Example usage and testing
if __name__ == "__main__":
    analyzer = AIStrategyAnalyzer()
    
    # Test with a Pine Script example
    pine_code = '''
    //@version=5
    strategy("RSI Strategy", overlay=true)
    
    rsiLength = input.int(14, title="RSI Length", minval=1, maxval=50, group="RSI Settings")
    rsiOverbought = input.float(70.0, title="Overbought Level", minval=50, maxval=100, group="RSI Settings")
    rsiOversold = input.float(30.0, title="Oversold Level", minval=0, maxval=50, group="RSI Settings")
    
    rsi = ta.rsi(close, rsiLength)
    
    longCondition = rsi < rsiOversold
    shortCondition = rsi > rsiOverbought
    
    if longCondition
        strategy.entry("Long", strategy.long)
        
    if shortCondition
        strategy.entry("Short", strategy.short)
    '''
    
    features = analyzer.analyze_strategy(pine_code, "pine")
    print(f"Strategy: {features.strategy_name}")
    print(f"Type: {features.strategy_type.value}")
    print(f"Parameters: {len(features.parameters)}")
    print(f"Complexity: {features.complexity_score:.2f}")
    print(f"Confidence: {features.conversion_confidence:.2f}")