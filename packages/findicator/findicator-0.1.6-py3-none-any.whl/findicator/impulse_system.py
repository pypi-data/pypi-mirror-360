import pandas as pd

def impulse_system(
    close: pd.Series,
    ema_period: int = 13,
    macd_fast: int = 12,
    macd_slow: int = 26,
    macd_signal: int = 9
) -> pd.Series:
    """
    Elder's Impulse System

    Combines EMA slope and MACD Histogram.

    Returns:
        pd.Series: +1 (bullish), -1 (bearish), 0 (neutral)
    """
    # Trend: EMA slope
    ema = close.ewm(span=ema_period, adjust=False).mean()
    ema_slope = ema.diff()

    # Momentum: MACD Histogram
    fast_ema = close.ewm(span=macd_fast, adjust=False).mean()
    slow_ema = close.ewm(span=macd_slow, adjust=False).mean()
    macd_line = fast_ema - slow_ema
    signal_line = macd_line.ewm(span=macd_signal, adjust=False).mean()
    histogram = macd_line - signal_line

    # Histogram slope
    hist_slope = histogram.diff()

    # Combine
    impulse = (
        (ema_slope > 0) & (hist_slope > 0)
    ).astype(int) - (
        (ema_slope < 0) & (hist_slope < 0)
    ).astype(int)

    return impulse
