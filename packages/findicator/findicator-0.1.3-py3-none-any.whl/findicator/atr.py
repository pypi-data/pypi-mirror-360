import pandas as pd
from typing import Tuple


def atr(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    period: int = 14
) -> pd.Series:
    """
    Average True Range (ATR)

    Parameters:
        high (pd.Series): High prices
        low (pd.Series): Low prices
        close (pd.Series): Close prices
        period (int): Period for ATR calculation (default: 14)

    Returns:
        pd.Series: ATR values
    """
    prev_close = close.shift(1)

    tr1 = high - low
    tr2 = (high - prev_close).abs()
    tr3 = (low - prev_close).abs()

    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    atr = tr.rolling(window=period).mean()

    return atr

