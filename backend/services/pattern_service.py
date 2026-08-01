import pandas as pd

from services.bullish_patterns import (
    detect_bullish_engulfing,
    detect_hammer,
    detect_morning_star,
    detect_piercing_pattern,
    detect_three_white_soldiers,
)

from services.bearish_patterns import (
    detect_bearish_engulfing,
    detect_shooting_star,
    detect_evening_star,
    detect_dark_cloud_cover,
    detect_hanging_man,
)

from services.neutral_patterns import (
    detect_doji,
    detect_spinning_top,
    detect_dragonfly_doji,
    detect_gravestone_doji,
    detect_marubozu,
)

from services.confidence_service import calculate_confidence


def detect_pattern(df: pd.DataFrame):
    """
    Main AI Pattern Detection Engine
    """

    if len(df) < 3:
        return {
            "pattern": "Unknown",
            "signal": "HOLD",
            "confidence": 0,
            "reason": ["Not enough candle data"],
        }

    # =====================================================
    # Bullish Pattern Checks
    # =====================================================

    bullish_patterns = [
        detect_bullish_engulfing,
        detect_hammer,
        detect_morning_star,
        detect_piercing_pattern,
        detect_three_white_soldiers,
    ]

    for detector in bullish_patterns:

        result = detector(df)

        if result:

            confidence, reasons = calculate_confidence(df, result)

            return {
                "pattern": result["pattern"],
                "signal": result["signal"],
                "confidence": confidence,
                "reason": reasons,
            }

    # =====================================================
    # Bearish Pattern Checks
    # =====================================================

    bearish_patterns = [
        detect_bearish_engulfing,
        detect_shooting_star,
        detect_evening_star,
        detect_dark_cloud_cover,
        detect_hanging_man,
    ]

    for detector in bearish_patterns:

        result = detector(df)

        if result:

            confidence, reasons = calculate_confidence(df, result)

            return {
                "pattern": result["pattern"],
                "signal": result["signal"],
                "confidence": confidence,
                "reason": reasons,
            }

    # =====================================================
    # Neutral Pattern Checks
    # =====================================================

    neutral_patterns = [
        detect_doji,
        detect_spinning_top,
        detect_dragonfly_doji,
        detect_gravestone_doji,
        detect_marubozu,
    ]

    for detector in neutral_patterns:

        result = detector(df)

        if result:

            confidence, reasons = calculate_confidence(df, result)

            return {
                "pattern": result["pattern"],
                "signal": result["signal"],
                "confidence": confidence,
                "reason": reasons,
            }

    # =====================================================
    # No Pattern Found
    # =====================================================

    confidence, reasons = calculate_confidence(
        df,
        {
            "pattern": "No Strong Pattern",
            "signal": "HOLD",
            "strength": 10,
        },
    )

    return {
        "pattern": "No Strong Pattern",
        "signal": "HOLD",
        "confidence": confidence,
        "reason": reasons,
    }