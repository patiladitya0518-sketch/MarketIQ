import pandas as pd


def detect_doji(df: pd.DataFrame):
    if len(df) < 1:
        return None

    candle = df.iloc[-1]

    body = abs(candle["Close"] - candle["Open"])
    total = candle["High"] - candle["Low"]

    if total == 0:
        return None

    if body / total < 0.1:
        return {
            "pattern": "Doji",
            "signal": "HOLD",
            "strength": 75,
        }

    return None


def detect_spinning_top(df: pd.DataFrame):
    if len(df) < 1:
        return None

    candle = df.iloc[-1]

    body = abs(candle["Close"] - candle["Open"])
    upper = candle["High"] - max(candle["Open"], candle["Close"])
    lower = min(candle["Open"], candle["Close"]) - candle["Low"]

    if (
        upper > body
        and lower > body
    ):
        return {
            "pattern": "Spinning Top",
            "signal": "HOLD",
            "strength": 70,
        }

    return None


def detect_dragonfly_doji(df: pd.DataFrame):
    if len(df) < 1:
        return None

    candle = df.iloc[-1]

    body = abs(candle["Close"] - candle["Open"])
    upper = candle["High"] - max(candle["Open"], candle["Close"])
    lower = min(candle["Open"], candle["Close"]) - candle["Low"]

    if (
        body < 1
        and upper < 1
        and lower > body * 3
    ):
        return {
            "pattern": "Dragonfly Doji",
            "signal": "HOLD",
            "strength": 80,
        }

    return None


def detect_gravestone_doji(df: pd.DataFrame):
    if len(df) < 1:
        return None

    candle = df.iloc[-1]

    body = abs(candle["Close"] - candle["Open"])
    upper = candle["High"] - max(candle["Open"], candle["Close"])
    lower = min(candle["Open"], candle["Close"]) - candle["Low"]

    if (
        body < 1
        and upper > body * 3
        and lower < 1
    ):
        return {
            "pattern": "Gravestone Doji",
            "signal": "HOLD",
            "strength": 80,
        }

    return None


def detect_marubozu(df: pd.DataFrame):
    if len(df) < 1:
        return None

    candle = df.iloc[-1]

    body = abs(candle["Close"] - candle["Open"])
    upper = candle["High"] - max(candle["Open"], candle["Close"])
    lower = min(candle["Open"], candle["Close"]) - candle["Low"]

    if (
        upper < body * 0.1
        and lower < body * 0.1
    ):
        signal = "BUY" if candle["Close"] > candle["Open"] else "SELL"

        return {
            "pattern": "Marubozu",
            "signal": signal,
            "strength": 90,
        }

    return None