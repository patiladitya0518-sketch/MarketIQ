import pandas as pd

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
# MARKETIQ BACKTEST CONFIGURATION
# ============================================================

INITIAL_CAPITAL = 100000.0


# ============================================================
# MAIN BACKTEST ENGINE
# ============================================================

def run_backtest(
    symbol: str,
    period: str = "1y",
):
    """
    MarketIQ Historical Backtesting Engine.

    Tests MarketIQ recommendations against
    historical NSE stock data.

    Prediction logic:
    - Calculate indicators using historical candles
    - Generate MarketIQ recommendation
    - Use next candle OPEN as the simulated entry
    - Use next candle CLOSE as the simulated exit
    - Prediction direction is also based on
      next OPEN -> next CLOSE

    Trading simulation:
    - BUY = long one-candle trade
    - SELL = short one-candle trade
    - HOLD = no trade
    - Initial capital = ₹1,00,000

    Calculates:
    - Prediction accuracy
    - Total trades
    - Winning trades
    - Losing trades
    - Win rate
    - Total return
    - Final capital
    - Maximum drawdown
    - Equity curve
    - Trade history
    - Best trade
    - Worst trade
    """

    symbol = symbol.upper().strip()

    # ============================================================
    # GET HISTORICAL DATA
    # ============================================================

    df = get_stock_history(
        symbol,
        period=period,
        interval="1d",
    )

    if df.empty:
        return {
            "success": False,
            "message": f"No historical data found for {symbol}",
        }

    # ============================================================
    # CALCULATE INDICATORS
    # ============================================================

    df = calculate_indicators(df)

    required_columns = [
        "RSI",
        "EMA20",
        "EMA50",
        "MACD",
        "MACD_SIGNAL",
    ]

    # Check required columns
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

    # Remove rows where indicators are not ready
    df = df.dropna(
        subset=required_columns
    ).copy()

    if len(df) < 60:
        return {
            "success": False,
            "message": "Not enough historical data for backtesting.",
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

        historical_df = df.iloc[: i + 1].copy()

        current_candle = df.iloc[i]

        next_candle = df.iloc[i + 1]

        # --------------------------------------------------------
        # CURRENT CANDLE
        # --------------------------------------------------------

        current_close = float(
            current_candle["Close"]
        )

        # --------------------------------------------------------
        # NEXT CANDLE
        # --------------------------------------------------------

        next_open = float(
            next_candle["Open"]
        )

        next_close = float(
            next_candle["Close"]
        )

        # Skip invalid prices
        if next_open <= 0:
            continue

        # ========================================================
        # PATTERN DETECTION
        # ========================================================

        pattern = detect_pattern(
            historical_df
        )

        # ========================================================
        # MARKET STRUCTURE
        # ========================================================

        market_structure = detect_market_structure(
            historical_df
        )

        # ========================================================
        # SUPPORT / RESISTANCE
        # ========================================================

        support_resistance = (
            calculate_support_resistance(
                historical_df
            )
        )

        # ========================================================
        # CURRENT INDICATORS
        # ========================================================

        latest = historical_df.iloc[-1]

        indicators = {
            "Close": float(
                latest["Close"]
            ),

            "RSI": float(
                latest["RSI"]
            ),

            "EMA20": float(
                latest["EMA20"]
            ),

            "EMA50": float(
                latest["EMA50"]
            ),

            "MACD": float(
                latest["MACD"]
            ),

            "MACD_SIGNAL": float(
                latest["MACD_SIGNAL"]
            ),

            "MACD_BULLISH_CROSSOVER": bool(
                latest[
                    "MACD_BULLISH_CROSSOVER"
                ]
            )
            if "MACD_BULLISH_CROSSOVER" in latest
            else False,

            "MACD_BEARISH_CROSSOVER": bool(
                latest[
                    "MACD_BEARISH_CROSSOVER"
                ]
            )
            if "MACD_BEARISH_CROSSOVER" in latest
            else False,
        }

        # ========================================================
        # MARKETIQ RECOMMENDATION
        # ========================================================

        recommendation = generate_recommendation(
            indicators,
            pattern,
            market_structure,
            support_resistance,
        )

        action = recommendation.get(
            "recommendation",
            "HOLD",
        )

        score = recommendation.get(
            "score",
            0,
        )

        confidence = recommendation.get(
            "confidence",
            0,
        )

        # ========================================================
        # ACTUAL NEXT-CANDLE DIRECTION
        #
        # IMPORTANT:
        # Prediction is now measured using the same prices
        # as the simulated trade:
        #
        # NEXT OPEN -> NEXT CLOSE
        # ========================================================

        if next_close > next_open:

            actual_direction = "UP"

        elif next_close < next_open:

            actual_direction = "DOWN"

        else:

            actual_direction = "FLAT"

        # ========================================================
        # PREDICTION RESULT
        # ========================================================

        correct = None

        if action == "BUY":

            correct = (
                actual_direction == "UP"
            )

        elif action == "SELL":

            correct = (
                actual_direction == "DOWN"
            )

        # ========================================================
        # BASE RESULT
        # ========================================================

        result = {
            "date": str(
                df.index[i].date()
            ),

            "action": action,

            "score": score,

            "confidence": confidence,

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

        # ========================================================
        # TRADE SIMULATION
        # ========================================================

        if action in ["BUY", "SELL"]:

            entry_price = next_open

            exit_price = next_close

            # ----------------------------------------------------
            # BUY / LONG
            # ----------------------------------------------------

            if action == "BUY":

                trade_return_pct = (
                    (
                        exit_price
                        - entry_price
                    )
                    / entry_price
                ) * 100

            # ----------------------------------------------------
            # SELL / SHORT
            # ----------------------------------------------------

            else:

                trade_return_pct = (
                    (
                        entry_price
                        - exit_price
                    )
                    / entry_price
                ) * 100

            # ----------------------------------------------------
            # CAPITAL BEFORE TRADE
            # ----------------------------------------------------

            capital_before = capital

            # ----------------------------------------------------
            # PROFIT / LOSS
            #
            # Entire simulated capital is used.
            # ----------------------------------------------------

            profit_loss = (
                capital_before
                * trade_return_pct
                / 100
            )

            capital = (
                capital
                + profit_loss
            )

            # Prevent extremely small floating-point
            # negative zero values.
            if abs(capital) < 0.000001:
                capital = 0.0

            # ----------------------------------------------------
            # TRADE RESULT
            # ----------------------------------------------------

            if profit_loss > 0:

                trade_result = "WIN"

            elif profit_loss < 0:

                trade_result = "LOSS"

            else:

                trade_result = "FLAT"

            # ----------------------------------------------------
            # UPDATE PEAK CAPITAL
            # ----------------------------------------------------

            if capital > peak_capital:

                peak_capital = capital

            # ----------------------------------------------------
            # CURRENT DRAWDOWN
            # ----------------------------------------------------

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

            # ----------------------------------------------------
            # MAXIMUM DRAWDOWN
            # ----------------------------------------------------

            if current_drawdown > max_drawdown:

                max_drawdown = current_drawdown

            # ----------------------------------------------------
            # TRADE OBJECT
            # ----------------------------------------------------

            trade_date = (
                next_candle.name.date()
                if hasattr(
                    next_candle.name,
                    "date",
                )
                else next_candle.name
            )

            trade = {
                "date": str(
                    trade_date
                ),

                "signal_date": str(
                    df.index[i].date()
                ),

                "action": action,

                "confidence": confidence,

                "score": score,

                "entry_price": round(
                    entry_price,
                    2,
                ),

                "exit_price": round(
                    exit_price,
                    2,
                ),

                "return_percent": round(
                    trade_return_pct,
                    2,
                ),

                "profit_loss": round(
                    profit_loss,
                    2,
                ),

                "capital_before": round(
                    capital_before,
                    2,
                ),

                "capital_after": round(
                    capital,
                    2,
                ),

                "result": trade_result,
            }

            trades.append(
                trade
            )

            # ----------------------------------------------------
            # ADD TRADE INFORMATION
            # ----------------------------------------------------

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

        # ========================================================
        # HOLD
        # ========================================================

        else:

            result.update(
                {
                    "trade": False,

                    "trade_result": None,

                    "trade_return_percent": None,

                    "profit_loss": 0.0,

                    "capital_after":
                        round(
                            capital,
                            2,
                        ),
                }
            )

        # ========================================================
        # EQUITY CURVE
        # ========================================================

        equity_date = (
            next_candle.name.date()
            if hasattr(
                next_candle.name,
                "date",
            )
            else next_candle.name
        )

        equity_curve.append(
            {
                "date": str(
                    equity_date
                ),

                "capital": round(
                    capital,
                    2,
                ),
            }
        )

        # ========================================================
        # STORE RESULT
        # ========================================================

        results.append(
            result
        )

    # ============================================================
    # PREDICTION STATISTICS
    # ============================================================

    prediction_results = [
        result
        for result in results
        if result["correct"] is not None
    ]

    correct_predictions = sum(
        1
        for result in prediction_results
        if result["correct"]
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
        for result in results
        if result["action"] == "BUY"
    )

    sell_signals = sum(
        1
        for result in results
        if result["action"] == "SELL"
    )

    hold_signals = sum(
        1
        for result in results
        if result["action"] == "HOLD"
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

        "initial_capital": round(
            INITIAL_CAPITAL,
            2,
        ),

        "final_capital": round(
            final_capital,
            2,
        ),

        "net_profit_loss": round(
            net_profit_loss,
            2,
        ),

        "total_return": round(
            total_return,
            2,
        ),

        # ========================================================
        # TRADING PERFORMANCE
        # ========================================================

        "total_trades": total_trades,

        "winning_trades": winning_trades,

        "losing_trades": losing_trades,

        "flat_trades": flat_trades,

        "win_rate": round(
            win_rate,
            2,
        ),

        "max_drawdown": round(
            max_drawdown,
            2,
        ),

        "average_trade_return": round(
            average_trade_return,
            2,
        ),

        # ========================================================
        # PREDICTION PERFORMANCE
        # ========================================================

        "summary": {
            "total_candles": len(df),

            "total_predictions":
                total_predictions,

            "correct_predictions":
                correct_predictions,

            "accuracy": round(
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

        "best_trade": best_trade,

        # ========================================================
        # WORST TRADE
        # ========================================================

        "worst_trade": worst_trade,

        # ========================================================
        # EQUITY CURVE
        # ========================================================

        "equity_curve": equity_curve,

        # ========================================================
        # COMPLETE TRADE HISTORY
        # ========================================================

        "trades": trades,

        # ========================================================
        # ORIGINAL PREDICTION RESULTS
        # ========================================================

        "results": results,
    }