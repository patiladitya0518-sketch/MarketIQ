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
    MarketIQ AI Pattern Detection Engine.

    Checks all supported candlestick patterns and selects
    the strongest detected pattern instead of returning
    the first pattern found.

    Supported:

    Bullish:
    - Bullish Engulfing
    - Hammer
    - Morning Star
    - Piercing Pattern
    - Three White Soldiers

    Bearish:
    - Bearish Engulfing
    - Shooting Star
    - Evening Star
    - Dark Cloud Cover
    - Hanging Man

    Neutral:
    - Doji
    - Spinning Top
    - Dragonfly Doji
    - Gravestone Doji
    - Marubozu
    """

    # ============================================================
    # VALIDATION
    # ============================================================

    if df is None or len(df) < 3:

        return {
            "pattern": "Unknown",
            "signal": "HOLD",
            "confidence": 0,
            "reason": [
                "Not enough candle data"
            ],
        }

    # ============================================================
    # ALL PATTERN DETECTORS
    # ============================================================

    bullish_patterns = [
        detect_bullish_engulfing,
        detect_hammer,
        detect_morning_star,
        detect_piercing_pattern,
        detect_three_white_soldiers,
    ]

    bearish_patterns = [
        detect_bearish_engulfing,
        detect_shooting_star,
        detect_evening_star,
        detect_dark_cloud_cover,
        detect_hanging_man,
    ]

    neutral_patterns = [
        detect_doji,
        detect_spinning_top,
        detect_dragonfly_doji,
        detect_gravestone_doji,
        detect_marubozu,
    ]

    all_detectors = (
        bullish_patterns
        + bearish_patterns
        + neutral_patterns
    )

    # ============================================================
    # DETECT ALL MATCHING PATTERNS
    # ============================================================

    detected_patterns = []

    for detector in all_detectors:

        try:

            result = detector(df)

            if result:

                confidence, reasons = calculate_confidence(
                    df,
                    result,
                )

                detected_patterns.append(
                    {
                        "pattern": result.get(
                            "pattern",
                            "Unknown",
                        ),

                        "signal": result.get(
                            "signal",
                            "HOLD",
                        ),

                        "strength": result.get(
                            "strength",
                            0,
                        ),

                        "confidence": confidence,

                        "reason": reasons,
                    }
                )

        except Exception as e:

            print(
                f"Pattern detector error "
                f"in {detector.__name__}: {e}"
            )

    # ============================================================
    # NO PATTERN
    # ============================================================

    if not detected_patterns:

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

    # ============================================================
    # SELECT STRONGEST PATTERN
    #
    # Priority:
    # 1. Pattern strength
    # 2. Confidence
    #
    # This prevents the first detected pattern from
    # automatically winning.
    # ============================================================

    detected_patterns.sort(
        key=lambda x: (
            x["strength"],
            x["confidence"],
        ),
        reverse=True,
    )

    strongest = detected_patterns[0]

    # ============================================================
    # RETURN BEST PATTERN
    # ============================================================

    return {
        "pattern": strongest["pattern"],

        "signal": strongest["signal"],

        "confidence": strongest["confidence"],

        "reason": strongest["reason"],
    }