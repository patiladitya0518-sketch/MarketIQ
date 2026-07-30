import ta


def calculate_indicators(df):
    """
    Calculate common technical indicators.
    """

    df["RSI"] = ta.momentum.RSIIndicator(df["Close"]).rsi()

    df["EMA20"] = ta.trend.EMAIndicator(
        df["Close"], window=20
    ).ema_indicator()

    df["EMA50"] = ta.trend.EMAIndicator(
        df["Close"], window=50
    ).ema_indicator()

    macd = ta.trend.MACD(df["Close"])

    df["MACD"] = macd.macd()
    df["MACD_SIGNAL"] = macd.macd_signal()

    return df