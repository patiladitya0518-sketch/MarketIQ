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
import PatternCard from "@/components/dashboard/PatternCard";

import useStock from "@/hooks/useStock";
import usePortfolio from "@/hooks/usePortfolio";

/* ============================================================
   HELPERS
============================================================ */

function formatPrice(value: number | null | undefined) {
  if (value === null || value === undefined || Number.isNaN(value)) {
    return "—";
  }

  return `₹${value.toLocaleString("en-IN", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}`;
}

/* ============================================================
   DASHBOARD
============================================================ */

export default function DashboardPage() {
  const [input, setInput] = useState("RELIANCE");
  const [symbol, setSymbol] = useState("RELIANCE");

  /* ============================================================
     PORTFOLIO FORM
  ============================================================ */

  const [showPortfolioForm, setShowPortfolioForm] =
    useState(false);

  const [quantity, setQuantity] = useState("1");
  const [averagePrice, setAveragePrice] = useState("");

  const [portfolioMessage, setPortfolioMessage] =
    useState("");

  const [portfolioError, setPortfolioError] =
    useState("");

  const [addingPortfolio, setAddingPortfolio] =
    useState(false);

  /* ============================================================
     STOCK
  ============================================================ */

  const {
    data,
    loading,
    refreshing: stockRefreshing,
    lastUpdated: stockLastUpdated,
    refreshStock,
  } = useStock(symbol);

  /* ============================================================
     PORTFOLIO
  ============================================================ */

  const {
    portfolio,
    summary,
    loading: portfolioLoading,
    refreshing: portfolioRefreshing,
    lastUpdated: portfolioLastUpdated,
    addPortfolioItem,
    deletePortfolioItem,
    refreshPortfolio,
  } = usePortfolio();

  /* ============================================================
     ADD TO PORTFOLIO
  ============================================================ */

  const handleAddPortfolio = async () => {
    setPortfolioMessage("");
    setPortfolioError("");

    const qty = Number(quantity);
    const price = Number(averagePrice);

    if (!Number.isFinite(qty) || qty <= 0) {
      setPortfolioError("Please enter a valid quantity.");
      return;
    }

    if (!Number.isFinite(price) || price <= 0) {
      setPortfolioError("Please enter a valid average price.");
      return;
    }

    try {
      setAddingPortfolio(true);

      await addPortfolioItem(symbol, qty, price);

      setPortfolioMessage(
        `${symbol} added to your portfolio successfully.`
      );

      setQuantity("1");
      setAveragePrice("");
      setShowPortfolioForm(false);
    } catch (error) {
      console.error(error);

      setPortfolioError(
        "Failed to add stock. Please make sure you are logged in."
      );
    } finally {
      setAddingPortfolio(false);
    }
  };

  /* ============================================================
     SEARCH STOCK
  ============================================================ */

  const analyseStock = () => {
    const cleanSymbol = input.trim().toUpperCase();

    if (!cleanSymbol) return;

    setSymbol(cleanSymbol);

    setPortfolioMessage("");
    setPortfolioError("");

    setShowPortfolioForm(false);
  };

  /* ============================================================
     LOADING
  ============================================================ */

  if (loading || !data || !data.recommendation) {
    return (
      <DashboardLayout>
        <div className="flex min-h-[80vh] items-center justify-center">
          <div className="text-center">
            <div className="mx-auto mb-4 h-12 w-12 animate-spin rounded-full border-4 border-blue-600 border-t-transparent" />

            <h2 className="text-2xl font-bold text-white">
              Loading MarketIQ...
            </h2>

            <p className="mt-2 text-slate-400">
              Analysing latest market data
            </p>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  /* ============================================================
     DERIVED DATA
  ============================================================ */

  const recommendation = data.recommendation;

  const marketStructure = data.market_structure;

  const supportResistance = data.support_resistance;

  const supportAnalysis =
    recommendation.support_resistance_analysis;

  const nearestSupport =
    supportAnalysis?.nearest_support ?? null;

  const nearestResistance =
    supportAnalysis?.nearest_resistance ?? null;

  const isBuy =
    recommendation.recommendation === "BUY";

  const isSell =
    recommendation.recommendation === "SELL";

  const recommendationColor = isBuy
    ? "text-green-400"
    : isSell
    ? "text-red-400"
    : "text-yellow-400";

  /* ============================================================
     RETURN
  ============================================================ */

  return (
    <DashboardLayout>

      {/* ========================================================
          LIVE MARKET
      ======================================================== */}

      <MarketCards />

      {/* ========================================================
          MARKET SUMMARY + AI RECOMMENDATION
      ======================================================== */}

      <div className="mt-6 grid gap-6 xl:grid-cols-3">

        <div className="xl:col-span-2">
          <MarketSummaryCard
            symbol={data.symbol}
            price={data.price}
          />
        </div>

        <RecommendationCard
          recommendation={recommendation.recommendation}
          confidence={recommendation.confidence}
          score={recommendation.score}
          reasons={recommendation.reasons}
          patternAnalysis={
            recommendation.pattern_analysis
          }
          marketStructureAnalysis={
            recommendation.market_structure_analysis
          }
          supportResistanceAnalysis={
            recommendation.support_resistance_analysis
          }
        />

      </div>

      {/* ========================================================
          PORTFOLIO
      ======================================================== */}

      <div className="mt-6 rounded-2xl border border-slate-800 bg-slate-900 p-6 shadow-lg">

        <div className="mb-6 flex flex-col gap-5 xl:flex-row xl:items-start xl:justify-between">

          <div>
            <h2 className="text-xl font-bold text-white">
              Your Portfolio
            </h2>

            <div className="mt-2 flex flex-wrap items-center gap-3">

              <p className="text-sm text-slate-400">
                Track your holdings and live profit/loss
              </p>

              <span className="flex items-center gap-1.5 text-xs font-medium text-green-400">
                <span className="h-2 w-2 rounded-full bg-green-400" />
                Live
              </span>

              {portfolioLastUpdated && (
                <span className="text-xs text-slate-500">
                  Updated{" "}
                  {portfolioLastUpdated.toLocaleTimeString(
                    "en-IN",
                    {
                      hour: "2-digit",
                      minute: "2-digit",
                      second: "2-digit",
                    }
                  )}
                </span>
              )}

              <button
                onClick={refreshPortfolio}
                disabled={portfolioRefreshing}
                className="rounded-lg border border-slate-700 bg-slate-800 px-3 py-1.5 text-xs font-medium text-slate-300 transition hover:bg-slate-700 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {portfolioRefreshing
                  ? "Updating..."
                  : "Refresh"}
              </button>

            </div>
          </div>

          {/* PORTFOLIO SUMMARY */}

          {!portfolioLoading &&
            portfolio.length > 0 && (

              <div className="grid grid-cols-2 gap-3 md:grid-cols-4">

                <div className="rounded-xl border border-slate-800 bg-slate-950 px-4 py-3">
                  <p className="text-xs text-slate-500">
                    Total Invested
                  </p>

                  <p className="mt-1 text-lg font-bold text-white">
                    ₹
                    {summary.total_invested.toLocaleString(
                      "en-IN",
                      {
                        minimumFractionDigits: 2,
                        maximumFractionDigits: 2,
                      }
                    )}
                  </p>
                </div>

                <div className="rounded-xl border border-slate-800 bg-slate-950 px-4 py-3">
                  <p className="text-xs text-slate-500">
                    Current Value
                  </p>

                  <p className="mt-1 text-lg font-bold text-white">
                    ₹
                    {summary.total_current_value.toLocaleString(
                      "en-IN",
                      {
                        minimumFractionDigits: 2,
                        maximumFractionDigits: 2,
                      }
                    )}
                  </p>
                </div>

                <div className="rounded-xl border border-slate-800 bg-slate-950 px-4 py-3">
                  <p className="text-xs text-slate-500">
                    Total P&L
                  </p>

                  <p
                    className={`mt-1 text-lg font-bold ${
                      summary.total_pnl >= 0
                        ? "text-green-400"
                        : "text-red-400"
                    }`}
                  >
                    {summary.total_pnl >= 0 ? "+" : "-"}₹
                    {Math.abs(
                      summary.total_pnl
                    ).toLocaleString("en-IN", {
                      minimumFractionDigits: 2,
                      maximumFractionDigits: 2,
                    })}
                  </p>
                </div>

                <div className="rounded-xl border border-slate-800 bg-slate-950 px-4 py-3">
                  <p className="text-xs text-slate-500">
                    P&L %
                  </p>

                  <p
                    className={`mt-1 text-lg font-bold ${
                      summary.total_pnl_percentage >= 0
                        ? "text-green-400"
                        : "text-red-400"
                    }`}
                  >
                    {summary.total_pnl_percentage >= 0
                      ? "+"
                      : ""}
                    {summary.total_pnl_percentage.toFixed(2)}%
                  </p>
                </div>

              </div>
            )}

        </div>

        {/* MESSAGES */}

        {portfolioMessage && (
          <div className="mb-4 rounded-xl border border-green-800 bg-green-950/40 px-4 py-3 text-sm text-green-400">
            {portfolioMessage}
          </div>
        )}

        {portfolioError && (
          <div className="mb-4 rounded-xl border border-red-800 bg-red-950/40 px-4 py-3 text-sm text-red-400">
            {portfolioError}
          </div>
        )}

        {/* PORTFOLIO */}

        {portfolioLoading ? (

          <div className="py-8 text-center text-slate-400">
            Loading portfolio...
          </div>

        ) : portfolio.length === 0 ? (

          <div className="rounded-xl border border-dashed border-slate-700 p-8 text-center">
            <p className="text-slate-400">
              Your portfolio is empty.
            </p>

            <p className="mt-2 text-sm text-slate-500">
              Analyse a stock and add it to your portfolio.
            </p>
          </div>

        ) : (

          <div className="overflow-x-auto">

            <table className="w-full min-w-[950px] text-left">

              <thead>
                <tr className="border-b border-slate-800 text-sm text-slate-400">

                  <th className="px-4 py-3">Symbol</th>
                  <th className="px-4 py-3">Quantity</th>
                  <th className="px-4 py-3">Avg Price</th>
                  <th className="px-4 py-3">Live Price</th>
                  <th className="px-4 py-3">Invested</th>
                  <th className="px-4 py-3">Current Value</th>
                  <th className="px-4 py-3">P&L</th>
                  <th className="px-4 py-3">Action</th>

                </tr>
              </thead>

              <tbody>

                {portfolio.map((item) => {

                  const profitLoss = item.pnl;
                  const profitLossPercent =
                    item.pnl_percentage;

                  const isProfit =
                    (profitLoss ?? 0) >= 0;

                  return (
                    <tr
                      key={item.id}
                      className="border-b border-slate-800 last:border-0"
                    >

                      <td className="px-4 py-4 font-semibold text-white">
                        {item.symbol}
                      </td>

                      <td className="px-4 py-4 text-slate-300">
                        {item.quantity}
                      </td>

                      <td className="px-4 py-4 text-slate-300">
                        {formatPrice(item.average_price)}
                      </td>

                      <td className="px-4 py-4 font-semibold text-blue-400">

                        {item.price_available &&
                        item.current_price !== null
                          ? formatPrice(item.current_price)
                          : (
                            <span className="text-slate-500">
                              Unavailable
                            </span>
                          )}

                      </td>

                      <td className="px-4 py-4 text-slate-300">
                        {formatPrice(item.invested_value)}
                      </td>

                      <td className="px-4 py-4 text-slate-300">
                        {formatPrice(item.current_value)}
                      </td>

                      <td className="px-4 py-4">

                        {profitLoss !== null ? (
                          <>
                            <div
                              className={
                                isProfit
                                  ? "font-semibold text-green-400"
                                  : "font-semibold text-red-400"
                              }
                            >
                              {isProfit ? "+" : "-"}₹
                              {Math.abs(
                                profitLoss
                              ).toLocaleString("en-IN", {
                                minimumFractionDigits: 2,
                                maximumFractionDigits: 2,
                              })}
                            </div>

                            <div
                              className={
                                isProfit
                                  ? "text-xs text-green-500"
                                  : "text-xs text-red-500"
                              }
                            >
                              {isProfit ? "+" : ""}
                              {(
                                profitLossPercent ?? 0
                              ).toFixed(2)}
                              %
                            </div>
                          </>
                        ) : (
                          <span className="text-slate-500">
                            —
                          </span>
                        )}

                      </td>

                      <td className="px-4 py-4">

                        <button
                          onClick={async () => {
                            try {
                              await deletePortfolioItem(item.id);
                            } catch (error) {
                              console.error(error);
                            }
                          }}
                          className="rounded-lg bg-red-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-red-700"
                        >
                          Delete
                        </button>

                      </td>

                    </tr>
                  );
                })}

              </tbody>

            </table>

          </div>
        )}

      </div>

      {/* ========================================================
          STOCK SEARCH
      ======================================================== */}

      <div className="mt-6 rounded-2xl border border-slate-800 bg-slate-900 p-6 shadow-lg">

        <div className="mb-5">

          <h2 className="text-xl font-bold text-white">
            Search Indian Stock
          </h2>

          <p className="text-sm text-slate-400">
            NSE Listed Companies
          </p>

        </div>

        <div className="flex flex-col gap-4 md:flex-row">

          <input
            className="flex-1 rounded-xl border border-slate-700 bg-slate-800 px-4 py-3 text-white outline-none transition focus:border-blue-500"
            placeholder="RELIANCE, TCS, INFY..."
            value={input}
            onChange={(e) =>
              setInput(e.target.value.toUpperCase())
            }
            onKeyDown={(e) => {
              if (e.key === "Enter") {
                analyseStock();
              }
            }}
          />

          <button
            onClick={analyseStock}
            className="rounded-xl bg-blue-600 px-8 py-3 font-semibold text-white transition hover:bg-blue-700"
          >
            Analyse Stock
          </button>

        </div>

      </div>

      {/* ========================================================
          STOCK RESULT
      ======================================================== */}

      <div className="mt-6 rounded-2xl border border-slate-800 bg-slate-900 p-6 shadow-lg">

        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">

          <div>

            <p className="text-sm text-slate-400">
              Currently Analysing
            </p>

            <h2 className="mt-1 text-2xl font-bold text-white">
              {data.symbol}
            </h2>

            <p className="mt-1 text-xl font-semibold text-blue-400">
              {formatPrice(data.price)}
            </p>

            <div className="mt-3 flex flex-wrap items-center gap-3">

              <span className="flex items-center gap-2 text-xs font-medium text-green-400">
                <span className="h-2 w-2 rounded-full bg-green-400" />
                Live
              </span>

              {stockLastUpdated && (
                <span className="text-xs text-slate-500">
                  Updated{" "}
                  {stockLastUpdated.toLocaleTimeString(
                    "en-IN",
                    {
                      hour: "2-digit",
                      minute: "2-digit",
                      second: "2-digit",
                    }
                  )}
                </span>
              )}

              {stockRefreshing && (
                <span className="text-xs text-blue-400">
                  Updating...
                </span>
              )}

              <button
                onClick={refreshStock}
                disabled={stockRefreshing}
                className="rounded-lg border border-slate-700 bg-slate-800 px-3 py-1.5 text-xs font-medium text-slate-300 transition hover:bg-slate-700 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {stockRefreshing
                  ? "Updating..."
                  : "Refresh"}
              </button>

            </div>

          </div>

          <button
            onClick={() => {
              setAveragePrice(data.price.toFixed(2));
              setQuantity("1");

              setPortfolioMessage("");
              setPortfolioError("");

              setShowPortfolioForm(true);
            }}
            className="rounded-xl bg-green-600 px-6 py-3 font-semibold text-white transition hover:bg-green-700"
          >
            + Add to Portfolio
          </button>

        </div>

        {/* ADD PORTFOLIO FORM */}

        {showPortfolioForm && (

          <div className="mt-6 rounded-xl border border-slate-700 bg-slate-800 p-5">

            <h3 className="mb-4 text-lg font-bold text-white">
              Add {data.symbol} to Portfolio
            </h3>

            <div className="grid gap-4 md:grid-cols-2">

              <div>
                <label className="mb-2 block text-sm text-slate-400">
                  Quantity
                </label>

                <input
                  type="number"
                  min="1"
                  value={quantity}
                  onChange={(e) =>
                    setQuantity(e.target.value)
                  }
                  className="w-full rounded-xl border border-slate-700 bg-slate-900 px-4 py-3 text-white outline-none focus:border-blue-500"
                />
              </div>

              <div>
                <label className="mb-2 block text-sm text-slate-400">
                  Average Price
                </label>

                <input
                  type="number"
                  min="0"
                  step="0.01"
                  value={averagePrice}
                  onChange={(e) =>
                    setAveragePrice(e.target.value)
                  }
                  className="w-full rounded-xl border border-slate-700 bg-slate-900 px-4 py-3 text-white outline-none focus:border-blue-500"
                />
              </div>

            </div>

            <div className="mt-5 flex flex-col gap-3 sm:flex-row">

              <button
                onClick={handleAddPortfolio}
                disabled={addingPortfolio}
                className="rounded-xl bg-green-600 px-6 py-3 font-semibold text-white transition hover:bg-green-700 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {addingPortfolio
                  ? "Adding..."
                  : "Add Stock"}
              </button>

              <button
                onClick={() => {
                  setShowPortfolioForm(false);
                  setPortfolioError("");
                }}
                className="rounded-xl border border-slate-700 px-6 py-3 font-semibold text-slate-300 transition hover:bg-slate-700"
              >
                Cancel
              </button>

            </div>

          </div>
        )}

      </div>

      {/* ========================================================
          CHART
      ======================================================== */}

      <div className="mt-6">
        <ChartCard symbol={symbol} />
      </div>

      {/* ========================================================
          TECHNICAL INDICATORS
      ======================================================== */}

      <div className="mt-6 grid gap-6 sm:grid-cols-2 xl:grid-cols-5">

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
          title="EMA50"
          value={data.indicators.EMA50.toFixed(2)}
          status={
            data.price > data.indicators.EMA50
              ? "Bullish"
              : "Bearish"
          }
        />

        <IndicatorCard
          title="Recommendation"
          value={recommendation.recommendation}
          status={recommendation.recommendation}
        />

      </div>

      {/* ========================================================
          AI ANALYSIS OVERVIEW
      ======================================================== */}

      <div className="mt-6 grid gap-6 xl:grid-cols-3">

        {/* AI SCORE */}

        <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6 shadow-lg">

          <p className="text-sm text-slate-400">
            AI Analysis Score
          </p>

          <div className="mt-3 flex items-end gap-3">

            <span
              className={`text-5xl font-bold ${recommendationColor}`}
            >
              {recommendation.score > 0 ? "+" : ""}
              {recommendation.score}
            </span>

            <span className="pb-1 text-sm text-slate-500">
              signal score
            </span>

          </div>

          <div className="mt-5">

            <div className="mb-2 flex justify-between text-xs">

              <span className="text-slate-500">
                Confidence
              </span>

              <span
                className={`font-semibold ${recommendationColor}`}
              >
                {recommendation.confidence}%
              </span>

            </div>

            <div className="h-2 overflow-hidden rounded-full bg-slate-800">

              <div
                className={`h-full rounded-full ${
                  isBuy
                    ? "bg-green-500"
                    : isSell
                    ? "bg-red-500"
                    : "bg-yellow-500"
                }`}
                style={{
                  width: `${Math.max(
                    0,
                    Math.min(
                      100,
                      recommendation.confidence
                    )
                  )}%`,
                }}
              />

            </div>

          </div>

          <div className="mt-5 rounded-xl bg-slate-950 p-4">

            <p className="text-xs text-slate-500">
              Final AI Decision
            </p>

            <p
              className={`mt-1 text-2xl font-bold ${recommendationColor}`}
            >
              {recommendation.recommendation}
            </p>

          </div>

        </div>

        {/* MARKET STRUCTURE */}

        <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6 shadow-lg">

          <p className="text-sm text-slate-400">
            Market Structure
          </p>

          {marketStructure ? (
            <>
              <div className="mt-3 flex items-center justify-between gap-3">

                <h3
                  className={`text-2xl font-bold ${
                    marketStructure.signal === "BUY"
                      ? "text-green-400"
                      : marketStructure.signal === "SELL"
                      ? "text-red-400"
                      : "text-yellow-400"
                  }`}
                >
                  {marketStructure.structure}
                </h3>

                <span className="rounded-lg border border-slate-700 bg-slate-800 px-3 py-1 text-xs font-semibold text-slate-300">
                  {marketStructure.confidence}%
                </span>

              </div>

              <p className="mt-2 text-sm text-slate-500">
                Trend:{" "}
                <span className="font-semibold text-slate-300">
                  {marketStructure.trend}
                </span>
              </p>

              <div className="mt-5 grid grid-cols-2 gap-3">

                <div className="rounded-xl bg-slate-950 p-3">
                  <p className="text-xs text-slate-500">
                    Higher High
                  </p>
                  <p className="mt-1 text-lg font-bold text-green-400">
                    {marketStructure.swing_counts.higher_high}
                  </p>
                </div>

                <div className="rounded-xl bg-slate-950 p-3">
                  <p className="text-xs text-slate-500">
                    Higher Low
                  </p>
                  <p className="mt-1 text-lg font-bold text-green-400">
                    {marketStructure.swing_counts.higher_low}
                  </p>
                </div>

                <div className="rounded-xl bg-slate-950 p-3">
                  <p className="text-xs text-slate-500">
                    Lower High
                  </p>
                  <p className="mt-1 text-lg font-bold text-red-400">
                    {marketStructure.swing_counts.lower_high}
                  </p>
                </div>

                <div className="rounded-xl bg-slate-950 p-3">
                  <p className="text-xs text-slate-500">
                    Lower Low
                  </p>
                  <p className="mt-1 text-lg font-bold text-red-400">
                    {marketStructure.swing_counts.lower_low}
                  </p>
                </div>

              </div>
            </>
          ) : (
            <p className="mt-4 text-sm text-slate-500">
              Market structure unavailable.
            </p>
          )}

        </div>

        {/* SUPPORT / RESISTANCE */}

        <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6 shadow-lg">

          <p className="text-sm text-slate-400">
            Support & Resistance
          </p>

          <div className="mt-4 grid grid-cols-2 gap-4">

            <div className="rounded-xl border border-green-900/50 bg-green-950/20 p-4">

              <p className="text-xs text-green-500">
                Nearest Support
              </p>

              <p className="mt-2 text-xl font-bold text-green-400">
                {formatPrice(nearestSupport)}
              </p>

            </div>

            <div className="rounded-xl border border-red-900/50 bg-red-950/20 p-4">

              <p className="text-xs text-red-500">
                Nearest Resistance
              </p>

              <p className="mt-2 text-xl font-bold text-red-400">
                {formatPrice(nearestResistance)}
              </p>

            </div>

          </div>

          {supportResistance && (
            <div className="mt-5">

              <p className="mb-2 text-xs text-slate-500">
                Key Levels
              </p>

              <div className="flex flex-wrap gap-2">

                {supportResistance.support.map(
                  (level, index) => (
                    <span
                      key={`support-${index}`}
                      className="rounded-lg bg-green-950/40 px-3 py-1.5 text-xs font-medium text-green-400"
                    >
                      S {formatPrice(level)}
                    </span>
                  )
                )}

                {supportResistance.resistance.map(
                  (level, index) => (
                    <span
                      key={`resistance-${index}`}
                      className="rounded-lg bg-red-950/40 px-3 py-1.5 text-xs font-medium text-red-400"
                    >
                      R {formatPrice(level)}
                    </span>
                  )
                )}

              </div>

            </div>
          )}

        </div>

      </div>

      {/* ========================================================
          MARKET STRUCTURE DETAILS
      ======================================================== */}

      {marketStructure && (
        <div className="mt-6 rounded-2xl border border-slate-800 bg-slate-900 p-6 shadow-lg">

          <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">

            <div>

              <p className="text-sm text-slate-400">
                Market Structure Analysis
              </p>

              <h2 className="mt-1 text-2xl font-bold text-white">
                {marketStructure.structure} Market
              </h2>

            </div>

            <div className="flex items-center gap-3">

              <span
                className={`rounded-xl px-4 py-2 text-sm font-bold ${
                  marketStructure.signal === "BUY"
                    ? "bg-green-950/50 text-green-400"
                    : marketStructure.signal === "SELL"
                    ? "bg-red-950/50 text-red-400"
                    : "bg-yellow-950/50 text-yellow-400"
                }`}
              >
                {marketStructure.signal}
              </span>

              <span className="rounded-xl border border-slate-700 bg-slate-800 px-4 py-2 text-sm text-slate-300">
                {marketStructure.confidence}% confidence
              </span>

            </div>

          </div>

          <div className="mt-5 grid gap-3 md:grid-cols-2">

            {marketStructure.reasons.map(
              (reason, index) => (
                <div
                  key={index}
                  className="rounded-xl border border-slate-800 bg-slate-950 px-4 py-3 text-sm text-slate-300"
                >
                  ✓ {reason}
                </div>
              )
            )}

          </div>

        </div>
      )}

      {/* ========================================================
          SUPPORT / RESISTANCE DETAILS
      ======================================================== */}

      {supportResistance && (
        <div className="mt-6 rounded-2xl border border-slate-800 bg-slate-900 p-6 shadow-lg">

          <div className="mb-5">

            <p className="text-sm text-slate-400">
              Technical Price Levels
            </p>

            <h2 className="mt-1 text-2xl font-bold text-white">
              Support & Resistance
            </h2>

          </div>

          <div className="grid gap-6 md:grid-cols-2">

            {/* SUPPORT */}

            <div>

              <h3 className="mb-3 font-semibold text-green-400">
                Support Levels
              </h3>

              <div className="space-y-2">

                {supportResistance.support.length > 0 ? (
                  supportResistance.support.map(
                    (level, index) => (
                      <div
                        key={index}
                        className="flex items-center justify-between rounded-xl border border-green-900/40 bg-green-950/20 px-4 py-3"
                      >
                        <span className="text-sm text-slate-400">
                          Support {index + 1}
                        </span>

                        <span className="font-semibold text-green-400">
                          {formatPrice(level)}
                        </span>
                      </div>
                    )
                  )
                ) : (
                  <p className="text-sm text-slate-500">
                    No support levels detected.
                  </p>
                )}

              </div>

            </div>

            {/* RESISTANCE */}

            <div>

              <h3 className="mb-3 font-semibold text-red-400">
                Resistance Levels
              </h3>

              <div className="space-y-2">

                {supportResistance.resistance.length > 0 ? (
                  supportResistance.resistance.map(
                    (level, index) => (
                      <div
                        key={index}
                        className="flex items-center justify-between rounded-xl border border-red-900/40 bg-red-950/20 px-4 py-3"
                      >
                        <span className="text-sm text-slate-400">
                          Resistance {index + 1}
                        </span>

                        <span className="font-semibold text-red-400">
                          {formatPrice(level)}
                        </span>
                      </div>
                    )
                  )
                ) : (
                  <p className="text-sm text-slate-500">
                    No resistance levels detected.
                  </p>
                )}

              </div>

            </div>

          </div>

        </div>
      )}

      {/* ========================================================
          TOP MOVERS
      ======================================================== */}

      <div className="mt-6">
        <TopMovers />
      </div>

      {/* ========================================================
          AI PATTERN
      ======================================================== */}

      <div className="mt-6">
        <PatternCard pattern={data.pattern} />
      </div>

      {/* ========================================================
          NEWS
      ======================================================== */}

      <div className="mt-6">
        <NewsCard />
      </div>

    </DashboardLayout>
  );
}