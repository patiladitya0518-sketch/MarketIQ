"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
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

function number(value: unknown) {
  const n = Number(value);
  if (!Number.isFinite(n)) return "—";
  return n.toFixed(2);
}

export default function StockSearchPage() {
  const router = useRouter();

  const [input, setInput] = useState("RELIANCE");
  const [symbol, setSymbol] = useState("RELIANCE");

  const {
    data,
    loading,
    refreshing,
    error,
    refreshStock,
  } = useStock(symbol);

  const analyseStock = (event?: FormEvent) => {
    event?.preventDefault();

    const cleanSymbol = input.trim().toUpperCase();

    if (!cleanSymbol) return;

    setSymbol(cleanSymbol);

    if (typeof window !== "undefined") {
      localStorage.setItem("marketiq_selected_stock", cleanSymbol);
    }
  };

  const openFullAnalysis = () => {
    if (typeof window !== "undefined") {
      localStorage.setItem(
        "marketiq_selected_stock",
        symbol
      );
    }

    router.push("/market-analysis");
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* HEADER */}
        <div>
          <h1 className="text-2xl font-bold text-white">
            Stock Search
          </h1>

          <p className="mt-1 text-sm text-slate-400">
            Search and analyse Indian listed stocks using
            MarketIQ AI.
          </p>
        </div>

        {/* SEARCH */}
        <section className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
          <div className="mb-3">
            <h2 className="text-lg font-semibold text-white">
              Search Indian Stock
            </h2>

            <p className="text-sm text-slate-400">
              Enter an NSE/BSE symbol such as RELIANCE, TCS,
              SBIN or INFY.
            </p>
          </div>

          <form
            onSubmit={analyseStock}
            className="flex flex-col gap-3 md:flex-row"
          >
            <input
              value={input}
              onChange={(event) =>
                setInput(event.target.value.toUpperCase())
              }
              placeholder="Enter stock symbol"
              className="flex-1 rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none placeholder:text-slate-500 focus:border-blue-500"
            />

            <button
              type="submit"
              disabled={loading || !input.trim()}
              className="rounded-xl bg-blue-600 px-6 py-3 font-semibold text-white transition hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {loading ? "Analysing..." : "Analyse Stock"}
            </button>
          </form>
        </section>

        {/* ERROR */}
        {error && (
          <section className="rounded-2xl border border-red-900/50 bg-red-950/30 p-5">
            <h2 className="font-semibold text-red-300">
              Unable to analyse stock
            </h2>

            <p className="mt-1 text-sm text-red-200">
              {error}
            </p>
          </section>
        )}

        {/* LOADING */}
        {loading && (
          <section className="rounded-2xl border border-slate-800 bg-slate-900 p-8 text-center">
            <div className="mx-auto h-10 w-10 animate-spin rounded-full border-4 border-slate-700 border-t-blue-500" />

            <p className="mt-4 font-medium text-white">
              MarketIQ is analysing {symbol}
            </p>

            <p className="mt-1 text-sm text-slate-400">
              Loading live market data and AI analysis...
            </p>
          </section>
        )}

        {/* RESULT */}
        {data && !loading && (
          <>
            <section className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
              <div className="flex flex-col justify-between gap-4 md:flex-row md:items-center">
                <div>
                  <div className="flex items-center gap-3">
                    <h2 className="text-2xl font-bold text-white">
                      {data.symbol}
                    </h2>

                    <span className="rounded-full border border-emerald-800 bg-emerald-950/40 px-3 py-1 text-xs font-semibold text-emerald-300">
                      {data.exchange || "NSE / BSE"}
                    </span>
                  </div>

                  <p className="mt-2 text-sm text-slate-400">
                    MarketIQ live stock analysis
                  </p>
                </div>

                <div className="text-left md:text-right">
                  <p className="text-sm text-slate-400">
                    Current Price
                  </p>

                  <p className="text-3xl font-bold text-white">
                    {money(data.price)}
                  </p>

                  <button
                    type="button"
                    onClick={() => refreshStock()}
                    disabled={refreshing}
                    className="mt-2 text-sm text-blue-400 hover:text-blue-300 disabled:opacity-50"
                  >
                    {refreshing ? "Refreshing..." : "Refresh"}
                  </button>
                </div>
              </div>
            </section>

            {/* QUICK INDICATORS */}
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
              {[
                ["RSI", number(data.indicators?.RSI)],
                ["EMA20", money(data.indicators?.EMA20)],
                ["EMA50", money(data.indicators?.EMA50)],
                ["MACD", number(data.indicators?.MACD)],
              ].map(([label, value]) => (
                <div
                  key={label}
                  className="rounded-2xl border border-slate-800 bg-slate-900 p-5"
                >
                  <p className="text-sm text-slate-400">
                    {label}
                  </p>

                  <p className="mt-2 text-2xl font-bold text-white">
                    {value}
                  </p>
                </div>
              ))}
            </div>

            {/* AI RESULT */}
            <section className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
              <div className="flex flex-col justify-between gap-4 md:flex-row md:items-center">
                <div>
                  <p className="text-sm text-slate-400">
                    MarketIQ Recommendation
                  </p>

                  <p className="mt-1 text-3xl font-bold text-white">
                    {data.recommendation?.recommendation || "HOLD"}
                  </p>

                  <p className="mt-1 text-sm text-slate-400">
                    AI score:{" "}
                    {number(data.recommendation?.score)}
                  </p>
                </div>

                <div className="rounded-xl border border-slate-700 bg-slate-950 px-5 py-4">
                  <p className="text-sm text-slate-400">
                    Confidence
                  </p>

                  <p className="mt-1 text-2xl font-bold text-white">
                    {number(
                      data.recommendation?.confidence
                    )}
                    %
                  </p>
                </div>
              </div>

              {Array.isArray(data.recommendation?.reasons) &&
                data.recommendation.reasons.length > 0 && (
                  <div className="mt-5 border-t border-slate-800 pt-5">
                    <p className="mb-3 text-sm font-semibold text-white">
                      Key Reasons
                    </p>

                    <div className="space-y-2">
                      {data.recommendation.reasons
                        .slice(0, 6)
                        .map((reason, index) => (
                          <div
                            key={index}
                            className="rounded-lg bg-slate-950 px-3 py-2 text-sm text-slate-300"
                          >
                            • {reason}
                          </div>
                        ))}
                    </div>
                  </div>
                )}
            </section>

            <button
              type="button"
              onClick={openFullAnalysis}
              className="w-full rounded-xl bg-blue-600 px-5 py-3 font-semibold text-white hover:bg-blue-500"
            >
              Open Full Market Analysis →
            </button>
          </>
        )}

        {/* EMPTY STATE */}
        {!data && !loading && !error && (
          <section className="rounded-2xl border border-dashed border-slate-700 bg-slate-900/50 p-10 text-center">
            <h2 className="text-lg font-semibold text-white">
              Search a stock to begin
            </h2>

            <p className="mt-2 text-sm text-slate-400">
              Enter an Indian listed stock symbol above and
              MarketIQ will analyse it.
            </p>
          </section>
        )}
      </div>
    </DashboardLayout>
  );
}