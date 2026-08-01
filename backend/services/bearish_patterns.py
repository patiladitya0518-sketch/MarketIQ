import pandas as pd


def detect_bearish_engulfing(df: pd.DataFrame):
    if len(df) < 2:
        return None

    prev = df.iloc[-2]
    curr = df.iloc[-1]

    if (
        prev["Close"] > prev["Open"]
        and curr["Close"] < curr["Open"]
        and curr["Open"] > prev["Close"]
        and curr["Close"] < prev["Open"]
    ):
        return {
            "pattern": "Bearish Engulfing",
            "signal": "SELL",
            "strength": 95,
        }

    return None


def detect_shooting_star(df: pd.DataFrame):
    if len(df) < 1:
        return None

    candle = df.iloc[-1]

    body = abs(candle["Close"] - candle["Open"])
    upper_shadow = candle["High"] - max(candle["Open"], candle["Close"])
    lower_shadow = min(candle["Open"], candle["Close"]) - candle["Low"]

    if (
        upper_shadow > body * 2
        and lower_shadow < body
    ):
        return {
            "pattern": "Shooting Star",
            "signal": "SELL",
            "strength": 88,
        }

    return None


def detect_evening_star(df: pd.DataFrame):
    if len(df) < 3:
        return None

    a = df.iloc[-3]
    b = df.iloc[-2]
    c = df.iloc[-1]

    if (
        a["Close"] > a["Open"]
        and abs(b["Close"] - b["Open"]) < abs(a["Close"] - a["Open"]) * 0.4
        and c["Close"] < c["Open"]
    ):
        return {
            "pattern": "Evening Star",
            "signal": "SELL",
            "strength": 92,
        }

    return None


def detect_dark_cloud_cover(df: pd.DataFrame):
    if len(df) < 2:
        return None

    prev = df.iloc[-2]
    curr = df.iloc[-1]

    midpoint = (prev["Open"] + prev["Close"]) / 2

    if (
        prev["Close"] > prev["Open"]
        and curr["Close"] < midpoint
        and curr["Close"] > prev["Open"]
    ):
        return {
            "pattern": "Dark Cloud Cover",
            "signal": "SELL",
            "strength": 85,
        }

    return None


def detect_hanging_man(df: pd.DataFrame):
    if len(df) < 1:
        return None

    candle = df.iloc[-1]

    body = abs(candle["Close"] - candle["Open"])
    lower_shadow = min(candle["Open"], candle["Close"]) - candle["Low"]
    upper_shadow = candle["High"] - max(candle["Open"], candle["Close"])

    if (
        lower_shadow > body * 2
        and upper_shadow < body
    ):
        return {
            "pattern": "Hanging Man",
            "signal": "SELL",
            "strength": 87,
        }

    return None