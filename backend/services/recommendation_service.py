from typing import Any


# ============================================================
# MARKETIQ AI RECOMMENDATION ENGINE
# ============================================================
#
# Combines:
#
# 1. RSI
# 2. Price vs EMA20
# 3. EMA20 vs EMA50
# 4. MACD
# 5. MACD crossover
# 6. Candlestick pattern
# 7. Market Structure
# 8. Support / Resistance
# 9. Smart Money Concepts (SMC)
#
# SMC includes:
# - Break of Structure (BOS)
# - Change of Character (CHoCH)
# - Order Blocks
# - Liquidity
# - Fair Value Gaps (FVG)
#
# IMPORTANT:
#
# SMC is PRICE-AWARE.
#
# Historical SMC zones are NOT treated equally.
# Zones close to the current price receive more weight.
#
# Directional signal:
#     BUY / SELL / HOLD
#
# Trade setup:
#     Approved when R:R >= 1.5; calculated levels remain visible below 1.5
#
# ============================================================



def build_v7_explanation(
    action, confidence, score, bullish_factors, bearish_factors,
    rsi, close, ema20, ema50, macd, macd_signal,
    market_regime, market_structure_info, smc_info,
    support_resistance_info, pattern_info, risk_reward, setup_available,
):
    """Build a human-readable V7.1 explanation without changing the decision engine."""
    def sig(value):
        return str(value or "HOLD").upper()

    structure_signal = sig((market_structure_info or {}).get("signal"))
    structure_conf = float((market_structure_info or {}).get("confidence") or 0)
    smc_signal = sig((smc_info or {}).get("signal"))
    smc_conf = float((smc_info or {}).get("confidence") or 0)
    pattern_signal = sig((pattern_info or {}).get("signal"))
    pattern_name = (pattern_info or {}).get("pattern") or "No Strong Pattern"
    support = (support_resistance_info or {}).get("nearest_support")
    resistance = (support_resistance_info or {}).get("nearest_resistance")

    technical = []
    if rsi >= 60:
        technical.append(f"RSI is bullish at {rsi:.2f}")
    elif rsi <= 40:
        technical.append(f"RSI is bearish at {rsi:.2f}")
    else:
        technical.append(f"RSI is neutral at {rsi:.2f}")
    if abs(close - ema20) <= 0.005:
        technical.append(f"Price ({close:.2f}) is approximately equal to EMA20 ({ema20:.2f})")
    elif close > ema20:
        technical.append(f"Price ({close:.2f}) is above EMA20 ({ema20:.2f})")
    else:
        technical.append(f"Price ({close:.2f}) is below EMA20 ({ema20:.2f})")
    if abs(ema20 - ema50) <= 0.005:
        technical.append(f"EMA20 ({ema20:.2f}) is approximately equal to EMA50 ({ema50:.2f})")
    elif ema20 > ema50:
        technical.append(f"EMA20 ({ema20:.2f}) is above EMA50 ({ema50:.2f})")
    else:
        technical.append(f"EMA20 ({ema20:.2f}) is below EMA50 ({ema50:.2f})")
    if abs(macd - macd_signal) <= 0.005:
        technical.append(f"MACD ({macd:.2f}) is approximately equal to signal ({macd_signal:.2f})")
    elif macd > macd_signal:
        technical.append(f"MACD ({macd:.2f}) is above signal ({macd_signal:.2f})")
    else:
        technical.append(f"MACD ({macd:.2f}) is below signal ({macd_signal:.2f})")

    conflict = structure_signal in ("BUY", "SELL") and smc_signal in ("BUY", "SELL") and structure_signal != smc_signal
    if action == "BUY":
        primary = "BUY — Bullish evidence is stronger across the highest-priority signals."
    elif action == "SELL":
        primary = "SELL — Bearish evidence is stronger across the highest-priority signals."
    else:
        if conflict:
            primary = "HOLD — Major signals conflict, so MarketIQ is avoiding a forced directional trade."
        elif structure_signal == "SELL" and smc_signal == "HOLD":
            primary = "HOLD — Bearish pressure exists, but confirmation is incomplete."
        elif structure_signal == "BUY" and smc_signal == "HOLD":
            primary = "HOLD — Bullish pressure exists, but confirmation is incomplete."
        else:
            primary = "HOLD — The available evidence is not strong enough for a confirmed directional trade."

    why_parts = []
    if structure_signal in ("BUY", "SELL") and structure_conf > 0:
        why_parts.append(f"market structure favors {structure_signal} ({structure_conf:.0f}% confidence)")
    if market_regime in ("BULLISH", "BEARISH"):
        why_parts.append(f"the market regime is {market_regime}")
    why_parts.append("technical trend/momentum is " + ("bearish" if close < ema20 and ema20 < ema50 and macd < macd_signal else "bullish" if close > ema20 and ema20 > ema50 and macd > macd_signal else "mixed"))
    if smc_signal in ("BUY", "SELL"):
        why_parts.append(f"SMC leans {smc_signal} ({smc_conf:.0f}% confidence)")
    elif smc_signal == "HOLD":
        why_parts.append(f"SMC is neutral ({smc_conf:.0f}% confidence)")
    if support is not None and close > 0:
        dist = abs(close - float(support)) / close * 100
        if dist <= 3:
            why_parts.append(f"price is near support ({float(support):.2f})")
    explanation = primary + " " + "; ".join(why_parts) + "."

    risk_explanation = ""
    if action in ("BUY", "SELL") and risk_reward is not None and risk_reward < 1.5:
        risk_explanation = f"{action} direction is detected, but the trade is not approved because risk/reward is only 1:{risk_reward:.2f}, below the required 1:1.50."
    elif action in ("BUY", "SELL") and setup_available:
        risk_explanation = f"Trade setup is approved with risk/reward of 1:{risk_reward:.2f}." if risk_reward is not None else "Trade setup is approved."
    else:
        risk_explanation = "No directional trade setup is approved."

    return {
        "version": "V7.1",
        "primary": primary,
        "explanation": explanation,
        "signal_hierarchy": [
            {"priority": 1, "name": "Market Structure", "signal": structure_signal, "confidence": round(structure_conf, 2)},
            {"priority": 2, "name": "Technical Trend & Momentum", "signal": "BEARISH" if close < ema20 and ema20 < ema50 and macd < macd_signal else "BULLISH" if close > ema20 and ema20 > ema50 and macd > macd_signal else "MIXED", "confidence": None},
            {"priority": 3, "name": "Smart Money Concepts", "signal": smc_signal, "confidence": round(smc_conf, 2)},
            {"priority": 4, "name": "Support & Resistance", "signal": "SUPPORT_NEAR" if support is not None and abs(close-float(support))/close*100 <= 3 else "NEUTRAL", "confidence": None},
            {"priority": 5, "name": "Candlestick", "signal": pattern_signal, "confidence": round(float((pattern_info or {}).get("confidence") or 0), 2), "pattern": pattern_name},
        ],
        "conflict": conflict,
        "bullish_factors": int(bullish_factors),
        "bearish_factors": int(bearish_factors),
        "risk_explanation": risk_explanation,
        "technical_evidence": technical,
    }

def generate_recommendation(
    indicators,
    pattern=None,
    market_structure=None,
    support_resistance=None,
    smc=None,
):
    """
    MarketIQ multi-factor recommendation engine.

    Final decision combines technical indicators,
    candlestick patterns, market structure,
    support/resistance and price-aware Smart Money Concepts.
    """

    # ============================================================
    # INITIALIZATION
    # ============================================================

    score = 0

    reasons = []

    bullish_factors = 0
    bearish_factors = 0

    # Risk/reward is referenced by V6 confidence calibration before the
    # trade-setup calculation. Initialize it here so every execution path
    # has a defined value. The actual R:R calculation later remains unchanged.
    risk_reward = None

    # ============================================================
    # SAFE HELPERS
    # ============================================================

    def safe_float(
        value: Any,
        default: float = 0.0,
    ) -> float:

        try:

            if value is None:
                return default

            number = float(value)

            if number != number:
                return default

            return number

        except (TypeError, ValueError):

            return default

    def safe_bool(value: Any) -> bool:

        if isinstance(value, bool):
            return value

        if isinstance(value, str):

            return value.strip().lower() in (
                "true",
                "1",
                "yes",
                "y",
            )

        return bool(value)

    def clean_signal(value: Any) -> str:

        if value is None:
            return "HOLD"

        return str(value).strip().upper()

    def clean_text(
        value: Any,
        default: str,
    ) -> str:

        if value is None:
            return default

        return str(value)

    # ============================================================
    # PRICE DISTANCE HELPERS
    # ============================================================

    def percentage_distance(
        price_a: float,
        price_b: float,
    ) -> float:

        if price_a <= 0 or price_b <= 0:
            return 999.0

        return (
            abs(price_a - price_b)
            / price_a
        ) * 100.0

    def zone_distance_percent(
        price: float,
        low: float,
        high: float,
    ) -> float:

        """
        Returns distance from current price to a zone.

        If price is inside the zone:
            distance = 0

        Otherwise:
            distance = percentage distance
            from nearest zone boundary.
        """

        if (
            price <= 0
            or low <= 0
            or high <= 0
        ):

            return 999.0

        if low > high:

            low, high = high, low

        if low <= price <= high:

            return 0.0

        if price < low:

            return (
                (low - price)
                / price
            ) * 100.0

        return (
            (price - high)
            / price
        ) * 100.0

    def is_near_zone(
        price: float,
        low: float,
        high: float,
        threshold: float = 2.0,
    ) -> bool:

        return (
            zone_distance_percent(
                price,
                low,
                high,
            )
            <= threshold
        )

    # ============================================================
    # SAFE INPUTS
    # ============================================================

    indicators = indicators or {}

    rsi = safe_float(
        indicators.get("RSI"),
        50,
    )

    close = safe_float(
        indicators.get("Close"),
        0,
    )

    ema20 = safe_float(
        indicators.get("EMA20"),
        close,
    )

    ema50 = safe_float(
        indicators.get("EMA50"),
        close,
    )

    macd = safe_float(
        indicators.get("MACD"),
        0,
    )

    macd_signal = safe_float(
        indicators.get("MACD_SIGNAL"),
        0,
    )

    macd_bullish_crossover = safe_bool(
        indicators.get(
            "MACD_BULLISH_CROSSOVER",
            False,
        )
    )

    macd_bearish_crossover = safe_bool(
        indicators.get(
            "MACD_BEARISH_CROSSOVER",
            False,
        )
    )

    # ============================================================
    # INTERNAL SCORE HELPERS
    # ============================================================

    def add_bullish(
        points: int,
        reason: str,
        factor_weight: int = 1,
    ):

        nonlocal score
        nonlocal bullish_factors

        score += points
        bullish_factors += factor_weight

        reasons.append(reason)

    def add_bearish(
        points: int,
        reason: str,
        factor_weight: int = 1,
    ):

        nonlocal score
        nonlocal bearish_factors

        score -= points
        bearish_factors += factor_weight

        reasons.append(reason)

    # ============================================================
    # 1. RSI
    # ============================================================

    if rsi >= 60:

        add_bullish(
            1,
            f"RSI is bullish at {rsi:.2f}",
        )

    elif rsi <= 40:

        add_bearish(
            1,
            f"RSI is bearish at {rsi:.2f}",
        )

    else:

        reasons.append(
            f"RSI is neutral at {rsi:.2f}"
        )

    # ============================================================
    # 2. PRICE VS EMA20
    # ============================================================

    if close > 0 and ema20 > 0:

        if close > ema20:

            add_bullish(
                1,
                f"Price ({close:.2f}) is above "
                f"EMA20 ({ema20:.2f})",
            )

        elif close < ema20:

            add_bearish(
                1,
                f"Price ({close:.2f}) is below "
                f"EMA20 ({ema20:.2f})",
            )

        else:

            reasons.append(
                "Price is exactly at EMA20"
            )

    # ============================================================
    # 3. EMA20 VS EMA50
    # ============================================================

    if ema20 > ema50:

        add_bullish(
            2,
            f"EMA20 ({ema20:.2f}) is above "
            f"EMA50 ({ema50:.2f}), indicating "
            f"short-term momentum is stronger than the medium-term average",
        )

    elif ema20 < ema50:

        add_bearish(
            2,
            f"EMA20 ({ema20:.2f}) is below "
            f"EMA50 ({ema50:.2f}), indicating "
            f"short-term momentum is weaker than the medium-term average",
        )

    else:

        reasons.append(
            "EMA20 and EMA50 are equal"
        )

    # ============================================================
    # 4. MACD
    # ============================================================

    if macd_bullish_crossover:

        add_bullish(
            2,
            "MACD bullish crossover confirmed",
        )

    elif macd_bearish_crossover:

        add_bearish(
            2,
            "MACD bearish crossover confirmed",
        )

    elif macd > macd_signal:

        add_bullish(
            1,
            f"MACD ({macd:.2f}) is above "
            f"signal ({macd_signal:.2f}), "
            f"showing bullish momentum",
        )

    elif macd < macd_signal:

        add_bearish(
            1,
            f"MACD ({macd:.2f}) is below "
            f"signal ({macd_signal:.2f}), "
            f"showing bearish momentum",
        )

    else:

        reasons.append(
            "MACD is neutral"
        )

    # ============================================================
    # 5. CANDLESTICK PATTERN
    # ============================================================

    pattern_info = None

    pattern_signal = "HOLD"

    pattern_confidence = 0.0

    if pattern:

        pattern_name = clean_text(
            pattern.get(
                "pattern",
                "Unknown",
            ),
            "Unknown",
        )

        pattern_signal = clean_signal(
            pattern.get(
                "signal",
                "HOLD",
            )
        )

        pattern_confidence = safe_float(
            pattern.get(
                "confidence",
                0,
            ),
            0,
        )

        pattern_info = {
            "pattern": pattern_name,
            "signal": pattern_signal,
            "confidence": round(
                pattern_confidence,
                2,
            ),
        }

        # --------------------------------------------------------
        # Strong BUY pattern
        # --------------------------------------------------------

        if (
            pattern_signal == "BUY"
            and pattern_confidence >= 75
        ):

            pattern_points = 3

            if pattern_confidence >= 90:
                pattern_points = 4

            add_bullish(
                pattern_points,
                f"{pattern_name} supports BUY "
                f"({pattern_confidence:.0f}% confidence)",
            )

        # --------------------------------------------------------
        # Strong SELL pattern
        # --------------------------------------------------------

        elif (
            pattern_signal == "SELL"
            and pattern_confidence >= 75
        ):

            pattern_points = 3

            if pattern_confidence >= 90:
                pattern_points = 4

            add_bearish(
                pattern_points,
                f"{pattern_name} supports SELL "
                f"({pattern_confidence:.0f}% confidence)",
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
    # ============================================================

    market_structure_info = None

    structure_signal = "HOLD"

    structure_confidence = 0.0

    if market_structure:

        structure = clean_text(
            market_structure.get(
                "structure",
                "Neutral",
            ),
            "Neutral",
        )

        trend = clean_text(
            market_structure.get(
                "trend",
                "NEUTRAL",
            ),
            "NEUTRAL",
        )

        structure_signal = clean_signal(
            market_structure.get(
                "signal",
                "HOLD",
            )
        )

        structure_confidence = safe_float(
            market_structure.get(
                "confidence",
                0,
            ),
            0,
        )

        market_structure_info = {
            "structure": structure,
            "trend": trend,
            "signal": structure_signal,
            "confidence": round(
                structure_confidence,
                2,
            ),
        }

        if (
            structure_signal == "BUY"
            and structure_confidence >= 60
        ):

            structure_points = 3

            if structure_confidence >= 75:
                structure_points = 4

            add_bullish(
                structure_points,
                f"Market structure is bullish "
                f"({structure_confidence:.0f}% confidence)",
            )

        elif (
            structure_signal == "SELL"
            and structure_confidence >= 60
        ):

            structure_points = 3

            if structure_confidence >= 75:
                structure_points = 4

            add_bearish(
                structure_points,
                f"Market structure is bearish "
                f"({structure_confidence:.0f}% confidence)",
            )

        else:

            reasons.append(
                "Market structure is neutral"
            )

    # ============================================================
    # 7. SUPPORT / RESISTANCE
    # ============================================================

    support_resistance_info = None

    nearest_support = None
    nearest_resistance = None

    clean_supports = []
    clean_resistances = []

    support_near = False
    resistance_near = False

    if support_resistance and close > 0:

        supports = (
            support_resistance.get(
                "support",
                [],
            )
            or []
        )

        resistances = (
            support_resistance.get(
                "resistance",
                [],
            )
            or []
        )

        for level in supports:

            try:

                value = float(level)

                if value > 0:
                    clean_supports.append(value)

            except (TypeError, ValueError):

                continue

        for level in resistances:

            try:

                value = float(level)

                if value > 0:
                    clean_resistances.append(value)

            except (TypeError, ValueError):

                continue

        # --------------------------------------------------------
        # Support must be below current price.
        # Resistance must be above current price.
        # --------------------------------------------------------

        below_supports = [
            level
            for level in clean_supports
            if level < close
        ]

        above_resistances = [
            level
            for level in clean_resistances
            if level > close
        ]

        if below_supports:

            nearest_support = max(
                below_supports
            )

        if above_resistances:

            nearest_resistance = min(
                above_resistances
            )

        support_distance_percent = None
        resistance_distance_percent = None

        # --------------------------------------------------------
        # Support proximity
        # --------------------------------------------------------

        if nearest_support is not None:

            support_distance_percent = (
                (
                    close
                    - nearest_support
                )
                / close
            ) * 100

            if support_distance_percent <= 2:

                support_near = True

                add_bullish(
                    1,
                    f"Price is near support "
                    f"({nearest_support:.2f})",
                )

        # --------------------------------------------------------
        # Resistance proximity
        # --------------------------------------------------------

        if nearest_resistance is not None:

            resistance_distance_percent = (
                (
                    nearest_resistance
                    - close
                )
                / close
            ) * 100

            if resistance_distance_percent <= 2:

                resistance_near = True

                add_bearish(
                    1,
                    f"Price is near resistance "
                    f"({nearest_resistance:.2f})",
                )

        if (
            not support_near
            and not resistance_near
        ):

            reasons.append(
                "Price is not near a major "
                "detected support or resistance level"
            )

        # --------------------------------------------------------
        # Support / resistance information
        # --------------------------------------------------------

        support_resistance_info = {

            "nearest_support": (
                round(
                    nearest_support,
                    2,
                )
                if nearest_support is not None
                else None
            ),

            "nearest_resistance": (
                round(
                    nearest_resistance,
                    2,
                )
                if nearest_resistance is not None
                else None
            ),

            "support_distance_percent": (
                round(
                    support_distance_percent,
                    2,
                )
                if support_distance_percent is not None
                else None
            ),

            "resistance_distance_percent": (
                round(
                    resistance_distance_percent,
                    2,
                )
                if resistance_distance_percent is not None
                else None
            ),

            "support_near": support_near,

            "resistance_near": resistance_near,
        }

        # --------------------------------------------------------
        # Additional context
        # --------------------------------------------------------

        if support_near:

            reasons.append(
                f"Price is near support "
                f"({nearest_support:.2f}) "
                f"with supportive technical conditions"
            )

        elif resistance_near:

            reasons.append(
                f"Price is near resistance "
                f"({nearest_resistance:.2f}) "
                f"with opposing technical conditions"
            )

    # ============================================================
    # 8. SMART MONEY CONCEPTS
    # ============================================================
    #
    # PRICE-AWARE SMC
    #
    # The previous implementation counted the existence of
    # historical OB/FVG zones equally.
    #
    # That creates problems such as:
    #
    # Current price = 2302
    #
    # Bullish OB:
    #     2064 - 2133  -> historical / far
    #
    # Bullish OB:
    #     2326 - 2391  -> close to current price
    #
    # These should NOT have equal influence.
    #
    # The new implementation:
    #
    # 1. Checks whether a zone is near current price.
    # 2. Checks whether price is inside a zone.
    # 3. Gives stronger weight to relevant zones.
    # 4. Does not count every historical zone.
    # 5. Treats liquidity primarily as context.
    # 6. Keeps BOS / CHoCH as stronger structural signals.
    #
    # ============================================================

    smc_info = None

    smc_signal = "HOLD"

    smc_confidence = 0.0

    smc_score = 0

    smc_bullish_score = 0

    smc_bearish_score = 0

    smc_bos = None
    smc_choch = None
    smc_order_blocks = {}
    smc_liquidity = {}
    smc_fvg = {}

    # Price-aware SMC variables
    nearby_bullish_ob = []
    nearby_bearish_ob = []

    nearby_bullish_fvg = []
    nearby_bearish_fvg = []

    nearby_buy_liquidity = []
    nearby_sell_liquidity = []

    bullish_ob_relevant = False
    bearish_ob_relevant = False

    bullish_fvg_relevant = False
    bearish_fvg_relevant = False

    buy_liquidity_relevant = False
    sell_liquidity_relevant = False

    if smc and isinstance(smc, dict):

        smc_signal = clean_signal(
            smc.get(
                "signal",
                "HOLD",
            )
        )

        smc_confidence = safe_float(
            smc.get(
                "confidence",
                0,
            ),
            0,
        )

        smc_score = safe_float(
            smc.get(
                "score",
                0,
            ),
            0,
        )

        smc_bullish_score = safe_float(
            smc.get(
                "bullish_score",
                0,
            ),
            0,
        )

        smc_bearish_score = safe_float(
            smc.get(
                "bearish_score",
                0,
            ),
            0,
        )

        smc_bos = smc.get(
            "break_of_structure",
            {},
        ) or {}

        smc_choch = smc.get(
            "change_of_character",
            {},
        ) or {}

        smc_order_blocks = smc.get(
            "order_blocks",
            {},
        ) or {}

        smc_liquidity = smc.get(
            "liquidity",
            {},
        ) or {}

        smc_fvg = smc.get(
            "fair_value_gaps",
            {},
        ) or {}

        smc_info = {
            "signal": smc_signal,
            "confidence": round(
                smc_confidence,
                2,
            ),
            "score": round(
                smc_score,
                2,
            ),
            "bullish_score": round(
                smc_bullish_score,
                2,
            ),
            "bearish_score": round(
                smc_bearish_score,
                2,
            ),
            "break_of_structure": smc_bos,
            "change_of_character": smc_choch,
            "order_blocks": smc_order_blocks,
            "liquidity": smc_liquidity,
            "fair_value_gaps": smc_fvg,
        }

        # ========================================================
        # BOS
        # ========================================================

        bos_detected = safe_bool(
            smc_bos.get(
                "detected",
                False,
            )
        )

        bos_type = clean_signal(
            smc_bos.get(
                "type",
                "",
            )
        )

        if bos_detected:

            if bos_type in (
                "BULLISH",
                "BULLISH_BOS",
                "BUY",
            ):

                add_bullish(
                    3,
                    "Bullish Break of Structure (BOS) detected by SMC",
                )

            elif bos_type in (
                "BEARISH",
                "BEARISH_BOS",
                "SELL",
            ):

                add_bearish(
                    3,
                    "Bearish Break of Structure (BOS) detected by SMC",
                )

            else:

                if smc_signal == "BUY":

                    add_bullish(
                        2,
                        "SMC Break of Structure supports bullish bias",
                    )

                elif smc_signal == "SELL":

                    add_bearish(
                        2,
                        "SMC Break of Structure supports bearish bias",
                    )

        else:

            reasons.append(
                "No recent Break of Structure detected"
            )

        # ========================================================
        # CHoCH
        # ========================================================

        choch_detected = safe_bool(
            smc_choch.get(
                "detected",
                False,
            )
        )

        choch_type = clean_signal(
            smc_choch.get(
                "type",
                "",
            )
        )

        if choch_detected:

            if choch_type in (
                "BULLISH",
                "BULLISH_CHOCH",
                "BUY",
            ):

                add_bullish(
                    2,
                    "Bullish Change of Character (CHoCH) detected",
                )

            elif choch_type in (
                "BEARISH",
                "BEARISH_CHOCH",
                "SELL",
            ):

                add_bearish(
                    2,
                    "Bearish Change of Character (CHoCH) detected",
                )

            else:

                if smc_signal == "BUY":

                    add_bullish(
                        1,
                        "SMC Change of Character supports bullish bias",
                    )

                elif smc_signal == "SELL":

                    add_bearish(
                        1,
                        "SMC Change of Character supports bearish bias",
                    )

        else:

            reasons.append(
                "No clear Change of Character detected"
            )

        # ========================================================
        # ORDER BLOCKS - PRICE AWARE
        # ========================================================

        bullish_order_blocks = (
            smc_order_blocks.get(
                "bullish",
                [],
            )
            or []
        )

        bearish_order_blocks = (
            smc_order_blocks.get(
                "bearish",
                [],
            )
            or []
        )

        # --------------------------------------------------------
        # Only inspect valid dictionary zones.
        # --------------------------------------------------------

        if close > 0:

            for block in bullish_order_blocks:

                if not isinstance(block, dict):
                    continue

                block_low = safe_float(
                    block.get(
                        "low",
                        block.get(
                            "price",
                            0,
                        ),
                    ),
                    0,
                )

                block_high = safe_float(
                    block.get(
                        "high",
                        block.get(
                            "price",
                            0,
                        ),
                    ),
                    0,
                )

                if block_low <= 0:

                    continue

                if block_high <= 0:

                    block_high = block_low

                distance = zone_distance_percent(
                    close,
                    block_low,
                    block_high,
                )

                # Only current / nearby zones matter.
                if distance <= 3:

                    nearby_bullish_ob.append(
                        {
                            "zone": block,
                            "distance_percent": round(
                                distance,
                                2,
                            ),
                        }
                    )

            for block in bearish_order_blocks:

                if not isinstance(block, dict):
                    continue

                block_low = safe_float(
                    block.get(
                        "low",
                        block.get(
                            "price",
                            0,
                        ),
                    ),
                    0,
                )

                block_high = safe_float(
                    block.get(
                        "high",
                        block.get(
                            "price",
                            0,
                        ),
                    ),
                    0,
                )

                if block_high <= 0:

                    continue

                if block_low <= 0:

                    block_low = block_high

                distance = zone_distance_percent(
                    close,
                    block_low,
                    block_high,
                )

                if distance <= 3:

                    nearby_bearish_ob.append(
                        {
                            "zone": block,
                            "distance_percent": round(
                                distance,
                                2,
                            ),
                        }
                    )

        # --------------------------------------------------------
        # Relevant bullish OB
        # --------------------------------------------------------

        if nearby_bullish_ob:

            bullish_ob_relevant = True

            closest_bullish_ob = min(
                nearby_bullish_ob,
                key=lambda x: x[
                    "distance_percent"
                ],
            )

            bullish_ob_distance = (
                closest_bullish_ob[
                    "distance_percent"
                ]
            )

            if bullish_ob_distance == 0:

                add_bullish(
                    2,
                    "Price is inside a bullish order block",
                )

            else:

                add_bullish(
                    1,
                    "Bullish order block is near current price",
                )

        # --------------------------------------------------------
        # Relevant bearish OB
        # --------------------------------------------------------

        if nearby_bearish_ob:

            bearish_ob_relevant = True

            closest_bearish_ob = min(
                nearby_bearish_ob,
                key=lambda x: x[
                    "distance_percent"
                ],
            )

            bearish_ob_distance = (
                closest_bearish_ob[
                    "distance_percent"
                ]
            )

            if bearish_ob_distance == 0:

                add_bearish(
                    2,
                    "Price is inside a bearish order block",
                )

            else:

                add_bearish(
                    1,
                    "Bearish order block is near current price",
                )

        # --------------------------------------------------------
        # No nearby OB
        # --------------------------------------------------------

        if (
            not bullish_ob_relevant
            and not bearish_ob_relevant
        ):

            reasons.append(
                "No nearby order block around current price"
            )

        else:

            if bullish_ob_relevant:

                reasons.append(
                    f"{len(nearby_bullish_ob)} "
                    f"relevant bullish order block zone(s) "
                    f"near current price"
                )

            if bearish_ob_relevant:

                reasons.append(
                    f"{len(nearby_bearish_ob)} "
                    f"relevant bearish order block zone(s) "
                    f"near current price"
                )

        # ========================================================
        # LIQUIDITY - PRICE AWARE / CONTEXTUAL
        # ========================================================

        buy_side_liquidity = (
            smc_liquidity.get(
                "buy_side",
                [],
            )
            or []
        )

        sell_side_liquidity = (
            smc_liquidity.get(
                "sell_side",
                [],
            )
            or []
        )

        if close > 0:

            for liquidity in buy_side_liquidity:

                if not isinstance(
                    liquidity,
                    dict,
                ):

                    continue

                liquidity_price = safe_float(
                    liquidity.get(
                        "price",
                        0,
                    ),
                    0,
                )

                if liquidity_price <= 0:
                    continue

                distance = percentage_distance(
                    close,
                    liquidity_price,
                )

                if distance <= 5:

                    nearby_buy_liquidity.append(
                        {
                            "zone": liquidity,
                            "distance_percent": round(
                                distance,
                                2,
                            ),
                        }
                    )

            for liquidity in sell_side_liquidity:

                if not isinstance(
                    liquidity,
                    dict,
                ):

                    continue

                liquidity_price = safe_float(
                    liquidity.get(
                        "price",
                        0,
                    ),
                    0,
                )

                if liquidity_price <= 0:
                    continue

                distance = percentage_distance(
                    close,
                    liquidity_price,
                )

                if distance <= 5:

                    nearby_sell_liquidity.append(
                        {
                            "zone": liquidity,
                            "distance_percent": round(
                                distance,
                                2,
                            ),
                        }
                    )

        if nearby_buy_liquidity:

            buy_liquidity_relevant = True

            closest_buy_liquidity = min(
                nearby_buy_liquidity,
                key=lambda x: x[
                    "distance_percent"
                ],
            )

            reasons.append(
                "Buy-side liquidity is nearby "
                f"({closest_buy_liquidity['distance_percent']:.2f}% away)"
            )

        if nearby_sell_liquidity:

            sell_liquidity_relevant = True

            closest_sell_liquidity = min(
                nearby_sell_liquidity,
                key=lambda x: x[
                    "distance_percent"
                ],
            )

            reasons.append(
                "Sell-side liquidity is nearby "
                f"({closest_sell_liquidity['distance_percent']:.2f}% away)"
            )

        if (
            not buy_liquidity_relevant
            and not sell_liquidity_relevant
        ):

            reasons.append(
                "No major liquidity zone is close "
                "to current price"
            )

        # Liquidity remains contextual.
        #
        # We deliberately DO NOT automatically add BUY/SELL
        # score merely because liquidity exists.
        #
        # This prevents:
        #
        # BUY-side liquidity = automatic BUY
        # SELL-side liquidity = automatic SELL
        #
        # which would be incorrect.

        # ========================================================
        # FAIR VALUE GAPS - PRICE AWARE
        # ========================================================

        bullish_fvg = (
            smc_fvg.get(
                "bullish",
                [],
            )
            or []
        )

        bearish_fvg = (
            smc_fvg.get(
                "bearish",
                [],
            )
            or []
        )

        if close > 0:

            for gap in bullish_fvg:

                if not isinstance(gap, dict):
                    continue

                gap_low = safe_float(
                    gap.get(
                        "low",
                        0,
                    ),
                    0,
                )

                gap_high = safe_float(
                    gap.get(
                        "high",
                        0,
                    ),
                    0,
                )

                if (
                    gap_low <= 0
                    or gap_high <= 0
                ):

                    continue

                distance = zone_distance_percent(
                    close,
                    gap_low,
                    gap_high,
                )

                if distance <= 3:

                    nearby_bullish_fvg.append(
                        {
                            "zone": gap,
                            "distance_percent": round(
                                distance,
                                2,
                            ),
                        }
                    )

            for gap in bearish_fvg:

                if not isinstance(gap, dict):
                    continue

                gap_low = safe_float(
                    gap.get(
                        "low",
                        0,
                    ),
                    0,
                )

                gap_high = safe_float(
                    gap.get(
                        "high",
                        0,
                    ),
                    0,
                )

                if (
                    gap_low <= 0
                    or gap_high <= 0
                ):

                    continue

                distance = zone_distance_percent(
                    close,
                    gap_low,
                    gap_high,
                )

                if distance <= 3:

                    nearby_bearish_fvg.append(
                        {
                            "zone": gap,
                            "distance_percent": round(
                                distance,
                                2,
                            ),
                        }
                    )

        # --------------------------------------------------------
        # Relevant bullish FVG
        # --------------------------------------------------------

        if nearby_bullish_fvg:

            bullish_fvg_relevant = True

            closest_bullish_fvg = min(
                nearby_bullish_fvg,
                key=lambda x: x[
                    "distance_percent"
                ],
            )

            bullish_fvg_distance = (
                closest_bullish_fvg[
                    "distance_percent"
                ]
            )

            if bullish_fvg_distance == 0:

                add_bullish(
                    1,
                    "Price is inside a bullish Fair Value Gap",
                )

            else:

                add_bullish(
                    1,
                    "Bullish Fair Value Gap is near current price",
                )

        # --------------------------------------------------------
        # Relevant bearish FVG
        # --------------------------------------------------------

        if nearby_bearish_fvg:

            bearish_fvg_relevant = True

            closest_bearish_fvg = min(
                nearby_bearish_fvg,
                key=lambda x: x[
                    "distance_percent"
                ],
            )

            bearish_fvg_distance = (
                closest_bearish_fvg[
                    "distance_percent"
                ]
            )

            if bearish_fvg_distance == 0:

                add_bearish(
                    1,
                    "Price is inside a bearish Fair Value Gap",
                )

            else:

                add_bearish(
                    1,
                    "Bearish Fair Value Gap is near current price",
                )

        if (
            not bullish_fvg_relevant
            and not bearish_fvg_relevant
        ):

            reasons.append(
                "No significant Fair Value Gap near current price"
            )

        else:

            if bullish_fvg_relevant:

                reasons.append(
                    f"{len(nearby_bullish_fvg)} "
                    f"relevant bullish FVG(s) near current price"
                )

            if bearish_fvg_relevant:

                reasons.append(
                    f"{len(nearby_bearish_fvg)} "
                    f"relevant bearish FVG(s) near current price"
                )

        # ========================================================
        # SMC OVERALL SIGNAL
        # ========================================================

        if smc_signal == "BUY":

            reasons.append(
                f"SMC overall signal is BUY "
                f"({smc_confidence:.0f}% confidence)"
            )

        elif smc_signal == "SELL":

            reasons.append(
                f"SMC overall signal is SELL "
                f"({smc_confidence:.0f}% confidence)"
            )

        else:

            reasons.append(
                f"SMC overall signal is HOLD "
                f"({smc_confidence:.0f}% confidence)"
            )

        # ========================================================
        # PRICE-AWARE SMC SUMMARY
        # ========================================================

        if bullish_ob_relevant:

            reasons.append(
                "SMC has bullish order-block support near price"
            )

        if bearish_ob_relevant:

            reasons.append(
                "SMC has bearish order-block resistance near price"
            )

        if bullish_fvg_relevant:

            reasons.append(
                "SMC has bullish imbalance support near price"
            )

        if bearish_fvg_relevant:

            reasons.append(
                "SMC has bearish imbalance resistance near price"
            )

        # --------------------------------------------------------
        # Update returned SMC analysis with contextual information.
        # --------------------------------------------------------

        smc_info["price_context"] = {

            "current_price": (
                round(close, 2)
                if close > 0
                else None
            ),

            "nearby_bullish_order_blocks": (
                len(nearby_bullish_ob)
            ),

            "nearby_bearish_order_blocks": (
                len(nearby_bearish_ob)
            ),

            "nearby_bullish_fvg": (
                len(nearby_bullish_fvg)
            ),

            "nearby_bearish_fvg": (
                len(nearby_bearish_fvg)
            ),

            "nearby_buy_side_liquidity": (
                len(nearby_buy_liquidity)
            ),

            "nearby_sell_side_liquidity": (
                len(nearby_sell_liquidity)
            ),

            "bullish_order_block_relevant": (
                bullish_ob_relevant
            ),

            "bearish_order_block_relevant": (
                bearish_ob_relevant
            ),

            "bullish_fvg_relevant": (
                bullish_fvg_relevant
            ),

            "bearish_fvg_relevant": (
                bearish_fvg_relevant
            ),
        }

    else:

        reasons.append(
            "SMC analysis is unavailable"
        )

    # ============================================================
    # SMC SETUP CONTEXT
    # ============================================================
    #
    # An SMC BUY/SELL signal is a directional bias. It is not
    # automatically a confirmed SMC trade setup.
    # ============================================================

    if smc_info is not None:
        smc_bullish_setup = safe_bool(
            smc.get("bullish_setup", False)
        )
        smc_bearish_setup = safe_bool(
            smc.get("bearish_setup", False)
        )

        if smc_signal == "BUY" and not smc_bullish_setup:
            reasons.append(
                "SMC has a bullish directional bias, but no confirmed SMC trade setup"
            )
        elif smc_signal == "SELL" and not smc_bearish_setup:
            reasons.append(
                "SMC has a bearish directional bias, but no confirmed SMC trade setup"
            )

    # ============================================================
    # 8B. EXTREME RSI EXHAUSTION ADJUSTMENT
    #
    # Keep the existing RSI scoring logic above, but add a correction
    # for extreme readings. An RSI below 30 can occur during a strong
    # downtrend, but it can also indicate that a bearish move is already
    # extended. Likewise, RSI above 70 can occur during a strong uptrend
    # but can also indicate an extended move.
    #
    # We therefore neutralize only the original one-point RSI contribution
    # at extreme levels. Other independent evidence remains untouched.
    # ============================================================

    if rsi < 30 and bearish_factors > 0:

        score += 1
        bearish_factors -= 1

        reasons.append(
            f"RSI is extremely oversold at {rsi:.2f}; "
            "its standalone bearish contribution is neutralized and "
            "direction now relies more on independent trend/structure evidence"
        )

    elif rsi > 70 and bullish_factors > 0:

        score -= 1
        bullish_factors -= 1

        reasons.append(
            f"RSI is extremely overbought at {rsi:.2f}; "
            "its standalone bullish contribution is neutralized and "
            "direction now relies more on independent trend/structure evidence"
        )

    # ============================================================
    # 8C. MOMENTUM REVERSAL / EXTENSION CALIBRATION
    #
    # Second calibration pass:
    # Extreme RSI by itself should not override a strong trend, but a
    # directional signal becomes less reliable when momentum is already
    # stretched and the faster momentum indicator is moving against it.
    #
    # This is intentionally additive. Existing scoring, SMC logic and
    # trade-setup calculations remain intact.
    # ============================================================

    # SELL exhaustion: oversold + MACD no longer confirms bearish momentum.
    if (
        rsi < 30
        and macd >= macd_signal
        and bearish_factors > 0
    ):

        score += 2
        bearish_factors -= 1

        reasons.append(
            f"Bearish momentum is being reduced because RSI is oversold at {rsi:.2f} "
            "while MACD is no longer below its signal; reversal risk is elevated"
        )

    # BUY exhaustion: overbought + MACD no longer confirms bullish momentum.
    elif (
        rsi > 70
        and macd <= macd_signal
        and bullish_factors > 0
    ):

        score -= 2
        bullish_factors -= 1

        reasons.append(
            f"Bullish momentum is being reduced because RSI is overbought at {rsi:.2f} "
            "while MACD is no longer above its signal; reversal risk is elevated"
        )

    # Strongly extended price moves receive an additional caution. We do
    # not force HOLD here; the existing confidence and setup validation
    # still decide whether the signal is actionable.
    if (
        close > 0
        and ema20 > 0
        and rsi < 35
        and close < ema20
    ):

        extension_percent = ((ema20 - close) / ema20) * 100

        if extension_percent >= 8:

            reasons.append(
                f"Price is extended {extension_percent:.2f}% below EMA20 with RSI {rsi:.2f}; "
                "downside continuation should require strong independent confirmation"
            )

    elif (
        close > 0
        and ema20 > 0
        and rsi > 65
        and close > ema20
    ):

        extension_percent = ((close - ema20) / ema20) * 100

        if extension_percent >= 8:

            reasons.append(
                f"Price is extended {extension_percent:.2f}% above EMA20 with RSI {rsi:.2f}; "
                "upside continuation should require strong independent confirmation"
            )

    # ============================================================
    # 8D. MARKET REGIME / COUNTER-TREND PROTECTION
    #
    # V2 separates directional strength from market regime. A strong
    # indicator score is not enough to justify a fresh counter-trend
    # trade. The regime is intentionally simple and explainable:
    #   bullish = price > EMA20 > EMA50
    #   bearish = price < EMA20 < EMA50
    #   mixed   = everything else
    #
    # Counter-trend signals are allowed only when independent structure
    # evidence is strong enough. This reduces BUY signals inside a
    # bearish regime and SELL signals inside a bullish regime without
    # changing normal trend-following signals.
    # ============================================================

    if (
        close > 0
        and ema20 > 0
        and ema50 > 0
    ):

        if close > ema20 and ema20 > ema50:
            market_regime = "BULLISH"

        elif close < ema20 and ema20 < ema50:
            market_regime = "BEARISH"

        else:
            market_regime = "MIXED"

    else:

        market_regime = "UNKNOWN"

    bullish_structure_confirmed_v2 = (
        structure_signal == "BUY"
        and structure_confidence >= 60
    )

    bearish_structure_confirmed_v2 = (
        structure_signal == "SELL"
        and structure_confidence >= 60
    )

    smc_bullish_setup_confirmed_v2 = (
        smc_signal == "BUY"
        and smc_confidence >= 70
        and safe_bool(
            smc.get("bullish_setup", False)
            if smc_info is not None
            else False
        )
    )

    smc_bearish_setup_confirmed_v2 = (
        smc_signal == "SELL"
        and smc_confidence >= 70
        and safe_bool(
            smc.get("bearish_setup", False)
            if smc_info is not None
            else False
        )
    )

    reasons.append(
        f"Market regime: {market_regime}"
    )

    # ============================================================
    # 9. MAJOR SIGNAL AGREEMENT
    # ============================================================

    major_bullish = 0
    major_bearish = 0

    # ------------------------------------------------------------
    # Candlestick
    # ------------------------------------------------------------

    if (
        pattern_signal == "BUY"
        and pattern_confidence >= 75
    ):

        major_bullish += 1

    elif (
        pattern_signal == "SELL"
        and pattern_confidence >= 75
    ):

        major_bearish += 1

    # ------------------------------------------------------------
    # Market structure
    # ------------------------------------------------------------

    if (
        structure_signal == "BUY"
        and structure_confidence >= 60
    ):

        major_bullish += 1

    elif (
        structure_signal == "SELL"
        and structure_confidence >= 60
    ):

        major_bearish += 1

    # ------------------------------------------------------------
    # EMA trend
    # ------------------------------------------------------------

    if ema20 > ema50:

        major_bullish += 1

    elif ema20 < ema50:

        major_bearish += 1

    # ------------------------------------------------------------
    # SMC
    # ------------------------------------------------------------

    if (
        smc_signal == "BUY"
        and smc_confidence >= 60
    ):

        major_bullish += 1

    elif (
        smc_signal == "SELL"
        and smc_confidence >= 60
    ):

        major_bearish += 1

    # ============================================================
    # PRICE-AWARE SMC MAJOR AGREEMENT
    # ============================================================
    #
    # Nearby SMC zones can support the major directional count,
    # but they do not replace BOS/CHoCH or the overall SMC signal.
    #
    # This prevents historical zones from dominating the decision.
    # ============================================================

    if bullish_ob_relevant and not bearish_ob_relevant:

        major_bullish += 1

    elif bearish_ob_relevant and not bullish_ob_relevant:

        major_bearish += 1

    # ============================================================
    # 9B. V5 WEIGHTED DECISION SCORE
    #
    # V5 corrects the decision layer instead of adding another post-hoc
    # HOLD filter. Raw indicator score remains useful, but trend and
    # market structure receive greater authority because they describe
    # the broader directional context. SMC is used as confirmation and
    # cannot override a conflicting trend/structure picture by confidence
    # alone.
    # ============================================================

    v5_raw_score = int(score)

    v5_trend_bias = 0.0
    if market_regime == "BULLISH":
        v5_trend_bias = 2.0
    elif market_regime == "BEARISH":
        v5_trend_bias = -2.0

    v5_structure_bias = 0.0
    if bullish_structure_confirmed_v2:
        v5_structure_bias = 3.0
    elif bearish_structure_confirmed_v2:
        v5_structure_bias = -3.0

    v5_smc_bias = 0.0
    if smc_bullish_setup_confirmed_v2:
        v5_smc_bias = 1.5
    elif smc_bearish_setup_confirmed_v2:
        v5_smc_bias = -1.5
    elif smc_signal == "BUY" and smc_confidence >= 60:
        v5_smc_bias = 0.5
    elif smc_signal == "SELL" and smc_confidence >= 60:
        v5_smc_bias = -0.5

    v5_ema_bias = 0.0
    if ema20 > ema50:
        v5_ema_bias = 1.0
    elif ema20 < ema50:
        v5_ema_bias = -1.0

    v5_pattern_bias = 0.0
    if pattern_signal == "BUY" and pattern_confidence >= 75:
        v5_pattern_bias = 0.5
    elif pattern_signal == "SELL" and pattern_confidence >= 75:
        v5_pattern_bias = -0.5

    # Dampen the raw score so repeated indicator evidence cannot dominate
    # the higher-level trend/structure context.
    v5_weighted_score = (
        (v5_raw_score * 0.55)
        + v5_trend_bias
        + v5_structure_bias
        + v5_smc_bias
        + v5_ema_bias
        + v5_pattern_bias
    )

    score = int(round(v5_weighted_score))
    score = max(-15, min(15, score))

    v5_direction_context = (
        f"V5 weighted decision: raw score {v5_raw_score}, "
        f"weighted score {score}; trend {market_regime}, "
        f"structure {structure_signal}, SMC {smc_signal}"
    )
    reasons.append(v5_direction_context)

    # ============================================================
    # 10. SCORE LIMIT
    # ============================================================

    score = int(
        max(
            -15,
            min(
                15,
                score,
            ),
        )
    )

    # ============================================================
    # 11. FINAL DIRECTION
    # ============================================================

    if (
        score >= 6
        or (
            score >= 5
            and major_bullish >= 3
            and major_bullish > major_bearish
        )
    ):

        action = "BUY"

    elif (
        score <= -6
        or (
            score <= -5
            and major_bearish >= 3
            and major_bearish > major_bullish
        )
    ):

        action = "SELL"

    else:

        action = "HOLD"

    # ============================================================
    # 11B. COUNTER-TREND DIRECTION FILTER
    # ============================================================

    if action == "BUY" and market_regime == "BEARISH":

        countertrend_buy_confirmed = (
            major_bullish >= 3
            and score >= 8
            and (
                bullish_structure_confirmed_v2
                or smc_bullish_setup_confirmed_v2
            )
        )

        if not countertrend_buy_confirmed:

            action = "HOLD"

            reasons.append(
                "BUY blocked by bearish market regime; a counter-trend BUY "
                "requires stronger independent structure confirmation"
            )

    elif action == "SELL" and market_regime == "BULLISH":

        countertrend_sell_confirmed = (
            major_bearish >= 3
            and score <= -8
            and (
                bearish_structure_confirmed_v2
                or smc_bearish_setup_confirmed_v2
            )
        )

        if not countertrend_sell_confirmed:

            action = "HOLD"

            reasons.append(
                "SELL blocked by bullish market regime; a counter-trend SELL "
                "requires stronger independent structure confirmation"
            )

    # ============================================================
    # 12. SIGNAL BALANCE
    # ============================================================

    factor_difference = abs(
        bullish_factors
        - bearish_factors
    )

    if (
        bullish_factors > 0
        and bearish_factors > 0
    ):

        if factor_difference <= 1:

            reasons.append(
                f"Signals are mixed "
                f"({bullish_factors} bullish vs "
                f"{bearish_factors} bearish factors)"
            )

            action = "HOLD"

        elif factor_difference == 2:

            reasons.append(
                f"Directional evidence is moderately "
                f"imbalanced "
                f"({bullish_factors} bullish vs "
                f"{bearish_factors} bearish factors)"
            )

    # ============================================================
    # 13. SMC CONFLICT PROTECTION
    # ============================================================
    #
    # If technicals strongly say BUY while SMC strongly says SELL,
    # do not blindly issue a directional trade.
    #
    # Same for SELL vs BUY.
    # ============================================================

    smc_strong_buy = (
        smc_signal == "BUY"
        and smc_confidence >= 70
    )

    smc_strong_sell = (
        smc_signal == "SELL"
        and smc_confidence >= 70
    )

    if action == "BUY" and smc_strong_sell:

        reasons.append(
            "Strong SMC bearish signal conflicts "
            "with the broader bullish evidence"
        )

        action = "HOLD"

    elif action == "SELL" and smc_strong_buy:

        reasons.append(
            "Strong SMC bullish signal conflicts "
            "with the broader bearish evidence"
        )

        action = "HOLD"

    # ============================================================
    # 14. CONFIDENCE
    # ============================================================

    absolute_score = abs(score)

    confidence_map = {
        0: 50,
        1: 50,
        2: 56,
        3: 62,
        4: 68,
        5: 73,
        6: 78,
        7: 82,
        8: 86,
        9: 89,
        10: 92,
        11: 94,
        12: 95,
        13: 96,
        14: 97,
        15: 98,
    }

    confidence = confidence_map.get(
        absolute_score,
        50,
    )

    # ------------------------------------------------------------
    # Mixed signal reduction
    # ------------------------------------------------------------

    if (
        bullish_factors > 0
        and bearish_factors > 0
    ):

        if factor_difference <= 1:

            confidence = min(
                confidence,
                55,
            )

        elif factor_difference == 2:

            confidence = min(
                confidence,
                68,
            )

    # ------------------------------------------------------------
    # SMC conflict reduces confidence
    # ------------------------------------------------------------

    if (
        action == "BUY"
        and smc_signal == "SELL"
    ):

        confidence = min(
            confidence,
            60,
        )

    elif (
        action == "SELL"
        and smc_signal == "BUY"
    ):

        confidence = min(
            confidence,
            60,
        )

    # ------------------------------------------------------------
    # HOLD confidence
    # ------------------------------------------------------------

    if action == "HOLD":

        confidence = min(
            confidence,
            65,
        )

    # ============================================================
    # 14B. DIRECTIONAL CONFIDENCE CALIBRATION
    #
    # Preserve the existing score-to-confidence mapping above. These
    # additional caps prevent a large raw score from being presented as
    # near-certain when the major independent components are not aligned.
    # Confidence is a MarketIQ strength score, not a literal probability.
    # ============================================================

    if action == "BUY":

        if major_bullish < 2:

            confidence = min(confidence, 73)

            reasons.append(
                f"Confidence calibrated because only {major_bullish} "
                "major independent bullish component(s) confirm the direction"
            )

        elif major_bullish < 3:

            confidence = min(confidence, 82)

            reasons.append(
                f"Confidence calibrated because only {major_bullish} "
                "major independent bullish component(s) confirm the direction"
            )

    elif action == "SELL":

        if major_bearish < 2:

            confidence = min(confidence, 73)

            reasons.append(
                f"Confidence calibrated because only {major_bearish} "
                "major independent bearish component(s) confirm the direction"
            )

        elif major_bearish < 3:

            confidence = min(confidence, 82)

            reasons.append(
                f"Confidence calibrated because only {major_bearish} "
                "major independent bearish component(s) confirm the direction"
            )

    # ------------------------------------------------------------
    # Extreme RSI confidence cap
    # ------------------------------------------------------------

    bullish_structure_confirmed = (
        structure_signal == "BUY"
        and structure_confidence >= 60
    )

    bearish_structure_confirmed = (
        structure_signal == "SELL"
        and structure_confidence >= 60
    )

    if action == "SELL" and rsi < 30:

        if not (bearish_structure_confirmed or smc_strong_sell):

            confidence = min(confidence, 68)

            reasons.append(
                f"Confidence capped because RSI is extremely oversold "
                f"at {rsi:.2f} without strong independent bearish structure/SMC confirmation"
            )

    elif action == "BUY" and rsi > 70:

        if not (bullish_structure_confirmed or smc_strong_buy):

            confidence = min(confidence, 68)

            reasons.append(
                f"Confidence capped because RSI is extremely overbought "
                f"at {rsi:.2f} without strong independent bullish structure/SMC confirmation"
            )

    # ============================================================
    # 14C. HIGH-CONFIDENCE CALIBRATION
    #
    # A 95-98 confidence value must represent broad agreement, not merely
    # a large raw score. Keep the existing mapping but prevent the highest
    # labels when fewer than four major components agree.
    # ============================================================

    if action == "BUY":

        if major_bullish < 4:

            confidence = min(confidence, 89)

            reasons.append(
                f"High-confidence ceiling applied: {major_bullish} major bullish "
                "components do not justify a near-certain confidence level"
            )

    elif action == "SELL":

        if major_bearish < 4:

            confidence = min(confidence, 89)

            reasons.append(
                f"High-confidence ceiling applied: {major_bearish} major bearish "
                "components do not justify a near-certain confidence level"
            )

    # ============================================================
    # 14D. V6 FINAL CONFIDENCE CALIBRATION
    #
    # V6 is the final calibration layer. It does not add another direction
    # filter. It fixes the remaining problem found in validation: a very
    # large score was sometimes displayed as 97-98% confidence even when
    # the independent confirmations were not strong enough to justify that
    # level. Confidence is therefore based on confirmation breadth, while
    # the V5 weighted score continues to determine direction.
    # ============================================================

    v6_confirmation_tier = 0

    if action == "BUY":
        if market_regime == "BULLISH":
            v6_confirmation_tier += 2
        elif market_regime == "MIXED":
            v6_confirmation_tier += 1

        if bullish_structure_confirmed_v2:
            v6_confirmation_tier += 2

        if smc_bullish_setup_confirmed_v2:
            v6_confirmation_tier += 2
        elif smc_signal == "BUY" and smc_confidence >= 60:
            v6_confirmation_tier += 1

        if ema20 > ema50:
            v6_confirmation_tier += 1

        if pattern_signal == "BUY" and pattern_confidence >= 75:
            v6_confirmation_tier += 1

    elif action == "SELL":
        if market_regime == "BEARISH":
            v6_confirmation_tier += 2
        elif market_regime == "MIXED":
            v6_confirmation_tier += 1

        if bearish_structure_confirmed_v2:
            v6_confirmation_tier += 2

        if smc_bearish_setup_confirmed_v2:
            v6_confirmation_tier += 2
        elif smc_signal == "SELL" and smc_confidence >= 60:
            v6_confirmation_tier += 1

        if ema20 < ema50:
            v6_confirmation_tier += 1

        if pattern_signal == "SELL" and pattern_confidence >= 75:
            v6_confirmation_tier += 1

    v6_confidence_ceiling = None

    if action in ("BUY", "SELL"):
        if v6_confirmation_tier <= 3:
            v6_confidence_ceiling = 75
        elif v6_confirmation_tier == 4:
            v6_confidence_ceiling = 82
        elif v6_confirmation_tier == 5:
            v6_confidence_ceiling = 88
        else:
            v6_confidence_ceiling = 94

        # Exceptional confidence is reserved for a broad confirmation set
        # plus a genuinely favorable trade structure.
        if (
            v6_confirmation_tier >= 6
            and risk_reward is not None
            and risk_reward >= 3.0
            and setup_available
        ):
            v6_confidence_ceiling = 96

        confidence = min(confidence, v6_confidence_ceiling)

        reasons.append(
            f"V6 final confidence calibration: {confidence:.0f}% "
            f"from confirmation tier {v6_confirmation_tier}/8"
        )

    # ============================================================
    # 14E. LATE-ENTRY / EXTREME-MOVE PROTECTION

    #
    # A very strong directional score can still produce a poor fresh
    # entry when price is already deeply stretched away from EMA20.
    # In that situation, the model should distinguish trend continuation
    # from a late entry. For extreme moves, require independent structure
    # plus a confirmed SMC setup before allowing a new directional action.
    # This is intentionally conservative and only applies to unusually
    # extended conditions; normal trend signals are unchanged.
    # ============================================================

    smc_bullish_setup_confirmed = (
        smc_signal == "BUY"
        and smc_strong_buy
        and safe_bool(
            smc.get("bullish_setup", False)
            if smc_info is not None
            else False
        )
    )

    smc_bearish_setup_confirmed = (
        smc_signal == "SELL"
        and smc_strong_sell
        and safe_bool(
            smc.get("bearish_setup", False)
            if smc_info is not None
            else False
        )
    )

    downside_extension = 0.0
    upside_extension = 0.0

    if close > 0 and ema20 > 0:

        if close < ema20:

            downside_extension = (
                (ema20 - close) / ema20
            ) * 100

        elif close > ema20:

            upside_extension = (
                (close - ema20) / ema20
            ) * 100

    if (
        action == "SELL"
        and rsi < 25
        and downside_extension >= 10
    ):

        if not (
            bearish_structure_confirmed
            and smc_bearish_setup_confirmed
        ):

            action = "HOLD"
            confidence = min(confidence, 65)

            reasons.append(
                f"Fresh SELL blocked because price is extremely extended "
                f"({downside_extension:.2f}% below EMA20) with RSI {rsi:.2f}; "
                "continuation requires confirmed bearish structure and a confirmed SMC setup"
            )

    elif (
        action == "BUY"
        and rsi > 75
        and upside_extension >= 10
    ):

        if not (
            bullish_structure_confirmed
            and smc_bullish_setup_confirmed
        ):

            action = "HOLD"
            confidence = min(confidence, 65)

            reasons.append(
                f"Fresh BUY blocked because price is extremely extended "
                f"({upside_extension:.2f}% above EMA20) with RSI {rsi:.2f}; "
                "continuation requires confirmed bullish structure and a confirmed SMC setup"
            )

    # ============================================================
    # 14F. ENTRY QUALITY / LATE-ENTRY PROTECTION
    #
    # Direction can be correct while the fresh entry is poor. V2 therefore
    # classifies the entry separately from direction. Normal trend entries
    # remain unchanged; only stretched entries receive stronger caution.
    # ============================================================

    entry_quality = "NORMAL"
    entry_extension_percent = 0.0

    if close > 0 and ema20 > 0:

        if action == "BUY" and close > ema20:

            entry_extension_percent = (
                (close - ema20) / ema20
            ) * 100

            if entry_extension_percent >= 12:
                entry_quality = "VERY_EXTENDED"

            elif entry_extension_percent >= 8:
                entry_quality = "EXTENDED"

        elif action == "SELL" and close < ema20:

            entry_extension_percent = (
                (ema20 - close) / ema20
            ) * 100

            if entry_extension_percent >= 12:
                entry_quality = "VERY_EXTENDED"

            elif entry_extension_percent >= 8:
                entry_quality = "EXTENDED"

    if entry_quality == "EXTENDED":

        confidence = min(confidence, 78)

        reasons.append(
            f"Entry quality is EXTENDED: price is "
            f"{entry_extension_percent:.2f}% away from EMA20; "
            "fresh entry carries elevated timing risk"
        )

    elif entry_quality == "VERY_EXTENDED":

        confidence = min(confidence, 70)

        reasons.append(
            f"Entry quality is VERY_EXTENDED: price is "
            f"{entry_extension_percent:.2f}% away from EMA20; "
            "fresh entry should require exceptional confirmation"
        )

        if action == "BUY" and not (
            bullish_structure_confirmed_v2
            and smc_bullish_setup_confirmed_v2
        ):

            action = "HOLD"
            confidence = min(confidence, 65)

            reasons.append(
                "Fresh BUY blocked because the entry is very extended "
                "without both confirmed bullish structure and a confirmed SMC setup"
            )

        elif action == "SELL" and not (
            bearish_structure_confirmed_v2
            and smc_bearish_setup_confirmed_v2
        ):

            action = "HOLD"
            confidence = min(confidence, 65)

            reasons.append(
                "Fresh SELL blocked because the entry is very extended "
                "without both confirmed bearish structure and a confirmed SMC setup"
            )

    # ============================================================
    # 14G. V3 CONFIRMATION QUALITY FILTER
    #
    # V2 correctly identifies the broad market regime, but a strong
    # directional score can still survive when the direction is fighting
    # the EMA trend. V3 requires BOTH independent structure confirmation
    # and a confirmed SMC setup for high-confidence counter-trend entries.
    # This is intentionally narrower than a global trend filter so that
    # proven trend-following trades remain unchanged.
    # ============================================================

    countertrend_quality_blocked = False

    if action == "BUY" and market_regime == "BEARISH":
        if not (
            bullish_structure_confirmed_v2
            and smc_bullish_setup_confirmed_v2
        ):
            action = "HOLD"
            confidence = min(confidence, 65)
            countertrend_quality_blocked = True
            reasons.append(
                "V3 BUY blocked: bearish regime requires both confirmed "
                "bullish market structure and a confirmed bullish SMC setup"
            )

    elif action == "SELL" and market_regime == "BULLISH":
        if not (
            bearish_structure_confirmed_v2
            and smc_bearish_setup_confirmed_v2
        ):
            action = "HOLD"
            confidence = min(confidence, 65)
            countertrend_quality_blocked = True
            reasons.append(
                "V3 SELL blocked: bullish regime requires both confirmed "
                "bearish market structure and a confirmed bearish SMC setup"
            )

    # High confidence is not treated as proof of correctness. When a
    # counter-trend signal survives V3, expose that it passed the stronger
    # confirmation gate rather than silently inflating confidence.
    if (
        not countertrend_quality_blocked
        and action in ("BUY", "SELL")
        and market_regime in ("BULLISH", "BEARISH")
    ):
        reasons.append(
            "V3 directional quality check passed with trend/structure/SMC context"
        )

    # ============================================================
    # 14H. V4 TRADE QUALITY FILTER
    #
    # Protect against the two recurring failure modes found in the
    # 1-year validation set: counter-trend BUYs and late/exhausted SELLs.
    # V4 is intentionally selective and does not alter backtest mechanics.
    # ============================================================

    v4_quality_blocked = False

    price_vs_ema20_pct = 0.0
    if ema20 and ema20 > 0:
        price_vs_ema20_pct = ((close - ema20) / ema20) * 100.0

    ema_trend_bullish = bool(ema20 and ema50 and close > ema20 > ema50)
    ema_trend_bearish = bool(ema20 and ema50 and close < ema20 < ema50)

    # BUY quality: do not take a fresh BUY while the medium-term trend is
    # bearish unless the reversal has independent structure + SMC support.
    if action == "BUY":
        if market_regime == "BEARISH" and not (
            bullish_structure_confirmed_v2 and smc_bullish_setup_confirmed_v2
        ):
            action = "HOLD"
            confidence = min(confidence, 65)
            v4_quality_blocked = True
            reasons.append(
                "V4 BUY blocked: bearish regime requires confirmed bullish structure and SMC setup"
            )

        # If BUY is already above EMA20, require enough trend context rather
        # than chasing an extended move. A normal trend-following BUY remains.
        elif price_vs_ema20_pct >= 10.0 and not (
            ema_trend_bullish and smc_bullish_setup_confirmed_v2
        ):
            action = "HOLD"
            confidence = min(confidence, 65)
            v4_quality_blocked = True
            reasons.append(
                f"V4 BUY blocked: entry is {price_vs_ema20_pct:.2f}% above EMA20 without strong trend/SMC confirmation"
            )

    # SELL quality: a bearish trend can continue through oversold RSI, so do
    # not ban RSI<30 by itself. Instead, block a late SELL when the move is
    # already stretched and independent bearish confirmation is missing.
    elif action == "SELL":
        downside_extension = max(0.0, -price_vs_ema20_pct)
        if downside_extension >= 10.0 and rsi is not None and rsi < 30 and not (
            bearish_structure_confirmed_v2 and smc_bearish_setup_confirmed_v2
        ):
            action = "HOLD"
            confidence = min(confidence, 65)
            v4_quality_blocked = True
            reasons.append(
                f"V4 SELL blocked: late bearish entry ({downside_extension:.2f}% below EMA20) with RSI {rsi:.2f} needs structure + SMC confirmation"
            )

    if not v4_quality_blocked and action in ("BUY", "SELL"):
        reasons.append("V4 trade-quality check passed")

    # ============================================================
    # 15. ENTRY PRICE
    # ============================================================

    entry_price = (
        round(close, 2)
        if close > 0
        else None
    )

    stop_loss = None
    target = None

    stop_type = None
    target_type = None

    setup_available = False

    # ============================================================
    # 16. BUY TRADE SETUP
    # ============================================================

    if (
        action == "BUY"
        and entry_price is not None
    ):

        # --------------------------------------------------------
        # Prefer structural support
        # --------------------------------------------------------

        if (
            nearest_support is not None
            and nearest_support < entry_price
        ):

            candidate_stop = round(
                nearest_support * 0.995,
                2,
            )

            if candidate_stop < entry_price:

                stop_loss = candidate_stop

                stop_type = "Support"

        # --------------------------------------------------------
        # SMC bullish order block can act as support.
        #
        # IMPORTANT:
        # Use only nearby bullish OBs instead of historical OBs.
        # --------------------------------------------------------

        if stop_loss is None:

            valid_blocks = []

            for item in nearby_bullish_ob:

                block = item.get(
                    "zone",
                    {},
                )

                if not isinstance(
                    block,
                    dict,
                ):

                    continue

                block_low = safe_float(
                    block.get(
                        "low",
                        block.get(
                            "price",
                            0,
                        ),
                    ),
                    0,
                )

                if (
                    block_low > 0
                    and block_low < entry_price
                ):

                    valid_blocks.append(
                        {
                            "low": block_low,
                            "distance": item.get(
                                "distance_percent",
                                999,
                            ),
                        }
                    )

            if valid_blocks:

                # Prefer the closest bullish OB below price.
                block_low = max(
                    valid_blocks,
                    key=lambda x: x["low"],
                )["low"]

                candidate_stop = round(
                    block_low * 0.995,
                    2,
                )

                if candidate_stop < entry_price:

                    stop_loss = candidate_stop

                    stop_type = (
                        "Bullish Order Block"
                    )

        # --------------------------------------------------------
        # Fallback stop
        # --------------------------------------------------------

        if stop_loss is None:

            stop_loss = round(
                entry_price * 0.98,
                2,
            )

            stop_type = "2% fallback"

        # --------------------------------------------------------
        # Target
        # --------------------------------------------------------

        if (
            nearest_resistance is not None
            and nearest_resistance > entry_price
        ):

            target = round(
                nearest_resistance,
                2,
            )

            target_type = "Resistance"

        else:

            # No structural resistance is available. Use a risk-based
            # minimum target so the target is derived from the actual
            # stop distance instead of an arbitrary percentage.
            if stop_loss is not None and stop_loss < entry_price:
                risk_amount = entry_price - stop_loss
                target = round(
                    entry_price + (risk_amount * 1.5),
                    2,
                )
                target_type = "1.5R risk-based target"
            else:
                target = round(
                    entry_price * 1.04,
                    2,
                )
                target_type = "4% fallback"

    # ============================================================
    # 17. SELL TRADE SETUP
    # ============================================================

    elif (
        action == "SELL"
        and entry_price is not None
    ):

        # --------------------------------------------------------
        # Prefer structural resistance
        # --------------------------------------------------------

        if (
            nearest_resistance is not None
            and nearest_resistance > entry_price
        ):

            candidate_stop = round(
                nearest_resistance * 1.005,
                2,
            )

            if candidate_stop > entry_price:

                stop_loss = candidate_stop

                stop_type = "Resistance"

        # --------------------------------------------------------
        # Bearish order block can act as resistance.
        #
        # Only nearby bearish OBs are considered.
        # --------------------------------------------------------

        if stop_loss is None:

            valid_blocks = []

            for item in nearby_bearish_ob:

                block = item.get(
                    "zone",
                    {},
                )

                if not isinstance(
                    block,
                    dict,
                ):

                    continue

                block_high = safe_float(
                    block.get(
                        "high",
                        block.get(
                            "price",
                            0,
                        ),
                    ),
                    0,
                )

                if (
                    block_high > entry_price
                ):

                    valid_blocks.append(
                        {
                            "high": block_high,
                            "distance": item.get(
                                "distance_percent",
                                999,
                            ),
                        }
                    )

            if valid_blocks:

                # Prefer the closest bearish OB above price.
                block_high = min(
                    valid_blocks,
                    key=lambda x: x["high"],
                )["high"]

                candidate_stop = round(
                    block_high * 1.005,
                    2,
                )

                if candidate_stop > entry_price:

                    stop_loss = candidate_stop

                    stop_type = (
                        "Bearish Order Block"
                    )

        # --------------------------------------------------------
        # Fallback stop
        # --------------------------------------------------------

        if stop_loss is None:

            stop_loss = round(
                entry_price * 1.02,
                2,
            )

            stop_type = "2% fallback"

        # --------------------------------------------------------
        # Target
        # --------------------------------------------------------

        if (
            nearest_support is not None
            and nearest_support < entry_price
        ):

            target = round(
                nearest_support,
                2,
            )

            target_type = "Support"

        else:

            # No structural support is available. Use a risk-based
            # minimum target so the target is derived from the actual
            # stop distance instead of an arbitrary percentage.
            if stop_loss is not None and stop_loss > entry_price:
                risk_amount = stop_loss - entry_price
                target = round(
                    entry_price - (risk_amount * 1.5),
                    2,
                )
                target_type = "1.5R risk-based target"
            else:
                target = round(
                    entry_price * 0.96,
                    2,
                )
                target_type = "4% fallback"

    # ============================================================
    # 18. RISK / REWARD
    # ============================================================

    if (
        action == "BUY"
        and entry_price is not None
        and stop_loss is not None
        and target is not None
    ):

        risk = (
            entry_price
            - stop_loss
        )

        reward = (
            target
            - entry_price
        )

        if (
            risk > 0
            and reward > 0
        ):

            risk_reward = round(
                reward / risk,
                2,
            )

    elif (
        action == "SELL"
        and entry_price is not None
        and stop_loss is not None
        and target is not None
    ):

        risk = (
            stop_loss
            - entry_price
        )

        reward = (
            entry_price
            - target
        )

        if (
            risk > 0
            and reward > 0
        ):

            risk_reward = round(
                reward / risk,
                2,
            )

    # ============================================================
    # 19. RISK / REWARD VALIDATION
    # ============================================================

    if action in (
        "BUY",
        "SELL",
    ):

        if (
            risk_reward is None
            or risk_reward < 1.5
        ):

            # Keep calculated stop-loss, target and R:R visible.
            # The setup remains unapproved when R:R is below 1:1.5.
            setup_available = False

            reasons.append(
                "Risk/reward is below the "
                "minimum 1:1.5 threshold"
            )

            if risk_reward is not None:
                reasons.append(
                    f"Calculated risk/reward is {risk_reward:.2f}; "
                    f"trade setup is not approved"
                )

            reasons.append(
                "Directional signal detected, "
                "but the trade setup is not approved "
                "because the risk/reward is insufficient"
            )

        else:

            setup_available = True

            reasons.append(
                f"Trade setup meets the minimum "
                f"1:1.5 risk/reward requirement "
                f"with R:R {risk_reward:.2f}"
            )

    # ============================================================
    # 20. RISK LEVEL
    # ============================================================

    if action == "HOLD":

        risk_level = "Medium"

    elif not setup_available:

        risk_level = "High"

    elif risk_reward is not None:

        if risk_reward >= 3:

            risk_level = "Low"

        elif risk_reward >= 2:

            risk_level = "Medium"

        else:

            risk_level = "High"

    else:

        risk_level = "Medium"

    # ============================================================
    # 21. FINAL DIRECTIONAL REASON
    # ============================================================

    if action == "BUY":

        reasons.append(
            f"AI identified a bullish directional bias "
            f"with {bullish_factors} bullish factors"
        )

    elif action == "SELL":

        reasons.append(
            f"AI identified a bearish directional bias "
            f"with {bearish_factors} bearish factors"
        )

    else:

        reasons.append(
            "Signals are not strong enough "
            "for a directional trade"
        )

    # ============================================================
    # 22. TRADE SETUP
    # ============================================================

    # ============================================================
    # 21B. V5 SIGNAL / TRADE-QUALITY SEPARATION
    # ============================================================
    # `confidence` remains the directional signal confidence for backward
    # compatibility. Trade quality is evaluated separately using setup,
    # R:R, regime alignment and entry timing.

    signal_confidence = int(
        max(0, min(100, confidence))
    )

    trade_quality_confidence = 50
    if action in ("BUY", "SELL"):
        trade_quality_confidence = 60

        if setup_available:
            trade_quality_confidence += 15

        if risk_reward is not None:
            if risk_reward >= 3.0:
                trade_quality_confidence += 15
            elif risk_reward >= 2.0:
                trade_quality_confidence += 10
            elif risk_reward >= 1.5:
                trade_quality_confidence += 5

        aligned_with_regime = (
            (action == "BUY" and market_regime == "BULLISH")
            or (action == "SELL" and market_regime == "BEARISH")
        )
        if aligned_with_regime:
            trade_quality_confidence += 10
        elif market_regime in ("BULLISH", "BEARISH"):
            trade_quality_confidence -= 10

        if entry_quality == "EXTENDED":
            trade_quality_confidence -= 10
        elif entry_quality == "VERY_EXTENDED":
            trade_quality_confidence -= 20

        trade_quality_confidence = max(0, min(100, trade_quality_confidence))

    if action in ("BUY", "SELL"):
        reasons.append(
            f"V5 trade quality: {trade_quality_confidence}/100 "
            f"(signal confidence {signal_confidence}/100)"
        )
    else:
        reasons.append(
            f"V5 signal confidence: {signal_confidence}/100; no directional trade setup"
        )

    trade_setup = {

        "action": action,

        "entry": entry_price,

        "stop_loss": stop_loss,

        "target": target,

        "risk_reward": risk_reward,

        "risk_level": risk_level,

        "stop_type": stop_type,

        "target_type": target_type,

        "setup_available": setup_available,
    }

    # ============================================================
    # 23. FINAL RESPONSE
    # ============================================================

    return {

        "recommendation": action,

        "confidence": int(
            max(
                0,
                min(
                    100,
                    confidence,
                ),
            )
        ),

        "score": int(score),

        "raw_score": int(v5_raw_score),

        "signal_confidence": int(signal_confidence),

        "trade_quality_confidence": int(trade_quality_confidence),

        "trade_quality": (
            "APPROVED" if setup_available else "NOT_APPROVED"
        ),

        "decision_context": {
            "market_regime": market_regime,
            "structure_signal": structure_signal,
            "smc_signal": smc_signal,
            "entry_quality": entry_quality,
            "risk_reward": risk_reward,
        },

        "bullish_factors": int(
            bullish_factors
        ),

        "bearish_factors": int(
            bearish_factors
        ),

        "entry_price": entry_price,

        "stop_loss": stop_loss,

        "target": target,

        "risk_reward": risk_reward,

        "risk_level": risk_level,

        "market_regime": market_regime,

        "entry_quality": entry_quality,

        "entry_extension_percent": round(
            entry_extension_percent,
            2,
        ),

        "trade_setup": trade_setup,

        "reasons": reasons,

        "pattern_analysis": pattern_info,

        "market_structure_analysis": (
            market_structure_info
        ),

        "support_resistance_analysis": (
            support_resistance_info
        ),

        "smc_analysis": smc_info,

        "v7_explanation": build_v7_explanation(
            action=action,
            confidence=confidence,
            score=score,
            bullish_factors=bullish_factors,
            bearish_factors=bearish_factors,
            rsi=rsi,
            close=close,
            ema20=ema20,
            ema50=ema50,
            macd=macd,
            macd_signal=macd_signal,
            market_regime=market_regime,
            market_structure_info=market_structure_info,
            smc_info=smc_info,
            support_resistance_info=support_resistance_info,
            pattern_info=pattern_info,
            risk_reward=risk_reward,
            setup_available=setup_available,
        ),
    }