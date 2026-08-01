import pandas as pd


def calculate_confidence(df: pd.DataFrame, pattern: dict):
    """
    Calculate AI confidence using
    candlestick pattern + technical indicators.
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

        reasons.append(f"{pattern['pattern']} detected")

    # ==================================================
    # RSI
    # ==================================================

    rsi = latest["RSI"]

    if rsi > 60:
        score += 10
        reasons.append("RSI confirms bullish momentum")

    elif rsi < 40:
        score += 10
        reasons.append("RSI confirms bearish momentum")

    # ==================================================
    # MACD
    # ==================================================

    if latest["MACD"] > latest["MACD_SIGNAL"]:
        score += 10
        reasons.append("MACD bullish crossover")

    else:
        score += 5
        reasons.append("MACD bearish trend")

    # ==================================================
    # EMA20
    # ==================================================

    if latest["Close"] > latest["EMA20"]:
        score += 10
        reasons.append("Price above EMA20")

    # ==================================================
    # EMA50
    # ==================================================

    if latest["Close"] > latest["EMA50"]:
        score += 10
        reasons.append("Price above EMA50")

    # ==================================================
    # Volume
    # ==================================================

    avg_volume = df["Volume"].tail(20).mean()

    if latest["Volume"] > avg_volume:
        score += 10
        reasons.append("High trading volume")

    # ==================================================
    # Clamp score
    # ==================================================

    score = min(100, max(0, int(score)))

    return score, reasons