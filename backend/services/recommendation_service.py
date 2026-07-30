def generate_recommendation(indicators):
    score = 0
    reasons = []

    # RSI
    if indicators["RSI"] > 55:
        score += 1
        reasons.append("RSI is bullish")
    elif indicators["RSI"] < 45:
        score -= 1
        reasons.append("RSI is bearish")

    # EMA
    if indicators["Close"] > indicators["EMA20"]:
        score += 1
        reasons.append("Price above EMA20")
    else:
        score -= 1
        reasons.append("Price below EMA20")

    # MACD
    if indicators["MACD"] > indicators["MACD_SIGNAL"]:
        score += 1
        reasons.append("MACD bullish crossover")
    else:
        score -= 1
        reasons.append("MACD bearish crossover")

    # Final recommendation
    if score >= 2:
        action = "BUY"
    elif score <= -2:
        action = "SELL"
    else:
        action = "HOLD"

    confidence = min(abs(score) * 30 + 40, 95)

    return {
        "recommendation": action,
        "confidence": confidence,
        "reasons": reasons
    }