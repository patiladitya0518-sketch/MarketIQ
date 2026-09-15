"use client";

import { useEffect, useState } from "react";

import DashboardLayout from "@/components/dashboard/DashboardLayout";
import MarketCards from "@/components/dashboard/MarketCards";
import MarketSummaryCard from "@/components/dashboard/MarketSummaryCard";
import RecommendationCard from "@/components/dashboard/RecommendationCard";
import IndicatorCard from "@/components/dashboard/IndicatorCard";
import ChartCard from "@/components/dashboard/ChartCard";
import TopMovers from "@/components/dashboard/TopMovers";
import NewsCard from "@/components/dashboard/NewsCard";
import PatternCard from "@/components/dashboard/PatternCard";
import api from "@/lib/api";

import useStock from "@/hooks/useStock";
import usePortfolio from "@/hooks/usePortfolio";

/* ============================================================
   HELPERS
============================================================ */

function formatPrice(
  value: number | null | undefined
) {
  if (
    value === null ||
    value === undefined ||
    Number.isNaN(value)
  ) {
    return "—";
  }

  return `₹${value.toLocaleString("en-IN", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}`;
}

function formatNumber(
  value: number | null | undefined
) {
  if (
    value === null ||
    value === undefined ||
    Number.isNaN(value)
  ) {
    return "—";
  }

  return value.toLocaleString("en-IN", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
}

function formatSignedNumber(
  value: number | null | undefined
) {
  if (
    value === null ||
    value === undefined ||
    !Number.isFinite(value)
  ) {
    return "—";
  }

  const absoluteValue = Math.abs(value);
  const formatted = absoluteValue.toLocaleString("en-IN", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });

  if (value < 0) {
    return `-₹${formatted}`;
  }

  if (value > 0) {
    return `+₹${formatted}`;
  }

  return `₹${formatted}`;
}

/* ============================================================
   DASHBOARD
============================================================ */

export default function DashboardPage() {
  const [input, setInput] =
    useState("RELIANCE");

  const [symbol, setSymbol] =
    useState("RELIANCE");

  /* ============================================================
     PORTFOLIO FORM
  ============================================================ */

  const [showPortfolioForm, setShowPortfolioForm] =
    useState(false);

  const [quantity, setQuantity] =
    useState("1");

  const [averagePrice, setAveragePrice] =
    useState("");

  const [portfolioMessage, setPortfolioMessage] =
    useState("");

  const [portfolioError, setPortfolioError] =
    useState("");

  const [addingPortfolio, setAddingPortfolio] =
    useState(false);

  const [deletingPortfolioId, setDeletingPortfolioId] =
    useState<number | string | null>(null);

  /* ============================================================
     PAPER TRADING
  ============================================================ */

  const [paperAccount, setPaperAccount] = useState<any>(null);
  const [paperLoading, setPaperLoading] = useState(false);
  const [paperRefreshing, setPaperRefreshing] = useState(false);
  const [paperQuantity, setPaperQuantity] = useState("1");
  const [paperMessage, setPaperMessage] = useState("");
  const [paperError, setPaperError] = useState("");
  const [paperOrderSide, setPaperOrderSide] = useState<"BUY" | "SELL">("BUY");
  const [paperOrdering, setPaperOrdering] = useState(false);
  const [paperSellSymbol, setPaperSellSymbol] = useState("");

  const loadPaperAccount = async (refresh = false) => {
    try {
      refresh ? setPaperRefreshing(true) : setPaperLoading(true);
      const response = await api.get("/paper-trading/account");
      const account = response.data;
      setPaperAccount(account);

      // Keep the SELL selector synchronized with the holdings returned
      // by the backend. If the previously selected holding no longer
      // exists, automatically select the first available holding.
      const positions = Array.isArray(account?.positions)
        ? account.positions
        : [];

      if (positions.length === 0) {
        setPaperSellSymbol("");
      } else {
        setPaperSellSymbol((current) => {
          const stillExists = positions.some(
            (position: any) =>
              String(position?.symbol ?? "").toUpperCase() ===
              String(current ?? "").toUpperCase()
          );

          return stillExists
            ? current
            : String(positions[0]?.symbol ?? "").toUpperCase();
        });
      }
    } catch (error: any) {
      console.error("Paper account failed:", error?.response?.data || error);
      setPaperError(error?.response?.data?.detail || "Unable to load paper trading account.");
    } finally {
      setPaperLoading(false);
      setPaperRefreshing(false);
    }
  };

  useEffect(() => {
    loadPaperAccount();
  }, []);

  // Refresh paper holdings whenever the analysed stock changes.
  // This keeps the SELL HOLDING selector synchronized when moving
  // between RELIANCE, TCS, INFY, etc., without requiring a page reload.
  useEffect(() => {
    if (!symbol) return;
    loadPaperAccount(true);
  }, [symbol]);

const handlePaperOrder = async (
  side: "BUY" | "SELL",
  orderSymbol?: string,
  orderPrice?: number
) => {
  setPaperMessage("");
  setPaperError("");

  const cleanSymbol = String(
    orderSymbol || data?.symbol || symbol || ""
  )
    .trim()
    .toUpperCase();

  const qty = Number(paperQuantity);
  const price = Number(
    orderPrice !== undefined
      ? orderPrice
      : data?.price
  );

  if (!cleanSymbol) {
    setPaperError("Unable to determine the stock symbol.");
    return;
  }

  if (!Number.isInteger(qty) || qty <= 0) {
    setPaperError(
      "Please enter a valid whole-number quantity."
    );
    return;
  }

  if (!Number.isFinite(price) || price <= 0) {
    setPaperError(
      "Current market price is unavailable."
    );
    return;
  }

  // When selling, make sure the selected holding exists
  // and the requested quantity does not exceed the holding.
  if (side === "SELL") {
    const position = paperAccount?.positions?.find(
      (item: any) =>
        String(item.symbol).toUpperCase() === cleanSymbol
    );

    if (!position) {
      setPaperError(
        `You do not currently hold ${cleanSymbol}.`
      );
      return;
    }

    const availableQuantity = Number(
      position.quantity
    );

    if (
      !Number.isFinite(availableQuantity) ||
      qty > availableQuantity
    ) {
      setPaperError(
        `You only have ${availableQuantity} share(s) of ${cleanSymbol} available to sell.`
      );
      return;
    }
  }

  try {
    setPaperOrderSide(side);
    setPaperOrdering(true);

    const response = await api.post(
      "/paper-trading/order",
      {
        symbol: cleanSymbol,
        side,
        quantity: qty,
        price,
      }
    );

    const responseData = response?.data;

    if (responseData?.account) {
      setPaperAccount(responseData.account);
    } else if (responseData) {
      setPaperAccount(responseData);
    }

    setPaperMessage(
      responseData?.message ||
        `${side} order executed successfully for ${qty} ${cleanSymbol}.`
    );

    setPaperQuantity("1");

    // Refresh account so all holdings and balances
    // are immediately synchronized.
    await loadPaperAccount(true);

  } catch (error: any) {
    console.error(
      "Paper order failed:",
      error?.response?.data ||
        error?.message ||
        error
    );

    const backendError =
      error?.response?.data?.detail ||
      error?.response?.data?.message;

    if (Array.isArray(backendError)) {
      setPaperError(
        backendError
          .map((item: any) =>
            typeof item === "string"
              ? item
              : item?.msg ||
                "Invalid order data."
          )
          .join(", ")
      );
    } else {
      setPaperError(
        backendError ||
          "Unable to execute paper trading order."
      );
    }
  } finally {
    setPaperOrdering(false);
    setPaperOrderSide("BUY");
  }
};
  /* ============================================================
     STOCK DATA
  ============================================================ */

  const {
    data,
    loading,
    refreshing: stockRefreshing,
    lastUpdated: stockLastUpdated,
    refreshStock,
    error: stockError,
  } = useStock(symbol);

  /* ============================================================
     PORTFOLIO DATA
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
     ADD STOCK TO PORTFOLIO
  ============================================================ */

  const handleAddPortfolio = async () => {
    setPortfolioMessage("");
    setPortfolioError("");

    const qty = Number(quantity);
    const price = Number(averagePrice);

    if (!Number.isInteger(qty) || qty <= 0) {
      setPortfolioError(
        "Please enter a valid whole-number quantity."
      );
      return;
    }

    if (!Number.isFinite(price) || price <= 0) {
      setPortfolioError(
        "Please enter a valid average price."
      );
      return;
    }

    try {
      setAddingPortfolio(true);

      await addPortfolioItem(
        symbol,
        qty,
        price
      );

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
     SEARCH / ANALYSE STOCK
  ============================================================ */

  const analyseStock = () => {
    const cleanSymbol =
      input.trim().toUpperCase();

    if (!cleanSymbol) {
      setPortfolioMessage("");
      setPortfolioError("Please enter a valid NSE/BSE stock symbol.");
      return;
    }

    if (!/^[A-Z0-9&.-]{1,30}$/.test(cleanSymbol)) {
      setPortfolioMessage("");
      setPortfolioError("Please enter a valid stock symbol, for example RELIANCE, TCS or INFY.");
      return;
    }

    setPortfolioMessage("");
    setPortfolioError("");
    setSymbol(cleanSymbol);

    setPortfolioMessage("");
    setPortfolioError("");
    setShowPortfolioForm(false);
  };

  /* ============================================================
     LOADING
  ============================================================ */

  if (loading || !data) {
    return (
      <DashboardLayout>
        <div className="flex min-h-[70vh] items-center justify-center px-4">
          <div className="w-full max-w-lg rounded-2xl border border-slate-800 bg-slate-900 p-8 text-center shadow-xl">
            {stockError ? (
              <>
                <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-full border border-red-500/20 bg-red-500/10 text-xl text-red-400">
                  !
                </div>
                <h2 className="text-xl font-bold text-white">Unable to load {symbol}</h2>
                <p className="mt-2 text-sm leading-6 text-slate-400">{stockError}</p>
                <div className="mt-6 flex flex-col justify-center gap-3 sm:flex-row">
                  <button
                    type="button"
                    onClick={refreshStock}
                    disabled={stockRefreshing}
                    className="rounded-xl bg-blue-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    {stockRefreshing ? "Retrying..." : "Retry"}
                  </button>
                  <button
                    type="button"
                    onClick={() => { setInput("RELIANCE"); setSymbol("RELIANCE"); }}
                    className="rounded-xl border border-slate-700 bg-slate-800 px-5 py-3 text-sm font-semibold text-slate-300 transition hover:bg-slate-700 hover:text-white"
                  >
                    Analyse RELIANCE
                  </button>
                </div>
              </>
            ) : (
              <>
                <div className="mx-auto mb-4 h-12 w-12 animate-spin rounded-full border-4 border-blue-600 border-t-transparent" />
                <h2 className="text-2xl font-bold text-white">Loading MarketIQ</h2>
                <p className="mt-2 text-sm text-slate-400">Fetching market data and preparing the AI analysis for {symbol}.</p>
              </>
            )}
          </div>
        </div>
      </DashboardLayout>
    );
  }

  /* ============================================================
     DERIVED DATA
  ============================================================ */

  const recommendation =
    data.recommendation;

  const marketStructure =
    data.market_structure;

  const supportResistance =
    data.support_resistance;

  const smc =
    data.smc;
  const smcData = smc as any;

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

  const recommendationColor =
    isBuy
      ? "text-green-400"
      : isSell
      ? "text-red-400"
      : "text-yellow-400";

  const recommendationBg =
    isBuy
      ? "bg-green-500"
      : isSell
      ? "bg-red-500"
      : "bg-yellow-500";

  /* ============================================================
     PORTFOLIO TOTALS

     Calculate the dashboard totals from the actual holdings so the
     displayed P&L cannot inherit an incorrect sign from the API
     summary object.
  ============================================================ */

  const portfolioTotals = portfolio.reduce(
    (totals, item) => {
      const invested = Number(item.invested_value);
      const currentValue = Number(item.current_value);

      if (Number.isFinite(invested)) {
        totals.invested += invested;
      }

      if (Number.isFinite(currentValue)) {
        totals.currentValue += currentValue;
      }

      return totals;
    },
    { invested: 0, currentValue: 0 }
  );

  const portfolioTotalPnl =
    portfolioTotals.currentValue -
    portfolioTotals.invested;

  const portfolioTotalPnlPercentage =
    portfolioTotals.invested > 0
      ? (portfolioTotalPnl / portfolioTotals.invested) * 100
      : 0;

  /* ============================================================
     PAPER TRADING - SELECTED SELL HOLDING
  ============================================================ */

  const paperPositions = Array.isArray(paperAccount?.positions)
    ? paperAccount.positions
    : [];

  const selectedSellPosition =
    paperPositions.find(
      (position: any) =>
        String(position?.symbol ?? "").toUpperCase() ===
        String(paperSellSymbol ?? "").toUpperCase()
    ) ?? paperPositions[0] ?? null;

  const selectedSellSymbol = String(
    selectedSellPosition?.symbol ?? paperSellSymbol ?? ""
  ).toUpperCase();

  const selectedSellQuantity = Number(
    selectedSellPosition?.quantity ?? 0
  );

  const selectedSellPrice = Number(
    selectedSellPosition?.current_price ?? 0
  );

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
          MARKET SUMMARY
      ======================================================== */}

      <div className="mt-6">

        <MarketSummaryCard
          symbol={data.symbol}
          price={data.price}
        />

      </div>

      {/* ========================================================
          AI RECOMMENDATION
      ======================================================== */}

      <div className="mt-6">

        <RecommendationCard
          recommendation={recommendation}
        />

      </div>

      {/* ========================================================
          PORTFOLIO
      ======================================================== */}

      <div className="mt-6 rounded-2xl border border-slate-800 bg-slate-900 p-6 shadow-lg">

        <div className="mb-6 flex flex-col gap-5 xl:flex-row xl:items-start xl:justify-between">

          <div>

            <div className="flex items-center gap-3">

              <h2 className="text-xl font-bold text-white">
                Your Portfolio
              </h2>

              <span className="rounded-full bg-blue-500/10 px-2.5 py-1 text-xs font-semibold text-blue-400">
                Live Tracking
              </span>

            </div>

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

          {/* ====================================================
              PORTFOLIO SUMMARY
          ==================================================== */}

          {!portfolioLoading &&
            portfolio.length > 0 && (

              <div className="grid grid-cols-2 gap-3 md:grid-cols-4">

                <div className="rounded-xl border border-slate-800 bg-slate-950 px-4 py-3">

                  <p className="text-xs text-slate-500">
                    Total Invested
                  </p>

                  <p className="mt-1 text-lg font-bold text-white">
                    ₹
                    {formatNumber(
                      portfolioTotals.invested
                    )}
                  </p>

                </div>

                <div className="rounded-xl border border-slate-800 bg-slate-950 px-4 py-3">

                  <p className="text-xs text-slate-500">
                    Current Value
                  </p>

                  <p className="mt-1 text-lg font-bold text-white">
                    ₹
                    {formatNumber(
                      portfolioTotals.currentValue
                    )}
                  </p>

                </div>

                <div className="rounded-xl border border-slate-800 bg-slate-950 px-4 py-3">

                  <p className="text-xs text-slate-500">
                    Total P&L
                  </p>

                  <p
                    className={`mt-1 text-lg font-bold ${
                      portfolioTotalPnl >= 0
                        ? "text-green-400"
                        : "text-red-400"
                    }`}
                  >

                    {formatSignedNumber(
                      portfolioTotalPnl
                    )}

                  </p>

                </div>

                <div className="rounded-xl border border-slate-800 bg-slate-950 px-4 py-3">

                  <p className="text-xs text-slate-500">
                    P&L %
                  </p>

                  <p
                    className={`mt-1 text-lg font-bold ${
                      portfolioTotalPnlPercentage >= 0
                        ? "text-green-400"
                        : "text-red-400"
                    }`}
                  >

                    {portfolioTotalPnlPercentage >= 0
                      ? "+"
                      : ""}

                    {portfolioTotalPnlPercentage.toFixed(
                      2
                    )}

                    %

                  </p>

                </div>

              </div>
            )}

        </div>

        {/* ====================================================
            MESSAGES
        ==================================================== */}

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

        {/* ====================================================
            PORTFOLIO CONTENT
        ==================================================== */}

        {portfolioLoading ? (

          <div className="py-8 text-center text-slate-400">
            Loading portfolio...
          </div>

        ) : portfolio.length === 0 ? (

          <div className="rounded-xl border border-dashed border-slate-700 p-8 text-center">

            <div className="mx-auto mb-3 flex h-12 w-12 items-center justify-center rounded-full bg-slate-800 text-xl">
              +
            </div>

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

                  const profitLoss =
                    item.pnl;

                  const profitLossPercent =
                    item.pnl_percentage;

                  const isProfit =
                    (profitLoss ?? 0) >= 0;

                  return (

                    <tr
                      key={item.id}
                      className="border-b border-slate-800 transition hover:bg-slate-800/40 last:border-0"
                    >

                      <td className="px-4 py-4 font-semibold text-white">
                        {item.symbol}
                      </td>

                      <td className="px-4 py-4 text-slate-300">
                        {item.quantity}
                      </td>

                      <td className="px-4 py-4 text-slate-300">
                        {formatPrice(
                          item.average_price
                        )}
                      </td>

                      <td className="px-4 py-4 font-semibold text-blue-400">

                        {item.price_available &&
                        item.current_price !== null
                          ? formatPrice(
                              item.current_price
                            )
                          : (
                            <span className="text-slate-500">
                              Unavailable
                            </span>
                          )}

                      </td>

                      <td className="px-4 py-4 text-slate-300">
                        {formatPrice(
                          item.invested_value
                        )}
                      </td>

                      <td className="px-4 py-4 text-slate-300">
                        {formatPrice(
                          item.current_value
                        )}
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

                              {isProfit
                                ? "+"
                                : "-"}

                              ₹

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

                              {isProfit
                                ? "+"
                                : ""}

                              {(
                                profitLossPercent ??
                                0
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
                            const confirmed = window.confirm(
                              `Delete ${item.symbol} from your portfolio? This action cannot be undone.`
                            );

                            if (!confirmed) return;

                            try {
                              setDeletingPortfolioId(item.id);
                              setPortfolioMessage("");
                              setPortfolioError("");

                              await deletePortfolioItem(
                                item.id
                              );

                              setPortfolioMessage(
                                `${item.symbol} was removed from your portfolio.`
                              );
                            } catch (error) {
                              console.error(error);

                              setPortfolioError(
                                `Failed to delete ${item.symbol}. Please try again.`
                              );
                            } finally {
                              setDeletingPortfolioId(null);
                            }
                          }}
                          disabled={deletingPortfolioId === item.id}
                          className="rounded-lg bg-red-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-red-700 disabled:cursor-not-allowed disabled:opacity-50"
                        >
                          {deletingPortfolioId === item.id
                            ? "Deleting..."
                            : "Delete"}
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

          <div className="flex items-center gap-3">

            <h2 className="text-xl font-bold text-white">
              Search Indian Stock
            </h2>

            <span className="rounded-full bg-blue-500/10 px-2.5 py-1 text-xs font-semibold text-blue-400">
              NSE / BSE
            </span>

          </div>

          <p className="mt-1 text-sm text-slate-400">
            Analyse Indian listed companies using MarketIQ AI.
          </p>

        </div>

        <div className="flex flex-col gap-4 md:flex-row">

          <input
            className="flex-1 rounded-xl border border-slate-700 bg-slate-800 px-4 py-3 text-white outline-none transition placeholder:text-slate-500 focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
            placeholder="RELIANCE, TCS, INFY..."
            value={input}
            onChange={(e) =>
              setInput(
                e.target.value.toUpperCase()
              )
            }
            onKeyDown={(e) => {

              if (e.key === "Enter") {
                analyseStock();
              }

            }}
          />

          <button
            onClick={analyseStock}
            disabled={loading || !input.trim()}
            className="rounded-xl bg-blue-600 px-8 py-3 font-semibold text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {loading ? "Analysing..." : "Analyse Stock"}
          </button>

        </div>

        {stockError && (
          <div className="mt-4 rounded-xl border border-red-800 bg-red-950/30 px-4 py-3 text-sm text-red-400">
            {stockError}
          </div>
        )}

      </div>

      {/* ========================================================
          CURRENT STOCK RESULT
      ======================================================== */}

      <div className="mt-6 rounded-2xl border border-slate-800 bg-slate-900 p-6 shadow-lg">

        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">

          <div>

            <div className="flex items-center gap-3">

              <p className="text-sm text-slate-400">
                Currently Analysing
              </p>

              <span className="flex items-center gap-1.5 text-xs font-medium text-green-400">

                <span className="h-2 w-2 rounded-full bg-green-400" />

                Live

              </span>

              {data.exchange && (
                <span className="rounded-full bg-slate-800 px-2.5 py-1 text-xs font-medium text-slate-400">
                  {data.exchange}
                </span>
              )}

              <span className="rounded-full border border-blue-500/20 bg-blue-500/10 px-2.5 py-1 text-xs font-medium text-blue-400">
                AI Analysis Ready
              </span>

            </div>

            <h2 className="mt-1 text-2xl font-bold text-white">
              {data.symbol}
            </h2>

            <p className="mt-1 text-xl font-semibold text-blue-400">
              {formatPrice(data.price)}
            </p>

            <div className="mt-3 flex flex-wrap items-center gap-3">

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

              setAveragePrice(
                data.price.toFixed(2)
              );

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

        {/* ====================================================
            ADD PORTFOLIO FORM
        ==================================================== */}

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
                  step="1"
                  value={quantity}
                  onChange={(e) =>
                    setQuantity(
                      e.target.value
                    )
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
                    setAveragePrice(
                      e.target.value
                    )
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
          PAPER TRADING
      ======================================================== */}

      <div className="mt-6 rounded-2xl border border-slate-800 bg-slate-900 p-6 shadow-lg">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
          <div>
            <div className="flex items-center gap-3">
              <h2 className="text-xl font-bold text-white">Paper Trading</h2>
              <span className="rounded-full bg-purple-500/10 px-2.5 py-1 text-xs font-semibold text-purple-400">Virtual Money</span>
            </div>
            <p className="mt-1 text-sm text-slate-400">Practice BUY and SELL orders with ₹1,00,000 virtual capital.</p>
          </div>
          <button
            onClick={() => loadPaperAccount(true)}
            disabled={paperRefreshing}
            className="rounded-lg border border-slate-700 bg-slate-800 px-4 py-2 text-sm font-medium text-slate-300 transition hover:bg-slate-700 disabled:opacity-50"
          >
            {paperRefreshing ? "Updating..." : "Refresh"}
          </button>
        </div>

        {paperMessage && <div className="mt-4 rounded-xl border border-green-800 bg-green-950/40 px-4 py-3 text-sm text-green-400">{paperMessage}</div>}
        {paperError && <div className="mt-4 rounded-xl border border-red-800 bg-red-950/40 px-4 py-3 text-sm text-red-400">{paperError}</div>}

        {paperLoading ? (
          <div className="py-8 text-center text-slate-400">Loading paper trading account...</div>
        ) : (
          <>
            <div className="mt-5 grid grid-cols-2 gap-3 md:grid-cols-4">
              {[
                ["Available Cash", paperAccount?.available_cash],
                ["Invested Value", paperAccount?.invested_value],
                ["Current Value", paperAccount?.current_value],
                ["Total Equity", paperAccount?.total_equity],
              ].map(([label, value]) => (
                <div key={String(label)} className="rounded-xl border border-slate-800 bg-slate-950 px-4 py-3">
                  <p className="text-xs text-slate-500">{label}</p>
                  <p className="mt-1 text-lg font-bold text-white">{value != null ? formatPrice(Number(value)) : "—"}</p>
                </div>
              ))}
            </div>

            <div className="mt-4 grid grid-cols-2 gap-3">
              <div className="rounded-xl border border-slate-800 bg-slate-950 px-4 py-3">
                <p className="text-xs text-slate-500">Total P&L</p>
                <p className={`mt-1 text-lg font-bold ${Number(paperAccount?.total_pnl ?? 0) >= 0 ? "text-green-400" : "text-red-400"}`}>
                  {formatSignedNumber(Number(paperAccount?.total_pnl ?? 0))}
                </p>
              </div>
              <div className="rounded-xl border border-slate-800 bg-slate-950 px-4 py-3">
                <p className="text-xs text-slate-500">P&L %</p>
                <p className={`mt-1 text-lg font-bold ${Number(paperAccount?.total_pnl_percentage ?? 0) >= 0 ? "text-green-400" : "text-red-400"}`}>
                  {Number(paperAccount?.total_pnl_percentage ?? 0) >= 0 ? "+" : ""}{Number(paperAccount?.total_pnl_percentage ?? 0).toFixed(2)}%
                </p>
              </div>
            </div>

            <div className="mt-5 rounded-xl border border-slate-800 bg-slate-950 p-5">
              <div className="mb-4">
                <p className="text-sm font-semibold text-white">Place Paper Order</p>
                <p className="mt-1 text-xs text-slate-500">
                  BUY the stock currently being analysed, or select exactly which holding you want to SELL.
                </p>
              </div>

              <div className="grid gap-4 lg:grid-cols-[1fr_1fr_140px_auto_auto] lg:items-end">
                {/* BUY STOCK */}
                <div className="rounded-xl border border-green-900/40 bg-green-950/10 p-4">
                  <p className="text-xs font-semibold uppercase tracking-wide text-green-400">Buy</p>
                  <p className="mt-2 text-lg font-bold text-white">{data.symbol}</p>
                  <p className="mt-1 text-xs text-slate-500">
                    Market price: {formatPrice(data.price)}
                  </p>
                </div>

                {/* SELL HOLDING SELECTOR */}
                <div className="rounded-xl border border-red-900/40 bg-red-950/10 p-4">
                  <label className="mb-2 block text-xs font-semibold uppercase tracking-wide text-red-400">
                    Sell Holding
                  </label>

                  {paperPositions.length > 0 ? (
                    <>
                      <select
                        value={selectedSellSymbol}
                        onChange={(e) => {
                          setPaperSellSymbol(e.target.value);
                          setPaperQuantity("1");
                          setPaperMessage("");
                          setPaperError("");
                        }}
                        disabled={paperOrdering}
                        className="w-full rounded-xl border border-slate-700 bg-slate-800 px-4 py-3 font-semibold text-white outline-none transition focus:border-red-500 disabled:cursor-not-allowed disabled:opacity-60"
                      >
                        {paperPositions.map((position: any) => {
                          const positionSymbol = String(position?.symbol ?? "").toUpperCase();
                          return (
                            <option key={positionSymbol} value={positionSymbol}>
                              {positionSymbol} — {position.quantity} share{Number(position.quantity) === 1 ? "" : "s"}
                            </option>
                          );
                        })}
                      </select>

                      <p className="mt-2 text-xs text-slate-500">
                        Available: {Number.isFinite(selectedSellQuantity) ? selectedSellQuantity : 0} share{selectedSellQuantity === 1 ? "" : "s"}
                        {Number.isFinite(selectedSellPrice) && selectedSellPrice > 0
                          ? ` • ${formatPrice(selectedSellPrice)}`
                          : ""}
                      </p>
                    </>
                  ) : (
                    <div className="rounded-xl border border-dashed border-slate-700 px-4 py-3 text-sm text-slate-500">
                      No holdings available to sell.
                    </div>
                  )}
                </div>

                {/* QUANTITY */}
                <div>
                  <label className="mb-2 block text-xs text-slate-500">Quantity</label>
                  <input
                    type="number"
                    min="1"
                    max={paperPositions.length > 0 && selectedSellSymbol ? selectedSellQuantity : undefined}
                    step="1"
                    value={paperQuantity}
                    onChange={(e) => setPaperQuantity(e.target.value)}
                    className="w-full rounded-xl border border-slate-700 bg-slate-800 px-4 py-3 text-white outline-none focus:border-blue-500"
                  />
                </div>

                {/* BUY */}
                <button
                  onClick={() => handlePaperOrder("BUY", data.symbol, Number(data.price))}
                  disabled={paperOrdering}
                  className="rounded-xl bg-green-600 px-7 py-3 font-semibold text-white transition hover:bg-green-700 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  {paperOrdering && paperOrderSide === "BUY"
                    ? "Buying..."
                    : `BUY ${data.symbol}`}
                </button>

                {/* SELL SELECTED */}
                <button
                  onClick={() =>
                    handlePaperOrder(
                      "SELL",
                      selectedSellSymbol,
                      selectedSellPrice
                    )
                  }
                  disabled={paperOrdering || !selectedSellSymbol || paperPositions.length === 0}
                  className="rounded-xl bg-red-600 px-7 py-3 font-semibold text-white transition hover:bg-red-700 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  {paperOrdering && paperOrderSide === "SELL"
                    ? "Selling..."
                    : selectedSellSymbol
                    ? `SELL ${selectedSellSymbol}`
                    : "SELL HOLDING"}
                </button>
              </div>

              {/* SELECTED HOLDING SUMMARY */}
              {selectedSellPosition && (
                <div className="mt-4 flex flex-wrap items-center gap-3 rounded-xl border border-slate-800 bg-slate-900 px-4 py-3 text-xs">
                  <span className="font-semibold text-white">Selected to sell: {selectedSellSymbol}</span>
                  <span className="text-slate-500">•</span>
                  <span className="text-slate-400">
                    {selectedSellQuantity} share{selectedSellQuantity === 1 ? "" : "s"} available
                  </span>
                  <span className="text-slate-500">•</span>
                  <span className="text-blue-400">
                    Live {formatPrice(selectedSellPrice)}
                  </span>
                </div>
              )}
            </div>

            {(paperAccount?.positions?.length ?? 0) > 0 && (
              <div className="mt-5 overflow-x-auto">
                <h3 className="mb-3 font-semibold text-white">Paper Positions</h3>
                <table className="w-full min-w-[800px] text-left">
                  <thead><tr className="border-b border-slate-800 text-xs text-slate-500"><th className="px-3 py-3">Symbol</th><th className="px-3 py-3">Qty</th><th className="px-3 py-3">Avg Price</th><th className="px-3 py-3">Live Price</th><th className="px-3 py-3">Invested</th><th className="px-3 py-3">P&L</th></tr></thead>
                  <tbody>
                    {paperAccount.positions.map((position: any) => (
                      <tr key={position.symbol} className="border-b border-slate-800 last:border-0">
                        <td className="px-3 py-3 font-semibold text-white">{position.symbol}</td>
                        <td className="px-3 py-3 text-slate-300">{position.quantity}</td>
                        <td className="px-3 py-3 text-slate-300">{formatPrice(Number(position.average_price))}</td>
                        <td className="px-3 py-3 text-blue-400">{formatPrice(Number(position.current_price))}</td>
                        <td className="px-3 py-3 text-slate-300">{formatPrice(Number(position.invested_value))}</td>
                        <td className={`px-3 py-3 font-semibold ${Number(position.unrealized_pnl) >= 0 ? "text-green-400" : "text-red-400"}`}>{formatSignedNumber(Number(position.unrealized_pnl))}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </>
        )}
      </div>

      {/* ========================================================
          CHART
      ======================================================== */}

      <div className="mt-6">

        <ChartCard
          symbol={symbol}
        />

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
            data.price >
            data.indicators.EMA20
              ? "Bullish"
              : "Bearish"
          }
        />

        <IndicatorCard
          title="EMA50"
          value={data.indicators.EMA50.toFixed(2)}
          status={
            data.price >
            data.indicators.EMA50
              ? "Bullish"
              : "Bearish"
          }
        />

        <IndicatorCard
          title="Recommendation"
          value={
            recommendation.recommendation
          }
          status={
            recommendation.recommendation === "BUY"
              ? "Bullish"
              : recommendation.recommendation === "SELL"
              ? "Bearish"
              : "Neutral"
          }
        />

      </div>

      {/* ========================================================
          AI ANALYSIS OVERVIEW
      ======================================================== */}

      <div className="mt-6 grid gap-6 xl:grid-cols-3">

        {/* ====================================================
            AI SCORE
        ==================================================== */}

        <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6 shadow-lg">

          <div className="flex items-center justify-between">

            <p className="text-sm text-slate-400">
              AI Analysis Score
            </p>

            <span className="rounded-lg bg-blue-500/10 px-2.5 py-1 text-xs font-semibold text-blue-400">
              AI
            </span>

          </div>

          <div className="mt-3 flex items-end gap-3">

            <span
              className={`text-5xl font-bold ${recommendationColor}`}
            >

              {recommendation.score > 0
                ? "+"
                : ""}

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
                className={`h-full rounded-full ${recommendationBg}`}
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

          {/* ==================================================
              AI REASONS
          ================================================== */}

          {recommendation.reasons &&
            recommendation.reasons.length > 0 && (

              <div className="mt-5">

                <p className="mb-2 text-xs text-slate-500">
                  Decision Factors
                </p>

                <div className="space-y-2">

                  {recommendation.reasons
                    .slice(0, 5)
                    .map(
                      (reason, index) => (

                        <div
                          key={index}
                          className="rounded-lg bg-slate-950 px-3 py-2 text-xs text-slate-300"
                        >
                          <span className="mr-2 text-blue-400">
                            ✓
                          </span>

                          {reason}
                        </div>

                      )
                    )}

                </div>

              </div>
            )}

        </div>

        {/* ====================================================
            MARKET STRUCTURE
        ==================================================== */}

        <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6 shadow-lg">

          <p className="text-sm text-slate-400">
            Market Structure
          </p>

          {marketStructure ? (

            <>

              <div className="mt-3 flex items-center justify-between gap-3">

                <h3
                  className={`text-2xl font-bold ${
                    marketStructure.signal ===
                    "BUY"
                      ? "text-green-400"
                      : marketStructure.signal ===
                        "SELL"
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
                    {marketStructure?.swing_counts?.higher_high ?? 0}
                  </p>

                </div>

                <div className="rounded-xl bg-slate-950 p-3">

                  <p className="text-xs text-slate-500">
                    Higher Low
                  </p>

                  <p className="mt-1 text-lg font-bold text-green-400">
                    {marketStructure?.swing_counts?.higher_low ?? 0}
                  </p>

                </div>

                <div className="rounded-xl bg-slate-950 p-3">

                  <p className="text-xs text-slate-500">
                    Lower High
                  </p>

                  <p className="mt-1 text-lg font-bold text-red-400">
                    {marketStructure?.swing_counts?.lower_high ?? 0}
                  </p>

                </div>

                <div className="rounded-xl bg-slate-950 p-3">

                  <p className="text-xs text-slate-500">
                    Lower Low
                  </p>

                  <p className="mt-1 text-lg font-bold text-red-400">
                    {marketStructure?.swing_counts?.lower_low ?? 0}
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

        {/* ====================================================
            SUPPORT / RESISTANCE
        ==================================================== */}

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

                {(supportResistance.support ?? []).map(
                  (level, index) => (

                    <span
                      key={`support-${index}`}
                      className="rounded-lg bg-green-950/40 px-3 py-1.5 text-xs font-medium text-green-400"
                    >
                      S {formatPrice(level)}
                    </span>

                  )
                )}

                {(supportResistance.resistance ?? []).map(
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
                  marketStructure.signal ===
                  "BUY"
                    ? "bg-green-950/50 text-green-400"
                    : marketStructure.signal ===
                      "SELL"
                    ? "bg-red-950/50 text-red-400"
                    : "bg-yellow-950/50 text-yellow-400"
                }`}
              >
                {marketStructure.signal}
              </span>

              <span className="rounded-xl border border-slate-700 bg-slate-800 px-4 py-2 text-sm text-slate-300">

                {marketStructure.confidence}%
                confidence

              </span>

            </div>

          </div>

          <div className="mt-5 grid gap-3 md:grid-cols-2">

            {(marketStructure?.reasons ?? []).map(
              (reason, index) => (

                <div
                  key={index}
                  className="rounded-xl border border-slate-800 bg-slate-950 px-4 py-3 text-sm text-slate-300"
                >

                  <span className="mr-2 text-green-400">
                    ✓
                  </span>

                  {reason}

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

                {(supportResistance.support ?? []).length > 0 ? (

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

                {(supportResistance.resistance ?? []).length > 0 ? (

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
          SMART MONEY CONCEPTS
      ======================================================== */}

      {smc && (
        <div className="mt-6 rounded-2xl border border-slate-800 bg-slate-900 p-6 shadow-lg">
          <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
            <div>
              <p className="text-sm text-slate-400">
                Smart Money Concepts
              </p>
              <h2 className="mt-1 text-2xl font-bold text-white">
                Institutional Market Analysis
              </h2>
              <p className="mt-1 text-sm text-slate-500">
                Directional SMC bias, structure, zones and liquidity are evaluated separately from an executable SMC setup.
              </p>
            </div>

            <div className="flex flex-wrap items-center gap-3">
              <span
                className={`rounded-xl px-4 py-2 text-sm font-bold ${
                  smcData.signal === "BUY"
                    ? "bg-green-950/50 text-green-400"
                    : smcData.signal === "SELL"
                    ? "bg-red-950/50 text-red-400"
                    : "bg-yellow-950/50 text-yellow-400"
                }`}
              >
                {smcData.signal ?? "HOLD"}
              </span>

              <span className="rounded-xl border border-slate-700 bg-slate-800 px-4 py-2 text-sm text-slate-300">
                {typeof smcData.confidence === "number"
                  ? `${smcData.confidence}% confidence`
                  : "—"}
              </span>
            </div>
          </div>

          {/* ==================================================
              SMC SCORE SUMMARY
          ================================================== */}

          <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
            <div className="rounded-xl border border-slate-800 bg-slate-950 p-4">
              <p className="text-xs text-slate-500">Market Bias</p>
              <p
                className={`mt-2 text-lg font-bold ${
                  smcData.market_bias === "BULLISH"
                    ? "text-green-400"
                    : smcData.market_bias === "BEARISH"
                    ? "text-red-400"
                    : "text-yellow-400"
                }`}
              >
                {smcData.market_bias ?? "NEUTRAL"}
              </p>
            </div>

            <div className="rounded-xl border border-slate-800 bg-slate-950 p-4">
              <p className="text-xs text-slate-500">SMC Trend</p>
              <p className="mt-2 text-lg font-bold text-white">
                {smcData.trend ?? "NEUTRAL"}
              </p>
            </div>

            <div className="rounded-xl border border-slate-800 bg-slate-950 p-4">
              <p className="text-xs text-slate-500">Structure</p>
              <p className="mt-2 text-lg font-bold text-white">
                {smcData.structure ?? "Neutral"}
              </p>
            </div>

            <div className="rounded-xl border border-slate-800 bg-slate-950 p-4">
              <p className="text-xs text-slate-500">SMC Score</p>
              <p
                className={`mt-2 text-2xl font-bold ${
                  Number(smcData.score ?? 0) > 0
                    ? "text-green-400"
                    : Number(smcData.score ?? 0) < 0
                    ? "text-red-400"
                    : "text-yellow-400"
                }`}
              >
                {Number(smcData.score ?? 0) > 0 ? "+" : ""}
                {Number(smcData.score ?? 0)}
              </p>
            </div>

            <div className="rounded-xl border border-slate-800 bg-slate-950 p-4">
              <p className="text-xs text-slate-500">Confirmations</p>
              <p className="mt-2 text-lg font-bold text-white">
                <span className="text-green-400">
                  {smcData.bullish_score ?? 0} Bullish
                </span>
                <span className="mx-1 text-slate-600">/</span>
                <span className="text-red-400">
                  {smcData.bearish_score ?? 0} Bearish
                </span>
              </p>
            </div>
          </div>

          {/* ==================================================
              BOS / CHOCH
          ================================================== */}

          <div className="mt-5 grid gap-4 md:grid-cols-2">
            <div className="rounded-xl border border-slate-800 bg-slate-950 p-4">
              <p className="text-xs text-slate-500">
                Break of Structure (BOS)
              </p>
              <p
                className={`mt-2 text-sm font-semibold ${
                  smcData.break_of_structure?.detected
                    ? smcData.break_of_structure.type === "BULLISH_BOS"
                      ? "text-green-400"
                      : "text-red-400"
                    : "text-slate-300"
                }`}
              >
                {smcData.break_of_structure?.detected
                  ? smcData.break_of_structure.type === "BULLISH_BOS"
                    ? "Bullish BOS detected"
                    : "Bearish BOS detected"
                  : "Not detected"}
              </p>
              <p className="mt-2 text-xs text-slate-500">
                {smcData.break_of_structure?.reason ??
                  "No recent Break of Structure detected."}
              </p>
            </div>

            <div className="rounded-xl border border-slate-800 bg-slate-950 p-4">
              <p className="text-xs text-slate-500">
                Change of Character (CHOCH)
              </p>
              <p
                className={`mt-2 text-sm font-semibold ${
                  smcData.change_of_character?.detected
                    ? smcData.change_of_character.type === "BULLISH_CHOCH"
                      ? "text-green-400"
                      : "text-red-400"
                    : "text-slate-300"
                }`}
              >
                {smcData.change_of_character?.detected
                  ? smcData.change_of_character.type === "BULLISH_CHOCH"
                    ? "Bullish CHOCH detected"
                    : "Bearish CHOCH detected"
                  : "Not detected"}
              </p>
              <p className="mt-2 text-xs text-slate-500">
                {smcData.change_of_character?.reason ??
                  "No clear recent Change of Character detected."}
              </p>
            </div>
          </div>

          {/* ==================================================
              PRICE-RELEVANT SMART MONEY ZONES
          ================================================== */}

          <div className="mt-5 grid gap-4 md:grid-cols-3">
            {/* ORDER BLOCKS */}
            <div className="rounded-xl border border-slate-800 bg-slate-950 p-4">
              <p className="text-xs text-slate-500">Order Blocks</p>

              <div className="mt-3 grid grid-cols-2 gap-2">
                <div className="rounded-lg bg-green-950/30 p-3">
                  <p className="text-xs text-slate-500">Bullish</p>
                  <p className="mt-1 text-xl font-bold text-green-400">
                    {smcData.relevant_order_blocks?.bullish?.length ?? 0}
                  </p>
                  <p className="text-[11px] text-slate-500">relevant</p>
                </div>

                <div className="rounded-lg bg-red-950/30 p-3">
                  <p className="text-xs text-slate-500">Bearish</p>
                  <p className="mt-1 text-xl font-bold text-red-400">
                    {smcData.relevant_order_blocks?.bearish?.length ?? 0}
                  </p>
                  <p className="text-[11px] text-slate-500">relevant</p>
                </div>
              </div>

              <p className="mt-3 text-xs text-slate-500">
                Historical: {(
                  (smcData.order_blocks?.bullish?.length ?? 0) +
                  (smcData.order_blocks?.bearish?.length ?? 0)
                )} zones
              </p>
            </div>

            {/* FAIR VALUE GAPS */}
            <div className="rounded-xl border border-slate-800 bg-slate-950 p-4">
              <p className="text-xs text-slate-500">Fair Value Gaps</p>

              <div className="mt-3 grid grid-cols-2 gap-2">
                <div className="rounded-lg bg-green-950/30 p-3">
                  <p className="text-xs text-slate-500">Bullish</p>
                  <p className="mt-1 text-xl font-bold text-green-400">
                    {smcData.relevant_fair_value_gaps?.bullish?.length ?? 0}
                  </p>
                  <p className="text-[11px] text-slate-500">relevant</p>
                </div>

                <div className="rounded-lg bg-red-950/30 p-3">
                  <p className="text-xs text-slate-500">Bearish</p>
                  <p className="mt-1 text-xl font-bold text-red-400">
                    {smcData.relevant_fair_value_gaps?.bearish?.length ?? 0}
                  </p>
                  <p className="text-[11px] text-slate-500">relevant</p>
                </div>
              </div>

              <p className="mt-3 text-xs text-slate-500">
                Historical: {(
                  (smcData.fair_value_gaps?.bullish?.length ?? 0) +
                  (smcData.fair_value_gaps?.bearish?.length ?? 0)
                )} gaps
              </p>
            </div>

            {/* LIQUIDITY */}
            <div className="rounded-xl border border-slate-800 bg-slate-950 p-4">
              <p className="text-xs text-slate-500">Liquidity</p>

              <div className="mt-3 grid grid-cols-2 gap-2">
                <div className="rounded-lg bg-green-950/30 p-3">
                  <p className="text-xs text-slate-500">Buy-side</p>
                  <p className="mt-1 text-xl font-bold text-green-400">
                    {smcData.relevant_liquidity?.buy_side?.length ?? 0}
                  </p>
                  <p className="text-[11px] text-slate-500">nearby</p>
                </div>

                <div className="rounded-lg bg-red-950/30 p-3">
                  <p className="text-xs text-slate-500">Sell-side</p>
                  <p className="mt-1 text-xl font-bold text-red-400">
                    {smcData.relevant_liquidity?.sell_side?.length ?? 0}
                  </p>
                  <p className="text-[11px] text-slate-500">nearby</p>
                </div>
              </div>

              <p className="mt-3 text-xs text-slate-500">
                Current price: {formatPrice(smcData.current_price ?? data.price)}
              </p>
            </div>
          </div>

          {/* ==================================================
              SETUPS
          ================================================== */}

          <div className="mt-5 grid gap-4 md:grid-cols-2">
            <div className="rounded-xl border border-slate-800 bg-slate-950 p-4">
              <p className="text-xs text-slate-500">Bullish SMC Setup</p>
              <p className="mt-2 font-bold text-slate-500">
                Not detected
              </p>
              <p className="mt-2 text-xs text-slate-500">
                No confirmed executable bullish SMC setup is present. Historical bullish zones alone are not treated as trade confirmation.
              </p>
            </div>

            <div className="rounded-xl border border-slate-800 bg-slate-950 p-4">
              <p className="text-xs text-slate-500">Bearish SMC Setup</p>
              <p className="mt-2 font-bold text-slate-500">
                Not detected
              </p>
              <p className="mt-2 text-xs text-slate-500">
                SMC can still show a bearish directional bias from BOS/CHOCH and other evidence, but this card only marks a fully confirmed executable SMC setup.
              </p>
            </div>
          </div>

          {/* ==================================================
              SMC REASONS
          ================================================== */}

          {Array.isArray(smcData.reasons) && smcData.reasons.length > 0 && (
            <div className="mt-5">
              <p className="mb-3 text-sm font-semibold text-slate-300">
                SMC Analysis
              </p>

              <div className="grid gap-3 md:grid-cols-2">
                {smcData.reasons.map(
                  (reason: string, index: number) => (
                    <div
                      key={index}
                      className="rounded-xl border border-slate-800 bg-slate-950 px-4 py-3 text-sm text-slate-300"
                    >
                      <span className="mr-2 text-blue-400">✓</span>
                      {reason}
                    </div>
                  )
                )}
              </div>
            </div>
          )}
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

        <PatternCard
          pattern={data.pattern}
        />

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