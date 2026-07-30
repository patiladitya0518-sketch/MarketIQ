import {
  LayoutDashboard,
  Search,
  LineChart,
  Brain,
  History,
  Settings,
} from "lucide-react";

const menuItems = [
  { icon: LayoutDashboard, label: "Dashboard" },
  { icon: Search, label: "Stock Search" },
  { icon: LineChart, label: "Market Analysis" },
  { icon: Brain, label: "AI Signals" },
  { icon: History, label: "Trade History" },
  { icon: Settings, label: "Settings" },
];

export default function Sidebar() {
  return (
    <aside className="flex h-screen w-64 flex-col border-r border-slate-800 bg-slate-950">
      <div className="border-b border-slate-800 p-6">
        <h1 className="text-3xl font-bold">
          <span className="text-blue-500">Market</span>
          <span className="text-white">IQ</span>
        </h1>
      </div>

      <nav className="flex-1 p-4">
        {menuItems.map((item) => {
          const Icon = item.icon;

          return (
            <button
              key={item.label}
              className="mb-3 flex w-full items-center gap-3 rounded-xl px-4 py-3 text-slate-300 transition hover:bg-slate-900 hover:text-white"
            >
              <Icon size={20} />
              <span>{item.label}</span>
            </button>
          );
        })}
      </nav>
    </aside>
  );
}