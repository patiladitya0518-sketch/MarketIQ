from typing import Any, Dict, List, Optional


# ============================================================
# MarketIQ AI Signal Engine
# ============================================================
#
# Combines:
#   1. RSI
#   2. MACD
#   3. EMA20
#   4. EMA50
#   5. Candlestick Pattern
#   6. Market Structure
#   7. Support / Resistance
#
# Output:
#   BUY / SELL / HOLD
#
# The engine uses a scoring system instead of allowing
# one indicator to completely control the final decision.
# ============================================================


# ============================================================
# CONFIGURATION
# ============================================================

BUY_THRESHOLD = 35
SELL_THRESHOLD = -35

STRONG_BUY_THRESHOLD = 60
STRONG_SELL_THRESHOLD = -60

MAX_SCORE = 100
MIN_SCORE = -100


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def safe_float(value: Any, default: float = 0.0) -> float:
    """
    Safely convert a value to float.
    """

    try:
        if value is None:
            return default

        return float(value)

    except (TypeError, ValueError):
        return default


def clamp(
    value: float,
    minimum: float = MIN_SCORE,
    maximum: float = MAX_SCORE,
) -> float:
    """
    Keep score inside allowed range.
    """

    return max(
        minimum,
        min(
            maximum,
            value,
        ),
    )


# ============================================================
# RSI SIGNAL
# ============================================================

def calculate_rsi_signal(
    rsi: Optional[float],
):
    """
    RSI contribution.

    > 60  -> bullish
    < 40  -> bearish
    40-60 -> neutral
    """

    if rsi is None:
        return 0, None

    rsi = safe_float(rsi)

    if rsi >= 70:
        return (
            8,
            f"RSI is overbought at {rsi:.2f}",
        )

    if rsi > 60:
        return (
            10,
            f"RSI confirms bullish momentum at {rsi:.2f}",
        )

    if rsi <= 30:
        return (
            -8,
            f"RSI is oversold at {rsi:.2f}",
        )

    if rsi < 40:
        return (
            -10,
            f"RSI confirms bearish momentum at {rsi:.2f}",
        )

    return (
        0,
        f"RSI is neutral at {rsi:.2f}",
    )


# ============================================================
# MACD SIGNAL
# ============================================================

def calculate_macd_signal(
    macd: Optional[float],
    macd_signal: Optional[float],
    bullish_crossover: bool = False,
    bearish_crossover: bool = False,
):
    """
    MACD contribution.

    Crossover receives more weight than a simple
    MACD / signal comparison.
    """

    if macd is None or macd_signal is None:
        return 0, None

    macd = safe_float(macd)
    macd_signal = safe_float(macd_signal)

    if bullish_crossover:
        return (
            15,
            "MACD bullish crossover confirmed",
        )

    if bearish_crossover:
        return (
            -15,
            "MACD bearish crossover confirmed",
        )

    if macd > macd_signal:
        return (
            7,
            f"MACD ({macd:.2f}) is above signal ({macd_signal:.2f}), showing bullish momentum",
        )

    if macd < macd_signal:
        return (
            -7,
            f"MACD ({macd:.2f}) is below signal ({macd_signal:.2f}), showing bearish momentum",
        )

    return (
        0,
        "MACD is neutral",
    )


# ============================================================
# EMA20 SIGNAL
# ============================================================

def calculate_ema20_signal(
    price: Optional[float],
    ema20: Optional[float],
):
    """
    Price vs EMA20.
    """

    if price is None or ema20 is None:
        return 0, None

    price = safe_float(price)
    ema20 = safe_float(ema20)

    if price > ema20:
        return (
            8,
            f"Price ({price:.2f}) is above EMA20 ({ema20:.2f})",
        )

    if price < ema20:
        return (
            -8,
            f"Price ({price:.2f}) is below EMA20 ({ema20:.2f})",
        )

    return (
        0,
        "Price is near EMA20",
    )


# ============================================================
# EMA50 SIGNAL
# ============================================================

def calculate_ema50_signal(
    price: Optional[float],
    ema50: Optional[float],
):
    """
    Price vs EMA50.
    """

    if price is None or ema50 is None:
        return 0, None

    price = safe_float(price)
    ema50 = safe_float(ema50)

    if price > ema50:
        return (
            10,
            f"Price ({price:.2f}) is above EMA50 ({ema50:.2f})",
        )

    if price < ema50:
        return (
            -10,
            f"Price ({price:.2f}) is below EMA50 ({ema50:.2f})",
        )

    return (
        0,
        "Price is near EMA50",
    )


# ============================================================
# EMA TREND SIGNAL
# ============================================================

def calculate_ema_trend_signal(
    ema20: Optional[float],
    ema50: Optional[float],
):
    """
    EMA20 vs EMA50.

    EMA20 > EMA50 -> bullish trend bias
    EMA20 < EMA50 -> bearish trend bias
    """

    if ema20 is None or ema50 is None:
        return 0, None

    ema20 = safe_float(ema20)
    ema50 = safe_float(ema50)

    if ema20 > ema50:
        return (
            10,
            f"EMA20 ({ema20:.2f}) is above EMA50 ({ema50:.2f}), indicating a bullish trend bias",
        )

    if ema20 < ema50:
        return (
            -10,
            f"EMA20 ({ema20:.2f}) is below EMA50 ({ema50:.2f}), indicating a bearish trend bias",
        )

    return (
        0,
        "EMA20 and EMA50 are nearly equal",
    )


# ============================================================
# CANDLESTICK PATTERN SIGNAL
# ============================================================

def calculate_pattern_signal(
    pattern: Optional[Dict[str, Any]],
):
    """
    Candlestick pattern contribution.

    Pattern strength is used but capped so that a single
    candle pattern cannot completely dominate the system.
    """

    if not pattern:
        return 0, None

    pattern_name = pattern.get(
        "pattern",
        "Unknown",
    )

    signal = str(
        pattern.get(
            "signal",
            "HOLD",
        )
    ).upper()

    confidence = safe_float(
        pattern.get(
            "confidence",
            0,
        )
    )

    strength = safe_float(
        pattern.get(
            "strength",
            confidence,
        )
    )

    if pattern_name in (
        "Unknown",
        "No Strong Pattern",
    ):
        return (
            0,
            "No strong candlestick pattern detected",
        )

    # Normalize pattern strength.
    pattern_score = min(
        20,
        max(
            5,
            strength * 0.20,
        ),
    )

    if signal == "BUY":

        return (
            round(pattern_score),
            f"{pattern_name} supports BUY ({confidence:.0f}% confidence)",
        )

    if signal == "SELL":

        return (
            -round(pattern_score),
            f"{pattern_name} supports SELL ({confidence:.0f}% confidence)",
        )

    return (
        0,
        f"{pattern_name} does not provide a strong directional signal",
    )


# ============================================================
# MARKET STRUCTURE SIGNAL
# ============================================================

def calculate_market_structure_signal(
    market_structure: Optional[Dict[str, Any]],
):
    """
    Market structure contribution.

    BUY structure  -> bullish
    SELL structure -> bearish
    Neutral        -> no directional score
    """

    if not market_structure:
        return 0, None

    structure = str(
        market_structure.get(
            "structure",
            "Neutral",
        )
    ).upper()

    signal = str(
        market_structure.get(
            "signal",
            "HOLD",
        )
    ).upper()

    confidence = safe_float(
        market_structure.get(
            "confidence",
            0,
        )
    )

    if signal == "BUY" or structure == "BULLISH":

        return (
            15,
            f"Market structure is bullish ({confidence:.0f}% confidence)",
        )

    if signal == "SELL" or structure == "BEARISH":

        return (
            -15,
            f"Market structure is bearish ({confidence:.0f}% confidence)",
        )

    return (
        0,
        "Market structure is neutral",
    )


# ============================================================
# SUPPORT / RESISTANCE SIGNAL
# ============================================================

def calculate_support_resistance_signal(
    price: Optional[float],
    support_resistance: Optional[Dict[str, Any]],
):
    """
    Support / resistance contribution.

    Near support:
        bullish opportunity

    Near resistance:
        bearish pressure

    Otherwise:
        neutral
    """

    if price is None or not support_resistance:
        return 0, None

    price = safe_float(price)

    supports = support_resistance.get(
        "support",
        [],
    )

    resistances = support_resistance.get(
        "resistance",
        [],
    )

    supports = [
        safe_float(level)
        for level in supports
        if level is not None
    ]

    resistances = [
        safe_float(level)
        for level in resistances
        if level is not None
    ]

    nearest_support = None
    nearest_resistance = None

    if supports:
        valid_supports = [
            level
            for level in supports
            if level <= price
        ]

        if valid_supports:
            nearest_support = max(
                valid_supports
            )

    if resistances:
        valid_resistances = [
            level
            for level in resistances
            if level >= price
        ]

        if valid_resistances:
            nearest_resistance = min(
                valid_resistances
            )

    # --------------------------------------------------------
    # Near support
    # --------------------------------------------------------

    if nearest_support:

        distance = (
            abs(price - nearest_support)
            / price
        ) * 100

        if distance <= 2:

            return (
                8,
                f"Price is near major support at ₹{nearest_support:.2f}",
            )

    # --------------------------------------------------------
    # Near resistance
    # --------------------------------------------------------

    if nearest_resistance:

        distance = (
            abs(nearest_resistance - price)
            / price
        ) * 100

        if distance <= 2:

            return (
                -8,
                f"Price is near major resistance at ₹{nearest_resistance:.2f}",
            )

    return (
        0,
        "Price is not near a major detected support or resistance level",
    )


# ============================================================
# FINAL SIGNAL
# ============================================================

def determine_signal(score: float):
    """
    Convert numerical score into final trading signal.
    """

    if score >= STRONG_BUY_THRESHOLD:
        return "BUY"

    if score <= STRONG_SELL_THRESHOLD:
        return "SELL"

    if score >= BUY_THRESHOLD:
        return "BUY"

    if score <= SELL_THRESHOLD:
        return "SELL"

    return "HOLD"


# ============================================================
# CONFIDENCE
# ============================================================

def calculate_signal_confidence(
    score: float,
    bullish_factors: int,
    bearish_factors: int,
):
    """
    Convert signal strength into a readable confidence value.

    Confidence is deliberately capped below 100 because
    technical analysis is probabilistic and not guaranteed.
    """

    absolute_score = abs(score)

    confidence = 50 + (
        absolute_score * 0.45
    )

    # Agreement bonus.
    if (
        bullish_factors >= 4
        or bearish_factors >= 4
    ):
        confidence += 5

    confidence = min(
        95,
        max(
            50,
            confidence,
        ),
    )

    return round(
        confidence
    )


# ============================================================
# MAIN AI SIGNAL ENGINE
# ============================================================

def generate_ai_signal(
    price: Optional[float],
    indicators: Optional[Dict[str, Any]],
    pattern: Optional[Dict[str, Any]] = None,
    market_structure: Optional[Dict[str, Any]] = None,
    support_resistance: Optional[Dict[str, Any]] = None,
):
    """
    Main MarketIQ AI Signal Engine.

    Parameters
    ----------
    price:
        Current market price.

    indicators:
        Dictionary containing:
            RSI
            MACD
            MACD_SIGNAL
            EMA20
            EMA50
            MACD_BULLISH_CROSSOVER
            MACD_BEARISH_CROSSOVER

    pattern:
        Candlestick pattern result.

    market_structure:
        Market structure result.

    support_resistance:
        Detected support and resistance levels.

    Returns
    -------
    dict
        Complete AI signal result.
    """

    indicators = indicators or {}

    score = 0

    reasons: List[str] = []

    bullish_factors = 0
    bearish_factors = 0

    contributions: Dict[str, float] = {}

    # ========================================================
    # RSI
    # ========================================================

    rsi = indicators.get(
        "RSI"
    )

    rsi_score, rsi_reason = calculate_rsi_signal(
        rsi
    )

    score += rsi_score

    contributions["RSI"] = rsi_score

    if rsi_score > 0:
        bullish_factors += 1

    elif rsi_score < 0:
        bearish_factors += 1

    if rsi_reason:
        reasons.append(
            rsi_reason
        )

    # ========================================================
    # MACD
    # ========================================================

    macd = indicators.get(
        "MACD"
    )

    macd_signal = indicators.get(
        "MACD_SIGNAL"
    )

    bullish_crossover = bool(
        indicators.get(
            "MACD_BULLISH_CROSSOVER",
            False,
        )
    )

    bearish_crossover = bool(
        indicators.get(
            "MACD_BEARISH_CROSSOVER",
            False,
        )
    )

    macd_score, macd_reason = calculate_macd_signal(
        macd,
        macd_signal,
        bullish_crossover,
        bearish_crossover,
    )

    score += macd_score

    contributions["MACD"] = macd_score

    if macd_score > 0:
        bullish_factors += 1

    elif macd_score < 0:
        bearish_factors += 1

    if macd_reason:
        reasons.append(
            macd_reason
        )

    # ========================================================
    # EMA20
    # ========================================================

    ema20 = indicators.get(
        "EMA20"
    )

    ema20_score, ema20_reason = calculate_ema20_signal(
        price,
        ema20,
    )

    score += ema20_score

    contributions["EMA20"] = ema20_score

    if ema20_score > 0:
        bullish_factors += 1

    elif ema20_score < 0:
        bearish_factors += 1

    if ema20_reason:
        reasons.append(
            ema20_reason
        )

    # ========================================================
    # EMA50
    # ========================================================

    ema50 = indicators.get(
        "EMA50"
    )

    ema50_score, ema50_reason = calculate_ema50_signal(
        price,
        ema50,
    )

    score += ema50_score

    contributions["EMA50"] = ema50_score

    if ema50_score > 0:
        bullish_factors += 1

    elif ema50_score < 0:
        bearish_factors += 1

    if ema50_reason:
        reasons.append(
            ema50_reason
        )

    # ========================================================
    # EMA20 / EMA50 TREND
    # ========================================================

    ema_trend_score, ema_trend_reason = calculate_ema_trend_signal(
        ema20,
        ema50,
    )

    score += ema_trend_score

    contributions["EMA_TREND"] = ema_trend_score

    if ema_trend_score > 0:
        bullish_factors += 1

    elif ema_trend_score < 0:
        bearish_factors += 1

    if ema_trend_reason:
        reasons.append(
            ema_trend_reason
        )

    # ========================================================
    # CANDLESTICK PATTERN
    # ========================================================

    pattern_score, pattern_reason = calculate_pattern_signal(
        pattern
    )

    score += pattern_score

    contributions["PATTERN"] = pattern_score

    if pattern_score > 0:
        bullish_factors += 1

    elif pattern_score < 0:
        bearish_factors += 1

    if pattern_reason:
        reasons.append(
            pattern_reason
        )

    # ========================================================
    # MARKET STRUCTURE
    # ========================================================

    structure_score, structure_reason = calculate_market_structure_signal(
        market_structure
    )

    score += structure_score

    contributions["MARKET_STRUCTURE"] = structure_score

    if structure_score > 0:
        bullish_factors += 1

    elif structure_score < 0:
        bearish_factors += 1

    if structure_reason:
        reasons.append(
            structure_reason
        )

    # ========================================================
    # SUPPORT / RESISTANCE
    # ========================================================

    sr_score, sr_reason = calculate_support_resistance_signal(
        price,
        support_resistance,
    )

    score += sr_score

    contributions["SUPPORT_RESISTANCE"] = sr_score

    if sr_score > 0:
        bullish_factors += 1

    elif sr_score < 0:
        bearish_factors += 1

    if sr_reason:
        reasons.append(
            sr_reason
        )

    # ========================================================
    # FINAL SCORE
    # ========================================================

    score = clamp(
        score
    )

    signal = determine_signal(
        score
    )

    # ========================================================
    # CONFIDENCE
    # ========================================================

    confidence = calculate_signal_confidence(
        score,
        bullish_factors,
        bearish_factors,
    )

    # ========================================================
    # MIXED SIGNAL CHECK
    # ========================================================

    if (
        bullish_factors >= 2
        and bearish_factors >= 2
        and abs(score) < 35
    ):

        signal = "HOLD"

        reasons.append(
            f"Signals are mixed "
            f"({bullish_factors} bullish vs "
            f"{bearish_factors} bearish factors)"
        )

    # ========================================================
    # WEAK SIGNAL CHECK
    # ========================================================

    if signal == "BUY" and score < BUY_THRESHOLD:

        signal = "HOLD"

    if signal == "SELL" and score > SELL_THRESHOLD:

        signal = "HOLD"

    # ========================================================
    # FINAL EXPLANATION
    # ========================================================

    if signal == "BUY":

        reasons.append(
            "Bullish signals are strong enough for a directional setup"
        )

    elif signal == "SELL":

        reasons.append(
            "Bearish signals are strong enough for a directional setup"
        )

    else:

        reasons.append(
            "Signals are not strong enough for a directional trade"
        )

    # ========================================================
    # RESULT
    # ========================================================

    return {
        "recommendation": signal,
        "signal": signal,

        "score": round(
            score
        ),

        "confidence": confidence,

        "bullish_factors": bullish_factors,

        "bearish_factors": bearish_factors,

        "reasons": reasons,

        "contributions": contributions,

        "is_directional": signal in (
            "BUY",
            "SELL",
        ),
    }