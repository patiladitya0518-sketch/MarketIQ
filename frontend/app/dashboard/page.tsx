"use client";

import { useState } from "react";

import DashboardLayout from "@/components/dashboard/DashboardLayout";
import MarketCards from "@/components/dashboard/MarketCards";
import MarketSummaryCard from "@/components/dashboard/MarketSummaryCard";
import RecommendationCard from "@/components/dashboard/RecommendationCard";
import IndicatorCard from "@/components/dashboard/IndicatorCard";
import ChartCard from "@/components/dashboard/ChartCard";
import TopMovers from "@/components/dashboard/TopMovers";
import NewsCard from "@/components/dashboard/NewsCard";

import useStock from "@/hooks/useStock";

export default function DashboardPage() {
  const [input, setInput] = useState("RELIANCE");
  const [symbol, setSymbol] = useState("RELIANCE");

  const { data, loading } = useStock(symbol);

  if (loading || !data || !data.recommendation) {
    return (
      <DashboardLayout>
        <div className="flex h-[80vh] items-center justify-center">
          <div className="text-center">
            <div className="mx-auto mb-4 h-12 w-12 animate-spin rounded-full border-4 border-blue-600 border-t-transparent"></div>
            <h2 className="text-2xl font-bold text-white">
              Loading MarketIQ...
            </h2>
            <p className="mt-2 text-slate-400">
              Fetching latest market data
            </p>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>

      {/* Live Market Cards */}
      <MarketCards />

      {/* Market Summary + AI Recommendation */}
      <div className="mt-6 grid gap-6 xl:grid-cols-3">

        <div className="xl:col-span-2">
          <MarketSummaryCard
            symbol={data.symbol}
            price={data.price}
          />
        </div>

        <RecommendationCard
          recommendation={data.recommendation.recommendation}
          confidence={data.recommendation.confidence}
          reasons={data.recommendation.reasons}
        />

      </div>

      {/* Search */}
      <div className="mt-6 rounded-2xl border border-slate-800 bg-slate-900 p-6 shadow-lg">

        <div className="mb-5 flex items-center justify-between">

          <div>
            <h2 className="text-xl font-bold text-white">
              Search Indian Stock
            </h2>

            <p className="text-sm text-slate-400">
              NSE Listed Companies
            </p>
          </div>

        </div>

        <div className="flex flex-col gap-4 md:flex-row">

          <input
            className="flex-1 rounded-xl border border-slate-700 bg-slate-800 px-4 py-3 text-white outline-none transition focus:border-blue-500"
            placeholder="RELIANCE, TCS, INFY..."
            value={input}
            onChange={(e) =>
              setInput(e.target.value.toUpperCase())
            }
          />

          <button
            onClick={() => setSymbol(input)}
            className="rounded-xl bg-blue-600 px-8 py-3 font-semibold text-white transition hover:bg-blue-700"
          >
            Analyse Stock
          </button>

        </div>

      </div>

      {/* TradingView Chart */}
      <div className="mt-6">
        <ChartCard symbol={symbol} />
      </div>

      {/* Indicators */}
      <div className="mt-6 grid gap-6 sm:grid-cols-2 xl:grid-cols-4">

        <IndicatorCard
          title="RSI"
          value={data.indicators.RSI.toFixed(2)}
          status={
            data.indicators.RSI > 60
              ? "Bullish"
              : data.indicators.RSI < 40
              ? "Bearish"
              : "Neutral"
          }
        />

        <IndicatorCard
          title="MACD"
          value={data.indicators.MACD.toFixed(2)}
          status={
            data.indicators.MACD >
            data.indicators.MACD_SIGNAL
              ? "Bullish"
              : "Bearish"
          }
        />

        <IndicatorCard
          title="EMA20"
          value={data.indicators.EMA20.toFixed(2)}
          status={
            data.price > data.indicators.EMA20
              ? "Bullish"
              : "Bearish"
          }
        />

        <IndicatorCard
          title="Recommendation"
          value={data.recommendation.recommendation}
          status={data.recommendation.recommendation}
        />

      </div>

      {/* Top Gainers & Top Losers */}
      <div className="mt-6">
        <TopMovers />
      </div>

      {/* Latest Financial News */}
      <div className="mt-6">
        <NewsCard />
      </div>

    </DashboardLayout>
  );
}