"use client";

import { useEffect, useState } from "react";
import api from "@/lib/api";
import DashboardLayout from "@/components/dashboard/DashboardLayout";

interface PaperAccount {
  cash?: number;
  available_cash?: number;
  invested_value?: number;
  current_value?: number;
  total_equity?: number;
  total_pnl?: number;
  pnl_percent?: number;
  positions?: any[];
  trades?: any[];
  history?: any[];
  orders?: any[];
  [key: string]: any;
}

function money(value: unknown) {
  const n = Number(value);

  if (!Number.isFinite(n)) return "—";

  return `₹${n.toLocaleString("en-IN", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}`;
}

function percent(value: unknown) {
  const n = Number(value);

  if (!Number.isFinite(n)) return "—";

  return `${n >= 0 ? "+" : ""}${n.toFixed(2)}%`;
}

export default function TradeHistoryPage() {
  const [account, setAccount] =
    useState<PaperAccount | null>(null);

  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] =
    useState(false);

  const [error, setError] = useState("");

  const loadAccount = async (
    background = false
  ) => {
    try {
      if (background) {
        setRefreshing(true);
      } else {
        setLoading(true);
      }

      setError("");

      const response = await api.get(
        "/paper-trading/account"
      );

      setAccount(response.data);
    } catch (err: any) {
      console.error(
        "Paper trading account failed:",
        err?.response?.data || err
      );

      setError(
        err?.response?.data?.detail ||
          "Unable to load paper trading account."
      );
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    loadAccount();
  }, []);

  const history =
    account?.trades ||
    account?.history ||
    account?.orders ||
    [];

  const positions =
    Array.isArray(account?.positions)
      ? account.positions
      : [];

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* HEADER */}
        <div className="flex flex-col justify-between gap-4 md:flex-row md:items-center">
          <div>
            <h1 className="text-2xl font-bold text-white">
              Trade History
            </h1>

            <p className="mt-1 text-sm text-slate-400">
              Review your MarketIQ paper-trading activity
              and current simulated positions.
            </p>
          </div>

          <button
            type="button"
            onClick={() => loadAccount(true)}
            disabled={loading || refreshing}
            className="rounded-xl border border-slate-700 bg-slate-900 px-5 py-3 text-sm font-semibold text-white hover:bg-slate-800 disabled:opacity-50"
          >
            {refreshing
              ? "Refreshing..."
              : "Refresh"}
          </button>
        </div>

        {error && (
          <section className="rounded-2xl border border-red-900/50 bg-red-950/30 p-5">
            <p className="font-semibold text-red-300">
              Unable to load paper trading data
            </p>

            <p className="mt-1 text-sm text-red-200">
              {error}
            </p>
          </section>
        )}

        {loading ? (
          <section className="rounded-2xl border border-slate-800 bg-slate-900 p-10 text-center">
            <div className="mx-auto h-10 w-10 animate-spin rounded-full border-4 border-slate-700 border-t-blue-500" />

            <p className="mt-4 text-white">
              Loading paper trading data...
            </p>
          </section>
        ) : (
          <>
            {/* ACCOUNT SUMMARY */}
            <section>
              <h2 className="mb-3 text-lg font-semibold text-white">
                Paper Trading Account
              </h2>

              <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
                <Summary
                  title="Available Cash"
                  value={money(
                    account?.cash ??
                      account?.available_cash
                  )}
                />

                <Summary
                  title="Invested Value"
                  value={money(
                    account?.invested_value
                  )}
                />

                <Summary
                  title="Current Value"
                  value={money(
                    account?.current_value
                  )}
                />

                <Summary
                  title="Total Equity"
                  value={money(
                    account?.total_equity
                  )}
                />

                <Summary
                  title="Total P&L"
                  value={money(
                    account?.total_pnl
                  )}
                  subvalue={percent(
                    account?.pnl_percent
                  )}
                />
              </div>
            </section>

            {/* TRADE HISTORY */}
            <section className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-lg font-semibold text-white">
                    Paper Trade History
                  </h2>

                  <p className="mt-1 text-sm text-slate-400">
                    Executed simulated BUY and SELL activity.
                  </p>
                </div>

                <span className="rounded-full border border-slate-700 bg-slate-950 px-3 py-1 text-xs text-slate-400">
                  {history.length} record
                  {history.length === 1 ? "" : "s"}
                </span>
              </div>

              {history.length === 0 ? (
                <div className="mt-6 rounded-xl border border-dashed border-slate-700 p-8 text-center">
                  <p className="font-medium text-white">
                    No completed trade history available.
                  </p>

                  <p className="mt-2 text-sm text-slate-500">
                    Paper BUY/SELL activity will appear here
                    when the backend provides transaction
                    records.
                  </p>
                </div>
              ) : (
                <div className="mt-5 overflow-x-auto">
                  <table className="w-full min-w-[760px] text-left text-sm">
                    <thead>
                      <tr className="border-b border-slate-800 text-slate-500">
                        <th className="px-3 py-3">
                          Date
                        </th>

                        <th className="px-3 py-3">
                          Symbol
                        </th>

                        <th className="px-3 py-3">
                          Side
                        </th>

                        <th className="px-3 py-3">
                          Quantity
                        </th>

                        <th className="px-3 py-3">
                          Price
                        </th>

                        <th className="px-3 py-3">
                          P&L
                        </th>
                      </tr>
                    </thead>

                    <tbody>
                      {history.map(
                        (trade: any, index: number) => {
                          const side = String(
                            trade?.side ||
                              trade?.action ||
                              "—"
                          ).toUpperCase();

                          const pnl = Number(
                            trade?.pnl ??
                              trade?.profit_loss ??
                              trade?.profitLoss
                          );

                          return (
                            <tr
                              key={
                                trade?.id ??
                                trade?.trade_id ??
                                index
                              }
                              className="border-b border-slate-800/70"
                            >
                              <td className="px-3 py-3 text-slate-300">
                                {trade?.date ||
                                  trade?.timestamp ||
                                  trade?.created_at ||
                                  "—"}
                              </td>

                              <td className="px-3 py-3 font-semibold text-white">
                                {trade?.symbol ||
                                  "—"}
                              </td>

                              <td
                                className={`px-3 py-3 font-semibold ${
                                  side === "BUY"
                                    ? "text-emerald-400"
                                    : side === "SELL"
                                      ? "text-red-400"
                                      : "text-slate-300"
                                }`}
                              >
                                {side}
                              </td>

                              <td className="px-3 py-3 text-slate-300">
                                {trade?.quantity ??
                                  "—"}
                              </td>

                              <td className="px-3 py-3 text-slate-300">
                                {money(
                                  trade?.price ??
                                    trade?.entry_price
                                )}
                              </td>

                              <td
                                className={`px-3 py-3 font-semibold ${
                                  Number.isFinite(pnl)
                                    ? pnl >= 0
                                      ? "text-emerald-400"
                                      : "text-red-400"
                                    : "text-slate-400"
                                }`}
                              >
                                {money(pnl)}
                              </td>
                            </tr>
                          );
                        }
                      )}
                    </tbody>
                  </table>
                </div>
              )}
            </section>

            {/* CURRENT POSITIONS */}
            <section className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
              <h2 className="text-lg font-semibold text-white">
                Current Paper Positions
              </h2>

              <p className="mt-1 text-sm text-slate-400">
                Your currently open simulated holdings.
              </p>

              {positions.length === 0 ? (
                <div className="mt-5 rounded-xl border border-dashed border-slate-700 p-8 text-center">
                  <p className="text-slate-400">
                    No open paper positions.
                  </p>
                </div>
              ) : (
                <div className="mt-5 grid gap-4 md:grid-cols-2">
                  {positions.map(
                    (position: any, index: number) => (
                      <div
                        key={
                          position?.id ??
                          position?.symbol ??
                          index
                        }
                        className="rounded-xl border border-slate-800 bg-slate-950 p-5"
                      >
                        <div className="flex justify-between">
                          <p className="font-bold text-white">
                            {position?.symbol ||
                              "—"}
                          </p>

                          <p className="text-sm text-slate-400">
                            Qty:{" "}
                            {position?.quantity ??
                              "—"}
                          </p>
                        </div>

                        <div className="mt-4 grid grid-cols-2 gap-3">
                          <PositionValue
                            title="Average Price"
                            value={money(
                              position?.average_price ??
                                position?.avg_price
                            )}
                          />

                          <PositionValue
                            title="Current Price"
                            value={money(
                              position?.current_price ??
                                position?.live_price
                            )}
                          />

                          <PositionValue
                            title="Invested"
                            value={money(
                              position?.invested_value
                            )}
                          />

                          <PositionValue
                            title="P&L"
                            value={money(
                              position?.pnl ??
                                position?.profit_loss
                            )}
                          />
                        </div>
                      </div>
                    )
                  )}
                </div>
              )}
            </section>
          </>
        )}
      </div>
    </DashboardLayout>
  );
}

function Summary({
  title,
  value,
  subvalue,
}: {
  title: string;
  value: string;
  subvalue?: string;
}) {
  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
      <p className="text-sm text-slate-400">
        {title}
      </p>

      <p className="mt-2 text-xl font-bold text-white">
        {value}
      </p>

      {subvalue && (
        <p className="mt-1 text-xs text-slate-500">
          {subvalue}
        </p>
      )}
    </div>
  );
}

function PositionValue({
  title,
  value,
}: {
  title: string;
  value: string;
}) {
  return (
    <div className="rounded-lg border border-slate-800 p-3">
      <p className="text-xs text-slate-500">
        {title}
      </p>

      <p className="mt-1 text-sm font-semibold text-white">
        {value}
      </p>
    </div>
  );
}