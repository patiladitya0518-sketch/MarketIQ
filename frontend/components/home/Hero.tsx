export default function Hero() {
  return (
    <section className="relative overflow-hidden px-6 py-28">

      <div className="absolute inset-0 bg-[radial-gradient(circle_at_top,#1d4ed8_0%,transparent_60%)] opacity-20" />

      <div className="relative mx-auto max-w-5xl text-center">

        <div className="inline-flex items-center rounded-full border border-blue-500/30 bg-blue-500/10 px-4 py-2 text-sm text-blue-400">
          🚀 AI Powered Trading Intelligence
        </div>

        <h1 className="mt-8 text-6xl font-extrabold leading-tight md:text-7xl">
          <span className="text-white">Trade Smarter.</span>

          <br />

          <span className="bg-gradient-to-r from-blue-400 to-cyan-300 bg-clip-text text-transparent">
            Decide Better.
          </span>
        </h1>

        <p className="mx-auto mt-8 max-w-3xl text-xl text-slate-400">
          MarketIQ analyses Indian stock markets using technical indicators,
          candlestick patterns, market structure and explainable AI.
        </p>

        <div className="mt-12 flex flex-wrap justify-center gap-5">

          <button className="rounded-xl bg-blue-600 px-8 py-4 font-semibold transition hover:bg-blue-700">
            Analyze Stock
          </button>

          <button className="rounded-xl border border-slate-700 px-8 py-4 text-white transition hover:bg-slate-800">
            Live Demo
          </button>

        </div>

      </div>
    </section>
  );
}