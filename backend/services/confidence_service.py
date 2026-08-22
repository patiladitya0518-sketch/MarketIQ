import pandas as pd


def calculate_confidence(
    df: pd.DataFrame,
    pattern: dict,
):
    """
    MarketIQ AI Confidence Engine.

    Confidence is calculated using whatever market data
    is available.

    Supported factors:
    - Candlestick pattern strength
    - RSI
    - MACD
    - MACD crossover
    - EMA20
    - EMA50
    - Volume

    The function is intentionally defensive.

    If an indicator is missing, it will NOT crash the
    pattern detection engine. The available indicators
    will still be used.
    """

    # ============================================================
    # VALIDATION
    # ============================================================

    if df is None or df.empty:

        return (
            0,
            [
                "No market data available"
            ],
        )

    latest = df.iloc[-1]

    # Base confidence
    score = 50

    reasons = []

    # ============================================================
    # CANDLESTICK PATTERN
    # ============================================================

    if pattern:

        pattern_name = pattern.get(
            "pattern",
            "Unknown",
        )

        strength = pattern.get(
            "strength",
            0,
        )

        try:
            strength = float(strength)
        except (
            TypeError,
            ValueError,
        ):
            strength = 0

        # Pattern contributes up to approximately 20 points
        score += strength * 0.20

        reasons.append(
            f"{pattern_name} detected"
        )

    # ============================================================
    # RSI
    # ============================================================

    rsi = latest.get(
        "RSI",
        None,
    )

    if pd.notna(rsi):

        try:
            rsi = float(rsi)

            if rsi > 60:

                score += 10

                reasons.append(
                    f"RSI {rsi:.2f} confirms bullish momentum"
                )

            elif rsi < 40:

                score += 10

                reasons.append(
                    f"RSI {rsi:.2f} confirms bearish momentum"
                )

            else:

                reasons.append(
                    f"RSI {rsi:.2f} is in a neutral zone"
                )

        except (
            TypeError,
            ValueError,
        ):

            reasons.append(
                "RSI data unavailable"
            )

    else:

        reasons.append(
            "RSI data unavailable"
        )

    # ============================================================
    # MACD
    # ============================================================

    macd = latest.get(
        "MACD",
        None,
    )

    macd_signal = latest.get(
        "MACD_SIGNAL",
        None,
    )

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

    if (
        pd.notna(macd)
        and pd.notna(macd_signal)
    ):

        try:

            macd = float(macd)
            macd_signal = float(
                macd_signal
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

        except (
            TypeError,
            ValueError,
        ):

            reasons.append(
                "MACD data unavailable"
            )

    else:

        reasons.append(
            "MACD data unavailable"
        )

    # ============================================================
    # EMA20
    # ============================================================

    close = latest.get(
        "Close",
        None,
    )

    ema20 = latest.get(
        "EMA20",
        None,
    )

    if (
        pd.notna(close)
        and pd.notna(ema20)
    ):

        try:

            close = float(close)
            ema20 = float(ema20)

            if close > ema20:

                score += 10

                reasons.append(
                    "Price above EMA20"
                )

            elif close < ema20:

                reasons.append(
                    "Price below EMA20"
                )

            else:

                reasons.append(
                    "Price is near EMA20"
                )

        except (
            TypeError,
            ValueError,
        ):

            reasons.append(
                "EMA20 data unavailable"
            )

    else:

        reasons.append(
            "EMA20 data unavailable"
        )

    # ============================================================
    # EMA50
    # ============================================================

    ema50 = latest.get(
        "EMA50",
        None,
    )

    if (
        pd.notna(close)
        and pd.notna(ema50)
    ):

        try:

            close = float(close)
            ema50 = float(ema50)

            if close > ema50:

                score += 10

                reasons.append(
                    "Price above EMA50"
                )

            elif close < ema50:

                reasons.append(
                    "Price below EMA50"
                )

            else:

                reasons.append(
                    "Price is near EMA50"
                )

        except (
            TypeError,
            ValueError,
        ):

            reasons.append(
                "EMA50 data unavailable"
            )

    else:

        reasons.append(
            "EMA50 data unavailable"
        )

    # ============================================================
    # VOLUME
    # ============================================================

    if "Volume" in df.columns:

        try:

            avg_volume = (
                pd.to_numeric(
                    df["Volume"],
                    errors="coerce",
                )
                .tail(20)
                .mean()
            )

            current_volume = pd.to_numeric(
                pd.Series(
                    [latest["Volume"]]
                ),
                errors="coerce",
            ).iloc[0]

            if (
                pd.notna(avg_volume)
                and pd.notna(current_volume)
            ):

                if current_volume > avg_volume:

                    score += 10

                    reasons.append(
                        "High trading volume"
                    )

                else:

                    reasons.append(
                        "Trading volume is normal"
                    )

            else:

                reasons.append(
                    "Volume data unavailable"
                )

        except Exception:

            reasons.append(
                "Volume data unavailable"
            )

    else:

        reasons.append(
            "Volume data unavailable"
        )

    # ============================================================
    # PATTERN SIGNAL ADJUSTMENT
    # ============================================================

    signal = (
        pattern.get(
            "signal",
            "HOLD",
        )
        if pattern
        else "HOLD"
    )

    # Give a small additional boost when the
    # detected pattern has a directional signal.
    if signal == "BUY":

        score += 3

    elif signal == "SELL":

        score += 3

    # ============================================================
    # CLAMP CONFIDENCE
    # ============================================================

    score = int(
        min(
            100,
            max(
                0,
                round(score),
            ),
        )
    )

    # ============================================================
    # RETURN
    # ============================================================

    return score, reasons