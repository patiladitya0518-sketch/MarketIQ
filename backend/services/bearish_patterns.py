import pandas as pd


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def candle_body(candle):
    return abs(float(candle["Close"]) - float(candle["Open"]))


def candle_range(candle):
    return float(candle["High"]) - float(candle["Low"])


def upper_shadow(candle):
    return float(candle["High"]) - max(
        float(candle["Open"]),
        float(candle["Close"]),
    )


def lower_shadow(candle):
    return min(
        float(candle["Open"]),
        float(candle["Close"]),
    ) - float(candle["Low"])


def is_bullish(candle):
    return float(candle["Close"]) > float(candle["Open"])


def is_bearish(candle):
    return float(candle["Close"]) < float(candle["Open"])


# ============================================================
# BEARISH ENGULFING
# ============================================================

def detect_bearish_engulfing(df: pd.DataFrame):

    if len(df) < 2:
        return None

    prev = df.iloc[-2]
    curr = df.iloc[-1]

    if (
        is_bullish(prev)
        and is_bearish(curr)
        and curr["Open"] >= prev["Close"]
        and curr["Close"] <= prev["Open"]
    ):

        return {
            "pattern": "Bearish Engulfing",
            "signal": "SELL",
            "strength": 95,
        }

    return None


# ============================================================
# SHOOTING STAR
# ============================================================

def detect_shooting_star(df: pd.DataFrame):

    if len(df) < 3:
        return None

    candle = df.iloc[-1]

    body = candle_body(candle)
    total_range = candle_range(candle)

    if total_range <= 0:
        return None

    upper = upper_shadow(candle)
    lower = lower_shadow(candle)

    effective_body = max(body, total_range * 0.01)

    shooting_shape = (
        upper >= effective_body * 2
        and lower <= effective_body * 0.8
        and body / total_range <= 0.45
    )

    previous = df.iloc[-3:-1]

    uptrend = (
        previous.iloc[0]["Close"]
        <= previous.iloc[-1]["Close"]
    )

    if shooting_shape and uptrend:

        return {
            "pattern": "Shooting Star",
            "signal": "SELL",
            "strength": 88,
        }

    return None


# ============================================================
# EVENING STAR
# ============================================================

def detect_evening_star(df: pd.DataFrame):

    if len(df) < 3:
        return None

    a = df.iloc[-3]
    b = df.iloc[-2]
    c = df.iloc[-1]

    body_a = candle_body(a)
    body_b = candle_body(b)

    if body_a <= 0:
        return None

    midpoint_a = (
        float(a["Open"]) + float(a["Close"])
    ) / 2

    if (
        is_bullish(a)
        and body_b <= body_a * 0.5
        and is_bearish(c)
        and c["Close"] < midpoint_a
    ):

        return {
            "pattern": "Evening Star",
            "signal": "SELL",
            "strength": 92,
        }

    return None


# ============================================================
# DARK CLOUD COVER
# ============================================================

def detect_dark_cloud_cover(df: pd.DataFrame):

    if len(df) < 2:
        return None

    prev = df.iloc[-2]
    curr = df.iloc[-1]

    midpoint = (
        float(prev["Open"]) + float(prev["Close"])
    ) / 2

    if (
        is_bullish(prev)
        and is_bearish(curr)
        and curr["Close"] < midpoint
        and curr["Close"] > prev["Open"]
    ):

        return {
            "pattern": "Dark Cloud Cover",
            "signal": "SELL",
            "strength": 85,
        }

    return None


# ============================================================
# HANGING MAN
# ============================================================

def detect_hanging_man(df: pd.DataFrame):

    if len(df) < 3:
        return None

    candle = df.iloc[-1]

    body = candle_body(candle)
    total_range = candle_range(candle)

    if total_range <= 0:
        return None

    lower = lower_shadow(candle)
    upper = upper_shadow(candle)

    effective_body = max(body, total_range * 0.01)

    hanging_shape = (
        lower >= effective_body * 2
        and upper <= effective_body * 0.8
        and body / total_range <= 0.45
    )

    previous = df.iloc[-3:-1]

    uptrend = (
        previous.iloc[0]["Close"]
        <= previous.iloc[-1]["Close"]
    )

    if hanging_shape and uptrend:

        return {
            "pattern": "Hanging Man",
            "signal": "SELL",
            "strength": 87,
        }

    return None