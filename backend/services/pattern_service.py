import pandas as pd


def detect_pattern(df: pd.DataFrame):
    """
    Detect simple candlestick patterns.
    """

    if len(df) < 2:
        return {
            "pattern": "Unknown",
            "signal": "HOLD",
            "confidence": 0,
            "reason": ["Not enough candle data"],
        }

    prev = df.iloc[-2]
    curr = df.iloc[-1]

    # ---------------------------------------------------
    # Bullish Engulfing
    # ---------------------------------------------------

    if (
        prev["Close"] < prev["Open"]
        and curr["Close"] > curr["Open"]
        and curr["Open"] < prev["Close"]
        and curr["Close"] > prev["Open"]
    ):
        return {
            "pattern": "Bullish Engulfing",
            "signal": "BUY",
            "confidence": 92,
            "reason": [
                "Bullish engulfing detected",
                "Strong buying pressure",
                "Possible trend reversal",
            ],
        }

    # ---------------------------------------------------
    # Bearish Engulfing
    # ---------------------------------------------------

    if (
        prev["Close"] > prev["Open"]
        and curr["Close"] < curr["Open"]
        and curr["Open"] > prev["Close"]
        and curr["Close"] < prev["Open"]
    ):
        return {
            "pattern": "Bearish Engulfing",
            "signal": "SELL",
            "confidence": 90,
            "reason": [
                "Bearish engulfing detected",
                "Selling pressure increasing",
                "Possible downtrend",
            ],
        }

    return {
        "pattern": "No Strong Pattern",
        "signal": "HOLD",
        "confidence": 60,
        "reason": [
            "No major candlestick pattern detected"
        ],
    }