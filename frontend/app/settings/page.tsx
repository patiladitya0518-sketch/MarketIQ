"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import DashboardLayout from "@/components/dashboard/DashboardLayout";

export default function SettingsPage() {
  const router = useRouter();

  const [selectedStock, setSelectedStock] =
    useState("RELIANCE");

  const [saved, setSaved] = useState(false);

  useEffect(() => {
    const value =
      typeof window !== "undefined"
        ? localStorage.getItem(
            "marketiq_selected_stock"
          )
        : null;

    if (value?.trim()) {
      setSelectedStock(value.toUpperCase());
    }
  }, []);

  const savePreferences = () => {
    const clean = selectedStock
      .trim()
      .toUpperCase();

    if (!clean) return;

    localStorage.setItem(
      "marketiq_selected_stock",
      clean
    );

    setSelectedStock(clean);
    setSaved(true);

    window.setTimeout(() => {
      setSaved(false);
    }, 2000);
  };

  const logout = () => {
    localStorage.removeItem("access_token");
    router.replace("/login");
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* HEADER */}
        <div>
          <h1 className="text-2xl font-bold text-white">
            Settings
          </h1>

          <p className="mt-1 text-sm text-slate-400">
            Manage your MarketIQ application preferences.
          </p>
        </div>

        {/* STOCK PREFERENCE */}
        <section className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
          <h2 className="text-lg font-semibold text-white">
            Analysis Preferences
          </h2>

          <p className="mt-1 text-sm text-slate-400">
            Choose the stock that MarketIQ should remember
            for your next analysis.
          </p>

          <div className="mt-5 max-w-xl">
            <label className="mb-2 block text-sm font-medium text-slate-300">
              Default Stock
            </label>

            <input
              value={selectedStock}
              onChange={(event) =>
                setSelectedStock(
                  event.target.value.toUpperCase()
                )
              }
              className="w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none focus:border-blue-500"
              placeholder="RELIANCE"
            />

            <button
              type="button"
              onClick={savePreferences}
              disabled={!selectedStock.trim()}
              className="mt-4 rounded-xl bg-blue-600 px-5 py-3 font-semibold text-white hover:bg-blue-500 disabled:opacity-50"
            >
              Save Preference
            </button>

            {saved && (
              <p className="mt-3 text-sm font-medium text-emerald-400">
                Preference saved successfully.
              </p>
            )}
          </div>
        </section>

        {/* MARKETIQ INFO */}
        <section className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
          <h2 className="text-lg font-semibold text-white">
            MarketIQ
          </h2>

          <div className="mt-5 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            <Info
              title="Application"
              value="MarketIQ"
            />

            <Info
              title="Environment"
              value="Development"
            />

            <Info
              title="Market"
              value="Indian Equities"
            />

            <Info
              title="Analysis"
              value="AI + Technical"
            />

            <Info
              title="Trading Mode"
              value="Paper Trading"
            />

            <Info
              title="Backtesting"
              value="6M / 1Y / 2Y / 5Y"
            />
          </div>
        </section>

        {/* SYSTEM INFORMATION */}
        <section className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
          <h2 className="text-lg font-semibold text-white">
            System Features
          </h2>

          <div className="mt-5 space-y-3">
            {[
              "Technical indicators",
              "Market structure",
              "Support & resistance",
              "Smart Money Concepts",
              "AI BUY / SELL / HOLD recommendation",
              "V7.1 AI explanation",
              "Paper trading",
              "Historical backtesting",
            ].map((feature) => (
              <div
                key={feature}
                className="flex items-center gap-3 rounded-xl bg-slate-950 px-4 py-3"
              >
                <span className="flex h-6 w-6 items-center justify-center rounded-full bg-emerald-500/10 text-sm text-emerald-400">
                  ✓
                </span>

                <span className="text-sm text-slate-300">
                  {feature}
                </span>
              </div>
            ))}
          </div>
        </section>

        {/* ACCOUNT */}
        <section className="rounded-2xl border border-red-900/40 bg-slate-900 p-6">
          <h2 className="text-lg font-semibold text-white">
            Account
          </h2>

          <p className="mt-1 text-sm text-slate-400">
            Sign out of your current MarketIQ account.
          </p>

          <button
            type="button"
            onClick={logout}
            className="mt-5 rounded-xl border border-red-800 bg-red-950/30 px-5 py-3 font-semibold text-red-300 hover:bg-red-950/60"
          >
            Logout
          </button>
        </section>

        {/* DISCLAIMER */}
        <section className="rounded-2xl border border-slate-800 bg-slate-950 p-5">
          <p className="text-xs leading-5 text-slate-500">
            MarketIQ provides AI-generated market analysis
            based on available technical data. Paper trading
            is simulated. AI-generated signals and historical
            backtests do not guarantee future trading results.
          </p>
        </section>
      </div>
    </DashboardLayout>
  );
}

function Info({
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

      <p className="mt-2 font-semibold text-white">
        {value}
      </p>
    </div>
  );
}