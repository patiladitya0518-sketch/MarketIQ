interface MarketSummaryProps {
  symbol: string;
  price: number;
}

export default function MarketSummaryCard({
  symbol,
  price,
}: MarketSummaryProps) {
  return (
    <div className="h-full rounded-2xl border border-slate-800 bg-slate-900 p-6 shadow-lg">

      {/* HEADER */}

      <div className="mb-6 flex items-center justify-between">

        <div>
          <p className="text-sm text-slate-400">
            Live market data
          </p>

          <h2 className="mt-1 text-xl font-bold text-white">
            Market Summary
          </h2>
        </div>

        <div className="flex items-center gap-2 rounded-full border border-green-900/50 bg-green-950/30 px-3 py-1.5">
          <span className="h-2 w-2 rounded-full bg-green-400" />

          <span className="text-xs font-semibold text-green-400">
            LIVE
          </span>
        </div>

      </div>

      {/* STOCK */}

      <div className="rounded-2xl border border-slate-800 bg-slate-950 p-5">

        <div className="flex flex-col gap-5 sm:flex-row sm:items-center sm:justify-between">

          <div>
            <p className="text-xs font-medium uppercase tracking-wider text-slate-500">
              NSE Stock
            </p>

            <h3 className="mt-1 text-3xl font-bold text-white">
              {symbol}
            </h3>
          </div>

          <div className="sm:text-right">
            <p className="text-xs text-slate-500">
              Current Price
            </p>

            <p className="mt-1 text-3xl font-bold text-blue-400">
              ₹
              {price.toLocaleString("en-IN", {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2,
              })}
            </p>
          </div>

        </div>

        {/* MARKET STATUS */}

        <div className="mt-5 grid grid-cols-2 gap-3">

          <div className="rounded-xl border border-slate-800 bg-slate-900 p-4">

            <p className="text-xs text-slate-500">
              Market
            </p>

            <p className="mt-1 font-semibold text-white">
              NSE
            </p>

          </div>

          <div className="rounded-xl border border-green-900/40 bg-green-950/20 p-4">

            <p className="text-xs text-slate-500">
              Status
            </p>

            <p className="mt-1 font-semibold text-green-400">
              Live
            </p>

          </div>

        </div>

      </div>

    </div>
  );
}