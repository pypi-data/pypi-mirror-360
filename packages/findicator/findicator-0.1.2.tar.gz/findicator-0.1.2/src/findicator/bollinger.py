import pandas as pd
from typing import Tuple


def bollinger_bands(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    period: int = 20,
    stddev_multiplier: float = 2.0
) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """
    Calculate Bollinger Bands (BB) based on typical price.

    Parameters:
        high (pd.Series): High prices
        low (pd.Series): Low prices
        close (pd.Series): Close prices
        period (int): Rolling window period (default: 20)
        stddev_multiplier (float): Std dev multiplier (default: 2.0)

    Returns:
        Tuple[pd.Series, pd.Series, pd.Series]:
            (middle_band, upper_band, lower_band)
    """
    typical_price = (high + low + close) / 3
    middle_band = typical_price.rolling(window=period).mean()
    stddev = typical_price.rolling(window=period).std()
    upper_band = middle_band + stddev_multiplier * stddev
    lower_band = middle_band - stddev_multiplier * stddev
    return middle_band, upper_band, lower_band

