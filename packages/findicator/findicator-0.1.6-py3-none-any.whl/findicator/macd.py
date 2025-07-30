import pandas as pd

def macd(
    close: pd.Series,
    fast_period: int = 12,
    slow_period: int = 26,
    signal_period: int = 9
) -> tuple[pd.Series, pd.Series, pd.Series]:
    """
    Moving Average Convergence Divergence (MACD) indicator with histogram.
    
    Parameters:
        close (pd.Series): Closing prices.
        fast_period (int): Period for fast EMA (default: 12).
        slow_period (int): Period for slow EMA (default: 26).
        signal_period (int): Period for signal line EMA (default: 9).
    
    Returns:
        tuple: (macd_line, signal_line, histogram)
    """
    fast_ema = close.ewm(span=fast_period, adjust=False).mean()
    slow_ema = close.ewm(span=slow_period, adjust=False).mean()
    macd_line = fast_ema - slow_ema
    signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()
    histogram = macd_line - signal_line

    return macd_line, signal_line, histogram
