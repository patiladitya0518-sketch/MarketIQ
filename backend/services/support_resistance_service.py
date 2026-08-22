import pandas as pd


def calculate_support_resistance(
    df: pd.DataFrame,
    current_price: float | None = None,
):
    """
    Calculate price-aware support and resistance levels.

    Improvements:
    - Detects swing highs/lows.
    - Keeps only relevant levels around current price.
    - Separates support below price and resistance above price.
    - Calculates distance from current price.
    - Identifies nearby levels using a percentage threshold.
    """

    if df is None or df.empty:
        return {
            "support": [],
            "resistance": [],
            "nearest_support": None,
            "nearest_resistance": None,
            "support_distance_percent": None,
            "resistance_distance_percent": None,
            "support_near": False,
            "resistance_near": False,
        }

    required_columns = {"High", "Low"}

    if not required_columns.issubset(df.columns):
        return {
            "support": [],
            "resistance": [],
            "nearest_support": None,
            "nearest_resistance": None,
            "support_distance_percent": None,
            "resistance_distance_percent": None,
            "support_near": False,
            "resistance_near": False,
        }

    # ============================================================
    # CURRENT PRICE
    # ============================================================

    if current_price is None:

        if "Close" in df.columns:

            try:
                current_price = float(
                    df["Close"].iloc[-1]
                )

            except (TypeError, ValueError):
                current_price = 0.0

        else:
            current_price = 0.0

    try:
        current_price = float(current_price)

    except (TypeError, ValueError):
        current_price = 0.0

    if current_price <= 0:
        return {
            "support": [],
            "resistance": [],
            "nearest_support": None,
            "nearest_resistance": None,
            "support_distance_percent": None,
            "resistance_distance_percent": None,
            "support_near": False,
            "resistance_near": False,
        }

    # ============================================================
    # CONFIGURATION
    # ============================================================

    lookback = 3

    # Maximum distance at which a level is considered relevant.
    relevance_percent = 12.0

    # Level is considered "near" within this distance.
    proximity_percent = 2.0

    # ============================================================
    # FIND SWINGS
    # ============================================================

    highs = []
    lows = []

    for i in range(
        lookback,
        len(df) - lookback,
    ):

        # --------------------------------------------------------
        # Swing High
        # --------------------------------------------------------

        try:

            high = float(
                df["High"].iloc[i]
            )

            surrounding_highs = (
                df["High"].iloc[
                    i - lookback:
                    i + lookback + 1
                ]
            )

            if high == float(
                surrounding_highs.max()
            ):

                highs.append(high)

        except (
            TypeError,
            ValueError,
        ):

            continue

        # --------------------------------------------------------
        # Swing Low
        # --------------------------------------------------------

        try:

            low = float(
                df["Low"].iloc[i]
            )

            surrounding_lows = (
                df["Low"].iloc[
                    i - lookback:
                    i + lookback + 1
                ]
            )

            if low == float(
                surrounding_lows.min()
            ):

                lows.append(low)

        except (
            TypeError,
            ValueError,
        ):

            continue

    # ============================================================
    # REMOVE DUPLICATES
    # ============================================================

    highs = sorted(
        set(
            round(level, 2)
            for level in highs
            if level > 0
        )
    )

    lows = sorted(
        set(
            round(level, 2)
            for level in lows
            if level > 0
        )
    )

    # ============================================================
    # PRICE-AWARE FILTERING
    # ============================================================

    supports = []

    resistances = []

    for level in lows:

        if level < current_price:

            distance = (
                (current_price - level)
                / current_price
            ) * 100

            if distance <= relevance_percent:

                supports.append(level)

    for level in highs:

        if level > current_price:

            distance = (
                (level - current_price)
                / current_price
            ) * 100

            if distance <= relevance_percent:

                resistances.append(level)

    # ============================================================
    # NEAREST LEVELS
    # ============================================================

    nearest_support = (
        max(supports)
        if supports
        else None
    )

    nearest_resistance = (
        min(resistances)
        if resistances
        else None
    )

    # ============================================================
    # DISTANCES
    # ============================================================

    support_distance_percent = None

    resistance_distance_percent = None

    if nearest_support is not None:

        support_distance_percent = round(
            (
                (
                    current_price
                    - nearest_support
                )
                / current_price
            )
            * 100,
            2,
        )

    if nearest_resistance is not None:

        resistance_distance_percent = round(
            (
                (
                    nearest_resistance
                    - current_price
                )
                / current_price
            )
            * 100,
            2,
        )

    # ============================================================
    # PROXIMITY
    # ============================================================

    support_near = (
        support_distance_percent is not None
        and support_distance_percent
        <= proximity_percent
    )

    resistance_near = (
        resistance_distance_percent is not None
        and resistance_distance_percent
        <= proximity_percent
    )

    # ============================================================
    # SELECT LEVELS
    # ============================================================

    # Closest supports first.
    supports = sorted(
        supports,
        key=lambda level: abs(
            current_price - level
        ),
    )[:3]

    # Closest resistances first.
    resistances = sorted(
        resistances,
        key=lambda level: abs(
            level - current_price
        ),
    )[:3]

    # ============================================================
    # FINAL RESPONSE
    # ============================================================

    return {

        "support": [
            round(level, 2)
            for level in supports
        ],

        "resistance": [
            round(level, 2)
            for level in resistances
        ],

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

        "support_distance_percent": (
            support_distance_percent
        ),

        "resistance_distance_percent": (
            resistance_distance_percent
        ),

        "support_near": support_near,

        "resistance_near": resistance_near,
    }