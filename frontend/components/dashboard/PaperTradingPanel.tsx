"use client";

import { useEffect, useState } from "react";
import api from "@/lib/api";

interface Position {
  symbol: string;
  quantity: number;
  average_price: number;
  current_price: number;
  invested_value: number;
  current_value: number;
  unrealized_pnl: number;
  unrealized_pnl_percentage: number;
}

interface Trade {
  id: string;
  symbol: string;
  side: string;
  quantity: number;
  price: number;
  total_value: number;
  realized_pnl: number;
  status: string;
  notes?: string;
  executed_at: string;
}

interface PaperAccount {
  initial_capital: number;
  available_cash: number;
  invested_value: number;
  current_value: number;
  total_equity: number;
  realized_pnl: number;
  unrealized_pnl: number;
  total_pnl: number;
  total_pnl_percentage: number;
  positions: Position[];
  recent_trades: Trade[];
}

interface PaperTradingPanelProps {
  selectedSymbol?: string;
  currentPrice?: number;
}

export default function PaperTradingPanel({
  selectedSymbol = "RELIANCE",
  currentPrice = 0,
}: PaperTradingPanelProps) {
  const [account, setAccount] =
    useState<PaperAccount | null>(null);

  const [symbol, setSymbol] =
    useState(selectedSymbol);

  const [quantity, setQuantity] =
    useState(1);

  const [price, setPrice] =
    useState(currentPrice);

  const [side, setSide] =
    useState<"BUY" | "SELL">("BUY");

  const [loading, setLoading] =
    useState(false);

  const [loadingAccount, setLoadingAccount] =
    useState(true);

  const [message, setMessage] =
    useState("");

  const [error, setError] =
    useState("");

  useEffect(() => {
    setSymbol(selectedSymbol);
  }, [selectedSymbol]);

  useEffect(() => {
    if (currentPrice > 0) {
      setPrice(currentPrice);
    }
  }, [currentPrice]);

  // ============================================================
  // LOAD ACCOUNT
  // ============================================================

  const loadAccount = async () => {
    try {
      setLoadingAccount(true);
      setError("");

      const response =
        await api.get<PaperAccount>(
          "/paper-trading/account"
        );

      setAccount(response.data);
    } catch (err: any) {
      console.error(
        "Paper trading account error:",
        err
      );

      setError(
        err?.response?.data?.detail ||
          "Unable to load paper trading account."
      );
    } finally {
      setLoadingAccount(false);
    }
  };

  useEffect(() => {
    loadAccount();
  }, []);

  // ============================================================
  // EXECUTE ORDER
  // ============================================================

  const executeOrder = async () => {
    try {
      setLoading(true);
      setError("");
      setMessage("");

      const cleanSymbol =
        symbol.trim().toUpperCase();

      if (!cleanSymbol) {
        setError(
          "Please enter a stock symbol."
        );
        return;
      }

      if (quantity <= 0) {
        setError(
          "Quantity must be greater than zero."
        );
        return;
      }

      const payload: {
        symbol: string;
        side: string;
        quantity: number;
        price?: number;
      } = {
        symbol: cleanSymbol,
        side,
        quantity,
      };

      if (price > 0) {
        payload.price = price;
      }

      const response =
        await api.post(
          "/paper-trading/order",
          payload
        );

      setMessage(
        response?.data?.message ||
          `${side} order executed successfully.`
      );

      await loadAccount();
    } catch (err: any) {
      console.error(
        "Paper trading order error:",
        err
      );

      setError(
        err?.response?.data?.detail ||
          "Unable to execute paper trading order."
      );
    } finally {
      setLoading(false);
    }
  };

  // ============================================================
  // RESET ACCOUNT
  // ============================================================

  const resetAccount = async () => {
    const confirmed =
      window.confirm(
        "Reset paper trading account to ₹1,00,000? This will remove all paper positions and trade history."
      );

    if (!confirmed) {
      return;
    }

    try {
      setLoading(true);
      setError("");
      setMessage("");

      await api.post(
        "/paper-trading/reset"
      );

      setMessage(
        "Paper trading account reset successfully."
      );

      await loadAccount();
    } catch (err: any) {
      console.error(
        "Paper trading reset error:",
        err
      );

      setError(
        err?.response?.data?.detail ||
          "Unable to reset paper trading account."
      );
    } finally {
      setLoading(false);
    }
  };

  // ============================================================
  // FORMATTERS
  // ============================================================

  const money = (value: number) =>
    new Intl.NumberFormat(
      "en-IN",
      {
        style: "currency",
        currency: "INR",
        maximumFractionDigits: 2,
      }
    ).format(value || 0);

  const percentage = (value: number) =>
    `${value >= 0 ? "+" : ""}${(
      value || 0
    ).toFixed(2)}%`;

  // ============================================================
  // LOADING
  // ============================================================

  if (loadingAccount) {
    return (
      <section className="rounded-2xl border border-slate-800 bg-slate-950 p-6">
        <div className="animate-pulse">
          <div className="mb-4 h-6 w-48 rounded bg-slate-800" />
          <div className="h-20 rounded-xl bg-slate-900" />
        </div>
      </section>
    );
  }

  return (
    <section className="space-y-6 rounded-2xl border border-slate-800 bg-slate-950 p-6 text-white">

      {/* ========================================================
          HEADER
      ======================================================== */}

      <div className="flex flex-col justify-between gap-4 md:flex-row md:items-center">

        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-xl font-bold">
              Paper Trading
            </h2>

            <span className="rounded-full bg-emerald-500/10 px-2 py-1 text-xs font-semibold text-emerald-400">
              LIVE
            </span>
          </div>

          <p className="mt-1 text-sm text-slate-400">
            Practice trading with virtual capital
            without risking real money.
          </p>
        </div>

        <button
          type="button"
          onClick={resetAccount}
          disabled={loading}
          className="rounded-lg border border-red-500/30 px-4 py-2 text-sm font-medium text-red-400 transition hover:bg-red-500/10 disabled:cursor-not-allowed disabled:opacity-50"
        >
          Reset Account
        </button>
      </div>

      {/* ========================================================
          ACCOUNT SUMMARY
      ======================================================== */}

      {account && (
        <div className="grid grid-cols-2 gap-3 md:grid-cols-4">

          <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-4">
            <p className="text-xs text-slate-400">
              Available Cash
            </p>

            <p className="mt-2 text-lg font-bold">
              {money(account.available_cash)}
            </p>
          </div>

          <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-4">
            <p className="text-xs text-slate-400">
              Invested Value
            </p>

            <p className="mt-2 text-lg font-bold">
              {money(account.invested_value)}
            </p>
          </div>

          <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-4">
            <p className="text-xs text-slate-400">
              Total Equity
            </p>

            <p className="mt-2 text-lg font-bold">
              {money(account.total_equity)}
            </p>
          </div>

          <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-4">
            <p className="text-xs text-slate-400">
              Total P&L
            </p>

            <p
              className={`mt-2 text-lg font-bold ${
                account.total_pnl >= 0
                  ? "text-emerald-400"
                  : "text-red-400"
              }`}
            >
              {money(account.total_pnl)}
            </p>

            <p
              className={`text-xs ${
                account.total_pnl_percentage >= 0
                  ? "text-emerald-400"
                  : "text-red-400"
              }`}
            >
              {percentage(
                account.total_pnl_percentage
              )}
            </p>
          </div>
        </div>
      )}

      {/* ========================================================
          ORDER PANEL
      ======================================================== */}

      <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-5">

        <div className="mb-5">
          <h3 className="font-semibold">
            Place Paper Order
          </h3>

          <p className="mt-1 text-xs text-slate-400">
            Orders use virtual money and do not
            interact with your real broker account.
          </p>
        </div>

        <div className="grid gap-4 md:grid-cols-4">

          {/* SYMBOL */}

          <div>
            <label className="mb-2 block text-xs font-medium text-slate-400">
              Symbol
            </label>

            <input
              value={symbol}
              onChange={(event) =>
                setSymbol(
                  event.target.value.toUpperCase()
                )
              }
              placeholder="RELIANCE"
              className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2.5 text-sm outline-none transition focus:border-cyan-500"
            />
          </div>

          {/* QUANTITY */}

          <div>
            <label className="mb-2 block text-xs font-medium text-slate-400">
              Quantity
            </label>

            <input
              type="number"
              min="1"
              value={quantity}
              onChange={(event) =>
                setQuantity(
                  Number(event.target.value)
                )
              }
              className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2.5 text-sm outline-none transition focus:border-cyan-500"
            />
          </div>

          {/* PRICE */}

          <div>
            <label className="mb-2 block text-xs font-medium text-slate-400">
              Execution Price
            </label>

            <input
              type="number"
              min="0"
              step="0.01"
              value={price}
              onChange={(event) =>
                setPrice(
                  Number(event.target.value)
                )
              }
              placeholder="Market price"
              className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2.5 text-sm outline-none transition focus:border-cyan-500"
            />
          </div>

          {/* SIDE */}

          <div>
            <label className="mb-2 block text-xs font-medium text-slate-400">
              Direction
            </label>

            <div className="grid grid-cols-2 gap-2">
              <button
                type="button"
                onClick={() =>
                  setSide("BUY")
                }
                className={`rounded-lg px-3 py-2.5 text-sm font-semibold transition ${
                  side === "BUY"
                    ? "bg-emerald-500 text-white"
                    : "border border-slate-700 bg-slate-950 text-slate-400 hover:text-white"
                }`}
              >
                BUY
              </button>

              <button
                type="button"
                onClick={() =>
                  setSide("SELL")
                }
                className={`rounded-lg px-3 py-2.5 text-sm font-semibold transition ${
                  side === "SELL"
                    ? "bg-red-500 text-white"
                    : "border border-slate-700 bg-slate-950 text-slate-400 hover:text-white"
                }`}
              >
                SELL
              </button>
            </div>
          </div>
        </div>

        {/* ORDER VALUE */}

        <div className="mt-4 rounded-lg border border-slate-800 bg-slate-950 p-4">
          <div className="flex items-center justify-between text-sm">
            <span className="text-slate-400">
              Estimated Order Value
            </span>

            <span className="font-semibold">
              {money(
                Math.max(price, 0) *
                  Math.max(quantity, 0)
              )}
            </span>
          </div>
        </div>

        {/* EXECUTE */}

        <button
          type="button"
          onClick={executeOrder}
          disabled={
            loading ||
            !symbol.trim() ||
            quantity <= 0
          }
          className={`mt-4 w-full rounded-lg px-4 py-3 text-sm font-bold transition disabled:cursor-not-allowed disabled:opacity-50 ${
            side === "BUY"
              ? "bg-emerald-500 hover:bg-emerald-400"
              : "bg-red-500 hover:bg-red-400"
          }`}
        >
          {loading
            ? "Processing..."
            : `Execute ${side} Order`}
        </button>

        {/* MESSAGES */}

        {message && (
          <div className="mt-4 rounded-lg border border-emerald-500/20 bg-emerald-500/10 p-3 text-sm text-emerald-400">
            {message}
          </div>
        )}

        {error && (
          <div className="mt-4 rounded-lg border border-red-500/20 bg-red-500/10 p-3 text-sm text-red-400">
            {error}
          </div>
        )}
      </div>

      {/* ========================================================
          POSITIONS
      ======================================================== */}

      <div>
        <div className="mb-4 flex items-center justify-between">
          <div>
            <h3 className="font-semibold">
              Open Positions
            </h3>

            <p className="text-xs text-slate-400">
              Your current virtual holdings
            </p>
          </div>

          <button
            type="button"
            onClick={loadAccount}
            disabled={loadingAccount}
            className="rounded-lg border border-slate-700 px-3 py-2 text-xs text-slate-300 hover:bg-slate-800"
          >
            Refresh
          </button>
        </div>

        {account?.positions?.length ? (
          <div className="overflow-x-auto rounded-xl border border-slate-800">
            <table className="w-full text-left text-sm">
              <thead className="bg-slate-900 text-xs text-slate-400">
                <tr>
                  <th className="px-4 py-3">
                    Symbol
                  </th>
                  <th className="px-4 py-3">
                    Qty
                  </th>
                  <th className="px-4 py-3">
                    Avg Price
                  </th>
                  <th className="px-4 py-3">
                    Live Price
                  </th>
                  <th className="px-4 py-3">
                    Current Value
                  </th>
                  <th className="px-4 py-3">
                    P&L
                  </th>
                </tr>
              </thead>

              <tbody>
                {account.positions.map(
                  (position) => (
                    <tr
                      key={position.symbol}
                      className="border-t border-slate-800"
                    >
                      <td className="px-4 py-3 font-semibold">
                        {position.symbol}
                      </td>

                      <td className="px-4 py-3">
                        {position.quantity}
                      </td>

                      <td className="px-4 py-3">
                        {money(
                          position.average_price
                        )}
                      </td>

                      <td className="px-4 py-3">
                        {money(
                          position.current_price
                        )}
                      </td>

                      <td className="px-4 py-3">
                        {money(
                          position.current_value
                        )}
                      </td>

                      <td
                        className={`px-4 py-3 font-semibold ${
                          position.unrealized_pnl >= 0
                            ? "text-emerald-400"
                            : "text-red-400"
                        }`}
                      >
                        {money(
                          position.unrealized_pnl
                        )}

                        <span className="ml-2 text-xs">
                          (
                          {percentage(
                            position.unrealized_pnl_percentage
                          )}
                          )
                        </span>
                      </td>
                    </tr>
                  )
                )}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="rounded-xl border border-dashed border-slate-800 bg-slate-900/30 p-8 text-center">
            <p className="text-sm font-medium text-slate-300">
              No open positions
            </p>

            <p className="mt-1 text-xs text-slate-500">
              Execute a BUY order to create your
              first paper-trading position.
            </p>
          </div>
        )}
      </div>

      {/* ========================================================
          RECENT TRADES
      ======================================================== */}

      <div>
        <h3 className="mb-4 font-semibold">
          Recent Trades
        </h3>

        {account?.recent_trades?.length ? (
          <div className="overflow-x-auto rounded-xl border border-slate-800">
            <table className="w-full text-left text-sm">
              <thead className="bg-slate-900 text-xs text-slate-400">
                <tr>
                  <th className="px-4 py-3">
                    Symbol
                  </th>
                  <th className="px-4 py-3">
                    Side
                  </th>
                  <th className="px-4 py-3">
                    Qty
                  </th>
                  <th className="px-4 py-3">
                    Price
                  </th>
                  <th className="px-4 py-3">
                    Value
                  </th>
                  <th className="px-4 py-3">
                    P&L
                  </th>
                  <th className="px-4 py-3">
                    Status
                  </th>
                </tr>
              </thead>

              <tbody>
                {account.recent_trades.map(
                  (trade) => (
                    <tr
                      key={trade.id}
                      className="border-t border-slate-800"
                    >
                      <td className="px-4 py-3 font-semibold">
                        {trade.symbol}
                      </td>

                      <td
                        className={`px-4 py-3 font-bold ${
                          trade.side === "BUY"
                            ? "text-emerald-400"
                            : "text-red-400"
                        }`}
                      >
                        {trade.side}
                      </td>

                      <td className="px-4 py-3">
                        {trade.quantity}
                      </td>

                      <td className="px-4 py-3">
                        {money(trade.price)}
                      </td>

                      <td className="px-4 py-3">
                        {money(
                          trade.total_value
                        )}
                      </td>

                      <td
                        className={`px-4 py-3 ${
                          trade.realized_pnl >= 0
                            ? "text-emerald-400"
                            : "text-red-400"
                        }`}
                      >
                        {money(
                          trade.realized_pnl
                        )}
                      </td>

                      <td className="px-4 py-3">
                        <span className="rounded-full bg-emerald-500/10 px-2 py-1 text-xs text-emerald-400">
                          {trade.status}
                        </span>
                      </td>
                    </tr>
                  )
                )}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="rounded-xl border border-dashed border-slate-800 p-6 text-center text-sm text-slate-500">
            No paper trades yet.
          </div>
        )}
      </div>
    </section>
  );
}