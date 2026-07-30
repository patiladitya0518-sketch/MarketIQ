import { Bell, UserCircle } from "lucide-react";

export default function Topbar() {
  return (
    <header className="flex h-20 items-center justify-between border-b border-slate-800 bg-slate-950 px-8">
      <h2 className="text-2xl font-bold text-white">
        Dashboard
      </h2>

      <div className="flex items-center gap-6">
        <Bell className="text-slate-300" />

        <UserCircle
          className="text-slate-300"
          size={34}
        />
      </div>
    </header>
  );
}