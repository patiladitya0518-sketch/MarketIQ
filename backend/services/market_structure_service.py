import pandas as pd


def detect_market_structure(df: pd.DataFrame):
    """
    MarketIQ Market Structure Engine.

    Detects:
    - Higher High (HH)
    - Higher Low (HL)
    - Lower High (LH)
    - Lower Low (LL)

    Also determines the overall market structure.
    """

    if df is None or df.empty or len(df) < 10:
        return {
            "structure": "Neutral",
            "trend": "NEUTRAL",
            "signal": "HOLD",
            "confidence": 0,
            "swings": [],
            "reasons": [
                "Not enough historical data"
            ],
        }

    # ------------------------------------------------------------
    # Use recent candles
    # ------------------------------------------------------------

    data = df.copy().tail(30)

    highs = data["High"].astype(float)
    lows = data["Low"].astype(float)

    swing_points = []

    # ------------------------------------------------------------
    # Detect simple swing highs / lows
    # ------------------------------------------------------------

    for i in range(1, len(data) - 1):

        previous_high = highs.iloc[i - 1]
        current_high = highs.iloc[i]
        next_high = highs.iloc[i + 1]

        previous_low = lows.iloc[i - 1]
        current_low = lows.iloc[i]
        next_low = lows.iloc[i + 1]

        # Swing High
        if (
            current_high > previous_high
            and current_high > next_high
        ):
            swing_points.append({
                "type": "HIGH",
                "price": round(current_high, 2),
                "position": i,
            })

        # Swing Low
        if (
            current_low < previous_low
            and current_low < next_low
        ):
            swing_points.append({
                "type": "LOW",
                "price": round(current_low, 2),
                "position": i,
            })

    # ------------------------------------------------------------
    # Classify swing structure
    # ------------------------------------------------------------

    highs_list = [
        point
        for point in swing_points
        if point["type"] == "HIGH"
    ]

    lows_list = [
        point
        for point in swing_points
        if point["type"] == "LOW"
    ]

    classifications = []

    # Higher High / Lower High
    for i in range(1, len(highs_list)):

        previous = highs_list[i - 1]["price"]
        current = highs_list[i]["price"]

        if current > previous:
            classifications.append("HH")

        elif current < previous:
            classifications.append("LH")

    # Higher Low / Lower Low
    for i in range(1, len(lows_list)):

        previous = lows_list[i - 1]["price"]
        current = lows_list[i]["price"]

        if current > previous:
            classifications.append("HL")

        elif current < previous:
            classifications.append("LL")

    # ------------------------------------------------------------
    # Count structure
    # ------------------------------------------------------------

    hh_count = classifications.count("HH")
    hl_count = classifications.count("HL")

    lh_count = classifications.count("LH")
    ll_count = classifications.count("LL")

    bullish_points = hh_count + hl_count
    bearish_points = lh_count + ll_count

    # ------------------------------------------------------------
    # Determine overall structure
    # ------------------------------------------------------------

    if bullish_points >= bearish_points + 2:

        structure = "Bullish"
        trend = "BULLISH"
        signal = "BUY"

    elif bearish_points >= bullish_points + 2:

        structure = "Bearish"
        trend = "BEARISH"
        signal = "SELL"

    else:

        structure = "Neutral"
        trend = "NEUTRAL"
        signal = "HOLD"

    # ------------------------------------------------------------
    # Confidence
    # ------------------------------------------------------------

    total_points = (
        bullish_points + bearish_points
    )

    if total_points == 0:
        confidence = 40

    else:
        difference = abs(
            bullish_points - bearish_points
        )

        confidence = min(
            50 + difference * 10,
            90,
        )

    # ------------------------------------------------------------
    # Reasons
    # ------------------------------------------------------------

    reasons = []

    if hh_count > 0:
        reasons.append(
            f"{hh_count} Higher High structure(s) detected"
        )

    if hl_count > 0:
        reasons.append(
            f"{hl_count} Higher Low structure(s) detected"
        )

    if lh_count > 0:
        reasons.append(
            f"{lh_count} Lower High structure(s) detected"
        )

    if ll_count > 0:
        reasons.append(
            f"{ll_count} Lower Low structure(s) detected"
        )

    if structure == "Bullish":
        reasons.append(
            "Market structure is bullish"
        )

    elif structure == "Bearish":
        reasons.append(
            "Market structure is bearish"
        )

    else:
        reasons.append(
            "Market structure is mixed"
        )

    # ------------------------------------------------------------
    # Return
    # ------------------------------------------------------------

    return {
        "structure": structure,
        "trend": trend,
        "signal": signal,
        "confidence": confidence,

        "swing_counts": {
            "higher_high": hh_count,
            "higher_low": hl_count,
            "lower_high": lh_count,
            "lower_low": ll_count,
        },

        "reasons": reasons,
    }