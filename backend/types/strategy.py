"""Strategy type definitions."""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, Union
import pandas as pd


@dataclass
class StrategyParameter:
    """Strategy parameter definition."""
    name: str
    default: Union[int, float, bool, str]
    min_val: Optional[Union[int, float]] = None
    max_val: Optional[Union[int, float]] = None
    step: Optional[Union[int, float]] = None
    options: Optional[List[str]] = None
    description: Optional[str] = None


@dataclass 
class StrategySignals:
    """Strategy entry/exit signals."""
    entries: pd.Series  # Boolean series for entry signals
    exits: pd.Series    # Boolean series for exit signals
    stops: Optional[pd.Series] = None    # Stop loss levels
    targets: Optional[pd.Series] = None  # Take profit levels
    
    def __post_init__(self):
        """Validate signal data."""
        if len(self.entries) != len(self.exits):
            raise ValueError("Entries and exits must have same length")
        if self.stops is not None and len(self.stops) != len(self.entries):
            raise ValueError("Stops must have same length as entries")
        if self.targets is not None and len(self.targets) != len(self.entries):
            raise ValueError("Targets must have same length as entries")


@dataclass
class StrategyMetadata:
    """Strategy metadata from Pine script."""
    name: str
    description: Optional[str] = None
    version: str = "v5"
    parameters: List[StrategyParameter] = field(default_factory=list)
    pine_source: Optional[str] = None
    conversion_timestamp: Optional[str] = None
    
    def get_param_defaults(self) -> Dict[str, Any]:
        """Get default parameter values."""
        return {param.name: param.default for param in self.parameters}
    
    def get_param_ranges(self) -> Dict[str, Dict[str, Any]]:
        """Get parameter ranges for optimization."""
        ranges = {}
        for param in self.parameters:
            if param.min_val is not None and param.max_val is not None:
                ranges[param.name] = {
                    'min': param.min_val,
                    'max': param.max_val,
                    'step': param.step or 1,
                    'default': param.default
                }
        return ranges


class ConvertedStrategy:
    """Wrapper for converted Pine strategy."""
    
    def __init__(self, metadata: StrategyMetadata, build_signals_func):
        self.metadata = metadata
        self._build_signals = build_signals_func
    
    def build_signals(self, df: pd.DataFrame, **params) -> StrategySignals:
        """Build trading signals from OHLC data."""
        # Merge defaults with provided params
        final_params = self.metadata.get_param_defaults()
        final_params.update(params)
        
        return self._build_signals(df, **final_params)
    
    @property
    def parameters(self) -> List[StrategyParameter]:
        """Get strategy parameters."""
        return self.metadata.parameters
    
    @property 
    def param_ranges(self) -> Dict[str, Dict[str, Any]]:
        """Get parameter ranges for optimization."""
        return self.metadata.get_param_ranges()