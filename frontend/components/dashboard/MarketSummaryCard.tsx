interface MarketSummaryProps {
  symbol: string;
  price: number;
}

export default function MarketSummaryCard({
  symbol,
  price,
}: MarketSummaryProps) {
  return (
    <div className="rounded-2xl border border-slate-700 bg-slate-900 p-6 shadow-lg">
      <h2 className="mb-6 text-xl font-bold text-white">
        Market Summary
      </h2>

      <div className="space-y-4">

        <div className="flex items-center justify-between rounded-lg bg-slate-800 p-4">
          <div>
            <h3 className="font-semibold text-white">{symbol}</h3>
            <p className="text-sm text-slate-400">
              ₹ {price.toFixed(2)}
            </p>
          </div>

          <span className="text-green-400 font-semibold">
            Live
          </span>
        </div>

      </div>
    </div>
  );
}