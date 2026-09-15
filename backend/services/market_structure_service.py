import pandas as pd


def detect_market_structure(df: pd.DataFrame):
    """
    MarketIQ Market Structure Engine.

    Detects:
    - Higher High (HH)
    - Higher Low (HL)
    - Lower High (LH)
    - Lower Low (LL)

    Always returns a consistent response structure
    so the frontend never receives undefined swing_counts.
    """

    # ============================================================
    # DEFAULT RESPONSE
    # ============================================================

    default_response = {
        "structure": "Neutral",
        "trend": "NEUTRAL",
        "signal": "HOLD",
        "confidence": 0,

        "swing_counts": {
            "higher_high": 0,
            "higher_low": 0,
            "lower_high": 0,
            "lower_low": 0,
        },

        "swings": [],

        "reasons": [
            "Not enough historical data",
        ],
    }

    # ============================================================
    # VALIDATE DATA
    # ============================================================

    if df is None or df.empty:
        return default_response

    if len(df) < 10:
        return default_response

    # ============================================================
    # CHECK REQUIRED COLUMNS
    # ============================================================

    required_columns = [
        "High",
        "Low",
    ]

    for column in required_columns:

        if column not in df.columns:
            return {
                **default_response,
                "reasons": [
                    f"Missing required column: {column}"
                ],
            }

    # ============================================================
    # COPY RECENT DATA
    # ============================================================

    try:
        data = df.copy().tail(30)

        data["High"] = pd.to_numeric(
            data["High"],
            errors="coerce",
        )

        data["Low"] = pd.to_numeric(
            data["Low"],
            errors="coerce",
        )

        data = data.dropna(
            subset=[
                "High",
                "Low",
            ]
        )

    except Exception as e:

        return {
            **default_response,
            "reasons": [
                f"Unable to process market data: {str(e)}"
            ],
        }

    if len(data) < 10:
        return default_response

    # ============================================================
    # HIGH / LOW SERIES
    # ============================================================

    highs = data["High"].astype(float)
    lows = data["Low"].astype(float)

    swing_points = []

    # ============================================================
    # DETECT SWING POINTS
    # ============================================================

    for i in range(1, len(data) - 1):

        previous_high = highs.iloc[i - 1]
        current_high = highs.iloc[i]
        next_high = highs.iloc[i + 1]

        previous_low = lows.iloc[i - 1]
        current_low = lows.iloc[i]
        next_low = lows.iloc[i + 1]

        # --------------------------------------------------------
        # Swing High
        # --------------------------------------------------------

        if (
            current_high > previous_high
            and current_high > next_high
        ):

            swing_points.append(
                {
                    "type": "HIGH",
                    "price": round(
                        float(current_high),
                        2,
                    ),
                    "position": i,
                }
            )

        # --------------------------------------------------------
        # Swing Low
        # --------------------------------------------------------

        if (
            current_low < previous_low
            and current_low < next_low
        ):

            swing_points.append(
                {
                    "type": "LOW",
                    "price": round(
                        float(current_low),
                        2,
                    ),
                    "position": i,
                }
            )

    # ============================================================
    # SEPARATE HIGH / LOW SWINGS
    # ============================================================

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

    # ============================================================
    # COUNTERS
    # ============================================================

    hh_count = 0
    hl_count = 0
    lh_count = 0
    ll_count = 0

    # ============================================================
    # CLASSIFY HIGH SWINGS
    # ============================================================

    for i in range(1, len(highs_list)):

        previous = highs_list[i - 1]["price"]
        current = highs_list[i]["price"]

        if current > previous:
            hh_count += 1

        elif current < previous:
            lh_count += 1

    # ============================================================
    # CLASSIFY LOW SWINGS
    # ============================================================

    for i in range(1, len(lows_list)):

        previous = lows_list[i - 1]["price"]
        current = lows_list[i]["price"]

        if current > previous:
            hl_count += 1

        elif current < previous:
            ll_count += 1

    # ============================================================
    # BULLISH / BEARISH POINTS
    # ============================================================

    bullish_points = (
        hh_count
        + hl_count
    )

    bearish_points = (
        lh_count
        + ll_count
    )

    # ============================================================
    # DETERMINE STRUCTURE
    # ============================================================

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

    # ============================================================
    # CONFIDENCE
    # ============================================================

    total_points = (
        bullish_points
        + bearish_points
    )

    if total_points == 0:

        confidence = 40

    else:

        difference = abs(
            bullish_points
            - bearish_points
        )

        confidence = min(
            50 + difference * 10,
            90,
        )

    # ============================================================
    # REASONS
    # ============================================================

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

    if not reasons:

        reasons.append(
            "No significant swing structure detected"
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

    # ============================================================
    # FINAL RESPONSE
    # ============================================================

    return {

        "structure": structure,

        "trend": trend,

        "signal": signal,

        "confidence": confidence,

        # IMPORTANT:
        # Always return this object.
        "swing_counts": {

            "higher_high": hh_count,

            "higher_low": hl_count,

            "lower_high": lh_count,

            "lower_low": ll_count,
        },

        "swings": swing_points,

        "reasons": reasons,
    }