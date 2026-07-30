const markets = [
  { name: "NIFTY 50", change: "+0.82%", positive: true },
  { name: "BANKNIFTY", change: "+1.14%", positive: true },
  { name: "SENSEX", change: "+0.61%", positive: true },
];

export default function MarketOverview() {
  return (
    <section className="mx-auto mt-16 max-w-6xl px-6">
      <h2 className="mb-8 text-center text-3xl font-bold text-white">
        Live Market Overview
      </h2>

      <div className="grid gap-6 md:grid-cols-3">
        {markets.map((market) => (
          <div
            key={market.name}
            className="rounded-2xl border border-slate-800 bg-slate-900 p-6"
          >
            <h3 className="text-xl font-semibold text-white">
              {market.name}
            </h3>

            <p
              className={`mt-4 text-3xl font-bold ${
                market.positive ? "text-green-400" : "text-red-400"
              }`}
            >
              {market.change}
            </p>
          </div>
        ))}
      </div>
    </section>
  );
}