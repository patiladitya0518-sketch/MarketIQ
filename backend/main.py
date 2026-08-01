from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from services.data_service import get_stock_history
from services.indicator_service import calculate_indicators
from services.recommendation_service import generate_recommendation
from services.support_resistance_service import calculate_support_resistance
from services.pattern_service import detect_pattern

app = FastAPI(
    title="MarketIQ API",
    description="AI Stock Market Analysis API",
    version="1.2.0",
)

# ==========================================================
# CORS
# ==========================================================

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://market-iq-five-orpin.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "Welcome to MarketIQ API 🚀"}


@app.get("/health")
def health():
    return {"status": "healthy"}


# ==========================================================
# STOCK ANALYSIS
# ==========================================================

@app.get("/stock/{symbol}")
def stock(symbol: str):

    df = get_stock_history(symbol)

    if df.empty:
        return {
            "success": False,
            "message": f"'{symbol}' is not a valid NSE stock symbol."
        }

    # Calculate indicators
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

        # NEW AI Pattern Detection
        "pattern": pattern,
    }


# ==========================================================
# CHART DATA
# ==========================================================

@app.get("/chart/{symbol}")
def get_chart(symbol: str, period: str = "6M"):

    period_map = {
        "1D": ("1d", "5m"),
        "5D": ("5d", "15m"),

        # Fetch extra history so indicators calculate correctly
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

    # Calculate indicators
    df = calculate_indicators(df)

    # Support / Resistance
    levels = calculate_support_resistance(df)

    # Remove rows where indicators aren't available
    df = df.dropna(
        subset=[
            "EMA20",
            "EMA50",
            "RSI",
            "MACD",
            "MACD_SIGNAL",
        ]
    )

    # Show only the latest month
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
            "support": [round(level, 2) for level in levels["support"]],
            "resistance": [round(level, 2) for level in levels["resistance"]],
        },

        "data": chart_data,
    }