import pandas as pd


def calculate_support_resistance(df: pd.DataFrame):
    """
    Detect recent swing highs and swing lows.

    Returns the strongest recent support
    and resistance levels.
    """

    highs = []
    lows = []

    lookback = 3

    # ============================================================
    # FIND SWING HIGHS AND SWING LOWS
    # ============================================================

    for i in range(
        lookback,
        len(df) - lookback,
    ):

        # --------------------------------------------------------
        # Swing High
        # --------------------------------------------------------

        if (
            df["High"].iloc[i]
            == max(
                df["High"].iloc[
                    i - lookback : i + lookback + 1
                ]
            )
        ):

            highs.append(
                float(
                    df["High"].iloc[i]
                )
            )

        # --------------------------------------------------------
        # Swing Low
        # --------------------------------------------------------

        if (
            df["Low"].iloc[i]
            == min(
                df["Low"].iloc[
                    i - lookback : i + lookback + 1
                ]
            )
        ):

            lows.append(
                float(
                    df["Low"].iloc[i]
                )
            )

    # ============================================================
    # REMOVE DUPLICATES
    # ============================================================

    highs = sorted(set(highs))
    lows = sorted(set(lows))

    # ============================================================
    # SELECT RECENT / STRONG LEVELS
    # ============================================================

    resistance = (
        highs[-3:]
        if len(highs) >= 3
        else highs
    )

    support = (
        lows[:3]
        if len(lows) >= 3
        else lows
    )

    # ============================================================
    # ROUND LEVELS
    # ============================================================

    support = [
        round(level, 2)
        for level in support
    ]

    resistance = [
        round(level, 2)
        for level in resistance
    ]

    # ============================================================
    # FINAL RESPONSE
    # ============================================================

    return {
        "support": support,
        "resistance": resistance,
    }