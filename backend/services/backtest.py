import math
from typing import Any, Dict, List, Optional

from services.data_service import get_stock_history
from services.indicator_service import calculate_indicators
from services.pattern_service import detect_pattern
from services.market_structure_service import detect_market_structure
from services.support_resistance_service import calculate_support_resistance
from services.recommendation_service import generate_recommendation

# SMC is optional for development compatibility.
try:
    from services.smc_service import analyze_smc
except ImportError:
    analyze_smc = None


# ============================================================
# MARKETIQ BACKTEST CONFIGURATION
# ============================================================

INITIAL_CAPITAL = 100000.0

POSITION_SIZE_PERCENT = 20.0

MIN_CONFIDENCE = 60.0

MIN_RISK_REWARD = 1.5

MAX_HOLDING_DAYS = 5
ANALYSIS_LOOKBACK = 300

# Use a rolling window instead of passing the entire historical
# dataframe into every analysis service.
#
# This is especially important for 2Y / 5Y backtests.
ANALYSIS_LOOKBACK = 300

# ------------------------------------------------------------
# STRATEGY CONFIRMATION
# These secondary filters are advisory/disabled by default because the
# recommendation engine already combines trend, RSI and MACD. Keeping
# them as hard gates caused valid signals to be over-filtered in backtests.
# SMC conflict remains the hard safety filter.
# ------------------------------------------------------------

ENABLE_TREND_FILTER = False
ENABLE_RSI_FILTER = False
ENABLE_MACD_FILTER = False
ENABLE_SMC_CONFLICT_FILTER = True

# RSI ranges for directional trades.
BUY_MIN_RSI = 45.0
BUY_MAX_RSI = 70.0

SELL_MIN_RSI = 30.0
SELL_MAX_RSI = 55.0

# Strong SMC opposite signal blocks the trade.
SMC_CONFLICT_CONFIDENCE = 70.0


# ============================================================
# HELPERS
# ============================================================


def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default

        number = float(value)

        if not math.isfinite(number):
            return default

        return number

    except (TypeError, ValueError):
        return default


def safe_bool(value: Any) -> bool:
    try:
        if value is None:
            return False

        if isinstance(value, float) and math.isnan(value):
            return False

        if isinstance(value, str):
            return value.strip().lower() in {
                "true",
                "1",
                "yes",
                "y",
            }

        return bool(value)

    except Exception:
        return False


def clean_action(value: Any) -> str:
    action = str(value or "HOLD").strip().upper()

    if action in {"BUY", "SELL", "HOLD"}:
        return action

    return "HOLD"


def format_date(value: Any) -> str:
    try:
        if hasattr(value, "date"):
            return str(value.date())

        return str(value)

    except Exception:
        return str(value)


def round_or_none(
    value: Any,
    digits: int = 2,
) -> Optional[float]:

    if value is None:
        return None

    number = safe_float(value, math.nan)

    if not math.isfinite(number):
        return None

    return round(number, digits)


def empty_smc() -> Dict[str, Any]:
    return {
        "success": False,
        "signal": "HOLD",
        "confidence": 0,
        "score": 0,
        "bullish_score": 0,
        "bearish_score": 0,
        "reasons": [],
    }


# ============================================================
# SMC
# ============================================================


def calculate_smc(historical_df) -> Dict[str, Any]:
    if analyze_smc is None:
        return empty_smc()

    try:
        value = analyze_smc(historical_df)

        if isinstance(value, dict):
            return value

        return empty_smc()

    except Exception as exc:
        print(
            f"[MarketIQ] SMC warning: {exc}"
        )

        return empty_smc()


# ============================================================
# RECOMMENDATION
# ============================================================


def calculate_recommendation(
    indicators: Dict[str, Any],
    pattern: Dict[str, Any],
    market_structure: Dict[str, Any],
    support_resistance: Dict[str, Any],
    smc: Dict[str, Any],
) -> Dict[str, Any]:

    try:

        # Current MarketIQ engine.
        recommendation = generate_recommendation(
            indicators,
            pattern,
            market_structure,
            support_resistance,
            smc,
        )

    except TypeError:

        # Compatibility with older engine.
        try:

            recommendation = generate_recommendation(
                indicators,
                pattern,
                market_structure,
                support_resistance,
            )

        except Exception as exc:

            print(
                f"[MarketIQ] Recommendation warning: {exc}"
            )

            return {}

    except Exception as exc:

        print(
            f"[MarketIQ] Recommendation warning: {exc}"
        )

        return {}

    if isinstance(recommendation, dict):
        return recommendation

    return {}


# ============================================================
# INDICATORS
# ============================================================


def build_indicators(latest) -> Dict[str, Any]:

    return {

        "Close": safe_float(
            latest.get("Close", 0)
        ),

        "RSI": safe_float(
            latest.get("RSI", 0)
        ),

        "EMA20": safe_float(
            latest.get("EMA20", 0)
        ),

        "EMA50": safe_float(
            latest.get("EMA50", 0)
        ),

        "MACD": safe_float(
            latest.get("MACD", 0)
        ),

        "MACD_SIGNAL": safe_float(
            latest.get("MACD_SIGNAL", 0)
        ),

        "MACD_BULLISH_CROSSOVER": safe_bool(
            latest.get(
                "MACD_BULLISH_CROSSOVER",
                False,
            )
        ),

        "MACD_BEARISH_CROSSOVER": safe_bool(
            latest.get(
                "MACD_BEARISH_CROSSOVER",
                False,
            )
        ),
    }


# ============================================================
# STRATEGY CONFIRMATION
# ============================================================


def strategy_confirmation(
    action: str,
    indicators: Dict[str, Any],
    smc: Dict[str, Any],
) -> Dict[str, Any]:

    if action not in {"BUY", "SELL"}:

        return {
            "approved": True,
            "reasons": [],
            "checks": {},
        }

    reasons: List[str] = []

    checks: Dict[str, bool] = {}

    ema20 = safe_float(
        indicators.get("EMA20")
    )

    ema50 = safe_float(
        indicators.get("EMA50")
    )

    rsi = safe_float(
        indicators.get("RSI")
    )

    macd = safe_float(
        indicators.get("MACD")
    )

    macd_signal = safe_float(
        indicators.get("MACD_SIGNAL")
    )

    bullish_cross = safe_bool(
        indicators.get(
            "MACD_BULLISH_CROSSOVER"
        )
    )

    bearish_cross = safe_bool(
        indicators.get(
            "MACD_BEARISH_CROSSOVER"
        )
    )

    smc_signal = clean_action(
        smc.get("signal", "HOLD")
    )

    smc_confidence = max(
        0.0,
        min(
            100.0,
            safe_float(
                smc.get("confidence", 0)
            ),
        ),
    )

    # --------------------------------------------------------
    # TREND
    # --------------------------------------------------------

    if ENABLE_TREND_FILTER:

        if action == "BUY":

            trend_ok = (
                ema20 > ema50
            )

            checks["trend"] = trend_ok

            if not trend_ok:
                reasons.append(
                    "BUY rejected: EMA20 is not above EMA50"
                )

        else:

            trend_ok = (
                ema20 < ema50
            )

            checks["trend"] = trend_ok

            if not trend_ok:
                reasons.append(
                    "SELL rejected: EMA20 is not below EMA50"
                )

    else:

        checks["trend"] = True

    # --------------------------------------------------------
    # RSI
    # --------------------------------------------------------

    if ENABLE_RSI_FILTER:

        if action == "BUY":

            rsi_ok = (
                BUY_MIN_RSI
                <= rsi
                <= BUY_MAX_RSI
            )

            checks["rsi"] = rsi_ok

            if not rsi_ok:

                if rsi > BUY_MAX_RSI:

                    reasons.append(
                        "BUY rejected: RSI is overbought"
                    )

                else:

                    reasons.append(
                        "BUY rejected: RSI is too weak"
                    )

        else:

            rsi_ok = (
                SELL_MIN_RSI
                <= rsi
                <= SELL_MAX_RSI
            )

            checks["rsi"] = rsi_ok

            if not rsi_ok:

                if rsi < SELL_MIN_RSI:

                    reasons.append(
                        "SELL rejected: RSI is oversold"
                    )

                else:

                    reasons.append(
                        "SELL rejected: RSI is too strong"
                    )

    else:

        checks["rsi"] = True

    # --------------------------------------------------------
    # MACD
    # --------------------------------------------------------

    if ENABLE_MACD_FILTER:

        if action == "BUY":

            macd_ok = (
                macd >= macd_signal
                or bullish_cross
            )

            checks["macd"] = macd_ok

            if not macd_ok:

                reasons.append(
                    "BUY rejected: MACD is bearish"
                )

        else:

            macd_ok = (
                macd <= macd_signal
                or bearish_cross
            )

            checks["macd"] = macd_ok

            if not macd_ok:

                reasons.append(
                    "SELL rejected: MACD is bullish"
                )

    else:

        checks["macd"] = True

    # --------------------------------------------------------
    # SMC CONFLICT
    # --------------------------------------------------------

    if ENABLE_SMC_CONFLICT_FILTER:

        if (
            action == "BUY"
            and smc_signal == "SELL"
            and smc_confidence >= SMC_CONFLICT_CONFIDENCE
        ):

            checks["smc_conflict"] = False

            reasons.append(
                "BUY rejected: strong bearish SMC conflict"
            )

        elif (
            action == "SELL"
            and smc_signal == "BUY"
            and smc_confidence >= SMC_CONFLICT_CONFIDENCE
        ):

            checks["smc_conflict"] = False

            reasons.append(
                "SELL rejected: strong bullish SMC conflict"
            )

        else:

            checks["smc_conflict"] = True

    else:

        checks["smc_conflict"] = True

    approved = all(checks.values())

    return {
        "approved": approved,
        "reasons": reasons,
        "checks": checks,
        "smc_signal": smc_signal,
        "smc_confidence": round(
            smc_confidence,
            2,
        ),
    }


# ============================================================
# EXIT SIMULATION
# ============================================================


def simulate_trade(
    df,
    entry_index: int,
    action: str,
    entry_price: float,
    stop_loss: Optional[float],
    target: Optional[float],
) -> Optional[Dict[str, Any]]:

    if entry_index >= len(df):
        return None

    if entry_price <= 0:
        return None

    valid_stop = safe_float(
        stop_loss,
        0,
    )

    valid_target = safe_float(
        target,
        0,
    )

    # --------------------------------------------------------
    # VALIDATE LEVELS
    # --------------------------------------------------------

    if action == "BUY":

        if (
            valid_stop <= 0
            or valid_stop >= entry_price
        ):

            valid_stop = (
                entry_price * 0.98
            )

        if valid_target <= entry_price:

            valid_target = (
                entry_price
                + (
                    (
                        entry_price
                        - valid_stop
                    )
                    * MIN_RISK_REWARD
                )
            )

    else:

        if (
            valid_stop <= entry_price
        ):

            valid_stop = (
                entry_price * 1.02
            )

        if (
            valid_target <= 0
            or valid_target >= entry_price
        ):

            valid_target = (
                entry_price
                - (
                    (
                        valid_stop
                        - entry_price
                    )
                    * MIN_RISK_REWARD
                )
            )

    # --------------------------------------------------------
    # HOLDING WINDOW
    # --------------------------------------------------------

    last_index = min(
        len(df) - 1,
        entry_index
        + MAX_HOLDING_DAYS
        - 1,
    )

    exit_index = last_index

    exit_price = safe_float(
        df.iloc[last_index]["Close"],
        entry_price,
    )

    exit_reason = (
        "MAX_HOLDING_PERIOD"
    )

    # --------------------------------------------------------
    # WALK THROUGH CANDLES
    # --------------------------------------------------------

    for j in range(
        entry_index,
        last_index + 1,
    ):

        candle = df.iloc[j]

        open_price = safe_float(
            candle["Open"],
            0,
        )

        high = safe_float(
            candle["High"],
            0,
        )

        low = safe_float(
            candle["Low"],
            0,
        )

        close = safe_float(
            candle["Close"],
            entry_price,
        )

        # ----------------------------------------------------
        # BUY
        # ----------------------------------------------------

        if action == "BUY":

            # Gap below stop.
            if (
                j == entry_index
                and open_price > 0
                and open_price <= valid_stop
            ):

                exit_index = j
                exit_price = open_price
                exit_reason = "STOP_LOSS_GAP"
                break

            # Gap above target.
            if (
                j == entry_index
                and open_price > 0
                and open_price >= valid_target
            ):

                exit_index = j
                exit_price = open_price
                exit_reason = "TARGET_GAP"
                break

            # Conservative daily OHLC:
            # stop is checked before target.
            if (
                low > 0
                and low <= valid_stop
            ):

                exit_index = j
                exit_price = valid_stop
                exit_reason = "STOP_LOSS"
                break

            if (
                high > 0
                and high >= valid_target
            ):

                exit_index = j
                exit_price = valid_target
                exit_reason = "TARGET"
                break

        # ----------------------------------------------------
        # SELL
        # ----------------------------------------------------

        else:

            # Gap above stop.
            if (
                j == entry_index
                and open_price > 0
                and open_price >= valid_stop
            ):

                exit_index = j
                exit_price = open_price
                exit_reason = "STOP_LOSS_GAP"
                break

            # Gap below target.
            if (
                j == entry_index
                and open_price > 0
                and open_price <= valid_target
            ):

                exit_index = j
                exit_price = open_price
                exit_reason = "TARGET_GAP"
                break

            # Conservative daily OHLC:
            # stop is checked before target.
            if (
                high > 0
                and high >= valid_stop
            ):

                exit_index = j
                exit_price = valid_stop
                exit_reason = "STOP_LOSS"
                break

            if (
                low > 0
                and low <= valid_target
            ):

                exit_index = j
                exit_price = valid_target
                exit_reason = "TARGET"
                break

        # Avoid unused variable warnings.
        _ = close

    # --------------------------------------------------------
    # RETURN
    # --------------------------------------------------------

    if action == "BUY":

        return_percent = (
            (
                exit_price
                - entry_price
            )
            / entry_price
        ) * 100

    else:

        return_percent = (
            (
                entry_price
                - exit_price
            )
            / entry_price
        ) * 100

    return {
        "exit_index": exit_index,

        "exit_date": format_date(
            df.index[exit_index]
        ),

        "exit_price": round(
            exit_price,
            2,
        ),

        "return_percent": round(
            return_percent,
            2,
        ),

        "exit_reason": exit_reason,

        "stop_loss": round(
            valid_stop,
            2,
        ),

        "target": round(
            valid_target,
            2,
        ),
    }


# ============================================================
# MAIN BACKTEST ENGINE
# ============================================================


def run_backtest(
    symbol: str,
    period: str = "1y",
):

    symbol = str(
        symbol or ""
    ).upper().strip()

    period = str(
        period or "1y"
    ).strip().lower()

    if not symbol:

        return {
            "success": False,
            "message": "Stock symbol is required.",
        }

    print(
        f"[MarketIQ] Starting backtest: "
        f"{symbol} / {period}"
    )

    # ========================================================
    # LOAD DATA
    # ========================================================

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
                f"Unable to load historical data "
                f"for {symbol}: {exc}"
            ),
        }

    if df is None or df.empty:

        return {
            "success": False,
            "message": (
                f"No historical data found "
                f"for {symbol}."
            ),
        }

    print(
        f"[MarketIQ] Loaded {len(df)} candles"
    )

    # ========================================================
    # INDICATORS
    # ========================================================

    try:

        df = calculate_indicators(df)

    except Exception as exc:

        return {
            "success": False,
            "message": (
                f"Unable to calculate indicators "
                f"for {symbol}: {exc}"
            ),
        }

    required_columns = [
        "Open",
        "High",
        "Low",
        "Close",
        "RSI",
        "EMA20",
        "EMA50",
        "MACD",
        "MACD_SIGNAL",
    ]

    missing = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing:

        return {
            "success": False,
            "message": (
                "Required columns are missing: "
                + ", ".join(missing)
            ),
        }

    df = df.dropna(
        subset=required_columns
    ).copy()

    if len(df) < 60:

        return {
            "success": False,
            "message": (
                "Not enough historical data "
                "for backtesting. At least "
                "60 valid candles are required."
            ),
        }

    # ========================================================
    # STATE
    # ========================================================

    capital = INITIAL_CAPITAL

    peak_capital = INITIAL_CAPITAL

    max_drawdown = 0.0

    results: List[
        Dict[str, Any]
    ] = []

    trades: List[
        Dict[str, Any]
    ] = []

    equity_curve: List[
        Dict[str, Any]
    ] = []

    total_signal_errors = 0

    total_rejected_by_strategy = 0

    rejection_reasons: Dict[
        str,
        int,
    ] = {}

    position_size_percent = max(
        0.0,
        min(
            100.0,
            POSITION_SIZE_PERCENT,
        ),
    )

    active_exit_index = -1

    start_index = 50

    total_iterations = (
        len(df)
        - start_index
        - 1
    )

    # ========================================================
    # WALK FORWARD
    # ========================================================

    for i in range(
        start_index,
        len(df) - 1,
    ):

        try:

            # ------------------------------------------------
            # PERFORMANCE OPTIMIZATION
            # ------------------------------------------------
            #
            # Instead of passing the complete dataframe
            # every time, only the most recent analysis
            # window is used.
            #
            # This greatly reduces the cost for 2Y/5Y
            # backtests while preserving the walk-forward
            # nature of the test.
            # ------------------------------------------------

            window_start = max(
                0,
                i + 1 - ANALYSIS_LOOKBACK,
            )

            historical_df = df.iloc[
                window_start : i + 1
            ].copy()

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
                or next_close <= 0
            ):

                continue

            # ------------------------------------------------
            # MARKETIQ ANALYSIS
            # ------------------------------------------------

            pattern = detect_pattern(
                historical_df
            )

            if not isinstance(
                pattern,
                dict,
            ):

                pattern = {}

            market_structure = (
                detect_market_structure(
                    historical_df
                )
            )

            if not isinstance(
                market_structure,
                dict,
            ):

                market_structure = {}

            support_resistance = (
                calculate_support_resistance(
                    historical_df
                )
            )

            if not isinstance(
                support_resistance,
                dict,
            ):

                support_resistance = {}

            smc = calculate_smc(
                historical_df
            )

            latest = historical_df.iloc[-1]

            indicators = build_indicators(
                latest
            )

            recommendation = (
                calculate_recommendation(
                    indicators,
                    pattern,
                    market_structure,
                    support_resistance,
                    smc,
                )
            )

            # ------------------------------------------------
            # RECOMMENDATION
            # ------------------------------------------------

            raw_action = clean_action(
                recommendation.get(
                    "recommendation",
                    "HOLD",
                )
            )

            confidence = max(
                0.0,
                min(
                    100.0,
                    safe_float(
                        recommendation.get(
                            "confidence",
                            0,
                        )
                    ),
                ),
            )

            score = safe_float(
                recommendation.get(
                    "score",
                    0,
                )
            )

            trade_setup = (
                recommendation.get(
                    "trade_setup",
                    {},
                )
            )

            if not isinstance(
                trade_setup,
                dict,
            ):

                trade_setup = {}

            setup_available = safe_bool(
                trade_setup.get(
                    "setup_available",
                    recommendation.get(
                        "setup_available",
                        False,
                    ),
                )
            )

            risk_reward = safe_float(
                recommendation.get(
                    "risk_reward",
                    trade_setup.get(
                        "risk_reward",
                        0,
                    ),
                ),
                0,
            )

            # ------------------------------------------------
            # PREDICTION ACCURACY
            # ------------------------------------------------

            if next_close > current_close:

                actual_direction = "UP"

            elif next_close < current_close:

                actual_direction = "DOWN"

            else:

                actual_direction = "FLAT"

            correct = None

            if raw_action == "BUY":

                correct = (
                    actual_direction
                    == "UP"
                )

            elif raw_action == "SELL":

                correct = (
                    actual_direction
                    == "DOWN"
                )

            # ------------------------------------------------
            # TRADE APPROVAL
            # ------------------------------------------------

            action = raw_action

            approval_reason = ""

            confirmation = {
                "approved": True,
                "reasons": [],
                "checks": {},
            }

            if raw_action in {
                "BUY",
                "SELL",
            }:

                if confidence < MIN_CONFIDENCE:

                    action = "HOLD"

                    approval_reason = (
                        "Confidence below "
                        "minimum threshold"
                    )

                elif not setup_available:

                    action = "HOLD"

                    approval_reason = (
                        "AI trade setup "
                        "is not approved"
                    )

                elif risk_reward < MIN_RISK_REWARD:

                    action = "HOLD"

                    approval_reason = (
                        "Risk/reward below "
                        "minimum threshold"
                    )

                elif (
                    i + 1
                ) <= active_exit_index:

                    action = "HOLD"

                    approval_reason = (
                        "Existing trade "
                        "is still open"
                    )

                else:

                    confirmation = (
                        strategy_confirmation(
                            raw_action,
                            indicators,
                            smc,
                        )
                    )

                    if not confirmation[
                        "approved"
                    ]:

                        action = "HOLD"

                        total_rejected_by_strategy += 1

                        reasons = (
                            confirmation.get(
                                "reasons",
                                [],
                            )
                        )

                        if reasons:

                            approval_reason = (
                                " | ".join(
                                    reasons
                                )
                            )

                            for reason in reasons:

                                rejection_reasons[
                                    reason
                                ] = (
                                    rejection_reasons.get(
                                        reason,
                                        0,
                                    )
                                    + 1
                                )

                        else:

                            approval_reason = (
                                "Strategy confirmation failed"
                            )

                    else:

                        approval_reason = (
                            "Trade setup approved "
                            "with strategy confirmation"
                        )

            # ------------------------------------------------
            # DATES
            # ------------------------------------------------

            signal_date = format_date(
                df.index[i]
            )

            next_date = format_date(
                next_candle.name
            )

            # ------------------------------------------------
            # RESULT
            # ------------------------------------------------

            result = {

                "date": signal_date,

                "action": action,

                "raw_action": raw_action,

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

                "setup_available":
                    setup_available,

                "risk_reward": (
                    round(
                        risk_reward,
                        2,
                    )
                    if risk_reward > 0
                    else None
                ),

                "risk_level":
                    recommendation.get(
                        "risk_level"
                    ),

                "approval_reason":
                    approval_reason,

                "ai_entry_price":
                    round_or_none(
                        recommendation.get(
                            "entry_price"
                        )
                    ),

                "ai_stop_loss":
                    round_or_none(
                        recommendation.get(
                            "stop_loss"
                        )
                    ),

                "ai_target":
                    round_or_none(
                        recommendation.get(
                            "target"
                        )
                    ),

                "ema20":
                    round_or_none(
                        indicators.get(
                            "EMA20"
                        )
                    ),

                "ema50":
                    round_or_none(
                        indicators.get(
                            "EMA50"
                        )
                    ),

                "rsi":
                    round_or_none(
                        indicators.get(
                            "RSI"
                        )
                    ),

                "macd":
                    round_or_none(
                        indicators.get(
                            "MACD"
                        )
                    ),

                "macd_signal":
                    round_or_none(
                        indicators.get(
                            "MACD_SIGNAL"
                        )
                    ),

                "smc_signal":
                    confirmation.get(
                        "smc_signal",
                        clean_action(
                            smc.get(
                                "signal",
                                "HOLD",
                            )
                        ),
                    ),

                "smc_confidence":
                    confirmation.get(
                        "smc_confidence",
                        round(
                            safe_float(
                                smc.get(
                                    "confidence",
                                    0,
                                )
                            ),
                            2,
                        ),
                    ),

                "strategy_checks":
                    confirmation.get(
                        "checks",
                        {},
                    ),
            }

            # ------------------------------------------------
            # TRADE
            # ------------------------------------------------

            if action in {
                "BUY",
                "SELL",
            }:

                stop_loss = (
                    round_or_none(
                        recommendation.get(
                            "stop_loss"
                        )
                    )
                )

                target = (
                    round_or_none(
                        recommendation.get(
                            "target"
                        )
                    )
                )

                simulated = simulate_trade(
                    df,
                    entry_index=i + 1,
                    action=action,
                    entry_price=next_open,
                    stop_loss=stop_loss,
                    target=target,
                )

                if simulated is not None:

                    capital_before = capital

                    position_capital = (
                        capital_before
                        * position_size_percent
                        / 100.0
                    )

                    position_capital = max(
                        0.0,
                        min(
                            capital_before,
                            position_capital,
                        ),
                    )

                    profit_loss = (
                        position_capital
                        * simulated[
                            "return_percent"
                        ]
                        / 100.0
                    )

                    capital = (
                        capital_before
                        + profit_loss
                    )

                    if profit_loss > 0:

                        trade_result = "WIN"

                    elif profit_loss < 0:

                        trade_result = "LOSS"

                    else:

                        trade_result = "FLAT"

                    # ------------------------------------------------
                    # DRAW DOWN
                    # ------------------------------------------------

                    if capital > peak_capital:

                        peak_capital = capital

                    drawdown = (

                        (
                            peak_capital
                            - capital
                        )
                        / peak_capital
                    ) * 100.0

                    max_drawdown = max(
                        max_drawdown,
                        drawdown,
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

                        "raw_action":
                            raw_action,

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
                                next_open,
                                2,
                            ),

                        "exit_price":
                            simulated[
                                "exit_price"
                            ],

                        "return_percent":
                            simulated[
                                "return_percent"
                            ],

                        "position_size_percent":
                            round(
                                position_size_percent,
                                2,
                            ),

                        "position_capital":
                            round(
                                position_capital,
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

                        "exit_reason":
                            simulated[
                                "exit_reason"
                            ],

                        "exit_date":
                            simulated[
                                "exit_date"
                            ],

                        "stop_loss":
                            simulated[
                                "stop_loss"
                            ],

                        "target":
                            simulated[
                                "target"
                            ],

                        "risk_reward":
                            (
                                round(
                                    risk_reward,
                                    2,
                                )
                                if risk_reward > 0
                                else None
                            ),

                        "risk_level":
                            recommendation.get(
                                "risk_level"
                            ),

                        "holding_days":
                            (
                                simulated[
                                    "exit_index"
                                ]
                                - (i + 1)
                                + 1
                            ),

                        "rsi":
                            round(
                                safe_float(
                                    indicators.get(
                                        "RSI"
                                    )
                                ),
                                2,
                            ),

                        "ema20":
                            round(
                                safe_float(
                                    indicators.get(
                                        "EMA20"
                                    )
                                ),
                                2,
                            ),

                        "ema50":
                            round(
                                safe_float(
                                    indicators.get(
                                        "EMA50"
                                    )
                                ),
                                2,
                            ),

                        "smc_signal":
                            clean_action(
                                smc.get(
                                    "signal",
                                    "HOLD",
                                )
                            ),

                        "smc_confidence":
                            round(
                                safe_float(
                                    smc.get(
                                        "confidence",
                                        0,
                                    )
                                ),
                                2,
                            ),
                    }

                    trades.append(
                        trade
                    )

                    active_exit_index = (
                        simulated[
                            "exit_index"
                        ]
                    )

                    result.update({

                        "trade": True,

                        "trade_result":
                            trade_result,

                        "trade_return_percent":
                            simulated[
                                "return_percent"
                            ],

                        "position_size_percent":
                            round(
                                position_size_percent,
                                2,
                            ),

                        "position_capital":
                            round(
                                position_capital,
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

                        "exit_reason":
                            simulated[
                                "exit_reason"
                            ],

                        "exit_date":
                            simulated[
                                "exit_date"
                            ],
                    })

                else:

                    result.update({

                        "trade": False,

                        "trade_result": None,

                        "trade_return_percent":
                            None,

                        "position_size_percent":
                            0.0,

                        "position_capital":
                            0.0,

                        "profit_loss":
                            0.0,

                        "capital_after":
                            round(
                                capital,
                                2,
                            ),
                    })

            else:

                result.update({

                    "trade": False,

                    "trade_result": None,

                    "trade_return_percent":
                        None,

                    "position_size_percent":
                        0.0,

                    "position_capital":
                        0.0,

                    "profit_loss":
                        0.0,

                    "capital_after":
                        round(
                            capital,
                            2,
                        ),
                })

            results.append(
                result
            )

            # ------------------------------------------------
            # EQUITY CURVE
            # ------------------------------------------------

            equity_curve.append({

                "date":
                    next_date,

                "capital":
                    round(
                        capital,
                        2,
                    ),
            })

            # ------------------------------------------------
            # PROGRESS LOGGING
            # ------------------------------------------------

            completed = (
                i
                - start_index
                + 1
            )

            if (
                completed % 25 == 0
                or completed
                == total_iterations
            ):

                progress = (
                    completed
                    / max(
                        total_iterations,
                        1,
                    )
                ) * 100.0

                print(
                    f"[MarketIQ] "
                    f"{symbol} backtest "
                    f"{progress:.0f}% "
                    f"({completed}/"
                    f"{total_iterations}) "
                    f"trades={len(trades)}"
                )

        except Exception as exc:

            total_signal_errors += 1

            print(
                f"[MarketIQ] Backtest warning "
                f"for {symbol} at index {i}: "
                f"{exc}"
            )

            continue

    # ========================================================
    # STATISTICS
    # ========================================================

    prediction_results = [
        item
        for item in results
        if item.get("correct") is not None
    ]

    total_predictions = len(
        prediction_results
    )

    correct_predictions = sum(
        1
        for item in prediction_results
        if item.get("correct") is True
    )

    accuracy = (

        (
            correct_predictions
            / total_predictions
        )
        * 100.0

        if total_predictions

        else 0.0
    )

    # --------------------------------------------------------
    # RAW SIGNALS
    # --------------------------------------------------------

    raw_buy_signals = sum(
        1
        for item in results
        if item.get("raw_action")
        == "BUY"
    )

    raw_sell_signals = sum(
        1
        for item in results
        if item.get("raw_action")
        == "SELL"
    )

    raw_hold_signals = sum(
        1
        for item in results
        if item.get("raw_action")
        == "HOLD"
    )

    # --------------------------------------------------------
    # FINAL SIGNALS
    # Count signals only from the same prediction population
    # used for prediction accuracy. This keeps the dashboard
    # totals internally consistent.
    # --------------------------------------------------------

    buy_signals = sum(
        1
        for item in prediction_results
        if item.get("action")
        == "BUY"
    )

    sell_signals = sum(
        1
        for item in prediction_results
        if item.get("action")
        == "SELL"
    )

    hold_signals = sum(
        1
        for item in prediction_results
        if item.get("action")
        == "HOLD"
    )

    # --------------------------------------------------------
    # TRADES
    # --------------------------------------------------------

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

    win_rate = (

        (
            winning_trades
            / total_trades
        )
        * 100.0

        if total_trades

        else 0.0
    )

    # --------------------------------------------------------
    # CAPITAL
    # --------------------------------------------------------

    final_capital = capital

    net_profit_loss = (
        final_capital
        - INITIAL_CAPITAL
    )

    total_return = (
        net_profit_loss
        / INITIAL_CAPITAL
    ) * 100.0

    # --------------------------------------------------------
    # TRADE RETURNS
    # --------------------------------------------------------

    average_trade_return = (

        sum(
            trade[
                "return_percent"
            ]
            for trade in trades
        )
        / total_trades

        if total_trades

        else 0.0
    )

    average_win = (

        sum(
            trade[
                "return_percent"
            ]
            for trade in trades
            if trade[
                "return_percent"
            ] > 0
        )
        / winning_trades

        if winning_trades

        else 0.0
    )

    average_loss = (

        sum(
            trade[
                "return_percent"
            ]
            for trade in trades
            if trade[
                "return_percent"
            ] < 0
        )
        / losing_trades

        if losing_trades

        else 0.0
    )

    # --------------------------------------------------------
    # PROFIT FACTOR
    # --------------------------------------------------------

    gross_profit = sum(

        trade["profit_loss"]

        for trade in trades

        if trade["profit_loss"] > 0
    )

    gross_loss = abs(
        sum(

            trade["profit_loss"]

            for trade in trades

            if trade["profit_loss"] < 0
        )
    )

    if gross_loss > 0:

        profit_factor = (
            gross_profit
            / gross_loss
        )

    elif gross_profit > 0:

        profit_factor = float(
            "inf"
        )

    else:

        profit_factor = 0.0

    # --------------------------------------------------------
    # BUY / SELL PERFORMANCE
    # --------------------------------------------------------

    buy_trades = [
        trade
        for trade in trades
        if trade["action"] == "BUY"
    ]

    sell_trades = [
        trade
        for trade in trades
        if trade["action"] == "SELL"
    ]

    buy_wins = sum(
        1
        for trade in buy_trades
        if trade["profit_loss"] > 0
    )

    sell_wins = sum(
        1
        for trade in sell_trades
        if trade["profit_loss"] > 0
    )

    buy_win_rate = (

        (
            buy_wins
            / len(buy_trades)
        )
        * 100.0

        if buy_trades

        else 0.0
    )

    sell_win_rate = (

        (
            sell_wins
            / len(sell_trades)
        )
        * 100.0

        if sell_trades

        else 0.0
    )

    # --------------------------------------------------------
    # BEST / WORST
    # --------------------------------------------------------

    best_trade = (

        max(
            trades,
            key=lambda x:
                x["profit_loss"],
        )

        if trades

        else None
    )

    worst_trade = (

        min(
            trades,
            key=lambda x:
                x["profit_loss"],
        )

        if trades

        else None
    )

    # ========================================================
    # FINAL RESPONSE
    # ========================================================

    print(
        f"[MarketIQ] Backtest complete: "
        f"{symbol} | "
        f"Trades={total_trades} | "
        f"WinRate={win_rate:.2f}% | "
        f"Return={total_return:.2f}%"
    )

    summary = {

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

        "raw_buy_signals":
            raw_buy_signals,

        "raw_sell_signals":
            raw_sell_signals,

        "raw_hold_signals":
            raw_hold_signals,

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

        "buy_trades":
            len(buy_trades),

        "sell_trades":
            len(sell_trades),

        "buy_wins":
            buy_wins,

        "sell_wins":
            sell_wins,

        "buy_win_rate":
            round(
                buy_win_rate,
                2,
            ),

        "sell_win_rate":
            round(
                sell_win_rate,
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

        "average_trade_return":
            round(
                average_trade_return,
                2,
            ),

        "average_win":
            round(
                average_win,
                2,
            ),

        "average_loss":
            round(
                average_loss,
                2,
            ),

        "gross_profit":
            round(
                gross_profit,
                2,
            ),

        "gross_loss":
            round(
                gross_loss,
                2,
            ),

        "profit_factor": (
            round(
                profit_factor,
                2,
            )
            if math.isfinite(
                profit_factor
            )
            else None
        ),

        "position_size_percent":
            round(
                position_size_percent,
                2,
            ),

        "minimum_confidence":
            MIN_CONFIDENCE,

        "minimum_risk_reward":
            MIN_RISK_REWARD,

        "max_holding_days":
            MAX_HOLDING_DAYS,

        "analysis_lookback":
            ANALYSIS_LOOKBACK,

        "strategy_filters": {
            "trend":
                ENABLE_TREND_FILTER,

            "rsi":
                ENABLE_RSI_FILTER,

            "macd":
                ENABLE_MACD_FILTER,

            "smc_conflict":
                ENABLE_SMC_CONFLICT_FILTER,
        },

        "strategy_rejections":
            total_rejected_by_strategy,

        "rejection_reasons":
            rejection_reasons,

        "backtest_warnings":
            total_signal_errors,
    }

    return {

        "success": True,

        "symbol":
            symbol,

        "period":
            period,

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

        "position_size_percent":
            round(
                position_size_percent,
                2,
            ),

        "minimum_confidence":
            MIN_CONFIDENCE,

        "minimum_risk_reward":
            MIN_RISK_REWARD,

        "max_holding_days":
            MAX_HOLDING_DAYS,

        "analysis_lookback":
            ANALYSIS_LOOKBACK,

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

        "buy_trades":
            len(buy_trades),

        "sell_trades":
            len(sell_trades),

        "buy_win_rate":
            round(
                buy_win_rate,
                2,
            ),

        "sell_win_rate":
            round(
                sell_win_rate,
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

        "average_win":
            round(
                average_win,
                2,
            ),

        "average_loss":
            round(
                average_loss,
                2,
            ),

        "gross_profit":
            round(
                gross_profit,
                2,
            ),

        "gross_loss":
            round(
                gross_loss,
                2,
            ),

        "profit_factor": (
            round(
                profit_factor,
                2,
            )
            if math.isfinite(
                profit_factor
            )
            else None
        ),

        "raw_buy_signals":
            raw_buy_signals,

        "raw_sell_signals":
            raw_sell_signals,

        "raw_hold_signals":
            raw_hold_signals,

        "buy_signals":
            buy_signals,

        "sell_signals":
            sell_signals,

        "hold_signals":
            hold_signals,

        "strategy_rejections":
            total_rejected_by_strategy,

        "rejection_reasons":
            rejection_reasons,

        "backtest_warnings":
            total_signal_errors,

        "summary":
            summary,

        "best_trade":
            best_trade,

        "worst_trade":
            worst_trade,

        "equity_curve":
            equity_curve,

        "trades":
            trades,

        "results":
            results,
    }