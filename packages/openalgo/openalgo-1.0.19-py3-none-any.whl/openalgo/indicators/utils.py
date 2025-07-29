# -*- coding: utf-8 -*-
"""
OpenAlgo Technical Indicators - Utility Functions
"""

import numpy as np
import pandas as pd
from numba import njit, prange
from typing import Union, Optional


# ------------------------------------------------------------------
# Core helper – ensure every indicator receives a contiguous float64
# ------------------------------------------------------------------

def validate_input(arr: Union[np.ndarray, pd.Series, list]) -> np.ndarray:
    """Return C-contiguous float64 numpy array (zero-copy when possible)."""
    arr = np.asarray(arr, dtype=np.float64)
    if not arr.flags['C_CONTIGUOUS']:
        arr = np.ascontiguousarray(arr)
    return arr


@njit(fastmath=True, cache=True)
def crossover(series1: np.ndarray, series2: np.ndarray) -> np.ndarray:
    """
    Check if series1 crosses over series2
    
    Parameters:
    -----------
    series1 : np.ndarray
        First series
    series2 : np.ndarray
        Second series
        
    Returns:
    --------
    np.ndarray
        Boolean array indicating crossover points
    """
    n = len(series1)
    result = np.zeros(n, dtype=np.bool_)
    
    for i in range(1, n):
        if (series1[i] > series2[i] and 
            series1[i-1] <= series2[i-1] and 
            not np.isnan(series1[i]) and not np.isnan(series2[i]) and
            not np.isnan(series1[i-1]) and not np.isnan(series2[i-1])):
            result[i] = True
    
    return result


@njit(fastmath=True, cache=True)
def crossunder(series1: np.ndarray, series2: np.ndarray) -> np.ndarray:
    """
    Check if series1 crosses under series2
    
    Parameters:
    -----------
    series1 : np.ndarray
        First series
    series2 : np.ndarray
        Second series
        
    Returns:
    --------
    np.ndarray
        Boolean array indicating crossunder points
    """
    n = len(series1)
    result = np.zeros(n, dtype=np.bool_)
    
    for i in range(1, n):
        if (series1[i] < series2[i] and 
            series1[i-1] >= series2[i-1] and 
            not np.isnan(series1[i]) and not np.isnan(series2[i]) and
            not np.isnan(series1[i-1]) and not np.isnan(series2[i-1])):
            result[i] = True
    
    return result


@njit(fastmath=True, cache=True, parallel=True)
def highest(data: np.ndarray, period: int) -> np.ndarray:
    """
    Calculate the highest value over a rolling window
    
    Parameters:
    -----------
    data : np.ndarray
        Input data
    period : int
        Window size
        
    Returns:
    --------
    np.ndarray
        Array of highest values
    """
    n = len(data)
    result = np.full(n, np.nan)
    
    for i in prange(period - 1, n):
        result[i] = data[i - period + 1:i + 1].max()
    
    return result


@njit(fastmath=True, cache=True, parallel=True)
def lowest(data: np.ndarray, period: int) -> np.ndarray:
    """
    Calculate the lowest value over a rolling window
    
    Parameters:
    -----------
    data : np.ndarray
        Input data
    period : int
        Window size
        
    Returns:
    --------
    np.ndarray
        Array of lowest values
    """
    n = len(data)
    result = np.full(n, np.nan)
    
    for i in prange(period - 1, n):
        result[i] = data[i - period + 1:i + 1].min()
    
    return result


@njit(fastmath=True, cache=True)
def change(data: np.ndarray, length: int = 1) -> np.ndarray:
    """
    Calculate the change in value over a specified number of periods
    
    Parameters:
    -----------
    data : np.ndarray
        Input data
    length : int, default=1
        Number of periods to look back
        
    Returns:
    --------
    np.ndarray
        Array of change values
    """
    n = len(data)
    result = np.full(n, np.nan)
    
    for i in range(length, n):
        result[i] = data[i] - data[i - length]
    
    return result


@njit(fastmath=True, cache=True)
def roc(data: np.ndarray, length: int) -> np.ndarray:
    """
    Calculate Rate of Change (ROC)
    
    Parameters:
    -----------
    data : np.ndarray
        Input data
    length : int
        Number of periods to look back
        
    Returns:
    --------
    np.ndarray
        Array of ROC values as percentages
    """
    n = len(data)
    result = np.full(n, np.nan)
    
    for i in range(length, n):
        if data[i - length] != 0:
            result[i] = ((data[i] - data[i - length]) / data[i - length]) * 100
    
    return result


@njit(fastmath=True, cache=True)
def sma(data: np.ndarray, period: int) -> np.ndarray:
    """
    Simple Moving Average utility function
    
    Parameters:
    -----------
    data : np.ndarray
        Input data
    period : int
        Moving average period
        
    Returns:
    --------
    np.ndarray
        Array of SMA values
    """
    n = len(data)
    result = np.full(n, np.nan)
    
    for i in range(period - 1, n):
        result[i] = np.mean(data[i - period + 1:i + 1])
    
    return result


@njit(fastmath=True, cache=True)
def ema(data: np.ndarray, period: int) -> np.ndarray:
    """
    Exponential Moving Average utility function
    
    Parameters:
    -----------
    data : np.ndarray
        Input data
    period : int
        EMA period
        
    Returns:
    --------
    np.ndarray
        Array of EMA values
    """
    n = len(data)
    result = np.empty(n)
    alpha = 2.0 / (period + 1)

    # Seed initial values with NaN until enough data is available
    result[:period-1] = np.nan

    # Calculate initial SMA as the first EMA value
    sum_val = 0.0
    for i in range(period):
        sum_val += data[i]
    result[period-1] = sum_val / period

    # Calculate EMA for remaining values
    for i in range(period, n):
        result[i] = alpha * data[i] + (1 - alpha) * result[i-1]

    return result


@njit(fastmath=True, cache=True)
def stdev(data: np.ndarray, period: int) -> np.ndarray:
    """
    Calculate rolling standard deviation
    
    Parameters:
    -----------
    data : np.ndarray
        Input data
    period : int
        Window size for standard deviation calculation
        
    Returns:
    --------
    np.ndarray
        Array of standard deviation values
    """
    n = len(data)
    result = np.full(n, np.nan)
    
    for i in range(period - 1, n):
        window_data = data[i - period + 1:i + 1]
        mean_val = np.mean(window_data)
        
        variance = 0.0
        for j in range(period):
            diff = window_data[j] - mean_val
            variance += diff * diff
        
        result[i] = np.sqrt(variance / period)
    
    return result


def true_range(high: np.ndarray, low: np.ndarray, close: np.ndarray) -> np.ndarray:
    """
    Calculate True Range
    
    Parameters:
    -----------
    high : np.ndarray
        High prices
    low : np.ndarray
        Low prices
    close : np.ndarray
        Closing prices
        
    Returns:
    --------
    np.ndarray
        Array of True Range values
    """
    n = len(high)
    tr = np.empty(n)
    
    # First TR value
    tr[0] = high[0] - low[0]
    
    # Calculate True Range
    for i in range(1, n):
        hl = high[i] - low[i]
        hc = abs(high[i] - close[i-1])
        lc = abs(low[i] - close[i-1])
        tr[i] = max(hl, hc, lc)
    
    return tr