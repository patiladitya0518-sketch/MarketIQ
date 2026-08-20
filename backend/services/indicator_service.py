import ta


def calculate_indicators(df):
    """
    Calculate common technical indicators.

    Includes:
    - RSI
    - EMA20
    - EMA50
    - MACD
    - MACD Signal
    - MACD Histogram
    - MACD crossover status
    """

    # ============================================================
    # RSI
    # ============================================================

    df["RSI"] = ta.momentum.RSIIndicator(
        df["Close"]
    ).rsi()

    # ============================================================
    # EMA20
    # ============================================================

    df["EMA20"] = ta.trend.EMAIndicator(
        df["Close"],
        window=20,
    ).ema_indicator()

    # ============================================================
    # EMA50
    # ============================================================

    df["EMA50"] = ta.trend.EMAIndicator(
        df["Close"],
        window=50,
    ).ema_indicator()

    # ============================================================
    # MACD
    # ============================================================

    macd = ta.trend.MACD(
        df["Close"]
    )

    df["MACD"] = macd.macd()

    df["MACD_SIGNAL"] = macd.macd_signal()

    df["MACD_HISTOGRAM"] = (
        df["MACD"] - df["MACD_SIGNAL"]
    )

    # ============================================================
    # MACD CROSSOVER
    # ============================================================

    previous_macd = df["MACD"].shift(1)
    previous_signal = df["MACD_SIGNAL"].shift(1)

    current_macd = df["MACD"]
    current_signal = df["MACD_SIGNAL"]

    # Bullish crossover:
    # Previous MACD was below/equal signal
    # Current MACD is above signal

    df["MACD_BULLISH_CROSSOVER"] = (
        (previous_macd <= previous_signal)
        & (current_macd > current_signal)
    )

    # Bearish crossover:
    # Previous MACD was above/equal signal
    # Current MACD is below signal

    df["MACD_BEARISH_CROSSOVER"] = (
        (previous_macd >= previous_signal)
        & (current_macd < current_signal)
    )

    # ============================================================
    # MACD STATUS
    # ============================================================

    df["MACD_STATUS"] = "NEUTRAL"

    df.loc[
        current_macd > current_signal,
        "MACD_STATUS",
    ] = "BULLISH"

    df.loc[
        current_macd < current_signal,
        "MACD_STATUS",
    ] = "BEARISH"

    return df