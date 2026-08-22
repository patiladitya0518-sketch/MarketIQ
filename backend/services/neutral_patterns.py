import pandas as pd


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def candle_body(candle):
    return abs(
        float(candle["Close"])
        - float(candle["Open"])
    )


def candle_range(candle):
    return (
        float(candle["High"])
        - float(candle["Low"])
    )


def upper_shadow(candle):
    return (
        float(candle["High"])
        - max(
            float(candle["Open"]),
            float(candle["Close"]),
        )
    )


def lower_shadow(candle):
    return (
        min(
            float(candle["Open"]),
            float(candle["Close"]),
        )
        - float(candle["Low"])
    )


# ============================================================
# DOJI
# ============================================================

def detect_doji(df: pd.DataFrame):

    if len(df) < 1:
        return None

    candle = df.iloc[-1]

    body = candle_body(candle)
    total = candle_range(candle)

    if total <= 0:
        return None

    body_ratio = body / total

    if body_ratio <= 0.12:

        return {
            "pattern": "Doji",
            "signal": "HOLD",
            "strength": 75,
        }

    return None


# ============================================================
# SPINNING TOP
# ============================================================

def detect_spinning_top(df: pd.DataFrame):

    if len(df) < 1:
        return None

    candle = df.iloc[-1]

    body = candle_body(candle)
    total = candle_range(candle)

    if total <= 0:
        return None

    upper = upper_shadow(candle)
    lower = lower_shadow(candle)

    body_ratio = body / total

    if (
        body_ratio <= 0.35
        and upper >= body
        and lower >= body
    ):

        return {
            "pattern": "Spinning Top",
            "signal": "HOLD",
            "strength": 70,
        }

    return None


# ============================================================
# DRAGONFLY DOJI
# ============================================================

def detect_dragonfly_doji(df: pd.DataFrame):

    if len(df) < 1:
        return None

    candle = df.iloc[-1]

    body = candle_body(candle)
    total = candle_range(candle)

    if total <= 0:
        return None

    upper = upper_shadow(candle)
    lower = lower_shadow(candle)

    body_ratio = body / total

    if (
        body_ratio <= 0.12
        and upper <= total * 0.12
        and lower >= total * 0.55
    ):

        return {
            "pattern": "Dragonfly Doji",
            "signal": "HOLD",
            "strength": 80,
        }

    return None


# ============================================================
# GRAVESTONE DOJI
# ============================================================

def detect_gravestone_doji(df: pd.DataFrame):

    if len(df) < 1:
        return None

    candle = df.iloc[-1]

    body = candle_body(candle)
    total = candle_range(candle)

    if total <= 0:
        return None

    upper = upper_shadow(candle)
    lower = lower_shadow(candle)

    body_ratio = body / total

    if (
        body_ratio <= 0.12
        and upper >= total * 0.55
        and lower <= total * 0.12
    ):

        return {
            "pattern": "Gravestone Doji",
            "signal": "HOLD",
            "strength": 80,
        }

    return None


# ============================================================
# MARUBOZU
# ============================================================

def detect_marubozu(df: pd.DataFrame):

    if len(df) < 1:
        return None

    candle = df.iloc[-1]

    body = candle_body(candle)
    total = candle_range(candle)

    if total <= 0:
        return None

    upper = upper_shadow(candle)
    lower = lower_shadow(candle)

    body_ratio = body / total

    if (
        body_ratio >= 0.90
        and upper <= total * 0.05
        and lower <= total * 0.05
    ):

        if candle["Close"] > candle["Open"]:
            signal = "BUY"
        elif candle["Close"] < candle["Open"]:
            signal = "SELL"
        else:
            signal = "HOLD"

        return {
            "pattern": "Marubozu",
            "signal": signal,
            "strength": 90,
        }

    return None