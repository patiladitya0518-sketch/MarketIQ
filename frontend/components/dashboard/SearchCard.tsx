"use client";

import { Search } from "lucide-react";
import { useState } from "react";

export default function SearchCard() {
  const [stock, setStock] = useState("");

  const popularStocks = [
    "RELIANCE",
    "TCS",
    "INFY",
    "HDFCBANK",
    "ICICIBANK",
  ];

  return (
    <div className="rounded-2xl border border-slate-700 bg-slate-900 p-6 shadow-lg">
      <h2 className="mb-5 text-xl font-bold text-white">
        🔍 Search Stock
      </h2>

      <div className="relative">
       <span className="absolute left-3 top-1/2 -translate-y-1/2">
  🔍
</span>

        <input
          value={stock}
          onChange={(e) => setStock(e.target.value)}
          placeholder="Search NSE Stock..."
          className="w-full rounded-lg border border-slate-700 bg-slate-800 py-3 pl-10 pr-4 text-white outline-none focus:border-blue-500"
        />
      </div>

      <div className="mt-6">
        <p className="mb-3 text-sm text-slate-400">
          Popular Stocks
        </p>

        <div className="flex flex-wrap gap-2">
          {popularStocks.map((item) => (
            <button
              key={item}
              className="rounded-full bg-slate-800 px-4 py-2 text-sm text-white hover:bg-blue-600 transition"
            >
              {item}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}