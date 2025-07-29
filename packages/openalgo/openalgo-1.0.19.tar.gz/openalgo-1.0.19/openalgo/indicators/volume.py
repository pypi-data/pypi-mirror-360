# -*- coding: utf-8 -*-
"""
OpenAlgo Technical Indicators - Volume Indicators
"""

import numpy as np
import pandas as pd
from numba import jit
from typing import Union, Tuple, Optional
from .base import BaseIndicator


class OBV(BaseIndicator):
    """
    On Balance Volume
    
    OBV is a momentum indicator that uses volume flow to predict changes in stock price.
    It adds volume on up days and subtracts volume on down days.
    
    Formula:
    If Close > Previous Close: OBV = Previous OBV + Volume
    If Close < Previous Close: OBV = Previous OBV - Volume  
    If Close = Previous Close: OBV = Previous OBV
    """
    
    def __init__(self):
        super().__init__("OBV")
    
    @staticmethod
    @jit(nopython=True)
    def _calculate_obv(close: np.ndarray, volume: np.ndarray) -> np.ndarray:
        """Numba optimized OBV calculation"""
        n = len(close)
        # Seed baseline with first volume (TA-Lib behaviour)
        obv = np.empty(n)
        obv[0] = volume[0]
        
        # Calculate OBV
        for i in range(1, n):
            if close[i] > close[i-1]:
                obv[i] = obv[i-1] + volume[i]
            elif close[i] < close[i-1]:
                obv[i] = obv[i-1] - volume[i]
            else:
                obv[i] = obv[i-1]
        
        return obv
    
    def calculate(self, close: Union[np.ndarray, pd.Series, list],
                 volume: Union[np.ndarray, pd.Series, list]) -> Union[np.ndarray, pd.Series]:
        """
        Calculate On Balance Volume
        
        Parameters:
        -----------
        close : Union[np.ndarray, pd.Series, list]
            Closing prices
        volume : Union[np.ndarray, pd.Series, list]
            Volume data
            
        Returns:
        --------
        Union[np.ndarray, pd.Series]
            OBV values in the same format as input
        """
        close_data, input_type, index = self.validate_input(close)
        volume_data, _, _ = self.validate_input(volume)
        
        # Align arrays
        close_data, volume_data = self.align_arrays(close_data, volume_data)
        
        result = self._calculate_obv(close_data, volume_data)
        return self.format_output(result, input_type, index)


class VWAP(BaseIndicator):
    """
    Volume Weighted Average Price
    
    VWAP is the average price a security has traded at throughout the day, 
    based on both volume and price. It gives more weight to prices with higher volume.
    
    Formula: VWAP = Σ(Typical Price × Volume) / Σ(Volume)
    Where: Typical Price = (High + Low + Close) / 3
    """
    
    def __init__(self):
        super().__init__("VWAP")
    
    @staticmethod
    @jit(nopython=True)
    def _calculate_vwap(high: np.ndarray, low: np.ndarray, close: np.ndarray,
                       volume: np.ndarray, period: int = 0) -> np.ndarray:
        """Numba optimized VWAP calculation"""
        n = len(close)
        vwap = np.empty(n)
        
        # Calculate typical price
        typical_price = (high + low + close) / 3.0
        
        if period == 0:  # Cumulative VWAP
            cumulative_pv = 0.0
            cumulative_volume = 0.0
            
            for i in range(n):
                pv = typical_price[i] * volume[i]
                cumulative_pv += pv
                cumulative_volume += volume[i]
                
                if cumulative_volume > 0:
                    vwap[i] = cumulative_pv / cumulative_volume
                else:
                    vwap[i] = typical_price[i]
        else:  # Rolling VWAP
            vwap[:period-1] = np.nan
            
            for i in range(period - 1, n):
                sum_pv = 0.0
                sum_volume = 0.0
                
                for j in range(period):
                    idx = i - period + 1 + j
                    pv = typical_price[idx] * volume[idx]
                    sum_pv += pv
                    sum_volume += volume[idx]
                
                if sum_volume > 0:
                    vwap[i] = sum_pv / sum_volume
                else:
                    vwap[i] = typical_price[i]
        
        return vwap
    
    def calculate(self, high: Union[np.ndarray, pd.Series, list],
                 low: Union[np.ndarray, pd.Series, list],
                 close: Union[np.ndarray, pd.Series, list],
                 volume: Union[np.ndarray, pd.Series, list],
                 period: int = 0) -> Union[np.ndarray, pd.Series]:
        """
        Calculate Volume Weighted Average Price
        
        Parameters:
        -----------
        high : Union[np.ndarray, pd.Series, list]
            High prices
        low : Union[np.ndarray, pd.Series, list]
            Low prices
        close : Union[np.ndarray, pd.Series, list]
            Closing prices
        volume : Union[np.ndarray, pd.Series, list]
            Volume data
        period : int, default=0
            Period for rolling VWAP. If 0, calculates cumulative VWAP
            
        Returns:
        --------
        Union[np.ndarray, pd.Series]
            VWAP values in the same format as input
        """
        high_data, input_type, index = self.validate_input(high)
        low_data, _, _ = self.validate_input(low)
        close_data, _, _ = self.validate_input(close)
        volume_data, _, _ = self.validate_input(volume)
        
        # Align arrays
        high_data, low_data, close_data, volume_data = self.align_arrays(high_data, low_data, close_data, volume_data)
        
        if period > 0:
            self.validate_period(period, len(close_data))
        
        result = self._calculate_vwap(high_data, low_data, close_data, volume_data, period)
        return self.format_output(result, input_type, index)


class MFI(BaseIndicator):
    """
    Money Flow Index
    
    MFI is a momentum indicator that uses both price and volume to measure 
    buying and selling pressure. It is also known as Volume-Weighted RSI.
    
    Formula:
    1. Typical Price = (High + Low + Close) / 3
    2. Raw Money Flow = Typical Price × Volume
    3. Positive/Negative Money Flow based on Typical Price comparison
    4. Money Ratio = Positive Money Flow / Negative Money Flow
    5. MFI = 100 - (100 / (1 + Money Ratio))
    """
    
    def __init__(self):
        super().__init__("MFI")
    
    @staticmethod
    @jit(nopython=True)
    def _calculate_mfi(high: np.ndarray, low: np.ndarray, close: np.ndarray,
                      volume: np.ndarray, period: int) -> np.ndarray:
        """Numba optimized MFI aligned with TA-Lib"""
        n = len(close)
        result = np.full(n, np.nan)
        
        tp = (high + low + close) / 3.0
        rmf = tp * volume  # raw money flow
        
        # Pre-compute positive / negative flows per bar
        pos_raw = np.zeros(n)
        neg_raw = np.zeros(n)
        for i in range(1, n):
            if tp[i] > tp[i - 1]:
                pos_raw[i] = rmf[i]
            elif tp[i] < tp[i - 1]:
                neg_raw[i] = rmf[i]
        
        # Rolling window sums
        pos_sum = 0.0
        neg_sum = 0.0
        for i in range(1, n):
            pos_sum += pos_raw[i]
            neg_sum += neg_raw[i]
            
            if i >= period:
                pos_sum -= pos_raw[i - period]
                neg_sum -= neg_raw[i - period]
            
            if i >= period - 1:
                if neg_sum == 0:
                    result[i] = 100.0
                else:
                    m_ratio = pos_sum / neg_sum
                    result[i] = 100.0 - (100.0 / (1.0 + m_ratio))
        
        return result
    
    def calculate(self, high: Union[np.ndarray, pd.Series, list],
                 low: Union[np.ndarray, pd.Series, list],
                 close: Union[np.ndarray, pd.Series, list],
                 volume: Union[np.ndarray, pd.Series, list],
                 period: int = 14) -> Union[np.ndarray, pd.Series]:
        """
        Calculate Money Flow Index
        
        Parameters:
        -----------
        high : Union[np.ndarray, pd.Series, list]
            High prices
        low : Union[np.ndarray, pd.Series, list]
            Low prices
        close : Union[np.ndarray, pd.Series, list]
            Closing prices
        volume : Union[np.ndarray, pd.Series, list]
            Volume data
        period : int, default=14
            Number of periods for MFI calculation
            
        Returns:
        --------
        Union[np.ndarray, pd.Series]
            MFI values (range: 0 to 100) in the same format as input
        """
        high_data, input_type, index = self.validate_input(high)
        low_data, _, _ = self.validate_input(low)
        close_data, _, _ = self.validate_input(close)
        volume_data, _, _ = self.validate_input(volume)
        
        # Align arrays
        high_data, low_data, close_data, volume_data = self.align_arrays(high_data, low_data, close_data, volume_data)
        self.validate_period(period, len(close_data))
        
        result = self._calculate_mfi(high_data, low_data, close_data, volume_data, period)
        return self.format_output(result, input_type, index)


class ADL(BaseIndicator):
    """
    Accumulation/Distribution Line
    
    ADL is a volume-based indicator designed to measure the cumulative flow 
    of money into and out of a security.
    
    Formula: ADL = Previous ADL + Money Flow Volume
    Where: Money Flow Volume = Volume × ((Close - Low) - (High - Close)) / (High - Low)
    """
    
    def __init__(self):
        super().__init__("ADL")
    
    @staticmethod
    @jit(nopython=True)
    def _calculate_adl(high: np.ndarray, low: np.ndarray, close: np.ndarray,
                      volume: np.ndarray) -> np.ndarray:
        """Numba optimized ADL calculation"""
        n = len(close)
        result = np.full(n, np.nan)
        
        result[0] = 0.0  # Seed baseline at 0 as per common definition
        
        for i in range(1, n):
            if high[i] != low[i]:
                mfm = ((close[i] - low[i]) - (high[i] - close[i])) / (high[i] - low[i])
            else:
                mfm = 0.0
            
            mfv = mfm * volume[i]
            result[i] = result[i - 1] + mfv
        
        return result
    
    def calculate(self, high: Union[np.ndarray, pd.Series, list],
                 low: Union[np.ndarray, pd.Series, list],
                 close: Union[np.ndarray, pd.Series, list],
                 volume: Union[np.ndarray, pd.Series, list]) -> Union[np.ndarray, pd.Series]:
        """
        Calculate Accumulation/Distribution Line
        
        Parameters:
        -----------
        high : Union[np.ndarray, pd.Series, list]
            High prices
        low : Union[np.ndarray, pd.Series, list]
            Low prices
        close : Union[np.ndarray, pd.Series, list]
            Closing prices
        volume : Union[np.ndarray, pd.Series, list]
            Volume data
            
        Returns:
        --------
        Union[np.ndarray, pd.Series]
            ADL values in the same format as input
        """
        high_data, input_type, index = self.validate_input(high)
        low_data, _, _ = self.validate_input(low)
        close_data, _, _ = self.validate_input(close)
        volume_data, _, _ = self.validate_input(volume)
        
        high_data, low_data, close_data, volume_data = self.align_arrays(high_data, low_data, close_data, volume_data)
        
        result = self._calculate_adl(high_data, low_data, close_data, volume_data)
        return self.format_output(result, input_type, index)


class CMF(BaseIndicator):
    """
    Chaikin Money Flow
    
    CMF is the sum of Money Flow Volume over a period divided by the sum of volume.
    
    Formula: CMF = Sum(Money Flow Volume, n) / Sum(Volume, n)
    """
    
    def __init__(self):
        super().__init__("CMF")
    
    @staticmethod
    @jit(nopython=True)
    def _calculate_cmf(high: np.ndarray, low: np.ndarray, close: np.ndarray,
                      volume: np.ndarray, period: int) -> np.ndarray:
        """Numba optimized CMF calculation"""
        n = len(close)
        result = np.full(n, np.nan)
        
        for i in range(period - 1, n):
            sum_mfv = 0.0
            sum_volume = 0.0
            
            for j in range(period):
                idx = i - period + 1 + j
                
                if high[idx] != low[idx]:
                    mfm = ((close[idx] - low[idx]) - (high[idx] - close[idx])) / (high[idx] - low[idx])
                else:
                    mfm = 0
                
                mfv = mfm * volume[idx]
                sum_mfv += mfv
                sum_volume += volume[idx]
            
            if sum_volume > 0:
                result[i] = sum_mfv / sum_volume
            else:
                result[i] = 0
        
        return result
    
    def calculate(self, high: Union[np.ndarray, pd.Series, list],
                 low: Union[np.ndarray, pd.Series, list],
                 close: Union[np.ndarray, pd.Series, list],
                 volume: Union[np.ndarray, pd.Series, list],
                 period: int = 20) -> Union[np.ndarray, pd.Series]:
        """
        Calculate Chaikin Money Flow
        
        Parameters:
        -----------
        high : Union[np.ndarray, pd.Series, list]
            High prices
        low : Union[np.ndarray, pd.Series, list]
            Low prices
        close : Union[np.ndarray, pd.Series, list]
            Closing prices
        volume : Union[np.ndarray, pd.Series, list]
            Volume data
        period : int, default=20
            Number of periods for CMF calculation
            
        Returns:
        --------
        Union[np.ndarray, pd.Series]
            CMF values in the same format as input
        """
        high_data, input_type, index = self.validate_input(high)
        low_data, _, _ = self.validate_input(low)
        close_data, _, _ = self.validate_input(close)
        volume_data, _, _ = self.validate_input(volume)
        
        high_data, low_data, close_data, volume_data = self.align_arrays(high_data, low_data, close_data, volume_data)
        self.validate_period(period, len(close_data))
        
        result = self._calculate_cmf(high_data, low_data, close_data, volume_data, period)
        return self.format_output(result, input_type, index)


class EMV(BaseIndicator):
    """
    Ease of Movement
    
    EMV relates price change to volume and is particularly useful 
    for assessing the strength of a trend.
    
    Formula: EMV = Distance Moved / Box Ratio
    Where: Distance Moved = (High + Low)/2 - (Previous High + Previous Low)/2
           Box Ratio = Volume / (High - Low)
    """
    
    def __init__(self):
        super().__init__("EMV")
    
    @staticmethod
    @jit(nopython=True)
    def _calculate_emv(high: np.ndarray, low: np.ndarray, volume: np.ndarray,
                      scale: float) -> np.ndarray:
        """Numba optimized EMV calculation"""
        n = len(high)
        result = np.full(n, np.nan)
        
        for i in range(1, n):
            # Distance moved
            hl_avg = (high[i] + low[i]) / 2
            prev_hl_avg = (high[i-1] + low[i-1]) / 2
            distance = hl_avg - prev_hl_avg
            
            # Box ratio
            if high[i] != low[i] and volume[i] > 0:
                box_ratio = volume[i] / (high[i] - low[i])
                result[i] = (distance / box_ratio) * scale
            else:
                result[i] = 0
        
        return result
    
    def calculate(self, high: Union[np.ndarray, pd.Series, list],
                 low: Union[np.ndarray, pd.Series, list],
                 volume: Union[np.ndarray, pd.Series, list],
                 scale: float = 1000000) -> Union[np.ndarray, pd.Series]:
        """
        Calculate Ease of Movement
        
        Parameters:
        -----------
        high : Union[np.ndarray, pd.Series, list]
            High prices
        low : Union[np.ndarray, pd.Series, list]
            Low prices
        volume : Union[np.ndarray, pd.Series, list]
            Volume data
        scale : float, default=1000000
            Scale factor for EMV values
            
        Returns:
        --------
        Union[np.ndarray, pd.Series]
            EMV values in the same format as input
        """
        high_data, input_type, index = self.validate_input(high)
        low_data, _, _ = self.validate_input(low)
        volume_data, _, _ = self.validate_input(volume)
        
        high_data, low_data, volume_data = self.align_arrays(high_data, low_data, volume_data)
        
        result = self._calculate_emv(high_data, low_data, volume_data, scale)
        return self.format_output(result, input_type, index)


class FI(BaseIndicator):
    """
    Force Index
    
    Force Index combines price and volume to assess the power used to move 
    the price of an asset.
    
    Formula: FI = Volume × (Close - Previous Close)
    """
    
    def __init__(self):
        super().__init__("FI")
    
    @staticmethod
    @jit(nopython=True)
    def _calculate_fi(close: np.ndarray, volume: np.ndarray) -> np.ndarray:
        """Numba optimized Force Index calculation"""
        n = len(close)
        result = np.full(n, np.nan)
        
        for i in range(1, n):
            price_change = close[i] - close[i-1]
            result[i] = volume[i] * price_change
        
        return result
    
    def calculate(self, close: Union[np.ndarray, pd.Series, list],
                 volume: Union[np.ndarray, pd.Series, list]) -> Union[np.ndarray, pd.Series]:
        """
        Calculate Force Index
        
        Parameters:
        -----------
        close : Union[np.ndarray, pd.Series, list]
            Closing prices
        volume : Union[np.ndarray, pd.Series, list]
            Volume data
            
        Returns:
        --------
        Union[np.ndarray, pd.Series]
            Force Index values in the same format as input
        """
        close_data, input_type, index = self.validate_input(close)
        volume_data, _, _ = self.validate_input(volume)
        
        close_data, volume_data = self.align_arrays(close_data, volume_data)
        
        result = self._calculate_fi(close_data, volume_data)
        return self.format_output(result, input_type, index)


class NVI(BaseIndicator):
    """
    Negative Volume Index
    
    NVI focuses on days when volume decreases from the previous day.
    
    Formula: If Volume < Previous Volume: NVI = Previous NVI × (1 + PCR)
             Else: NVI = Previous NVI
    Where: PCR = (Close - Previous Close) / Previous Close
    """
    
    def __init__(self):
        super().__init__("NVI")
    
    @staticmethod
    @jit(nopython=True)
    def _calculate_nvi(close: np.ndarray, volume: np.ndarray) -> np.ndarray:
        """Numba optimized NVI calculation"""
        n = len(close)
        result = np.empty(n)
        
        result[0] = 1000  # Start with base value
        
        for i in range(1, n):
            if volume[i] < volume[i-1]:
                pcr = (close[i] - close[i-1]) / close[i-1] if close[i-1] != 0 else 0
                result[i] = result[i-1] * (1 + pcr)
            else:
                result[i] = result[i-1]
        
        return result
    
    def calculate(self, close: Union[np.ndarray, pd.Series, list],
                 volume: Union[np.ndarray, pd.Series, list]) -> Union[np.ndarray, pd.Series]:
        """
        Calculate Negative Volume Index
        
        Parameters:
        -----------
        close : Union[np.ndarray, pd.Series, list]
            Closing prices
        volume : Union[np.ndarray, pd.Series, list]
            Volume data
            
        Returns:
        --------
        Union[np.ndarray, pd.Series]
            NVI values in the same format as input
        """
        close_data, input_type, index = self.validate_input(close)
        volume_data, _, _ = self.validate_input(volume)
        
        close_data, volume_data = self.align_arrays(close_data, volume_data)
        
        result = self._calculate_nvi(close_data, volume_data)
        return self.format_output(result, input_type, index)


class PVI(BaseIndicator):
    """
    Positive Volume Index
    
    PVI focuses on days when volume increases from the previous day.
    
    Formula: If Volume > Previous Volume: PVI = Previous PVI × (1 + PCR)
             Else: PVI = Previous PVI
    Where: PCR = (Close - Previous Close) / Previous Close
    """
    
    def __init__(self):
        super().__init__("PVI")
    
    @staticmethod
    @jit(nopython=True)
    def _calculate_pvi(close: np.ndarray, volume: np.ndarray) -> np.ndarray:
        """Numba optimized PVI calculation"""
        n = len(close)
        result = np.empty(n)
        
        result[0] = 1000  # Start with base value
        
        for i in range(1, n):
            if volume[i] > volume[i-1]:
                pcr = (close[i] - close[i-1]) / close[i-1] if close[i-1] != 0 else 0
                result[i] = result[i-1] * (1 + pcr)
            else:
                result[i] = result[i-1]
        
        return result
    
    def calculate(self, close: Union[np.ndarray, pd.Series, list],
                 volume: Union[np.ndarray, pd.Series, list]) -> Union[np.ndarray, pd.Series]:
        """
        Calculate Positive Volume Index
        
        Parameters:
        -----------
        close : Union[np.ndarray, pd.Series, list]
            Closing prices
        volume : Union[np.ndarray, pd.Series, list]
            Volume data
            
        Returns:
        --------
        Union[np.ndarray, pd.Series]
            PVI values in the same format as input
        """
        close_data, input_type, index = self.validate_input(close)
        volume_data, _, _ = self.validate_input(volume)
        
        close_data, volume_data = self.align_arrays(close_data, volume_data)
        
        result = self._calculate_pvi(close_data, volume_data)
        return self.format_output(result, input_type, index)


class VO(BaseIndicator):
    """
    Volume Oscillator
    
    Volume Oscillator shows the relationship between two moving averages of volume.
    
    Formula: VO = ((Short MA - Long MA) / Long MA) × 100
    """
    
    def __init__(self):
        super().__init__("VO")
    
    @staticmethod
    @jit(nopython=True)
    def _calculate_sma(data: np.ndarray, period: int) -> np.ndarray:
        """Calculate SMA"""
        n = len(data)
        result = np.full(n, np.nan)
        
        for i in range(period - 1, n):
            result[i] = np.mean(data[i - period + 1:i + 1])
        
        return result
    
    def calculate(self, volume: Union[np.ndarray, pd.Series, list],
                 fast_period: int = 5, slow_period: int = 10) -> Union[np.ndarray, pd.Series]:
        """
        Calculate Volume Oscillator
        
        Parameters:
        -----------
        volume : Union[np.ndarray, pd.Series, list]
            Volume data
        fast_period : int, default=5
            Fast moving average period
        slow_period : int, default=10
            Slow moving average period
            
        Returns:
        --------
        Union[np.ndarray, pd.Series]
            Volume Oscillator values in the same format as input
        """
        validated_volume, input_type, index = self.validate_input(volume)
        
        # Calculate moving averages
        fast_ma = self._calculate_sma(validated_volume, fast_period)
        slow_ma = self._calculate_sma(validated_volume, slow_period)
        
        # Calculate Volume Oscillator
        vo = np.empty_like(validated_volume)
        for i in range(len(validated_volume)):
            if slow_ma[i] != 0:
                vo[i] = ((fast_ma[i] - slow_ma[i]) / slow_ma[i]) * 100
            else:
                vo[i] = 0
        
        return self.format_output(vo, input_type, index)


class VROC(BaseIndicator):
    """
    Volume Rate of Change
    
    VROC measures the rate of change in volume.
    
    Formula: VROC = ((Volume - Volume[n periods ago]) / Volume[n periods ago]) × 100
    """
    
    def __init__(self):
        super().__init__("VROC")
    
    @staticmethod
    @jit(nopython=True)
    def _calculate_vroc(volume: np.ndarray, period: int) -> np.ndarray:
        """Numba optimized VROC calculation"""
        n = len(volume)
        result = np.full(n, np.nan)
        
        for i in range(period, n):
            if volume[i - period] != 0:
                result[i] = ((volume[i] - volume[i - period]) / volume[i - period]) * 100
            else:
                result[i] = 0
        
        return result
    
    def calculate(self, volume: Union[np.ndarray, pd.Series, list], period: int = 25) -> Union[np.ndarray, pd.Series]:
        """
        Calculate Volume Rate of Change
        
        Parameters:
        -----------
        volume : Union[np.ndarray, pd.Series, list]
            Volume data
        period : int, default=25
            Number of periods to look back
            
        Returns:
        --------
        Union[np.ndarray, pd.Series]
            VROC values in the same format as input
        """
        validated_volume, input_type, index = self.validate_input(volume)
        self.validate_period(period, len(validated_volume))
        
        result = self._calculate_vroc(validated_volume, period)
        return self.format_output(result, input_type, index)