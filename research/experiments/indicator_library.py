"""
Intelligent Indicator Library
Implements all indicators identified by the AI analysis agent
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, Tuple
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class IndicatorResult:
    """Result of an indicator calculation"""
    values: pd.Series
    metadata: Dict[str, Any]
    success: bool
    error_message: Optional[str] = None

class IndicatorLibrary:
    """
    Library of technical indicators optimized for Pine Script conversion
    Each indicator matches Pine Script behavior exactly
    """
    
    @staticmethod
    def rsi(source: pd.Series, length: int = 14) -> IndicatorResult:
        """
        Relative Strength Index - matches Pine Script rsi() function
        
        Args:
            source: Price series (typically close prices)
            length: RSI period
            
        Returns:
            IndicatorResult with RSI values
        """
        try:
            delta = source.diff()
            gain = delta.where(delta > 0, 0)
            loss = -delta.where(delta < 0, 0)
            
            # Use Wilder's smoothing (same as Pine Script)
            alpha = 1.0 / length
            avg_gain = gain.ewm(alpha=alpha, adjust=False).mean()
            avg_loss = loss.ewm(alpha=alpha, adjust=False).mean()
            
            rs = avg_gain / avg_loss
            rsi_values = 100 - (100 / (1 + rs))
            
            return IndicatorResult(
                values=rsi_values,
                metadata={'length': length, 'type': 'rsi'},
                success=True
            )
            
        except Exception as e:
            return IndicatorResult(
                values=pd.Series(),
                metadata={},
                success=False,
                error_message=str(e)
            )
    
    @staticmethod
    def ema(source: pd.Series, length: int) -> IndicatorResult:
        """
        Exponential Moving Average - matches Pine Script ema() function
        """
        try:
            alpha = 2.0 / (length + 1)
            ema_values = source.ewm(alpha=alpha, adjust=False).mean()
            
            return IndicatorResult(
                values=ema_values,
                metadata={'length': length, 'type': 'ema'},
                success=True
            )
            
        except Exception as e:
            return IndicatorResult(
                values=pd.Series(),
                metadata={},
                success=False,
                error_message=str(e)
            )
    
    @staticmethod
    def sma(source: pd.Series, length: int) -> IndicatorResult:
        """
        Simple Moving Average - matches Pine Script sma() function
        """
        try:
            sma_values = source.rolling(window=length).mean()
            
            return IndicatorResult(
                values=sma_values,
                metadata={'length': length, 'type': 'sma'},
                success=True
            )
            
        except Exception as e:
            return IndicatorResult(
                values=pd.Series(),
                metadata={},
                success=False,
                error_message=str(e)
            )
    
    @staticmethod
    def vwap(df: pd.DataFrame, period: int = None) -> IndicatorResult:
        """
        Volume Weighted Average Price
        
        Args:
            df: DataFrame with high, low, close, volume columns
            period: Period for VWAP calculation (None for session VWAP)
        """
        try:
            typical_price = (df['high'] + df['low'] + df['close']) / 3
            typical_price_volume = typical_price * df['volume']
            
            if period is None:
                # Session VWAP (cumulative)
                cum_tpv = typical_price_volume.cumsum()
                cum_volume = df['volume'].cumsum()
                vwap_values = cum_tpv / cum_volume
            else:
                # Rolling VWAP
                cum_tpv = typical_price_volume.rolling(window=period).sum()
                cum_volume = df['volume'].rolling(window=period).sum()
                vwap_values = cum_tpv / cum_volume
            
            return IndicatorResult(
                values=vwap_values,
                metadata={'period': period, 'type': 'vwap'},
                success=True
            )
            
        except Exception as e:
            return IndicatorResult(
                values=pd.Series(),
                metadata={},
                success=False,
                error_message=str(e)
            )
    
    @staticmethod
    def multi_period_vwap(df: pd.DataFrame, periods: Dict[str, int]) -> Dict[str, IndicatorResult]:
        """
        Multiple VWAP calculations for HYE strategy
        
        Args:
            df: OHLCV DataFrame
            periods: Dict with 'small', 'big', 'mean' periods
            
        Returns:
            Dict of VWAP results for each period
        """
        results = {}
        
        for name, period in periods.items():
            result = IndicatorLibrary.vwap(df, period)
            result.metadata['period_name'] = name
            results[name] = result
        
        return results
    
    @staticmethod
    def tsv(df: pd.DataFrame, length: int = 20) -> IndicatorResult:
        """
        Time Series Volume - Custom implementation based on HYE analysis
        
        Pine Script equivalent:
        tsv = sum(close>close[1]?volume*(close-close[1]):close<close[1]?volume*(close-close[1]):0,length)
        """
        try:
            close = df['close']
            volume = df['volume']
            
            # Calculate price change
            price_change = close.diff()
            
            # Volume-weighted price change (only when price moves)
            volume_weighted_change = np.where(
                price_change != 0,
                volume * price_change,
                0
            )
            
            # Sum over the specified length
            tsv_values = pd.Series(volume_weighted_change).rolling(window=length).sum()
            
            return IndicatorResult(
                values=tsv_values,
                metadata={'length': length, 'type': 'tsv'},
                success=True
            )
            
        except Exception as e:
            return IndicatorResult(
                values=pd.Series(),
                metadata={},
                success=False,
                error_message=str(e)
            )
    
    @staticmethod
    def cmo(source: pd.Series, length: int) -> IndicatorResult:
        """
        Chande Momentum Oscillator - required for Vidya calculation
        """
        try:
            delta = source.diff()
            gain = delta.where(delta > 0, 0)
            loss = -delta.where(delta < 0, 0)
            
            sum_gain = gain.rolling(window=length).sum()
            sum_loss = loss.rolling(window=length).sum()
            
            cmo_values = 100 * (sum_gain - sum_loss) / (sum_gain + sum_loss)
            
            return IndicatorResult(
                values=cmo_values,
                metadata={'length': length, 'type': 'cmo'},
                success=True
            )
            
        except Exception as e:
            return IndicatorResult(
                values=pd.Series(),
                metadata={},
                success=False,
                error_message=str(e)
            )
    
    @staticmethod
    def vidya(source: pd.Series, length: int = 20) -> IndicatorResult:
        """
        Variable Index Dynamic Average (Vidya)
        Uses CMO to adjust the smoothing factor
        """
        try:
            # Calculate CMO
            cmo_result = IndicatorLibrary.cmo(source, length)
            if not cmo_result.success:
                return cmo_result
            
            cmo_values = cmo_result.values
            
            # Calculate alpha using CMO
            alpha = 2.0 / (length + 1)
            adaptive_alpha = alpha * (cmo_values.abs() / 100)
            
            # Calculate Vidya
            vidya_values = pd.Series(index=source.index, dtype=float)
            vidya_values.iloc[0] = source.iloc[0]
            
            for i in range(1, len(source)):
                if pd.notna(adaptive_alpha.iloc[i]):
                    vidya_values.iloc[i] = (adaptive_alpha.iloc[i] * source.iloc[i] + 
                                          (1 - adaptive_alpha.iloc[i]) * vidya_values.iloc[i-1])
                else:
                    vidya_values.iloc[i] = vidya_values.iloc[i-1]
            
            return IndicatorResult(
                values=vidya_values,
                metadata={'length': length, 'type': 'vidya'},
                success=True
            )
            
        except Exception as e:
            return IndicatorResult(
                values=pd.Series(),
                metadata={},
                success=False,
                error_message=str(e)
            )
    
    @staticmethod
    def ichimoku_components(df: pd.DataFrame, 
                          tenkan_period: int = 9, 
                          kijun_period: int = 26) -> Dict[str, IndicatorResult]:
        """
        Ichimoku-style components for HYE strategy
        Based on VWAP instead of traditional high/low
        """
        try:
            high, low, close, volume = df['high'], df['low'], df['close'], df['volume']
            
            # Calculate VWAP-based values for each period
            typical_price = (high + low + close) / 3
            typical_price_volume = typical_price * volume
            
            # Tenkan-sen (VWAP-based)
            tenkan_tpv = typical_price_volume.rolling(window=tenkan_period).sum()
            tenkan_vol = volume.rolling(window=tenkan_period).sum()
            tenkan_vwap = tenkan_tpv / tenkan_vol
            
            # Get highest and lowest of VWAP values for Tenkan
            tenkan_high = tenkan_vwap.rolling(window=tenkan_period).max()
            tenkan_low = tenkan_vwap.rolling(window=tenkan_period).min()
            tenkan_sen = (tenkan_high + tenkan_low) / 2
            
            # Kijun-sen (VWAP-based)
            kijun_tpv = typical_price_volume.rolling(window=kijun_period).sum()
            kijun_vol = volume.rolling(window=kijun_period).sum()
            kijun_vwap = kijun_tpv / kijun_vol
            
            # Get highest and lowest of VWAP values for Kijun
            kijun_high = kijun_vwap.rolling(window=kijun_period).max()
            kijun_low = kijun_vwap.rolling(window=kijun_period).min()
            kijun_sen = (kijun_high + kijun_low) / 2
            
            # Lead Line (average of Tenkan and Kijun)
            lead_line = (tenkan_sen + kijun_sen) / 2
            
            return {
                'tenkan_sen': IndicatorResult(
                    values=tenkan_sen,
                    metadata={'period': tenkan_period, 'type': 'tenkan_vwap'},
                    success=True
                ),
                'kijun_sen': IndicatorResult(
                    values=kijun_sen,
                    metadata={'period': kijun_period, 'type': 'kijun_vwap'},
                    success=True
                ),
                'lead_line': IndicatorResult(
                    values=lead_line,
                    metadata={'type': 'lead_line_vwap'},
                    success=True
                )
            }
            
        except Exception as e:
            error_result = IndicatorResult(
                values=pd.Series(),
                metadata={},
                success=False,
                error_message=str(e)
            )
            return {
                'tenkan_sen': error_result,
                'kijun_sen': error_result,
                'lead_line': error_result
            }
    
    @staticmethod
    def bollinger_bands(source: pd.Series, length: int = 20, mult: float = 2.0) -> Dict[str, IndicatorResult]:
        """
        Bollinger Bands
        """
        try:
            basis = source.rolling(window=length).mean()
            dev = source.rolling(window=length).std() * mult
            
            upper = basis + dev
            lower = basis - dev
            
            return {
                'basis': IndicatorResult(
                    values=basis,
                    metadata={'length': length, 'type': 'bb_basis'},
                    success=True
                ),
                'upper': IndicatorResult(
                    values=upper,
                    metadata={'length': length, 'mult': mult, 'type': 'bb_upper'},
                    success=True
                ),
                'lower': IndicatorResult(
                    values=lower,
                    metadata={'length': length, 'mult': mult, 'type': 'bb_lower'},
                    success=True
                )
            }
            
        except Exception as e:
            error_result = IndicatorResult(
                values=pd.Series(),
                metadata={},
                success=False,
                error_message=str(e)
            )
            return {
                'basis': error_result,
                'upper': error_result,
                'lower': error_result
            }

class PineScriptHelpers:
    """Helper functions that mimic Pine Script built-in functions"""
    
    @staticmethod
    def crossover(series1: pd.Series, series2: pd.Series) -> pd.Series:
        """Pine Script crossover() function"""
        prev_series1 = series1.shift(1)
        prev_series2 = series2.shift(1)
        
        return (series1 > series2) & (prev_series1 <= prev_series2)
    
    @staticmethod
    def crossunder(series1: pd.Series, series2: pd.Series) -> pd.Series:
        """Pine Script crossunder() function"""
        prev_series1 = series1.shift(1)
        prev_series2 = series2.shift(1)
        
        return (series1 < series2) & (prev_series1 >= prev_series2)
    
    @staticmethod
    def highest(source: pd.Series, length: int) -> pd.Series:
        """Pine Script highest() function"""
        return source.rolling(window=length).max()
    
    @staticmethod
    def lowest(source: pd.Series, length: int) -> pd.Series:
        """Pine Script lowest() function"""
        return source.rolling(window=length).min()
    
    @staticmethod
    def sum_series(source: pd.Series, length: int) -> pd.Series:
        """Pine Script sum() function"""
        return source.rolling(window=length).sum()
    
    @staticmethod
    def avg(series1: pd.Series, series2: pd.Series) -> pd.Series:
        """Pine Script avg() function"""
        return (series1 + series2) / 2

# Example usage and testing
if __name__ == "__main__":
    # Test with sample data
    import pandas as pd
    
    # Create sample OHLCV data
    dates = pd.date_range('2024-01-01', periods=100, freq='1H')
    np.random.seed(42)
    
    sample_data = pd.DataFrame({
        'open': 100 + np.random.randn(100).cumsum(),
        'high': 101 + np.random.randn(100).cumsum(),
        'low': 99 + np.random.randn(100).cumsum(),
        'close': 100 + np.random.randn(100).cumsum(),
        'volume': 1000 + np.random.randint(-100, 100, 100)
    }, index=dates)
    
    # Ensure high >= low
    sample_data['high'] = np.maximum(sample_data['high'], sample_data[['open', 'close']].max(axis=1))
    sample_data['low'] = np.minimum(sample_data['low'], sample_data[['open', 'close']].min(axis=1))
    
    print("Testing Indicator Library...")
    
    # Test RSI
    rsi_result = IndicatorLibrary.rsi(sample_data['close'], 14)
    print(f"RSI: {rsi_result.success}, last value: {rsi_result.values.iloc[-1]:.2f}")
    
    # Test VWAP
    vwap_result = IndicatorLibrary.vwap(sample_data, 20)
    print(f"VWAP: {vwap_result.success}, last value: {vwap_result.values.iloc[-1]:.2f}")
    
    # Test TSV
    tsv_result = IndicatorLibrary.tsv(sample_data, 20)
    print(f"TSV: {tsv_result.success}, last value: {tsv_result.values.iloc[-1]:.2f}")
    
    # Test Vidya
    vidya_result = IndicatorLibrary.vidya(sample_data['close'], 20)
    print(f"Vidya: {vidya_result.success}, last value: {vidya_result.values.iloc[-1]:.2f}")
    
    print("All tests completed!")