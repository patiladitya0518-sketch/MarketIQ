import pandas as pd


def calculate_confidence(df: pd.DataFrame, pattern: dict):
    """
    Calculate AI confidence using:
    - Candlestick pattern
    - RSI
    - MACD
    - EMA20
    - EMA50
    - Volume

    MACD crossover is only reported when an actual
    crossover is detected between the previous and
    current candle.
    """

    if df.empty:
        return 0, ["No market data available"]

    latest = df.iloc[-1]

    score = 50
    reasons = []

    # ==================================================
    # Pattern Strength
    # ==================================================

    if pattern:

        strength = pattern.get("strength", 0)

        score += strength * 0.20

        reasons.append(
            f"{pattern['pattern']} detected"
        )

    # ==================================================
    # RSI
    # ==================================================

    rsi = latest["RSI"]

    if rsi > 60:

        score += 10

        reasons.append(
            "RSI confirms bullish momentum"
        )

    elif rsi < 40:

        score += 10

        reasons.append(
            "RSI confirms bearish momentum"
        )

    else:

        reasons.append(
            "RSI is in a neutral zone"
        )

    # ==================================================
    # MACD
    # ==================================================

    macd = latest["MACD"]
    macd_signal = latest["MACD_SIGNAL"]

    bullish_crossover = bool(
        latest.get(
            "MACD_BULLISH_CROSSOVER",
            False,
        )
    )

    bearish_crossover = bool(
        latest.get(
            "MACD_BEARISH_CROSSOVER",
            False,
        )
    )

    if bullish_crossover:

        score += 10

        reasons.append(
            "MACD bullish crossover confirmed"
        )

    elif bearish_crossover:

        score += 10

        reasons.append(
            "MACD bearish crossover confirmed"
        )

    elif macd > macd_signal:

        score += 5

        reasons.append(
            "MACD is bullish"
        )

    elif macd < macd_signal:

        score += 5

        reasons.append(
            "MACD is bearish"
        )

    else:

        reasons.append(
            "MACD is neutral"
        )

    # ==================================================
    # EMA20
    # ==================================================

    if latest["Close"] > latest["EMA20"]:

        score += 10

        reasons.append(
            "Price above EMA20"
        )

    elif latest["Close"] < latest["EMA20"]:

        reasons.append(
            "Price below EMA20"
        )

    # ==================================================
    # EMA50
    # ==================================================

    if latest["Close"] > latest["EMA50"]:

        score += 10

        reasons.append(
            "Price above EMA50"
        )

    elif latest["Close"] < latest["EMA50"]:

        reasons.append(
            "Price below EMA50"
        )

    # ==================================================
    # Volume
    # ==================================================

    if "Volume" in df.columns:

        avg_volume = (
            df["Volume"]
            .tail(20)
            .mean()
        )

        if (
            pd.notna(avg_volume)
            and latest["Volume"] > avg_volume
        ):

            score += 10

            reasons.append(
                "High trading volume"
            )

    # ==================================================
    # Clamp Score
    # ==================================================

    score = min(
        100,
        max(
            0,
            int(score),
        ),
    )

    return score, reasons