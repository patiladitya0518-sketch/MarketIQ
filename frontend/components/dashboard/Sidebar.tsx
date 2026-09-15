"use client";

import { usePathname, useRouter } from "next/navigation";

interface SidebarProps {
  onNavigate?: () => void;
}

const menuItems = [
  {
    label: "Dashboard",
    route: "/dashboard",
    icon: "▣",
  },
  {
    label: "Stock Search",
    route: "/stock-search",
    icon: "⌕",
  },
  {
    label: "Market Analysis",
    route: "/market-analysis",
    icon: "◈",
  },
  {
    label: "AI Signals",
    route: "/ai-signals",
    icon: "✦",
  },
  {
    label: "Trade History",
    route: "/trade-history",
    icon: "◷",
  },
  {
    label: "Settings",
    route: "/settings",
    icon: "⚙",
  },
];

export default function Sidebar({
  onNavigate,
}: SidebarProps) {
  const router = useRouter();
  const pathname = usePathname();

  const handleNavigation = (route: string) => {
    router.push(route);

    if (onNavigate) {
      onNavigate();
    }
  };

  return (
    <aside className="flex h-full w-full flex-col border-r border-slate-800 bg-slate-950">
      {/* LOGO */}
      <div className="flex h-20 items-center border-b border-slate-800 px-6">
        <button
          type="button"
          onClick={() => handleNavigation("/dashboard")}
          className="flex items-center gap-3"
        >
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-600 text-lg font-black text-white">
            M
          </div>

          <div className="text-left">
            <p className="text-lg font-bold text-white">
              MarketIQ
            </p>

            <p className="text-xs text-slate-500">
              AI Stock Intelligence
            </p>
          </div>
        </button>
      </div>

      {/* MAIN MENU */}
      <div className="flex-1 overflow-y-auto px-4 py-6">
        <p className="mb-3 px-3 text-xs font-semibold uppercase tracking-wider text-slate-500">
          Main Menu
        </p>

        <nav className="space-y-1">
          {menuItems.map((item) => {
            const isActive =
              pathname === item.route ||
              (item.route !== "/dashboard" &&
                pathname.startsWith(
                  `${item.route}/`
                ));

            return (
              <button
                key={item.route}
                type="button"
                onClick={() =>
                  handleNavigation(item.route)
                }
                className={`group flex w-full items-center gap-3 rounded-xl px-3 py-3 text-left text-sm font-medium transition ${
                  isActive
                    ? "bg-blue-600/15 text-blue-400"
                    : "text-slate-400 hover:bg-slate-900 hover:text-white"
                }`}
              >
                <span
                  className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-lg text-lg ${
                    isActive
                      ? "bg-blue-600/20 text-blue-400"
                      : "bg-slate-900 text-slate-500 group-hover:text-slate-300"
                  }`}
                >
                  {item.icon}
                </span>

                <span className="truncate">
                  {item.label}
                </span>

                {isActive && (
                  <span className="ml-auto h-2 w-2 rounded-full bg-blue-400" />
                )}
              </button>
            );
          })}
        </nav>

        {/* BACKTEST */}
        <div className="mt-8">
          <p className="mb-3 px-3 text-xs font-semibold uppercase tracking-wider text-slate-500">
            Tools
          </p>

          <button
            type="button"
            onClick={() =>
              handleNavigation("/backtest")
            }
            className={`group flex w-full items-center gap-3 rounded-xl px-3 py-3 text-left text-sm font-medium transition ${
              pathname === "/backtest"
                ? "bg-blue-600/15 text-blue-400"
                : "text-slate-400 hover:bg-slate-900 hover:text-white"
            }`}
          >
            <span
              className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-lg text-lg ${
                pathname === "/backtest"
                  ? "bg-blue-600/20 text-blue-400"
                  : "bg-slate-900 text-slate-500 group-hover:text-slate-300"
              }`}
            >
              ↗
            </span>

            <span>Backtesting</span>

            {pathname === "/backtest" && (
              <span className="ml-auto h-2 w-2 rounded-full bg-blue-400" />
            )}
          </button>
        </div>
      </div>

      {/* FOOTER */}
      <div className="border-t border-slate-800 p-4">
        <div className="rounded-xl bg-slate-900 p-4">
          <p className="text-xs font-semibold text-slate-300">
            MarketIQ
          </p>

          <p className="mt-1 text-xs leading-5 text-slate-500">
            AI-powered technical analysis,
            signals and paper trading.
          </p>
        </div>
      </div>
    </aside>
  );
}