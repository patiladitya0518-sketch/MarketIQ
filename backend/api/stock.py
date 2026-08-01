from fastapi import APIRouter

from services.data_service import get_stock_history
from services.indicator_service import calculate_indicators
from services.recommendation_service import generate_recommendation
from services.pattern_service import detect_pattern

router = APIRouter(
    prefix="/stock",
    tags=["Stock"],
)


@router.get("/{symbol}")
def stock(symbol: str):

    df = get_stock_history(symbol)

    if df.empty:
        return {
            "success": False,
            "message": f"'{symbol}' is not a valid NSE stock symbol."
        }

    # Calculate Indicators
    df = calculate_indicators(df)

    latest = df.iloc[-1]

    indicators = {
        "Close": float(latest["Close"]),
        "RSI": float(latest["RSI"]),
        "EMA20": float(latest["EMA20"]),
        "EMA50": float(latest["EMA50"]),
        "MACD": float(latest["MACD"]),
        "MACD_SIGNAL": float(latest["MACD_SIGNAL"]),
    }

    # AI Recommendation
    recommendation = generate_recommendation(indicators)

    # AI Pattern Detection
    pattern = detect_pattern(df)

    return {
        "success": True,
        "symbol": symbol.upper(),
        "price": round(indicators["Close"], 2),

        "indicators": {
            "RSI": round(indicators["RSI"], 2),
            "EMA20": round(indicators["EMA20"], 2),
            "EMA50": round(indicators["EMA50"], 2),
            "MACD": round(indicators["MACD"], 2),
            "MACD_SIGNAL": round(indicators["MACD_SIGNAL"], 2),
        },

        "recommendation": recommendation,

        "pattern": pattern,
    }