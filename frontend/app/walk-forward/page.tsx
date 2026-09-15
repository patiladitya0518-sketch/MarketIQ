"use client";

import { useEffect, useState } from "react";
import api from "@/lib/api";

interface OOSResult {
  success?: boolean;
  validation?: string;
  version?: string;
  symbol?: string;
  period?: string;
  test_window?: {
    start_date?: string;
    end_date?: string;
    start_source?: string;
    oos_ratio?: number;
  };
  frozen_strategy?: {
    minimum_rank?: string;
    minimum_confidence?: number;
    minimum_risk_reward?: number;
    position_size_percent?: number;
    max_holding_days?: number;
    sl_target_unchanged?: boolean;
    recommendation_engine_unchanged?: boolean;
  };
  out_of_sample?: {
    total_trades?: number;
    winning_trades?: number;
    losing_trades?: number;
    flat_trades?: number;
    win_rate?: number;
    total_return?: number;
    max_drawdown?: number;
    net_profit_loss?: number;
    average_trade_return?: number;
    profit_factor?: number | null;
    prediction_accuracy?: number;
    exit_reason_breakdown?: Record<string, number>;
  };
  methodology?: {
    type?: string;
    signal_data_rule?: string;
    entry_rule?: string;
    oos_rule?: string;
    boundary_rule?: string;
    strategy_tuning_during_test?: boolean;
    status?: string;
  };
  trades?: any[];
  backtest_warnings?: number;
  message?: string;
}

const formatNumber = (value: any, decimals = 2) => {
  const number = Number(value);
  if (!Number.isFinite(number)) return "—";
  return number.toFixed(decimals);
};

const formatCurrency = (value: any) => {
  const number = Number(value);
  if (!Number.isFinite(number)) return "—";
  return `₹${number.toLocaleString("en-IN", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}`;
};

const formatPercent = (value: any) => {
  const number = Number(value);
  if (!Number.isFinite(number)) return "—";
  return `${number.toFixed(2)}%`;
};

function MetricCard({
  label,
  value,
  detail,
}: {
  label: string;
  value: string;
  detail?: string;
}) {
  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
      <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
        {label}
      </p>
      <p className="mt-2 text-2xl font-bold text-white">{value}</p>
      {detail ? (
        <p className="mt-1 text-xs text-slate-500">{detail}</p>
      ) : null}
    </div>
  );
}

export default function WalkForwardPage() {
  const [symbol, setSymbol] = useState("RELIANCE");
  const [period, setPeriod] = useState("5y");
  const [oosRatio, setOosRatio] = useState("0.40");
  const [testStart, setTestStart] = useState("");
  const [testEnd, setTestEnd] = useState("");
  const [result, setResult] = useState<OOSResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [elapsedSeconds, setElapsedSeconds] = useState(0);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!loading) return;
    const startedAt = Date.now();
    const timer = window.setInterval(() => {
      setElapsedSeconds(Math.floor((Date.now() - startedAt) / 1000));
    }, 1000);
    return () => window.clearInterval(timer);
  }, [loading]);

  const runValidation = async () => {
    if (loading) return;

    const cleanSymbol = symbol.trim().toUpperCase();
    if (!cleanSymbol) {
      setError("Please enter a stock symbol.");
      return;
    }

    const ratio = Number(oosRatio);
    if (!Number.isFinite(ratio) || ratio < 0.2 || ratio > 0.6) {
      setError("OOS ratio must be between 0.20 and 0.60.");
      return;
    }

    try {
      setLoading(true);
      setError(null);
      setResult(null);
      setElapsedSeconds(0);

      const params: Record<string, string | number> = {
        period,
        oos_ratio: ratio,
      };

      if (testStart.trim()) params.test_start_date = testStart.trim();
      if (testEnd.trim()) params.test_end_date = testEnd.trim();

      const response = await api.get(
        `/backtest/walk-forward/${encodeURIComponent(cleanSymbol)}`,
        {
          params,
          timeout:
            period === "5y"
              ? 15 * 60 * 1000
              : period === "2y"
              ? 10 * 60 * 1000
              : 5 * 60 * 1000,
        }
      );

      const data = response?.data as OOSResult;
      if (!data) {
        setError("Backend returned an empty response.");
        return;
      }

      if (data.success === false) {
        setError(data.message || "Unable to run OOS validation.");
        return;
      }

      setResult(data);
    } catch (err: any) {
      console.error(
        "Walk-forward validation error:",
        err?.response?.data || err?.message || err
      );
      setError(
        err?.response?.data?.detail ||
          err?.response?.data?.message ||
          err?.message ||
          "Failed to run out-of-sample validation."
      );
    } finally {
      setLoading(false);
    }
  };

  const oos = result?.out_of_sample;
  const windowInfo = result?.test_window;
  const strategy = result?.frozen_strategy;
  const methodology = result?.methodology;
  const exits = oos?.exit_reason_breakdown || {};

  return (
    <main className="min-h-screen bg-slate-950 px-6 py-10 text-white">
      <div className="mx-auto max-w-7xl">
        <div className="mb-8">
          <p className="mb-2 text-sm font-medium text-cyan-400">MarketIQ</p>
          <h1 className="text-3xl font-bold">V3 Out-of-Sample Validation</h1>
          <p className="mt-2 max-w-3xl text-slate-400">
            Test the frozen MarketIQ V3 strategy on an unseen historical window.
            This validation does not tune or modify the strategy.
          </p>
        </div>

        <section className="rounded-2xl border border-slate-800 bg-slate-900 p-6 shadow-xl">
          <div className="grid gap-5 md:grid-cols-5">
            <div>
              <label className="mb-2 block text-sm text-slate-300">Stock</label>
              <input
                value={symbol}
                onChange={(e) => setSymbol(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter") runValidation();
                }}
                className="w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 outline-none focus:border-cyan-500"
                placeholder="RELIANCE"
              />
            </div>

            <div>
              <label className="mb-2 block text-sm text-slate-300">Period</label>
              <select
                value={period}
                onChange={(e) => setPeriod(e.target.value)}
                className="w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 outline-none focus:border-cyan-500"
              >
                <option value="6mo">6 Months</option>
                <option value="1y">1 Year</option>
                <option value="2y">2 Years</option>
                <option value="5y">5 Years</option>
              </select>
            </div>

            <div>
              <label className="mb-2 block text-sm text-slate-300">OOS Ratio</label>
              <input
                type="number"
                min="0.20"
                max="0.60"
                step="0.05"
                value={oosRatio}
                onChange={(e) => setOosRatio(e.target.value)}
                className="w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 outline-none focus:border-cyan-500"
              />
            </div>

            <div>
              <label className="mb-2 block text-sm text-slate-300">Test Start (optional)</label>
              <input
                type="date"
                value={testStart}
                onChange={(e) => setTestStart(e.target.value)}
                className="w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 outline-none focus:border-cyan-500"
              />
            </div>

            <div>
              <label className="mb-2 block text-sm text-slate-300">Test End (optional)</label>
              <input
                type="date"
                value={testEnd}
                onChange={(e) => setTestEnd(e.target.value)}
                className="w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 outline-none focus:border-cyan-500"
              />
            </div>
          </div>

          <button
            type="button"
            onClick={runValidation}
            disabled={loading}
            className="mt-6 rounded-xl bg-cyan-500 px-6 py-3 font-semibold text-slate-950 transition hover:bg-cyan-400 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {loading ? "Running OOS Validation…" : "Run OOS Validation"}
          </button>

          {loading ? (
            <div className="mt-4 rounded-xl border border-cyan-900/50 bg-cyan-950/20 p-4 text-sm text-cyan-300">
              V3 is evaluating unseen candles. Elapsed: {elapsedSeconds}s. Do not change the strategy while this test is running.
            </div>
          ) : null}

          {error ? (
            <div className="mt-4 rounded-xl border border-red-900/50 bg-red-950/30 p-4 text-sm text-red-300">
              {error}
            </div>
          ) : null}
        </section>

        {result ? (
          <div className="mt-8 space-y-6">
            <section className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div>
                  <p className="text-xs uppercase tracking-wide text-cyan-400">Validation Result</p>
                  <h2 className="mt-1 text-2xl font-bold">
                    {result.symbol} · {result.period}
                  </h2>
                </div>
                <span className="rounded-full border border-emerald-800 bg-emerald-950/30 px-4 py-2 text-sm font-semibold text-emerald-300">
                  {methodology?.status || "COMPLETED"}
                </span>
              </div>

              <div className="mt-5 grid gap-4 md:grid-cols-4">
                <MetricCard label="OOS Trades" value={formatNumber(oos?.total_trades, 0)} />
                <MetricCard label="Win Rate" value={formatPercent(oos?.win_rate)} />
                <MetricCard label="OOS Return" value={formatPercent(oos?.total_return)} />
                <MetricCard label="Max Drawdown" value={formatPercent(oos?.max_drawdown)} />
                <MetricCard label="Net P&L" value={formatCurrency(oos?.net_profit_loss)} />
                <MetricCard label="Profit Factor" value={oos?.profit_factor == null ? "—" : formatNumber(oos.profit_factor)} />
                <MetricCard label="Prediction Accuracy" value={formatPercent(oos?.prediction_accuracy)} />
                <MetricCard label="Warnings" value={formatNumber(result.backtest_warnings, 0)} />
              </div>
            </section>

            <section className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
              <h2 className="text-xl font-bold">OOS Window</h2>
              <div className="mt-4 grid gap-4 md:grid-cols-4">
                <MetricCard label="Start" value={windowInfo?.start_date || "—"} />
                <MetricCard label="End" value={windowInfo?.end_date || "—"} />
                <MetricCard label="OOS Ratio" value={formatNumber((windowInfo?.oos_ratio || 0) * 100, 0) + "%"} />
                <MetricCard label="Start Source" value={windowInfo?.start_source || "—"} />
              </div>
            </section>

            <section className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
              <h2 className="text-xl font-bold">Frozen Strategy Controls</h2>
              <div className="mt-4 grid gap-4 md:grid-cols-3">
                <MetricCard label="Minimum Rank" value={strategy?.minimum_rank || "—"} />
                <MetricCard label="Minimum Confidence" value={formatPercent(strategy?.minimum_confidence)} />
                <MetricCard label="Minimum R:R" value={formatNumber(strategy?.minimum_risk_reward)} />
                <MetricCard label="Position Size" value={formatPercent(strategy?.position_size_percent)} />
                <MetricCard label="Max Holding" value={`${formatNumber(strategy?.max_holding_days, 0)} sessions`} />
                <MetricCard label="SL / Target" value={strategy?.sl_target_unchanged ? "UNCHANGED" : "CHECK"} />
              </div>
              <p className="mt-4 text-sm text-slate-400">
                Recommendation engine unchanged: {strategy?.recommendation_engine_unchanged ? "YES" : "NO"}. Strategy tuning during this test: {methodology?.strategy_tuning_during_test ? "YES" : "NO"}.
              </p>
            </section>

            <section className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
              <h2 className="text-xl font-bold">Methodology</h2>
              <div className="mt-4 space-y-3 text-sm text-slate-300">
                <p><strong>Type:</strong> {methodology?.type || "—"}</p>
                <p><strong>Signal rule:</strong> {methodology?.signal_data_rule || "—"}</p>
                <p><strong>Entry rule:</strong> {methodology?.entry_rule || "—"}</p>
                <p><strong>OOS rule:</strong> {methodology?.oos_rule || "—"}</p>
                <p><strong>Boundary rule:</strong> {methodology?.boundary_rule || "—"}</p>
              </div>
            </section>

            <section className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
              <h2 className="text-xl font-bold">Exit Breakdown</h2>
              <div className="mt-4 grid gap-3 md:grid-cols-4">
                {Object.entries(exits).map(([reason, count]) => (
                  <div key={reason} className="rounded-xl border border-slate-800 bg-slate-950 p-4">
                    <p className="text-xs uppercase tracking-wide text-slate-500">{reason}</p>
                    <p className="mt-1 text-xl font-bold">{count}</p>
                  </div>
                ))}
              </div>
            </section>
          </div>
        ) : null}
      </div>
    </main>
  );
}
