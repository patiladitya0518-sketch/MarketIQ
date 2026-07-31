export default function TopMovers() {
  const gainers = [
    { symbol: "RELIANCE", change: "+3.25%" },
    { symbol: "TCS", change: "+2.48%" },
    { symbol: "INFY", change: "+1.95%" },
    { symbol: "ICICIBANK", change: "+1.63%" },
    { symbol: "SBIN", change: "+1.22%" },
  ];

  const losers = [
    { symbol: "WIPRO", change: "-2.11%" },
    { symbol: "HCLTECH", change: "-1.82%" },
    { symbol: "LT", change: "-1.46%" },
    { symbol: "ONGC", change: "-1.22%" },
    { symbol: "TITAN", change: "-0.91%" },
  ];

  return (
    <div className="grid gap-6 lg:grid-cols-2">
      <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
        <h2 className="mb-4 text-xl font-bold text-green-400">
          🔥 Top Gainers
        </h2>

        {gainers.map((stock) => (
          <div
            key={stock.symbol}
            className="mb-3 flex items-center justify-between rounded-lg bg-slate-800 p-3"
          >
            <span className="font-semibold text-white">{stock.symbol}</span>
            <span className="font-bold text-green-400">
              {stock.change}
            </span>
          </div>
        ))}
      </div>

      <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
        <h2 className="mb-4 text-xl font-bold text-red-400">
          📉 Top Losers
        </h2>

        {losers.map((stock) => (
          <div
            key={stock.symbol}
            className="mb-3 flex items-center justify-between rounded-lg bg-slate-800 p-3"
          >
            <span className="font-semibold text-white">{stock.symbol}</span>
            <span className="font-bold text-red-400">
              {stock.change}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}