import pandas as pd
import numpy as np


# ============================================================
# MARKETIQ SMART MONEY CONCEPTS SERVICE
# ============================================================
#
# Improvements:
#
# 1. BOS / CHOCH:
#    - Uses recent confirmed swings.
#    - Avoids treating very old structure as a fresh signal.
#
# 2. ORDER BLOCK / FVG:
#    - Detects zones but only gives scoring weight to
#      zones that are relevant to the current price.
#
# 3. SMC SCORING / EXPLANATION:
#    - Historical zones are reported separately.
#    - Price-relevant zones contribute to the final signal.
#    - Reasons clearly distinguish confirmation,
#      support and resistance.
#
# ============================================================


# ============================================================
# CONFIGURATION
# ============================================================

SWING_LOOKBACK = 2

STRUCTURE_LOOKBACK = 30

ZONE_LOOKBACK = 50

PRICE_PROXIMITY = 0.02       # 2%

LIQUIDITY_TOLERANCE = 0.005   # 0.5%


# ============================================================
# SAFE FLOAT
# ============================================================

def _safe_float(value, default=0.0):

    try:

        if value is None:
            return default

        value = float(value)

        if np.isnan(value) or np.isinf(value):
            return default

        return value

    except (TypeError, ValueError):

        return default


# ============================================================
# PRICE PROXIMITY
# ============================================================

def _is_price_near_zone(
    current_price,
    zone_low,
    zone_high,
    proximity=PRICE_PROXIMITY,
):

    current_price = _safe_float(
        current_price
    )

    zone_low = _safe_float(
        zone_low
    )

    zone_high = _safe_float(
        zone_high
    )

    if current_price <= 0:
        return False

    if zone_low > zone_high:

        zone_low, zone_high = (
            zone_high,
            zone_low,
        )

    # --------------------------------------------------------
    # Price is inside the zone
    # --------------------------------------------------------

    if (
        zone_low
        <= current_price
        <= zone_high
    ):
        return True

    # --------------------------------------------------------
    # Price is close to the zone
    # --------------------------------------------------------

    distance = min(
        abs(current_price - zone_low),
        abs(current_price - zone_high),
    )

    return (
        distance / current_price
    ) <= proximity


# ============================================================
# SWING POINT DETECTION
# ============================================================

def detect_swings(
    df: pd.DataFrame,
    lookback: int = SWING_LOOKBACK,
):

    if df is None or df.empty:

        return {
            "swing_highs": [],
            "swing_lows": [],
        }

    if len(df) < (
        lookback * 2 + 1
    ):

        return {
            "swing_highs": [],
            "swing_lows": [],
        }

    highs = []
    lows = []

    for i in range(
        lookback,
        len(df) - lookback,
    ):

        current_high = _safe_float(
            df.iloc[i]["High"]
        )

        current_low = _safe_float(
            df.iloc[i]["Low"]
        )

        left_highs = [
            _safe_float(
                df.iloc[j]["High"]
            )
            for j in range(
                i - lookback,
                i,
            )
        ]

        right_highs = [
            _safe_float(
                df.iloc[j]["High"]
            )
            for j in range(
                i + 1,
                i + lookback + 1,
            )
        ]

        left_lows = [
            _safe_float(
                df.iloc[j]["Low"]
            )
            for j in range(
                i - lookback,
                i,
            )
        ]

        right_lows = [
            _safe_float(
                df.iloc[j]["Low"]
            )
            for j in range(
                i + 1,
                i + lookback + 1,
            )
        ]

        # ----------------------------------------------------
        # Swing high
        # ----------------------------------------------------

        if (
            current_high > max(left_highs)
            and current_high > max(right_highs)
        ):

            highs.append(
                {
                    "index": i,
                    "price": current_high,
                }
            )

        # ----------------------------------------------------
        # Swing low
        # ----------------------------------------------------

        if (
            current_low < min(left_lows)
            and current_low < min(right_lows)
        ):

            lows.append(
                {
                    "index": i,
                    "price": current_low,
                }
            )

    return {
        "swing_highs": highs,
        "swing_lows": lows,
    }


# ============================================================
# RECENT CONFIRMED SWINGS
# ============================================================

def _get_recent_swings(
    swings,
    data_length,
    lookback=STRUCTURE_LOOKBACK,
):

    minimum_index = max(
        0,
        data_length - lookback,
    )

    recent_highs = [
        swing
        for swing in swings.get(
            "swing_highs",
            [],
        )
        if swing["index"] >= minimum_index
        and swing["index"] < data_length - 1
    ]

    recent_lows = [
        swing
        for swing in swings.get(
            "swing_lows",
            [],
        )
        if swing["index"] >= minimum_index
        and swing["index"] < data_length - 1
    ]

    return (
        recent_highs,
        recent_lows,
    )


# ============================================================
# BREAK OF STRUCTURE
# ============================================================

def detect_bos(
    df: pd.DataFrame,
    swings: dict,
):

    if df is None or df.empty:

        return {
            "detected": False,
            "type": None,
            "price": None,
            "index": None,
            "reason": "No market data available.",
        }

    close = _safe_float(
        df.iloc[-1]["Close"]
    )

    recent_highs, recent_lows = (
        _get_recent_swings(
            swings,
            len(df),
        )
    )

    # ========================================================
    # IMPORTANT:
    #
    # Only the latest confirmed swing is considered.
    # This prevents an old swing from generating a
    # misleading "recent BOS".
    # ========================================================

    latest_high = (
        recent_highs[-1]
        if recent_highs
        else None
    )

    latest_low = (
        recent_lows[-1]
        if recent_lows
        else None
    )

    # --------------------------------------------------------
    # Bullish BOS
    # --------------------------------------------------------

    if latest_high is not None:

        if close > latest_high["price"]:

            return {
                "detected": True,
                "type": "BULLISH_BOS",
                "price": latest_high["price"],
                "index": latest_high["index"],
                "reason": (
                    f"Price {close:.2f} broke above "
                    f"the recent confirmed swing high "
                    f"{latest_high['price']:.2f}."
                ),
            }

    # --------------------------------------------------------
    # Bearish BOS
    # --------------------------------------------------------

    if latest_low is not None:

        if close < latest_low["price"]:

            return {
                "detected": True,
                "type": "BEARISH_BOS",
                "price": latest_low["price"],
                "index": latest_low["index"],
                "reason": (
                    f"Price {close:.2f} broke below "
                    f"the recent confirmed swing low "
                    f"{latest_low['price']:.2f}."
                ),
            }

    return {
        "detected": False,
        "type": None,
        "price": None,
        "index": None,
        "reason": (
            "No recent Break of Structure detected."
        ),
    }


# ============================================================
# CHANGE OF CHARACTER
# ============================================================

def detect_choch(
    df: pd.DataFrame,
    swings: dict,
):

    if df is None or df.empty:

        return {
            "detected": False,
            "type": None,
            "price": None,
            "reason": "No market data available.",
        }

    recent_highs, recent_lows = (
        _get_recent_swings(
            swings,
            len(df),
        )
    )

    if (
        len(recent_highs) < 2
        or len(recent_lows) < 2
    ):

        return {
            "detected": False,
            "type": None,
            "price": None,
            "reason": (
                "Insufficient recent swing data "
                "for Change of Character."
            ),
        }

    close = _safe_float(
        df.iloc[-1]["Close"]
    )

    previous_high = (
        recent_highs[-2]["price"]
    )

    latest_high = (
        recent_highs[-1]["price"]
    )

    previous_low = (
        recent_lows[-2]["price"]
    )

    latest_low = (
        recent_lows[-1]["price"]
    )

    # ========================================================
    # Bullish CHOCH
    # ========================================================

    if (
        latest_low < previous_low
        and close > previous_high
    ):

        return {
            "detected": True,
            "type": "BULLISH_CHOCH",
            "price": previous_high,
            "reason": (
                "Price formed a lower low and "
                "then reclaimed the previous swing high, "
                "indicating a possible bullish character change."
            ),
        }

    # ========================================================
    # Bearish CHOCH
    # ========================================================

    if (
        latest_high > previous_high
        and close < previous_low
    ):

        return {
            "detected": True,
            "type": "BEARISH_CHOCH",
            "price": previous_low,
            "reason": (
                "Price formed a higher high and "
                "then broke the previous swing low, "
                "indicating a possible bearish character change."
            ),
        }

    return {
        "detected": False,
        "type": None,
        "price": None,
        "reason": (
            "No clear recent Change of Character detected."
        ),
    }


# ============================================================
# ORDER BLOCK DETECTION
# ============================================================

def detect_order_blocks(
    df: pd.DataFrame,
    lookback: int = ZONE_LOOKBACK,
):

    if df is None or df.empty:

        return {
            "bullish": [],
            "bearish": [],
        }

    bullish = []
    bearish = []

    start = max(
        1,
        len(df) - lookback,
    )

    for i in range(
        start,
        len(df),
    ):

        previous = df.iloc[i - 1]
        current = df.iloc[i]

        previous_open = _safe_float(
            previous["Open"]
        )

        previous_close = _safe_float(
            previous["Close"]
        )

        previous_high = _safe_float(
            previous["High"]
        )

        previous_low = _safe_float(
            previous["Low"]
        )

        current_close = _safe_float(
            current["Close"]
        )

        # ----------------------------------------------------
        # Bullish order block
        # ----------------------------------------------------

        if (
            previous_close < previous_open
            and current_close > previous_high
        ):

            bullish.append(
                {
                    "index": i - 1,
                    "high": round(
                        previous_high,
                        2,
                    ),
                    "low": round(
                        previous_low,
                        2,
                    ),
                    "price": round(
                        previous_low,
                        2,
                    ),
                    "type":
                        "BULLISH_ORDER_BLOCK",
                }
            )

        # ----------------------------------------------------
        # Bearish order block
        # ----------------------------------------------------

        if (
            previous_close > previous_open
            and current_close < previous_low
        ):

            bearish.append(
                {
                    "index": i - 1,
                    "high": round(
                        previous_high,
                        2,
                    ),
                    "low": round(
                        previous_low,
                        2,
                    ),
                    "price": round(
                        previous_high,
                        2,
                    ),
                    "type":
                        "BEARISH_ORDER_BLOCK",
                }
            )

    return {
        "bullish": bullish[-5:],
        "bearish": bearish[-5:],
    }


# ============================================================
# FILTER PRICE-RELEVANT ORDER BLOCKS
# ============================================================

def get_relevant_order_blocks(
    df: pd.DataFrame,
    order_blocks: dict,
):

    current_price = _safe_float(
        df.iloc[-1]["Close"]
    )

    bullish_relevant = [
        zone
        for zone in order_blocks.get(
            "bullish",
            [],
        )
        if _is_price_near_zone(
            current_price,
            zone["low"],
            zone["high"],
        )
    ]

    bearish_relevant = [
        zone
        for zone in order_blocks.get(
            "bearish",
            [],
        )
        if _is_price_near_zone(
            current_price,
            zone["low"],
            zone["high"],
        )
    ]

    return {
        "bullish": bullish_relevant,
        "bearish": bearish_relevant,
    }


# ============================================================
# LIQUIDITY DETECTION
# ============================================================

def detect_liquidity(
    df: pd.DataFrame,
    swings: dict,
    tolerance: float = LIQUIDITY_TOLERANCE,
):

    if df is None or df.empty:

        return {
            "buy_side": [],
            "sell_side": [],
        }

    buy_side = []
    sell_side = []

    swing_highs = swings.get(
        "swing_highs",
        [],
    )

    swing_lows = swings.get(
        "swing_lows",
        [],
    )

    # --------------------------------------------------------
    # Buy-side liquidity
    # --------------------------------------------------------

    if len(swing_highs) >= 2:

        for i in range(
            1,
            len(swing_highs),
        ):

            previous = swing_highs[
                i - 1
            ]["price"]

            current = swing_highs[
                i
            ]["price"]

            average = abs(
                current + previous
            ) / 2

            if average <= 0:
                continue

            percentage = (
                abs(current - previous)
                / average
            )

            if percentage <= tolerance:

                liquidity_price = max(
                    current,
                    previous,
                )

                buy_side.append(
                    {
                        "price": round(
                            liquidity_price,
                            2,
                        ),
                        "type":
                            "BUY_SIDE_LIQUIDITY",
                    }
                )

    # --------------------------------------------------------
    # Sell-side liquidity
    # --------------------------------------------------------

    if len(swing_lows) >= 2:

        for i in range(
            1,
            len(swing_lows),
        ):

            previous = swing_lows[
                i - 1
            ]["price"]

            current = swing_lows[
                i
            ]["price"]

            average = abs(
                current + previous
            ) / 2

            if average <= 0:
                continue

            percentage = (
                abs(current - previous)
                / average
            )

            if percentage <= tolerance:

                liquidity_price = min(
                    current,
                    previous,
                )

                sell_side.append(
                    {
                        "price": round(
                            liquidity_price,
                            2,
                        ),
                        "type":
                            "SELL_SIDE_LIQUIDITY",
                    }
                )

    return {
        "buy_side": buy_side[-5:],
        "sell_side": sell_side[-5:],
    }


# ============================================================
# FAIR VALUE GAP
# ============================================================

def detect_fvg(
    df: pd.DataFrame,
    lookback: int = ZONE_LOOKBACK,
):

    if df is None or len(df) < 3:

        return {
            "bullish": [],
            "bearish": [],
        }

    bullish = []
    bearish = []

    start = max(
        2,
        len(df) - lookback,
    )

    for i in range(
        start,
        len(df),
    ):

        candle_one = df.iloc[i - 2]
        candle_three = df.iloc[i]

        first_high = _safe_float(
            candle_one["High"]
        )

        first_low = _safe_float(
            candle_one["Low"]
        )

        third_high = _safe_float(
            candle_three["High"]
        )

        third_low = _safe_float(
            candle_three["Low"]
        )

        # ----------------------------------------------------
        # Bullish FVG
        # ----------------------------------------------------

        if third_low > first_high:

            bullish.append(
                {
                    "index": i,
                    "low": round(
                        first_high,
                        2,
                    ),
                    "high": round(
                        third_low,
                        2,
                    ),
                    "type":
                        "BULLISH_FVG",
                }
            )

        # ----------------------------------------------------
        # Bearish FVG
        # ----------------------------------------------------

        if third_high < first_low:

            bearish.append(
                {
                    "index": i,
                    "low": round(
                        third_high,
                        2,
                    ),
                    "high": round(
                        first_low,
                        2,
                    ),
                    "type":
                        "BEARISH_FVG",
                }
            )

    return {
        "bullish": bullish[-5:],
        "bearish": bearish[-5:],
    }


# ============================================================
# FILTER PRICE-RELEVANT FVGs
# ============================================================

def get_relevant_fvg(
    df: pd.DataFrame,
    fvg: dict,
):

    current_price = _safe_float(
        df.iloc[-1]["Close"]
    )

    bullish_relevant = [
        zone
        for zone in fvg.get(
            "bullish",
            [],
        )
        if _is_price_near_zone(
            current_price,
            zone["low"],
            zone["high"],
        )
    ]

    bearish_relevant = [
        zone
        for zone in fvg.get(
            "bearish",
            [],
        )
        if _is_price_near_zone(
            current_price,
            zone["low"],
            zone["high"],
        )
    ]

    return {
        "bullish": bullish_relevant,
        "bearish": bearish_relevant,
    }


# ============================================================
# LIQUIDITY RELEVANCE
# ============================================================

def get_relevant_liquidity(
    df: pd.DataFrame,
    liquidity: dict,
):

    current_price = _safe_float(
        df.iloc[-1]["Close"]
    )

    buy_side_relevant = [
        zone
        for zone in liquidity.get(
            "buy_side",
            [],
        )
        if (
            current_price > 0
            and abs(
                zone["price"]
                - current_price
            )
            / current_price
            <= PRICE_PROXIMITY
        )
    ]

    sell_side_relevant = [
        zone
        for zone in liquidity.get(
            "sell_side",
            [],
        )
        if (
            current_price > 0
            and abs(
                zone["price"]
                - current_price
            )
            / current_price
            <= PRICE_PROXIMITY
        )
    ]

    return {
        "buy_side": buy_side_relevant,
        "sell_side": sell_side_relevant,
    }


# ============================================================
# MARKET BIAS FROM SMC
# ============================================================

def determine_smc_bias(
    bos,
    choch,
    relevant_order_blocks,
    relevant_liquidity,
    relevant_fvg,
):

    bullish = 0
    bearish = 0

    # --------------------------------------------------------
    # BOS
    # --------------------------------------------------------

    if bos.get("type") == "BULLISH_BOS":
        bullish += 3

    elif bos.get("type") == "BEARISH_BOS":
        bearish += 3

    # --------------------------------------------------------
    # CHOCH
    # --------------------------------------------------------

    if choch.get("type") == "BULLISH_CHOCH":
        bullish += 3

    elif choch.get("type") == "BEARISH_CHOCH":
        bearish += 3

    # --------------------------------------------------------
    # Relevant order blocks
    # --------------------------------------------------------

    if relevant_order_blocks.get(
        "bullish"
    ):
        bullish += 1

    if relevant_order_blocks.get(
        "bearish"
    ):
        bearish += 1

    # --------------------------------------------------------
    # Relevant FVG
    # --------------------------------------------------------

    if relevant_fvg.get(
        "bullish"
    ):
        bullish += 1

    if relevant_fvg.get(
        "bearish"
    ):
        bearish += 1

    # --------------------------------------------------------
    # Liquidity is informational.
    #
    # It does NOT automatically create BUY/SELL bias.
    # --------------------------------------------------------

    if bullish > bearish:

        bias = "BULLISH"

    elif bearish > bullish:

        bias = "BEARISH"

    else:

        bias = "NEUTRAL"

    total = (
        bullish
        + bearish
    )

    if total == 0:

        confidence = 50

    else:

        confidence = min(
            95,
            int(
                50
                + (
                    abs(
                        bullish
                        - bearish
                    )
                    / total
                )
                * 45
            ),
        )

    return {
        "bias": bias,
        "bullish_score": bullish,
        "bearish_score": bearish,
        "confidence": confidence,
    }


# ============================================================
# SMC SIGNAL
# ============================================================

def generate_smc_signal(
    bos,
    choch,
    order_blocks,
    relevant_order_blocks,
    liquidity,
    relevant_liquidity,
    fvg,
    relevant_fvg,
):

    bullish_score = 0
    bearish_score = 0

    reasons = []

    # ========================================================
    # BOS
    # ========================================================

    if bos.get(
        "type"
    ) == "BULLISH_BOS":

        bullish_score += 3

        reasons.append(
            "Bullish Break of Structure "
            "detected on recent price action."
        )

    elif bos.get(
        "type"
    ) == "BEARISH_BOS":

        bearish_score += 3

        reasons.append(
            "Bearish Break of Structure "
            "detected on recent price action."
        )

    else:

        reasons.append(
            "No recent Break of Structure detected."
        )

    # ========================================================
    # CHOCH
    # ========================================================

    if choch.get(
        "type"
    ) == "BULLISH_CHOCH":

        bullish_score += 3

        reasons.append(
            "Bullish Change of Character detected."
        )

    elif choch.get(
        "type"
    ) == "BEARISH_CHOCH":

        bearish_score += 3

        reasons.append(
            "Bearish Change of Character detected."
        )

    else:

        reasons.append(
            "No clear recent Change of Character detected."
        )

    # ========================================================
    # ORDER BLOCKS
    # ========================================================

    bullish_ob = relevant_order_blocks.get(
        "bullish",
        [],
    )

    bearish_ob = relevant_order_blocks.get(
        "bearish",
        [],
    )

    historical_bullish_ob = order_blocks.get(
        "bullish",
        [],
    )

    historical_bearish_ob = order_blocks.get(
        "bearish",
        [],
    )

    # --------------------------------------------------------
    # Relevant bullish OB
    # --------------------------------------------------------

    if bullish_ob:

        bullish_score += 1

        reasons.append(
            f"Bullish order-block support is near "
            f"current price "
            f"({len(bullish_ob)} relevant zone(s))."
        )

    elif historical_bullish_ob:

        reasons.append(
            "Bullish order blocks exist historically, "
            "but none are close enough to current price "
            "to provide strong confirmation."
        )

    # --------------------------------------------------------
    # Relevant bearish OB
    # --------------------------------------------------------

    if bearish_ob:

        bearish_score += 1

        reasons.append(
            f"Bearish order-block resistance is near "
            f"current price "
            f"({len(bearish_ob)} relevant zone(s))."
        )

    elif historical_bearish_ob:

        reasons.append(
            "Bearish order blocks exist historically, "
            "but none are close enough to current price "
            "to provide strong confirmation."
        )

    # ========================================================
    # LIQUIDITY
    # ========================================================

    buy_side = liquidity.get(
        "buy_side",
        [],
    )

    sell_side = liquidity.get(
        "sell_side",
        [],
    )

    relevant_buy_side = relevant_liquidity.get(
        "buy_side",
        [],
    )

    relevant_sell_side = relevant_liquidity.get(
        "sell_side",
        [],
    )

    # --------------------------------------------------------
    # Liquidity does NOT automatically add score.
    # --------------------------------------------------------

    if relevant_buy_side:

        reasons.append(
            f"Buy-side liquidity is nearby "
            f"({len(relevant_buy_side)} zone(s))."
        )

    elif buy_side:

        reasons.append(
            "Buy-side liquidity exists, "
            "but it is not close enough to current price "
            "to act as a strong confirmation."
        )

    if relevant_sell_side:

        reasons.append(
            f"Sell-side liquidity is nearby "
            f"({len(relevant_sell_side)} zone(s))."
        )

    elif sell_side:

        reasons.append(
            "Sell-side liquidity exists, "
            "but it is not close enough to current price "
            "to act as a strong confirmation."
        )

    # ========================================================
    # FVG
    # ========================================================

    bullish_fvg = relevant_fvg.get(
        "bullish",
        [],
    )

    bearish_fvg = relevant_fvg.get(
        "bearish",
        [],
    )

    historical_bullish_fvg = fvg.get(
        "bullish",
        [],
    )

    historical_bearish_fvg = fvg.get(
        "bearish",
        [],
    )

    # --------------------------------------------------------
    # Relevant bullish FVG
    # --------------------------------------------------------

    if bullish_fvg:

        bullish_score += 1

        reasons.append(
            f"Bullish Fair Value Gap support is near "
            f"current price "
            f"({len(bullish_fvg)} relevant gap(s))."
        )

    elif historical_bullish_fvg:

        reasons.append(
            "Bullish Fair Value Gaps exist historically, "
            "but none are currently price-relevant."
        )

    # --------------------------------------------------------
    # Relevant bearish FVG
    # --------------------------------------------------------

    if bearish_fvg:

        bearish_score += 1

        reasons.append(
            f"Bearish Fair Value Gap resistance is near "
            f"current price "
            f"({len(bearish_fvg)} relevant gap(s))."
        )

    elif historical_bearish_fvg:

        reasons.append(
            "Bearish Fair Value Gaps exist historically, "
            "but none are currently price-relevant."
        )

    # ========================================================
    # FINAL SIGNAL
    # ========================================================

    total = (
        bullish_score
        + bearish_score
    )

    if total == 0:

        signal = "HOLD"
        confidence = 50

    else:

        difference = (
            bullish_score
            - bearish_score
        )

        if difference > 0:

            signal = "BUY"

        elif difference < 0:

            signal = "SELL"

        else:

            signal = "HOLD"

        confidence = min(
            95,
            int(
                50
                + (
                    abs(difference)
                    / total
                )
                * 45
            ),
        )

    # ========================================================
    # SIGNAL SUMMARY
    # ========================================================

    if signal == "BUY":

        reasons.append(
            f"SMC overall signal is BUY "
            f"({confidence}% confidence) based on "
            f"{bullish_score} bullish vs "
            f"{bearish_score} bearish confirmations."
        )

    elif signal == "SELL":

        reasons.append(
            f"SMC overall signal is SELL "
            f"({confidence}% confidence) based on "
            f"{bearish_score} bearish vs "
            f"{bullish_score} bullish confirmations."
        )

    else:

        reasons.append(
            f"SMC overall signal is HOLD "
            f"({confidence}% confidence) because "
            f"the relevant confirmations are balanced "
            f"or insufficient."
        )

    return {
        "signal": signal,

        "score": (
            bullish_score
            - bearish_score
        ),

        "confidence": confidence,

        "bullish_score": bullish_score,

        "bearish_score": bearish_score,

        "reasons": reasons,
    }


# ============================================================
# MAIN SMC ANALYSIS
# ============================================================

def analyze_smc(
    df: pd.DataFrame,
):

    # ========================================================
    # EMPTY DATA
    # ========================================================

    if df is None or df.empty:

        return {
            "success": False,

            "signal": "HOLD",

            "confidence": 0,

            "score": 0,

            "bullish_score": 0,

            "bearish_score": 0,

            "market_bias": "NEUTRAL",

            "trend": "NEUTRAL",

            "structure": "NEUTRAL",

            "message":
                "No market data available.",

            "break_of_structure": {
                "detected": False,
                "type": None,
                "price": None,
                "index": None,
                "reason":
                    "No market data available.",
            },

            "change_of_character": {
                "detected": False,
                "type": None,
                "price": None,
                "reason":
                    "No market data available.",
            },

            "order_blocks": {
                "bullish": [],
                "bearish": [],
            },

            "relevant_order_blocks": {
                "bullish": [],
                "bearish": [],
            },

            "liquidity": {
                "buy_side": [],
                "sell_side": [],
            },

            "relevant_liquidity": {
                "buy_side": [],
                "sell_side": [],
            },

            "fair_value_gaps": {
                "bullish": [],
                "bearish": [],
            },

            "relevant_fair_value_gaps": {
                "bullish": [],
                "bearish": [],
            },

            "reasons": [],
        }

    # ========================================================
    # CURRENT PRICE
    # ========================================================

    current_price = _safe_float(
        df.iloc[-1]["Close"]
    )

    # ========================================================
    # DETECT SWINGS
    # ========================================================

    swings = detect_swings(
        df
    )

    # ========================================================
    # BOS
    # ========================================================

    bos = detect_bos(
        df,
        swings,
    )

    # ========================================================
    # CHOCH
    # ========================================================

    choch = detect_choch(
        df,
        swings,
    )

    # ========================================================
    # ORDER BLOCKS
    # ========================================================

    order_blocks = detect_order_blocks(
        df
    )

    relevant_order_blocks = (
        get_relevant_order_blocks(
            df,
            order_blocks,
        )
    )

    # ========================================================
    # LIQUIDITY
    # ========================================================

    liquidity = detect_liquidity(
        df,
        swings,
    )

    relevant_liquidity = (
        get_relevant_liquidity(
            df,
            liquidity,
        )
    )

    # ========================================================
    # FAIR VALUE GAPS
    # ========================================================

    fvg = detect_fvg(
        df
    )

    relevant_fvg = get_relevant_fvg(
        df,
        fvg,
    )

    # ========================================================
    # GENERATE SMC SIGNAL
    # ========================================================

    signal = generate_smc_signal(
        bos=bos,
        choch=choch,
        order_blocks=order_blocks,
        relevant_order_blocks=relevant_order_blocks,
        liquidity=liquidity,
        relevant_liquidity=relevant_liquidity,
        fvg=fvg,
        relevant_fvg=relevant_fvg,
    )

    # ========================================================
    # DETERMINE BIAS
    # ========================================================

    bias = determine_smc_bias(
        bos=bos,
        choch=choch,
        relevant_order_blocks=
            relevant_order_blocks,
        relevant_liquidity=
            relevant_liquidity,
        relevant_fvg=
            relevant_fvg,
    )

    # ========================================================
    # MARKET STRUCTURE
    # ========================================================

    if bos.get(
        "type"
    ) == "BULLISH_BOS":

        structure = "Bullish"

    elif bos.get(
        "type"
    ) == "BEARISH_BOS":

        structure = "Bearish"

    elif choch.get(
        "type"
    ) == "BULLISH_CHOCH":

        structure = "Bullish"

    elif choch.get(
        "type"
    ) == "BEARISH_CHOCH":

        structure = "Bearish"

    else:

        structure = "Neutral"

    # ========================================================
    # FINAL RESULT
    # ========================================================

    return {

        "success": True,

        # ----------------------------------------------------
        # SIGNAL
        # ----------------------------------------------------

        "signal":
            signal["signal"],

        "confidence":
            signal["confidence"],

        "score":
            signal["score"],

        "bullish_score":
            signal["bullish_score"],

        "bearish_score":
            signal["bearish_score"],

        # ----------------------------------------------------
        # CURRENT PRICE
        # ----------------------------------------------------

        "current_price":
            round(
                current_price,
                2,
            ),

        # ----------------------------------------------------
        # FRONTEND SUMMARY
        # ----------------------------------------------------

        "market_bias":
            bias["bias"],

        "trend":
            bias["bias"],

        "structure":
            structure,

        # ----------------------------------------------------
        # BOS
        # ----------------------------------------------------

        "break_of_structure":
            bos,

        # ----------------------------------------------------
        # CHOCH
        # ----------------------------------------------------

        "change_of_character":
            choch,

        # ----------------------------------------------------
        # ALL ORDER BLOCKS
        # ----------------------------------------------------

        "order_blocks":
            order_blocks,

        # ----------------------------------------------------
        # PRICE-RELEVANT ORDER BLOCKS
        # ----------------------------------------------------

        "relevant_order_blocks":
            relevant_order_blocks,

        # ----------------------------------------------------
        # ALL LIQUIDITY
        # ----------------------------------------------------

        "liquidity":
            liquidity,

        # ----------------------------------------------------
        # PRICE-RELEVANT LIQUIDITY
        # ----------------------------------------------------

        "relevant_liquidity":
            relevant_liquidity,

        # ----------------------------------------------------
        # ALL FVG
        # ----------------------------------------------------

        "fair_value_gaps":
            fvg,

        # ----------------------------------------------------
        # PRICE-RELEVANT FVG
        # ----------------------------------------------------

        "relevant_fair_value_gaps":
            relevant_fvg,

        # ----------------------------------------------------
        # SWINGS
        # ----------------------------------------------------

        "swings":
            swings,

        # ----------------------------------------------------
        # EXPLANATION
        # ----------------------------------------------------

        "reasons":
            signal["reasons"],
    }