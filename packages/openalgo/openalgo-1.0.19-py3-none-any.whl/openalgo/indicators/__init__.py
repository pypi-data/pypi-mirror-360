# -*- coding: utf-8 -*-
"""
OpenAlgo Technical Indicators Library

A high-performance technical analysis library with NumPy and Numba optimizations.
Provides TradingView-like syntax for easy use.
"""

import numpy as np
import pandas as pd
from typing import Union, Tuple, Optional

# Import all indicator classes
from .trend import (SMA, EMA, WMA, DEMA, TEMA, Supertrend, Ichimoku, HMA, VWMA, 
                   ALMA, KAMA, ZLEMA, T3, FRAMA)
from .momentum import RSI, MACD, Stochastic, CCI, WilliamsR
from .volatility import (ATR, BollingerBands, KeltnerChannel, DonchianChannel,
                        ChaikinVolatility, NATR, RVI, ULTOSC, STDDEV, TRANGE, MASS)
from .volume import (OBV, VWAP, MFI, ADL, CMF, EMV, FI, NVI, PVI, VO, VROC)
from .oscillators import (ROC, CMO, TRIX, UO, AO, AC, PPO, PO, DPO, AROONOSC)
from .statistics import (LINEARREG, LINEARREG_SLOPE, CORREL, BETA, VAR, TSF, MEDIAN, MODE)
from .hybrid import (ADX, Aroon, PivotPoints, SAR, DMI, PSAR, HT_TRENDLINE)
from .utils import (crossover, crossunder, highest, lowest, change, roc, 
                   sma as utils_sma, ema as utils_ema, stdev, validate_input)


class TechnicalAnalysis:
    """
    Main technical analysis interface providing TradingView-like syntax
    
    Usage:
    ------
    from openalgo import ta
    
    # Trend indicators
    sma_20 = ta.sma(close, 20)
    ema_50 = ta.ema(close, 50)
    [supertrend, direction] = ta.supertrend(high, low, close, 10, 3)
    
    # Momentum indicators
    rsi_14 = ta.rsi(close, 14)
    [macd_line, signal_line, histogram] = ta.macd(close, 12, 26, 9)
    
    # Volatility indicators
    [upper, middle, lower] = ta.bbands(close, 20, 2)
    atr_14 = ta.atr(high, low, close, 14)
    
    # Volume indicators
    obv_values = ta.obv(close, volume)
    vwap_values = ta.vwap(high, low, close, volume)
    """
    
    def __init__(self):
        # Initialize all indicator classes
        # Trend indicators
        self._sma = SMA()
        self._ema = EMA()
        self._wma = WMA()
        self._dema = DEMA()
        self._tema = TEMA()
        self._hma = HMA()
        self._vwma = VWMA()
        self._alma = ALMA()
        self._kama = KAMA()
        self._zlema = ZLEMA()
        self._t3 = T3()
        self._frama = FRAMA()
        self._supertrend = Supertrend()
        self._ichimoku = Ichimoku()
        
        # Momentum indicators
        self._rsi = RSI()
        self._macd = MACD()
        self._stochastic = Stochastic()
        self._cci = CCI()
        self._williams_r = WilliamsR()
        
        # Volatility indicators
        self._atr = ATR()
        self._bbands = BollingerBands()
        self._keltner = KeltnerChannel()
        self._donchian = DonchianChannel()
        self._chaikin_volatility = ChaikinVolatility()
        self._natr = NATR()
        self._rvi = RVI()
        self._ultosc = ULTOSC()
        self._stddev = STDDEV()
        self._trange = TRANGE()
        self._mass = MASS()
        
        # Volume indicators
        self._obv = OBV()
        self._vwap = VWAP()
        self._mfi = MFI()
        self._adl = ADL()
        self._cmf = CMF()
        self._emv = EMV()
        self._fi = FI()
        self._nvi = NVI()
        self._pvi = PVI()
        self._vo = VO()
        self._vroc = VROC()
        
        # Oscillators
        self._roc = ROC()
        self._cmo = CMO()
        self._trix = TRIX()
        self._uo = UO()
        self._ao = AO()
        self._ac = AC()
        self._ppo = PPO()
        self._po = PO()
        self._dpo = DPO()
        self._aroonosc = AROONOSC()
        
        # Statistical indicators
        self._linearreg = LINEARREG()
        self._linearreg_slope = LINEARREG_SLOPE()
        self._correl = CORREL()
        self._beta = BETA()
        self._var = VAR()
        self._tsf = TSF()
        self._median = MEDIAN()
        self._mode = MODE()
        
        # Hybrid indicators
        self._adx = ADX()
        self._aroon = Aroon()
        self._pivot_points = PivotPoints()
        self._sar = SAR()
        self._dmi = DMI()
        self._psar = PSAR()
        self._ht_trendline = HT_TRENDLINE()
    
    # =================== TREND INDICATORS ===================
    
    def sma(self, data: Union[np.ndarray, pd.Series, list], period: int) -> Union[np.ndarray, pd.Series]:
        """
        Simple Moving Average
        
        Parameters:
        -----------
        data : Union[np.ndarray, pd.Series, list]
            Price data (typically closing prices)
        period : int
            Number of periods for the moving average
            
        Returns:
        --------
        Union[np.ndarray, pd.Series]
            SMA values in the same format as input
        """
        return self._sma.calculate(data, period)
    
    def ema(self, data: Union[np.ndarray, pd.Series, list], period: int) -> Union[np.ndarray, pd.Series]:
        """
        Exponential Moving Average
        
        Parameters:
        -----------
        data : Union[np.ndarray, pd.Series, list]
            Price data (typically closing prices)
        period : int
            Number of periods for the moving average
            
        Returns:
        --------
        Union[np.ndarray, pd.Series]
            EMA values in the same format as input
        """
        return self._ema.calculate(data, period)
    
    def wma(self, data: Union[np.ndarray, pd.Series, list], period: int) -> np.ndarray:
        """
        Weighted Moving Average
        
        Parameters:
        -----------
        data : Union[np.ndarray, pd.Series, list]
            Price data (typically closing prices)
        period : int
            Number of periods for the moving average
            
        Returns:
        --------
        np.ndarray
            Array of WMA values
        """
        return self._wma.calculate(data, period)
    
    def dema(self, data: Union[np.ndarray, pd.Series, list], period: int) -> np.ndarray:
        """
        Double Exponential Moving Average
        
        Parameters:
        -----------
        data : Union[np.ndarray, pd.Series, list]
            Price data (typically closing prices)
        period : int
            Number of periods for the moving average
            
        Returns:
        --------
        np.ndarray
            Array of DEMA values
        """
        return self._dema.calculate(data, period)
    
    def tema(self, data: Union[np.ndarray, pd.Series, list], period: int) -> np.ndarray:
        """
        Triple Exponential Moving Average
        
        Parameters:
        -----------
        data : Union[np.ndarray, pd.Series, list]
            Price data (typically closing prices)
        period : int
            Number of periods for the moving average
            
        Returns:
        --------
        np.ndarray
            Array of TEMA values
        """
        return self._tema.calculate(data, period)
    
    def supertrend(self, high: Union[np.ndarray, pd.Series, list],
                   low: Union[np.ndarray, pd.Series, list],
                   close: Union[np.ndarray, pd.Series, list],
                   period: int = 10, multiplier: float = 3.0) -> Union[Tuple[np.ndarray, np.ndarray], Tuple[pd.Series, pd.Series]]:
        """
        Supertrend Indicator
        
        Parameters:
        -----------
        high : Union[np.ndarray, pd.Series, list]
            High prices
        low : Union[np.ndarray, pd.Series, list]
            Low prices
        close : Union[np.ndarray, pd.Series, list]
            Closing prices
        period : int, default=10
            ATR period
        multiplier : float, default=3.0
            ATR multiplier
            
        Returns:
        --------
        Union[Tuple[np.ndarray, np.ndarray], Tuple[pd.Series, pd.Series]]
            (supertrend values, direction values) in the same format as input
        """
        return self._supertrend.calculate(high, low, close, period, multiplier)
    
    def ichimoku(self, high: Union[np.ndarray, pd.Series, list],
                 low: Union[np.ndarray, pd.Series, list],
                 close: Union[np.ndarray, pd.Series, list],
                 tenkan_period: int = 9, kijun_period: int = 26,
                 senkou_b_period: int = 52, displacement: int = 26) -> Tuple[np.ndarray, ...]:
        """
        Ichimoku Cloud
        
        Parameters:
        -----------
        high : Union[np.ndarray, pd.Series, list]
            High prices
        low : Union[np.ndarray, pd.Series, list]
            Low prices
        close : Union[np.ndarray, pd.Series, list]
            Closing prices
        tenkan_period : int, default=9
            Period for Tenkan-sen calculation
        kijun_period : int, default=26
            Period for Kijun-sen calculation
        senkou_b_period : int, default=52
            Period for Senkou Span B calculation
        displacement : int, default=26
            Displacement for Senkou Spans and Chikou Span
            
        Returns:
        --------
        Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]
            (tenkan_sen, kijun_sen, senkou_span_a, senkou_span_b, chikou_span)
        """
        return self._ichimoku.calculate(high, low, close, tenkan_period, 
                                       kijun_period, senkou_b_period, displacement)
    
    def hma(self, data: Union[np.ndarray, pd.Series, list], period: int) -> np.ndarray:
        """Hull Moving Average"""
        return self._hma.calculate(data, period)
    
    def vwma(self, data: Union[np.ndarray, pd.Series, list],
             volume: Union[np.ndarray, pd.Series, list], period: int) -> np.ndarray:
        """Volume Weighted Moving Average"""
        return self._vwma.calculate(data, volume, period)
    
    def alma(self, data: Union[np.ndarray, pd.Series, list], 
             period: int = 21, offset: float = 0.85, sigma: float = 6.0) -> np.ndarray:
        """Arnaud Legoux Moving Average"""
        return self._alma.calculate(data, period, offset, sigma)
    
    def kama(self, data: Union[np.ndarray, pd.Series, list],
             period: int = 10, fast_period: int = 2, slow_period: int = 30) -> np.ndarray:
        """Kaufman's Adaptive Moving Average"""
        return self._kama.calculate(data, period, fast_period, slow_period)
    
    def zlema(self, data: Union[np.ndarray, pd.Series, list], period: int) -> np.ndarray:
        """Zero Lag Exponential Moving Average"""
        return self._zlema.calculate(data, period)
    
    def t3(self, data: Union[np.ndarray, pd.Series, list],
           period: int = 21, v_factor: float = 0.7) -> np.ndarray:
        """T3 Moving Average"""
        return self._t3.calculate(data, period, v_factor)
    
    def frama(self, data: Union[np.ndarray, pd.Series, list], period: int = 16) -> np.ndarray:
        """Fractal Adaptive Moving Average"""
        return self._frama.calculate(data, period)
    
    # =================== MOMENTUM INDICATORS ===================
    
    def rsi(self, data: Union[np.ndarray, pd.Series, list], period: int = 14) -> np.ndarray:
        """
        Relative Strength Index
        
        Parameters:
        -----------
        data : Union[np.ndarray, pd.Series, list]
            Price data (typically closing prices)
        period : int, default=14
            Number of periods for RSI calculation
            
        Returns:
        --------
        np.ndarray
            Array of RSI values
        """
        return self._rsi.calculate(data, period)
    
    def macd(self, data: Union[np.ndarray, pd.Series, list], 
             fast_period: int = 12, slow_period: int = 26, 
             signal_period: int = 9) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Moving Average Convergence Divergence
        
        Parameters:
        -----------
        data : Union[np.ndarray, pd.Series, list]
            Price data (typically closing prices)
        fast_period : int, default=12
            Period for fast EMA
        slow_period : int, default=26
            Period for slow EMA
        signal_period : int, default=9
            Period for signal line EMA
            
        Returns:
        --------
        Tuple[np.ndarray, np.ndarray, np.ndarray]
            (macd_line, signal_line, histogram)
        """
        return self._macd.calculate(data, fast_period, slow_period, signal_period)
    
    def stochastic(self, high: Union[np.ndarray, pd.Series, list],
                   low: Union[np.ndarray, pd.Series, list],
                   close: Union[np.ndarray, pd.Series, list],
                   k_period: int = 14, d_period: int = 3) -> Tuple[np.ndarray, np.ndarray]:
        """
        Stochastic Oscillator
        
        Parameters:
        -----------
        high : Union[np.ndarray, pd.Series, list]
            High prices
        low : Union[np.ndarray, pd.Series, list]
            Low prices
        close : Union[np.ndarray, pd.Series, list]
            Closing prices
        k_period : int, default=14
            Period for %K calculation
        d_period : int, default=3
            Period for %D calculation
            
        Returns:
        --------
        Tuple[np.ndarray, np.ndarray]
            (k_percent, d_percent)
        """
        return self._stochastic.calculate(high, low, close, k_period, d_period)
    
    def cci(self, high: Union[np.ndarray, pd.Series, list],
            low: Union[np.ndarray, pd.Series, list],
            close: Union[np.ndarray, pd.Series, list],
            period: int = 20) -> np.ndarray:
        """
        Commodity Channel Index
        
        Parameters:
        -----------
        high : Union[np.ndarray, pd.Series, list]
            High prices
        low : Union[np.ndarray, pd.Series, list]
            Low prices
        close : Union[np.ndarray, pd.Series, list]
            Closing prices
        period : int, default=20
            Number of periods for CCI calculation
            
        Returns:
        --------
        np.ndarray
            Array of CCI values
        """
        return self._cci.calculate(high, low, close, period)
    
    def williams_r(self, high: Union[np.ndarray, pd.Series, list],
                   low: Union[np.ndarray, pd.Series, list],
                   close: Union[np.ndarray, pd.Series, list],
                   period: int = 14) -> np.ndarray:
        """
        Williams %R
        
        Parameters:
        -----------
        high : Union[np.ndarray, pd.Series, list]
            High prices
        low : Union[np.ndarray, pd.Series, list]
            Low prices
        close : Union[np.ndarray, pd.Series, list]
            Closing prices
        period : int, default=14
            Number of periods for Williams %R calculation
            
        Returns:
        --------
        np.ndarray
            Array of Williams %R values
        """
        return self._williams_r.calculate(high, low, close, period)
    
    # =================== VOLATILITY INDICATORS ===================
    
    def atr(self, high: Union[np.ndarray, pd.Series, list],
            low: Union[np.ndarray, pd.Series, list],
            close: Union[np.ndarray, pd.Series, list],
            period: int = 14) -> np.ndarray:
        """
        Average True Range
        
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
        np.ndarray
            Array of ATR values
        """
        return self._atr.calculate(high, low, close, period)
    
    def bbands(self, data: Union[np.ndarray, pd.Series, list],
               period: int = 20, std_dev: float = 2.0) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Bollinger Bands
        
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
        Tuple[np.ndarray, np.ndarray, np.ndarray]
            (upper_band, middle_band, lower_band)
        """
        return self._bbands.calculate(data, period, std_dev)
    
    def keltner_channel(self, high: Union[np.ndarray, pd.Series, list],
                        low: Union[np.ndarray, pd.Series, list],
                        close: Union[np.ndarray, pd.Series, list],
                        ema_period: int = 20, atr_period: int = 10, 
                        multiplier: float = 2.0) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Keltner Channel
        
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
        Tuple[np.ndarray, np.ndarray, np.ndarray]
            (upper_channel, middle_line, lower_channel)
        """
        return self._keltner.calculate(high, low, close, ema_period, atr_period, multiplier)
    
    def donchian_channel(self, high: Union[np.ndarray, pd.Series, list],
                         low: Union[np.ndarray, pd.Series, list],
                         period: int = 20) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Donchian Channel
        
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
        Tuple[np.ndarray, np.ndarray, np.ndarray]
            (upper_channel, middle_line, lower_channel)
        """
        return self._donchian.calculate(high, low, period)
    
    def chaikin_volatility(self, high: Union[np.ndarray, pd.Series, list],
                          low: Union[np.ndarray, pd.Series, list],
                          ema_period: int = 10, roc_period: int = 10) -> np.ndarray:
        """Chaikin Volatility"""
        return self._chaikin_volatility.calculate(high, low, ema_period, roc_period)
    
    def natr(self, high: Union[np.ndarray, pd.Series, list],
             low: Union[np.ndarray, pd.Series, list],
             close: Union[np.ndarray, pd.Series, list],
             period: int = 14) -> np.ndarray:
        """Normalized Average True Range"""
        return self._natr.calculate(high, low, close, period)
    
    def rvi_volatility(self, data: Union[np.ndarray, pd.Series, list],
                      stdev_period: int = 10, rsi_period: int = 14) -> np.ndarray:
        """Relative Volatility Index"""
        return self._rvi.calculate(data, stdev_period, rsi_period)
    
    def ultimate_oscillator(self, high: Union[np.ndarray, pd.Series, list],
                           low: Union[np.ndarray, pd.Series, list],
                           close: Union[np.ndarray, pd.Series, list],
                           period1: int = 7, period2: int = 14, period3: int = 28) -> np.ndarray:
        """Ultimate Oscillator"""
        return self._ultosc.calculate(high, low, close, period1, period2, period3)
    
    def stddev(self, data: Union[np.ndarray, pd.Series, list], period: int = 20) -> np.ndarray:
        """Standard Deviation"""
        return self._stddev.calculate(data, period)
    
    def true_range(self, high: Union[np.ndarray, pd.Series, list],
                   low: Union[np.ndarray, pd.Series, list],
                   close: Union[np.ndarray, pd.Series, list]) -> np.ndarray:
        """True Range"""
        return self._trange.calculate(high, low, close)
    
    def mass_index(self, high: Union[np.ndarray, pd.Series, list],
                   low: Union[np.ndarray, pd.Series, list],
                   fast_period: int = 9, slow_period: int = 25) -> np.ndarray:
        """Mass Index"""
        return self._mass.calculate(high, low, fast_period, slow_period)
    
    # =================== VOLUME INDICATORS ===================
    
    def obv(self, close: Union[np.ndarray, pd.Series, list],
            volume: Union[np.ndarray, pd.Series, list]) -> np.ndarray:
        """
        On Balance Volume
        
        Parameters:
        -----------
        close : Union[np.ndarray, pd.Series, list]
            Closing prices
        volume : Union[np.ndarray, pd.Series, list]
            Volume data
            
        Returns:
        --------
        np.ndarray
            Array of OBV values
        """
        return self._obv.calculate(close, volume)
    
    def vwap(self, high: Union[np.ndarray, pd.Series, list],
             low: Union[np.ndarray, pd.Series, list],
             close: Union[np.ndarray, pd.Series, list],
             volume: Union[np.ndarray, pd.Series, list],
             period: int = 0) -> np.ndarray:
        """
        Volume Weighted Average Price
        
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
        np.ndarray
            Array of VWAP values
        """
        return self._vwap.calculate(high, low, close, volume, period)
    
    def mfi(self, high: Union[np.ndarray, pd.Series, list],
            low: Union[np.ndarray, pd.Series, list],
            close: Union[np.ndarray, pd.Series, list],
            volume: Union[np.ndarray, pd.Series, list],
            period: int = 14) -> np.ndarray:
        """
        Money Flow Index
        
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
        np.ndarray
            Array of MFI values
        """
        return self._mfi.calculate(high, low, close, volume, period)
    
    def adl(self, high: Union[np.ndarray, pd.Series, list],
            low: Union[np.ndarray, pd.Series, list],
            close: Union[np.ndarray, pd.Series, list],
            volume: Union[np.ndarray, pd.Series, list]) -> np.ndarray:
        """Accumulation/Distribution Line"""
        return self._adl.calculate(high, low, close, volume)
    
    def cmf(self, high: Union[np.ndarray, pd.Series, list],
            low: Union[np.ndarray, pd.Series, list],
            close: Union[np.ndarray, pd.Series, list],
            volume: Union[np.ndarray, pd.Series, list],
            period: int = 20) -> np.ndarray:
        """Chaikin Money Flow"""
        return self._cmf.calculate(high, low, close, volume, period)
    
    def emv(self, high: Union[np.ndarray, pd.Series, list],
            low: Union[np.ndarray, pd.Series, list],
            volume: Union[np.ndarray, pd.Series, list],
            scale: float = 1000000) -> np.ndarray:
        """Ease of Movement"""
        return self._emv.calculate(high, low, volume, scale)
    
    def force_index(self, close: Union[np.ndarray, pd.Series, list],
                    volume: Union[np.ndarray, pd.Series, list]) -> np.ndarray:
        """Force Index"""
        return self._fi.calculate(close, volume)
    
    def nvi(self, close: Union[np.ndarray, pd.Series, list],
            volume: Union[np.ndarray, pd.Series, list]) -> np.ndarray:
        """Negative Volume Index"""
        return self._nvi.calculate(close, volume)
    
    def pvi(self, close: Union[np.ndarray, pd.Series, list],
            volume: Union[np.ndarray, pd.Series, list]) -> np.ndarray:
        """Positive Volume Index"""
        return self._pvi.calculate(close, volume)
    
    def volume_oscillator(self, volume: Union[np.ndarray, pd.Series, list],
                         fast_period: int = 5, slow_period: int = 10) -> np.ndarray:
        """Volume Oscillator"""
        return self._vo.calculate(volume, fast_period, slow_period)
    
    def vroc(self, volume: Union[np.ndarray, pd.Series, list], period: int = 25) -> np.ndarray:
        """Volume Rate of Change"""
        return self._vroc.calculate(volume, period)
    
    # =================== OSCILLATORS ===================
    
    def roc_oscillator(self, data: Union[np.ndarray, pd.Series, list], period: int = 12) -> np.ndarray:
        """Rate of Change"""
        return self._roc.calculate(data, period)
    
    def cmo(self, data: Union[np.ndarray, pd.Series, list], period: int = 14) -> np.ndarray:
        """Chande Momentum Oscillator"""
        return self._cmo.calculate(data, period)
    
    def trix(self, data: Union[np.ndarray, pd.Series, list], period: int = 14) -> np.ndarray:
        """TRIX"""
        return self._trix.calculate(data, period)
    
    def uo_oscillator(self, high: Union[np.ndarray, pd.Series, list],
                     low: Union[np.ndarray, pd.Series, list],
                     close: Union[np.ndarray, pd.Series, list],
                     period1: int = 7, period2: int = 14, period3: int = 28) -> np.ndarray:
        """Ultimate Oscillator"""
        return self._uo.calculate(high, low, close, period1, period2, period3)
    
    def awesome_oscillator(self, high: Union[np.ndarray, pd.Series, list],
                          low: Union[np.ndarray, pd.Series, list],
                          fast_period: int = 5, slow_period: int = 34) -> np.ndarray:
        """Awesome Oscillator"""
        return self._ao.calculate(high, low, fast_period, slow_period)
    
    def accelerator_oscillator(self, high: Union[np.ndarray, pd.Series, list],
                              low: Union[np.ndarray, pd.Series, list],
                              period: int = 5) -> np.ndarray:
        """Accelerator Oscillator"""
        return self._ac.calculate(high, low, period)
    
    def ppo(self, data: Union[np.ndarray, pd.Series, list],
            fast_period: int = 12, slow_period: int = 26,
            signal_period: int = 9) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Percentage Price Oscillator"""
        return self._ppo.calculate(data, fast_period, slow_period, signal_period)
    
    def price_oscillator(self, data: Union[np.ndarray, pd.Series, list],
                        fast_period: int = 10, slow_period: int = 20,
                        ma_type: str = "SMA") -> np.ndarray:
        """Price Oscillator"""
        return self._po.calculate(data, fast_period, slow_period, ma_type)
    
    def dpo(self, data: Union[np.ndarray, pd.Series, list], period: int = 20) -> np.ndarray:
        """Detrended Price Oscillator"""
        return self._dpo.calculate(data, period)
    
    def aroon_oscillator(self, high: Union[np.ndarray, pd.Series, list],
                        low: Union[np.ndarray, pd.Series, list],
                        period: int = 25) -> np.ndarray:
        """Aroon Oscillator"""
        return self._aroonosc.calculate(high, low, period)
    
    # =================== STATISTICAL INDICATORS ===================
    
    def linear_regression(self, data: Union[np.ndarray, pd.Series, list], period: int = 14) -> np.ndarray:
        """Linear Regression"""
        return self._linearreg.calculate(data, period)
    
    def linear_regression_slope(self, data: Union[np.ndarray, pd.Series, list], period: int = 14) -> np.ndarray:
        """Linear Regression Slope"""
        return self._linearreg_slope.calculate(data, period)
    
    def correlation(self, data1: Union[np.ndarray, pd.Series, list],
                   data2: Union[np.ndarray, pd.Series, list],
                   period: int = 20) -> np.ndarray:
        """Pearson Correlation Coefficient"""
        return self._correl.calculate(data1, data2, period)
    
    def beta(self, asset: Union[np.ndarray, pd.Series, list],
             market: Union[np.ndarray, pd.Series, list],
             period: int = 252) -> np.ndarray:
        """Beta Coefficient"""
        return self._beta.calculate(asset, market, period)
    
    def variance(self, data: Union[np.ndarray, pd.Series, list], period: int = 20) -> np.ndarray:
        """Variance"""
        return self._var.calculate(data, period)
    
    def time_series_forecast(self, data: Union[np.ndarray, pd.Series, list], period: int = 14) -> np.ndarray:
        """Time Series Forecast"""
        return self._tsf.calculate(data, period)
    
    def median(self, data: Union[np.ndarray, pd.Series, list], period: int = 20) -> np.ndarray:
        """Rolling Median"""
        return self._median.calculate(data, period)
    
    def mode(self, data: Union[np.ndarray, pd.Series, list], 
             period: int = 20, bins: int = 10) -> np.ndarray:
        """Rolling Mode"""
        return self._mode.calculate(data, period, bins)
    
    # =================== HYBRID INDICATORS ===================
    
    def adx_system(self, high: Union[np.ndarray, pd.Series, list],
                   low: Union[np.ndarray, pd.Series, list],
                   close: Union[np.ndarray, pd.Series, list],
                   period: int = 14) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Average Directional Index System (+DI, -DI, ADX)"""
        return self._adx.calculate(high, low, close, period)
    
    def aroon_system(self, high: Union[np.ndarray, pd.Series, list],
                     low: Union[np.ndarray, pd.Series, list],
                     period: int = 25) -> Tuple[np.ndarray, np.ndarray]:
        """Aroon Indicator (Up, Down)"""
        return self._aroon.calculate(high, low, period)
    
    def pivot_points(self, high: Union[np.ndarray, pd.Series, list],
                     low: Union[np.ndarray, pd.Series, list],
                     close: Union[np.ndarray, pd.Series, list]) -> Tuple[np.ndarray, ...]:
        """Pivot Points (Pivot, R1, S1, R2, S2, R3, S3)"""
        return self._pivot_points.calculate(high, low, close)
    
    def parabolic_sar(self, high: Union[np.ndarray, pd.Series, list],
                      low: Union[np.ndarray, pd.Series, list],
                      acceleration: float = 0.02, maximum: float = 0.2) -> Tuple[np.ndarray, np.ndarray]:
        """Parabolic SAR (values, trend)"""
        return self._sar.calculate(high, low, acceleration, maximum)
    
    def directional_movement(self, high: Union[np.ndarray, pd.Series, list],
                            low: Union[np.ndarray, pd.Series, list],
                            close: Union[np.ndarray, pd.Series, list],
                            period: int = 14) -> Tuple[np.ndarray, np.ndarray]:
        """Directional Movement Index (+DI, -DI)"""
        return self._dmi.calculate(high, low, close, period)
    
    def psar(self, high: Union[np.ndarray, pd.Series, list],
             low: Union[np.ndarray, pd.Series, list],
             acceleration: float = 0.02, maximum: float = 0.2) -> np.ndarray:
        """Parabolic SAR (values only)"""
        return self._psar.calculate(high, low, acceleration, maximum)
    
    def hilbert_trendline(self, data: Union[np.ndarray, pd.Series, list]) -> np.ndarray:
        """Hilbert Transform Trendline"""
        return self._ht_trendline.calculate(data)
    
    # =================== UTILITY FUNCTIONS ===================
    
    def crossover(self, series1: Union[np.ndarray, pd.Series, list], 
                  series2: Union[np.ndarray, pd.Series, list]) -> np.ndarray:
        """
        Check if series1 crosses over series2
        
        Parameters:
        -----------
        series1 : Union[np.ndarray, pd.Series, list]
            First series
        series2 : Union[np.ndarray, pd.Series, list]
            Second series
            
        Returns:
        --------
        np.ndarray
            Boolean array indicating crossover points
        """
        series1 = validate_input(series1)
        series2 = validate_input(series2)
        return crossover(series1, series2)
    
    def crossunder(self, series1: Union[np.ndarray, pd.Series, list], 
                   series2: Union[np.ndarray, pd.Series, list]) -> np.ndarray:
        """
        Check if series1 crosses under series2
        
        Parameters:
        -----------
        series1 : Union[np.ndarray, pd.Series, list]
            First series
        series2 : Union[np.ndarray, pd.Series, list]
            Second series
            
        Returns:
        --------
        np.ndarray
            Boolean array indicating crossunder points
        """
        series1 = validate_input(series1)
        series2 = validate_input(series2)
        return crossunder(series1, series2)
    
    def highest(self, data: Union[np.ndarray, pd.Series, list], period: int) -> np.ndarray:
        """
        Highest value over a period
        
        Parameters:
        -----------
        data : Union[np.ndarray, pd.Series, list]
            Input data
        period : int
            Window size
            
        Returns:
        --------
        np.ndarray
            Array of highest values
        """
        data = validate_input(data)
        return highest(data, period)
    
    def lowest(self, data: Union[np.ndarray, pd.Series, list], period: int) -> np.ndarray:
        """
        Lowest value over a period
        
        Parameters:
        -----------
        data : Union[np.ndarray, pd.Series, list]
            Input data
        period : int
            Window size
            
        Returns:
        --------
        np.ndarray
            Array of lowest values
        """
        data = validate_input(data)
        return lowest(data, period)
    
    def change(self, data: Union[np.ndarray, pd.Series, list], length: int = 1) -> np.ndarray:
        """
        Change in value over a specified number of periods
        
        Parameters:
        -----------
        data : Union[np.ndarray, pd.Series, list]
            Input data
        length : int, default=1
            Number of periods to look back
            
        Returns:
        --------
        np.ndarray
            Array of change values
        """
        data = validate_input(data)
        return change(data, length)
    
    def roc(self, data: Union[np.ndarray, pd.Series, list], length: int) -> np.ndarray:
        """
        Rate of Change (ROC)
        
        Parameters:
        -----------
        data : Union[np.ndarray, pd.Series, list]
            Input data
        length : int
            Number of periods to look back
            
        Returns:
        --------
        np.ndarray
            Array of ROC values as percentages
        """
        data = validate_input(data)
        return roc(data, length)
    
    def stdev(self, data: Union[np.ndarray, pd.Series, list], period: int) -> np.ndarray:
        """
        Rolling standard deviation
        
        Parameters:
        -----------
        data : Union[np.ndarray, pd.Series, list]
            Input data
        period : int
            Window size for standard deviation calculation
            
        Returns:
        --------
        np.ndarray
            Array of standard deviation values
        """
        data = validate_input(data)
        return stdev(data, period)


# Create global instance for easy access
ta = TechnicalAnalysis()

# Make indicator classes available for advanced users
__all__ = [
    'ta', 'TechnicalAnalysis',
    # Trend indicators
    'SMA', 'EMA', 'WMA', 'DEMA', 'TEMA', 'HMA', 'VWMA', 'ALMA', 'KAMA', 'ZLEMA', 'T3', 'FRAMA',
    'Supertrend', 'Ichimoku',
    # Momentum indicators  
    'RSI', 'MACD', 'Stochastic', 'CCI', 'WilliamsR',
    # Volatility indicators
    'ATR', 'BollingerBands', 'KeltnerChannel', 'DonchianChannel', 'ChaikinVolatility', 'NATR', 
    'RVI', 'ULTOSC', 'STDDEV', 'TRANGE', 'MASS',
    # Volume indicators
    'OBV', 'VWAP', 'MFI', 'ADL', 'CMF', 'EMV', 'FI', 'NVI', 'PVI', 'VO', 'VROC',
    # Oscillators
    'ROC', 'CMO', 'TRIX', 'UO', 'AO', 'AC', 'PPO', 'PO', 'DPO', 'AROONOSC',
    # Statistical indicators
    'LINEARREG', 'LINEARREG_SLOPE', 'CORREL', 'BETA', 'VAR', 'TSF', 'MEDIAN', 'MODE',
    # Hybrid indicators
    'ADX', 'Aroon', 'PivotPoints', 'SAR', 'DMI', 'PSAR', 'HT_TRENDLINE',
    # Utility functions
    'crossover', 'crossunder', 'highest', 'lowest', 'change', 'roc', 'stdev'
]