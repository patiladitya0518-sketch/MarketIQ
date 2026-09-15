from fastapi import APIRouter

from services.data_service import (
    get_stock_history,
    resolve_symbol,
)
from services.indicator_service import calculate_indicators
from services.support_resistance_service import (
    calculate_support_resistance,
)


router = APIRouter(
    prefix="/chart",
    tags=["Chart"],
)


@router.get("/{symbol}")
def get_chart(
    symbol: str,
    period: str = "6M",
):
    # ============================================================
    # CLEAN INPUT
    # ============================================================

    symbol = symbol.strip()

    if not symbol:
        return {
            "success": False,
            "message": "Please enter a stock symbol.",
        }

    requested_period = period.strip().upper()

    # ============================================================
    # SUPPORTED PERIODS
    # ============================================================

    period_map = {
        "1D": ("1d", "5m"),
        "5D": ("5d", "15m"),
        "1M": ("3mo", "1d"),
        "3M": ("3mo", "1d"),
        "6M": ("6mo", "1d"),
        "1Y": ("1y", "1d"),
    }

    if requested_period not in period_map:
        return {
            "success": False,
            "message": (
                f"Unsupported chart period '{period}'. "
                "Supported periods are 1D, 5D, 1M, 3M, 6M and 1Y."
            ),
        }

    selected_period, selected_interval = period_map[
        requested_period
    ]

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

    try:
        df = get_stock_history(
            resolved_symbol,
            period=selected_period,
            interval=selected_interval,
        )
    except Exception as error:
        return {
            "success": False,
            "message": (
                f"Unable to load chart data for "
                f"'{symbol.upper()}'."
            ),
            "error": str(error),
        }

    if df is None or df.empty:
        return {
            "success": False,
            "message": (
                f"Historical chart data is unavailable "
                f"for '{symbol.upper()}'."
            ),
        }

    # ============================================================
    # TECHNICAL INDICATORS
    # ============================================================

    try:
        df = calculate_indicators(df)
    except Exception as error:
        return {
            "success": False,
            "message": (
                f"Unable to calculate chart indicators "
                f"for '{symbol.upper()}'."
            ),
            "error": str(error),
        }

    if df is None or df.empty:
        return {
            "success": False,
            "message": (
                f"Chart indicators could not be calculated "
                f"for '{symbol.upper()}'."
            ),
        }

    # ============================================================
    # SUPPORT & RESISTANCE
    # ============================================================

    try:
        levels = calculate_support_resistance(df)
    except Exception:
        levels = {
            "support": [],
            "resistance": [],
        }

    # ============================================================
    # REQUIRED COLUMNS
    # ============================================================

    required_columns = [
        "Open",
        "High",
        "Low",
        "Close",
        "Volume",
        "EMA20",
        "EMA50",
        "RSI",
        "MACD",
        "MACD_SIGNAL",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        return {
            "success": False,
            "message": (
                "Chart data is missing required fields."
            ),
            "missing_columns": missing_columns,
        }

    # ============================================================
    # REMOVE INVALID INDICATOR ROWS
    # ============================================================

    df = df.dropna(
        subset=[
            "Open",
            "High",
            "Low",
            "Close",
            "EMA20",
            "EMA50",
            "RSI",
            "MACD",
            "MACD_SIGNAL",
        ]
    )

    if df.empty:
        return {
            "success": False,
            "message": (
                f"Not enough historical data to build "
                f"the chart for '{symbol.upper()}'."
            ),
        }

    # ============================================================
    # 1 MONTH DISPLAY WINDOW
    # ============================================================
    #
    # We request 3 months internally so EMA20/EMA50 and
    # other indicators have enough historical candles to warm up.
    #
    # Only the latest approximately 22 trading sessions are
    # returned to the frontend for the 1M chart.
    # ============================================================

    if requested_period == "1M":
        df = df.tail(22)

    # ============================================================
    # SAFE NUMBER HELPER
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

    # ============================================================
    # CHART DATA
    # ============================================================

    chart_data = []

    for index, row in df.iterrows():

        open_price = safe_float(row["Open"])
        high_price = safe_float(row["High"])
        low_price = safe_float(row["Low"])
        close_price = safe_float(row["Close"])

        volume = safe_float(
            row["Volume"],
            0,
        )

        ema20 = safe_float(
            row["EMA20"],
            close_price,
        )

        ema50 = safe_float(
            row["EMA50"],
            close_price,
        )

        rsi = safe_float(
            row["RSI"],
            50,
        )

        macd = safe_float(
            row["MACD"],
            0,
        )

        macd_signal = safe_float(
            row["MACD_SIGNAL"],
            0,
        )

        # --------------------------------------------------------
        # TIME FORMAT
        # --------------------------------------------------------

        if selected_interval != "1d":
            chart_time = index.strftime(
                "%Y-%m-%d %H:%M"
            )
        else:
            chart_time = index.strftime(
                "%Y-%m-%d"
            )

        chart_data.append(
            {
                "time": chart_time,

                "open": round(
                    open_price,
                    2,
                ),

                "high": round(
                    high_price,
                    2,
                ),

                "low": round(
                    low_price,
                    2,
                ),

                "close": round(
                    close_price,
                    2,
                ),

                "volume": int(
                    volume
                ),

                "ema20": round(
                    ema20,
                    2,
                ),

                "ema50": round(
                    ema50,
                    2,
                ),

                "rsi": round(
                    rsi,
                    2,
                ),

                "macd": round(
                    macd,
                    2,
                ),

                "macdSignal": round(
                    macd_signal,
                    2,
                ),
            }
        )

    # ============================================================
    # CLEAN SUPPORT / RESISTANCE LEVELS
    # ============================================================

    support_levels = []

    resistance_levels = []

    for level in levels.get(
        "support",
        [],
    ):
        value = safe_float(
            level,
            None,
        )

        if value is not None:
            support_levels.append(
                round(value, 2)
            )

    for level in levels.get(
        "resistance",
        [],
    ):
        value = safe_float(
            level,
            None,
        )

        if value is not None:
            resistance_levels.append(
                round(value, 2)
            )

    # ============================================================
    # FINAL RESPONSE
    # ============================================================

    return {
        "success": True,

        "query": symbol.upper(),

        "symbol": (
            resolved_symbol
            .replace(".NS", "")
            .replace(".BO", "")
        ),

        "yahoo_symbol": resolved_symbol,

        "exchange": (
            "NSE"
            if resolved_symbol.endswith(".NS")
            else "BSE"
            if resolved_symbol.endswith(".BO")
            else "UNKNOWN"
        ),

        "period": requested_period,

        "interval": selected_interval,

        "count": len(chart_data),

        "levels": {
            "support": support_levels,
            "resistance": resistance_levels,
        },

        "data": chart_data,
    }