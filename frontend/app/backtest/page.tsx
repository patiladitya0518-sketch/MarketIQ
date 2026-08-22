"use client";

import { useMemo, useState } from "react";
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
   FORMATTERS
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

const formatNumber = (value: any, decimals = 2) => {
  const number = Number(value);

  if (!Number.isFinite(number)) {
    return "—";
  }

  return number.toFixed(decimals);
};

/* ============================================================
   MAIN PAGE
============================================================ */

export default function BacktestPage() {
  const [symbol, setSymbol] = useState("RELIANCE");
  const [period, setPeriod] = useState("1y");
  const [result, setResult] = useState<BacktestResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  /* ==========================================================
     RUN BACKTEST
  ========================================================== */

  const runBacktest = async () => {
    const cleanSymbol = symbol.trim().toUpperCase();

    if (!cleanSymbol) {
      setError("Please enter a stock symbol.");
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const response = await api.get(
        `/backtest/${encodeURIComponent(cleanSymbol)}`,
        {
          params: {
            period,
          },
        }
      );

      const data = response?.data;

      if (data?.success === false) {
        setError(data?.message || "Unable to run backtest.");
        setResult(null);
        return;
      }

      setResult(data);
    } catch (err: any) {
      console.error(
        "Backtest error:",
        err?.response?.data || err?.message || err
      );

      setError(
        err?.response?.data?.detail ||
          err?.response?.data?.message ||
          err?.message ||
          "Failed to run backtest."
      );

      setResult(null);
    } finally {
      setLoading(false);
    }
  };

  /* ==========================================================
     DERIVED VALUES
  ========================================================== */

  const initialCapital =
    result?.initial_capital ??
    result?.summary?.initial_capital ??
    0;

  const finalCapital =
    result?.final_capital ??
    result?.summary?.final_capital ??
    0;

  const netProfitLoss =
    result?.net_profit_loss ??
    result?.summary?.net_profit_loss ??
    0;

  const totalReturn =
    result?.total_return ??
    result?.summary?.total_return;

  const maxDrawdown =
    result?.max_drawdown ??
    result?.summary?.max_drawdown;

  const totalTrades =
    result?.total_trades ??
    result?.summary?.total_trades ??
    0;

  const winningTrades =
    result?.winning_trades ??
    result?.summary?.winning_trades ??
    0;

  const losingTrades =
    result?.losing_trades ??
    result?.summary?.losing_trades ??
    0;

  const winRate =
    result?.win_rate ??
    result?.summary?.win_rate;

  const predictionAccuracy =
    result?.summary?.accuracy;

  const equityStats = useMemo(() => {
    const points = result?.equity_curve || [];

    if (points.length === 0) {
      return {
        min: 0,
        max: 0,
        start: 0,
        end: 0,
      };
    }

    const values = points
      .map((point) => Number(point.capital))
      .filter(Number.isFinite);

    if (values.length === 0) {
      return {
        min: 0,
        max: 0,
        start: 0,
        end: 0,
      };
    }

    return {
      min: Math.min(...values),
      max: Math.max(...values),
      start: values[0],
      end: values[values.length - 1],
    };
  }, [result]);

  /* ==========================================================
     RENDER
  ========================================================== */

  return (
    <main className="min-h-screen bg-slate-950 px-4 py-8 text-white sm:px-6 lg:px-8">
      <div className="mx-auto max-w-7xl">

        {/* ====================================================
            HEADER
        ==================================================== */}

        <div className="mb-8">
          <p className="mb-2 text-sm font-medium text-cyan-400">
            MarketIQ
          </p>

          <div className="flex flex-col justify-between gap-4 md:flex-row md:items-end">
            <div>
              <h1 className="text-3xl font-bold tracking-tight sm:text-4xl">
                Strategy Backtesting
              </h1>

              <p className="mt-2 max-w-2xl text-slate-400">
                Test MarketIQ trading signals against historical
                Indian stock market data.
              </p>
            </div>

            {result && (
              <div className="rounded-xl border border-slate-800 bg-slate-900 px-4 py-3">
                <p className="text-xs uppercase tracking-wider text-slate-500">
                  Backtest
                </p>

                <p className="mt-1 font-semibold text-cyan-400">
                  {result.symbol || symbol.toUpperCase()}
                  {" • "}
                  {result.period || period}
                </p>
              </div>
            )}
          </div>
        </div>

        {/* ====================================================
            SEARCH / CONFIGURATION
        ==================================================== */}

        <section className="rounded-2xl border border-slate-800 bg-slate-900 p-5 shadow-xl sm:p-6">
          <div className="grid gap-5 md:grid-cols-3">

            {/* SYMBOL */}

            <div>
              <label className="mb-2 block text-sm font-medium text-slate-300">
                Stock Symbol
              </label>

              <input
                value={symbol}
                onChange={(e) => setSymbol(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter") {
                    runBacktest();
                  }
                }}
                placeholder="RELIANCE"
                className="w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none transition placeholder:text-slate-600 focus:border-cyan-500"
              />
            </div>

            {/* PERIOD */}

            <div>
              <label className="mb-2 block text-sm font-medium text-slate-300">
                Historical Period
              </label>

              <select
                value={period}
                onChange={(e) => setPeriod(e.target.value)}
                className="w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none focus:border-cyan-500"
              >
                <option value="6mo">6 Months</option>
                <option value="1y">1 Year</option>
                <option value="2y">2 Years</option>
                <option value="5y">5 Years</option>
              </select>
            </div>

            {/* BUTTON */}

            <div className="flex items-end">
              <button
                onClick={runBacktest}
                disabled={loading}
                className="w-full rounded-xl bg-cyan-500 px-5 py-3 font-semibold text-slate-950 transition hover:bg-cyan-400 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {loading ? "Running Backtest..." : "Run Backtest"}
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

        {/* ====================================================
            LOADING
        ==================================================== */}

        {loading && (
          <div className="mt-8 rounded-2xl border border-slate-800 bg-slate-900 p-10 text-center">
            <div className="mx-auto h-10 w-10 animate-spin rounded-full border-4 border-slate-700 border-t-cyan-400" />

            <p className="mt-5 text-lg font-semibold">
              Running historical backtest...
            </p>

            <p className="mt-2 text-sm text-slate-400">
              MarketIQ is analysing historical candles and generating
              trades.
            </p>
          </div>
        )}

        {/* ====================================================
            RESULTS
        ==================================================== */}

        {result && !loading && (
          <section className="mt-8">

            {/* ==================================================
                PERFORMANCE HERO
            ================================================== */}

            <div className="mb-6 grid gap-5 lg:grid-cols-3">

              {/* NET RESULT */}

              <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6 lg:col-span-2">
                <div className="flex flex-col justify-between gap-5 sm:flex-row">
                  <div>
                    <p className="text-sm text-slate-400">
                      Backtest Performance
                    </p>

                    <h2 className="mt-1 text-2xl font-bold">
                      {result.symbol || symbol.toUpperCase()}
                    </h2>

                    <p className="mt-1 text-sm text-slate-500">
                      Historical period: {result.period || period}
                    </p>
                  </div>

                  <div className="text-left sm:text-right">
                    <p className="text-sm text-slate-400">
                      Net P&L
                    </p>

                    <p
                      className={`mt-1 text-3xl font-bold ${
                        Number(netProfitLoss) >= 0
                          ? "text-emerald-400"
                          : "text-red-400"
                      }`}
                    >
                      {formatCurrency(netProfitLoss)}
                    </p>

                    <p
                      className={`mt-1 text-sm font-semibold ${
                        Number(totalReturn) >= 0
                          ? "text-emerald-400"
                          : "text-red-400"
                      }`}
                    >
                      {formatPercent(totalReturn)} total return
                    </p>
                  </div>
                </div>

                <div className="mt-6 grid gap-4 sm:grid-cols-3">
                  <MiniMetric
                    label="Initial Capital"
                    value={formatCurrency(initialCapital)}
                  />

                  <MiniMetric
                    label="Final Capital"
                    value={formatCurrency(finalCapital)}
                  />

                  <MiniMetric
                    label="Max Drawdown"
                    value={formatPercent(maxDrawdown)}
                    negative
                  />
                </div>
              </div>

              {/* ACCURACY */}

              <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
                <p className="text-sm text-slate-400">
                  Prediction Accuracy
                </p>

                <p className="mt-3 text-4xl font-bold text-cyan-400">
                  {formatPercent(predictionAccuracy)}
                </p>

                <p className="mt-2 text-sm text-slate-500">
                  Correct directional predictions
                </p>

                <div className="mt-5 h-2 overflow-hidden rounded-full bg-slate-800">
                  <div
                    className="h-full rounded-full bg-cyan-400 transition-all"
                    style={{
                      width: `${Math.min(
                        Math.max(Number(predictionAccuracy) || 0, 0),
                        100
                      )}%`,
                    }}
                  />
                </div>

                <div className="mt-4 flex justify-between text-xs text-slate-500">
                  <span>
                    Correct:{" "}
                    {result.summary?.correct_predictions ?? 0}
                  </span>

                  <span>
                    Predictions:{" "}
                    {result.summary?.total_predictions ?? 0}
                  </span>
                </div>
              </div>
            </div>

            {/* ==================================================
                MAIN PERFORMANCE CARDS
            ================================================== */}

            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">

              <StatCard
                title="Total Trades"
                value={totalTrades}
                icon="📊"
              />

              <StatCard
                title="Win Rate"
                value={formatPercent(winRate)}
                icon="🏆"
                positive={Number(winRate) >= 50}
              />

              <StatCard
                title="Total Return"
                value={formatPercent(totalReturn)}
                icon="📈"
                positive={Number(totalReturn) >= 0}
              />

              <StatCard
                title="Max Drawdown"
                value={formatPercent(maxDrawdown)}
                icon="📉"
                negative
              />
            </div>

            {/* ==================================================
                CAPITAL CARDS
            ================================================== */}

            <div className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">

              <StatCard
                title="Initial Capital"
                value={formatCurrency(initialCapital)}
                icon="💰"
              />

              <StatCard
                title="Final Capital"
                value={formatCurrency(finalCapital)}
                icon="💵"
                positive={Number(finalCapital) >= Number(initialCapital)}
              />

              <StatCard
                title="Net P&L"
                value={formatCurrency(netProfitLoss)}
                icon={Number(netProfitLoss) >= 0 ? "🟢" : "🔴"}
                positive={Number(netProfitLoss) >= 0}
                negative={Number(netProfitLoss) < 0}
              />

              <StatCard
                title="Avg Trade Return"
                value={formatPercent(result.average_trade_return)}
                icon="⚡"
                positive={Number(result.average_trade_return) >= 0}
                negative={Number(result.average_trade_return) < 0}
              />
            </div>

            {/* ==================================================
                EQUITY CURVE
            ================================================== */}

            <div className="mt-6 rounded-2xl border border-slate-800 bg-slate-900 p-5 sm:p-6">

              <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
                <div>
                  <h3 className="text-lg font-semibold">
                    Equity Curve
                  </h3>

                  <p className="mt-1 text-sm text-slate-400">
                    Portfolio capital throughout the historical
                    backtest.
                  </p>
                </div>

                <div className="text-left sm:text-right">
                  <p className="text-xs text-slate-500">
                    Current Equity
                  </p>

                  <p className="font-semibold text-white">
                    {formatCurrency(equityStats.end)}
                  </p>
                </div>
              </div>

              {result.equity_curve &&
              result.equity_curve.length > 1 ? (
                <EquityChart
                  data={result.equity_curve}
                  initialCapital={Number(initialCapital)}
                />
              ) : (
                <div className="mt-6 rounded-xl border border-dashed border-slate-800 bg-slate-950 p-10 text-center text-sm text-slate-400">
                  No sufficient equity curve data available.
                </div>
              )}
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
                    value={totalTrades}
                  />

                  <ResultRow
                    label="Winning Trades"
                    value={winningTrades}
                    valueClass="text-emerald-400"
                  />

                  <ResultRow
                    label="Losing Trades"
                    value={losingTrades}
                    valueClass="text-red-400"
                  />

                  <ResultRow
                    label="Flat Trades"
                    value={result.flat_trades ?? "—"}
                  />

                  <ResultRow
                    label="Win Rate"
                    value={formatPercent(winRate)}
                  />

                  <ResultRow
                    label="Max Drawdown"
                    value={formatPercent(maxDrawdown)}
                  />
                </div>

                <div className="mt-6 grid grid-cols-2 gap-3">
                  <div className="rounded-xl bg-emerald-500/5 p-4">
                    <p className="text-xs text-slate-500">
                      Winning
                    </p>
                    <p className="mt-1 text-xl font-bold text-emerald-400">
                      {winningTrades}
                    </p>
                  </div>

                  <div className="rounded-xl bg-red-500/5 p-4">
                    <p className="text-xs text-slate-500">
                      Losing
                    </p>
                    <p className="mt-1 text-xl font-bold text-red-400">
                      {losingTrades}
                    </p>
                  </div>
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
                    value={result.summary?.buy_signals ?? "—"}
                    valueClass="text-emerald-400"
                  />

                  <ResultRow
                    label="SELL Signals"
                    value={result.summary?.sell_signals ?? "—"}
                    valueClass="text-red-400"
                  />

                  <ResultRow
                    label="HOLD Signals"
                    value={result.summary?.hold_signals ?? "—"}
                  />

                  <ResultRow
                    label="Total Predictions"
                    value={
                      result.summary?.total_predictions ?? "—"
                    }
                  />

                  <ResultRow
                    label="Correct Predictions"
                    value={
                      result.summary?.correct_predictions ?? "—"
                    }
                  />

                  <ResultRow
                    label="Prediction Accuracy"
                    value={formatPercent(
                      result.summary?.accuracy
                    )}
                  />
                </div>

                <div className="mt-6">
                  <SignalBar
                    label="BUY"
                    value={result.summary?.buy_signals ?? 0}
                    total={
                      (result.summary?.buy_signals ?? 0) +
                      (result.summary?.sell_signals ?? 0) +
                      (result.summary?.hold_signals ?? 0)
                    }
                  />

                  <SignalBar
                    label="SELL"
                    value={result.summary?.sell_signals ?? 0}
                    total={
                      (result.summary?.buy_signals ?? 0) +
                      (result.summary?.sell_signals ?? 0) +
                      (result.summary?.hold_signals ?? 0)
                    }
                  />

                  <SignalBar
                    label="HOLD"
                    value={result.summary?.hold_signals ?? 0}
                    total={
                      (result.summary?.buy_signals ?? 0) +
                      (result.summary?.sell_signals ?? 0) +
                      (result.summary?.hold_signals ?? 0)
                    }
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

            <div className="mt-6 rounded-2xl border border-slate-800 bg-slate-900 p-5 sm:p-6">

              <div className="mb-5 flex flex-col justify-between gap-3 sm:flex-row sm:items-center">
                <div>
                  <h3 className="text-lg font-semibold">
                    Trade History
                  </h3>

                  <p className="mt-1 text-sm text-slate-400">
                    Simulated one-candle trades generated by
                    MarketIQ.
                  </p>
                </div>

                <span className="w-fit rounded-lg border border-slate-700 bg-slate-950 px-3 py-1 text-sm text-slate-300">
                  {result.trades?.length ?? 0} trades
                </span>
              </div>

              {result.trades && result.trades.length > 0 ? (
                <div className="overflow-x-auto rounded-xl border border-slate-800">
                  <table className="w-full min-w-[900px] text-left text-sm">
                    <thead className="bg-slate-950">
                      <tr className="border-b border-slate-800 text-slate-400">
                        <th className="px-4 py-3">Date</th>
                        <th className="px-4 py-3">Action</th>
                        <th className="px-4 py-3">Entry</th>
                        <th className="px-4 py-3">Exit</th>
                        <th className="px-4 py-3">Return</th>
                        <th className="px-4 py-3">P&L</th>
                        <th className="px-4 py-3">Confidence</th>
                        <th className="px-4 py-3">Result</th>
                      </tr>
                    </thead>

                    <tbody>
                      {result.trades.map((trade, index) => (
                        <tr
                          key={`${trade.date}-${index}`}
                          className="border-b border-slate-800/70 transition hover:bg-slate-800/30"
                        >
                          <td className="px-4 py-3 text-slate-300">
                            {trade.date || "—"}
                          </td>

                          <td
                            className={`px-4 py-3 font-semibold ${
                              trade.action === "BUY"
                                ? "text-emerald-400"
                                : trade.action === "SELL"
                                ? "text-red-400"
                                : "text-slate-300"
                            }`}
                          >
                            {trade.action || "—"}
                          </td>

                          <td className="px-4 py-3">
                            {formatCurrency(trade.entry_price)}
                          </td>

                          <td className="px-4 py-3">
                            {formatCurrency(trade.exit_price)}
                          </td>

                          <td
                            className={`px-4 py-3 font-medium ${
                              Number(trade.return_percent) >= 0
                                ? "text-emerald-400"
                                : "text-red-400"
                            }`}
                          >
                            {formatPercent(trade.return_percent)}
                          </td>

                          <td
                            className={`px-4 py-3 font-medium ${
                              Number(trade.profit_loss) >= 0
                                ? "text-emerald-400"
                                : "text-red-400"
                            }`}
                          >
                            {formatCurrency(trade.profit_loss)}
                          </td>

                          <td className="px-4 py-3">
                            {formatPercent(trade.confidence)}
                          </td>

                          <td className="px-4 py-3">
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
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div className="rounded-xl border border-dashed border-slate-800 bg-slate-950 p-8 text-center text-slate-400">
                  No trades were generated during this backtest
                  period.
                </div>
              )}
            </div>

            {/* ==================================================
                EQUITY DATA
            ================================================== */}

            <div className="mt-6 rounded-2xl border border-slate-800 bg-slate-900 p-5 sm:p-6">
              <div className="mb-5">
                <h3 className="text-lg font-semibold">
                  Equity Data
                </h3>

                <p className="mt-1 text-sm text-slate-400">
                  Historical capital values generated by the
                  backtesting engine.
                </p>
              </div>

              {result.equity_curve &&
              result.equity_curve.length > 0 ? (
                <div className="max-h-80 overflow-auto rounded-xl border border-slate-800 bg-slate-950">
                  <table className="w-full text-left text-sm">
                    <thead className="sticky top-0 bg-slate-950">
                      <tr className="border-b border-slate-800 text-slate-400">
                        <th className="px-4 py-3">Date</th>
                        <th className="px-4 py-3">Capital</th>
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

                            <td
                              className={`px-4 py-3 font-semibold ${
                                Number(point.capital) >=
                                Number(initialCapital)
                                  ? "text-emerald-400"
                                  : "text-red-400"
                              }`}
                            >
                              {formatCurrency(point.capital)}
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
                BACKTEST DATA
            ================================================== */}

            <details className="mt-6 rounded-2xl border border-slate-800 bg-slate-900 p-5 sm:p-6">
              <summary className="cursor-pointer text-lg font-semibold text-white">
                Raw Backtest Response
              </summary>

              <div className="mt-5 rounded-xl border border-slate-800 bg-slate-950 p-4">
                <pre className="max-h-96 overflow-auto whitespace-pre-wrap break-words text-sm text-slate-300">
                  {JSON.stringify(result, null, 2)}
                </pre>
              </div>
            </details>

            {/* ==================================================
                DISCLAIMER
            ================================================== */}

            <div className="mt-6 rounded-xl border border-yellow-900/50 bg-yellow-950/20 p-4 text-sm leading-6 text-yellow-300">
              Backtest results are based on historical data and do
              not guarantee future trading performance. This
              simulation does not include brokerage, taxes,
              slippage or liquidity effects. Always perform your
              own research and risk assessment.
            </div>
          </section>
        )}

        {/* ====================================================
            EMPTY STATE
        ==================================================== */}

        {!result && !loading && !error && (
          <div className="mt-8 rounded-2xl border border-dashed border-slate-800 bg-slate-900/50 p-12 text-center">
            <div className="text-4xl">📊</div>

            <h2 className="mt-4 text-xl font-semibold">
              Ready to Backtest
            </h2>

            <p className="mx-auto mt-2 max-w-lg text-slate-400">
              Enter an NSE stock symbol, choose a historical
              period and run MarketIQ&apos;s backtesting engine.
            </p>

            <button
              onClick={runBacktest}
              className="mt-6 rounded-xl border border-slate-700 bg-slate-900 px-5 py-3 text-sm font-semibold text-cyan-400 transition hover:border-cyan-500"
            >
              Run RELIANCE Backtest
            </button>
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
  icon,
  positive = false,
  negative = false,
}: {
  title: string;
  value: any;
  icon: string;
  positive?: boolean;
  negative?: boolean;
}) {
  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
      <div className="flex items-center justify-between">
        <p className="text-sm text-slate-400">
          {title}
        </p>

        <span className="text-lg">
          {icon}
        </span>
      </div>

      <p
        className={`mt-3 text-2xl font-bold ${
          positive
            ? "text-emerald-400"
            : negative
            ? "text-red-400"
            : "text-white"
        }`}
      >
        {value}
      </p>
    </div>
  );
}

/* ============================================================
   MINI METRIC
============================================================ */

function MiniMetric({
  label,
  value,
  negative = false,
}: {
  label: string;
  value: any;
  negative?: boolean;
}) {
  return (
    <div className="rounded-xl border border-slate-800 bg-slate-950 p-4">
      <p className="text-xs text-slate-500">
        {label}
      </p>

      <p
        className={`mt-1 font-semibold ${
          negative
            ? "text-red-400"
            : "text-white"
        }`}
      >
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
  valueClass = "text-white",
}: {
  label: string;
  value: any;
  valueClass?: string;
}) {
  return (
    <div className="flex items-center justify-between gap-4 border-b border-slate-800 pb-3 last:border-0">
      <span className="text-sm text-slate-400">
        {label}
      </span>

      <span className={`font-semibold ${valueClass}`}>
        {value}
      </span>
    </div>
  );
}

/* ============================================================
   SIGNAL BAR
============================================================ */

function SignalBar({
  label,
  value,
  total,
}: {
  label: string;
  value: number;
  total: number;
}) {
  const percentage =
    total > 0
      ? Math.min((value / total) * 100, 100)
      : 0;

  const textClass =
    label === "BUY"
      ? "text-emerald-400"
      : label === "SELL"
      ? "text-red-400"
      : "text-slate-300";

  return (
    <div className="mb-4 last:mb-0">
      <div className="mb-2 flex justify-between text-xs">
        <span className={`font-semibold ${textClass}`}>
          {label}
        </span>

        <span className="text-slate-500">
          {value}
        </span>
      </div>

      <div className="h-2 overflow-hidden rounded-full bg-slate-800">
        <div
          className={`h-full rounded-full ${
            label === "BUY"
              ? "bg-emerald-500"
              : label === "SELL"
              ? "bg-red-500"
              : "bg-slate-500"
          }`}
          style={{
            width: `${percentage}%`,
          }}
        />
      </div>
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

  const profit = Number(trade.profit_loss);

  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">

      <div className="mb-5 flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold">
            {title}
          </h3>

          <p className="mt-1 text-xs text-slate-500">
            {trade.date || "Unknown date"}
          </p>
        </div>

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

      <div className="mb-5 rounded-xl border border-slate-800 bg-slate-950 p-4">
        <div className="flex items-center justify-between">
          <span className="text-sm text-slate-400">
            Profit / Loss
          </span>

          <span
            className={`text-xl font-bold ${
              profit >= 0
                ? "text-emerald-400"
                : "text-red-400"
            }`}
          >
            {formatCurrency(trade.profit_loss)}
          </span>
        </div>
      </div>

      <div className="space-y-4">
        <ResultRow
          label="Action"
          value={trade.action || "—"}
          valueClass={
            trade.action === "BUY"
              ? "text-emerald-400"
              : trade.action === "SELL"
              ? "text-red-400"
              : "text-white"
          }
        />

        <ResultRow
          label="Entry Price"
          value={formatCurrency(trade.entry_price)}
        />

        <ResultRow
          label="Exit Price"
          value={formatCurrency(trade.exit_price)}
        />

        <ResultRow
          label="Return"
          value={formatPercent(trade.return_percent)}
          valueClass={
            Number(trade.return_percent) >= 0
              ? "text-emerald-400"
              : "text-red-400"
          }
        />

        <ResultRow
          label="Confidence"
          value={formatPercent(trade.confidence)}
        />

        <ResultRow
          label="Signal Score"
          value={formatNumber(trade.score, 0)}
        />
      </div>
    </div>
  );
}

/* ============================================================
   EQUITY CHART
   No external chart library required.
============================================================ */

function EquityChart({
  data,
  initialCapital,
}: {
  data: EquityPoint[];
  initialCapital: number;
}) {
  const width = 1000;
  const height = 320;
  const paddingLeft = 60;
  const paddingRight = 20;
  const paddingTop = 20;
  const paddingBottom = 45;

  const values = data
    .map((point) => Number(point.capital))
    .filter(Number.isFinite);

  if (values.length < 2) {
    return null;
  }

  const minValue = Math.min(
    ...values,
    initialCapital
  );

  const maxValue = Math.max(
    ...values,
    initialCapital
  );

  const range =
    maxValue - minValue === 0
      ? 1
      : maxValue - minValue;

  const xStep =
    (width - paddingLeft - paddingRight) /
    Math.max(values.length - 1, 1);

  const getX = (index: number) =>
    paddingLeft + index * xStep;

  const getY = (value: number) =>
    paddingTop +
    (1 - (value - minValue) / range) *
      (height - paddingTop - paddingBottom);

  const points = values
    .map(
      (value, index) =>
        `${getX(index)},${getY(value)}`
    )
    .join(" ");

  const initialY = getY(initialCapital);

  const areaPoints = [
    `${paddingLeft},${height - paddingBottom}`,
    points,
    `${getX(values.length - 1)},${
      height - paddingBottom
    }`,
  ].join(" ");

  const firstDate =
    data[0]?.date || "";

  const lastDate =
    data[data.length - 1]?.date || "";

  return (
    <div className="mt-6">

      <div className="overflow-x-auto">
        <div className="min-w-[700px]">
          <svg
            viewBox={`0 0 ${width} ${height}`}
            className="h-[320px] w-full"
            preserveAspectRatio="none"
          >

            {/* GRID */}

            {[0, 1, 2, 3, 4].map((step) => {
              const y =
                paddingTop +
                (step / 4) *
                  (height -
                    paddingTop -
                    paddingBottom);

              const value =
                maxValue -
                (step / 4) * range;

              return (
                <g key={step}>
                  <line
                    x1={paddingLeft}
                    x2={width - paddingRight}
                    y1={y}
                    y2={y}
                    stroke="currentColor"
                    className="text-slate-800"
                    strokeWidth="1"
                  />

                  <text
                    x="5"
                    y={y + 4}
                    className="fill-slate-500 text-[12px]"
                  >
                    ₹
                    {Math.round(value).toLocaleString(
                      "en-IN"
                    )}
                  </text>
                </g>
              );
            })}

            {/* INITIAL CAPITAL LINE */}

            <line
              x1={paddingLeft}
              x2={width - paddingRight}
              y1={initialY}
              y2={initialY}
              stroke="currentColor"
              className="text-slate-600"
              strokeDasharray="6 6"
            />

            {/* EQUITY AREA */}

            <polygon
              points={areaPoints}
              className="fill-cyan-500/5"
            />

            {/* EQUITY LINE */}

            <polyline
              points={points}
              fill="none"
              stroke="currentColor"
              className="text-cyan-400"
              strokeWidth="3"
              strokeLinejoin="round"
              strokeLinecap="round"
            />

            {/* START POINT */}

            <circle
              cx={getX(0)}
              cy={getY(values[0])}
              r="5"
              className="fill-cyan-400"
            />

            {/* END POINT */}

            <circle
              cx={getX(values.length - 1)}
              cy={getY(values[values.length - 1])}
              r="6"
              className="fill-cyan-400"
            />

            {/* INITIAL CAPITAL LABEL */}

            <text
              x={width - 170}
              y={initialY - 8}
              className="fill-slate-500 text-[11px]"
            >
              Initial Capital
            </text>

            {/* DATE LABELS */}

            <text
              x={paddingLeft}
              y={height - 15}
              className="fill-slate-500 text-[11px]"
            >
              {firstDate}
            </text>

            <text
              x={width - paddingRight}
              y={height - 15}
              textAnchor="end"
              className="fill-slate-500 text-[11px]"
            >
              {lastDate}
            </text>
          </svg>
        </div>
      </div>

      {/* CHART LEGEND */}

      <div className="mt-4 flex flex-wrap gap-5 text-xs text-slate-400">
        <div className="flex items-center gap-2">
          <span className="h-2 w-5 rounded-full bg-cyan-400" />
          Portfolio Equity
        </div>

        <div className="flex items-center gap-2">
          <span className="h-0.5 w-5 border-t border-dashed border-slate-500" />
          Initial Capital
        </div>
      </div>
    </div>
  );
}