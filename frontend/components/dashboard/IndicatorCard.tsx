interface IndicatorCardProps {
  title: string;
  value: string;
  status: "Bullish" | "Bearish" | "Neutral";
}

export default function IndicatorCard({
  title,
  value,
  status,
}: IndicatorCardProps) {
  const statusColor =
    status === "Bullish"
      ? "text-green-400"
      : status === "Bearish"
      ? "text-red-400"
      : "text-yellow-400";

  return (
    <div className="rounded-2xl border border-slate-700 bg-slate-900 p-5 shadow-lg transition hover:border-blue-500">
      <h3 className="text-sm font-medium text-slate-400">{title}</h3>

      <div className="mt-3 text-3xl font-bold text-white">
        {value}
      </div>

      <p className={`mt-2 font-semibold ${statusColor}`}>
        {status}
      </p>
    </div>
  );
}