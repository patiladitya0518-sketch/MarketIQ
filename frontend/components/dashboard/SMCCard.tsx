"use client";

interface SMCCardProps {
  smc?: {
    signal?: string;
    confidence?: number;
    trend?: string;
    market_bias?: string;
    structure?: string;

    bos?: unknown;
    choch?: unknown;

    reasons?: string[];

    [key: string]: unknown;
  } | null;
}

function getSignalColor(signal?: string) {
  const value = signal?.toUpperCase();

  if (value === "BUY" || value === "BULLISH") {
    return "text-green-400";
  }

  if (value === "SELL" || value === "BEARISH") {
    return "text-red-400";
  }

  return "text-yellow-400";
}

function getSignalBackground(signal?: string) {
  const value = signal?.toUpperCase();

  if (value === "BUY" || value === "BULLISH") {
    return "bg-green-950/40 border-green-900/50";
  }

  if (value === "SELL" || value === "BEARISH") {
    return "bg-red-950/40 border-red-900/50";
  }

  return "bg-yellow-950/40 border-yellow-900/50";
}

function formatValue(value: unknown) {
  if (value === null || value === undefined) {
    return "Not detected";
  }

  if (typeof value === "boolean") {
    return value ? "Yes" : "No";
  }

  if (typeof value === "string") {
    return value;
  }

  if (typeof value === "object") {
    return "Detected";
  }

  return String(value);
}

export default function SMCCard({ smc }: SMCCardProps) {
  // ======================================================
  // SMC DATA UNAVAILABLE
  // ======================================================

  if (!smc) {
    return (
      <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6 shadow-lg">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-slate-400">
              Smart Money Concepts
            </p>

            <h2 className="mt-1 text-2xl font-bold text-white">
              SMC Analysis
            </h2>
          </div>

          <span className="rounded-lg bg-slate-800 px-3 py-1 text-xs font-semibold text-slate-400">
            Unavailable
          </span>
        </div>

        <p className="mt-5 text-sm text-slate-500">
          Smart Money Concepts data is currently unavailable for this stock.
        </p>
      </div>
    );
  }

  // ======================================================
  // SIGNAL
  // ======================================================

  const signal =
    smc.signal ||
    smc.market_bias ||
    "NEUTRAL";

  const confidence =
    typeof smc.confidence === "number"
      ? Math.max(0, Math.min(100, smc.confidence))
      : 0;

  const signalColor = getSignalColor(signal);

  const signalBackground =
    getSignalBackground(signal);

  const reasons =
    Array.isArray(smc.reasons)
      ? smc.reasons
      : [];

  const normalizedSignal =
    signal.toUpperCase();

  const progressColor =
    normalizedSignal === "BUY" ||
    normalizedSignal === "BULLISH"
      ? "bg-green-500"
      : normalizedSignal === "SELL" ||
        normalizedSignal === "BEARISH"
      ? "bg-red-500"
      : "bg-yellow-500";

  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6 shadow-lg">

      {/* ======================================================
          HEADER
      ====================================================== */}

      <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">

        <div>

          <div className="flex items-center gap-3">

            <p className="text-sm text-slate-400">
              Smart Money Concepts
            </p>

            <span className="rounded-full bg-purple-500/10 px-2.5 py-1 text-xs font-semibold text-purple-400">
              SMC
            </span>

          </div>

          <h2 className="mt-1 text-2xl font-bold text-white">
            Institutional Market Analysis
          </h2>

          <p className="mt-1 text-sm text-slate-500">
            Market structure, liquidity and smart-money price-action signals.
          </p>

        </div>

        {/* SMC SIGNAL */}

        <div
          className={`rounded-xl border px-5 py-3 text-center ${signalBackground}`}
        >

          <p className="text-xs text-slate-500">
            SMC Signal
          </p>

          <p
            className={`mt-1 text-xl font-bold ${signalColor}`}
          >
            {signal}
          </p>

          <p
            className={`mt-1 text-xs font-semibold ${signalColor}`}
          >
            {confidence}% confidence
          </p>

        </div>

      </div>


      {/* ======================================================
          MAIN METRICS
      ====================================================== */}

      <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">

        {/* MARKET BIAS */}

        <div className="rounded-xl border border-slate-800 bg-slate-950 p-4">

          <p className="text-xs text-slate-500">
            Market Bias
          </p>

          <p
            className={`mt-2 text-lg font-bold ${signalColor}`}
          >
            {formatValue(
              smc.market_bias || signal
            )}
          </p>

        </div>


        {/* TREND */}

        <div className="rounded-xl border border-slate-800 bg-slate-950 p-4">

          <p className="text-xs text-slate-500">
            SMC Trend
          </p>

          <p className="mt-2 text-lg font-bold text-white">
            {formatValue(smc.trend)}
          </p>

        </div>


        {/* STRUCTURE */}

        <div className="rounded-xl border border-slate-800 bg-slate-950 p-4">

          <p className="text-xs text-slate-500">
            Structure
          </p>

          <p className="mt-2 text-lg font-bold text-white">
            {formatValue(smc.structure)}
          </p>

        </div>


        {/* CONFIDENCE */}

        <div className="rounded-xl border border-slate-800 bg-slate-950 p-4">

          <div className="flex items-center justify-between">

            <p className="text-xs text-slate-500">
              Confidence
            </p>

            <span
              className={`text-sm font-bold ${signalColor}`}
            >
              {confidence}%
            </span>

          </div>

          <div className="mt-3 h-2 overflow-hidden rounded-full bg-slate-800">

            <div
              className={`h-full rounded-full ${progressColor}`}
              style={{
                width: `${confidence}%`,
              }}
            />

          </div>

        </div>

      </div>


      {/* ======================================================
          BOS / CHOCH
      ====================================================== */}

      <div className="mt-6 grid gap-4 md:grid-cols-2">

        {/* BOS */}

        <div className="rounded-xl border border-blue-900/40 bg-blue-950/20 p-4">

          <p className="text-xs font-semibold text-blue-400">
            Break of Structure — BOS
          </p>

          <p className="mt-2 text-sm font-semibold text-white">
            {formatValue(smc.bos)}
          </p>

        </div>


        {/* CHOCH */}

        <div className="rounded-xl border border-purple-900/40 bg-purple-950/20 p-4">

          <p className="text-xs font-semibold text-purple-400">
            Change of Character — CHoCH
          </p>

          <p className="mt-2 text-sm font-semibold text-white">
            {formatValue(smc.choch)}
          </p>

        </div>

      </div>


      {/* ======================================================
          SMC REASONS
      ====================================================== */}

      {reasons.length > 0 && (

        <div className="mt-6">

          <div className="mb-3 flex items-center justify-between">

            <div>

              <p className="text-sm font-semibold text-slate-300">
                SMC Analysis
              </p>

              <p className="mt-1 text-xs text-slate-500">
                Evidence used by the Smart Money Concepts engine.
              </p>

            </div>

            <span className="rounded-lg bg-purple-500/10 px-3 py-1 text-xs font-semibold text-purple-400">
              {reasons.length} factors
            </span>

          </div>


          <div className="grid gap-3 md:grid-cols-2">

            {reasons.map((reason, index) => (

              <div
                key={index}
                className="rounded-xl border border-slate-800 bg-slate-950 px-4 py-3 text-sm text-slate-300"
              >

                <span className="mr-2 text-purple-400">
                  ✓
                </span>

                {reason}

              </div>

            ))}

          </div>

        </div>

      )}

    </div>
  );
}