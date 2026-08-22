import math
from typing import Any

from services.data_service import get_stock_history
from services.indicator_service import calculate_indicators
from services.pattern_service import detect_pattern
from services.market_structure_service import detect_market_structure
from services.support_resistance_service import (
    calculate_support_resistance,
)
from services.recommendation_service import (
    generate_recommendation,
)

# ============================================================
# SMART MONEY CONCEPTS
# ============================================================

from services.smc_service import analyze_smc


# ============================================================
# MARKETIQ BACKTEST CONFIGURATION
# ============================================================

INITIAL_CAPITAL = 100000.0


# ============================================================
# HELPERS
# ============================================================

def safe_float(value: Any, default: float = 0.0) -> float:
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
    Safely convert indicator crossover values to bool.

    Prevents NaN values from becoming True.
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
    into a consistent YYYY-MM-DD string.
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

    - BUY  -> next candle open to next candle close
    - SELL -> next candle open to next candle close
    - HOLD -> no trade
    - Initial capital = ₹1,00,000

    Calculates:

    - Prediction accuracy
    - BUY / SELL / HOLD signals
    - Total trades
    - Winning trades
    - Losing trades
    - Win rate
    - Total return
    - Final capital
    - Maximum drawdown
    - Average trade return
    - Best trade
    - Worst trade
    - Equity curve
    - Complete trade history
    """

    # ============================================================
    # NORMALIZE SYMBOL
    # ============================================================

    symbol = str(symbol).upper().strip()

    if not symbol:
        return {
            "success": False,
            "message": "Stock symbol is required.",
        }

    # ============================================================
    # GET HISTORICAL DATA
    # ============================================================

    try:
        df = get_stock_history(
            symbol,
            period=period,
            interval="1d",
        )

    except Exception as exc:
        return {
            "success": False,
            "message": (
                f"Unable to load historical data for "
                f"{symbol}: {str(exc)}"
            ),
        }

    if df is None or df.empty:
        return {
            "success": False,
            "message": (
                f"No historical data found for {symbol}."
            ),
        }

    # ============================================================
    # CALCULATE INDICATORS
    # ============================================================

    try:
        df = calculate_indicators(df)

    except Exception as exc:
        return {
            "success": False,
            "message": (
                f"Unable to calculate indicators for "
                f"{symbol}: {str(exc)}"
            ),
        }

    # ============================================================
    # REQUIRED INDICATORS
    # ============================================================

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

    # ============================================================
    # REMOVE INVALID INDICATOR ROWS
    # ============================================================

    df = df.dropna(
        subset=required_columns
    ).copy()

    # ============================================================
    # MINIMUM DATA VALIDATION
    # ============================================================

    if len(df) < 60:
        return {
            "success": False,
            "message": (
                "Not enough historical data for backtesting. "
                "At least 60 valid candles are required."
            ),
        }

    # ============================================================
    # BACKTEST STATE
    # ============================================================

    results = []

    trades = []

    equity_curve = []

    capital = INITIAL_CAPITAL

    peak_capital = INITIAL_CAPITAL

    max_drawdown = 0.0

    # ============================================================
    # WALK THROUGH HISTORICAL DATA
    # ============================================================

    for i in range(50, len(df) - 1):

        try:
            # ----------------------------------------------------
            # ONLY DATA AVAILABLE UP TO CURRENT CANDLE
            # ----------------------------------------------------

            historical_df = df.iloc[: i + 1].copy()

            current_candle = df.iloc[i]

            next_candle = df.iloc[i + 1]

            # ----------------------------------------------------
            # CURRENT CANDLE
            # ----------------------------------------------------

            current_close = safe_float(
                current_candle["Close"]
            )

            # ----------------------------------------------------
            # NEXT CANDLE
            # ----------------------------------------------------

            next_open = safe_float(
                next_candle["Open"]
            )

            next_close = safe_float(
                next_candle["Close"]
            )

            if current_close <= 0 or next_open <= 0:
                continue

            # ====================================================
            # CANDLESTICK PATTERN
            # ====================================================

            pattern = detect_pattern(
                historical_df
            )

            # ====================================================
            # MARKET STRUCTURE
            # ====================================================

            market_structure = detect_market_structure(
                historical_df
            )

            # ====================================================
            # SUPPORT / RESISTANCE
            # ====================================================

            support_resistance = (
                calculate_support_resistance(
                    historical_df
                )
            )

            # ====================================================
            # SMART MONEY CONCEPTS
            #
            # IMPORTANT:
            # Only historical candles are passed.
            # Future candles are never used here.
            # ====================================================

            smc = analyze_smc(
                historical_df
            )

            # ====================================================
            # CURRENT INDICATORS
            # ====================================================

            latest = historical_df.iloc[-1]

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
            # SAME ENGINE AS LIVE ANALYSIS
            # ====================================================

            recommendation = generate_recommendation(
                indicators,
                pattern,
                market_structure,
                support_resistance,
                smc,
            )

            if not isinstance(
                recommendation,
                dict,
            ):
                recommendation = {}

            # ----------------------------------------------------
            # NORMALIZE RECOMMENDATION
            # ----------------------------------------------------

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

            # Keep confidence within valid range.
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
            # BASE RESULT
            # ====================================================

            signal_date = format_date(
                df.index[i]
            )

            next_date = format_date(
                next_candle.name
            )

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
                # UPDATE PEAK CAPITAL
                # ------------------------------------------------

                if capital > peak_capital:

                    peak_capital = capital

                # ------------------------------------------------
                # CURRENT DRAWDOWN
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

                    "capital": round(
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

        except Exception as exc:
            # ----------------------------------------------------
            # IMPORTANT:
            # One problematic historical candle should not
            # destroy the complete backtest.
            # ----------------------------------------------------

            print(
                f"Backtest warning for "
                f"{symbol} at index {i}: {exc}"
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

        average_trade_return = sum(
            trade["return_percent"]
            for trade in trades
        ) / total_trades

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