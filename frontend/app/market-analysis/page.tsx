"use client";

import { useEffect, useState } from "react";
import DashboardLayout from "@/components/dashboard/DashboardLayout";
import useStock from "@/hooks/useStock";

function money(value: unknown) {
  const n = Number(value);

  if (!Number.isFinite(n)) return "—";

  return `₹${n.toLocaleString("en-IN", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}`;
}

function num(value: unknown) {
  const n = Number(value);

  if (!Number.isFinite(n)) return "—";

  return n.toFixed(2);
}

function status(value: unknown) {
  const text = String(value || "—").toUpperCase();

  if (text.includes("BULL") || text.includes("BUY")) {
    return "Bullish";
  }

  if (text.includes("BEAR") || text.includes("SELL")) {
    return "Bearish";
  }

  return text;
}

export default function MarketAnalysisPage() {
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

  const marketStructure =
    data?.market_structure;

  const supportResistance =
    data?.support_resistance;

  const pattern = data?.pattern;

  const smc = data?.smc as any;

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* HEADER */}
        <div>
          <h1 className="text-2xl font-bold text-white">
            Market Analysis
          </h1>

          <p className="mt-1 text-sm text-slate-400">
            Technical trend, momentum, market structure,
            support/resistance and Smart Money Concepts.
          </p>
        </div>

        {/* STOCK SELECTOR */}
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
              className="rounded-xl bg-blue-600 px-6 py-3 font-semibold text-white hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {loading ? "Analysing..." : "Analyse"}
            </button>

            <button
              type="button"
              onClick={() => refreshStock()}
              disabled={loading || refreshing || !data}
              className="rounded-xl border border-slate-700 bg-slate-950 px-5 py-3 font-semibold text-slate-200 hover:bg-slate-800 disabled:opacity-50"
            >
              {refreshing ? "Refreshing..." : "Refresh"}
            </button>
          </div>
        </section>

        {error && (
          <section className="rounded-2xl border border-red-900/50 bg-red-950/30 p-5">
            <p className="font-semibold text-red-300">
              Market analysis failed
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
              Analysing {symbol}...
            </p>
          </section>
        )}

        {data && !loading && (
          <>
            {/* STOCK HEADER */}
            <section className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
              <div className="flex flex-col justify-between gap-4 md:flex-row md:items-center">
                <div>
                  <h2 className="text-2xl font-bold text-white">
                    {data.symbol}
                  </h2>

                  <p className="mt-1 text-sm text-slate-400">
                    {data.exchange || "NSE / BSE"}
                  </p>
                </div>

                <div>
                  <p className="text-sm text-slate-400">
                    Current Price
                  </p>

                  <p className="text-3xl font-bold text-white">
                    {money(data.price)}
                  </p>
                </div>
              </div>
            </section>

            {/* INDICATORS */}
            <section>
              <h2 className="mb-3 text-lg font-semibold text-white">
                Technical Indicators
              </h2>

              <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
                {[
                  [
                    "RSI (14)",
                    num(data.indicators?.RSI),
                    "Momentum",
                  ],
                  [
                    "EMA 20",
                    money(data.indicators?.EMA20),
                    data.price >=
                    Number(data.indicators?.EMA20)
                      ? "Above"
                      : "Below",
                  ],
                  [
                    "EMA 50",
                    money(data.indicators?.EMA50),
                    data.price >=
                    Number(data.indicators?.EMA50)
                      ? "Above"
                      : "Below",
                  ],
                  [
                    "MACD",
                    num(data.indicators?.MACD),
                    Number(data.indicators?.MACD) >=
                    Number(
                      data.indicators?.MACD_SIGNAL
                    )
                      ? "Bullish"
                      : "Bearish",
                  ],
                ].map(([title, value, subtitle]) => (
                  <div
                    key={title}
                    className="rounded-2xl border border-slate-800 bg-slate-900 p-5"
                  >
                    <p className="text-sm text-slate-400">
                      {title}
                    </p>

                    <p className="mt-2 text-2xl font-bold text-white">
                      {value}
                    </p>

                    <p className="mt-1 text-xs text-slate-500">
                      {subtitle}
                    </p>
                  </div>
                ))}
              </div>
            </section>

            {/* MARKET STRUCTURE */}
            <section className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
              <h2 className="text-lg font-semibold text-white">
                Market Structure
              </h2>

              <div className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
                <AnalysisBox
                  title="Structure"
                  value={status(marketStructure?.structure)}
                />

                <AnalysisBox
                  title="Trend"
                  value={status(marketStructure?.trend)}
                />

                <AnalysisBox
                  title="Signal"
                  value={status(marketStructure?.signal)}
                />

                <AnalysisBox
                  title="Confidence"
                  value={`${num(
                    marketStructure?.confidence
                  )}%`}
                />
              </div>

              {Array.isArray(marketStructure?.reasons) &&
                marketStructure.reasons.length > 0 && (
                  <div className="mt-5 space-y-2">
                    {marketStructure.reasons
                      .slice(0, 6)
                      .map((reason, index) => (
                        <p
                          key={index}
                          className="rounded-lg bg-slate-950 px-3 py-2 text-sm text-slate-300"
                        >
                          • {reason}
                        </p>
                      ))}
                  </div>
                )}
            </section>

            {/* SUPPORT RESISTANCE */}
            <section className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
              <h2 className="text-lg font-semibold text-white">
                Support & Resistance
              </h2>

              <div className="mt-4 grid gap-4 md:grid-cols-2">
                <div className="rounded-xl border border-slate-800 bg-slate-950 p-5">
                  <p className="text-sm text-slate-400">
                    Nearest Support
                  </p>

                  <p className="mt-2 text-2xl font-bold text-white">
                    {money(
                      Array.isArray(
                        supportResistance?.support
                      )
                        ? supportResistance.support[
                            supportResistance.support.length - 1
                          ]
                        : null
                    )}
                  </p>
                </div>

                <div className="rounded-xl border border-slate-800 bg-slate-950 p-5">
                  <p className="text-sm text-slate-400">
                    Nearest Resistance
                  </p>

                  <p className="mt-2 text-2xl font-bold text-white">
                    {money(
                      Array.isArray(
                        supportResistance?.resistance
                      )
                        ? supportResistance.resistance[0]
                        : null
                    )}
                  </p>
                </div>
              </div>
            </section>

            {/* CANDLESTICK */}
            <section className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
              <h2 className="text-lg font-semibold text-white">
                Candlestick Pattern
              </h2>

              <div className="mt-4 grid gap-4 sm:grid-cols-3">
                <AnalysisBox
                  title="Pattern"
                  value={pattern?.pattern || "—"}
                />

                <AnalysisBox
                  title="Signal"
                  value={status(pattern?.signal)}
                />

                <AnalysisBox
                  title="Confidence"
                  value={`${num(
                    pattern?.confidence
                  )}%`}
                />
              </div>
            </section>

            {/* SMC */}
            <section className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
              <h2 className="text-lg font-semibold text-white">
                Smart Money Concepts
              </h2>

              <div className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
                <AnalysisBox
                  title="Signal"
                  value={status(smc?.signal)}
                />

                <AnalysisBox
                  title="Confidence"
                  value={`${num(
                    smc?.confidence
                  )}%`}
                />

                <AnalysisBox
                  title="Market Bias"
                  value={status(
                    smc?.market_bias || smc?.trend
                  )}
                />

                <AnalysisBox
                  title="Structure"
                  value={status(smc?.structure)}
                />
              </div>

              {Array.isArray(smc?.reasons) &&
                smc.reasons.length > 0 && (
                  <div className="mt-5 space-y-2">
                    {smc.reasons
                      .slice(0, 8)
                      .map((reason: string, index: number) => (
                        <p
                          key={index}
                          className="rounded-lg bg-slate-950 px-3 py-2 text-sm text-slate-300"
                        >
                          • {reason}
                        </p>
                      ))}
                  </div>
                )}
            </section>
          </>
        )}

        {!data && !loading && !error && (
          <section className="rounded-2xl border border-dashed border-slate-700 p-10 text-center">
            <p className="text-slate-400">
              Analyse a stock to view MarketIQ market analysis.
            </p>
          </section>
        )}
      </div>
    </DashboardLayout>
  );
}

function AnalysisBox({
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

      <p className="mt-2 text-lg font-semibold text-white">
        {value}
      </p>
    </div>
  );
}