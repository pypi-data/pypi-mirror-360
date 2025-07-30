import pandas as pd

def ema_channel(
    close: pd.Series,
    ema_period: int = 20,
    atr_period: int = 14,
    atr_multipliers: list[float] = [1, 2, 3],
    use_atr: bool = True,
    coeff: float = 0.0
) -> pd.DataFrame:
    """
    EMA Channel with optional ATR bands or coefficient bands.

    Parameters:
        close (pd.Series): Closing prices.
        ema_period (int): Period for the EMA.
        atr_period (int): Period for ATR if using ATR bands.
        atr_multipliers (list[float]): ATR multipliers for bands.
        use_atr (bool): Use ATR bands if True, else use coefficient.
        coeff (float): Coefficient for EMA-based bands if not using ATR.

    Returns:
        pd.DataFrame: EMA, upper & lower bands.

    Example:
    
        # ATR bands:
        channel = ema_channel(df['Close'], ema_period=20, atr_period=14, atr_multipliers=[1,2,3])

        # Coefficient bands:
        channel = ema_channel(df['Close'], ema_period=20, use_atr=False, coeff=0.05)

        # Plain EMA:
        channel = ema_channel(df['Close'], use_atr=False)

    """
    ema = close.ewm(span=ema_period, adjust=False).mean()
    bands = {}

    if use_atr:
        # Compute ATR
        high = close  # Use close for demo; replace with real High if you have it
        low = close   # Same
        prev_close = close.shift(1)

        tr1 = high - low
        tr2 = (high - prev_close).abs()
        tr3 = (low - prev_close).abs()
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=atr_period).mean()

        for mult in atr_multipliers:
            bands[f'upper_{mult}atr'] = ema + mult * atr
            bands[f'lower_{mult}atr'] = ema - mult * atr

    elif coeff > 0:
        offset = ema * coeff
        bands['upper'] = ema + offset
        bands['lower'] = ema - offset

    return pd.DataFrame({'ema': ema, **bands})
