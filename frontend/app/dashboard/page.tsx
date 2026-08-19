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

export default function DashboardPage() {
  const [input, setInput] = useState("RELIANCE");
  const [symbol, setSymbol] = useState("RELIANCE");

  // Portfolio form
  const [showPortfolioForm, setShowPortfolioForm] = useState(false);
  const [quantity, setQuantity] = useState("1");
  const [averagePrice, setAveragePrice] = useState("");
  const [portfolioMessage, setPortfolioMessage] = useState("");
  const [portfolioError, setPortfolioError] = useState("");
  const [addingPortfolio, setAddingPortfolio] = useState(false);

  const { data, loading } = useStock(symbol);

  const {
    portfolio,
    summary,
    loading: portfolioLoading,
    addPortfolioItem,
    deletePortfolioItem,
  } = usePortfolio();

  // =========================
  // ADD TO PORTFOLIO
  // =========================

  const handleAddPortfolio = async () => {
    setPortfolioMessage("");
    setPortfolioError("");

    const qty = Number(quantity);
    const price = Number(averagePrice);

    if (!qty || qty <= 0) {
      setPortfolioError("Please enter a valid quantity.");
      return;
    }

    if (!price || price <= 0) {
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

  // =========================
  // LOADING
  // =========================

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

      {/* =========================
          LIVE MARKET CARDS
      ========================= */}

      <MarketCards />

      {/* =========================
          MARKET SUMMARY + AI
      ========================= */}

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

      {/* =========================
          PORTFOLIO
      ========================= */}

      <div className="mt-6 rounded-2xl border border-slate-800 bg-slate-900 p-6 shadow-lg">

        <div className="mb-6 flex flex-col gap-4 md:flex-row md:items-center md:justify-between">

          <div>
            <h2 className="text-xl font-bold text-white">
              Your Portfolio
            </h2>

            <p className="text-sm text-slate-400">
              Track your holdings and live profit/loss

              <span className="ml-2 text-xs text-green-500">
                ● Live
              </span>
            </p>
          </div>

          {/* =========================
              PORTFOLIO SUMMARY
          ========================= */}

          {!portfolioLoading && portfolio.length > 0 && (
            <div className="grid grid-cols-2 gap-3 md:grid-cols-4">

              {/* Total Invested */}
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

              {/* Current Value */}
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

              {/* Total P&L */}
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
                  {Math.abs(summary.total_pnl).toLocaleString(
                    "en-IN",
                    {
                      minimumFractionDigits: 2,
                      maximumFractionDigits: 2,
                    }
                  )}
                </p>
              </div>

              {/* P&L Percentage */}
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
                  {summary.total_pnl_percentage >= 0 ? "+" : ""}
                  {summary.total_pnl_percentage.toFixed(2)}%
                </p>
              </div>

            </div>
          )}
        </div>

        {/* =========================
            SUCCESS MESSAGE
        ========================= */}

        {portfolioMessage && (
          <div className="mb-4 rounded-xl border border-green-800 bg-green-950/40 px-4 py-3 text-sm text-green-400">
            {portfolioMessage}
          </div>
        )}

        {/* =========================
            ERROR MESSAGE
        ========================= */}

        {portfolioError && (
          <div className="mb-4 rounded-xl border border-red-800 bg-red-950/40 px-4 py-3 text-sm text-red-400">
            {portfolioError}
          </div>
        )}

        {/* =========================
            PORTFOLIO LOADING
        ========================= */}

        {portfolioLoading ? (

          <div className="py-8 text-center text-slate-400">
            Loading portfolio...
          </div>

        ) : portfolio.length === 0 ? (

          /* =========================
              EMPTY PORTFOLIO
          ========================= */

          <div className="rounded-xl border border-dashed border-slate-700 p-8 text-center">

            <p className="text-slate-400">
              Your portfolio is empty.
            </p>

            <p className="mt-2 text-sm text-slate-500">
              Analyse a stock and add it to your portfolio.
            </p>

          </div>

        ) : (

          /* =========================
              PORTFOLIO TABLE
          ========================= */

          <div className="overflow-x-auto">

            <table className="w-full text-left">

              <thead>
                <tr className="border-b border-slate-800 text-sm text-slate-400">

                  <th className="px-4 py-3">
                    Symbol
                  </th>

                  <th className="px-4 py-3">
                    Quantity
                  </th>

                  <th className="px-4 py-3">
                    Avg Price
                  </th>

                  <th className="px-4 py-3">
                    Live Price
                  </th>

                  <th className="px-4 py-3">
                    Invested
                  </th>

                  <th className="px-4 py-3">
                    Current Value
                  </th>

                  <th className="px-4 py-3">
                    P&L
                  </th>

                  <th className="px-4 py-3">
                    Action
                  </th>

                </tr>
              </thead>

              <tbody>

                {portfolio.map((item) => {

                  const currentPrice = item.current_price;
                  const investedValue = item.invested_value;
                  const currentValue = item.current_value;
                  const profitLoss = item.pnl;
                  const profitLossPercent = item.pnl_percentage;

                  const isProfit = (profitLoss ?? 0) >= 0;

                  return (

                    <tr
                      key={item.id}
                      className="border-b border-slate-800 last:border-0"
                    >

                      {/* Symbol */}
                      <td className="px-4 py-4 font-semibold text-white">
                        {item.symbol}
                      </td>

                      {/* Quantity */}
                      <td className="px-4 py-4 text-slate-300">
                        {item.quantity}
                      </td>

                      {/* Average Price */}
                      <td className="px-4 py-4 text-slate-300">
                        ₹
                        {item.average_price.toLocaleString(
                          "en-IN",
                          {
                            minimumFractionDigits: 2,
                            maximumFractionDigits: 2,
                          }
                        )}
                      </td>

                      {/* Live Price */}
                      <td className="px-4 py-4 font-semibold text-blue-400">

                        {item.price_available &&
                        currentPrice !== null ? (

                          <>
                            ₹
                            {currentPrice.toLocaleString(
                              "en-IN",
                              {
                                minimumFractionDigits: 2,
                                maximumFractionDigits: 2,
                              }
                            )}
                          </>

                        ) : (

                          <span className="text-slate-500">
                            Unavailable
                          </span>

                        )}

                      </td>

                      {/* Invested */}
                      <td className="px-4 py-4 text-slate-300">

                        ₹
                        {investedValue.toLocaleString(
                          "en-IN",
                          {
                            minimumFractionDigits: 2,
                            maximumFractionDigits: 2,
                          }
                        )}

                      </td>

                      {/* Current Value */}
                      <td className="px-4 py-4 text-slate-300">

                        {currentValue !== null ? (

                          <>
                            ₹
                            {currentValue.toLocaleString(
                              "en-IN",
                              {
                                minimumFractionDigits: 2,
                                maximumFractionDigits: 2,
                              }
                            )}
                          </>

                        ) : (

                          <span className="text-slate-500">
                            —
                          </span>

                        )}

                      </td>

                      {/* P&L */}
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
                              ).toLocaleString(
                                "en-IN",
                                {
                                  minimumFractionDigits: 2,
                                  maximumFractionDigits: 2,
                                }
                              )}
                            </div>

                            <div
                              className={
                                isProfit
                                  ? "text-xs text-green-500"
                                  : "text-xs text-red-500"
                              }
                            >
                              {isProfit ? "+" : ""}
                              {(profitLossPercent ?? 0).toFixed(2)}%
                            </div>

                          </>

                        ) : (

                          <span className="text-slate-500">
                            —
                          </span>

                        )}

                      </td>

                      {/* Delete */}
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

      {/* =========================
          STOCK SEARCH
      ========================= */}

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
          />

          <button
            onClick={() => {
              if (input.trim()) {
                setSymbol(input.trim().toUpperCase());
                setPortfolioMessage("");
                setPortfolioError("");
              }
            }}
            className="rounded-xl bg-blue-600 px-8 py-3 font-semibold text-white transition hover:bg-blue-700"
          >
            Analyse Stock
          </button>

        </div>

      </div>

      {/* =========================
          STOCK RESULT
      ========================= */}

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
              ₹{data.price.toFixed(2)}
            </p>

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

        {/* =========================
            ADD PORTFOLIO FORM
        ========================= */}

        {showPortfolioForm && (

          <div className="mt-6 rounded-xl border border-slate-700 bg-slate-800 p-5">

            <h3 className="mb-4 text-lg font-bold text-white">
              Add {symbol} to Portfolio
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

      {/* =========================
          TRADINGVIEW CHART
      ========================= */}

      <div className="mt-6">
        <ChartCard symbol={symbol} />
      </div>

      {/* =========================
          INDICATORS
      ========================= */}

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

      {/* =========================
          TOP MOVERS
      ========================= */}

      <div className="mt-6">
        <TopMovers />
      </div>

      {/* =========================
          AI PATTERN
      ========================= */}

      <div className="mt-6">
        <PatternCard pattern={data?.pattern} />
      </div>

      {/* =========================
          NEWS
      ========================= */}

      <div className="mt-6">
        <NewsCard />
      </div>

    </DashboardLayout>
  );
}