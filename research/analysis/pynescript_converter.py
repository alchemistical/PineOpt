"""
Epic 6: PyneScript Integration for Advanced Pine Script Conversion
Uses PyneScript library for accurate Pine Script to Python conversion
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import re
import json

# PyneScript imports
try:
    import pynescript as ps
    from pynescript import PineScript
    PYNESCRIPT_AVAILABLE = True
except ImportError:
    PYNESCRIPT_AVAILABLE = False
    print("PyneScript not available. Install with: pip install pynescript")

from .ai_strategy_analyzer import AIStrategyAnalyzer, StrategyFeatures, StrategyParameter

logger = logging.getLogger(__name__)

@dataclass
class ConversionResult:
    """Results of Pine Script to Python conversion"""
    success: bool
    python_code: str
    strategy_features: StrategyFeatures
    settings_panel: Dict[str, Any]
    ui_components: List[Dict[str, Any]]
    conversion_notes: List[str]
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'success': self.success,
            'python_code': self.python_code,
            'strategy_features': asdict(self.strategy_features),
            'settings_panel': self.settings_panel,
            'ui_components': self.ui_components,
            'conversion_notes': self.conversion_notes,
            'error_message': self.error_message
        }

class PynescriptConverter:
    """
    Advanced Pine Script to Python converter using PyneScript
    with AI-powered feature extraction and UI generation
    """
    
    def __init__(self):
        self.analyzer = AIStrategyAnalyzer()
        self.available = PYNESCRIPT_AVAILABLE
        self.conversion_templates = self._load_conversion_templates()
        self.ui_templates = self._load_ui_templates()
    
    def _load_conversion_templates(self) -> Dict[str, str]:
        """Load Python code generation templates"""
        return {
            'strategy_header': '''"""
{description}
Generated using Pine2Py with PyneScript integration
Strategy Type: {strategy_type}
Complexity Score: {complexity_score:.2f}
Conversion Confidence: {conversion_confidence:.2f}
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import logging

# Technical Analysis Libraries
import talib
import pandas_ta as ta
{pynescript_imports}

# Pine2Py Runtime
from pine2py.runtime import ta as pine_ta, nz, change, crossover, crossunder
from shared.types.strategy import StrategySignals, StrategyParameter, StrategyMetadata

logger = logging.getLogger(__name__)

STRATEGY_NAME = "{strategy_name}"
''',
            
            'parameters_section': '''
# Strategy Parameters
PARAMS = {
{param_definitions}
}

# Parameter Definitions for UI
PARAM_DEFINITIONS = [
{param_ui_definitions}
]
''',
            
            'indicators_section': '''
class TechnicalIndicators:
    """Technical indicator calculations using multiple libraries"""
    
    def __init__(self, data: pd.DataFrame):
        self.data = data
        self.close = data['close']
        self.high = data['high'] 
        self.low = data['low']
        self.open = data['open']
        self.volume = data['volume'] if 'volume' in data.columns else None
        
{indicator_methods}
''',
            
            'strategy_logic': '''
def build_signals(df: pd.DataFrame, **params) -> StrategySignals:
    """
    Build trading signals from OHLC data
    
    Strategy Logic:
{logic_description}
    
    Args:
        df: OHLC DataFrame with datetime index
        **params: Strategy parameters
        
    Returns:
        StrategySignals: Entry and exit signals
    """
    
    # Apply parameter defaults
    final_params = PARAMS.copy()
    final_params.update(params)
    
    # Initialize indicators
    indicators = TechnicalIndicators(df)
    
    # Initialize signals
    long_entries = pd.Series(False, index=df.index)
    short_entries = pd.Series(False, index=df.index)
    long_exits = pd.Series(False, index=df.index)
    short_exits = pd.Series(False, index=df.index)
    
    # Calculate all indicators
{indicator_calculations}
    
    # Entry Logic
{entry_logic}
    
    # Exit Logic  
{exit_logic}
    
    # Risk Management
{risk_management}
    
    # Combine signals
    entries = long_entries | short_entries
    exits = long_exits | short_exits
    
    return StrategySignals(
        entries=entries,
        exits=exits,
        long_entries=long_entries,
        short_entries=short_entries,
        long_exits=long_exits,
        short_exits=short_exits
    )
''',
            
            'metadata_section': '''
# Strategy metadata
METADATA = StrategyMetadata(
    name=STRATEGY_NAME,
    description="""{description}""",
    parameters=PARAM_DEFINITIONS,
    strategy_type="{strategy_type}",
    complexity_score={complexity_score},
    estimated_performance={estimated_performance}
)
'''
        }
    
    def _load_ui_templates(self) -> Dict[str, Any]:
        """Load UI component templates"""
        return {
            'settings_panel': {
                'type': 'panel',
                'title': 'Strategy Settings',
                'collapsible': True,
                'sections': []
            },
            'parameter_input': {
                'int': {
                    'component': 'NumberInput',
                    'props': ['min', 'max', 'step', 'default']
                },
                'float': {
                    'component': 'NumberInput',
                    'props': ['min', 'max', 'step', 'default', 'precision']
                },
                'bool': {
                    'component': 'Switch',
                    'props': ['default', 'label']
                },
                'str': {
                    'component': 'TextInput',
                    'props': ['default', 'placeholder']
                }
            },
            'gauge': {
                'component': 'Gauge',
                'props': ['min', 'max', 'value', 'title', 'color']
            },
            'chart_overlay': {
                'component': 'ChartOverlay',
                'props': ['series', 'color', 'lineWidth', 'style']
            }
        }
    
    def convert_strategy(self, pine_code: str, strategy_name: Optional[str] = None) -> ConversionResult:
        """
        Main conversion method - converts Pine Script to Python with full UI
        
        Args:
            pine_code: Pine Script source code
            strategy_name: Optional strategy name override
            
        Returns:
            ConversionResult: Complete conversion results
        """
        logger.info(f"Starting PyneScript conversion for strategy: {strategy_name or 'Unknown'}")
        
        try:
            # Step 1: AI Analysis - Extract all features
            features = self.analyzer.analyze_strategy(pine_code, "pine")
            
            if strategy_name:
                features.strategy_name = strategy_name
            
            logger.info(f"AI Analysis complete: {features.strategy_type.value} strategy, {len(features.parameters)} parameters")
            
            # Step 2: PyneScript Conversion (if available)
            pynescript_code = ""
            pynescript_notes = []
            
            if self.available:
                try:
                    # Use PyneScript for core conversion
                    ps_converter = PineScript(pine_code)
                    pynescript_result = ps_converter.to_python()
                    pynescript_code = pynescript_result.get('code', '')
                    pynescript_notes = pynescript_result.get('notes', [])
                    logger.info("PyneScript conversion successful")
                except Exception as e:
                    logger.warning(f"PyneScript conversion failed: {e}, using fallback")
                    pynescript_notes.append(f"PyneScript failed: {e}")
            else:
                pynescript_notes.append("PyneScript not available, using AI conversion")
            
            # Step 3: Generate Enhanced Python Code
            python_code = self._generate_python_code(features, pynescript_code)
            
            # Step 4: Generate UI Components and Settings Panel
            settings_panel = self._generate_settings_panel(features)
            ui_components = self._generate_ui_components(features)
            
            # Step 5: Compile conversion notes
            conversion_notes = self._generate_conversion_notes(features, pynescript_notes)
            
            logger.info(f"Conversion complete: {len(python_code)} chars of Python code generated")
            
            return ConversionResult(
                success=True,
                python_code=python_code,
                strategy_features=features,
                settings_panel=settings_panel,
                ui_components=ui_components,
                conversion_notes=conversion_notes
            )
            
        except Exception as e:
            logger.error(f"Conversion failed: {e}")
            return ConversionResult(
                success=False,
                python_code="",
                strategy_features=StrategyFeatures(
                    strategy_name=strategy_name or "Failed Strategy",
                    strategy_type="unknown",
                    description="Conversion failed"
                ),
                settings_panel={},
                ui_components=[],
                conversion_notes=[],
                error_message=str(e)
            )
    
    def _generate_python_code(self, features: StrategyFeatures, pynescript_code: str) -> str:
        """Generate complete Python strategy code"""
        
        # Prepare template variables
        template_vars = {
            'strategy_name': features.strategy_name,
            'description': features.description,
            'strategy_type': features.strategy_type.value,
            'complexity_score': features.complexity_score,
            'conversion_confidence': features.conversion_confidence,
            'estimated_performance': repr(features.estimated_performance),
            'pynescript_imports': self._generate_pynescript_imports(pynescript_code),
            'param_definitions': self._generate_param_definitions(features.parameters),
            'param_ui_definitions': self._generate_param_ui_definitions(features.parameters),
            'indicator_methods': self._generate_indicator_methods(features.indicators),
            'logic_description': self._generate_logic_description(features),
            'indicator_calculations': self._generate_indicator_calculations(features.indicators),
            'entry_logic': self._generate_entry_logic(features.entry_logic),
            'exit_logic': self._generate_exit_logic(features.exit_logic),
            'risk_management': self._generate_risk_management(features.risk_management)
        }
        
        # Generate complete code
        code_sections = []
        
        # Header
        code_sections.append(self.conversion_templates['strategy_header'].format(**template_vars))
        
        # Parameters
        code_sections.append(self.conversion_templates['parameters_section'].format(**template_vars))
        
        # Indicators
        code_sections.append(self.conversion_templates['indicators_section'].format(**template_vars))
        
        # Main strategy logic
        code_sections.append(self.conversion_templates['strategy_logic'].format(**template_vars))
        
        # Metadata
        code_sections.append(self.conversion_templates['metadata_section'].format(**template_vars))
        
        # Add PyneScript code as reference if available
        if pynescript_code:
            code_sections.append(f'''
# PyneScript Generated Code (Reference)
"""
{pynescript_code}
"""
''')
        
        return '\n'.join(code_sections)
    
    def _generate_pynescript_imports(self, pynescript_code: str) -> str:
        """Generate PyneScript-specific imports"""
        if not pynescript_code:
            return "# PyneScript not used"
        
        imports = []
        if 'pynescript' in pynescript_code:
            imports.append("import pynescript as ps")
        
        return '\n'.join(imports) if imports else "# No additional PyneScript imports needed"
    
    def _generate_param_definitions(self, parameters: List[StrategyParameter]) -> str:
        """Generate parameter definitions dictionary"""
        if not parameters:
            return "    # No parameters defined"
        
        param_lines = []
        for param in parameters:
            param_lines.append(f"    '{param.name}': {repr(param.default_value)},")
        
        return '\n'.join(param_lines)
    
    def _generate_param_ui_definitions(self, parameters: List[StrategyParameter]) -> str:
        """Generate UI parameter definitions"""
        if not parameters:
            return "    # No parameters for UI"
        
        ui_lines = []
        for param in parameters:
            ui_def = f"""    StrategyParameter(
        name='{param.name}',
        default={repr(param.default_value)},
        param_type='{param.param_type}',
        title='{param.title or param.name.replace('_', ' ').title()}',
        group='{param.group or 'General'}',
        min_val={repr(param.min_value)},
        max_val={repr(param.max_value)}
    ),"""
            ui_lines.append(ui_def)
        
        return '\n'.join(ui_lines)
    
    def _generate_indicator_methods(self, indicators: Dict[str, Dict[str, Any]]) -> str:
        """Generate indicator calculation methods"""
        if not indicators:
            return "        pass  # No indicators used"
        
        methods = []
        for indicator_name, indicator_info in indicators.items():
            method_name = f"calculate_{indicator_name}"
            
            # Generate method based on indicator type
            if indicator_name == 'rsi':
                method = f'''    def {method_name}(self, period: int = 14) -> pd.Series:
        """Calculate RSI using multiple methods for accuracy"""
        try:
            # Primary: TALib
            rsi = talib.RSI(self.close.values, timeperiod=period)
            return pd.Series(rsi, index=self.close.index)
        except:
            # Fallback: pandas_ta
            return ta.rsi(self.close, length=period)'''
            
            elif indicator_name == 'sma':
                method = f'''    def {method_name}(self, period: int = 20) -> pd.Series:
        """Calculate Simple Moving Average"""
        try:
            sma = talib.SMA(self.close.values, timeperiod=period)
            return pd.Series(sma, index=self.close.index)
        except:
            return self.close.rolling(window=period).mean()'''
            
            elif indicator_name == 'ema':
                method = f'''    def {method_name}(self, period: int = 12) -> pd.Series:
        """Calculate Exponential Moving Average"""
        try:
            ema = talib.EMA(self.close.values, timeperiod=period)
            return pd.Series(ema, index=self.close.index)
        except:
            return self.close.ewm(span=period).mean()'''
            
            elif indicator_name == 'macd':
                method = f'''    def {method_name}(self, fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """Calculate MACD"""
        try:
            macd, signal_line, histogram = talib.MACD(self.close.values, fastperiod=fast, slowperiod=slow, signalperiod=signal)
            return (
                pd.Series(macd, index=self.close.index),
                pd.Series(signal_line, index=self.close.index),
                pd.Series(histogram, index=self.close.index)
            )
        except:
            macd_data = ta.macd(self.close, fast=fast, slow=slow, signal=signal)
            return macd_data['MACD_12_26_9'], macd_data['MACDs_12_26_9'], macd_data['MACDh_12_26_9']'''
            
            else:
                # Generic indicator method
                method = f'''    def {method_name}(self, **kwargs) -> pd.Series:
        """Calculate {indicator_name.upper()}"""
        # Implementation needed for {indicator_name}
        return pd.Series(0, index=self.close.index)'''
            
            methods.append(method)
        
        return '\n\n'.join(methods)
    
    def _generate_logic_description(self, features: StrategyFeatures) -> str:
        """Generate strategy logic description"""
        description_parts = []
        
        # Entry logic
        if features.entry_logic:
            description_parts.append("    Entry Conditions:")
            for i, logic in enumerate(features.entry_logic, 1):
                description_parts.append(f"      {i}. {logic.logic_type.title()}: {', '.join(logic.conditions[:3])}")
        
        # Exit logic
        if features.exit_logic:
            description_parts.append("    Exit Conditions:")
            for i, logic in enumerate(features.exit_logic, 1):
                description_parts.append(f"      {i}. {logic.logic_type.title()}: {', '.join(logic.conditions[:3])}")
        
        # Risk management
        if features.risk_management:
            description_parts.append("    Risk Management:")
            for logic in features.risk_management:
                description_parts.append(f"      - {logic.component.value}: {logic.code_snippet[:50]}...")
        
        return '\n'.join(description_parts) if description_parts else "    # Basic strategy logic"
    
    def _generate_indicator_calculations(self, indicators: Dict[str, Dict[str, Any]]) -> str:
        """Generate indicator calculation code"""
        if not indicators:
            return "    # No indicators to calculate"
        
        calculations = []
        for indicator_name, indicator_info in indicators.items():
            params = indicator_info.get('parameters_used', [])
            
            # Generate calculation call
            if indicator_name == 'rsi':
                param_name = next((p for p in params if 'length' in p.lower() or 'period' in p.lower()), 'final_params["rsi_length"]')
                calc = f"    rsi = indicators.calculate_rsi(period={param_name})"
            elif indicator_name == 'sma':
                param_name = next((p for p in params if 'length' in p.lower() or 'period' in p.lower()), 'final_params.get("sma_length", 20)')
                calc = f"    sma = indicators.calculate_sma(period={param_name})"
            elif indicator_name == 'ema':
                param_name = next((p for p in params if 'length' in p.lower() or 'period' in p.lower()), 'final_params.get("ema_length", 12)')
                calc = f"    ema = indicators.calculate_ema(period={param_name})"
            elif indicator_name == 'macd':
                calc = f"    macd_line, signal_line, histogram = indicators.calculate_macd()"
            else:
                calc = f"    {indicator_name} = indicators.calculate_{indicator_name}()"
            
            calculations.append(calc)
        
        return '\n'.join(calculations)
    
    def _generate_entry_logic(self, entry_logic: List) -> str:
        """Generate entry logic code"""
        if not entry_logic:
            return "    # No entry logic defined"
        
        logic_lines = []
        
        for i, logic in enumerate(entry_logic):
            logic_type = logic.logic_type
            conditions = logic.conditions
            
            # Create condition string
            if conditions:
                condition_str = " & ".join([self._convert_condition_to_python(cond) for cond in conditions[:3]])
                
                if logic_type == 'long' or logic_type == 'both':
                    logic_lines.append(f"    # Entry Logic {i+1}: {logic_type}")
                    logic_lines.append(f"    long_condition_{i+1} = {condition_str}")
                    logic_lines.append(f"    long_entries = long_entries | long_condition_{i+1}")
                
                if logic_type == 'short' or logic_type == 'both':
                    # Invert conditions for short
                    inverted_condition = self._invert_condition_for_short(condition_str)
                    logic_lines.append(f"    short_condition_{i+1} = {inverted_condition}")
                    logic_lines.append(f"    short_entries = short_entries | short_condition_{i+1}")
        
        return '\n'.join(logic_lines) if logic_lines else "    # Entry logic to be implemented"
    
    def _generate_exit_logic(self, exit_logic: List) -> str:
        """Generate exit logic code"""
        if not exit_logic:
            return "    # No exit logic defined"
        
        logic_lines = []
        
        for i, logic in enumerate(exit_logic):
            conditions = logic.conditions
            
            if conditions:
                condition_str = " & ".join([self._convert_condition_to_python(cond) for cond in conditions[:3]])
                logic_lines.append(f"    # Exit Logic {i+1}")
                logic_lines.append(f"    exit_condition_{i+1} = {condition_str}")
                logic_lines.append(f"    long_exits = long_exits | exit_condition_{i+1}")
                logic_lines.append(f"    short_exits = short_exits | exit_condition_{i+1}")
        
        return '\n'.join(logic_lines) if logic_lines else "    # Exit logic to be implemented"
    
    def _generate_risk_management(self, risk_logic: List) -> str:
        """Generate risk management code"""
        if not risk_logic:
            return "    # No risk management defined"
        
        risk_lines = []
        
        for logic in risk_logic:
            if 'stop' in logic.code_snippet.lower():
                risk_lines.append("    # Stop Loss Logic")
                risk_lines.append("    # TODO: Implement stop loss from: " + logic.code_snippet[:50])
            elif 'profit' in logic.code_snippet.lower():
                risk_lines.append("    # Take Profit Logic")
                risk_lines.append("    # TODO: Implement take profit from: " + logic.code_snippet[:50])
        
        return '\n'.join(risk_lines) if risk_lines else "    # Risk management to be implemented"
    
    def _convert_condition_to_python(self, condition: str) -> str:
        """Convert Pine Script condition to Python pandas condition"""
        # Simple conversion rules
        condition = condition.replace('and', '&').replace('or', '|')
        condition = condition.replace('crossover', 'crossover')  # Keep as is, assuming function exists
        condition = condition.replace('crossunder', 'crossunder')
        
        return condition
    
    def _invert_condition_for_short(self, condition: str) -> str:
        """Invert condition for short entries"""
        # Simple inversion - replace > with <, etc.
        inverted = condition.replace('>', 'TEMP_GT').replace('<', '>').replace('TEMP_GT', '<')
        inverted = inverted.replace('>=', 'TEMP_GTE').replace('<=', '>=').replace('TEMP_GTE', '<=')
        
        return inverted
    
    def _generate_settings_panel(self, features: StrategyFeatures) -> Dict[str, Any]:
        """Generate UI settings panel configuration"""
        panel = self.ui_templates['settings_panel'].copy()
        panel['title'] = f"{features.strategy_name} Settings"
        
        # Group parameters by group
        param_groups = {}
        for param in features.parameters:
            group = param.group or 'General'
            if group not in param_groups:
                param_groups[group] = []
            param_groups[group].append(param)
        
        # Create sections for each group
        for group_name, params in param_groups.items():
            section = {
                'title': group_name,
                'collapsible': True,
                'inputs': []
            }
            
            for param in params:
                input_config = self._create_parameter_input(param)
                section['inputs'].append(input_config)
            
            panel['sections'].append(section)
        
        return panel
    
    def _create_parameter_input(self, param: StrategyParameter) -> Dict[str, Any]:
        """Create UI input configuration for parameter"""
        template = self.ui_templates['parameter_input'][param.param_type]
        
        input_config = {
            'name': param.name,
            'title': param.title or param.name.replace('_', ' ').title(),
            'component': template['component'],
            'props': {
                'default': param.default_value,
                'label': param.title or param.name.replace('_', ' ').title()
            }
        }
        
        # Add type-specific properties
        if param.param_type in ['int', 'float']:
            if param.min_value is not None:
                input_config['props']['min'] = param.min_value
            if param.max_value is not None:
                input_config['props']['max'] = param.max_value
            if param.step is not None:
                input_config['props']['step'] = param.step
            if param.param_type == 'float':
                input_config['props']['precision'] = 2
        
        return input_config
    
    def _generate_ui_components(self, features: StrategyFeatures) -> List[Dict[str, Any]]:
        """Generate additional UI components (gauges, charts, etc.)"""
        components = []
        
        # Performance gauges
        components.append({
            'type': 'gauge',
            'title': 'Strategy Complexity',
            'value': features.complexity_score,
            'min': 0,
            'max': 10,
            'color': 'blue',
            'format': '0.1f'
        })
        
        components.append({
            'type': 'gauge',
            'title': 'Conversion Confidence',
            'value': features.conversion_confidence * 100,
            'min': 0,
            'max': 100,
            'color': 'green',
            'format': '0.0f',
            'suffix': '%'
        })
        
        # Strategy type indicator
        components.append({
            'type': 'indicator',
            'title': 'Strategy Type',
            'value': features.strategy_type.value.replace('_', ' ').title(),
            'color': self._get_strategy_type_color(features.strategy_type.value)
        })
        
        # Indicators used
        if features.indicators:
            components.append({
                'type': 'list',
                'title': 'Technical Indicators',
                'items': [
                    {
                        'name': indicator_name.upper(),
                        'type': indicator_info.get('type', 'unknown'),
                        'description': indicator_info.get('name', indicator_name)
                    }
                    for indicator_name, indicator_info in features.indicators.items()
                ]
            })
        
        # Chart overlays for plot elements
        for plot in features.plot_elements:
            components.append({
                'type': 'chart_overlay',
                'title': plot['title'],
                'variable': plot['variable'],
                'color': plot['color'],
                'style': plot.get('style', 'line')
            })
        
        return components
    
    def _get_strategy_type_color(self, strategy_type: str) -> str:
        """Get color for strategy type"""
        colors = {
            'trend_following': '#2196F3',
            'mean_reversion': '#4CAF50', 
            'momentum': '#FF9800',
            'breakout': '#E91E63',
            'scalping': '#9C27B0',
            'hybrid': '#607D8B'
        }
        return colors.get(strategy_type, '#757575')
    
    def _generate_conversion_notes(self, features: StrategyFeatures, pynescript_notes: List[str]) -> List[str]:
        """Generate comprehensive conversion notes"""
        notes = []
        
        # Conversion method
        if pynescript_notes and any('failed' not in note.lower() for note in pynescript_notes):
            notes.append("✅ PyneScript conversion successful")
        else:
            notes.append("⚠️ Used AI fallback conversion (PyneScript unavailable/failed)")
        
        # Strategy analysis
        notes.append(f"📊 Strategy classified as: {features.strategy_type.value.replace('_', ' ').title()}")
        notes.append(f"🔧 Extracted {len(features.parameters)} parameters")
        notes.append(f"📈 Found {len(features.indicators)} technical indicators")
        notes.append(f"⚡ Complexity score: {features.complexity_score:.2f}/10")
        notes.append(f"✅ Conversion confidence: {features.conversion_confidence*100:.0f}%")
        
        # Components extracted
        components = []
        if features.entry_logic:
            components.append(f"{len(features.entry_logic)} entry conditions")
        if features.exit_logic:
            components.append(f"{len(features.exit_logic)} exit conditions") 
        if features.risk_management:
            components.append(f"{len(features.risk_management)} risk rules")
        if features.filters:
            components.append(f"{len(features.filters)} filters")
        
        if components:
            notes.append(f"🎯 Trading components: {', '.join(components)}")
        
        # Warnings and recommendations
        if features.complexity_score > 7:
            notes.append("⚠️ High complexity strategy - thorough testing recommended")
        
        if features.conversion_confidence < 0.8:
            notes.append("⚠️ Lower confidence conversion - manual review recommended")
        
        # PyneScript specific notes
        notes.extend(pynescript_notes)
        
        return notes

# Example usage
if __name__ == "__main__":
    converter = PynescriptConverter()
    
    pine_code = '''
    //@version=5
    strategy("Advanced RSI Strategy", overlay=true)
    
    // Parameters
    rsiLength = input.int(14, title="RSI Length", minval=1, maxval=50, group="RSI Settings")
    rsiOverbought = input.float(70.0, title="Overbought", minval=50, maxval=100, group="RSI Settings")
    rsiOversold = input.float(30.0, title="Oversold", minval=0, maxval=50, group="RSI Settings")
    
    stopLoss = input.float(2.0, title="Stop Loss %", minval=0.1, maxval=10, group="Risk Management")
    takeProfit = input.float(4.0, title="Take Profit %", minval=0.1, maxval=20, group="Risk Management")
    
    // Indicators
    rsi = ta.rsi(close, rsiLength)
    sma20 = ta.sma(close, 20)
    
    // Entry conditions
    longCondition = rsi < rsiOversold and close > sma20
    shortCondition = rsi > rsiOverbought and close < sma20
    
    // Entries
    if longCondition
        strategy.entry("Long", strategy.long)
    if shortCondition
        strategy.entry("Short", strategy.short)
    
    // Risk management
    strategy.exit("Long Exit", "Long", stop=close*(1-stopLoss/100), limit=close*(1+takeProfit/100))
    strategy.exit("Short Exit", "Short", stop=close*(1+stopLoss/100), limit=close*(1-takeProfit/100))
    '''
    
    result = converter.convert_strategy(pine_code, "Advanced RSI Strategy")
    
    if result.success:
        print("✅ Conversion successful!")
        print(f"Strategy: {result.strategy_features.strategy_name}")
        print(f"Type: {result.strategy_features.strategy_type.value}")
        print(f"Parameters: {len(result.strategy_features.parameters)}")
        print(f"Settings sections: {len(result.settings_panel.get('sections', []))}")
        print(f"UI components: {len(result.ui_components)}")
        print("\n--- Python Code Preview ---")
        print(result.python_code[:500] + "...")
    else:
        print(f"❌ Conversion failed: {result.error_message}")