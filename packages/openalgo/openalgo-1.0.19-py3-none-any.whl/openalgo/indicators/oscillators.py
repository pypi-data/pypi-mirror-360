# -*- coding: utf-8 -*-
"""
OpenAlgo Technical Indicators - Oscillators
"""

import numpy as np
import pandas as pd
from numba import jit
from typing import Union, Tuple, Optional
from .base import BaseIndicator


class ROC(BaseIndicator):
    """
    Rate of Change (Price Oscillator)
    
    ROC measures the percentage change in price from n periods ago.
    
    Formula: ROC = ((Price - Price[n periods ago]) / Price[n periods ago]) × 100
    """
    
    def __init__(self):
        super().__init__("ROC")
    
    @staticmethod
    @jit(nopython=True)
    def _calculate_roc(data: np.ndarray, period: int) -> np.ndarray:
        """Numba optimized ROC calculation"""
        n = len(data)
        result = np.full(n, np.nan)
        
        for i in range(period, n):
            if data[i - period] != 0:
                result[i] = ((data[i] - data[i - period]) / data[i - period]) * 100
            else:
                result[i] = 0.0
        
        return result
    
    def calculate(self, data: Union[np.ndarray, pd.Series, list], period: int = 12) -> Union[np.ndarray, pd.Series]:
        """
        Calculate Rate of Change
        
        Parameters:
        -----------
        data : Union[np.ndarray, pd.Series, list]
            Price data (typically closing prices)
        period : int, default=12
            Number of periods to look back
            
        Returns:
        --------
        Union[np.ndarray, pd.Series]
            ROC values in the same format as input
        """
        validated_data, input_type, index = self.validate_input(data)
        self.validate_period(period, len(validated_data))
        result = self._calculate_roc(validated_data, period)
        return self.format_output(result, input_type, index)


class CMO(BaseIndicator):
    """
    Chande Momentum Oscillator
    
    CMO is a momentum oscillator developed by Tushar Chande.
    
    Formula: CMO = 100 × (Sum of Up Days - Sum of Down Days) / (Sum of Up Days + Sum of Down Days)
    """
    
    def __init__(self):
        super().__init__("CMO")
    
    @staticmethod
    @jit(nopython=True)
    def _calculate_cmo(data: np.ndarray, period: int) -> np.ndarray:
        """Numba optimized CMO calculation"""
        n = len(data)
        result = np.full(n, np.nan)
        
        # Calculate price changes
        changes = np.diff(data)
        
        for i in range(period, n):
            sum_up = 0.0
            sum_down = 0.0
            
            for j in range(period):
                change = changes[i - period + j]
                if change > 0:
                    sum_up += change
                elif change < 0:
                    sum_down += abs(change)
            
            total_movement = sum_up + sum_down
            if total_movement > 0:
                result[i] = 100 * (sum_up - sum_down) / total_movement
            else:
                result[i] = 0.0
        
        return result
    
    def calculate(self, data: Union[np.ndarray, pd.Series, list], period: int = 14) -> Union[np.ndarray, pd.Series]:
        """
        Calculate Chande Momentum Oscillator
        
        Parameters:
        -----------
        data : Union[np.ndarray, pd.Series, list]
            Price data (typically closing prices)
        period : int, default=14
            Number of periods for CMO calculation
            
        Returns:
        --------
        Union[np.ndarray, pd.Series]
            CMO values in the same format as input
        """
        validated_data, input_type, index = self.validate_input(data)
        self.validate_period(period + 1, len(validated_data))  # +1 for diff
        result = self._calculate_cmo(validated_data, period)
        return self.format_output(result, input_type, index)


class TRIX(BaseIndicator):
    """
    TRIX - Triple Exponential Average
    
    TRIX is a momentum oscillator that displays the percentage rate of change 
    of a triple exponentially smoothed moving average.
    
    Formula: TRIX = % change of triple EMA
    """
    
    def __init__(self):
        super().__init__("TRIX")
    
    @staticmethod
    @jit(nopython=True)
    def _calculate_ema(data: np.ndarray, period: int) -> np.ndarray:
        """Calculate EMA"""
        n = len(data)
        result = np.empty(n)
        alpha = 2.0 / (period + 1)
        
        result[0] = data[0]
        for i in range(1, n):
            result[i] = alpha * data[i] + (1 - alpha) * result[i - 1]
        
        return result
    
    def calculate(self, data: Union[np.ndarray, pd.Series, list], period: int = 14) -> Union[np.ndarray, pd.Series]:
        """
        Calculate TRIX
        
        Parameters:
        -----------
        data : Union[np.ndarray, pd.Series, list]
            Price data (typically closing prices)
        period : int, default=14
            Number of periods for EMA calculation
            
        Returns:
        --------
        Union[np.ndarray, pd.Series]
            TRIX values in the same format as input
        """
        validated_data, input_type, index = self.validate_input(data)
        self.validate_period(period, len(validated_data))
        
        # Calculate triple EMA
        ema1 = self._calculate_ema(validated_data, period)
        ema2 = self._calculate_ema(ema1, period)
        ema3 = self._calculate_ema(ema2, period)
        
        # Calculate percentage change of triple EMA
        trix = np.full_like(ema3, np.nan)
        for i in range(1, len(ema3)):
            if ema3[i - 1] != 0:
                trix[i] = ((ema3[i] - ema3[i - 1]) / ema3[i - 1]) * 100  # ×100 to express percentage change
        
        return self.format_output(trix, input_type, index)


class UO(BaseIndicator):
    """
    Ultimate Oscillator
    
    The Ultimate Oscillator combines short, medium, and long-term price action 
    into one oscillator.
    
    Formula: UO = 100 × (4×AVG7 + 2×AVG14 + AVG28) / (4 + 2 + 1)
    Where: AVG = Average of (Close - TrueLow) / (TrueRange)
    """
    
    def __init__(self):
        super().__init__("UO")
    
    @staticmethod
    @jit(nopython=True)
    def _calculate_uo(high: np.ndarray, low: np.ndarray, close: np.ndarray,
                     period1: int, period2: int, period3: int) -> np.ndarray:
        """Numba optimized Ultimate Oscillator calculation"""
        n = len(close)
        result = np.full(n, np.nan)
        
        # Calculate True Low and True Range
        true_low = np.empty(n)
        true_range = np.empty(n)
        buying_pressure = np.empty(n)
        
        true_low[0] = low[0]
        true_range[0] = high[0] - low[0]
        buying_pressure[0] = close[0] - true_low[0]
        
        for i in range(1, n):
            true_low[i] = min(low[i], close[i - 1])
            true_range[i] = max(high[i] - low[i], 
                               abs(high[i] - close[i - 1]), 
                               abs(low[i] - close[i - 1]))
            buying_pressure[i] = close[i] - true_low[i]
        
        # Calculate Ultimate Oscillator
        max_period = max(period1, period2, period3)
        for i in range(max_period - 1, n):
            # Calculate averages for each period
            bp1 = np.sum(buying_pressure[i - period1 + 1:i + 1])
            tr1 = np.sum(true_range[i - period1 + 1:i + 1])
            avg1 = bp1 / tr1 if tr1 > 0 else 0
            
            bp2 = np.sum(buying_pressure[i - period2 + 1:i + 1])
            tr2 = np.sum(true_range[i - period2 + 1:i + 1])
            avg2 = bp2 / tr2 if tr2 > 0 else 0
            
            bp3 = np.sum(buying_pressure[i - period3 + 1:i + 1])
            tr3 = np.sum(true_range[i - period3 + 1:i + 1])
            avg3 = bp3 / tr3 if tr3 > 0 else 0
            
            # Calculate Ultimate Oscillator
            result[i] = 100 * (4 * avg1 + 2 * avg2 + avg3) / 7
        
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
        
        result = self._calculate_uo(high_data, low_data, close_data, period1, period2, period3)
        return self.format_output(result, input_type, index)


class AO(BaseIndicator):
    """
    Awesome Oscillator
    
    The Awesome Oscillator is an indicator used to measure market momentum.
    
    Formula: AO = SMA(HL/2, 5) - SMA(HL/2, 34)
    Where: HL/2 = (High + Low) / 2
    """
    
    def __init__(self):
        super().__init__("AO")
    
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
                 fast_period: int = 5, slow_period: int = 34) -> Union[np.ndarray, pd.Series]:
        """
        Calculate Awesome Oscillator
        
        Parameters:
        -----------
        high : Union[np.ndarray, pd.Series, list]
            High prices
        low : Union[np.ndarray, pd.Series, list]
            Low prices
        fast_period : int, default=5
            Fast SMA period
        slow_period : int, default=34
            Slow SMA period
            
        Returns:
        --------
        Union[np.ndarray, pd.Series]
            Awesome Oscillator values in the same format as input
        """
        high_data, input_type, index = self.validate_input(high)
        low_data, _, _ = self.validate_input(low)
        
        high_data, low_data = self.align_arrays(high_data, low_data)
        
        # Calculate median price
        median_price = (high_data + low_data) / 2
        
        # Calculate SMAs
        fast_sma = self._calculate_sma(median_price, fast_period)
        slow_sma = self._calculate_sma(median_price, slow_period)
        
        # Calculate AO
        result = fast_sma - slow_sma
        return self.format_output(result, input_type, index)


class AC(BaseIndicator):
    """
    Accelerator Oscillator
    
    The Accelerator Oscillator measures acceleration and deceleration of momentum.
    
    Formula: AC = AO - SMA(AO, 5)
    Where: AO = Awesome Oscillator
    """
    
    def __init__(self):
        super().__init__("AC")
        self._ao = AO()
    
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
                 period: int = 5) -> Union[np.ndarray, pd.Series]:
        """
        Calculate Accelerator Oscillator
        
        Parameters:
        -----------
        high : Union[np.ndarray, pd.Series, list]
            High prices
        low : Union[np.ndarray, pd.Series, list]
            Low prices
        period : int, default=5
            SMA period for acceleration calculation
            
        Returns:
        --------
        Union[np.ndarray, pd.Series]
            Accelerator Oscillator values in the same format as input
        """
        high_data, input_type, index = self.validate_input(high)
        low_data, _, _ = self.validate_input(low)
        
        # Calculate Awesome Oscillator
        ao_raw = self._ao.calculate(high, low)
        
        # Ensure numpy array for numba SMA calculation
        if isinstance(ao_raw, pd.Series):
            ao_data = ao_raw.values.astype(np.float64)
        else:
            ao_data = ao_raw.astype(np.float64)
        
        # Calculate SMA of AO
        ao_sma = self._calculate_sma(ao_data, period)
        
        # Calculate AC (array diff)
        result_arr = ao_data - ao_sma
        return self.format_output(result_arr, input_type, index)


class PPO(BaseIndicator):
    """
    Percentage Price Oscillator
    
    PPO is a momentum oscillator that measures the difference between two 
    moving averages as a percentage of the larger moving average.
    
    Formula: PPO = ((Fast EMA - Slow EMA) / Slow EMA) × 100
    """
    
    def __init__(self):
        super().__init__("PPO")
    
    @staticmethod
    @jit(nopython=True)
    def _calculate_ema(data: np.ndarray, period: int) -> np.ndarray:
        """Calculate EMA"""
        n = len(data)
        result = np.empty(n)
        alpha = 2.0 / (period + 1)
        
        result[0] = data[0]
        for i in range(1, n):
            result[i] = alpha * data[i] + (1 - alpha) * result[i - 1]
        
        return result
    
    def calculate(self, data: Union[np.ndarray, pd.Series, list],
                 fast_period: int = 12, slow_period: int = 26,
                 signal_period: int = 9) -> Union[Tuple[np.ndarray, np.ndarray, np.ndarray], Tuple[pd.Series, pd.Series, pd.Series]]:
        """
        Calculate Percentage Price Oscillator
        
        Parameters:
        -----------
        data : Union[np.ndarray, pd.Series, list]
            Price data (typically closing prices)
        fast_period : int, default=12
            Fast EMA period
        slow_period : int, default=26
            Slow EMA period
        signal_period : int, default=9
            Signal line EMA period
            
        Returns:
        --------
        Union[Tuple[np.ndarray, np.ndarray, np.ndarray], Tuple[pd.Series, pd.Series, pd.Series]]
            (ppo_line, signal_line, histogram) in the same format as input
        """
        validated_data, input_type, index = self.validate_input(data)
        
        # Calculate EMAs
        fast_ema = self._calculate_ema(validated_data, fast_period)
        slow_ema = self._calculate_ema(validated_data, slow_period)
        
        # Calculate PPO line
        ppo_line = np.empty_like(validated_data)
        for i in range(len(validated_data)):
            if slow_ema[i] != 0:
                ppo_line[i] = ((fast_ema[i] - slow_ema[i]) / slow_ema[i]) * 100
            else:
                ppo_line[i] = 0
        
        # Calculate signal line
        signal_line = self._calculate_ema(ppo_line, signal_period)
        
        # Calculate histogram
        histogram = ppo_line - signal_line
        
        results = (ppo_line, signal_line, histogram)
        return self.format_multiple_outputs(results, input_type, index)


class PO(BaseIndicator):
    """
    Price Oscillator
    
    Price Oscillator shows the difference between two moving averages.
    
    Formula: PO = Fast MA - Slow MA
    """
    
    def __init__(self):
        super().__init__("PO")
    
    @staticmethod
    @jit(nopython=True)
    def _calculate_sma(data: np.ndarray, period: int) -> np.ndarray:
        """Calculate SMA"""
        n = len(data)
        result = np.full(n, np.nan)
        
        for i in range(period - 1, n):
            result[i] = np.mean(data[i - period + 1:i + 1])
        
        return result
    
    @staticmethod
    @jit(nopython=True)
    def _calculate_ema(data: np.ndarray, period: int) -> np.ndarray:
        """Calculate EMA"""
        n = len(data)
        result = np.empty(n)
        alpha = 2.0 / (period + 1)
        
        result[0] = data[0]
        for i in range(1, n):
            result[i] = alpha * data[i] + (1 - alpha) * result[i - 1]
        
        return result
    
    def calculate(self, data: Union[np.ndarray, pd.Series, list],
                 fast_period: int = 10, slow_period: int = 20,
                 ma_type: str = "SMA") -> Union[np.ndarray, pd.Series]:
        """
        Calculate Price Oscillator
        
        Parameters:
        -----------
        data : Union[np.ndarray, pd.Series, list]
            Price data (typically closing prices)
        fast_period : int, default=10
            Fast moving average period
        slow_period : int, default=20
            Slow moving average period
        ma_type : str, default="SMA"
            Type of moving average ("SMA" or "EMA")
            
        Returns:
        --------
        Union[np.ndarray, pd.Series]
            Price Oscillator values in the same format as input
        """
        validated_data, input_type, index = self.validate_input(data)
        
        if ma_type.upper() == "SMA":
            fast_ma = self._calculate_sma(validated_data, fast_period)
            slow_ma = self._calculate_sma(validated_data, slow_period)
        elif ma_type.upper() == "EMA":
            fast_ma = self._calculate_ema(validated_data, fast_period)
            slow_ma = self._calculate_ema(validated_data, slow_period)
        else:
            raise ValueError(f"Unsupported MA type: {ma_type}")
        
        result = fast_ma - slow_ma
        return self.format_output(result, input_type, index)


class DPO(BaseIndicator):
    """
    Detrended Price Oscillator
    
    DPO attempts to eliminate the trend in prices by comparing a past price 
    to a moving average.
    
    Formula: DPO = Price[n/2 + 1 periods ago] - SMA(n)
    """
    
    def __init__(self):
        super().__init__("DPO")
    
    @staticmethod
    @jit(nopython=True)
    def _calculate_sma(data: np.ndarray, period: int) -> np.ndarray:
        """Calculate SMA"""
        n = len(data)
        result = np.full(n, np.nan)
        
        for i in range(period - 1, n):
            result[i] = np.mean(data[i - period + 1:i + 1])
        
        return result
    
    def calculate(self, data: Union[np.ndarray, pd.Series, list], period: int = 20) -> Union[np.ndarray, pd.Series]:
        """
        Calculate Detrended Price Oscillator
        
        Parameters:
        -----------
        data : Union[np.ndarray, pd.Series, list]
            Price data (typically closing prices)
        period : int, default=20
            Period for SMA calculation
            
        Returns:
        --------
        Union[np.ndarray, pd.Series]
            DPO values in the same format as input
        """
        validated_data, input_type, index = self.validate_input(data)
        self.validate_period(period, len(validated_data))
        
        # Calculate SMA
        sma = self._calculate_sma(validated_data, period)
        
        # Calculate DPO
        dpo = np.full_like(validated_data, np.nan)
        offset = period // 2 + 1
        
        for i in range(offset, len(validated_data)):
            if not np.isnan(sma[i]):
                dpo[i] = validated_data[i - offset] - sma[i]
        
        return self.format_output(dpo, input_type, index)


class AROONOSC(BaseIndicator):
    """
    Aroon Oscillator
    
    The Aroon Oscillator is the difference between Aroon Up and Aroon Down.
    
    Formula: Aroon Oscillator = Aroon Up - Aroon Down
    """
    
    def __init__(self):
        super().__init__("Aroon Oscillator")
    
    @staticmethod
    @jit(nopython=True)
    def _calculate_aroon_osc(high: np.ndarray, low: np.ndarray, period: int) -> np.ndarray:
        """Numba optimized Aroon Oscillator calculation"""
        n = len(high)
        result = np.full(n, np.nan)
        
        for i in range(period - 1, n):
            # Find highest high and lowest low positions
            high_window = high[i - period + 1:i + 1]
            low_window = low[i - period + 1:i + 1]
            
            highest_pos = 0
            lowest_pos = 0
            
            for j in range(len(high_window)):
                if high_window[j] >= high_window[highest_pos]:
                    highest_pos = j
                if low_window[j] <= low_window[lowest_pos]:
                    lowest_pos = j
            
            # Calculate Aroon Up and Down
            aroon_up = ((period - (period - 1 - highest_pos)) / period) * 100
            aroon_down = ((period - (period - 1 - lowest_pos)) / period) * 100
            
            # Aroon Oscillator
            result[i] = aroon_up - aroon_down
        
        return result
    
    def calculate(self, high: Union[np.ndarray, pd.Series, list],
                 low: Union[np.ndarray, pd.Series, list],
                 period: int = 25) -> Union[np.ndarray, pd.Series]:
        """
        Calculate Aroon Oscillator
        
        Parameters:
        -----------
        high : Union[np.ndarray, pd.Series, list]
            High prices
        low : Union[np.ndarray, pd.Series, list]
            Low prices
        period : int, default=25
            Period for Aroon calculation
            
        Returns:
        --------
        Union[np.ndarray, pd.Series]
            Aroon Oscillator values in the same format as input
        """
        high_data, input_type, index = self.validate_input(high)
        low_data, _, _ = self.validate_input(low)
        
        high_data, low_data = self.align_arrays(high_data, low_data)
        self.validate_period(period, len(high_data))
        
        result = self._calculate_aroon_osc(high_data, low_data, period)
        return self.format_output(result, input_type, index)