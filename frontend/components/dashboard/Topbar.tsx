import { Bell, Menu, UserCircle } from "lucide-react";

interface TopbarProps {
  onMenu?: () => void;
}

export default function Topbar({ onMenu }: TopbarProps) {
  return (
    <header className="sticky top-0 z-30 flex h-20 items-center justify-between border-b border-slate-800 bg-slate-950/95 px-4 backdrop-blur sm:px-6 lg:px-8">
      <div className="flex items-center gap-3">
        <button
          type="button"
          aria-label="Open navigation"
          onClick={onMenu}
          className="rounded-lg border border-slate-800 bg-slate-900 p-2 text-slate-300 transition hover:bg-slate-800 hover:text-white lg:hidden"
        >
          <Menu size={20} />
        </button>
        <h2 className="text-2xl font-bold text-white">
        Dashboard
        </h2>
      </div>

      <div className="flex items-center gap-4 sm:gap-6">
        <Bell className="text-slate-300" />

        <UserCircle
          className="text-slate-300"
          size={34}
        />
      </div>
    </header>
  );
}