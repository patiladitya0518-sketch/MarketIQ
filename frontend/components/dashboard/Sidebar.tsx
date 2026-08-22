"use client";

import {
  LayoutDashboard,
  Search,
  LineChart,
  Brain,
  History,
  Settings,
} from "lucide-react";

const menuItems = [
  {
    icon: LayoutDashboard,
    label: "Dashboard",
  },
  {
    icon: Search,
    label: "Stock Search",
  },
  {
    icon: LineChart,
    label: "Market Analysis",
  },
  {
    icon: Brain,
    label: "AI Signals",
  },
  {
    icon: History,
    label: "Trade History",
  },
  {
    icon: Settings,
    label: "Settings",
  },
];

export default function Sidebar() {
  return (
    <aside className="flex h-screen w-64 flex-col overflow-hidden border-r border-slate-800 bg-slate-900">

      {/* =====================================================
          LOGO
      ===================================================== */}

      <div className="flex h-20 shrink-0 items-center border-b border-slate-800 px-6">
        <h1 className="text-2xl font-bold tracking-tight">
          <span className="text-blue-500">
            Market
          </span>

          <span className="text-white">
            IQ
          </span>
        </h1>
      </div>

      {/* =====================================================
          NAVIGATION
      ===================================================== */}

      <nav className="flex-1 overflow-y-auto px-3 py-5">

        <p className="mb-3 px-3 text-xs font-semibold uppercase tracking-wider text-slate-500">
          Main Menu
        </p>

        <div className="space-y-1">

          {menuItems.map((item) => {
            const Icon = item.icon;

            const isDashboard =
              item.label === "Dashboard";

            return (
              <button
                key={item.label}
                type="button"
                className={`group flex w-full items-center gap-3 rounded-xl px-4 py-3 text-left text-sm font-medium transition-all duration-200 ${
                  isDashboard
                    ? "bg-blue-600/15 text-blue-400"
                    : "text-slate-400 hover:bg-slate-800 hover:text-white"
                }`}
              >

                <Icon
                  size={20}
                  strokeWidth={1.8}
                  className={
                    isDashboard
                      ? "text-blue-400"
                      : "text-slate-400 transition group-hover:text-white"
                  }
                />

                <span>
                  {item.label}
                </span>

                {isDashboard && (
                  <span className="ml-auto h-2 w-2 rounded-full bg-blue-500" />
                )}

              </button>
            );
          })}

        </div>
      </nav>

      {/* =====================================================
          SIDEBAR FOOTER
      ===================================================== */}

      <div className="shrink-0 border-t border-slate-800 p-4">

        <div className="rounded-xl border border-slate-800 bg-slate-950 p-3">

          <div className="flex items-center gap-3">

            <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-blue-600/20 text-sm font-bold text-blue-400">
              MI
            </div>

            <div className="min-w-0">

              <p className="truncate text-sm font-semibold text-white">
                MarketIQ
              </p>

              <p className="truncate text-xs text-slate-500">
                AI Trading Assistant
              </p>

            </div>

          </div>

        </div>

      </div>

    </aside>
  );
}