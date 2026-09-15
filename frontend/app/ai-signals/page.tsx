"use client";

import { useEffect, useState } from "react";
import DashboardLayout from "@/components/dashboard/DashboardLayout";
import useStock from "@/hooks/useStock";

function num(value: unknown) {
  const n = Number(value);
  if (!Number.isFinite(n)) return "—";
  return n.toFixed(2);
}

function money(value: unknown) {
  const n = Number(value);

  if (!Number.isFinite(n)) return "—";

  return `₹${n.toLocaleString("en-IN", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}`;
}

export default function AISignalsPage() {
  const [symbol, setSymbol] = useState("RELIANCE");
  const [input, setInput] = useState("RELIANCE");

  useEffect(() => {
    const saved =
      typeof window !== "undefined"
        ? localStorage.getItem(
            "marketiq_selected_stock"
          )
        : null;

    if (saved?.trim()) {
      const clean = saved.trim().toUpperCase();

      setSymbol(clean);
      setInput(clean);
    }
  }, []);

  const {
    data,
    loading,
    refreshing,
    error,
    refreshStock,
  } = useStock(symbol);

  const analyse = () => {
    const clean = input.trim().toUpperCase();

    if (!clean) return;

    setSymbol(clean);

    if (typeof window !== "undefined") {
      localStorage.setItem(
        "marketiq_selected_stock",
        clean
      );
    }
  };

  const recommendation = data?.recommendation as any;
  const explanation =
    recommendation?.v7_explanation;

  const setupApproved =
    explanation?.trade_setup_approved === true ||
    recommendation?.trade_quality === "APPROVED";

  const action =
    String(
      recommendation?.recommendation || "HOLD"
    ).toUpperCase();

  const actionClass =
    action === "BUY"
      ? "text-emerald-400"
      : action === "SELL"
        ? "text-red-400"
        : "text-amber-400";

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* HEADER */}
        <div>
          <h1 className="text-2xl font-bold text-white">
            AI Signals
          </h1>

          <p className="mt-1 text-sm text-slate-400">
            MarketIQ BUY, SELL and HOLD decisions with
            confidence, evidence and tradeability.
          </p>
        </div>

        {/* SEARCH */}
        <section className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
          <div className="flex flex-col gap-3 md:flex-row">
            <input
              value={input}
              onChange={(event) =>
                setInput(event.target.value.toUpperCase())
              }
              onKeyDown={(event) => {
                if (event.key === "Enter") {
                  analyse();
                }
              }}
              className="flex-1 rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none focus:border-blue-500"
              placeholder="RELIANCE"
            />

            <button
              type="button"
              onClick={analyse}
              disabled={loading || !input.trim()}
              className="rounded-xl bg-blue-600 px-6 py-3 font-semibold text-white hover:bg-blue-500 disabled:opacity-50"
            >
              {loading ? "Analysing..." : "Generate AI Signal"}
            </button>

            <button
              type="button"
              onClick={() => refreshStock()}
              disabled={!data || loading || refreshing}
              className="rounded-xl border border-slate-700 bg-slate-950 px-5 py-3 text-white hover:bg-slate-800 disabled:opacity-50"
            >
              {refreshing ? "Refreshing..." : "Refresh"}
            </button>
          </div>
        </section>

        {error && (
          <section className="rounded-2xl border border-red-900/50 bg-red-950/30 p-5">
            <p className="font-semibold text-red-300">
              AI analysis failed
            </p>

            <p className="mt-1 text-sm text-red-200">
              {error}
            </p>
          </section>
        )}

        {loading && (
          <section className="rounded-2xl border border-slate-800 bg-slate-900 p-10 text-center">
            <div className="mx-auto h-10 w-10 animate-spin rounded-full border-4 border-slate-700 border-t-blue-500" />

            <p className="mt-4 text-white">
              MarketIQ is generating the signal...
            </p>
          </section>
        )}

        {data && !loading && (
          <>
            {/* MAIN SIGNAL */}
            <section className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
              <div className="flex flex-col justify-between gap-6 md:flex-row md:items-center">
                <div>
                  <p className="text-sm text-slate-400">
                    {data.symbol} · MarketIQ AI Signal
                  </p>

                  <h2
                    className={`mt-2 text-5xl font-black ${actionClass}`}
                  >
                    {action}
                  </h2>

                  <p className="mt-3 text-slate-400">
                    Current Price:{" "}
                    <span className="font-semibold text-white">
                      {money(data.price)}
                    </span>
                  </p>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <Metric
                    title="Confidence"
                    value={`${num(
                      recommendation?.confidence
                    )}%`}
                  />

                  <Metric
                    title="Score"
                    value={num(
                      recommendation?.score
                    )}
                  />

                  <Metric
                    title="Signal Confidence"
                    value={`${num(
                      recommendation?.signal_confidence
                    )}%`}
                  />

                  <Metric
                    title="Trade Quality"
                    value={
                      recommendation?.trade_quality ||
                      "—"
                    }
                  />
                </div>
              </div>
            </section>

            {/* TRADEABILITY */}
            <section className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
              <h2 className="text-lg font-semibold text-white">
                Tradeability
              </h2>

              <div
                className={`mt-4 rounded-xl border p-5 ${
                  setupApproved
                    ? "border-emerald-800 bg-emerald-950/20"
                    : "border-amber-800 bg-amber-950/20"
                }`}
              >
                <p
                  className={`font-semibold ${
                    setupApproved
                      ? "text-emerald-300"
                      : "text-amber-300"
                  }`}
                >
                  {setupApproved
                    ? "Trade Setup Approved"
                    : "Trade Setup Not Approved"}
                </p>

                <p className="mt-2 text-sm text-slate-300">
                  {setupApproved
                    ? "MarketIQ has accepted the directional signal as a tradeable setup."
                    : action === "HOLD"
                      ? "MarketIQ is avoiding a forced directional trade."
                      : "A directional signal may exist, but the complete trade setup did not pass the risk checks."}
                </p>
              </div>

              <div className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
                <Metric
                  title="Entry"
                  value={money(
                    recommendation?.entry_price
                  )}
                />

                <Metric
                  title="Stop Loss"
                  value={money(
                    recommendation?.stop_loss
                  )}
                />

                <Metric
                  title="Target"
                  value={money(
                    recommendation?.target
                  )}
                />

                <Metric
                  title="Risk : Reward"
                  value={
                    recommendation?.risk_reward
                      ? `1:${num(
                          recommendation.risk_reward
                        )}`
                      : "—"
                  }
                />
              </div>
            </section>

            {/* V7.1 EXPLANATION */}
            <section className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
              <div className="flex items-center gap-3">
                <h2 className="text-lg font-semibold text-white">
                  Why AI gave this signal
                </h2>

                {explanation?.version && (
                  <span className="rounded-full border border-blue-800 bg-blue-950/30 px-2 py-1 text-xs font-semibold text-blue-300">
                    {explanation.version}
                  </span>
                )}
              </div>

              <div className="mt-4 rounded-xl bg-slate-950 p-5">
                <p className="font-semibold text-white">
                  {explanation?.primary ||
                    `MarketIQ recommendation: ${action}`}
                </p>

                {explanation?.summary && (
                  <p className="mt-2 text-sm leading-6 text-slate-400">
                    {explanation.summary}
                  </p>
                )}
              </div>

              {Array.isArray(
                explanation?.hierarchy
              ) &&
                explanation.hierarchy.length > 0 && (
                  <div className="mt-5">
                    <p className="mb-3 text-sm font-semibold text-white">
                      Decision Hierarchy
                    </p>

                    <div className="grid gap-2 md:grid-cols-5">
                      {explanation.hierarchy.map(
                        (item: string, index: number) => (
                          <div
                            key={index}
                            className="rounded-lg border border-slate-800 bg-slate-950 p-3 text-center text-xs text-slate-300"
                          >
                            {index + 1}. {item}
                          </div>
                        )
                      )}
                    </div>
                  </div>
                )}

              {explanation?.signal_conflict !==
                undefined && (
                <div className="mt-5 rounded-xl border border-slate-800 bg-slate-950 p-4">
                  <p className="text-sm font-semibold text-white">
                    Signal Conflict
                  </p>

                  <p className="mt-1 text-sm text-slate-400">
                    {typeof explanation.signal_conflict ===
                    "string"
                      ? explanation.signal_conflict
                      : explanation.signal_conflict
                        ? "Directional signals conflict."
                        : "No major directional conflict detected."}
                  </p>
                </div>
              )}
            </section>

            {/* LAYERS */}
            {explanation?.layers && (
              <section className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
                <h2 className="text-lg font-semibold text-white">
                  AI Evidence Layers
                </h2>

                <div className="mt-4 space-y-3">
                  {[
                    [
                      "Market Structure",
                      explanation.layers
                        .market_structure,
                    ],
                    [
                      "Technical Trend & Momentum",
                      explanation.layers
                        .technical_trend_momentum,
                    ],
                    [
                      "Smart Money Concepts",
                      explanation.layers.smc,
                    ],
                    [
                      "Support & Resistance",
                      explanation.layers
                        .support_resistance,
                    ],
                    [
                      "Candlestick",
                      explanation.layers.candlestick,
                    ],
                  ].map(([title, text]) => (
                    <div
                      key={title}
                      className="rounded-xl border border-slate-800 bg-slate-950 p-4"
                    >
                      <p className="text-sm font-semibold text-white">
                        {title}
                      </p>

                      <p className="mt-1 text-sm leading-6 text-slate-400">
                        {text || "No additional explanation available."}
                      </p>
                    </div>
                  ))}
                </div>
              </section>
            )}

            {/* BULLISH / BEARISH FACTORS */}
            <section className="grid gap-5 lg:grid-cols-2">
              <FactorList
                title="Bullish Factors"
                factors={
                  Array.isArray(
                    recommendation?.bullish_factors
                  )
                    ? recommendation.bullish_factors
                    : []
                }
              />

              <FactorList
                title="Bearish Factors"
                factors={
                  Array.isArray(
                    recommendation?.bearish_factors
                  )
                    ? recommendation.bearish_factors
                    : []
                }
              />
            </section>

            {/* BASIC FALLBACK REASONS */}
            {Array.isArray(
              recommendation?.reasons
            ) &&
              recommendation.reasons.length > 0 && (
                <section className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
                  <h2 className="text-lg font-semibold text-white">
                    Additional AI Reasons
                  </h2>

                  <div className="mt-4 space-y-2">
                    {recommendation.reasons.map(
                      (reason: string, index: number) => (
                        <p
                          key={index}
                          className="rounded-lg bg-slate-950 px-4 py-3 text-sm text-slate-300"
                        >
                          • {reason}
                        </p>
                      )
                    )}
                  </div>
                </section>
              )}
          </>
        )}

        {!data && !loading && !error && (
          <section className="rounded-2xl border border-dashed border-slate-700 p-10 text-center">
            <p className="text-slate-400">
              Generate an AI signal to view MarketIQ's
              decision analysis.
            </p>
          </section>
        )}
      </div>
    </DashboardLayout>
  );
}

function Metric({
  title,
  value,
}: {
  title: string;
  value: string;
}) {
  return (
    <div className="rounded-xl border border-slate-800 bg-slate-950 p-4">
      <p className="text-xs uppercase tracking-wide text-slate-500">
        {title}
      </p>

      <p className="mt-2 text-lg font-bold text-white">
        {value}
      </p>
    </div>
  );
}

function FactorList({
  title,
  factors,
}: {
  title: string;
  factors: unknown[];
}) {
  return (
    <section className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
      <h2 className="text-lg font-semibold text-white">
        {title}
      </h2>

      {factors.length === 0 ? (
        <p className="mt-4 text-sm text-slate-500">
          No factors available.
        </p>
      ) : (
        <div className="mt-4 space-y-2">
          {factors.map((factor, index) => (
            <p
              key={index}
              className="rounded-lg bg-slate-950 px-4 py-3 text-sm text-slate-300"
            >
              • {String(factor)}
            </p>
          ))}
        </div>
      )}
    </section>
  );
}