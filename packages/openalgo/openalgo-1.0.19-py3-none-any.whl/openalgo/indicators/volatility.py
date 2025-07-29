# -*- coding: utf-8 -*-
"""
OpenAlgo Technical Indicators - Volatility Indicators
"""

import numpy as np
import pandas as pd
from numba import jit
from typing import Union, Tuple, Optional
from .base import BaseIndicator


class ATR(BaseIndicator):
    """
    Average True Range
    
    ATR is a technical analysis indicator that measures market volatility by 
    decomposing the entire range of an asset price for that period.
    
    Formula:
    True Range = max(High - Low, |High - Previous Close|, |Low - Previous Close|)
    ATR = Moving Average of True Range over n periods
    """
    
    def __init__(self):
        super().__init__("ATR")
    
    @staticmethod
    @jit(nopython=True)
    def _calculate_atr(high: np.ndarray, low: np.ndarray, close: np.ndarray, 
                      period: int) -> np.ndarray:
        """Numba optimized ATR calculation"""
        n = len(high)
        tr = np.empty(n)
        atr = np.full(n, np.nan)
        
        # First TR value
        tr[0] = high[0] - low[0]
        
        # Calculate True Range
        for i in range(1, n):
            hl = high[i] - low[i]
            hc = abs(high[i] - close[i-1])
            lc = abs(low[i] - close[i-1])
            tr[i] = max(hl, hc, lc)
        
        # Calculate ATR using Wilder's smoothing
        if n >= period:
            # Initial ATR is simple average
            sum_tr = 0.0
            for i in range(period):
                sum_tr += tr[i]
            atr[period-1] = sum_tr / period
            
            # Subsequent ATR values use Wilder's smoothing
            for i in range(period, n):
                atr[i] = (atr[i-1] * (period - 1) + tr[i]) / period
        
        return atr
    
    def calculate(self, high: Union[np.ndarray, pd.Series, list],
                 low: Union[np.ndarray, pd.Series, list],
                 close: Union[np.ndarray, pd.Series, list],
                 period: int = 14) -> Union[np.ndarray, pd.Series]:
        """
        Calculate Average True Range
        
        Parameters:
        -----------
        high : Union[np.ndarray, pd.Series, list]
            High prices
        low : Union[np.ndarray, pd.Series, list]
            Low prices
        close : Union[np.ndarray, pd.Series, list]
            Closing prices
        period : int, default=14
            Number of periods for ATR calculation
            
        Returns:
        --------
        Union[np.ndarray, pd.Series]
            ATR values in the same format as input
        """
        high_data, input_type, index = self.validate_input(high)
        low_data, _, _ = self.validate_input(low)
        close_data, _, _ = self.validate_input(close)
        
        # Align arrays
        high_data, low_data, close_data = self.align_arrays(high_data, low_data, close_data)
        self.validate_period(period, len(close_data))
        
        result = self._calculate_atr(high_data, low_data, close_data, period)
        return self.format_output(result, input_type, index)


class BollingerBands(BaseIndicator):
    """
    Bollinger Bands
    
    Bollinger Bands consist of a middle band (SMA) and two outer bands that are 
    standard deviations away from the middle band.
    
    Formula:
    Middle Band = Simple Moving Average (SMA)
    Upper Band = SMA + (Standard Deviation × multiplier)
    Lower Band = SMA - (Standard Deviation × multiplier)
    """
    
    def __init__(self):
        super().__init__("Bollinger Bands")
    
    @staticmethod
    @jit(nopython=True)
    def _calculate_bollinger_bands(data: np.ndarray, period: int, 
                                  std_dev: float) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Numba optimized Bollinger Bands calculation"""
        n = len(data)
        upper = np.full(n, np.nan)
        middle = np.full(n, np.nan)
        lower = np.full(n, np.nan)
        
        for i in range(period - 1, n):
            # Calculate SMA (middle band)
            window_data = data[i - period + 1:i + 1]
            sma = np.mean(window_data)
            middle[i] = sma
            
            # Calculate standard deviation
            variance = 0.0
            for j in range(period):
                diff = window_data[j] - sma
                variance += diff * diff
            std = np.sqrt(variance / period)
            
            # Calculate upper and lower bands
            upper[i] = sma + (std_dev * std)
            lower[i] = sma - (std_dev * std)
        
        return upper, middle, lower
    
    def calculate(self, data: Union[np.ndarray, pd.Series, list],
                 period: int = 20, std_dev: float = 2.0) -> Union[Tuple[np.ndarray, np.ndarray, np.ndarray], Tuple[pd.Series, pd.Series, pd.Series]]:
        """
        Calculate Bollinger Bands
        
        Parameters:
        -----------
        data : Union[np.ndarray, pd.Series, list]
            Price data (typically closing prices)
        period : int, default=20
            Number of periods for moving average and standard deviation
        std_dev : float, default=2.0
            Number of standard deviations for the bands
            
        Returns:
        --------
        Union[Tuple[np.ndarray, np.ndarray, np.ndarray], Tuple[pd.Series, pd.Series, pd.Series]]
            (upper_band, middle_band, lower_band) in the same format as input
        """
        validated_data, input_type, index = self.validate_input(data)
        self.validate_period(period, len(validated_data))
        
        if std_dev <= 0:
            raise ValueError(f"Standard deviation multiplier must be positive, got {std_dev}")
        
        results = self._calculate_bollinger_bands(validated_data, period, std_dev)
        return self.format_multiple_outputs(results, input_type, index)


# Helper function for EMA calculation (outside class for Numba)
@jit(nopython=True)
def _calculate_ema_keltner(data: np.ndarray, period: int) -> np.ndarray:
    """EMA calculation for Keltner Channel"""
    n = len(data)
    ema = np.empty(n)
    alpha = 2.0 / (period + 1)
    
    # Seed initial NaNs until period-1
    ema[:period-1] = np.nan
    
    # Initial SMA
    sum_val = 0.0
    for i in range(period):
        sum_val += data[i]
    ema[period-1] = sum_val / period
    
    # Exponential smoothing thereafter
    for i in range(period, n):
        ema[i] = alpha * data[i] + (1 - alpha) * ema[i-1]
    
    return ema


class KeltnerChannel(BaseIndicator):
    """
    Keltner Channel
    
    Keltner Channels are volatility-based envelopes set above and below an 
    exponential moving average. The channels use ATR to set channel distance.
    
    Formula:
    Middle Line = EMA of Close
    Upper Channel = EMA + (multiplier × ATR)
    Lower Channel = EMA - (multiplier × ATR)
    """
    
    def __init__(self):
        super().__init__("Keltner Channel")
    
    @staticmethod
    @jit(nopython=True)
    def _calculate_keltner_channel(high: np.ndarray, low: np.ndarray, close: np.ndarray,
                                  ema_period: int, atr_period: int, 
                                  multiplier: float) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Numba optimized Keltner Channel calculation"""
        n = len(close)
        
        # Calculate EMA of close (middle line)
        middle = _calculate_ema_keltner(close, ema_period)
        
        # Calculate ATR
        tr = np.empty(n)
        atr = np.full(n, np.nan)
        
        # First TR value
        tr[0] = high[0] - low[0]
        
        # Calculate True Range
        for i in range(1, n):
            hl = high[i] - low[i]
            hc = abs(high[i] - close[i-1])
            lc = abs(low[i] - close[i-1])
            tr[i] = max(hl, hc, lc)
        
        # Calculate ATR
        if n >= atr_period:
            # Initial ATR
            sum_tr = 0.0
            for i in range(atr_period):
                sum_tr += tr[i]
            atr[atr_period-1] = sum_tr / atr_period
            
            # Subsequent ATR values
            for i in range(atr_period, n):
                atr[i] = (atr[i-1] * (atr_period - 1) + tr[i]) / atr_period
        
        # Calculate upper and lower channels
        upper = np.empty(n)
        lower = np.empty(n)
        
        for i in range(n):
            if np.isnan(atr[i]):
                upper[i] = np.nan
                lower[i] = np.nan
            else:
                upper[i] = middle[i] + multiplier * atr[i]
                lower[i] = middle[i] - multiplier * atr[i]
        
        return upper, middle, lower
    
    def calculate(self, high: Union[np.ndarray, pd.Series, list],
                 low: Union[np.ndarray, pd.Series, list],
                 close: Union[np.ndarray, pd.Series, list],
                 ema_period: int = 20, atr_period: int = 10, 
                 multiplier: float = 2.0) -> Union[Tuple[np.ndarray, np.ndarray, np.ndarray], Tuple[pd.Series, pd.Series, pd.Series]]:
        """
        Calculate Keltner Channel
        
        Parameters:
        -----------
        high : Union[np.ndarray, pd.Series, list]
            High prices
        low : Union[np.ndarray, pd.Series, list]
            Low prices
        close : Union[np.ndarray, pd.Series, list]
            Closing prices
        ema_period : int, default=20
            Period for the EMA calculation
        atr_period : int, default=10
            Period for the ATR calculation
        multiplier : float, default=2.0
            Multiplier for the ATR
            
        Returns:
        --------
        Union[Tuple[np.ndarray, np.ndarray, np.ndarray], Tuple[pd.Series, pd.Series, pd.Series]]
            (upper_channel, middle_line, lower_channel) in the same format as input
        """
        high_data, input_type, index = self.validate_input(high)
        low_data, _, _ = self.validate_input(low)
        close_data, _, _ = self.validate_input(close)
        
        # Align arrays
        high_data, low_data, close_data = self.align_arrays(high_data, low_data, close_data)
        
        # Validate parameters
        self.validate_period(ema_period, len(close_data))
        self.validate_period(atr_period, len(close_data))
        if multiplier <= 0:
            raise ValueError(f"Multiplier must be positive, got {multiplier}")
        
        results = self._calculate_keltner_channel(high_data, low_data, close_data, ema_period, atr_period, multiplier)
        return self.format_multiple_outputs(results, input_type, index)


class DonchianChannel(BaseIndicator):
    """
    Donchian Channel
    
    Donchian Channels are formed by taking the highest high and the lowest low 
    of the last n periods. The middle line is the average of the upper and lower lines.
    
    Formula:
    Upper Channel = Highest High over n periods
    Lower Channel = Lowest Low over n periods
    Middle Line = (Upper Channel + Lower Channel) / 2
    """
    
    def __init__(self):
        super().__init__("Donchian Channel")
    
    @staticmethod
    @jit(nopython=True)
    def _calculate_donchian_channel(high: np.ndarray, low: np.ndarray, 
                                   period: int) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Numba optimized Donchian Channel calculation"""
        n = len(high)
        upper = np.full(n, np.nan)
        lower = np.full(n, np.nan)
        middle = np.full(n, np.nan)
        
        for i in range(period - 1, n):
            # Highest high over period
            upper[i] = high[i - period + 1:i + 1].max()
            
            # Lowest low over period
            lower[i] = low[i - period + 1:i + 1].min()
            
            # Middle line
            middle[i] = (upper[i] + lower[i]) / 2.0
        
        return upper, middle, lower
    
    def calculate(self, high: Union[np.ndarray, pd.Series, list],
                 low: Union[np.ndarray, pd.Series, list],
                 period: int = 20) -> Union[Tuple[np.ndarray, np.ndarray, np.ndarray], Tuple[pd.Series, pd.Series, pd.Series]]:
        """
        Calculate Donchian Channel
        
        Parameters:
        -----------
        high : Union[np.ndarray, pd.Series, list]
            High prices
        low : Union[np.ndarray, pd.Series, list]
            Low prices
        period : int, default=20
            Number of periods for the channel calculation
            
        Returns:
        --------
        Union[Tuple[np.ndarray, np.ndarray, np.ndarray], Tuple[pd.Series, pd.Series, pd.Series]]
            (upper_channel, middle_line, lower_channel) in the same format as input
        """
        high_data, input_type, index = self.validate_input(high)
        low_data, _, _ = self.validate_input(low)
        
        # Align arrays
        high_data, low_data = self.align_arrays(high_data, low_data)
        self.validate_period(period, len(high_data))
        
        results = self._calculate_donchian_channel(high_data, low_data, period)
        return self.format_multiple_outputs(results, input_type, index)


class ChaikinVolatility(BaseIndicator):
    """
    Chaikin Volatility
    
    Chaikin Volatility measures the rate of change of the trading range.
    
    Formula: CV = ((H-L EMA - H-L EMA[n periods ago]) / H-L EMA[n periods ago]) × 100
    """
    
    def __init__(self):
        super().__init__("Chaikin Volatility")
    
    @staticmethod
    @jit(nopython=True)
    def _calculate_ema(data: np.ndarray, period: int) -> np.ndarray:
        """Calculate EMA"""
        n = len(data)
        result = np.empty(n)
        alpha = 2.0 / (period + 1)
        
        result[:period-1] = np.nan
        
        # Initial SMA seed
        sma = 0.0
        for i in range(period):
            sma += data[i]
        result[period-1] = sma / period
        
        for i in range(period, n):
            result[i] = alpha * data[i] + (1 - alpha) * result[i - 1]
        
        return result
    
    def calculate(self, high: Union[np.ndarray, pd.Series, list],
                 low: Union[np.ndarray, pd.Series, list],
                 ema_period: int = 10, roc_period: int = 10) -> Union[np.ndarray, pd.Series]:
        """
        Calculate Chaikin Volatility
        
        Parameters:
        -----------
        high : Union[np.ndarray, pd.Series, list]
            High prices
        low : Union[np.ndarray, pd.Series, list]
            Low prices
        ema_period : int, default=10
            Period for EMA of high-low range
        roc_period : int, default=10
            Period for rate of change calculation
            
        Returns:
        --------
        Union[np.ndarray, pd.Series]
            Chaikin Volatility values in the same format as input
        """
        high_data, input_type, index = self.validate_input(high)
        low_data, _, _ = self.validate_input(low)
        
        high_data, low_data = self.align_arrays(high_data, low_data)
        
        # Calculate high-low range
        hl_range = high_data - low_data
        
        # Calculate EMA of the range
        ema_range = self._calculate_ema(hl_range, ema_period)
        
        # Calculate rate of change
        cv = np.full_like(ema_range, np.nan)
        for i in range(roc_period, len(ema_range)):
            if ema_range[i - roc_period] != 0:
                cv[i] = ((ema_range[i] - ema_range[i - roc_period]) / ema_range[i - roc_period]) * 100
        
        return self.format_output(cv, input_type, index)


class NATR(BaseIndicator):
    """
    Normalized Average True Range
    
    NATR is ATR expressed as a percentage of closing price.
    
    Formula: NATR = (ATR / Close) × 100
    """
    
    def __init__(self):
        super().__init__("NATR")
        self._atr = ATR()
    
    def calculate(self, high: Union[np.ndarray, pd.Series, list],
                 low: Union[np.ndarray, pd.Series, list],
                 close: Union[np.ndarray, pd.Series, list],
                 period: int = 14) -> Union[np.ndarray, pd.Series]:
        """
        Calculate Normalized Average True Range
        
        Parameters:
        -----------
        high : Union[np.ndarray, pd.Series, list]
            High prices
        low : Union[np.ndarray, pd.Series, list]
            Low prices
        close : Union[np.ndarray, pd.Series, list]
            Closing prices
        period : int, default=14
            Period for ATR calculation
            
        Returns:
        --------
        Union[np.ndarray, pd.Series]
            NATR values in the same format as input
        """
        close_data, input_type, index = self.validate_input(close)
        
        # Calculate ATR
        atr = self._atr.calculate(high, low, close, period)
        
        # Calculate NATR
        natr = np.empty_like(atr)
        for i in range(len(atr)):
            if close_data[i] != 0:
                natr[i] = (atr[i] / close_data[i]) * 100
            else:
                natr[i] = 0
        
        return self.format_output(natr, input_type, index)


class RVI(BaseIndicator):
    """
    Relative Volatility Index
    
    RVI applies the RSI calculation to standard deviation instead of price changes.
    
    Formula: RVI = RSI applied to standard deviation
    """
    
    def __init__(self):
        super().__init__("RVI")
    
    @staticmethod
    @jit(nopython=True)
    def _calculate_stdev(data: np.ndarray, period: int) -> np.ndarray:
        """Calculate rolling standard deviation"""
        n = len(data)
        result = np.full(n, np.nan)
        
        for i in range(period - 1, n):
            window = data[i - period + 1:i + 1]
            mean_val = np.mean(window)
            
            variance = 0.0
            for j in range(period):
                diff = window[j] - mean_val
                variance += diff * diff
            
            result[i] = np.sqrt(variance / period)
        
        return result
    
    @staticmethod
    @jit(nopython=True)
    def _calculate_rsi_on_stdev(stdev: np.ndarray, period: int) -> np.ndarray:
        """Calculate RSI on standard deviation values"""
        n = len(stdev)
        result = np.full(n, np.nan)
        
        # Calculate changes in standard deviation
        changes = np.diff(stdev)
        gains = np.where(changes > 0, changes, 0)
        losses = np.where(changes < 0, -changes, 0)
        
        if len(gains) < period:
            return result
        
        # Calculate initial average gain and loss
        avg_gain = np.mean(gains[:period])
        avg_loss = np.mean(losses[:period])
        
        # Calculate first RSI value
        if avg_loss == 0:
            result[period] = 100.0
        else:
            rs = avg_gain / avg_loss
            result[period] = 100.0 - (100.0 / (1.0 + rs))
        
        # Calculate subsequent RSI values
        for i in range(period, len(changes)):
            gain = gains[i] if i < len(gains) else 0
            loss = losses[i] if i < len(losses) else 0
            
            avg_gain = (avg_gain * (period - 1) + gain) / period
            avg_loss = (avg_loss * (period - 1) + loss) / period
            
            if avg_loss == 0:
                result[i + 1] = 100.0
            else:
                rs = avg_gain / avg_loss
                result[i + 1] = 100.0 - (100.0 / (1.0 + rs))
        
        return result
    
    def calculate(self, data: Union[np.ndarray, pd.Series, list],
                 stdev_period: int = 10, rsi_period: int = 14) -> Union[np.ndarray, pd.Series]:
        """
        Calculate Relative Volatility Index
        
        Parameters:
        -----------
        data : Union[np.ndarray, pd.Series, list]
            Price data (typically closing prices)
        stdev_period : int, default=10
            Period for standard deviation calculation
        rsi_period : int, default=14
            Period for RSI calculation
            
        Returns:
        --------
        Union[np.ndarray, pd.Series]
            RVI values in the same format as input
        """
        validated_data, input_type, index = self.validate_input(data)
        
        # Calculate rolling standard deviation
        stdev = self._calculate_stdev(validated_data, stdev_period)
        
        # Calculate RSI on standard deviation
        result = self._calculate_rsi_on_stdev(stdev, rsi_period)
        
        return self.format_output(result, input_type, index)


class ULTOSC(BaseIndicator):
    """
    Ultimate Oscillator (Volatility version)
    
    A different implementation focusing on volatility aspects.
    """
    
    def __init__(self):
        super().__init__("Ultimate Oscillator")
    
    @staticmethod
    @jit(nopython=True)
    def _calculate_ultosc(high: np.ndarray, low: np.ndarray, close: np.ndarray,
                         period1: int, period2: int, period3: int) -> np.ndarray:
        """Calculate Ultimate Oscillator"""
        n = len(close)
        result = np.full(n, np.nan)
        
        # Calculate True Range and Buying Pressure
        tr = np.empty(n)
        bp = np.empty(n)
        
        tr[0] = high[0] - low[0]
        bp[0] = close[0] - min(low[0], close[0])
        
        for i in range(1, n):
            tr[i] = max(high[i] - low[i], 
                       abs(high[i] - close[i-1]), 
                       abs(low[i] - close[i-1]))
            bp[i] = close[i] - min(low[i], close[i-1])
        
        # Calculate Ultimate Oscillator
        max_period = max(period1, period2, period3)
        for i in range(max_period - 1, n):
            # Short period
            bp_sum1 = np.sum(bp[i - period1 + 1:i + 1])
            tr_sum1 = np.sum(tr[i - period1 + 1:i + 1])
            raw1 = bp_sum1 / tr_sum1 if tr_sum1 > 0 else 0
            
            # Medium period
            bp_sum2 = np.sum(bp[i - period2 + 1:i + 1])
            tr_sum2 = np.sum(tr[i - period2 + 1:i + 1])
            raw2 = bp_sum2 / tr_sum2 if tr_sum2 > 0 else 0
            
            # Long period
            bp_sum3 = np.sum(bp[i - period3 + 1:i + 1])
            tr_sum3 = np.sum(tr[i - period3 + 1:i + 1])
            raw3 = bp_sum3 / tr_sum3 if tr_sum3 > 0 else 0
            
            # Ultimate Oscillator formula
            result[i] = 100 * (4 * raw1 + 2 * raw2 + raw3) / 7
        
        return result
    
    def calculate(self, high: Union[np.ndarray, pd.Series, list],
                 low: Union[np.ndarray, pd.Series, list],
                 close: Union[np.ndarray, pd.Series, list],
                 period1: int = 7, period2: int = 14, period3: int = 28) -> Union[np.ndarray, pd.Series]:
        """
        Calculate Ultimate Oscillator
        
        Parameters:
        -----------
        high : Union[np.ndarray, pd.Series, list]
            High prices
        low : Union[np.ndarray, pd.Series, list]
            Low prices
        close : Union[np.ndarray, pd.Series, list]
            Closing prices
        period1 : int, default=7
            Short period
        period2 : int, default=14
            Medium period
        period3 : int, default=28
            Long period
            
        Returns:
        --------
        Union[np.ndarray, pd.Series]
            Ultimate Oscillator values in the same format as input
        """
        high_data, input_type, index = self.validate_input(high)
        low_data, _, _ = self.validate_input(low)
        close_data, _, _ = self.validate_input(close)
        
        high_data, low_data, close_data = self.align_arrays(high_data, low_data, close_data)
        
        result = self._calculate_ultosc(high_data, low_data, close_data, period1, period2, period3)
        return self.format_output(result, input_type, index)


class STDDEV(BaseIndicator):
    """
    Standard Deviation
    
    Standard deviation is a measure of volatility.
    
    Formula: STDDEV = sqrt(Σ(Price - SMA)² / n)
    """
    
    def __init__(self):
        super().__init__("Standard Deviation")
    
    @staticmethod
    @jit(nopython=True)
    def _calculate_stddev(data: np.ndarray, period: int) -> np.ndarray:
        """Numba optimized standard deviation calculation"""
        n = len(data)
        result = np.full(n, np.nan)
        
        for i in range(period - 1, n):
            window = data[i - period + 1:i + 1]
            mean_val = np.mean(window)
            
            variance = 0.0
            for j in range(period):
                diff = window[j] - mean_val
                variance += diff * diff
            
            result[i] = np.sqrt(variance / period)
        
        return result
    
    def calculate(self, data: Union[np.ndarray, pd.Series, list], period: int = 20) -> Union[np.ndarray, pd.Series]:
        """
        Calculate Standard Deviation
        
        Parameters:
        -----------
        data : Union[np.ndarray, pd.Series, list]
            Price data (typically closing prices)
        period : int, default=20
            Period for standard deviation calculation
            
        Returns:
        --------
        Union[np.ndarray, pd.Series]
            Standard deviation values in the same format as input
        """
        validated_data, input_type, index = self.validate_input(data)
        self.validate_period(period, len(validated_data))
        
        result = self._calculate_stddev(validated_data, period)
        return self.format_output(result, input_type, index)


class TRANGE(BaseIndicator):
    """
    True Range
    
    True Range is a measure of volatility that accounts for gaps.
    
    Formula: TR = max(H-L, |H-C[prev]|, |L-C[prev]|)
    """
    
    def __init__(self):
        super().__init__("True Range")
    
    @staticmethod
    @jit(nopython=True)
    def _calculate_trange(high: np.ndarray, low: np.ndarray, close: np.ndarray) -> np.ndarray:
        """Numba optimized True Range calculation"""
        n = len(high)
        result = np.empty(n)
        
        # First value
        result[0] = high[0] - low[0]
        
        # Calculate True Range
        for i in range(1, n):
            hl = high[i] - low[i]
            hc = abs(high[i] - close[i-1])
            lc = abs(low[i] - close[i-1])
            result[i] = max(hl, hc, lc)
        
        return result
    
    def calculate(self, high: Union[np.ndarray, pd.Series, list],
                 low: Union[np.ndarray, pd.Series, list],
                 close: Union[np.ndarray, pd.Series, list]) -> Union[np.ndarray, pd.Series]:
        """
        Calculate True Range
        
        Parameters:
        -----------
        high : Union[np.ndarray, pd.Series, list]
            High prices
        low : Union[np.ndarray, pd.Series, list]
            Low prices
        close : Union[np.ndarray, pd.Series, list]
            Closing prices
            
        Returns:
        --------
        Union[np.ndarray, pd.Series]
            True Range values in the same format as input
        """
        high_data, input_type, index = self.validate_input(high)
        low_data, _, _ = self.validate_input(low)
        close_data, _, _ = self.validate_input(close)
        
        high_data, low_data, close_data = self.align_arrays(high_data, low_data, close_data)
        
        result = self._calculate_trange(high_data, low_data, close_data)
        return self.format_output(result, input_type, index)


class MASS(BaseIndicator):
    """
    Mass Index
    
    The Mass Index uses the high-low range to identify trend reversals 
    based on range expansion.
    
    Formula: MI = SMA(EMA(H-L, 9) / EMA(EMA(H-L, 9), 9), 25)
    """
    
    def __init__(self):
        super().__init__("Mass Index")
    
    @staticmethod
    @jit(nopython=True)
    def _calculate_ema(data: np.ndarray, period: int) -> np.ndarray:
        """Calculate EMA"""
        n = len(data)
        result = np.empty(n)
        alpha = 2.0 / (period + 1)
        
        result[:period-1] = np.nan
        
        sma_seed = 0.0
        for i in range(period):
            sma_seed += data[i]
        result[period-1] = sma_seed / period
        
        for i in range(period, n):
            result[i] = alpha * data[i] + (1 - alpha) * result[i - 1]
        
        return result
    
    @staticmethod
    @jit(nopython=True)
    def _calculate_sma(data: np.ndarray, period: int) -> np.ndarray:
        """Calculate SMA"""
        n = len(data)
        result = np.full(n, np.nan)
        
        for i in range(period - 1, n):
            result[i] = np.mean(data[i - period + 1:i + 1])
        
        return result
    
    def calculate(self, high: Union[np.ndarray, pd.Series, list],
                 low: Union[np.ndarray, pd.Series, list],
                 fast_period: int = 9, slow_period: int = 25) -> Union[np.ndarray, pd.Series]:
        """
        Calculate Mass Index
        
        Parameters:
        -----------
        high : Union[np.ndarray, pd.Series, list]
            High prices
        low : Union[np.ndarray, pd.Series, list]
            Low prices
        fast_period : int, default=9
            Period for EMA calculation
        slow_period : int, default=25
            Period for SMA calculation
            
        Returns:
        --------
        Union[np.ndarray, pd.Series]
            Mass Index values in the same format as input
        """
        high_data, input_type, index = self.validate_input(high)
        low_data, _, _ = self.validate_input(low)
        
        high_data, low_data = self.align_arrays(high_data, low_data)
        
        # Calculate high-low range
        hl_range = high_data - low_data
        
        # Calculate first EMA
        ema1 = self._calculate_ema(hl_range, fast_period)
        
        # Calculate second EMA
        ema2 = self._calculate_ema(ema1, fast_period)
        
        # Calculate ratio
        ratio = np.empty_like(ema1)
        for i in range(len(ema1)):
            if ema2[i] != 0:
                ratio[i] = ema1[i] / ema2[i]
            else:
                ratio[i] = 1.0
        
        # Calculate SMA of ratio
        result = self._calculate_sma(ratio, slow_period)
        
        return self.format_output(result, input_type, index)