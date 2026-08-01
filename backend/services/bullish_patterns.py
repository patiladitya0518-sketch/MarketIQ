import pandas as pd


def detect_bullish_engulfing(df: pd.DataFrame):
    if len(df) < 2:
        return None

    prev = df.iloc[-2]
    curr = df.iloc[-1]

    if (
        prev["Close"] < prev["Open"]
        and curr["Close"] > curr["Open"]
        and curr["Open"] < prev["Close"]
        and curr["Close"] > prev["Open"]
    ):
        return {
            "pattern": "Bullish Engulfing",
            "signal": "BUY",
            "strength": 95,
        }

    return None


def detect_hammer(df: pd.DataFrame):
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
            "pattern": "Hammer",
            "signal": "BUY",
            "strength": 88,
        }

    return None


def detect_morning_star(df: pd.DataFrame):
    if len(df) < 3:
        return None

    a = df.iloc[-3]
    b = df.iloc[-2]
    c = df.iloc[-1]

    if (
        a["Close"] < a["Open"]
        and abs(b["Close"] - b["Open"]) < abs(a["Close"] - a["Open"]) * 0.4
        and c["Close"] > c["Open"]
    ):
        return {
            "pattern": "Morning Star",
            "signal": "BUY",
            "strength": 93,
        }

    return None


def detect_piercing_pattern(df: pd.DataFrame):
    if len(df) < 2:
        return None

    prev = df.iloc[-2]
    curr = df.iloc[-1]

    midpoint = (prev["Open"] + prev["Close"]) / 2

    if (
        prev["Close"] < prev["Open"]
        and curr["Close"] > midpoint
        and curr["Close"] < prev["Open"]
    ):
        return {
            "pattern": "Piercing Pattern",
            "signal": "BUY",
            "strength": 86,
        }

    return None


def detect_three_white_soldiers(df: pd.DataFrame):
    if len(df) < 3:
        return None

    a = df.iloc[-3]
    b = df.iloc[-2]
    c = df.iloc[-1]

    if (
        a["Close"] > a["Open"]
        and b["Close"] > b["Open"]
        and c["Close"] > c["Open"]
        and a["Close"] < b["Close"] < c["Close"]
    ):
        return {
            "pattern": "Three White Soldiers",
            "signal": "BUY",
            "strength": 97,
        }

    return None