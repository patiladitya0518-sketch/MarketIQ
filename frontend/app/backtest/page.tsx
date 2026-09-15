"use client";

import { useState } from "react";
import api from "@/lib/api";

/* ============================================================
   TYPES
============================================================ */

interface Trade {
  date?: string;
  signal_date?: string;
  action?: string;
  confidence?: number;
  score?: number;
  entry_price?: number;
  exit_price?: number;
  return_percent?: number;
  profit_loss?: number;
  capital_before?: number;
  capital_after?: number;
  result?: string;
}

interface EquityPoint {
  date?: string;
  capital?: number;
}

interface BacktestSummary {
  total_candles?: number;
  total_predictions?: number;
  correct_predictions?: number;
  accuracy?: number;

  buy_signals?: number;
  sell_signals?: number;
  hold_signals?: number;

  total_trades?: number;
  winning_trades?: number;
  losing_trades?: number;
  win_rate?: number;

  initial_capital?: number;
  final_capital?: number;
  net_profit_loss?: number;
  total_return?: number;
  max_drawdown?: number;
}

interface BacktestResult {
  success?: boolean;
  symbol?: string;
  period?: string;

  initial_capital?: number;
  final_capital?: number;
  net_profit_loss?: number;
  total_return?: number;

  total_trades?: number;
  winning_trades?: number;
  losing_trades?: number;
  flat_trades?: number;

  win_rate?: number;
  max_drawdown?: number;
  average_trade_return?: number;

  best_trade?: Trade | null;
  worst_trade?: Trade | null;

  equity_curve?: EquityPoint[];
  trades?: Trade[];
  results?: any[];

  summary?: BacktestSummary;

  [key: string]: any;
}

/* ============================================================
   GLOBAL FORMATTERS
   IMPORTANT:
   These are outside BacktestPage so TradeCard can use them.
============================================================ */

const formatCurrency = (value: any) => {
  const number = Number(value);

  if (!Number.isFinite(number)) {
    return "—";
  }

  return `₹${number.toLocaleString("en-IN", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}`;
};

const formatPercent = (value: any) => {
  const number = Number(value);

  if (!Number.isFinite(number)) {
    return "—";
  }

  return `${number.toFixed(2)}%`;
};

const formatNumber = (
  value: any,
  decimals = 2
) => {
  const number = Number(value);

  if (!Number.isFinite(number)) {
    return "—";
  }

  return number.toFixed(decimals);
};

/* ============================================================
   MAIN BACKTEST PAGE
============================================================ */

export default function BacktestPage() {
  const [symbol, setSymbol] =
    useState("RELIANCE");

  const [period, setPeriod] =
    useState("1y");

  const [result, setResult] =
    useState<BacktestResult | null>(null);

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState<string | null>(null);

  /* ==========================================================
     RUN BACKTEST
  ========================================================== */

  const runBacktest = async () => {
    // Prevent duplicate requests from repeated clicks or Enter presses.
    if (loading) {
      return;
    }

    const cleanSymbol =
      symbol.trim().toUpperCase();

    if (!cleanSymbol) {
      setError(
        "Please enter a stock symbol."
      );
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const timeoutByPeriod: Record<string, number> = {
        "6mo": 180000,
        "1y": 180000,
        "2y": 900000,
        "5y": 1800000,
      };

      const response = await api.get(
        `/backtest/${encodeURIComponent(
          cleanSymbol
        )}`,
        {
          params: {
            period,
          },
          timeout: timeoutByPeriod[period] ?? 180000,
        }
      );

      const data = response?.data;

      if (data?.success === false) {
        setError(
          data?.message ||
            "Unable to run backtest."
        );
        return;
      }

      setResult(data);

    } catch (err: any) {
      console.error(
        "Backtest error:",
        err?.response?.data ||
          err?.message ||
          err
      );

      const status = err?.response?.status;
      const isTimeout =
        err?.code === "ECONNABORTED" ||
        err?.code === "ETIMEDOUT" ||
        typeof err?.message === "string" &&
          err.message.toLowerCase().includes("timeout");

      setError(
        isTimeout
          ? "The backtest is taking longer than expected. 2Y/5Y analysis can take several minutes. Please wait and try again if it eventually fails."
          : status === 404
            ? "Backtest endpoint was not found. Please check the backend deployment."
            : status === 401
              ? "Your session has expired. Please log in again."
              : err?.response?.data?.detail ||
                err?.response?.data?.message ||
                err?.message ||
                "Failed to run backtest. Please try again."
      );

    } finally {
      setLoading(false);
    }
  };

  /* ==========================================================
     RENDER
  ========================================================== */

  return (
    <main className="min-h-screen bg-slate-950 text-white px-6 py-10">

      <div className="mx-auto max-w-7xl">

        {/* ======================================================
            HEADER
        ====================================================== */}

        <div className="mb-8">

          <p className="mb-2 text-sm font-medium text-cyan-400">
            MarketIQ
          </p>

          <h1 className="text-3xl font-bold">
            Strategy Backtesting
          </h1>

          <p className="mt-2 text-slate-400">
            Test MarketIQ trading signals against
            historical Indian stock market data.
          </p>

        </div>

        {/* ======================================================
            SEARCH CARD
        ====================================================== */}

        <section className="rounded-2xl border border-slate-800 bg-slate-900 p-6 shadow-xl">

          <div className="grid gap-5 md:grid-cols-3">

            {/* SYMBOL */}

            <div>

              <label className="mb-2 block text-sm font-medium text-slate-300">
                Stock Symbol
              </label>

              <input
                value={symbol}
                onChange={(e) =>
                  setSymbol(e.target.value)
                }
                onKeyDown={(e) => {
                  if (e.key === "Enter") {
                    runBacktest();
                  }
                }}
                placeholder="RELIANCE"
                className="w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none transition focus:border-cyan-500"
              />

            </div>

            {/* PERIOD */}

            <div>

              <label className="mb-2 block text-sm font-medium text-slate-300">
                Historical Period
              </label>

              <select
                value={period}
                onChange={(e) =>
                  setPeriod(e.target.value)
                }
                className="w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none focus:border-cyan-500"
              >

                <option value="6mo">
                  6 Months
                </option>

                <option value="1y">
                  1 Year
                </option>

                <option value="2y">
                  2 Years
                </option>

                <option value="5y">
                  5 Years
                </option>

              </select>

            </div>

            {/* BUTTON */}

            <div className="flex items-end">

              <button
                onClick={runBacktest}
                disabled={loading}
                className="w-full rounded-xl bg-cyan-500 px-5 py-3 font-semibold text-slate-950 transition hover:bg-cyan-400 disabled:cursor-not-allowed disabled:opacity-50"
              >

                {loading ? (
                  <span className="flex items-center justify-center gap-2">
                    <span
                      className="h-4 w-4 animate-spin rounded-full border-2 border-slate-950 border-t-transparent"
                      aria-hidden="true"
                    />
                    Running Backtest...
                  </span>
                ) : (
                  "Run Backtest"
                )}

              </button>

            </div>

          </div>

          {/* ERROR */}

          {error && (
            <div className="mt-5 rounded-xl border border-red-900 bg-red-950/40 px-4 py-3 text-sm text-red-300">
              {error}
            </div>
          )}

        </section>

        {/* ======================================================
            LOADING
        ====================================================== */}

        {loading && (
          <div className="mt-8 rounded-2xl border border-slate-800 bg-slate-900 p-10 text-center">

            <div className="text-3xl">
              📊
            </div>

            <p className="mt-4 text-lg font-semibold">
              Running historical backtest...
            </p>

            <p className="mt-2 text-sm text-slate-400">
              MarketIQ is analysing historical
              candles and generating trades. Please keep this page open until the request finishes.
            </p>

          </div>
        )}

        {/* ======================================================
            RESULTS
        ====================================================== */}

        {result && !loading && (
          <section className="mt-8">

            {/* RESULT HEADER */}

            <div className="mb-6 flex flex-col justify-between gap-3 md:flex-row md:items-center">

              <div>

                <p className="text-sm text-slate-400">
                  Backtest Result
                </p>

                <h2 className="text-2xl font-bold">
                  {result.symbol ||
                    symbol.toUpperCase()}
                </h2>

              </div>

              <div className="rounded-xl border border-slate-800 bg-slate-900 px-4 py-2 text-sm text-slate-300">

                Period:{" "}

                <span className="font-semibold text-white">
                  {result.period || period}
                </span>

              </div>

            </div>

            {/* ==================================================
                MAIN PERFORMANCE CARDS
            ================================================== */}

            <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-4">

              <StatCard
                title="Total Trades"
                value={
                  result.total_trades ??
                  result.summary?.total_trades ??
                  0
                }
              />

              <StatCard
                title="Win Rate"
                value={formatPercent(
                  result.win_rate ??
                    result.summary?.win_rate
                )}
              />

              <StatCard
                title="Total Return"
                value={formatPercent(
                  result.total_return ??
                    result.summary?.total_return
                )}
              />

              <StatCard
                title="Max Drawdown"
                value={formatPercent(
                  result.max_drawdown ??
                    result.summary?.max_drawdown
                )}
              />

            </div>

            {/* ==================================================
                CAPITAL PERFORMANCE
            ================================================== */}

            <div className="mt-6 grid gap-5 sm:grid-cols-2 lg:grid-cols-4">

              <StatCard
                title="Initial Capital"
                value={formatCurrency(
                  result.initial_capital ??
                    result.summary?.initial_capital
                )}
              />

              <StatCard
                title="Final Capital"
                value={formatCurrency(
                  result.final_capital ??
                    result.summary?.final_capital
                )}
              />

              <StatCard
                title="Net P&L"
                value={formatCurrency(
                  result.net_profit_loss ??
                    result.summary?.net_profit_loss
                )}
              />

              <StatCard
                title="Avg Trade Return"
                value={formatPercent(
                  result.average_trade_return
                )}
              />

            </div>

            {/* ==================================================
                TRADING + SIGNAL STATISTICS
            ================================================== */}

            <div className="mt-6 grid gap-6 lg:grid-cols-2">

              {/* TRADING PERFORMANCE */}

              <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">

                <h3 className="mb-5 text-lg font-semibold">
                  Trading Performance
                </h3>

                <div className="space-y-4">

                  <ResultRow
                    label="Total Trades"
                    value={
                      result.total_trades ??
                      result.summary?.total_trades ??
                      "—"
                    }
                  />

                  <ResultRow
                    label="Winning Trades"
                    value={
                      result.winning_trades ??
                      result.summary?.winning_trades ??
                      "—"
                    }
                  />

                  <ResultRow
                    label="Losing Trades"
                    value={
                      result.losing_trades ??
                      result.summary?.losing_trades ??
                      "—"
                    }
                  />

                  <ResultRow
                    label="Flat Trades"
                    value={
                      result.flat_trades ??
                      "—"
                    }
                  />

                  <ResultRow
                    label="Win Rate"
                    value={formatPercent(
                      result.win_rate ??
                        result.summary?.win_rate
                    )}
                  />

                  <ResultRow
                    label="Max Drawdown"
                    value={formatPercent(
                      result.max_drawdown ??
                        result.summary?.max_drawdown
                    )}
                  />

                </div>

              </div>

              {/* SIGNAL STATISTICS */}

              <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">

                <h3 className="mb-5 text-lg font-semibold">
                  Signal Statistics
                </h3>

                <div className="space-y-4">

                  <ResultRow
                    label="BUY Signals"
                    value={
                      result.summary?.buy_signals ??
                      "—"
                    }
                  />

                  <ResultRow
                    label="SELL Signals"
                    value={
                      result.summary?.sell_signals ??
                      "—"
                    }
                  />

                  <ResultRow
                    label="HOLD Signals"
                    value={
                      result.summary?.hold_signals ??
                      "—"
                    }
                  />

                  <ResultRow
                    label="Total Predictions"
                    value={
                      result.summary?.total_predictions ??
                      "—"
                    }
                  />

                  <ResultRow
                    label="Correct Predictions"
                    value={
                      result.summary?.correct_predictions ??
                      "—"
                    }
                  />

                  <ResultRow
                    label="Prediction Accuracy"
                    value={formatPercent(
                      result.summary?.accuracy
                    )}
                  />

                </div>

              </div>

            </div>

            {/* ==================================================
                BEST / WORST TRADE
            ================================================== */}

            <div className="mt-6 grid gap-6 lg:grid-cols-2">

              <TradeCard
                title="Best Trade"
                trade={result.best_trade}
                positive
              />

              <TradeCard
                title="Worst Trade"
                trade={result.worst_trade}
              />

            </div>

            {/* ==================================================
                TRADE HISTORY
            ================================================== */}

            <div className="mt-6 rounded-2xl border border-slate-800 bg-slate-900 p-6">

              <div className="mb-5 flex items-center justify-between">

                <div>

                  <h3 className="text-lg font-semibold">
                    Trade History
                  </h3>

                  <p className="mt-1 text-sm text-slate-400">
                    Simulated one-candle trades
                    generated by MarketIQ.
                  </p>

                </div>

                <span className="rounded-lg border border-slate-700 bg-slate-950 px-3 py-1 text-sm text-slate-300">
                  {result.trades?.length ?? 0} trades
                </span>

              </div>

              {result.trades &&
              result.trades.length > 0 ? (

                <div className="overflow-x-auto">

                  <table className="w-full text-left text-sm">

                    <thead>

                      <tr className="border-b border-slate-800 text-slate-400">

                        <th className="px-3 py-3">
                          Date
                        </th>

                        <th className="px-3 py-3">
                          Action
                        </th>

                        <th className="px-3 py-3">
                          Entry
                        </th>

                        <th className="px-3 py-3">
                          Exit
                        </th>

                        <th className="px-3 py-3">
                          Return
                        </th>

                        <th className="px-3 py-3">
                          P&L
                        </th>

                        <th className="px-3 py-3">
                          Result
                        </th>

                      </tr>

                    </thead>

                    <tbody>

                      {result.trades.map(
                        (trade, index) => (

                          <tr
                            key={`${trade.date}-${index}`}
                            className="border-b border-slate-800/70"
                          >

                            <td className="px-3 py-3 text-slate-300">
                              {trade.date || "—"}
                            </td>

                            <td
                              className={`px-3 py-3 font-semibold ${
                                trade.action === "BUY"
                                  ? "text-emerald-400"
                                  : trade.action === "SELL"
                                  ? "text-red-400"
                                  : "text-slate-300"
                              }`}
                            >
                              {trade.action || "—"}
                            </td>

                            <td className="px-3 py-3">
                              {formatCurrency(
                                trade.entry_price
                              )}
                            </td>

                            <td className="px-3 py-3">
                              {formatCurrency(
                                trade.exit_price
                              )}
                            </td>

                            <td
                              className={`px-3 py-3 font-medium ${
                                Number(
                                  trade.return_percent
                                ) >= 0
                                  ? "text-emerald-400"
                                  : "text-red-400"
                              }`}
                            >
                              {formatPercent(
                                trade.return_percent
                              )}
                            </td>

                            <td
                              className={`px-3 py-3 font-medium ${
                                Number(
                                  trade.profit_loss
                                ) >= 0
                                  ? "text-emerald-400"
                                  : "text-red-400"
                              }`}
                            >
                              {formatCurrency(
                                trade.profit_loss
                              )}
                            </td>

                            <td className="px-3 py-3">

                              <span
                                className={`rounded-lg px-2 py-1 text-xs font-semibold ${
                                  trade.result === "WIN"
                                    ? "bg-emerald-500/10 text-emerald-400"
                                    : trade.result === "LOSS"
                                    ? "bg-red-500/10 text-red-400"
                                    : "bg-slate-700 text-slate-300"
                                }`}
                              >
                                {trade.result || "—"}
                              </span>

                            </td>

                          </tr>

                        )
                      )}

                    </tbody>

                  </table>

                </div>

              ) : (

                <div className="rounded-xl border border-dashed border-slate-800 bg-slate-950 p-8 text-center text-slate-400">

                  No trades were generated during
                  this backtest period.

                </div>

              )}

            </div>

            {/* ==================================================
                EQUITY CURVE
            ================================================== */}

            <div className="mt-6 rounded-2xl border border-slate-800 bg-slate-900 p-6">

              <h3 className="mb-2 text-lg font-semibold">
                Equity Curve
              </h3>

              <p className="mb-5 text-sm text-slate-400">
                Portfolio capital after each
                historical trading day.
              </p>

              {result.equity_curve &&
              result.equity_curve.length > 0 ? (

                <div className="max-h-80 overflow-auto rounded-xl border border-slate-800 bg-slate-950">

                  <table className="w-full text-left text-sm">

                    <thead className="sticky top-0 bg-slate-950">

                      <tr className="border-b border-slate-800 text-slate-400">

                        <th className="px-4 py-3">
                          Date
                        </th>

                        <th className="px-4 py-3">
                          Capital
                        </th>

                      </tr>

                    </thead>

                    <tbody>

                      {result.equity_curve.map(
                        (point, index) => (

                          <tr
                            key={`${point.date}-${index}`}
                            className="border-b border-slate-800/70"
                          >

                            <td className="px-4 py-3 text-slate-300">
                              {point.date || "—"}
                            </td>

                            <td className="px-4 py-3 font-semibold">
                              {formatCurrency(
                                point.capital
                              )}
                            </td>

                          </tr>

                        )
                      )}

                    </tbody>

                  </table>

                </div>

              ) : (

                <p className="text-sm text-slate-400">
                  No equity curve data available.
                </p>

              )}

            </div>

            {/* ==================================================
                TRADE DIAGNOSTICS
            ================================================== */}

            {result.trade_diagnostics && (
              <div className="mt-6 rounded-2xl border border-cyan-900/60 bg-slate-900 p-6">
                <h3 className="mb-2 text-lg font-semibold">
                  Trade Diagnostics
                </h3>
                <p className="mb-5 text-sm text-slate-400">
                  Diagnostic-only analysis of exits, realized risk, and price excursions. These metrics do not change the trading strategy.
                </p>

                {result.trade_diagnostics.trade_quality_v3 && (
                  <div className="mb-6 rounded-xl border border-emerald-900/60 bg-slate-950 p-4">
                    <div className="flex flex-wrap items-center justify-between gap-2">
                      <h4 className="font-semibold text-emerald-300">MarketIQ V3 Strategy</h4>
                      <span className="rounded-full border border-emerald-800 px-2 py-1 text-xs text-emerald-300">ACTIVE · A / A+ ONLY</span>
                    </div>
                    <p className="mt-1 text-sm text-slate-400">
                      V3 adds market-regime detection, entry-timing confirmation and A+/A/B/C signal ranking on top of the frozen V2.1 framework. It uses only the signal candle and earlier candles.
                    </p>
                    <div className="mt-4 grid gap-3 md:grid-cols-4">
                      <ResultRow label="Version" value={result.trade_diagnostics.trade_quality_v3.version || "V3"} />
                      <ResultRow label="Minimum Rank" value={result.trade_diagnostics.trade_quality_v3.minimum_rank || "A"} />
                      <ResultRow label="A+ Results" value={result.trade_diagnostics.trade_quality_v3.rank_breakdown?.["A+"] ?? 0} />
                      <ResultRow label="A Results" value={result.trade_diagnostics.trade_quality_v3.rank_breakdown?.A ?? 0} />
                    </div>
                    <div className="mt-4 grid gap-4 lg:grid-cols-2">
                      <div className="rounded-lg border border-slate-800 p-3">
                        <h5 className="mb-3 font-medium text-emerald-300">Signal Rank Breakdown</h5>
                        <div className="space-y-2 text-sm">
                          {Object.entries(result.trade_diagnostics.trade_quality_v3.rank_breakdown || {}).map(([name, value]: [string, any]) => (
                            <ResultRow key={name} label={name} value={value} />
                          ))}
                        </div>
                      </div>
                      <div className="rounded-lg border border-slate-800 p-3">
                        <h5 className="mb-3 font-medium text-cyan-300">Market Regime</h5>
                        <div className="space-y-2 text-sm">
                          {Object.entries(result.trade_diagnostics.trade_quality_v3.regime_breakdown || {}).map(([name, value]: [string, any]) => (
                            <ResultRow key={name} label={name} value={value} />
                          ))}
                        </div>
                      </div>
                    </div>
                    <div className="mt-4 rounded-lg border border-emerald-900/50 bg-emerald-950/20 p-3 text-sm text-slate-300">
                      <strong className="text-emerald-300">V3 risk controls:</strong> existing V2.1 stop-loss, target, R:R ≥ 1.5, 20% position size and 5-session maximum holding period are unchanged. V3 only tightens which directional entries are allowed.
                    </div>
                  </div>
                )}

                {result.trade_diagnostics.trade_quality_v25 && (
                  <div className="mb-6 rounded-xl border border-cyan-900/60 bg-slate-950 p-4">
                    <div className="flex flex-wrap items-center justify-between gap-2">
                      <h4 className="font-semibold text-cyan-300">Composite Entry Analysis V2.5</h4>
                      <span className="rounded-full border border-cyan-800 px-2 py-1 text-xs text-cyan-300">FINAL DIAGNOSTIC · Strategy Unchanged</span>
                    </div>
                    <p className="mt-1 text-sm text-slate-400">
                      Final diagnostic pass combining momentum, EMA20 position, market structure, SMC, candle confirmation, opening alignment, and confidence. No trading rule is changed by this analysis.
                    </p>
                    <div className="mt-4 grid gap-3 md:grid-cols-4">
                      <ResultRow label="Version" value={result.trade_diagnostics.trade_quality_v25.version || "V2.5"} />
                      <ResultRow label="Target Trades" value={result.trade_diagnostics.trade_quality_v25.target_trades ?? 0} />
                      <ResultRow label="Stop-Loss Trades" value={result.trade_diagnostics.trade_quality_v25.stop_loss_trades ?? 0} />
                      <ResultRow label="Target Net P&L" value={formatCurrency(result.trade_diagnostics.trade_quality_v25.target_net_profit_loss)} />
                    </div>
                    <div className="mt-5 rounded-lg border border-slate-800 p-3">
                      <h5 className="mb-3 font-medium text-emerald-300">Candidate Composite Rules — TARGET vs STOP</h5>
                      <div className="space-y-2 text-sm">
                        {(result.trade_diagnostics.trade_quality_v25.ranked_combinations || []).map((item: any) => (
                          <ResultRow
                            key={item.name}
                            label={item.name}
                            value={`Target ${item.target_count ?? 0}/${item.target_rate ?? 0}% · Stop ${item.stop_count ?? 0}/${item.stop_rate ?? 0}% · Δ ${item.target_minus_stop_rate ?? 0}%`}
                          />
                        ))}
                      </div>
                    </div>
                    <div className="mt-4 grid gap-4 lg:grid-cols-2">
                      <div className="rounded-lg border border-slate-800 p-3">
                        <h5 className="mb-3 font-medium text-emerald-300">Target Averages</h5>
                        <div className="space-y-2 text-sm">
                          {Object.entries(result.trade_diagnostics.trade_quality_v25.target_averages || {}).map(([name, value]: [string, any]) => (
                            <ResultRow key={name} label={name} value={formatNumber(value)} />
                          ))}
                        </div>
                      </div>
                      <div className="rounded-lg border border-slate-800 p-3">
                        <h5 className="mb-3 font-medium text-amber-300">Stop-Loss Averages</h5>
                        <div className="space-y-2 text-sm">
                          {Object.entries(result.trade_diagnostics.trade_quality_v25.stop_loss_averages || {}).map(([name, value]: [string, any]) => (
                            <ResultRow key={name} label={name} value={formatNumber(value)} />
                          ))}
                        </div>
                      </div>
                    </div>
                    <div className="mt-4 rounded-lg border border-slate-800 p-3">
                      <h5 className="mb-3 font-medium text-red-300">Worst STOP-LOSS Cases</h5>
                      <div className="space-y-2">
                        {(result.trade_diagnostics.trade_quality_v25.worst_stop_loss_cases || []).slice(0, 5).map((item: any, index: number) => (
                          <div key={`${item.date || "case"}-${index}`} className="rounded-lg border border-slate-800 p-3 text-xs text-slate-300">
                            <div className="flex flex-wrap justify-between gap-2">
                              <span>{item.date || "—"} · {item.action || "—"}</span>
                              <span className="text-red-300">{formatPercent(item.return_percent)} · {formatCurrency(item.profit_loss)}</span>
                            </div>
                            <div className="mt-2 grid gap-1 md:grid-cols-4">
                              <span>Conf {formatNumber(item.confidence)}%</span>
                              <span>RSI {formatNumber(item.rsi)}</span>
                              <span>MACD Δ {formatNumber(item.macd_delta)}</span>
                              <span>EMA20 Δ {formatNumber(item.price_vs_ema20_percent)}%</span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                    <div className="mt-4 rounded-lg border border-cyan-900/50 bg-cyan-950/20 p-3 text-sm text-slate-300">
                      <strong className="text-cyan-300">Promotion gate:</strong> V2.5 is diagnostic only. A rule should be promoted only if it separates TARGET from STOP-LOSS trades without relying on the small RELIANCE sample and improves broader out-of-sample validation. Otherwise, freeze V2.1.
                    </div>
                  </div>
                )}

                {result.trade_diagnostics.trade_quality_v24 && (
                  <div className="mb-6 rounded-xl border border-cyan-900/60 bg-slate-950 p-4">
                    <div className="flex flex-wrap items-center justify-between gap-2">
                      <h4 className="font-semibold text-cyan-300">Trade Entry Confirmation V2.4</h4>
                      <span className="rounded-full border border-cyan-800 px-2 py-1 text-xs text-cyan-300">Diagnostic Only · Strategy Unchanged</span>
                    </div>
                    <p className="mt-1 text-sm text-slate-400">
                      Tests signal-candle strength, close confirmation, momentum, EMA20 distance, and next-candle opening alignment against TARGET and STOP-LOSS outcomes.
                    </p>
                    <div className="mt-4 grid gap-3 md:grid-cols-4">
                      <ResultRow label="Version" value={result.trade_diagnostics.trade_quality_v24.version || "V2.4"} />
                      <ResultRow label="Target Trades" value={result.trade_diagnostics.trade_quality_v24.target_trades ?? 0} />
                      <ResultRow label="Stop-Loss Trades" value={result.trade_diagnostics.trade_quality_v24.stop_loss_trades ?? 0} />
                      <ResultRow label="Target Net P&L" value={formatCurrency(result.trade_diagnostics.trade_quality_v24.target_net_profit_loss)} />
                    </div>
                    <div className="mt-5 grid gap-4 lg:grid-cols-2">
                      <div className="rounded-lg border border-slate-800 p-3">
                        <h5 className="mb-3 font-medium text-emerald-300">Average Entry Features</h5>
                        <div className="space-y-2 text-sm">
                          {Object.entries(result.trade_diagnostics.trade_quality_v24.target_averages || {}).map(([name, target]: [string, any]) => (
                            <ResultRow
                              key={name}
                              label={name}
                              value={`Target ${formatNumber(target)} · Stop ${formatNumber((result.trade_diagnostics.trade_quality_v24.stop_loss_averages || {})[name])}`}
                            />
                          ))}
                        </div>
                      </div>
                      <div className="rounded-lg border border-slate-800 p-3">
                        <h5 className="mb-3 font-medium text-amber-300">Confirmation Counts</h5>
                        <div className="space-y-2 text-sm">
                          {Object.entries(result.trade_diagnostics.trade_quality_v24.target_feature_counts || {}).map(([name, target]: [string, any]) => (
                            <ResultRow
                              key={name}
                              label={name}
                              value={`Target ${target ?? 0} · Stop ${((result.trade_diagnostics.trade_quality_v24.stop_loss_feature_counts || {})[name]) ?? 0}`}
                            />
                          ))}
                        </div>
                      </div>
                    </div>
                    <div className="mt-4 grid gap-4 lg:grid-cols-2">
                      <div className="rounded-lg border border-slate-800 p-3">
                        <h5 className="mb-3 font-medium text-emerald-300">TARGET Combinations</h5>
                        <div className="space-y-2 text-sm">
                          {Object.entries(result.trade_diagnostics.trade_quality_v24.target_combinations || {}).map(([name, value]: [string, any]) => (
                            <ResultRow key={name} label={name} value={value ?? 0} />
                          ))}
                        </div>
                      </div>
                      <div className="rounded-lg border border-slate-800 p-3">
                        <h5 className="mb-3 font-medium text-red-300">STOP-LOSS Combinations</h5>
                        <div className="space-y-2 text-sm">
                          {Object.entries(result.trade_diagnostics.trade_quality_v24.stop_loss_combinations || {}).map(([name, value]: [string, any]) => (
                            <ResultRow key={name} label={name} value={value ?? 0} />
                          ))}
                        </div>
                      </div>
                    </div>
                    <div className="mt-4 rounded-lg border border-slate-800 p-3">
                      <h5 className="mb-3 font-medium text-red-300">Worst STOP-LOSS Cases</h5>
                      <div className="space-y-2 text-sm">
                        {(result.trade_diagnostics.trade_quality_v24.worst_stop_loss_cases || []).map((item: any, index: number) => (
                          <div key={`${item.date || "case"}-${index}`} className="rounded-lg border border-slate-800 bg-slate-900 p-3">
                            <div className="font-medium text-white">
                              {item.date || "—"} · {item.action || "—"} · {formatNumber(item.return_percent)}% · {formatCurrency(item.profit_loss)}
                            </div>
                            <div className="mt-1 text-slate-400">
                              Conf {formatNumber(item.confidence)} · RSI {formatNumber(item.rsi)} · Body/Range {formatNumber(item.signal_candle_body_to_range_percent)}% · Confirmation {item.entry_confirmation_score ?? 0}/5 · MFE {formatNumber(item.mfe_percent)}% · MAE {formatNumber(item.mae_percent)}%
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                )}

                {result.trade_diagnostics.trade_quality_v23 && (
                  <div className="mb-6 rounded-xl border border-cyan-900/60 bg-slate-950 p-4">
                    <div className="flex flex-wrap items-center justify-between gap-2">
                      <h4 className="font-semibold text-cyan-300">Trade Entry Timing V2.3</h4>
                      <span className="rounded-full border border-cyan-800 px-2 py-1 text-xs text-cyan-300">Diagnostic Only · Strategy Unchanged</span>
                    </div>
                    <p className="mt-1 text-sm text-slate-400">
                      Compares successful TARGET entries with STOP-LOSS entries to identify repeatable entry-timing and follow-through differences.
                    </p>
                    <div className="mt-4 grid gap-3 md:grid-cols-4">
                      <ResultRow label="Version" value={result.trade_diagnostics.trade_quality_v23.version || "V2.3"} />
                      <ResultRow label="Target Trades" value={result.trade_diagnostics.trade_quality_v23.target_trades ?? 0} />
                      <ResultRow label="Stop-Loss Trades" value={result.trade_diagnostics.trade_quality_v23.stop_loss_trades ?? 0} />
                      <ResultRow label="Target Net P&L" value={formatCurrency(result.trade_diagnostics.trade_quality_v23.target_net_profit_loss)} />
                    </div>

                    <div className="mt-5 grid gap-4 lg:grid-cols-2">
                      <div className="rounded-lg border border-slate-800 p-3">
                        <h5 className="mb-3 font-medium text-emerald-300">TARGET vs STOP-LOSS Features</h5>
                        <div className="space-y-2 text-sm">
                          {Object.entries(result.trade_diagnostics.trade_quality_v23.feature_comparison || {}).map(([name, stats]: [string, any]) => (
                            <ResultRow
                              key={name}
                              label={name}
                              value={`Target ${formatNumber(stats.target_average)} · Stop ${formatNumber(stats.stop_loss_average)} · Δ ${formatNumber(stats.difference_target_minus_stop)}`}
                            />
                          ))}
                        </div>
                      </div>

                      <div className="rounded-lg border border-slate-800 p-3">
                        <h5 className="mb-3 font-medium text-amber-300">Entry Timing Signals</h5>
                        <div className="space-y-2 text-sm">
                          <ResultRow label="Target MFE < 0.5%" value={result.trade_diagnostics.trade_quality_v23.target_timing?.mfe_below_0_5 ?? 0} />
                          <ResultRow label="Stop MFE < 0.5%" value={result.trade_diagnostics.trade_quality_v23.stop_loss_timing?.mfe_below_0_5 ?? 0} />
                          <ResultRow label="Target High Confidence" value={result.trade_diagnostics.trade_quality_v23.high_confidence_target_trades ?? 0} />
                          <ResultRow label="Stop High Confidence" value={result.trade_diagnostics.trade_quality_v23.high_confidence_stop_loss_trades ?? 0} />
                          <ResultRow label="Target RSI Exhausted" value={result.trade_diagnostics.trade_quality_v23.target_timing?.rsi_exhausted ?? 0} />
                          <ResultRow label="Stop RSI Exhausted" value={result.trade_diagnostics.trade_quality_v23.stop_loss_timing?.rsi_exhausted ?? 0} />
                          <ResultRow label="Target Extended" value={result.trade_diagnostics.trade_quality_v23.extended_target_trades ?? 0} />
                          <ResultRow label="Stop Extended" value={result.trade_diagnostics.trade_quality_v23.extended_stop_loss_trades ?? 0} />
                        </div>
                      </div>
                    </div>

                    <div className="mt-4 rounded-lg border border-slate-800 p-3 text-sm text-slate-300">
                      <div className="grid gap-3 md:grid-cols-2">
                        <div>
                          <span className="text-slate-500">TARGET alignment:</span>{" "}
                          MS {result.trade_diagnostics.trade_quality_v23.target_alignment?.market_structure_aligned ?? 0}, SMC {result.trade_diagnostics.trade_quality_v23.target_alignment?.smc_aligned ?? 0}, Both {result.trade_diagnostics.trade_quality_v23.target_alignment?.both_aligned ?? 0}
                        </div>
                        <div>
                          <span className="text-slate-500">STOP alignment:</span>{" "}
                          MS {result.trade_diagnostics.trade_quality_v23.stop_loss_alignment?.market_structure_aligned ?? 0}, SMC {result.trade_diagnostics.trade_quality_v23.stop_loss_alignment?.smc_aligned ?? 0}, Both {result.trade_diagnostics.trade_quality_v23.stop_loss_alignment?.both_aligned ?? 0}
                        </div>
                      </div>
                    </div>

                    <div className="mt-4 rounded-lg border border-slate-800 p-3">
                      <h5 className="mb-3 font-medium">Worst STOP-LOSS Cases</h5>
                      <div className="space-y-2">
                        {(result.trade_diagnostics.trade_quality_v23.worst_stop_loss_cases || []).slice(0, 5).map((trade: any, index: number) => (
                          <div key={`${trade.date}-${index}`} className="rounded-lg border border-slate-800 p-3 text-xs text-slate-300">
                            <div className="flex flex-wrap justify-between gap-2">
                              <span>{trade.date} · {trade.action}</span>
                              <span className="text-red-300">{formatPercent(trade.return_percent)} · {formatCurrency(trade.profit_loss)}</span>
                            </div>
                            <div className="mt-2 grid gap-1 md:grid-cols-4">
                              <span>Conf {formatNumber(trade.confidence)}%</span>
                              <span>RSI {formatNumber(trade.rsi)}</span>
                              <span>MFE {formatPercent(trade.mfe_percent)}</span>
                              <span>MAE {formatPercent(trade.mae_percent)}</span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                )}

                {result.trade_diagnostics.trade_quality_v21 && (
                  <div className="mb-6 rounded-xl border border-violet-900/60 bg-slate-950 p-4">
                    <h4 className="font-semibold text-violet-300">Trade Entry Quality V2.1</h4>
                    <p className="mt-1 text-sm text-slate-400">
                      Entry-timing diagnostics and safeguards derived from the RELIANCE failure analysis. No future candles are used.
                    </p>
                    <div className="mt-4 grid gap-3 md:grid-cols-4">
                      <ResultRow label="Version" value={result.trade_diagnostics.trade_quality_v21.version || "V2.1"} />
                      <ResultRow label="High-Confidence Threshold" value={`${formatNumber(result.trade_diagnostics.trade_quality_v21.high_confidence_threshold)}%`} />
                      <ResultRow label="RSI Exhaustion BUY" value={formatNumber(result.trade_diagnostics.trade_quality_v21.rsi_exhaustion_buy)} />
                      <ResultRow label="RSI Exhaustion SELL" value={formatNumber(result.trade_diagnostics.trade_quality_v21.rsi_exhaustion_sell)} />
                    </div>
                  </div>
                )}

                <div className="grid gap-4 md:grid-cols-4">
                  <StatCard
                    title="Max-Hold Trades"
                    value={result.trade_diagnostics.max_holding_period?.count ?? 0}
                  />
                  <StatCard
                    title="Max-Hold Net P&L"
                    value={formatCurrency(result.trade_diagnostics.max_holding_period?.net_profit_loss)}
                  />
                  <StatCard
                    title="Risk-Exceeded Trades"
                    value={result.trade_diagnostics.risk_exceeded?.count ?? 0}
                  />
                  <StatCard
                    title="Risk-Exceeded %"
                    value={formatPercent(result.trade_diagnostics.risk_exceeded?.percent_of_trades)}
                  />
                </div>

                <div className="mt-6 grid gap-6 lg:grid-cols-2">
                  <div className="rounded-xl border border-slate-800 bg-slate-950 p-4">
                    <h4 className="mb-4 font-semibold">Exit Reason Breakdown</h4>
                    <div className="space-y-3">
                      {Object.entries(result.trade_diagnostics.exit_reason_breakdown || {}).map(([reason, stats]: [string, any]) => (
                        <div key={reason} className="rounded-lg border border-slate-800 p-3">
                          <div className="flex justify-between gap-4">
                            <span className="font-medium">{reason}</span>
                            <span className="text-slate-300">{stats.count} trades</span>
                          </div>
                          <div className="mt-2 grid grid-cols-3 gap-2 text-xs text-slate-400">
                            <span>Wins: {stats.wins}</span>
                            <span>Losses: {stats.losses}</span>
                            <span>Avg: {formatPercent(stats.average_return_percent)}</span>
                          </div>
                          <p className="mt-2 text-sm text-slate-300">
                            Net P&L: {formatCurrency(stats.net_profit_loss)} · Avg hold: {formatNumber(stats.average_holding_days)} days
                          </p>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="rounded-xl border border-slate-800 bg-slate-950 p-4">
                    <h4 className="mb-4 font-semibold">Risk & Excursion Analysis</h4>
                    <div className="space-y-3 text-sm">
                      <ResultRow label="Average MAE" value={formatPercent(result.trade_diagnostics.excursion?.average_mae_percent)} />
                      <ResultRow label="Worst MAE" value={formatPercent(result.trade_diagnostics.excursion?.worst_mae_percent)} />
                      <ResultRow label="Average MFE" value={formatPercent(result.trade_diagnostics.excursion?.average_mfe_percent)} />
                      <ResultRow label="Best MFE" value={formatPercent(result.trade_diagnostics.excursion?.best_mfe_percent)} />
                      <ResultRow label="Average Realized R" value={formatNumber(result.trade_diagnostics.realized_r_multiple?.average)} />
                      <ResultRow label="Worst Realized R" value={formatNumber(result.trade_diagnostics.realized_r_multiple?.worst)} />
                      <ResultRow label="Best Realized R" value={formatNumber(result.trade_diagnostics.realized_r_multiple?.best)} />
                      <ResultRow label="No-Lookahead Audit" value={result.trade_diagnostics.lookahead_audit?.status || "—"} />
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* ==================================================
                RAW BACKTEST RESPONSE
            ================================================== */}

            <div className="mt-6 rounded-2xl border border-slate-800 bg-slate-900 p-6">

              <h3 className="mb-5 text-lg font-semibold">
                Backtest Data
              </h3>

              <div className="rounded-xl border border-slate-800 bg-slate-950 p-4">

                <pre className="max-h-96 overflow-auto whitespace-pre-wrap break-words text-sm text-slate-300">
                  {JSON.stringify(
                    result,
                    null,
                    2
                  )}
                </pre>

              </div>

            </div>

            {/* ==================================================
                DISCLAIMER
            ================================================== */}

            <div className="mt-6 rounded-xl border border-yellow-900/50 bg-yellow-950/20 p-4 text-sm text-yellow-300">

              Backtest results are based on
              historical data and do not guarantee
              future trading performance. This
              simulation does not include brokerage,
              taxes, slippage or liquidity effects.
              Always perform your own research and
              risk assessment.

            </div>

          </section>
        )}

        {/* ======================================================
            EMPTY STATE
        ====================================================== */}

        {!result &&
        !loading &&
        !error && (

          <div className="mt-8 rounded-2xl border border-dashed border-slate-800 bg-slate-900/50 p-12 text-center">

            <div className="text-4xl">
              📊
            </div>

            <h2 className="mt-4 text-xl font-semibold">
              Ready to Backtest
            </h2>

            <p className="mx-auto mt-2 max-w-lg text-slate-400">
              Enter an NSE stock symbol, choose a
              historical period and run MarketIQ's
              backtesting engine.
            </p>

          </div>

        )}

      </div>

    </main>
  );
}

/* ============================================================
   STAT CARD
============================================================ */

function StatCard({
  title,
  value,
}: {
  title: string;
  value: any;
}) {
  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">

      <p className="text-sm text-slate-400">
        {title}
      </p>

      <p className="mt-2 text-2xl font-bold text-white">
        {value}
      </p>

    </div>
  );
}

/* ============================================================
   RESULT ROW
============================================================ */

function ResultRow({
  label,
  value,
}: {
  label: string;
  value: any;
}) {
  return (
    <div className="flex items-center justify-between border-b border-slate-800 pb-3 last:border-0">

      <span className="text-sm text-slate-400">
        {label}
      </span>

      <span className="font-semibold text-white">
        {value}
      </span>

    </div>
  );
}

/* ============================================================
   TRADE CARD
============================================================ */

function TradeCard({
  title,
  trade,
  positive = false,
}: {
  title: string;
  trade?: Trade | null;
  positive?: boolean;
}) {
  if (!trade) {
    return (
      <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">

        <h3 className="mb-5 text-lg font-semibold">
          {title}
        </h3>

        <p className="text-sm text-slate-400">
          No trade available.
        </p>

      </div>
    );
  }

  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">

      <div className="mb-5 flex items-center justify-between">

        <h3 className="text-lg font-semibold">
          {title}
        </h3>

        <span
          className={`rounded-lg px-3 py-1 text-xs font-semibold ${
            positive
              ? "bg-emerald-500/10 text-emerald-400"
              : "bg-red-500/10 text-red-400"
          }`}
        >
          {trade.result || "TRADE"}
        </span>

      </div>

      <div className="space-y-4">

        <ResultRow
          label="Date"
          value={trade.date || "—"}
        />

        <ResultRow
          label="Action"
          value={trade.action || "—"}
        />

        <ResultRow
          label="Entry Price"
          value={formatCurrency(
            trade.entry_price
          )}
        />

        <ResultRow
          label="Exit Price"
          value={formatCurrency(
            trade.exit_price
          )}
        />

        <ResultRow
          label="Return"
          value={formatPercent(
            trade.return_percent
          )}
        />

        <ResultRow
          label="Profit / Loss"
          value={formatCurrency(
            trade.profit_loss
          )}
        />

        <ResultRow
          label="Confidence"
          value={formatPercent(
            trade.confidence
          )}
        />

      </div>

    </div>
  );
}