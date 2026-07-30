import pandas as pd


def calculate_support_resistance(df: pd.DataFrame):
    """
    Detect recent swing highs and swing lows.
    Returns the strongest support and resistance levels.
    """

    highs = []
    lows = []

    lookback = 3

    for i in range(lookback, len(df) - lookback):

        # Swing High
        if (
            df["High"].iloc[i]
            == max(df["High"].iloc[i - lookback : i + lookback + 1])
        ):
            highs.append(float(df["High"].iloc[i]))

        # Swing Low
        if (
            df["Low"].iloc[i]
            == min(df["Low"].iloc[i - lookback : i + lookback + 1])
        ):
            lows.append(float(df["Low"].iloc[i]))

    highs = sorted(set(highs))
    lows = sorted(set(lows))

    resistance = highs[-3:] if len(highs) >= 3 else highs
    support = lows[:3] if len(lows) >= 3 else lows

    return {
        "support": support,
        "resistance": resistance,
    }