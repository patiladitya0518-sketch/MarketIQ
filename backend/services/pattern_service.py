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


# ============================================================
# PATTERN DETECTION ENGINE
# ============================================================

def detect_pattern(df: pd.DataFrame):

    # ========================================================
    # VALIDATION
    # ========================================================

    if df is None or df.empty:

        return {
            "pattern": "Unknown",
            "signal": "HOLD",
            "confidence": 0,
            "reason": [
                "No market data available"
            ],
        }

    if len(df) < 3:

        return {
            "pattern": "Unknown",
            "signal": "HOLD",
            "confidence": 0,
            "reason": [
                "Not enough candle data"
            ],
        }

    # ========================================================
    # REQUIRED COLUMNS
    # ========================================================

    required_columns = [
        "Open",
        "High",
        "Low",
        "Close",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:

        return {
            "pattern": "Unknown",
            "signal": "HOLD",
            "confidence": 0,
            "reason": [
                "Missing candle columns: "
                + ", ".join(missing_columns)
            ],
        }

    # ========================================================
    # REMOVE INVALID CANDLES
    # ========================================================

    df = df.copy()

    for column in required_columns:

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce",
        )

    df = df.dropna(
        subset=required_columns
    )

    if len(df) < 3:

        return {
            "pattern": "Unknown",
            "signal": "HOLD",
            "confidence": 0,
            "reason": [
                "Not enough valid OHLC candle data"
            ],
        }

    # ========================================================
    # DETECTORS
    # ========================================================

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

    # ========================================================
    # STORE ALL DETECTED PATTERNS
    # ========================================================

    detected_patterns = []

    # ========================================================
    # BULLISH
    # ========================================================

    for detector in bullish_patterns:

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
                            "BUY",
                        ),

                        "strength": result.get(
                            "strength",
                            0,
                        ),

                        "confidence": confidence,

                        "direction_priority": 3,

                        "reason": reasons,
                    }
                )

        except Exception as error:

            print(
                f"Bullish detector error "
                f"in {detector.__name__}: {error}"
            )

    # ========================================================
    # BEARISH
    # ========================================================

    for detector in bearish_patterns:

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
                            "SELL",
                        ),

                        "strength": result.get(
                            "strength",
                            0,
                        ),

                        "confidence": confidence,

                        "direction_priority": 3,

                        "reason": reasons,
                    }
                )

        except Exception as error:

            print(
                f"Bearish detector error "
                f"in {detector.__name__}: {error}"
            )

    # ========================================================
    # NEUTRAL
    # ========================================================

    for detector in neutral_patterns:

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

                        "direction_priority": 1,

                        "reason": reasons,
                    }
                )

        except Exception as error:

            print(
                f"Neutral detector error "
                f"in {detector.__name__}: {error}"
            )

    # ========================================================
    # NO PATTERN
    # ========================================================

    if not detected_patterns:

        return {
            "pattern": "No Strong Pattern",
            "signal": "HOLD",
            "confidence": 50,
            "reason": [
                "No supported candlestick pattern "
                "was detected on the latest candles.",
                "Technical indicators are being used "
                "instead of forcing a candlestick signal.",
            ],
        }

    # ========================================================
    # SELECT BEST PATTERN
    #
    # Priority:
    # 1. Pattern strength
    # 2. Confidence
    # 3. Directional pattern over neutral pattern
    # ========================================================

    detected_patterns.sort(
        key=lambda item: (
            item["strength"],
            item["confidence"],
            item["direction_priority"],
        ),
        reverse=True,
    )

    strongest = detected_patterns[0]

    # ========================================================
    # RETURN
    # ========================================================

    return {
        "pattern": strongest["pattern"],

        "signal": strongest["signal"],

        "confidence": strongest["confidence"],

        "reason": strongest["reason"],
    }