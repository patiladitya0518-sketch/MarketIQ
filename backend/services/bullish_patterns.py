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
# BULLISH ENGULFING
# ============================================================

def detect_bullish_engulfing(df: pd.DataFrame):

    if len(df) < 2:
        return None

    prev = df.iloc[-2]
    curr = df.iloc[-1]

    if (
        is_bearish(prev)
        and is_bullish(curr)
        and curr["Open"] <= prev["Close"]
        and curr["Close"] >= prev["Open"]
    ):

        return {
            "pattern": "Bullish Engulfing",
            "signal": "BUY",
            "strength": 95,
        }

    return None


# ============================================================
# HAMMER
# ============================================================

def detect_hammer(df: pd.DataFrame):

    if len(df) < 3:
        return None

    candle = df.iloc[-1]

    body = candle_body(candle)
    total_range = candle_range(candle)

    if total_range <= 0:
        return None

    lower = lower_shadow(candle)
    upper = upper_shadow(candle)

    # Avoid division problems with extremely small bodies
    effective_body = max(body, total_range * 0.01)

    # Hammer structure
    hammer_shape = (
        lower >= effective_body * 2
        and upper <= effective_body * 0.8
        and body / total_range <= 0.45
    )

    # Previous candles should show some downward movement
    previous = df.iloc[-3:-1]

    downtrend = (
        previous.iloc[0]["Close"]
        >= previous.iloc[-1]["Close"]
    )

    if hammer_shape and downtrend:

        return {
            "pattern": "Hammer",
            "signal": "BUY",
            "strength": 88,
        }

    return None


# ============================================================
# MORNING STAR
# ============================================================

def detect_morning_star(df: pd.DataFrame):

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
        is_bearish(a)
        and body_b <= body_a * 0.5
        and is_bullish(c)
        and c["Close"] > midpoint_a
    ):

        return {
            "pattern": "Morning Star",
            "signal": "BUY",
            "strength": 93,
        }

    return None


# ============================================================
# PIERCING PATTERN
# ============================================================

def detect_piercing_pattern(df: pd.DataFrame):

    if len(df) < 2:
        return None

    prev = df.iloc[-2]
    curr = df.iloc[-1]

    previous_body = candle_body(prev)

    if previous_body <= 0:
        return None

    midpoint = (
        float(prev["Open"]) + float(prev["Close"])
    ) / 2

    if (
        is_bearish(prev)
        and is_bullish(curr)
        and curr["Close"] > midpoint
        and curr["Close"] < prev["Open"]
        and curr["Open"] <= prev["Close"]
    ):

        return {
            "pattern": "Piercing Pattern",
            "signal": "BUY",
            "strength": 86,
        }

    return None


# ============================================================
# THREE WHITE SOLDIERS
# ============================================================

def detect_three_white_soldiers(df: pd.DataFrame):

    if len(df) < 3:
        return None

    a = df.iloc[-3]
    b = df.iloc[-2]
    c = df.iloc[-1]

    if not (
        is_bullish(a)
        and is_bullish(b)
        and is_bullish(c)
    ):
        return None

    body_a = candle_body(a)
    body_b = candle_body(b)
    body_c = candle_body(c)

    if min(body_a, body_b, body_c) <= 0:
        return None

    # Each candle closes higher
    higher_closes = (
        a["Close"] < b["Close"] < c["Close"]
    )

    # Each candle opens within or near previous body
    valid_opens = (
        b["Open"] <= a["Close"]
        and b["Open"] >= a["Open"]
        and c["Open"] <= b["Close"]
        and c["Open"] >= b["Open"]
    )

    # Small upper shadows
    small_upper_shadows = (
        upper_shadow(a) <= body_a * 0.5
        and upper_shadow(b) <= body_b * 0.5
        and upper_shadow(c) <= body_c * 0.5
    )

    if (
        higher_closes
        and valid_opens
        and small_upper_shadows
    ):

        return {
            "pattern": "Three White Soldiers",
            "signal": "BUY",
            "strength": 97,
        }

    return None