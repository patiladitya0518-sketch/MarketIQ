from fastapi import APIRouter

from services.data_service import (
    get_stock_history,
    get_live_price,
)

from services.indicator_service import calculate_indicators
from services.recommendation_service import generate_recommendation
from services.pattern_service import detect_pattern
from services.market_structure_service import detect_market_structure
from services.support_resistance_service import (
    calculate_support_resistance,
)


router = APIRouter(
    prefix="/stock",
    tags=["Stock"],
)


@router.get("/{symbol}")
def stock(symbol: str):

    symbol = symbol.upper().strip()

    # ============================================================
    # HISTORICAL DATA
    # ============================================================

    df = get_stock_history(symbol)

    if df.empty:
        return {
            "success": False,
            "message": f"'{symbol}' is not a valid NSE stock symbol.",
        }

    # ============================================================
    # TECHNICAL INDICATORS
    # ============================================================

    df = calculate_indicators(df)

    latest = df.iloc[-1]

    indicators = {
        "Close": float(latest["Close"]),
        "RSI": float(latest["RSI"]),
        "EMA20": float(latest["EMA20"]),
        "EMA50": float(latest["EMA50"]),
        "MACD": float(latest["MACD"]),
        "MACD_SIGNAL": float(latest["MACD_SIGNAL"]),

        "MACD_BULLISH_CROSSOVER": bool(
            latest["MACD_BULLISH_CROSSOVER"]
        ),

        "MACD_BEARISH_CROSSOVER": bool(
            latest["MACD_BEARISH_CROSSOVER"]
        ),
    }

    # ============================================================
    # LIVE PRICE
    # ============================================================

    live_price = get_live_price(symbol)

    if live_price is None:
        live_price = round(
            indicators["Close"],
            2,
        )

    # ============================================================
    # CANDLESTICK PATTERN
    # ============================================================

    pattern = detect_pattern(df)

    # ============================================================
    # MARKET STRUCTURE
    # ============================================================

    market_structure = detect_market_structure(df)

    # ============================================================
    # SUPPORT & RESISTANCE
    # ============================================================

    support_resistance = calculate_support_resistance(df)

    # ============================================================
    # COMBINED AI RECOMMENDATION
    # ============================================================

    recommendation = generate_recommendation(
        indicators,
        pattern,
        market_structure,
        support_resistance,
    )

    # ============================================================
    # RESPONSE
    # ============================================================

    return {
        "success": True,

        "symbol": symbol,

        # --------------------------------------------------------
        # Current market price
        # --------------------------------------------------------

        "price": round(
            live_price,
            2,
        ),

        # --------------------------------------------------------
        # Technical indicators
        # --------------------------------------------------------

        "indicators": {
            "RSI": round(
                indicators["RSI"],
                2,
            ),

            "EMA20": round(
                indicators["EMA20"],
                2,
            ),

            "EMA50": round(
                indicators["EMA50"],
                2,
            ),

            "MACD": round(
                indicators["MACD"],
                2,
            ),

            "MACD_SIGNAL": round(
                indicators["MACD_SIGNAL"],
                2,
            ),
        },

        # --------------------------------------------------------
        # AI recommendation
        # --------------------------------------------------------

        "recommendation": recommendation,

        # --------------------------------------------------------
        # Candlestick pattern
        # --------------------------------------------------------

        "pattern": pattern,

        # --------------------------------------------------------
        # Market structure
        # --------------------------------------------------------

        "market_structure": market_structure,

        # --------------------------------------------------------
        # Support & Resistance
        # --------------------------------------------------------

        "support_resistance": support_resistance,
    }