"use client";

import { TrendingUp, TrendingDown, Activity } from "lucide-react";

const markets = [
  {
    name: "NIFTY 50",
    value: "25,185.80",
    change: "+0.82%",
    positive: true,
  },
  {
    name: "BANKNIFTY",
    value: "57,320.40",
    change: "+1.14%",
    positive: true,
  },
  {
    name: "SENSEX",
    value: "82,408.17",
    change: "+0.61%",
    positive: true,
  },
  {
    name: "INDIA VIX",
    value: "13.22",
    change: "-2.80%",
    positive: false,
  },
];

export default function MarketCards() {
  return (
    <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
      {markets.map((market) => (
        <div
          key={market.name}
          className="rounded-xl border border-slate-800 bg-slate-900 p-5 shadow-lg transition hover:border-blue-500"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-slate-400">{market.name}</p>

              <h2 className="mt-2 text-2xl font-bold text-white">
                {market.value}
              </h2>

              <div
                className={`mt-2 flex items-center gap-2 text-sm font-medium ${
                  market.positive ? "text-green-400" : "text-red-400"
                }`}
              >
                {market.positive ? (
                  <TrendingUp size={16} />
                ) : (
                  <TrendingDown size={16} />
                )}

                {market.change}
              </div>
            </div>

            <div className="rounded-full bg-slate-800 p-3">
              <Activity className="text-blue-400" size={22} />
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}