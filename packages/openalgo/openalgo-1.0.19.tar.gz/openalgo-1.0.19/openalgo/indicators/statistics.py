# -*- coding: utf-8 -*-
"""
OpenAlgo Technical Indicators - Statistical Indicators
"""

import numpy as np
import pandas as pd
from numba import jit
from typing import Union, Tuple, Optional
from .base import BaseIndicator


class LINEARREG(BaseIndicator):
    """
    Linear Regression
    
    Linear Regression calculates the linear regression line for the given period.
    
    Formula: y = mx + b (least squares method)
    """
    
    def __init__(self):
        super().__init__("Linear Regression")
    
    @staticmethod
    @jit(nopython=True)
    def _calculate_linearreg(data: np.ndarray, period: int) -> np.ndarray:
        """Numba optimized Linear Regression calculation"""
        n = len(data)
        result = np.full(n, np.nan)
        
        for i in range(period - 1, n):
            # Extract window
            y = data[i - period + 1:i + 1]
            x = np.arange(period)
            
            # Calculate linear regression
            sum_x = np.sum(x)
            sum_y = np.sum(y)
            sum_xy = np.sum(x * y)
            sum_x2 = np.sum(x * x)
            
            # Calculate slope and intercept
            denominator = period * sum_x2 - sum_x * sum_x
            if denominator != 0:
                slope = (period * sum_xy - sum_x * sum_y) / denominator
                intercept = (sum_y - slope * sum_x) / period
                
                # Calculate value at the end of the period
                result[i] = slope * (period - 1) + intercept
            else:
                result[i] = y[-1]  # Fallback to last value
        
        return result
    
    def calculate(self, data: Union[np.ndarray, pd.Series, list], period: int = 14) -> Union[np.ndarray, pd.Series]:
        """
        Calculate Linear Regression
        
        Parameters:
        -----------
        data : Union[np.ndarray, pd.Series, list]
            Price data (typically closing prices)
        period : int, default=14
            Period for linear regression calculation
            
        Returns:
        --------
        Union[np.ndarray, pd.Series]
            Linear Regression values in the same format as input
        """
        validated_data, input_type, index = self.validate_input(data)
        self.validate_period(period, len(validated_data))
        
        result = self._calculate_linearreg(validated_data, period)
        return self.format_output(result, input_type, index)


class LINEARREG_SLOPE(BaseIndicator):
    """
    Linear Regression Slope
    
    Calculates the slope of the linear regression line.
    """
    
    def __init__(self):
        super().__init__("Linear Regression Slope")
    
    @staticmethod
    @jit(nopython=True)
    def _calculate_slope(data: np.ndarray, period: int) -> np.ndarray:
        """Numba optimized slope calculation"""
        n = len(data)
        result = np.full(n, np.nan)
        
        for i in range(period - 1, n):
            y = data[i - period + 1:i + 1]
            x = np.arange(period)
            
            sum_x = np.sum(x)
            sum_y = np.sum(y)
            sum_xy = np.sum(x * y)
            sum_x2 = np.sum(x * x)
            
            denominator = period * sum_x2 - sum_x * sum_x
            if denominator != 0:
                result[i] = (period * sum_xy - sum_x * sum_y) / denominator
            else:
                result[i] = 0
        
        return result
    
    def calculate(self, data: Union[np.ndarray, pd.Series, list], period: int = 14) -> Union[np.ndarray, pd.Series]:
        """
        Calculate Linear Regression Slope
        
        Parameters:
        -----------
        data : Union[np.ndarray, pd.Series, list]
            Price data (typically closing prices)
        period : int, default=14
            Period for slope calculation
            
        Returns:
        --------
        Union[np.ndarray, pd.Series]
            Slope values in the same format as input
        """
        validated_data, input_type, index = self.validate_input(data)
        self.validate_period(period, len(validated_data))
        
        result = self._calculate_slope(validated_data, period)
        return self.format_output(result, input_type, index)


class CORREL(BaseIndicator):
    """
    Pearson Correlation Coefficient
    
    Measures the correlation between two data series.
    
    Formula: r = Σ((x - x̄)(y - ȳ)) / √(Σ(x - x̄)² × Σ(y - ȳ)²)
    """
    
    def __init__(self):
        super().__init__("Correlation")
    
    @staticmethod
    @jit(nopython=True)
    def _calculate_correl(data1: np.ndarray, data2: np.ndarray, period: int) -> np.ndarray:
        """Numba optimized correlation calculation"""
        n = len(data1)
        result = np.full(n, np.nan)
        
        for i in range(period - 1, n):
            x = data1[i - period + 1:i + 1]
            y = data2[i - period + 1:i + 1]
            
            # Calculate means
            mean_x = np.mean(x)
            mean_y = np.mean(y)
            
            # Calculate correlation coefficient
            numerator = np.sum((x - mean_x) * (y - mean_y))
            sum_sq_x = np.sum((x - mean_x) ** 2)
            sum_sq_y = np.sum((y - mean_y) ** 2)
            
            denominator = np.sqrt(sum_sq_x * sum_sq_y)
            
            if denominator > 0:
                result[i] = numerator / denominator
            else:
                result[i] = 0
        
        return result
    
    def calculate(self, data1: Union[np.ndarray, pd.Series, list],
                 data2: Union[np.ndarray, pd.Series, list],
                 period: int = 20) -> Union[np.ndarray, pd.Series]:
        """
        Calculate Pearson Correlation Coefficient
        
        Parameters:
        -----------
        data1 : Union[np.ndarray, pd.Series, list]
            First data series
        data2 : Union[np.ndarray, pd.Series, list]
            Second data series
        period : int, default=20
            Period for correlation calculation
            
        Returns:
        --------
        Union[np.ndarray, pd.Series]
            Correlation values in the same format as input
        """
        data1_validated, input_type, index = self.validate_input(data1)
        data2_validated, _, _ = self.validate_input(data2)
        
        data1_validated, data2_validated = self.align_arrays(data1_validated, data2_validated)
        self.validate_period(period, len(data1_validated))
        
        result = self._calculate_correl(data1_validated, data2_validated, period)
        return self.format_output(result, input_type, index)


class BETA(BaseIndicator):
    """
    Beta Coefficient
    
    Measures the volatility of a security relative to the market.
    
    Formula: β = Cov(asset, market) / Var(market)
    """
    
    def __init__(self):
        super().__init__("Beta")
    
    @staticmethod
    @jit(nopython=True)
    def _calculate_beta(asset: np.ndarray, market: np.ndarray, period: int) -> np.ndarray:
        """Numba optimized Beta calculation"""
        n = len(asset)
        result = np.full(n, np.nan)
        
        for i in range(period, n):
            # Calculate returns
            asset_returns = np.diff(asset[i - period:i + 1])
            market_returns = np.diff(market[i - period:i + 1])
            
            # Calculate means
            mean_asset = np.mean(asset_returns)
            mean_market = np.mean(market_returns)
            
            # Calculate covariance and variance
            covariance = np.mean((asset_returns - mean_asset) * (market_returns - mean_market))
            market_variance = np.mean((market_returns - mean_market) ** 2)
            
            if market_variance > 0:
                result[i] = covariance / market_variance
            else:
                result[i] = 0
        
        return result
    
    def calculate(self, asset: Union[np.ndarray, pd.Series, list],
                 market: Union[np.ndarray, pd.Series, list],
                 period: int = 252) -> Union[np.ndarray, pd.Series]:
        """
        Calculate Beta Coefficient
        
        Parameters:
        -----------
        asset : Union[np.ndarray, pd.Series, list]
            Asset price data
        market : Union[np.ndarray, pd.Series, list]
            Market price data
        period : int, default=252
            Period for beta calculation (typically 1 year = 252 trading days)
            
        Returns:
        --------
        Union[np.ndarray, pd.Series]
            Beta values in the same format as input
        """
        asset_data, input_type, index = self.validate_input(asset)
        market_data, _, _ = self.validate_input(market)
        
        asset_data, market_data = self.align_arrays(asset_data, market_data)
        self.validate_period(period + 1, len(asset_data))  # +1 for diff
        
        result = self._calculate_beta(asset_data, market_data, period)
        return self.format_output(result, input_type, index)


class VAR(BaseIndicator):
    """
    Variance
    
    Measures the dispersion of a dataset.
    
    Formula: Var = Σ(x - μ)² / n
    """
    
    def __init__(self):
        super().__init__("Variance")
    
    @staticmethod
    @jit(nopython=True)
    def _calculate_var(data: np.ndarray, period: int) -> np.ndarray:
        """Numba optimized variance calculation"""
        n = len(data)
        result = np.full(n, np.nan)
        
        for i in range(period - 1, n):
            window = data[i - period + 1:i + 1]
            mean_val = np.mean(window)
            
            variance = np.mean((window - mean_val) ** 2)
            result[i] = variance
        
        return result
    
    def calculate(self, data: Union[np.ndarray, pd.Series, list], period: int = 20) -> Union[np.ndarray, pd.Series]:
        """
        Calculate Variance
        
        Parameters:
        -----------
        data : Union[np.ndarray, pd.Series, list]
            Price data
        period : int, default=20
            Period for variance calculation
            
        Returns:
        --------
        Union[np.ndarray, pd.Series]
            Variance values in the same format as input
        """
        validated_data, input_type, index = self.validate_input(data)
        self.validate_period(period, len(validated_data))
        
        result = self._calculate_var(validated_data, period)
        return self.format_output(result, input_type, index)


class TSF(BaseIndicator):
    """
    Time Series Forecast
    
    Forecasts the next value using linear regression.
    """
    
    def __init__(self):
        super().__init__("Time Series Forecast")
    
    @staticmethod
    @jit(nopython=True)
    def _calculate_tsf(data: np.ndarray, period: int) -> np.ndarray:
        """Numba optimized TSF calculation"""
        n = len(data)
        result = np.full(n, np.nan)
        
        for i in range(period - 1, n):
            y = data[i - period + 1:i + 1]
            x = np.arange(period)
            
            sum_x = np.sum(x)
            sum_y = np.sum(y)
            sum_xy = np.sum(x * y)
            sum_x2 = np.sum(x * x)
            
            denominator = period * sum_x2 - sum_x * sum_x
            if denominator != 0:
                slope = (period * sum_xy - sum_x * sum_y) / denominator
                intercept = (sum_y - slope * sum_x) / period
                
                # Forecast next value
                result[i] = slope * period + intercept
            else:
                result[i] = y[-1]
        
        return result
    
    def calculate(self, data: Union[np.ndarray, pd.Series, list], period: int = 14) -> Union[np.ndarray, pd.Series]:
        """
        Calculate Time Series Forecast
        
        Parameters:
        -----------
        data : Union[np.ndarray, pd.Series, list]
            Price data
        period : int, default=14
            Period for forecast calculation
            
        Returns:
        --------
        Union[np.ndarray, pd.Series]
            Time Series Forecast values in the same format as input
        """
        validated_data, input_type, index = self.validate_input(data)
        self.validate_period(period, len(validated_data))
        
        result = self._calculate_tsf(validated_data, period)
        return self.format_output(result, input_type, index)


class MEDIAN(BaseIndicator):
    """
    Rolling Median
    
    Calculates the median value over a rolling window.
    """
    
    def __init__(self):
        super().__init__("Median")
    
    @staticmethod
    @jit(nopython=True)
    def _calculate_median(data: np.ndarray, period: int) -> np.ndarray:
        """Numba optimized median calculation"""
        n = len(data)
        result = np.full(n, np.nan)
        
        for i in range(period - 1, n):
            window = data[i - period + 1:i + 1].copy()
            
            # Simple bubble sort for median (works well for small periods)
            for j in range(period):
                for k in range(period - 1 - j):
                    if window[k] > window[k + 1]:
                        window[k], window[k + 1] = window[k + 1], window[k]
            
            # Get median
            if period % 2 == 1:
                result[i] = window[period // 2]
            else:
                result[i] = (window[period // 2 - 1] + window[period // 2]) / 2
        
        return result
    
    def calculate(self, data: Union[np.ndarray, pd.Series, list], period: int = 20) -> Union[np.ndarray, pd.Series]:
        """
        Calculate Rolling Median
        
        Parameters:
        -----------
        data : Union[np.ndarray, pd.Series, list]
            Price data
        period : int, default=20
            Period for median calculation
            
        Returns:
        --------
        Union[np.ndarray, pd.Series]
            Median values in the same format as input
        """
        validated_data, input_type, index = self.validate_input(data)
        self.validate_period(period, len(validated_data))
        
        result = self._calculate_median(validated_data, period)
        return self.format_output(result, input_type, index)


class MODE(BaseIndicator):
    """
    Rolling Mode
    
    Calculates the most frequent value over a rolling window.
    """
    
    def __init__(self):
        super().__init__("Mode")
    
    def calculate(self, data: Union[np.ndarray, pd.Series, list], 
                 period: int = 20, bins: int = 10) -> Union[np.ndarray, pd.Series]:
        """
        Calculate Rolling Mode
        
        Parameters:
        -----------
        data : Union[np.ndarray, pd.Series, list]
            Price data
        period : int, default=20
            Period for mode calculation
        bins : int, default=10
            Number of bins for discretization
            
        Returns:
        --------
        Union[np.ndarray, pd.Series]
            Mode values in the same format as input
        """
        validated_data, input_type, index = self.validate_input(data)
        self.validate_period(period, len(validated_data))
        
        n = len(validated_data)
        result = np.full(n, np.nan)
        
        for i in range(period - 1, n):
            window = validated_data[i - period + 1:i + 1]
            
            # Discretize the data into bins
            min_val = np.min(window)
            max_val = np.max(window)
            
            if max_val > min_val:
                bin_width = (max_val - min_val) / bins
                bin_indices = ((window - min_val) / bin_width).astype(int)
                bin_indices = np.clip(bin_indices, 0, bins - 1)
                
                # Count frequencies
                counts = np.zeros(bins)
                for idx in bin_indices:
                    counts[idx] += 1
                
                # Find mode bin
                mode_bin = np.argmax(counts)
                result[i] = min_val + (mode_bin + 0.5) * bin_width
            else:
                result[i] = window[0]
        
        return self.format_output(result, input_type, index)