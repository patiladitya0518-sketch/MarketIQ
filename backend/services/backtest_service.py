import math
from typing import Any

from services.data_service import get_stock_history
from services.indicator_service import calculate_indicators
from services.pattern_service import detect_pattern
from services.market_structure_service import detect_market_structure
from services.support_resistance_service import (
    calculate_support_resistance,
)
from services.recommendation_service import generate_recommendation
from services.smc_service import analyze_smc


# ============================================================
# MARKETIQ BACKTEST CONFIGURATION
# ============================================================

INITIAL_CAPITAL = 100000.0

# Limit expensive historical analysis to recent candles.
# Indicators are still calculated using the complete dataset.
PATTERN_LOOKBACK = 30
STRUCTURE_LOOKBACK = 60
SUPPORT_RESISTANCE_LOOKBACK = 100
SMC_LOOKBACK = 100

MINIMUM_CANDLES = 60


# ============================================================
# HELPERS
# ============================================================

def safe_float(
    value: Any,
    default: float = 0.0,
) -> float:
    """
    Safely convert a value to float.

    Handles:
    - None
    - NaN
    - Infinity
    - strings
    """

    try:
        number = float(value)

        if not math.isfinite(number):
            return default

        return number

    except (TypeError, ValueError):
        return default


def safe_bool(value: Any) -> bool:
    """
    Safely convert crossover values to bool.
    """

    try:
        if value is None:
            return False

        if isinstance(value, float) and math.isnan(value):
            return False

        return bool(value)

    except Exception:
        return False


def format_date(value: Any) -> str:
    """
    Convert pandas Timestamp/date values
    into YYYY-MM-DD.
    """

    try:
        if hasattr(value, "date"):
            return str(value.date())

        return str(value)

    except Exception:
        return str(value)


# ============================================================
# MAIN BACKTEST ENGINE
# ============================================================

def run_backtest(
    symbol: str,
    period: str = "1y",
):
    """
    MarketIQ Historical Backtesting Engine.

    Uses the same MarketIQ recommendation engine
    used by live stock analysis.

    Historical workflow:

    1. Download historical stock data
    2. Calculate technical indicators
    3. Detect candlestick patterns
    4. Detect market structure
    5. Calculate support/resistance
    6. Analyze Smart Money Concepts
    7. Generate MarketIQ recommendation
    8. Validate against the next candle

    Trading simulation:

    BUY:
        Next candle OPEN -> next candle CLOSE

    SELL:
        Next candle OPEN -> next candle CLOSE

    HOLD:
        No trade

    Initial capital:
        ₹1,00,000
    """

    # ========================================================
    # NORMALIZE SYMBOL
    # ========================================================

    symbol = str(symbol).upper().strip()

    if not symbol:
        return {
            "success": False,
            "message": "Stock symbol is required.",
        }

    print(
        f"[MarketIQ Backtest] Starting "
        f"{symbol} | period={period}"
    )

    # ========================================================
    # GET HISTORICAL DATA
    # ========================================================

    try:

        print(
            f"[MarketIQ Backtest] Fetching history: "
            f"{symbol}"
        )

        df = get_stock_history(
            symbol,
            period=period,
            interval="1d",
        )

    except Exception as exc:

        print(
            f"[MarketIQ Backtest] History error: "
            f"{exc}"
        )

        return {
            "success": False,
            "message": (
                f"Unable to load historical data "
                f"for {symbol}: {str(exc)}"
            ),
        }

    if df is None or df.empty:

        return {
            "success": False,
            "message": (
                f"No historical data found for {symbol}."
            ),
        }

    print(
        f"[MarketIQ Backtest] History loaded: "
        f"{len(df)} candles"
    )

    # ========================================================
    # CALCULATE INDICATORS
    #
    # IMPORTANT:
    # Indicators are calculated ONCE using the complete
    # historical dataset.
    # ========================================================

    try:

        print(
            "[MarketIQ Backtest] Calculating indicators..."
        )

        df = calculate_indicators(df)

    except Exception as exc:

        print(
            f"[MarketIQ Backtest] Indicator error: "
            f"{exc}"
        )

        return {
            "success": False,
            "message": (
                f"Unable to calculate indicators "
                f"for {symbol}: {str(exc)}"
            ),
        }

    # ========================================================
    # REQUIRED INDICATORS
    # ========================================================

    required_columns = [
        "RSI",
        "EMA20",
        "EMA50",
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
                "Required indicator columns are missing: "
                + ", ".join(missing_columns)
            ),
        }

    # ========================================================
    # REMOVE INVALID INDICATOR ROWS
    # ========================================================

    df = df.dropna(
        subset=required_columns
    ).copy()

    if len(df) < MINIMUM_CANDLES:

        return {
            "success": False,
            "message": (
                "Not enough historical data for "
                "backtesting. At least 60 valid "
                "candles are required."
            ),
        }

    print(
        f"[MarketIQ Backtest] Valid candles: "
        f"{len(df)}"
    )

    # ========================================================
    # BACKTEST STATE
    # ========================================================

    results = []
    trades = []
    equity_curve = []

    capital = INITIAL_CAPITAL
    peak_capital = INITIAL_CAPITAL
    max_drawdown = 0.0

    total_iterations = len(df) - 51
    completed_iterations = 0

    # ========================================================
    # WALK THROUGH HISTORICAL DATA
    # ========================================================

    for i in range(
        50,
        len(df) - 1,
    ):

        try:

            # ====================================================
            # CURRENT + NEXT CANDLE
            # ====================================================

            current_candle = df.iloc[i]
            next_candle = df.iloc[i + 1]

            current_close = safe_float(
                current_candle["Close"]
            )

            next_open = safe_float(
                next_candle["Open"]
            )

            next_close = safe_float(
                next_candle["Close"]
            )

            if (
                current_close <= 0
                or next_open <= 0
            ):
                continue

            # ====================================================
            # HISTORICAL DATA AVAILABLE AT THIS POINT
            #
            # IMPORTANT:
            # We NEVER include df.iloc[i + 1] in analysis.
            # Therefore there is no future-data leakage.
            # ====================================================

            historical_df = df.iloc[
                : i + 1
            ]

            # ====================================================
            # OPTIMIZED ANALYSIS WINDOWS
            #
            # Instead of passing the complete historical
            # dataframe to every expensive service, use the
            # amount of history actually needed by that
            # analysis.
            # ====================================================

            pattern_df = historical_df.tail(
                PATTERN_LOOKBACK
            )

            structure_df = historical_df.tail(
                STRUCTURE_LOOKBACK
            )

            support_resistance_df = (
                historical_df.tail(
                    SUPPORT_RESISTANCE_LOOKBACK
                )
            )

            smc_df = historical_df.tail(
                SMC_LOOKBACK
            )

            # ====================================================
            # CANDLESTICK PATTERN
            # ====================================================

            pattern = detect_pattern(
                pattern_df
            )

            # ====================================================
            # MARKET STRUCTURE
            # ====================================================

            market_structure = (
                detect_market_structure(
                    structure_df
                )
            )

            # ====================================================
            # SUPPORT / RESISTANCE
            # ====================================================

            support_resistance = (
                calculate_support_resistance(
                    support_resistance_df
                )
            )

            # ====================================================
            # SMART MONEY CONCEPTS
            #
            # Only historical candles are passed.
            # ====================================================

            smc = analyze_smc(
                smc_df
            )

            # ====================================================
            # CURRENT INDICATORS
            # ====================================================

            latest = current_candle

            indicators = {
                "Close": safe_float(
                    latest["Close"]
                ),

                "RSI": safe_float(
                    latest["RSI"]
                ),

                "EMA20": safe_float(
                    latest["EMA20"]
                ),

                "EMA50": safe_float(
                    latest["EMA50"]
                ),

                "MACD": safe_float(
                    latest["MACD"]
                ),

                "MACD_SIGNAL": safe_float(
                    latest["MACD_SIGNAL"]
                ),

                "MACD_BULLISH_CROSSOVER":
                    safe_bool(
                        latest.get(
                            "MACD_BULLISH_CROSSOVER",
                            False,
                        )
                    ),

                "MACD_BEARISH_CROSSOVER":
                    safe_bool(
                        latest.get(
                            "MACD_BEARISH_CROSSOVER",
                            False,
                        )
                    ),
            }

            # ====================================================
            # MARKETIQ RECOMMENDATION
            #
            # SAME ENGINE USED BY LIVE ANALYSIS
            # ====================================================

            recommendation = (
                generate_recommendation(
                    indicators,
                    pattern,
                    market_structure,
                    support_resistance,
                    smc,
                )
            )

            if not isinstance(
                recommendation,
                dict,
            ):
                recommendation = {}

            # ====================================================
            # NORMALIZE RECOMMENDATION
            # ====================================================

            action = str(
                recommendation.get(
                    "recommendation",
                    "HOLD",
                )
            ).upper()

            if action not in {
                "BUY",
                "SELL",
                "HOLD",
            }:
                action = "HOLD"

            score = safe_float(
                recommendation.get(
                    "score",
                    0,
                )
            )

            confidence = safe_float(
                recommendation.get(
                    "confidence",
                    0,
                )
            )

            confidence = max(
                0.0,
                min(
                    100.0,
                    confidence,
                ),
            )

            # ====================================================
            # ACTUAL NEXT-DAY DIRECTION
            # ====================================================

            if next_close > current_close:

                actual_direction = "UP"

            elif next_close < current_close:

                actual_direction = "DOWN"

            else:

                actual_direction = "FLAT"

            # ====================================================
            # PREDICTION RESULT
            # ====================================================

            correct = None

            if action == "BUY":

                correct = (
                    actual_direction == "UP"
                )

            elif action == "SELL":

                correct = (
                    actual_direction == "DOWN"
                )

            # ====================================================
            # DATES
            # ====================================================

            signal_date = format_date(
                df.index[i]
            )

            next_date = format_date(
                next_candle.name
            )

            # ====================================================
            # BASE RESULT
            # ====================================================

            result = {
                "date": signal_date,

                "action": action,

                "score": round(
                    score,
                    2,
                ),

                "confidence": round(
                    confidence,
                    2,
                ),

                "signal_price": round(
                    current_close,
                    2,
                ),

                "entry_price": round(
                    next_open,
                    2,
                ),

                "exit_price": round(
                    next_close,
                    2,
                ),

                "actual_direction":
                    actual_direction,

                "correct": correct,
            }

            # ====================================================
            # TRADE SIMULATION
            # ====================================================

            if action in {
                "BUY",
                "SELL",
            }:

                entry_price = next_open
                exit_price = next_close

                # ------------------------------------------------
                # TRADE RETURN
                # ------------------------------------------------

                if action == "BUY":

                    trade_return_pct = (
                        (
                            exit_price
                            - entry_price
                        )
                        / entry_price
                    ) * 100

                else:

                    trade_return_pct = (
                        (
                            entry_price
                            - exit_price
                        )
                        / entry_price
                    ) * 100

                # ------------------------------------------------
                # CAPITAL BEFORE TRADE
                # ------------------------------------------------

                capital_before = capital

                # ------------------------------------------------
                # PROFIT / LOSS
                # ------------------------------------------------

                profit_loss = (
                    capital_before
                    * trade_return_pct
                    / 100
                )

                capital = (
                    capital
                    + profit_loss
                )

                # ------------------------------------------------
                # TRADE RESULT
                # ------------------------------------------------

                if profit_loss > 0:

                    trade_result = "WIN"

                elif profit_loss < 0:

                    trade_result = "LOSS"

                else:

                    trade_result = "FLAT"

                # ------------------------------------------------
                # UPDATE PEAK
                # ------------------------------------------------

                if capital > peak_capital:

                    peak_capital = capital

                # ------------------------------------------------
                # DRAWDOWN
                # ------------------------------------------------

                if peak_capital > 0:

                    current_drawdown = (
                        (
                            peak_capital
                            - capital
                        )
                        / peak_capital
                    ) * 100

                else:

                    current_drawdown = 0.0

                max_drawdown = max(
                    max_drawdown,
                    current_drawdown,
                )

                # ------------------------------------------------
                # TRADE OBJECT
                # ------------------------------------------------

                trade = {
                    "date": next_date,

                    "signal_date":
                        signal_date,

                    "action":
                        action,

                    "confidence":
                        round(
                            confidence,
                            2,
                        ),

                    "score":
                        round(
                            score,
                            2,
                        ),

                    "entry_price":
                        round(
                            entry_price,
                            2,
                        ),

                    "exit_price":
                        round(
                            exit_price,
                            2,
                        ),

                    "return_percent":
                        round(
                            trade_return_pct,
                            2,
                        ),

                    "profit_loss":
                        round(
                            profit_loss,
                            2,
                        ),

                    "capital_before":
                        round(
                            capital_before,
                            2,
                        ),

                    "capital_after":
                        round(
                            capital,
                            2,
                        ),

                    "result":
                        trade_result,
                }

                trades.append(
                    trade
                )

                # ------------------------------------------------
                # ADD TRADE DATA TO RESULT
                # ------------------------------------------------

                result.update(
                    {
                        "trade": True,

                        "trade_result":
                            trade_result,

                        "trade_return_percent":
                            round(
                                trade_return_pct,
                                2,
                            ),

                        "profit_loss":
                            round(
                                profit_loss,
                                2,
                            ),

                        "capital_after":
                            round(
                                capital,
                                2,
                            ),
                    }
                )

            else:

                result.update(
                    {
                        "trade": False,

                        "trade_result":
                            None,

                        "trade_return_percent":
                            None,

                        "profit_loss":
                            0.0,

                        "capital_after":
                            round(
                                capital,
                                2,
                            ),
                    }
                )

            # ====================================================
            # EQUITY CURVE
            # ====================================================

            equity_curve.append(
                {
                    "date": next_date,

                    "capital":
                        round(
                            capital,
                            2,
                        ),
                }
            )

            # ====================================================
            # STORE RESULT
            # ====================================================

            results.append(
                result
            )

            completed_iterations += 1

            # ====================================================
            # PROGRESS LOG
            # ====================================================

            if (
                completed_iterations % 25 == 0
                or i == len(df) - 2
            ):

                progress = (
                    completed_iterations
                    / max(
                        total_iterations,
                        1,
                    )
                ) * 100

                print(
                    f"[MarketIQ Backtest] "
                    f"{symbol} progress: "
                    f"{progress:.0f}% "
                    f"({completed_iterations}/"
                    f"{total_iterations})"
                )

        except Exception as exc:

            print(
                f"[MarketIQ Backtest] "
                f"Warning at index {i}: {exc}"
            )

            continue

    # ============================================================
    # PREDICTION STATISTICS
    # ============================================================

    prediction_results = [
        item
        for item in results
        if item.get("correct") is not None
    ]

    correct_predictions = sum(
        1
        for item in prediction_results
        if item.get("correct") is True
    )

    total_predictions = len(
        prediction_results
    )

    if total_predictions > 0:

        accuracy = (
            correct_predictions
            / total_predictions
        ) * 100

    else:

        accuracy = 0.0

    # ============================================================
    # SIGNAL COUNTS
    # ============================================================

    buy_signals = sum(
        1
        for item in results
        if item.get("action") == "BUY"
    )

    sell_signals = sum(
        1
        for item in results
        if item.get("action") == "SELL"
    )

    hold_signals = sum(
        1
        for item in results
        if item.get("action") == "HOLD"
    )

    # ============================================================
    # TRADING STATISTICS
    # ============================================================

    winning_trades = sum(
        1
        for trade in trades
        if trade["profit_loss"] > 0
    )

    losing_trades = sum(
        1
        for trade in trades
        if trade["profit_loss"] < 0
    )

    flat_trades = sum(
        1
        for trade in trades
        if trade["profit_loss"] == 0
    )

    total_trades = len(
        trades
    )

    if total_trades > 0:

        win_rate = (
            winning_trades
            / total_trades
        ) * 100

    else:

        win_rate = 0.0

    # ============================================================
    # FINAL CAPITAL
    # ============================================================

    final_capital = capital

    total_return = (
        (
            final_capital
            - INITIAL_CAPITAL
        )
        / INITIAL_CAPITAL
    ) * 100

    # ============================================================
    # NET PROFIT / LOSS
    # ============================================================

    net_profit_loss = (
        final_capital
        - INITIAL_CAPITAL
    )

    # ============================================================
    # AVERAGE TRADE RETURN
    # ============================================================

    if total_trades > 0:

        average_trade_return = (
            sum(
                trade["return_percent"]
                for trade in trades
            )
            / total_trades
        )

    else:

        average_trade_return = 0.0

    # ============================================================
    # BEST / WORST TRADE
    # ============================================================

    if trades:

        best_trade = max(
            trades,
            key=lambda trade:
                trade["profit_loss"],
        )

        worst_trade = min(
            trades,
            key=lambda trade:
                trade["profit_loss"],
        )

    else:

        best_trade = None
        worst_trade = None

    # ============================================================
    # FINAL LOG
    # ============================================================

    print(
        f"[MarketIQ Backtest] COMPLETE | "
        f"{symbol} | "
        f"predictions={total_predictions} | "
        f"trades={total_trades} | "
        f"accuracy={accuracy:.2f}% | "
        f"final_capital={final_capital:.2f}"
    )

    # ============================================================
    # FINAL RESPONSE
    # ============================================================

    return {
        "success": True,

        "symbol": symbol,

        "period": period,

        # ========================================================
        # CAPITAL
        # ========================================================

        "initial_capital":
            round(
                INITIAL_CAPITAL,
                2,
            ),

        "final_capital":
            round(
                final_capital,
                2,
            ),

        "net_profit_loss":
            round(
                net_profit_loss,
                2,
            ),

        "total_return":
            round(
                total_return,
                2,
            ),

        # ========================================================
        # TRADING PERFORMANCE
        # ========================================================

        "total_trades":
            total_trades,

        "winning_trades":
            winning_trades,

        "losing_trades":
            losing_trades,

        "flat_trades":
            flat_trades,

        "win_rate":
            round(
                win_rate,
                2,
            ),

        "max_drawdown":
            round(
                max_drawdown,
                2,
            ),

        "average_trade_return":
            round(
                average_trade_return,
                2,
            ),

        # ========================================================
        # PREDICTION PERFORMANCE
        # ========================================================

        "summary": {
            "total_candles":
                len(df),

            "total_predictions":
                total_predictions,

            "correct_predictions":
                correct_predictions,

            "accuracy":
                round(
                    accuracy,
                    2,
                ),

            "buy_signals":
                buy_signals,

            "sell_signals":
                sell_signals,

            "hold_signals":
                hold_signals,

            "total_trades":
                total_trades,

            "winning_trades":
                winning_trades,

            "losing_trades":
                losing_trades,

            "win_rate":
                round(
                    win_rate,
                    2,
                ),

            "initial_capital":
                round(
                    INITIAL_CAPITAL,
                    2,
                ),

            "final_capital":
                round(
                    final_capital,
                    2,
                ),

            "net_profit_loss":
                round(
                    net_profit_loss,
                    2,
                ),

            "total_return":
                round(
                    total_return,
                    2,
                ),

            "max_drawdown":
                round(
                    max_drawdown,
                    2,
                ),
        },

        # ========================================================
        # BEST TRADE
        # ========================================================

        "best_trade":
            best_trade,

        # ========================================================
        # WORST TRADE
        # ========================================================

        "worst_trade":
            worst_trade,

        # ========================================================
        # EQUITY CURVE
        # ========================================================

        "equity_curve":
            equity_curve,

        # ========================================================
        # COMPLETE TRADE HISTORY
        # ========================================================

        "trades":
            trades,

        # ========================================================
        # ORIGINAL PREDICTION RESULTS
        # ========================================================

        "results":
            results,
    }