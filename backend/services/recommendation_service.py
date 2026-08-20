def generate_recommendation(
    indicators,
    pattern=None,
    market_structure=None,
    support_resistance=None,
):
    """
    MarketIQ AI Recommendation Engine

    Combines:
    - RSI
    - Price vs EMA20
    - EMA20 vs EMA50
    - MACD + crossover
    - Candlestick pattern
    - Market structure
    - Support / Resistance

    The engine is designed to avoid strong BUY/SELL
    decisions when the signals are heavily mixed.
    """

    score = 0
    reasons = []

    bullish_factors = 0
    bearish_factors = 0

    # ============================================================
    # INDICATORS
    # ============================================================

    rsi = float(indicators.get("RSI", 50))
    close = float(indicators.get("Close", 0))
    ema20 = float(indicators.get("EMA20", close))
    ema50 = float(indicators.get("EMA50", close))

    macd = float(indicators.get("MACD", 0))
    macd_signal = float(
        indicators.get("MACD_SIGNAL", 0)
    )

    macd_bullish_crossover = bool(
        indicators.get(
            "MACD_BULLISH_CROSSOVER",
            False,
        )
    )

    macd_bearish_crossover = bool(
        indicators.get(
            "MACD_BEARISH_CROSSOVER",
            False,
        )
    )

    # ============================================================
    # 1. RSI
    # Weight: 1
    # ============================================================

    if rsi >= 60:

        score += 1
        bullish_factors += 1

        reasons.append(
            f"RSI is bullish at {rsi:.2f}"
        )

    elif rsi <= 40:

        score -= 1
        bearish_factors += 1

        reasons.append(
            f"RSI is bearish at {rsi:.2f}"
        )

    else:

        reasons.append(
            f"RSI is neutral at {rsi:.2f}"
        )

    # ============================================================
    # 2. PRICE VS EMA20
    # Weight: 1
    # ============================================================

    if close > ema20:

        score += 1
        bullish_factors += 1

        reasons.append(
            f"Price ({close:.2f}) is above "
            f"EMA20 ({ema20:.2f})"
        )

    elif close < ema20:

        score -= 1
        bearish_factors += 1

        reasons.append(
            f"Price ({close:.2f}) is below "
            f"EMA20 ({ema20:.2f})"
        )

    # ============================================================
    # 3. EMA20 VS EMA50
    # Weight: 1
    # ============================================================

    if ema20 > ema50:

        score += 1
        bullish_factors += 1

        reasons.append(
            f"EMA20 ({ema20:.2f}) is above "
            f"EMA50 ({ema50:.2f}), indicating "
            f"a bullish trend bias"
        )

    elif ema20 < ema50:

        score -= 1
        bearish_factors += 1

        reasons.append(
            f"EMA20 ({ema20:.2f}) is below "
            f"EMA50 ({ema50:.2f}), indicating "
            f"a bearish trend bias"
        )

    # ============================================================
    # 4. MACD
    # Weight: 1
    # ============================================================

    if macd_bullish_crossover:

        score += 1
        bullish_factors += 1

        reasons.append(
            "MACD bullish crossover confirmed"
        )

    elif macd_bearish_crossover:

        score -= 1
        bearish_factors += 1

        reasons.append(
            "MACD bearish crossover confirmed"
        )

    elif macd > macd_signal:

        score += 1
        bullish_factors += 1

        reasons.append(
            f"MACD ({macd:.2f}) is above "
            f"signal ({macd_signal:.2f}), "
            f"showing bullish momentum"
        )

    elif macd < macd_signal:

        score -= 1
        bearish_factors += 1

        reasons.append(
            f"MACD ({macd:.2f}) is below "
            f"signal ({macd_signal:.2f}), "
            f"showing bearish momentum"
        )

    else:

        reasons.append(
            "MACD is neutral"
        )

    # ============================================================
    # 5. CANDLESTICK PATTERN
    #
    # Strong patterns only affect the score when
    # confidence is sufficiently high.
    # ============================================================

    pattern_info = None

    if pattern:

        pattern_name = pattern.get(
            "pattern",
            "Unknown",
        )

        pattern_signal = pattern.get(
            "signal",
            "HOLD",
        )

        pattern_confidence = float(
            pattern.get(
                "confidence",
                0,
            )
        )

        pattern_info = {
            "pattern": pattern_name,
            "signal": pattern_signal,
            "confidence": pattern_confidence,
        }

        if (
            pattern_signal == "BUY"
            and pattern_confidence >= 75
        ):

            score += 1
            bullish_factors += 1

            reasons.append(
                f"{pattern_name} supports BUY "
                f"({pattern_confidence:.0f}% confidence)"
            )

        elif (
            pattern_signal == "SELL"
            and pattern_confidence >= 75
        ):

            score -= 1
            bearish_factors += 1

            reasons.append(
                f"{pattern_name} supports SELL "
                f"({pattern_confidence:.0f}% confidence)"
            )

        elif pattern_signal == "HOLD":

            reasons.append(
                f"{pattern_name} does not provide "
                f"a strong directional signal"
            )

        else:

            reasons.append(
                f"{pattern_name} has insufficient "
                f"confidence for a directional signal"
            )

    # ============================================================
    # 6. MARKET STRUCTURE
    #
    # Weight: 2
    # ============================================================

    market_structure_info = None

    if market_structure:

        structure = market_structure.get(
            "structure",
            "Neutral",
        )

        trend = market_structure.get(
            "trend",
            "NEUTRAL",
        )

        structure_signal = market_structure.get(
            "signal",
            "HOLD",
        )

        structure_confidence = float(
            market_structure.get(
                "confidence",
                0,
            )
        )

        market_structure_info = {
            "structure": structure,
            "trend": trend,
            "signal": structure_signal,
            "confidence": structure_confidence,
        }

        if (
            structure_signal == "BUY"
            and structure_confidence >= 60
        ):

            score += 2
            bullish_factors += 2

            reasons.append(
                f"Market structure is bullish "
                f"({structure_confidence:.0f}% confidence)"
            )

        elif (
            structure_signal == "SELL"
            and structure_confidence >= 60
        ):

            score -= 2
            bearish_factors += 2

            reasons.append(
                f"Market structure is bearish "
                f"({structure_confidence:.0f}% confidence)"
            )

        else:

            reasons.append(
                "Market structure is neutral"
            )

    # ============================================================
    # 7. SUPPORT / RESISTANCE
    # Weight: 1
    # ============================================================

    support_resistance_info = None

    nearest_support = None
    nearest_resistance = None

    if support_resistance and close > 0:

        supports = support_resistance.get(
            "support",
            [],
        )

        resistances = support_resistance.get(
            "resistance",
            [],
        )

        # --------------------------------------------------------
        # Clean numeric levels
        # --------------------------------------------------------

        supports = [
            float(level)
            for level in supports
            if level is not None
        ]

        resistances = [
            float(level)
            for level in resistances
            if level is not None
        ]

        # --------------------------------------------------------
        # Nearest support below current price
        # --------------------------------------------------------

        below_supports = [
            level
            for level in supports
            if level <= close
        ]

        if below_supports:

            nearest_support = max(
                below_supports
            )

        # --------------------------------------------------------
        # Nearest resistance above current price
        # --------------------------------------------------------

        above_resistances = [
            level
            for level in resistances
            if level >= close
        ]

        if above_resistances:

            nearest_resistance = min(
                above_resistances
            )

        support_near = False
        resistance_near = False

        # --------------------------------------------------------
        # Support proximity
        # --------------------------------------------------------

        if nearest_support is not None:

            support_distance = (
                abs(close - nearest_support)
                / close
            ) * 100

            if support_distance <= 2:

                support_near = True

                score += 1
                bullish_factors += 1

                reasons.append(
                    f"Price is near support "
                    f"({nearest_support:.2f})"
                )

        # --------------------------------------------------------
        # Resistance proximity
        # --------------------------------------------------------

        if nearest_resistance is not None:

            resistance_distance = (
                abs(nearest_resistance - close)
                / close
            ) * 100

            if resistance_distance <= 2:

                resistance_near = True

                score -= 1
                bearish_factors += 1

                reasons.append(
                    f"Price is near resistance "
                    f"({nearest_resistance:.2f})"
                )

        if (
            not support_near
            and not resistance_near
        ):

            reasons.append(
                "Price is not near a major "
                "detected support or resistance level"
            )

        support_resistance_info = {

            "nearest_support": (
                round(nearest_support, 2)
                if nearest_support is not None
                else None
            ),

            "nearest_resistance": (
                round(nearest_resistance, 2)
                if nearest_resistance is not None
                else None
            ),
        }

    # ============================================================
    # SIGNAL BALANCE
    # ============================================================

    total_factors = (
        bullish_factors
        + bearish_factors
    )

    # ------------------------------------------------------------
    # Strong disagreement between signals
    # ------------------------------------------------------------

    if (
        bullish_factors > 0
        and bearish_factors > 0
    ):

        difference = abs(
            bullish_factors
            - bearish_factors
        )

        if difference <= 1:

            reasons.append(
                f"Signals are mixed "
                f"({bullish_factors} bullish vs "
                f"{bearish_factors} bearish factors)"
            )

            # Prevent a weakly conflicting setup
            # from producing an aggressive signal.
            if abs(score) < 4:

                score = 0

    # ============================================================
    # FINAL RECOMMENDATION
    # ============================================================

    if score >= 4:

        action = "BUY"

    elif score <= -4:

        action = "SELL"

    else:

        action = "HOLD"

    # ============================================================
    # CONFIDENCE
    #
    # Confidence depends on:
    # - absolute score
    # - agreement between factors
    # - number of supporting factors
    # ============================================================

    absolute_score = abs(score)

    confidence_map = {
        0: 50,
        1: 55,
        2: 62,
        3: 70,
        4: 80,
        5: 87,
        6: 92,
        7: 95,
        8: 97,
        9: 98,
    }

    confidence = confidence_map.get(
        absolute_score,
        98,
    )

    # ------------------------------------------------------------
    # Mixed signals reduce confidence
    # ------------------------------------------------------------

    if (
        bullish_factors > 0
        and bearish_factors > 0
    ):

        imbalance = abs(
            bullish_factors
            - bearish_factors
        )

        if imbalance <= 1:

            confidence = min(
                confidence,
                55,
            )

        elif imbalance == 2:

            confidence = min(
                confidence,
                68,
            )

    # ------------------------------------------------------------
    # HOLD should never claim excessive confidence
    # ------------------------------------------------------------

    if action == "HOLD":

        confidence = min(
            confidence,
            65,
        )

    # ============================================================
    # FINAL RESPONSE
    # ============================================================

    return {

        "recommendation": action,

        "confidence": confidence,

        "score": score,

        "reasons": reasons,

        "pattern_analysis": pattern_info,

        "market_structure_analysis": (
            market_structure_info
        ),

        "support_resistance_analysis": (
            support_resistance_info
        ),
    }