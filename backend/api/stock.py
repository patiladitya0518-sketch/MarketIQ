from fastapi import APIRouter

from services.data_service import (
    get_stock_history,
    get_live_price,
    resolve_symbol,
)

from services.indicator_service import calculate_indicators
from services.recommendation_service import generate_recommendation
from services.pattern_service import detect_pattern
from services.market_structure_service import detect_market_structure
from services.support_resistance_service import (
    calculate_support_resistance,
)

from services.smc_service import analyze_smc


router = APIRouter(
    prefix="/stock",
    tags=["Stock"],
)


@router.get("/{symbol}")
def stock(symbol: str):

    # ============================================================
    # CLEAN INPUT
    # ============================================================

    symbol = symbol.strip()

    if not symbol:
        return {
            "success": False,
            "message": (
                "Please enter a stock symbol "
                "or company name."
            ),
        }

    # ============================================================
    # RESOLVE SYMBOL
    # ============================================================

    resolved_symbol = resolve_symbol(symbol)

    if not resolved_symbol:
        return {
            "success": False,
            "message": (
                f"Unable to find '{symbol}' "
                "in supported Indian market data."
            ),
        }

    # ============================================================
    # HISTORICAL DATA
    # ============================================================

    df = get_stock_history(resolved_symbol)

    if df.empty:
        return {
            "success": False,
            "message": (
                "Historical market data is unavailable "
                f"for '{resolved_symbol}'."
            ),
        }

    # ============================================================
    # TECHNICAL INDICATORS
    # ============================================================

    df = calculate_indicators(df)

    if df.empty:
        return {
            "success": False,
            "message": (
                "Unable to calculate indicators "
                f"for '{resolved_symbol}'."
            ),
        }

    latest = df.iloc[-1]

    # ============================================================
    # SAFE HELPERS
    # ============================================================

    def safe_float(value, default=0.0):

        try:

            if value is None:
                return default

            number = float(value)

            if number != number:
                return default

            return number

        except (TypeError, ValueError):

            return default

    def safe_bool(value):

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

    # ============================================================
    # INDICATORS
    # ============================================================

    historical_close = safe_float(
        latest.get("Close"),
        0,
    )

    rsi = safe_float(
        latest.get("RSI"),
        50,
    )

    ema20 = safe_float(
        latest.get("EMA20"),
        historical_close,
    )

    ema50 = safe_float(
        latest.get("EMA50"),
        historical_close,
    )

    macd = safe_float(
        latest.get("MACD"),
        0,
    )

    macd_signal = safe_float(
        latest.get("MACD_SIGNAL"),
        0,
    )

    macd_bullish_crossover = safe_bool(
        latest.get(
            "MACD_BULLISH_CROSSOVER",
            False,
        )
    )

    macd_bearish_crossover = safe_bool(
        latest.get(
            "MACD_BEARISH_CROSSOVER",
            False,
        )
    )

    indicators = {

        "Close": historical_close,

        "RSI": rsi,

        "EMA20": ema20,

        "EMA50": ema50,

        "MACD": macd,

        "MACD_SIGNAL": macd_signal,

        "MACD_BULLISH_CROSSOVER": (
            macd_bullish_crossover
        ),

        "MACD_BEARISH_CROSSOVER": (
            macd_bearish_crossover
        ),
    }

    # ============================================================
    # LIVE PRICE
    # ============================================================

    try:

        live_price = get_live_price(
            resolved_symbol
        )

    except Exception:

        live_price = None

    if live_price is None:

        live_price = historical_close

    live_price = safe_float(
        live_price,
        historical_close,
    )

    # ============================================================
    # RECOMMENDATION INPUT
    # ============================================================

    recommendation_indicators = {
        **indicators,
        "Close": live_price,
    }

    # ============================================================
    # CANDLESTICK PATTERN
    # ============================================================

    try:

        pattern = detect_pattern(df)

    except Exception as error:

        pattern = {
            "pattern": "Unknown",
            "signal": "HOLD",
            "confidence": 0,
            "reason": [
                f"Pattern analysis unavailable: {error}"
            ],
        }

    # ============================================================
    # MARKET STRUCTURE
    # ============================================================

    try:

        market_structure = (
            detect_market_structure(df)
        )

    except Exception as error:

        market_structure = {
            "structure": "Neutral",
            "trend": "NEUTRAL",
            "signal": "HOLD",
            "confidence": 0,
            "swing_counts": {
                "higher_high": 0,
                "higher_low": 0,
                "lower_high": 0,
                "lower_low": 0,
            },
            "swings": [],
            "reasons": [
                f"Market structure unavailable: {error}"
            ],
        }

    # ============================================================
    # SUPPORT & RESISTANCE
    # ============================================================

    try:

        support_resistance = (
            calculate_support_resistance(df)
        )

    except Exception as error:

        support_resistance = {
            "support": [],
            "resistance": [],
            "error": str(error),
        }

    # ============================================================
    # SMART MONEY CONCEPTS
    # ============================================================

    try:

        smc = analyze_smc(df)

    except Exception as error:

        smc = {
            "success": False,
            "signal": "HOLD",
            "confidence": 0,
            "score": 0,
            "bullish_score": 0,
            "bearish_score": 0,

            "break_of_structure": {
                "detected": False,
                "type": None,
                "price": None,
                "index": None,
                "reason": (
                    "SMC analysis unavailable."
                ),
            },

            "change_of_character": {
                "detected": False,
                "type": None,
                "price": None,
                "reason": (
                    "SMC analysis unavailable."
                ),
            },

            "order_blocks": {
                "bullish": [],
                "bearish": [],
            },

            "liquidity": {
                "buy_side": [],
                "sell_side": [],
            },

            "fair_value_gaps": {
                "bullish": [],
                "bearish": [],
            },

            "reasons": [
                f"SMC analysis unavailable: {error}"
            ],
        }

    # ============================================================
    # AI RECOMMENDATION
    # ============================================================
    #
    # IMPORTANT:
    # SMC is now passed into the recommendation engine.
    #
    # recommendation_service.py must have:
    #
    # generate_recommendation(
    #     indicators,
    #     pattern,
    #     market_structure,
    #     support_resistance,
    #     smc,
    # )
    #
    # ============================================================

    recommendation = generate_recommendation(
        recommendation_indicators,
        pattern,
        market_structure,
        support_resistance,
        smc,
    )

    # ============================================================
    # EXCHANGE
    # ============================================================

    if resolved_symbol.endswith(".NS"):

        exchange = "NSE"

    elif resolved_symbol.endswith(".BO"):

        exchange = "BSE"

    else:

        exchange = "UNKNOWN"

    # ============================================================
    # DISPLAY SYMBOL
    # ============================================================

    display_symbol = resolved_symbol

    if display_symbol.endswith(".NS"):

        display_symbol = display_symbol[:-3]

    elif display_symbol.endswith(".BO"):

        display_symbol = display_symbol[:-3]

    # ============================================================
    # FINAL RESPONSE
    # ============================================================

    return {

        "success": True,

        # --------------------------------------------------------
        # SEARCH INFORMATION
        # --------------------------------------------------------

        "query": symbol.upper(),

        "symbol": display_symbol,

        "yahoo_symbol": resolved_symbol,

        "exchange": exchange,

        # --------------------------------------------------------
        # CURRENT PRICE
        # --------------------------------------------------------

        "price": round(
            live_price,
            2,
        ),

        # ========================================================
        # TECHNICAL INDICATORS
        # ========================================================

        "indicators": {

            "RSI": round(
                rsi,
                2,
            ),

            "EMA20": round(
                ema20,
                2,
            ),

            "EMA50": round(
                ema50,
                2,
            ),

            "MACD": round(
                macd,
                2,
            ),

            "MACD_SIGNAL": round(
                macd_signal,
                2,
            ),

            "MACD_BULLISH_CROSSOVER": (
                macd_bullish_crossover
            ),

            "MACD_BEARISH_CROSSOVER": (
                macd_bearish_crossover
            ),
        },

        # ========================================================
        # AI RECOMMENDATION
        # ========================================================

        "recommendation": recommendation,

        # ========================================================
        # CANDLESTICK PATTERN
        # ========================================================

        "pattern": pattern,

        # ========================================================
        # MARKET STRUCTURE
        # ========================================================

        "market_structure": market_structure,

        # ========================================================
        # SUPPORT & RESISTANCE
        # ========================================================

        "support_resistance": (
            support_resistance
        ),

        # ========================================================
        # SMART MONEY CONCEPTS
        # ========================================================

        "smc": smc,
    }