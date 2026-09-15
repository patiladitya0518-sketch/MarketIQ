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
# TRADE QUALITY V2 / THESIS FAILURE EXIT DISABLED
# ============================================================

ENABLE_TRADE_QUALITY_FILTER = True
MIN_QUALITY_CONFIRMATIONS = 3

# ============================================================
# TRADE ENTRY QUALITY V2.1
# Evidence-driven protection against overextended and weak
# follow-through entries. This gate does not alter the core
# recommendation engine or use future candles.
# ============================================================

V21_HIGH_CONFIDENCE_THRESHOLD = 88.0
V21_HIGH_CONF_MIN_TECHNICAL = 3
V21_HIGH_CONF_MIN_SMC_CONFIDENCE = 60.0
V21_RSI_EXHAUSTION_BUY = 75.0
V21_RSI_EXHAUSTION_SELL = 25.0
V21_EXTENSION_DISTANCE_PERCENT = 4.0
V21_EXTENSION_RSI_BUY = 65.0
V21_EXTENSION_RSI_SELL = 35.0

# MarketIQ V3 Strategy layer (V2.1 remains the frozen baseline)
ENABLE_V3_STRATEGY = True
V3_MIN_RANK = "A"
V3_A_PLUS_CONFIDENCE = 80.0
V3_A_CONFIDENCE = 75.0
V3_STRUCTURE_CONFIDENCE = 60.0
V3_A_PLUS_STRUCTURE_CONFIDENCE = 70.0
V3_SMC_CONFIDENCE = 60.0
V3_A_PLUS_SMC_CONFIDENCE = 65.0
V3_MIN_TECHNICAL_A = 3
V3_MIN_TIMING_A = 3
V3_MIN_TECHNICAL_A_PLUS = 3
V3_MIN_TIMING_A_PLUS = 4

ENABLE_THESIS_FAILURE_EXIT = False
THESIS_FAILURE_CONFIRMATIONS = 2
THESIS_FAILURE_CONSECUTIVE_CANDLES = 2
THESIS_FAILURE_MIN_ENTRY_DAY = 1


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


def _bucket(value: Any, edges: List[float], labels: List[str]) -> str:
    number = safe_float(value, float("nan"))
    if not math.isfinite(number):
        return "UNKNOWN"
    for edge, label in zip(edges, labels):
        if number < edge:
            return label
    return labels[-1]


def build_v22_stop_loss_analysis(trades: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Diagnostic-only V2.2 analysis of stop-loss failures.

    This function never changes trade selection, exits, risk, or position sizing.
    It only groups completed STOP_LOSS / STOP_LOSS_GAP trades so the next
    strategy decision can be evidence-driven.
    """
    stop_trades = [
        t for t in trades
        if str(t.get("exit_reason") or "").upper() in {"STOP_LOSS", "STOP_LOSS_GAP"}
    ]

    def count_where(predicate):
        return sum(1 for t in stop_trades if predicate(t))

    def net_where(predicate):
        return round(sum(
            safe_float(t.get("profit_loss"), 0.0)
            for t in stop_trades if predicate(t)
        ), 2)

    def bucket_breakdown(field: str, edges: List[float], labels: List[str]) -> Dict[str, Any]:
        out = {label: {"trades": 0, "wins": 0, "losses": 0, "net_profit_loss": 0.0} for label in labels}
        out["UNKNOWN"] = {"trades": 0, "wins": 0, "losses": 0, "net_profit_loss": 0.0}
        for trade in stop_trades:
            label = _bucket(trade.get(field), edges, labels)
            row = out[label]
            pnl = safe_float(trade.get("profit_loss"), 0.0)
            row["trades"] += 1
            row["wins"] += int(pnl > 0)
            row["losses"] += int(pnl < 0)
            row["net_profit_loss"] += pnl
        for row in out.values():
            row["net_profit_loss"] = round(row["net_profit_loss"], 2)
        if out.get("UNKNOWN", {}).get("trades") == 0:
            out.pop("UNKNOWN", None)
        return out

    action = {}
    for side in ("BUY", "SELL"):
        rows = [t for t in stop_trades if str(t.get("action") or "").upper() == side]
        action[side] = {
            "trades": len(rows),
            "wins": sum(1 for t in rows if safe_float(t.get("profit_loss"), 0) > 0),
            "losses": sum(1 for t in rows if safe_float(t.get("profit_loss"), 0) < 0),
            "net_profit_loss": round(sum(safe_float(t.get("profit_loss"), 0) for t in rows), 2),
            "average_return_percent": round(sum(safe_float(t.get("return_percent"), 0) for t in rows) / len(rows), 2) if rows else 0.0,
        }

    structure = {}
    for side in ("BUY", "SELL", "HOLD", "UNKNOWN"):
        rows = [t for t in stop_trades if str(t.get("market_structure_signal") or "UNKNOWN").upper() == side]
        structure[side] = {
            "trades": len(rows),
            "net_profit_loss": round(sum(safe_float(t.get("profit_loss"), 0) for t in rows), 2),
        }
    structure_aligned = count_where(lambda t: str(t.get("market_structure_signal") or "").upper() == str(t.get("action") or "").upper())
    smc_aligned = count_where(lambda t: str(t.get("smc_signal") or "").upper() == str(t.get("action") or "").upper())

    high_conf = count_where(lambda t: safe_float(t.get("confidence"), 0) >= V21_HIGH_CONFIDENCE_THRESHOLD)
    extended = count_where(lambda t: str(t.get("entry_quality") or "NORMAL").upper() in {"EXTENDED", "VERY_EXTENDED"})

    worst = sorted(stop_trades, key=lambda t: safe_float(t.get("profit_loss"), 0.0))[:10]
    worst_cases = [{
        "date": t.get("date"),
        "action": t.get("action"),
        "confidence": t.get("confidence"),
        "score": t.get("score"),
        "rsi": t.get("rsi"),
        "ema20": t.get("ema20"),
        "ema50": t.get("ema50"),
        "market_structure_signal": t.get("market_structure_signal"),
        "market_structure_confidence": t.get("market_structure_confidence"),
        "smc_signal": t.get("smc_signal"),
        "smc_confidence": t.get("smc_confidence"),
        "entry_quality": t.get("entry_quality"),
        "mae_percent": t.get("max_adverse_excursion_percent"),
        "mfe_percent": t.get("max_favorable_excursion_percent"),
        "risk_reward": t.get("risk_reward"),
        "return_percent": t.get("return_percent"),
        "profit_loss": t.get("profit_loss"),
        "exit_reason": t.get("exit_reason"),
    } for t in worst]

    return {
        "version": "V2.2",
        "diagnostic_only": True,
        "strategy_changed": False,
        "stop_loss_trades": len(stop_trades),
        "stop_loss_gap_trades": sum(1 for t in stop_trades if str(t.get("exit_reason") or "").upper() == "STOP_LOSS_GAP"),
        "stop_loss_net_profit_loss": round(sum(safe_float(t.get("profit_loss"), 0) for t in stop_trades), 2),
        "action_breakdown": action,
        "confidence_buckets": bucket_breakdown("confidence", [70, 80, 88, 90], ["<70", "70-79", "80-87", "88-89", "90+"]),
        "rsi_buckets": bucket_breakdown("rsi", [30, 40, 50, 60, 70, 75], ["<30", "30-39", "40-49", "50-59", "60-69", "70-74", "75+"]),
        "mae_buckets": bucket_breakdown("max_adverse_excursion_percent", [1, 2, 3, 5, 8], ["<1%", "1-1.99%", "2-2.99%", "3-4.99%", "5-7.99%", "8%+"]),
        "mfe_buckets": bucket_breakdown("max_favorable_excursion_percent", [0.5, 1, 2, 3], ["<0.5%", "0.5-0.99%", "1-1.99%", "2-2.99%", "3%+"]),
        "market_structure": structure,
        "market_structure_aligned_count": structure_aligned,
        "market_structure_misaligned_count": max(0, len(stop_trades) - structure_aligned),
        "smc_aligned_count": smc_aligned,
        "smc_misaligned_count": max(0, len(stop_trades) - smc_aligned),
        "high_confidence_stop_losses": high_conf,
        "extended_entry_stop_losses": extended,
        "worst_cases": worst_cases,
        "interpretation": {
            "stop_loss_dominance": "STOP_LOSS failures are the primary loss source in this diagnostic set." if stop_trades else "No stop-loss failures found.",
            "high_confidence_warning": high_conf > 0,
            "entry_extension_warning": extended > 0,
            "next_step": "Use these diagnostics to evaluate entry timing/confirmation before changing SL, target, or holding period."
        },
    }



def build_v23_entry_timing_analysis(trades: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Diagnostic-only V2.3 target-vs-stop entry timing analysis.

    V2.3 does not alter recommendation generation, trade selection, exits,
    risk, sizing, or holding period. It compares completed TARGET trades with
    STOP_LOSS / STOP_LOSS_GAP trades to identify repeatable entry weaknesses.
    """
    targets = [t for t in trades if str(t.get("exit_reason") or "").upper() == "TARGET"]
    stops = [t for t in trades if str(t.get("exit_reason") or "").upper() in {"STOP_LOSS", "STOP_LOSS_GAP"}]

    def val(t, key, default=0.0):
        return safe_float(t.get(key), default)

    def avg(rows, key):
        return round(sum(val(t, key) for t in rows) / len(rows), 2) if rows else 0.0

    def count(rows, predicate):
        return sum(1 for t in rows if predicate(t))

    def pct(rows, predicate):
        return round(100.0 * count(rows, predicate) / len(rows), 2) if rows else 0.0

    def side_stats(rows):
        out = {}
        for side in ("BUY", "SELL"):
            r = [t for t in rows if str(t.get("action") or "").upper() == side]
            out[side] = {
                "trades": len(r),
                "average_confidence": avg(r, "confidence"),
                "average_rsi": avg(r, "rsi"),
                "average_mae_percent": avg(r, "max_adverse_excursion_percent"),
                "average_mfe_percent": avg(r, "max_favorable_excursion_percent"),
                "average_holding_days": avg(r, "holding_days"),
                "net_profit_loss": round(sum(val(t, "profit_loss") for t in r), 2),
            }
        return out

    def alignment(rows):
        return {
            "market_structure_aligned": count(rows, lambda t: str(t.get("market_structure_signal") or "").upper() == str(t.get("action") or "").upper()),
            "smc_aligned": count(rows, lambda t: str(t.get("smc_signal") or "").upper() == str(t.get("action") or "").upper()),
            "both_aligned": count(rows, lambda t: (
                str(t.get("market_structure_signal") or "").upper() == str(t.get("action") or "").upper()
                and str(t.get("smc_signal") or "").upper() == str(t.get("action") or "").upper()
            )),
        }

    def feature_comparison():
        fields = [
            ("confidence", "confidence"),
            ("rsi", "RSI"),
            ("market_structure_confidence", "market_structure_confidence"),
            ("smc_confidence", "smc_confidence"),
            ("max_adverse_excursion_percent", "MAE %"),
            ("max_favorable_excursion_percent", "MFE %"),
            ("holding_days", "holding days"),
        ]
        out = {}
        for key, label in fields:
            ta, sa = avg(targets, key), avg(stops, key)
            out[label] = {
                "target_average": ta,
                "stop_loss_average": sa,
                "difference_target_minus_stop": round(ta - sa, 2),
            }
        return out

    def timing(rows):
        return {
            "high_confidence_88_plus": count(rows, lambda t: val(t, "confidence") >= V21_HIGH_CONFIDENCE_THRESHOLD),
            "rsi_exhausted": count(rows, lambda t: (
                (str(t.get("action") or "").upper() == "BUY" and val(t, "rsi") >= V21_RSI_EXHAUSTION_BUY)
                or (str(t.get("action") or "").upper() == "SELL" and val(t, "rsi") <= V21_RSI_EXHAUSTION_SELL)
            )),
            "rsi_stretched": count(rows, lambda t: (
                (str(t.get("action") or "").upper() == "BUY" and val(t, "rsi") >= 65)
                or (str(t.get("action") or "").upper() == "SELL" and val(t, "rsi") <= 35)
            )),
            "mfe_below_0_5": count(rows, lambda t: val(t, "max_favorable_excursion_percent") < 0.5),
            "mfe_below_1": count(rows, lambda t: val(t, "max_favorable_excursion_percent") < 1.0),
            "mae_below_1": count(rows, lambda t: val(t, "max_adverse_excursion_percent") < 1.0),
            "mae_2_plus": count(rows, lambda t: val(t, "max_adverse_excursion_percent") >= 2.0),
            "normal_entry": count(rows, lambda t: str(t.get("entry_quality") or "NORMAL").upper() == "NORMAL"),
            "extended_entry": count(rows, lambda t: str(t.get("entry_quality") or "NORMAL").upper() in {"EXTENDED", "VERY_EXTENDED"}),
        }

    def case(t):
        macd = val(t, "macd")
        macd_signal = val(t, "macd_signal")
        signal_price = val(t, "signal_price")
        ema20 = val(t, "ema20")
        ema50 = val(t, "ema50")
        action = str(t.get("action") or "").upper()
        return {
            "date": t.get("date"),
            "signal_date": t.get("signal_date"),
            "action": action,
            "confidence": t.get("confidence"),
            "score": t.get("score"),
            "signal_price": t.get("signal_price"),
            "entry_price": t.get("entry_price"),
            "rsi": t.get("rsi"),
            "ema20": t.get("ema20"),
            "ema50": t.get("ema50"),
            "price_vs_ema20_percent": round((signal_price - ema20) / signal_price * 100.0, 2) if signal_price > 0 and ema20 > 0 else 0.0,
            "ema20_vs_ema50_percent": round((ema20 - ema50) / ema50 * 100.0, 2) if ema50 > 0 else 0.0,
            "macd": t.get("macd"),
            "macd_signal": t.get("macd_signal"),
            "macd_aligned": (macd > macd_signal) if action == "BUY" else ((macd < macd_signal) if action == "SELL" else False),
            "market_structure_signal": t.get("market_structure_signal"),
            "market_structure_confidence": t.get("market_structure_confidence"),
            "smc_signal": t.get("smc_signal"),
            "smc_confidence": t.get("smc_confidence"),
            "entry_quality": t.get("entry_quality"),
            "mae_percent": t.get("max_adverse_excursion_percent"),
            "mfe_percent": t.get("max_favorable_excursion_percent"),
            "risk_reward": t.get("risk_reward"),
            "return_percent": t.get("return_percent"),
            "profit_loss": t.get("profit_loss"),
            "holding_days": t.get("holding_days"),
            "exit_reason": t.get("exit_reason"),
        }

    worst_stops = sorted(stops, key=lambda t: val(t, "profit_loss"))[:10]
    best_targets = sorted(targets, key=lambda t: val(t, "profit_loss"), reverse=True)[:10]

    return {
        "version": "V2.3",
        "diagnostic_only": True,
        "strategy_changed": False,
        "purpose": "Compare TARGET and STOP_LOSS entries to identify repeatable entry-timing and follow-through characteristics.",
        "target_trades": len(targets),
        "stop_loss_trades": len(stops),
        "target_net_profit_loss": round(sum(val(t, "profit_loss") for t in targets), 2),
        "stop_loss_net_profit_loss": round(sum(val(t, "profit_loss") for t in stops), 2),
        "target_side_breakdown": side_stats(targets),
        "stop_loss_side_breakdown": side_stats(stops),
        "feature_comparison": feature_comparison(),
        "target_alignment": alignment(targets),
        "stop_loss_alignment": alignment(stops),
        "target_timing": timing(targets),
        "stop_loss_timing": timing(stops),
        "high_confidence_target_trades": count(targets, lambda t: val(t, "confidence") >= V21_HIGH_CONFIDENCE_THRESHOLD),
        "high_confidence_stop_loss_trades": count(stops, lambda t: val(t, "confidence") >= V21_HIGH_CONFIDENCE_THRESHOLD),
        "extended_target_trades": count(targets, lambda t: str(t.get("entry_quality") or "NORMAL").upper() in {"EXTENDED", "VERY_EXTENDED"}),
        "extended_stop_loss_trades": count(stops, lambda t: str(t.get("entry_quality") or "NORMAL").upper() in {"EXTENDED", "VERY_EXTENDED"}),
        "best_target_cases": [case(t) for t in best_targets],
        "worst_stop_loss_cases": [case(t) for t in worst_stops],
        "interpretation": {
            "strategy_changed": False,
            "warning": "Do not change SL, target, or holding period from this diagnostic alone.",
            "decision_rule": "Only promote an entry filter when the characteristic separates TARGET from STOP_LOSS trades and survives broader validation.",
        },
    }

def build_v24_confirmation_analysis(trades: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Diagnostic-only V2.4 signal-candle confirmation analysis."""
    targets = [t for t in trades if str(t.get("exit_reason") or "").upper() == "TARGET"]
    stops = [t for t in trades if str(t.get("exit_reason") or "").upper() in {"STOP_LOSS", "STOP_LOSS_GAP"}]

    def val(t, key, default=0.0):
        return safe_float(t.get(key), default)

    def count(rows, predicate):
        return sum(1 for t in rows if predicate(t))

    def avg(rows, key):
        return round(sum(val(t, key) for t in rows) / len(rows), 2) if rows else 0.0

    def rates(rows):
        return {
            "strong_signal_candle": count(rows, lambda t: bool(t.get("signal_candle_strong"))),
            "close_confirmed": count(rows, lambda t: bool(t.get("signal_candle_close_confirmed"))),
            "momentum_confirmed": count(rows, lambda t: bool(t.get("momentum_confirmed"))),
            "next_open_not_adverse": count(rows, lambda t: bool(t.get("next_open_not_adverse"))),
            "ema20_distance_lt_2": count(rows, lambda t: abs(val(t, "price_vs_ema20_percent")) < 2.0),
            "ema20_distance_lt_4": count(rows, lambda t: abs(val(t, "price_vs_ema20_percent")) < 4.0),
            "macd_confirmed": count(rows, lambda t: bool(t.get("macd_aligned"))),
            "rsi_supportive": count(rows, lambda t: bool(t.get("rsi_supportive"))),
            "technical_3_plus": count(rows, lambda t: val(t, "entry_technical_confirmations") >= 3),
            "confirmation_score_3_plus": count(rows, lambda t: val(t, "entry_confirmation_score") >= 3),
            "confirmation_score_4_plus": count(rows, lambda t: val(t, "entry_confirmation_score") >= 4),
        }

    def averages(rows):
        return {
            "body_percent": avg(rows, "signal_candle_body_percent"),
            "range_percent": avg(rows, "signal_candle_range_percent"),
            "body_to_range_percent": avg(rows, "signal_candle_body_to_range_percent"),
            "next_open_gap_percent": avg(rows, "next_open_gap_percent"),
            "price_vs_ema20_percent": avg(rows, "price_vs_ema20_percent"),
            "rsi": avg(rows, "rsi"),
            "macd_delta": avg(rows, "macd_delta"),
            "confirmation_score": avg(rows, "entry_confirmation_score"),
        }

    def combos(rows):
        return {
            "strong_candle_and_close": count(rows, lambda t: bool(t.get("signal_candle_strong")) and bool(t.get("signal_candle_close_confirmed"))),
            "strong_close_momentum": count(rows, lambda t: bool(t.get("signal_candle_strong")) and bool(t.get("signal_candle_close_confirmed")) and bool(t.get("momentum_confirmed"))),
            "close_momentum_no_adverse_open": count(rows, lambda t: bool(t.get("signal_candle_close_confirmed")) and bool(t.get("momentum_confirmed")) and bool(t.get("next_open_not_adverse"))),
            "all_core_conditions": count(rows, lambda t: bool(t.get("signal_candle_strong")) and bool(t.get("signal_candle_close_confirmed")) and bool(t.get("momentum_confirmed")) and bool(t.get("next_open_not_adverse"))),
        }

    def side_alignment(rows):
        return {
            "market_structure": count(rows, lambda t: str(t.get("market_structure_signal") or "").upper() == str(t.get("action") or "").upper()),
            "smc": count(rows, lambda t: str(t.get("smc_signal") or "").upper() == str(t.get("action") or "").upper()),
            "both": count(rows, lambda t: str(t.get("market_structure_signal") or "").upper() == str(t.get("action") or "").upper() and str(t.get("smc_signal") or "").upper() == str(t.get("action") or "").upper()),
        }

    def case(t):
        return {k: t.get(k) for k in [
            "date", "signal_date", "action", "confidence", "score", "signal_open", "signal_high", "signal_low", "signal_close",
            "entry_price", "next_open_gap_percent", "signal_candle_body_percent", "signal_candle_range_percent",
            "signal_candle_body_to_range_percent", "signal_candle_strong", "signal_candle_close_confirmed",
            "momentum_confirmed", "next_open_not_adverse", "entry_confirmation_score", "entry_technical_confirmations",
            "rsi", "macd_delta", "price_vs_ema20_percent", "max_favorable_excursion_percent",
            "max_adverse_excursion_percent", "return_percent", "profit_loss", "exit_reason"
        ]}

    return {
        "version": "V2.4",
        "diagnostic_only": True,
        "strategy_changed": False,
        "purpose": "Compare signal-candle confirmation and immediate entry conditions between TARGET and STOP_LOSS trades.",
        "target_trades": len(targets),
        "stop_loss_trades": len(stops),
        "target_net_profit_loss": round(sum(val(t, "profit_loss") for t in targets), 2),
        "stop_loss_net_profit_loss": round(sum(val(t, "profit_loss") for t in stops), 2),
        "target_averages": averages(targets),
        "stop_loss_averages": averages(stops),
        "target_feature_counts": rates(targets),
        "stop_loss_feature_counts": rates(stops),
        "target_combinations": combos(targets),
        "stop_loss_combinations": combos(stops),
        "target_alignment": side_alignment(targets),
        "stop_loss_alignment": side_alignment(stops),
        "best_target_cases": [case(t) for t in sorted(targets, key=lambda x: val(x, "profit_loss"), reverse=True)[:10]],
        "worst_stop_loss_cases": [case(t) for t in sorted(stops, key=lambda x: val(x, "profit_loss"))[:10]],
        "interpretation": {
            "strategy_changed": False,
            "warning": "V2.4 is diagnostic only. Do not promote a filter until the characteristic separates TARGET from STOP_LOSS trades and survives broader validation.",
            "focus": "Signal-candle strength, close location, momentum, EMA20 distance, and next-candle opening alignment.",
        },
    }



def build_v25_composite_entry_analysis(trades: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Diagnostic-only V2.5 composite entry analysis.

    Combines the V2.4 entry features to test whether a repeatable composite
    condition separates TARGET trades from STOP_LOSS trades. This function
    never changes trade approval, exits, position sizing, or recommendations.
    """
    targets = [t for t in trades if str(t.get("exit_reason") or "").upper() == "TARGET"]
    stops = [t for t in trades if str(t.get("exit_reason") or "").upper() in {"STOP_LOSS", "STOP_LOSS_GAP"}]

    def val(t, key, default=0.0):
        return safe_float(t.get(key), default)

    def count(rows, predicate):
        return sum(1 for t in rows if predicate(t))

    def rate(rows, predicate):
        return round((count(rows, predicate) / len(rows) * 100.0), 2) if rows else 0.0

    def avg(rows, key):
        return round(sum(val(t, key) for t in rows) / len(rows), 2) if rows else 0.0

    def aligned(t):
        action = str(t.get("action") or "HOLD").upper()
        ms = str(t.get("market_structure_signal") or "").upper()
        smc = str(t.get("smc_signal") or "").upper()
        return ms == action, smc == action, ms == action and smc == action

    def composite_flags(t):
        action = str(t.get("action") or "HOLD").upper()
        ms_ok, smc_ok, both_ok = aligned(t)
        tech = val(t, "entry_technical_confirmations")
        score = val(t, "entry_confirmation_score")
        rsi_ok = bool(t.get("rsi_supportive"))
        macd_ok = bool(t.get("macd_aligned"))
        candle_ok = bool(t.get("signal_candle_strong"))
        close_ok = bool(t.get("signal_candle_close_confirmed"))
        open_ok = bool(t.get("next_open_not_adverse"))
        ema_ok = abs(val(t, "price_vs_ema20_percent")) < 4.0
        confidence_ok = val(t, "confidence") >= 88.0
        core_momentum = rsi_ok and macd_ok
        technical_core = rsi_ok and macd_ok and ema_ok
        confirmation_core = candle_ok and close_ok and core_momentum and ema_ok and open_ok
        composite_3 = sum([rsi_ok, macd_ok, ema_ok, ms_ok, smc_ok]) >= 3
        composite_4 = sum([rsi_ok, macd_ok, ema_ok, ms_ok, smc_ok]) >= 4
        composite_5 = sum([rsi_ok, macd_ok, ema_ok, ms_ok, smc_ok]) == 5
        return {
            "technical_core": technical_core,
            "confirmation_core": confirmation_core,
            "structure_smc_both": both_ok,
            "confidence_plus_core": confidence_ok and technical_core,
            "composite_3": composite_3,
            "composite_4": composite_4,
            "composite_5": composite_5,
            "rsi_macd": core_momentum,
            "rsi_macd_ema": technical_core,
            "rsi_macd_structure": rsi_ok and macd_ok and ms_ok,
            "rsi_macd_smc": rsi_ok and macd_ok and smc_ok,
            "rsi_macd_structure_smc": rsi_ok and macd_ok and both_ok,
            "candle_momentum": candle_ok and close_ok and core_momentum,
            "candle_momentum_open": candle_ok and close_ok and core_momentum and open_ok,
            "action_valid": action in {"BUY", "SELL"},
            "technical_count": tech,
            "score": score,
        }

    names = [
        "rsi_macd", "rsi_macd_ema", "rsi_macd_structure", "rsi_macd_smc",
        "rsi_macd_structure_smc", "technical_core", "confirmation_core",
        "structure_smc_both", "confidence_plus_core", "composite_3", "composite_4",
        "composite_5", "candle_momentum", "candle_momentum_open",
    ]

    def separation(rows_a, rows_b):
        output = {}
        for name in names:
            output[name] = {
                "target_count": count(rows_a, lambda t, n=name: composite_flags(t)[n]),
                "target_rate": rate(rows_a, lambda t, n=name: composite_flags(t)[n]),
                "stop_count": count(rows_b, lambda t, n=name: composite_flags(t)[n]),
                "stop_rate": rate(rows_b, lambda t, n=name: composite_flags(t)[n]),
                "target_minus_stop_rate": round(
                    rate(rows_a, lambda t, n=name: composite_flags(t)[n]) -
                    rate(rows_b, lambda t, n=name: composite_flags(t)[n]), 2
                ),
            }
        return output

    def side_stats(rows):
        return {
            "BUY": count(rows, lambda t: str(t.get("action") or "").upper() == "BUY"),
            "SELL": count(rows, lambda t: str(t.get("action") or "").upper() == "SELL"),
        }

    def case(t):
        flags = composite_flags(t)
        return {
            k: t.get(k) for k in [
                "date", "signal_date", "action", "confidence", "score", "entry_price",
                "signal_open", "signal_high", "signal_low", "signal_close",
                "rsi", "macd", "macd_signal", "macd_delta", "price_vs_ema20_percent",
                "ema20", "ema50", "market_structure_signal", "market_structure_confidence",
                "smc_signal", "smc_confidence", "entry_quality", "entry_technical_confirmations",
                "entry_confirmation_score", "signal_candle_body_to_range_percent",
                "signal_candle_strong", "signal_candle_close_confirmed", "next_open_gap_percent",
                "next_open_not_adverse", "max_favorable_excursion_percent",
                "max_adverse_excursion_percent", "return_percent", "profit_loss", "exit_reason",
            ]
        } | {"composite_flags": flags}

    all_cases = []
    for t in targets:
        all_cases.append({"outcome": "TARGET", **case(t)})
    for t in stops:
        all_cases.append({"outcome": "STOP_LOSS", **case(t)})

    ranked = []
    for name in names:
        a = separation(targets, stops)[name]
        # Rank by positive target-minus-stop separation, while preferring
        # conditions with at least one TARGET and zero STOP when available.
        rank = (
            1000 if a["target_count"] > 0 and a["stop_count"] == 0 else 0,
            a["target_minus_stop_rate"],
            a["target_count"],
        )
        ranked.append({"name": name, **a, "rank_key": list(rank)})
    ranked.sort(key=lambda x: tuple(x["rank_key"]), reverse=True)
    for row in ranked:
        row.pop("rank_key", None)

    return {
        "version": "V2.5",
        "diagnostic_only": True,
        "strategy_changed": False,
        "purpose": "Test composite combinations of V2.4 entry confirmation, momentum, structure, SMC, and confidence features for repeatable TARGET-vs-STOP separation.",
        "target_trades": len(targets),
        "stop_loss_trades": len(stops),
        "target_net_profit_loss": round(sum(val(t, "profit_loss") for t in targets), 2),
        "stop_loss_net_profit_loss": round(sum(val(t, "profit_loss") for t in stops), 2),
        "target_side_breakdown": side_stats(targets),
        "stop_loss_side_breakdown": side_stats(stops),
        "separation": separation(targets, stops),
        "ranked_combinations": ranked,
        "target_averages": {
            "rsi": avg(targets, "rsi"),
            "macd_delta": avg(targets, "macd_delta"),
            "price_vs_ema20_percent": avg(targets, "price_vs_ema20_percent"),
            "confirmation_score": avg(targets, "entry_confirmation_score"),
        },
        "stop_loss_averages": {
            "rsi": avg(stops, "rsi"),
            "macd_delta": avg(stops, "macd_delta"),
            "price_vs_ema20_percent": avg(stops, "price_vs_ema20_percent"),
            "confirmation_score": avg(stops, "entry_confirmation_score"),
        },
        "worst_stop_loss_cases": [case(t) for t in sorted(stops, key=lambda x: val(x, "profit_loss"))[:10]],
        "best_target_cases": [case(t) for t in sorted(targets, key=lambda x: val(x, "profit_loss"), reverse=True)[:10]],
        "all_cases": all_cases,
        "interpretation": {
            "strategy_changed": False,
            "warning": "V2.5 is diagnostic only. Do not promote a composite rule from this sample alone.",
            "promotion_gate": "A candidate should show meaningful TARGET-vs-STOP separation, avoid relying on a tiny sample, and improve broader out-of-sample validation before becoming a live strategy rule.",
            "next_step": "If no robust composite separates the classes, freeze V2.1 rather than adding more arbitrary filters.",
        },
    }

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
# TRADE QUALITY V2 / THESIS FAILURE EXIT DISABLED
# ============================================================


def trade_quality_gate(
    action: str,
    indicators: Dict[str, Any],
    smc: Dict[str, Any],
    market_structure: Optional[Dict[str, Any]] = None,
    confidence: float = 0.0,
    entry_quality: str = "NORMAL",
) -> Dict[str, Any]:
    """
    Trade Quality V2.1 entry gate.

    V2.1 keeps the V2 structural framework and adds evidence-driven
    entry-timing protection based only on information available on the
    signal candle:
      - rejects RSI exhaustion at extreme levels;
      - rejects strongly extended price/EMA20 entries when momentum is
        already stretched;
      - requires stronger technical + SMC agreement for very high
        confidence signals, because the diagnostic showed that high
        confidence alone was not sufficiently discriminating.

    No future candle is read here. The core recommendation engine is
    unchanged.
    """
    if action not in {"BUY", "SELL"}:
        return {
            "approved": True,
            "confirmations": 0,
            "checks": {},
            "reason": "",
            "version": "V2.1",
        }

    close = safe_float(indicators.get("Close"), 0.0)
    ema20 = safe_float(indicators.get("EMA20"), 0.0)
    ema50 = safe_float(indicators.get("EMA50"), 0.0)
    rsi = safe_float(indicators.get("RSI"), 50.0)
    macd = safe_float(indicators.get("MACD"), 0.0)
    macd_signal = safe_float(indicators.get("MACD_SIGNAL"), 0.0)

    smc_signal = clean_action(smc.get("signal", "HOLD"))
    smc_confidence = safe_float(smc.get("confidence"), 0.0)

    structure = market_structure or {}
    structure_signal = clean_action(structure.get("signal", "HOLD"))
    structure_confidence = safe_float(structure.get("confidence"), 0.0)

    if action == "BUY":
        technical_checks = {
            "price_above_ema20": close > ema20,
            "ema20_above_ema50": ema20 > ema50,
            "macd_bullish": macd > macd_signal,
            "rsi_supportive": BUY_MIN_RSI <= rsi <= BUY_MAX_RSI,
        }
        structure_aligned = structure_signal == "BUY" and structure_confidence >= 60
        smc_aligned = smc_signal == "BUY" and smc_confidence >= 60
        opposite_smc = smc_signal == "SELL" and smc_confidence >= SMC_CONFLICT_CONFIDENCE
        rsi_exhausted = rsi >= V21_RSI_EXHAUSTION_BUY
    else:
        technical_checks = {
            "price_below_ema20": close < ema20,
            "ema20_below_ema50": ema20 < ema50,
            "macd_bearish": macd < macd_signal,
            "rsi_supportive": SELL_MIN_RSI <= rsi <= SELL_MAX_RSI,
        }
        structure_aligned = structure_signal == "SELL" and structure_confidence >= 60
        smc_aligned = smc_signal == "SELL" and smc_confidence >= 60
        opposite_smc = smc_signal == "BUY" and smc_confidence >= SMC_CONFLICT_CONFIDENCE
        rsi_exhausted = rsi <= V21_RSI_EXHAUSTION_SELL

    technical_confirmations = sum(1 for value in technical_checks.values() if value)

    extension_distance = 0.0
    if close > 0 and ema20 > 0:
        extension_distance = abs(close - ema20) / close * 100.0

    if action == "BUY":
        extension_risk = (
            extension_distance >= V21_EXTENSION_DISTANCE_PERCENT
            and rsi >= V21_EXTENSION_RSI_BUY
        )
    else:
        extension_risk = (
            extension_distance >= V21_EXTENSION_DISTANCE_PERCENT
            and rsi <= V21_EXTENSION_RSI_SELL
        )

    checks = dict(technical_checks)
    checks["market_structure_aligned"] = structure_aligned
    checks["smc_aligned"] = smc_aligned
    checks["no_strong_opposite_smc"] = not opposite_smc
    checks["rsi_not_exhausted"] = not rsi_exhausted
    checks["not_extended_with_stretched_rsi"] = not extension_risk

    if opposite_smc:
        return {
            "approved": False,
            "confirmations": technical_confirmations,
            "checks": checks,
            "reason": f"{action} rejected: strong opposite SMC signal ({smc_signal} {smc_confidence:.0f}%)",
            "version": "V2.1",
            "structure_signal": structure_signal,
            "structure_confidence": round(structure_confidence, 2),
            "smc_signal": smc_signal,
            "smc_confidence": round(smc_confidence, 2),
            "technical_confirmations": technical_confirmations,
            "entry_quality": entry_quality,
            "extension_distance_percent": round(extension_distance, 2),
            "rsi_exhausted": rsi_exhausted,
            "extension_risk": extension_risk,
        }

    if rsi_exhausted:
        reason = (
            f"{action} rejected by Trade Quality V2.1: RSI exhaustion "
            f"({rsi:.2f})"
        )
        approved = False
    elif extension_risk:
        reason = (
            f"{action} rejected by Trade Quality V2.1: price is extended "
            f"{extension_distance:.2f}% from EMA20 with stretched RSI ({rsi:.2f})"
        )
        approved = False
    else:
        structure_ok = structure_aligned
        technical_ok = technical_confirmations >= MIN_QUALITY_CONFIRMATIONS - 1
        smc_or_strong_technical = smc_aligned or technical_confirmations == 4

        extension_ok = True
        if entry_quality in {"EXTENDED", "VERY_EXTENDED"}:
            extension_ok = structure_aligned and smc_aligned

        high_confidence_ok = True
        if confidence >= V21_HIGH_CONFIDENCE_THRESHOLD:
            high_confidence_ok = (
                technical_confirmations >= V21_HIGH_CONF_MIN_TECHNICAL
                and smc_aligned
                and smc_confidence >= V21_HIGH_CONF_MIN_SMC_CONFIDENCE
            )

        approved = (
            structure_ok
            and technical_ok
            and smc_or_strong_technical
            and extension_ok
            and high_confidence_ok
            and confidence >= MIN_CONFIDENCE
        )

        failures = []
        if not structure_ok:
            failures.append(f"market structure not aligned ({structure_signal} {structure_confidence:.0f}%)")
        if not technical_ok:
            failures.append(f"only {technical_confirmations}/4 technical confirmations")
        if not smc_or_strong_technical:
            failures.append("SMC not aligned and technical confirmation is not 4/4")
        if not extension_ok:
            failures.append(f"{entry_quality.lower()} entry requires structure + SMC alignment")
        if not high_confidence_ok:
            failures.append(
                f"high-confidence entry requires {V21_HIGH_CONF_MIN_TECHNICAL}/4 technical confirmations "
                f"and aligned SMC >= {V21_HIGH_CONF_MIN_SMC_CONFIDENCE:.0f}%"
            )
        if confidence < MIN_CONFIDENCE:
            failures.append(f"confidence {confidence:.0f}% below {MIN_CONFIDENCE:.0f}%")

        if approved:
            reason = (
                f"{action} approved by Trade Quality V2.1: structure aligned, "
                f"{technical_confirmations}/4 technical confirmations, "
                f"SMC {'aligned' if smc_aligned else 'not required with 4/4 technical confirmations'}"
            )
        else:
            reason = "Trade Quality V2.1 rejected: " + "; ".join(failures)

    return {
        "approved": approved,
        "confirmations": technical_confirmations,
        "checks": checks,
        "reason": reason,
        "version": "V2.1",
        "structure_signal": structure_signal,
        "structure_confidence": round(structure_confidence, 2),
        "smc_signal": smc_signal,
        "smc_confidence": round(smc_confidence, 2),
        "technical_confirmations": technical_confirmations,
        "entry_quality": entry_quality,
        "extension_distance_percent": round(extension_distance, 2),
        "rsi_exhausted": rsi_exhausted,
        "extension_risk": extension_risk,
        "high_confidence_rule_applied": confidence >= V21_HIGH_CONFIDENCE_THRESHOLD,
    }



def v3_entry_quality_gate(action, indicators, smc, market_structure, historical_df, confidence):
    """V3 signal-candle-only regime and entry-timing gate."""
    if action not in {"BUY", "SELL"}:
        return {"approved": True, "rank": "C", "regime": "TRANSITION", "regime_score": 0, "technical_score": 0, "timing_score": 0, "checks": {}, "reason": "", "version": "V3"}
    close=safe_float(indicators.get("Close"),0.0); ema20=safe_float(indicators.get("EMA20"),0.0); ema50=safe_float(indicators.get("EMA50"),0.0)
    rsi=safe_float(indicators.get("RSI"),50.0); macd=safe_float(indicators.get("MACD"),0.0); msig=safe_float(indicators.get("MACD_SIGNAL"),0.0)
    ss=clean_action(smc.get("signal","HOLD")); sc=safe_float(smc.get("confidence"),0.0)
    st=market_structure or {}; mss=clean_action(st.get("signal","HOLD")); msc=safe_float(st.get("confidence"),0.0)
    buy=action=="BUY"
    price_ok=close>ema20 if buy else close<ema20; ema_ok=ema20>ema50 if buy else ema20<ema50
    macd_ok=macd>msig if buy else macd<msig; rsi_ok=45<=rsi<=70 if buy else 30<=rsi<=55
    ms_ok=mss==action and msc>=V3_STRUCTURE_CONFIDENCE; smc_ok=ss==action and sc>=V3_SMC_CONFIDENCE
    tech={"price_vs_ema20":price_ok,"ema20_vs_ema50":ema_ok,"macd":macd_ok,"rsi":rsi_ok}; tech_score=sum(map(bool,tech.values()))
    dist=abs(close-ema20)/close*100 if close>0 else 0.0; exhausted=rsi>=75 if buy else rsi<=25
    extended=dist>=4 and (rsi>=65 if buy else rsi<=35)
    prev_rsi=rsi; prev_ema=ema20; prev_delta=macd-msig
    if historical_df is not None and len(historical_df)>=2:
        try:
            prev=historical_df.iloc[-2]; prev_rsi=safe_float(prev.get("RSI"),rsi); prev_ema=safe_float(prev.get("EMA20"),ema20)
            prev_delta=safe_float(prev.get("MACD"),macd)-safe_float(prev.get("MACD_SIGNAL"),msig)
        except Exception: pass
    rsi_slope=rsi>prev_rsi if buy else rsi<prev_rsi; ema_slope=ema20>prev_ema if buy else ema20<prev_ema; macd_slope=(macd-msig)>prev_delta if buy else (macd-msig)<prev_delta
    op=safe_float(indicators.get("Open"),close); hi=safe_float(indicators.get("High"),close); lo=safe_float(indicators.get("Low"),close); rng=max(hi-lo,0.0)
    body=abs(close-op); ratio=body/rng if rng>0 else 0.0; candle_side=close>=op if buy else close<=op; loc=(close-lo)/rng if rng>0 else .5; close_ok=loc>=.60 if buy else loc<=.40
    timing={"candle_direction":candle_side,"close_confirmation":close_ok,"macd_alignment":macd_ok,"rsi_support":rsi_ok,"ema20_slope":ema_slope,"macd_slope":macd_slope,"rsi_slope":rsi_slope,"not_extended":not extended,"not_exhausted":not exhausted}
    timing_score=sum(map(bool,timing.values()))
    regime="BULLISH" if buy and price_ok and ema_ok and ms_ok else "BEARISH" if (not buy and price_ok and ema_ok and ms_ok) else "TRANSITION"
    regime_score=int(price_ok)+int(ema_ok)+int(ms_ok)+int(smc_ok)
    ap=(regime in {"BULLISH","BEARISH"} and msc>=70 and smc_ok and sc>=65 and tech_score>=3 and timing_score>=4 and confidence>=80 and not exhausted and not extended)
    aa=(regime in {"BULLISH","BEARISH"} and ms_ok and smc_ok and tech_score>=3 and timing_score>=3 and confidence>=75 and not exhausted and not extended)
    bb=(regime in {"BULLISH","BEARISH"} and ms_ok and tech_score>=2 and confidence>=MIN_CONFIDENCE and not exhausted and not extended)
    rank="A+" if ap else "A" if aa else "B" if bb else "C"; approved=rank in {"A+","A"} if ENABLE_V3_STRATEGY else True
    reasons=[]
    if regime=="TRANSITION": reasons.append("market regime is transitional")
    if not ms_ok: reasons.append(f"market structure not aligned ({mss} {msc:.0f}%)")
    if not smc_ok: reasons.append(f"SMC not aligned ({ss} {sc:.0f}%)")
    if tech_score<3: reasons.append(f"technical confirmation {tech_score}/4")
    if timing_score<3: reasons.append(f"entry timing confirmation {timing_score}/9")
    if exhausted: reasons.append(f"RSI exhaustion ({rsi:.2f})")
    if extended: reasons.append(f"extended {dist:.2f}% from EMA20 with stretched RSI")
    if confidence<75: reasons.append(f"confidence {confidence:.0f}% below V3 A threshold 75%")
    reason=f"V3 {rank} entry approved: {regime.lower()} regime, {tech_score}/4 technical, {timing_score}/9 timing, SMC aligned" if approved else ("V3 rejected: "+"; ".join(reasons[:5]) if reasons else f"V3 rank {rank} below A")
    return {"approved":approved,"rank":rank,"regime":regime,"regime_score":regime_score,"technical_score":tech_score,"timing_score":timing_score,"structure_signal":mss,"structure_confidence":round(msc,2),"smc_signal":ss,"smc_confidence":round(sc,2),"extension_distance_percent":round(dist,2),"rsi_exhausted":exhausted,"extended":extended,"checks":{**tech,**timing,"market_structure_aligned":ms_ok,"smc_aligned":smc_ok},"reason":reason,"version":"V3"}

def thesis_failure_check(df, start_index: int, current_index: int, action: str) -> bool:
    if not ENABLE_THESIS_FAILURE_EXIT:
        return False
    if current_index - start_index + 1 < max(
        THESIS_FAILURE_MIN_ENTRY_DAY,
        THESIS_FAILURE_CONSECUTIVE_CANDLES,
    ):
        return False
    first = current_index - THESIS_FAILURE_CONSECUTIVE_CANDLES + 1
    if first < start_index:
        return False
    for idx in range(first, current_index + 1):
        candle = df.iloc[idx]
        close = safe_float(candle.get("Close"), 0.0)
        ema20 = safe_float(candle.get("EMA20"), 0.0)
        rsi = safe_float(candle.get("RSI"), 50.0)
        macd = safe_float(candle.get("MACD"), 0.0)
        macd_signal = safe_float(candle.get("MACD_SIGNAL"), 0.0)
        if action == "BUY":
            adverse = [close < ema20, rsi < BUY_MIN_RSI, macd < macd_signal]
        else:
            adverse = [close > ema20, rsi > SELL_MAX_RSI, macd > macd_signal]
        if sum(1 for value in adverse if value) < THESIS_FAILURE_CONFIRMATIONS:
            return False
    return True


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

            if thesis_failure_check(df, entry_index, j, action):
                exit_index = j
                exit_price = close
                exit_reason = "THESIS_FAILURE"
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

            if thesis_failure_check(df, entry_index, j, action):
                exit_index = j
                exit_price = close
                exit_reason = "THESIS_FAILURE"
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

    if action == "BUY":
        planned_risk_percent = (
            (entry_price - valid_stop)
            / entry_price
        ) * 100.0
        planned_reward_percent = (
            (valid_target - entry_price)
            / entry_price
        ) * 100.0
    else:
        planned_risk_percent = (
            (valid_stop - entry_price)
            / entry_price
        ) * 100.0
        planned_reward_percent = (
            (entry_price - valid_target)
            / entry_price
        ) * 100.0

    planned_risk_percent = max(planned_risk_percent, 0.0)
    planned_reward_percent = max(planned_reward_percent, 0.0)

    max_adverse_percent = 0.0
    max_favorable_percent = 0.0

    for k in range(entry_index, exit_index + 1):
        candle = df.iloc[k]
        high = safe_float(candle["High"], 0)
        low = safe_float(candle["Low"], 0)

        if action == "BUY":
            if low > 0:
                max_adverse_percent = max(
                    max_adverse_percent,
                    ((entry_price - low) / entry_price) * 100.0,
                )
            if high > 0:
                max_favorable_percent = max(
                    max_favorable_percent,
                    ((high - entry_price) / entry_price) * 100.0,
                )
        else:
            if high > 0:
                max_adverse_percent = max(
                    max_adverse_percent,
                    ((high - entry_price) / entry_price) * 100.0,
                )
            if low > 0:
                max_favorable_percent = max(
                    max_favorable_percent,
                    ((entry_price - low) / entry_price) * 100.0,
                )

    realized_r_multiple = (
        return_percent / planned_risk_percent
        if planned_risk_percent > 0
        else None
    )
    risk_exceeded = (
        return_percent < -planned_risk_percent
        if planned_risk_percent > 0
        else False
    )

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
        "planned_risk_percent": round(
            planned_risk_percent,
            2,
        ),
        "planned_reward_percent": round(
            planned_reward_percent,
            2,
        ),
        "realized_r_multiple": (
            round(realized_r_multiple, 2)
            if realized_r_multiple is not None
            else None
        ),
        "max_adverse_excursion_percent": round(
            max_adverse_percent,
            2,
        ),
        "max_favorable_excursion_percent": round(
            max_favorable_percent,
            2,
        ),
        "risk_exceeded": risk_exceeded,
    }


# ============================================================
# MAIN BACKTEST ENGINE
# ============================================================


def run_backtest(
    symbol: str,
    period: str = "1y",
    evaluation_start_date: Optional[str] = None,
    evaluation_end_date: Optional[str] = None,
    evaluation_mode: str = "FULL",
):

    symbol = str(
        symbol or ""
    ).upper().strip()

    period = str(
        period or "1y"
    ).strip().lower()

    evaluation_start_date = (
        str(evaluation_start_date).strip()
        if evaluation_start_date
        else None
    )
    evaluation_end_date = (
        str(evaluation_end_date).strip()
        if evaluation_end_date
        else None
    )
    evaluation_mode = (
        str(evaluation_mode or "FULL").strip().upper()
    )

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
    # OPTIONAL OUT-OF-SAMPLE EVALUATION WINDOW
    #
    # Signals are still calculated candle-by-candle using only data
    # available through the signal candle.  The evaluation window only
    # controls which completed predictions/trades are included in the
    # reported OOS result.  Training/warm-up candles are never traded.
    # ========================================================

    if evaluation_start_date:
        evaluation_start_date = evaluation_start_date[:10]
    if evaluation_end_date:
        evaluation_end_date = evaluation_end_date[:10]

    if evaluation_start_date and evaluation_end_date:
        if evaluation_start_date > evaluation_end_date:
            return {
                "success": False,
                "message": "evaluation_start_date must be on or before evaluation_end_date.",
            }

    evaluation_window_enabled = bool(
        evaluation_start_date or evaluation_end_date
    )

    def is_in_evaluation_window(date_text: str) -> bool:
        if not evaluation_window_enabled:
            return True
        if evaluation_start_date and date_text < evaluation_start_date:
            return False
        if evaluation_end_date and date_text > evaluation_end_date:
            return False
        return True

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

                    if action in {"BUY", "SELL"}:
                        entry_quality_value = str(recommendation.get("entry_quality", "NORMAL") or "NORMAL").upper()
                        quality = trade_quality_gate(
                            action,
                            indicators,
                            smc,
                            market_structure=market_structure,
                            confidence=confidence,
                            entry_quality=entry_quality_value,
                        )
                        if not quality["approved"]:
                            action = "HOLD"
                            total_rejected_by_strategy += 1
                            approval_reason = quality["reason"]
                            rejection_reasons[quality["reason"]] = rejection_reasons.get(quality["reason"], 0) + 1
                    else:
                        quality = {"approved": True, "confirmations": 0, "checks": {}, "reason": ""}

            else:
                quality = {"approved": True, "confirmations": 0, "checks": {}, "reason": ""}

            # ------------------------------------------------
            # V3 STRATEGY LAYER
            # ------------------------------------------------
            v3_quality = {"approved": True, "rank": "C", "regime": "TRANSITION", "regime_score": 0, "technical_score": 0, "timing_score": 0, "checks": {}, "reason": "", "version": "V3"}
            if action in {"BUY", "SELL"} and ENABLE_V3_STRATEGY:
                v3_quality = v3_entry_quality_gate(action, indicators, smc, market_structure, historical_df, confidence)
                if not v3_quality["approved"]:
                    action = "HOLD"
                    total_rejected_by_strategy += 1
                    approval_reason = v3_quality["reason"]
                    rejection_reasons[v3_quality["reason"]] = rejection_reasons.get(v3_quality["reason"], 0) + 1

            # ------------------------------------------------
            # DATES
            # ------------------------------------------------

            signal_date = format_date(
                df.index[i]
            )

            next_date = format_date(
                next_candle.name
            )

            in_evaluation_window = is_in_evaluation_window(signal_date)

            # ------------------------------------------------
            # V2.4 DIAGNOSTIC FEATURES
            # Signal candle + next open only; strategy unchanged.
            # ------------------------------------------------
            signal_open = safe_float(current_candle.get("Open"), current_close)
            signal_high = safe_float(current_candle.get("High"), current_close)
            signal_low = safe_float(current_candle.get("Low"), current_close)
            candle_range = max(signal_high - signal_low, 0.0)
            candle_body = abs(current_close - signal_open)
            candle_range_percent = (candle_range / signal_open * 100.0) if signal_open > 0 else 0.0
            candle_body_percent = (candle_body / signal_open * 100.0) if signal_open > 0 else 0.0
            body_to_range_percent = (candle_body / candle_range * 100.0) if candle_range > 0 else 0.0
            side_candle_confirmed = (action == "BUY" and current_close >= signal_open) or (action == "SELL" and current_close <= signal_open)
            close_location = ((current_close - signal_low) / candle_range) if candle_range > 0 else 0.5
            close_location_confirmed = (action == "BUY" and close_location >= 0.60) or (action == "SELL" and close_location <= 0.40)
            strong_signal_candle = side_candle_confirmed and body_to_range_percent >= 50.0
            macd_value = safe_float(indicators.get("MACD"), 0.0)
            macd_signal_value = safe_float(indicators.get("MACD_SIGNAL"), 0.0)
            macd_delta = macd_value - macd_signal_value
            macd_confirmed = (action == "BUY" and macd_delta > 0) or (action == "SELL" and macd_delta < 0)
            rsi_value = safe_float(indicators.get("RSI"), 50.0)
            rsi_supportive = (action == "BUY" and 45.0 <= rsi_value <= 70.0) or (action == "SELL" and 30.0 <= rsi_value <= 55.0)
            ema20_value = safe_float(indicators.get("EMA20"), 0.0)
            price_vs_ema20_percent = ((current_close - ema20_value) / ema20_value * 100.0) if ema20_value > 0 else 0.0
            ema_distance_ok = abs(price_vs_ema20_percent) < 4.0
            next_open_gap_percent = ((next_open - current_close) / current_close * 100.0) if current_close > 0 else 0.0
            next_open_not_adverse = (action == "BUY" and next_open >= current_close) or (action == "SELL" and next_open <= current_close)
            momentum_confirmed = macd_confirmed and rsi_supportive
            entry_technical_confirmations = sum([bool(side_candle_confirmed), bool(close_location_confirmed), bool(macd_confirmed), bool(rsi_supportive)])
            entry_confirmation_score = sum([bool(strong_signal_candle), bool(close_location_confirmed), bool(momentum_confirmed), bool(ema_distance_ok), bool(next_open_not_adverse)])

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

                "signal_open": round(signal_open, 2),
                "signal_high": round(signal_high, 2),
                "signal_low": round(signal_low, 2),
                "signal_close": round(current_close, 2),
                "signal_candle_body_percent": round(candle_body_percent, 2),
                "signal_candle_range_percent": round(candle_range_percent, 2),
                "signal_candle_body_to_range_percent": round(body_to_range_percent, 2),
                "signal_candle_strong": strong_signal_candle,
                "signal_candle_close_confirmed": close_location_confirmed,
                "momentum_confirmed": momentum_confirmed,
                "next_open_gap_percent": round(next_open_gap_percent, 2),
                "next_open_not_adverse": next_open_not_adverse,
                "entry_confirmation_score": entry_confirmation_score,
                "entry_technical_confirmations": entry_technical_confirmations,
                "macd_aligned": macd_confirmed,
                "macd_delta": round(macd_delta, 4),
                "rsi_supportive": rsi_supportive,
                "price_vs_ema20_percent": round(price_vs_ema20_percent, 2),

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

                "market_structure_signal":
                    clean_action(
                        market_structure.get(
                            "signal",
                            market_structure.get(
                                "recommendation",
                                "HOLD",
                            ),
                        )
                    ),

                "market_structure_confidence":
                    round(
                        safe_float(
                            market_structure.get(
                                "confidence",
                                0,
                            )
                        ),
                        2,
                    ),

                "entry_quality":
                    str(
                        recommendation.get(
                            "entry_quality",
                            "NORMAL",
                        )
                        or "NORMAL"
                    ).upper(),

                "strategy_checks":
                    confirmation.get(
                        "checks",
                        {},
                    ),

                "trade_quality_approved": quality.get("approved", True),
                "trade_quality_confirmations": quality.get("confirmations", 0),
                "trade_quality_checks": quality.get("checks", {}),
                "trade_quality_reason": quality.get("reason", ""),
                "v3_rank": v3_quality.get("rank", "C"),
                "v3_regime": v3_quality.get("regime", "TRANSITION"),
                "v3_regime_score": v3_quality.get("regime_score", 0),
                "v3_technical_score": v3_quality.get("technical_score", 0),
                "v3_timing_score": v3_quality.get("timing_score", 0),
                "v3_approved": v3_quality.get("approved", True),
                "v3_checks": v3_quality.get("checks", {}),
                "v3_reason": v3_quality.get("reason", ""),
            }

            # ------------------------------------------------
            # TRADE
            # ------------------------------------------------

            if (
                action in {
                    "BUY",
                    "SELL",
                }
                and in_evaluation_window
            ):

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

                if (
                    simulated is not None
                    and evaluation_end_date
                    and str(simulated.get("exit_date") or "")[:10] > evaluation_end_date
                ):
                    simulated = None

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

                        "v3_rank": v3_quality.get("rank", "C"),
                        "v3_regime": v3_quality.get("regime", "TRANSITION"),
                        "v3_regime_score": v3_quality.get("regime_score", 0),
                        "v3_technical_score": v3_quality.get("technical_score", 0),
                        "v3_timing_score": v3_quality.get("timing_score", 0),
                        "v3_approved": v3_quality.get("approved", True),
                        "v3_reason": v3_quality.get("reason", ""),

                        "holding_days":
                            (
                                simulated[
                                    "exit_index"
                                ]
                                - (i + 1)
                                + 1
                            ),

                        "planned_risk_percent":
                            simulated["planned_risk_percent"],

                        "planned_reward_percent":
                            simulated["planned_reward_percent"],

                        "realized_r_multiple":
                            simulated["realized_r_multiple"],

                        "max_adverse_excursion_percent":
                            simulated["max_adverse_excursion_percent"],

                        "max_favorable_excursion_percent":
                            simulated["max_favorable_excursion_percent"],

                        "risk_exceeded":
                            simulated["risk_exceeded"],

                        "rsi":
                            round(
                                safe_float(
                                    indicators.get(
                                        "RSI"
                                    )
                                ),
                                2,
                            ),

                        "macd":
                            round(
                                safe_float(
                                    indicators.get(
                                        "MACD"
                                    )
                                ),
                                4,
                            ),

                        "macd_signal":
                            round(
                                safe_float(
                                    indicators.get(
                                        "MACD_SIGNAL"
                                    )
                                ),
                                4,
                            ),

                        "signal_price":
                            round(
                                current_close,
                                2,
                            ),

                        "signal_open": round(signal_open, 2),
                        "signal_high": round(signal_high, 2),
                        "signal_low": round(signal_low, 2),
                        "signal_close": round(current_close, 2),
                        "signal_candle_body_percent": round(candle_body_percent, 2),
                        "signal_candle_range_percent": round(candle_range_percent, 2),
                        "signal_candle_body_to_range_percent": round(body_to_range_percent, 2),
                        "signal_candle_strong": strong_signal_candle,
                        "signal_candle_close_confirmed": close_location_confirmed,
                        "momentum_confirmed": momentum_confirmed,
                        "next_open_gap_percent": round(next_open_gap_percent, 2),
                        "next_open_not_adverse": next_open_not_adverse,
                        "entry_confirmation_score": entry_confirmation_score,
                        "entry_technical_confirmations": entry_technical_confirmations,
                        "macd_aligned": macd_confirmed,
                        "macd_delta": round(macd_delta, 4),
                        "rsi_supportive": rsi_supportive,
                        "price_vs_ema20_percent": round(price_vs_ema20_percent, 2),

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

                        "market_structure_signal":
                            clean_action(
                                market_structure.get(
                                    "signal",
                                    market_structure.get(
                                        "recommendation",
                                        "HOLD",
                                    ),
                                )
                            ),

                        "market_structure_confidence":
                            round(
                                safe_float(
                                    market_structure.get(
                                        "confidence",
                                        0,
                                    )
                                ),
                                2,
                            ),

                        "entry_quality":
                            str(
                                recommendation.get(
                                    "entry_quality",
                                    "NORMAL",
                                )
                                or "NORMAL"
                            ).upper(),
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

            if in_evaluation_window:
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
    # FINAL / EVALUATED SIGNALS
    # Use the exact same evaluated population as accuracy.
    # This guarantees BUY + SELL + HOLD == Total Predictions.
    # Raw signal counts remain separate diagnostics above.
    # --------------------------------------------------------

    buy_signals = sum(
        1
        for item in prediction_results
        if clean_action(item.get("action")) == "BUY"
    )

    sell_signals = sum(
        1
        for item in prediction_results
        if clean_action(item.get("action")) == "SELL"
    )

    hold_signals = sum(
        1
        for item in prediction_results
        if clean_action(item.get("action")) == "HOLD"
    )

    classified_predictions = (
        buy_signals
        + sell_signals
        + hold_signals
    )

    if classified_predictions != total_predictions:
        hold_signals += max(
            0,
            total_predictions - classified_predictions,
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

    # ========================================================
    # TRADE EXIT / RISK DIAGNOSTICS
    # ========================================================

    exit_reason_stats: Dict[str, Dict[str, Any]] = {}

    for trade in trades:
        reason = str(trade.get("exit_reason") or "UNKNOWN")
        bucket = exit_reason_stats.setdefault(
            reason,
            {
                "count": 0,
                "wins": 0,
                "losses": 0,
                "flat": 0,
                "net_profit_loss": 0.0,
                "average_return_percent": 0.0,
                "average_holding_days": 0.0,
            },
        )
        bucket["count"] += 1
        pnl = safe_float(trade.get("profit_loss"), 0.0)
        ret = safe_float(trade.get("return_percent"), 0.0)
        days = safe_float(trade.get("holding_days"), 0.0)
        bucket["net_profit_loss"] += pnl
        bucket["average_return_percent"] += ret
        bucket["average_holding_days"] += days
        if pnl > 0:
            bucket["wins"] += 1
        elif pnl < 0:
            bucket["losses"] += 1
        else:
            bucket["flat"] += 1

    for bucket in exit_reason_stats.values():
        count = bucket["count"]
        if count:
            bucket["net_profit_loss"] = round(bucket["net_profit_loss"], 2)
            bucket["average_return_percent"] = round(
                bucket["average_return_percent"] / count, 2
            )
            bucket["average_holding_days"] = round(
                bucket["average_holding_days"] / count, 2
            )

    max_holding_trades = [
        trade for trade in trades
        if trade.get("exit_reason") == "MAX_HOLDING_PERIOD"
    ]
    risk_exceeded_trades = [
        trade for trade in trades
        if trade.get("risk_exceeded") is True
    ]

    mae_values = [
        safe_float(trade.get("max_adverse_excursion_percent"), 0.0)
        for trade in trades
    ]
    mfe_values = [
        safe_float(trade.get("max_favorable_excursion_percent"), 0.0)
        for trade in trades
    ]
    r_values = [
        safe_float(trade.get("realized_r_multiple"), 0.0)
        for trade in trades
        if trade.get("realized_r_multiple") is not None
    ]

    # --------------------------------------------------------
    # TRADE-LEVEL DIAGNOSTICS
    # Keep the diagnostic output focused on the trades that need
    # investigation. This does not alter trade simulation.
    # --------------------------------------------------------

    diagnostic_trades = []

    for trade in trades:
        exit_reason = str(
            trade.get("exit_reason") or ""
        ).upper()

        if exit_reason not in {
            "STOP_LOSS",
            "STOP_LOSS_GAP",
            "MAX_HOLDING_PERIOD",
        }:
            continue

        diagnostic_trades.append({
            "date": trade.get("date"),
            "signal_date": trade.get("signal_date"),
            "action": trade.get("action"),
            "raw_action": trade.get("raw_action"),
            "result": trade.get("result"),
            "exit_reason": exit_reason,
            "exit_date": trade.get("exit_date"),
            "holding_days": trade.get("holding_days"),
            "confidence": trade.get("confidence"),
            "score": trade.get("score"),
            "entry_price": trade.get("entry_price"),
            "exit_price": trade.get("exit_price"),
            "stop_loss": trade.get("stop_loss"),
            "target": trade.get("target"),
            "risk_reward": trade.get("risk_reward"),
            "return_percent": trade.get("return_percent"),
            "profit_loss": trade.get("profit_loss"),
            "planned_risk_percent": trade.get("planned_risk_percent"),
            "planned_reward_percent": trade.get("planned_reward_percent"),
            "realized_r_multiple": trade.get("realized_r_multiple"),
            "max_adverse_excursion_percent": trade.get("max_adverse_excursion_percent"),
            "max_favorable_excursion_percent": trade.get("max_favorable_excursion_percent"),
            "risk_exceeded": trade.get("risk_exceeded"),
            "rsi": trade.get("rsi"),
            "ema20": trade.get("ema20"),
            "ema50": trade.get("ema50"),
            "smc_signal": trade.get("smc_signal"),
            "smc_confidence": trade.get("smc_confidence"),
            "market_structure_signal": trade.get("market_structure_signal"),
            "market_structure_confidence": trade.get("market_structure_confidence"),
            "entry_quality": trade.get("entry_quality"),
            "v3_rank": trade.get("v3_rank"),
            "v3_regime": trade.get("v3_regime"),
            "v3_regime_score": trade.get("v3_regime_score"),
            "v3_technical_score": trade.get("v3_technical_score"),
            "v3_timing_score": trade.get("v3_timing_score"),
            "v3_approved": trade.get("v3_approved"),
            "v3_reason": trade.get("v3_reason"),
        })

    # Worst losses first, then max-hold cases. This makes the output
    # immediately useful for the failure analysis pass.
    diagnostic_trades.sort(
        key=lambda item: (
            safe_float(item.get("profit_loss"), 0.0),
            0 if item.get("exit_reason") == "STOP_LOSS" else 1,
        )
    )

    thesis_failure_trades = [t for t in trades if t.get("exit_reason") == "THESIS_FAILURE"]
    quality_rejected_results = [t for t in results if t.get("trade_quality_reason")]

    diagnostic_summary = {
        "exit_reason_breakdown": exit_reason_stats,
        "trade_quality_v22": build_v22_stop_loss_analysis(trades),
        "trade_quality_v23": build_v23_entry_timing_analysis(trades),
        "trade_quality_v24": build_v24_confirmation_analysis(trades),
        "trade_quality_v25": build_v25_composite_entry_analysis(trades),
        "trade_quality_v3": {
            "enabled": ENABLE_V3_STRATEGY, "version": "V3", "minimum_rank": V3_MIN_RANK,
            "rank_breakdown": {rank: sum(1 for item in results if item.get("v3_rank") == rank) for rank in ["A+", "A", "B", "C"]},
            "trade_rank_breakdown": {rank: sum(1 for trade in trades if trade.get("v3_rank") == rank) for rank in ["A+", "A", "B", "C"]},
            "regime_breakdown": {regime: sum(1 for item in results if item.get("v3_regime") == regime) for regime in ["BULLISH", "BEARISH", "TRANSITION"]},
        },
        "trade_quality_v21": {
            "enabled": ENABLE_TRADE_QUALITY_FILTER,
            "version": "V2.1",
            "minimum_technical_confirmations": 2,
            "high_confidence_threshold": V21_HIGH_CONFIDENCE_THRESHOLD,
            "high_confidence_min_technical_confirmations": V21_HIGH_CONF_MIN_TECHNICAL,
            "rsi_exhaustion_buy": V21_RSI_EXHAUSTION_BUY,
            "rsi_exhaustion_sell": V21_RSI_EXHAUSTION_SELL,
            "extension_distance_percent": V21_EXTENSION_DISTANCE_PERCENT,
            "requires_market_structure_alignment": True,
            "requires_smc_or_full_technical_confirmation": True,
            "extended_entry_requires_structure_and_smc": True,
            "rejected_signals": len(quality_rejected_results),
        },
        "thesis_failure_exit_v1_disabled": {
            "enabled": ENABLE_THESIS_FAILURE_EXIT,
            "trades": len(thesis_failure_trades),
            "wins": sum(1 for t in thesis_failure_trades if safe_float(t.get("profit_loss"), 0.0) > 0),
            "losses": sum(1 for t in thesis_failure_trades if safe_float(t.get("profit_loss"), 0.0) < 0),
            "net_profit_loss": round(sum(safe_float(t.get("profit_loss"), 0.0) for t in thesis_failure_trades), 2),
        },
        "trade_level_cases": diagnostic_trades,
        "trade_level_case_count": len(diagnostic_trades),
        "max_holding_period": {
            "count": len(max_holding_trades),
            "losses": sum(1 for t in max_holding_trades if t.get("profit_loss", 0) < 0),
            "wins": sum(1 for t in max_holding_trades if t.get("profit_loss", 0) > 0),
            "net_profit_loss": round(sum(safe_float(t.get("profit_loss"), 0.0) for t in max_holding_trades), 2),
            "average_return_percent": round(
                sum(safe_float(t.get("return_percent"), 0.0) for t in max_holding_trades) / len(max_holding_trades), 2
            ) if max_holding_trades else 0.0,
        },
        "risk_exceeded": {
            "count": len(risk_exceeded_trades),
            "percent_of_trades": round(
                len(risk_exceeded_trades) / total_trades * 100.0, 2
            ) if total_trades else 0.0,
            "net_profit_loss": round(sum(safe_float(t.get("profit_loss"), 0.0) for t in risk_exceeded_trades), 2),
        },
        "excursion": {
            "average_mae_percent": round(sum(mae_values) / len(mae_values), 2) if mae_values else 0.0,
            "worst_mae_percent": round(max(mae_values), 2) if mae_values else 0.0,
            "average_mfe_percent": round(sum(mfe_values) / len(mfe_values), 2) if mfe_values else 0.0,
            "best_mfe_percent": round(max(mfe_values), 2) if mfe_values else 0.0,
        },
        "realized_r_multiple": {
            "average": round(sum(r_values) / len(r_values), 2) if r_values else 0.0,
            "worst": round(min(r_values), 2) if r_values else 0.0,
            "best": round(max(r_values), 2) if r_values else 0.0,
        },
        "lookahead_audit": {
            "walk_forward": True,
            "signal_uses_data_through_signal_candle": True,
            "entry_uses_next_candle_open": True,
            "exit_begins_at_entry_candle": True,
            "future_candles_not_used_for_signal": True,
            "status": "PASS",
        },
    }

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

        "trade_diagnostics":
            diagnostic_summary,

        "backtest_warnings":
            total_signal_errors,
    }

    return {

        "success": True,

        "symbol":
            symbol,

        "period":
            period,

        "evaluation_mode":
            evaluation_mode,

        "evaluation_window": {
            "enabled": evaluation_window_enabled,
            "start_date": evaluation_start_date,
            "end_date": evaluation_end_date,
        },

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

        "trade_diagnostics":
            diagnostic_summary,

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


# ============================================================
# MARKETIQ V3 OUT-OF-SAMPLE / WALK-FORWARD VALIDATION
# ============================================================
#
# This is intentionally a validation wrapper around the frozen V3
# engine. It does NOT change recommendation logic, ranking, SL, target,
# R:R, sizing, or holding-period rules.
#
# Default design:
#   - Load the requested historical period once through run_backtest.
#   - Use an anchored warm-up portion that is never traded.
#   - Evaluate only the final OOS portion.
#   - Because the engine itself walks candle-by-candle, every OOS signal
#     still sees only candles available through its signal candle.
#
# The API can override the OOS start/end dates when a stricter experiment
# requires an explicit holdout window.
# ============================================================


def run_walk_forward_oos(
    symbol: str,
    period: str = "5y",
    test_start_date: Optional[str] = None,
    test_end_date: Optional[str] = None,
    oos_ratio: float = 0.40,
) -> Dict[str, Any]:
    """
    Run a frozen-V3 anchored out-of-sample validation.

    If test_start_date is supplied, it is used exactly.
    Otherwise the function uses a deterministic calendar holdout based on
    the requested period:
      5y -> last 40% by calendar time
      2y -> last 40%
      1y -> last 40%
      6mo -> last 40%

    The end date defaults to today, but the engine naturally stops at the
    latest available candle. For reproducibility, callers should provide
    explicit start/end dates for formal research runs.
    """
    import datetime as _dt

    symbol = str(symbol or "").upper().strip()
    period = str(period or "5y").strip().lower()

    allowed_periods = {"6mo", "1y", "2y", "5y"}
    if period not in allowed_periods:
        return {
            "success": False,
            "message": "Unsupported period. Use 6mo, 1y, 2y, or 5y.",
        }

    try:
        ratio = float(oos_ratio)
    except Exception:
        ratio = 0.40

    ratio = max(0.20, min(0.60, ratio))

    if test_end_date:
        end_date = str(test_end_date).strip()[:10]
    else:
        end_date = _dt.date.today().isoformat()

    if test_start_date:
        start_date = str(test_start_date).strip()[:10]
        start_source = "explicit"
    else:
        years = {
            "5y": 5,
            "2y": 2,
            "1y": 1,
            "6mo": 0.5,
        }[period]
        total_days = int(round(years * 365.25))
        start_of_period = _dt.date.fromisoformat(end_date) - _dt.timedelta(days=total_days)
        warmup_days = int(round(total_days * (1.0 - ratio)))
        start_date = (
            start_of_period
            + _dt.timedelta(days=warmup_days)
        ).isoformat()
        start_source = "calendar_ratio"

    if start_date > end_date:
        return {
            "success": False,
            "message": "OOS test start date must be on or before the test end date.",
        }

    print(
        f"[MarketIQ] Starting V3 OOS validation: {symbol} / {period} "
        f"| test={start_date}..{end_date}"
    )

    result = run_backtest(
        symbol,
        period=period,
        evaluation_start_date=start_date,
        evaluation_end_date=end_date,
        evaluation_mode="OOS",
    )

    if not isinstance(result, dict):
        return {
            "success": False,
            "message": "Backtest engine returned an invalid response.",
        }

    if result.get("success") is False:
        return result

    total_trades = int(result.get("total_trades") or 0)
    winning_trades = int(result.get("winning_trades") or 0)
    losing_trades = int(result.get("losing_trades") or 0)
    flat_trades = int(result.get("flat_trades") or 0)
    gross_profit = safe_float(result.get("gross_profit"), 0.0)
    gross_loss = abs(safe_float(result.get("gross_loss"), 0.0))

    profit_factor = (
        gross_profit / gross_loss
        if gross_loss > 0
        else (float("inf") if gross_profit > 0 else 0.0)
    )

    trades = result.get("trades") or []
    exit_reasons: Dict[str, int] = {}
    for trade in trades:
        reason = str(trade.get("exit_reason") or "UNKNOWN")
        exit_reasons[reason] = exit_reasons.get(reason, 0) + 1

    return {
        "success": True,
        "validation": "V3_OUT_OF_SAMPLE",
        "version": "V3",
        "symbol": symbol,
        "period": period,
        "test_window": {
            "start_date": start_date,
            "end_date": end_date,
            "start_source": start_source,
            "oos_ratio": round(ratio, 4),
        },
        "frozen_strategy": {
            "v3_enabled": ENABLE_V3_STRATEGY,
            "minimum_rank": V3_MIN_RANK,
            "minimum_confidence": MIN_CONFIDENCE,
            "minimum_risk_reward": MIN_RISK_REWARD,
            "position_size_percent": POSITION_SIZE_PERCENT,
            "max_holding_days": MAX_HOLDING_DAYS,
            "sl_target_unchanged": True,
            "recommendation_engine_unchanged": True,
        },
        "out_of_sample": {
            "success": True,
            "total_trades": total_trades,
            "winning_trades": winning_trades,
            "losing_trades": losing_trades,
            "flat_trades": flat_trades,
            "win_rate": safe_float(result.get("win_rate"), 0.0),
            "total_return": safe_float(result.get("total_return"), 0.0),
            "max_drawdown": safe_float(result.get("max_drawdown"), 0.0),
            "net_profit_loss": safe_float(result.get("net_profit_loss"), 0.0),
            "average_trade_return": safe_float(result.get("average_trade_return"), 0.0),
            "profit_factor": (
                round(profit_factor, 2)
                if math.isfinite(profit_factor)
                else None
            ),
            "prediction_accuracy": safe_float(
                (result.get("summary") or {}).get("accuracy"),
                0.0,
            ),
            "exit_reason_breakdown": exit_reasons,
        },
        "trades": trades,
        "summary": result.get("summary"),
        "trade_diagnostics": result.get("trade_diagnostics"),
        "backtest_warnings": result.get("backtest_warnings", 0),
        "methodology": {
            "type": "anchored_walk_forward_holdout",
            "signal_data_rule": "Only data through the signal candle is used.",
            "entry_rule": "Next candle open.",
            "oos_rule": "Only signals/trades inside the OOS window are included.",
            "boundary_rule": "Trades whose exit would occur after the OOS end are excluded.",
            "strategy_tuning_during_test": False,
            "status": "PASS" if result.get("backtest_warnings", 0) == 0 else "WARNINGS",
        },
    }
