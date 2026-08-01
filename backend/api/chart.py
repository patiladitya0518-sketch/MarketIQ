from fastapi import APIRouter

from services.data_service import get_stock_history
from services.indicator_service import calculate_indicators
from services.support_resistance_service import calculate_support_resistance

router = APIRouter(
    prefix="/chart",
    tags=["Chart"],
)


@router.get("/{symbol}")
def get_chart(symbol: str, period: str = "6M"):

    period_map = {
        "1D": ("1d", "5m"),
        "5D": ("5d", "15m"),
        "1M": ("3mo", "1d"),
        "3M": ("3mo", "1d"),
        "6M": ("6mo", "1d"),
        "1Y": ("1y", "1d"),
    }

    selected_period, selected_interval = period_map.get(
        period.upper(),
        ("6mo", "1d"),
    )

    df = get_stock_history(
        symbol,
        period=selected_period,
        interval=selected_interval,
    )

    if df.empty:
        return {
            "success": False,
            "message": f"'{symbol}' is not a valid NSE stock symbol."
        }

    df = calculate_indicators(df)

    levels = calculate_support_resistance(df)

    df = df.dropna(
        subset=[
            "EMA20",
            "EMA50",
            "RSI",
            "MACD",
            "MACD_SIGNAL",
        ]
    )

    if period.upper() == "1M":
        df = df.tail(22)

    chart_data = []

    for index, row in df.iterrows():

        chart_data.append({
            "time": (
                index.strftime("%Y-%m-%d %H:%M")
                if selected_interval != "1d"
                else index.strftime("%Y-%m-%d")
            ),

            "open": round(float(row["Open"]), 2),
            "high": round(float(row["High"]), 2),
            "low": round(float(row["Low"]), 2),
            "close": round(float(row["Close"]), 2),

            "volume": int(row["Volume"]),

            "ema20": round(float(row["EMA20"]), 2),
            "ema50": round(float(row["EMA50"]), 2),

            "rsi": round(float(row["RSI"]), 2),

            "macd": round(float(row["MACD"]), 2),
            "macdSignal": round(float(row["MACD_SIGNAL"]), 2),
        })

    return {
        "success": True,
        "symbol": symbol.upper(),
        "period": period.upper(),
        "count": len(chart_data),

        "levels": {
            "support": [
                round(level, 2)
                for level in levels["support"]
            ],
            "resistance": [
                round(level, 2)
                for level in levels["resistance"]
            ],
        },

        "data": chart_data,
    }