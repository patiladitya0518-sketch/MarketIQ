"use client";

interface PatternAnalysis {
  pattern?: string;
  signal?: string;
  confidence?: number;
}

interface MarketStructureAnalysis {
  structure?: string;
  trend?: string;
  signal?: string;
  confidence?: number;
}

interface SupportResistanceAnalysis {
  nearest_support?: number | null;
  nearest_resistance?: number | null;
}

interface Recommendation {
  recommendation: "BUY" | "SELL" | "HOLD";
  confidence: number;
  score: number;

  bullish_factors?: number;
  bearish_factors?: number;

  entry_price?: number | null;
  stop_loss?: number | null;
  target?: number | null;
  risk_reward?: number | null;

  reasons?: string[];

  pattern_analysis?: PatternAnalysis | null;
  market_structure_analysis?: MarketStructureAnalysis | null;
  support_resistance_analysis?: SupportResistanceAnalysis | null;
}

interface RecommendationCardProps {
  recommendation: Recommendation;
}

/* ============================================================
   PRICE FORMATTER
============================================================ */

function formatPrice(value: number | null | undefined) {
  if (
    value === null ||
    value === undefined ||
    !Number.isFinite(value)
  ) {
    return "—";
  }

  return `₹${value.toLocaleString("en-IN", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}`;
}

/* ============================================================
   MAIN COMPONENT
============================================================ */

export default function RecommendationCard({
  recommendation,
}: RecommendationCardProps) {
  /* ============================================================
     SAFE DATA
  ============================================================ */

  const action =
    recommendation?.recommendation ?? "HOLD";

  const confidence = Number(
    recommendation?.confidence ?? 50
  );

  const score = Number(
    recommendation?.score ?? 0
  );

  const bullishFactors = Number(
    recommendation?.bullish_factors ?? 0
  );

  const bearishFactors = Number(
    recommendation?.bearish_factors ?? 0
  );

  const entryPrice =
    recommendation?.entry_price ?? null;

  const stopLoss =
    recommendation?.stop_loss ?? null;

  const target =
    recommendation?.target ?? null;

  const riskReward =
    recommendation?.risk_reward ?? null;

  /* ============================================================
     SAFE REASONS
  ============================================================ */

  const reasons = Array.isArray(
    recommendation?.reasons
  )
    ? recommendation.reasons.filter(
        (reason): reason is string =>
          typeof reason === "string" &&
          reason.trim().length > 0
      )
    : [];

  const patternAnalysis =
    recommendation?.pattern_analysis ?? null;

  const marketStructureAnalysis =
    recommendation?.market_structure_analysis ?? null;

  const supportResistanceAnalysis =
    recommendation?.support_resistance_analysis ?? null;

  /* ============================================================
     SIGNAL STATE
  ============================================================ */

  const isBuy = action === "BUY";
  const isSell = action === "SELL";
  const isHold = action === "HOLD";

  const signalColor = isBuy
    ? "text-green-400"
    : isSell
    ? "text-red-400"
    : "text-yellow-400";

  const signalBg = isBuy
    ? "border-green-900/40 bg-green-950/20"
    : isSell
    ? "border-red-900/40 bg-red-950/20"
    : "border-yellow-900/40 bg-yellow-950/20";

  const progressColor = isBuy
    ? "bg-green-500"
    : isSell
    ? "bg-red-500"
    : "bg-yellow-500";

  /* ============================================================
     REUSABLE TRADE VALUE CARD
  ============================================================ */

  const tradeCard =
    "min-w-0 rounded-xl border bg-slate-950 p-4";

  /* ============================================================
     RENDER
  ============================================================ */

  return (
    <div className="min-w-0 space-y-6">

      {/* ========================================================
          AI RECOMMENDATION
      ======================================================== */}

      <div className="min-w-0 rounded-2xl border border-slate-800 bg-slate-900 p-5 shadow-lg sm:p-6">

        <div className="mb-5">
          <p className="text-sm text-slate-400">
            Multi-factor market analysis
          </p>

          <h2 className="mt-1 text-xl font-semibold text-white">
            AI Recommendation
          </h2>
        </div>

        {/* ======================================================
            SIGNAL / SCORE / CONFIDENCE
        ====================================================== */}

        <div className="grid grid-cols-3 gap-2 sm:gap-3">

          {/* SIGNAL */}

          <div className="min-w-0 rounded-xl border border-slate-800 bg-slate-950 p-3 sm:p-4">

            <p className="text-xs text-slate-400 sm:text-sm">
              Current Signal
            </p>

            <p
              className={`mt-2 truncate text-xl font-bold sm:text-2xl ${signalColor}`}
            >
              {action}
            </p>

          </div>

          {/* SCORE */}

          <div className="min-w-0 rounded-xl border border-slate-800 bg-slate-950 p-3 sm:p-4">

            <p className="text-xs text-slate-400 sm:text-sm">
              AI Score
            </p>

            <p className="mt-2 text-xl font-bold text-white sm:text-2xl">
              {score > 0 ? "+" : ""}
              {score}
            </p>

          </div>

          {/* CONFIDENCE */}

          <div className="min-w-0 rounded-xl border border-slate-800 bg-slate-950 p-3 sm:p-4">

            <p className="text-xs text-slate-400 sm:text-sm">
              Confidence
            </p>

            <p
              className={`mt-2 text-xl font-bold sm:text-2xl ${signalColor}`}
            >
              {confidence}%
            </p>

          </div>

        </div>

        {/* ======================================================
            CONFIDENCE BAR
        ====================================================== */}

        <div className="mt-5">

          <div className="mb-2 flex items-center justify-between text-xs">

            <span className="text-slate-500">
              AI Confidence
            </span>

            <span
              className={`font-semibold ${signalColor}`}
            >
              {confidence}%
            </span>

          </div>

          <div className="h-2 overflow-hidden rounded-full bg-slate-800">

            <div
              className={`h-full rounded-full transition-all duration-500 ${progressColor}`}
              style={{
                width: `${Math.max(
                  0,
                  Math.min(100, confidence)
                )}%`,
              }}
            />

          </div>

        </div>

      </div>


      {/* ========================================================
          TRADE SETUP
      ======================================================== */}

      {!isHold && (
        <div className="min-w-0 rounded-2xl border border-slate-800 bg-slate-900 p-5 shadow-lg sm:p-6">

          <div className="mb-5">

            <p className="text-sm text-slate-400">
              AI-generated trade setup
            </p>

            <h2 className="mt-1 text-xl font-semibold text-white">
              Trade Setup
            </h2>

          </div>

          {/* ====================================================
              IMPORTANT:
              2 COLUMNS ON NARROW SIDEBAR
              4 COLUMNS WHEN THERE IS ENOUGH SPACE
          ==================================================== */}

          <div className="grid grid-cols-2 gap-3">

            {/* ENTRY */}

            <div
              className={`${tradeCard} border-slate-800`}
            >

              <p className="text-xs text-slate-400 sm:text-sm">
                Entry Price
              </p>

              <p className="mt-2 break-words text-base font-bold text-white sm:text-lg">
                {formatPrice(entryPrice)}
              </p>

            </div>


            {/* STOP LOSS */}

            <div
              className={`${tradeCard} border-red-900/40`}
            >

              <p className="text-xs text-slate-400 sm:text-sm">
                Stop Loss
              </p>

              <p className="mt-2 break-words text-base font-bold text-red-400 sm:text-lg">
                {formatPrice(stopLoss)}
              </p>

            </div>


            {/* TARGET */}

            <div
              className={`${tradeCard} border-green-900/40`}
            >

              <p className="text-xs text-slate-400 sm:text-sm">
                Target
              </p>

              <p className="mt-2 break-words text-base font-bold text-green-400 sm:text-lg">
                {formatPrice(target)}
              </p>

            </div>


            {/* RISK REWARD */}

            <div
              className={`${tradeCard} border-slate-800`}
            >

              <p className="text-xs text-slate-400 sm:text-sm">
                Risk / Reward
              </p>

              <p className="mt-2 break-words text-base font-bold text-white sm:text-lg">

                {riskReward !== null &&
                riskReward !== undefined &&
                Number.isFinite(Number(riskReward))
                  ? `1 : ${Number(riskReward).toFixed(2)}`
                  : "—"}

              </p>

            </div>

          </div>


          {/* ====================================================
              TRADE DIRECTION
          ==================================================== */}

          <div
            className={`mt-5 min-w-0 rounded-xl border p-4 ${signalBg}`}
          >

            <p className="text-xs text-slate-400 sm:text-sm">
              Trade Direction
            </p>

            <p
              className={`mt-1 break-words text-base font-semibold sm:text-lg ${signalColor}`}
            >
              {isBuy
                ? "Bullish setup — potential BUY"
                : "Bearish setup — potential SELL"}
            </p>

          </div>

        </div>
      )}


      {/* ========================================================
          HOLD
      ======================================================== */}

      {isHold && (
        <div className="rounded-2xl border border-yellow-900/40 bg-yellow-950/10 p-5 sm:p-6">

          <h2 className="text-lg font-semibold text-yellow-400">
            No Directional Trade Setup
          </h2>

          <p className="mt-2 text-sm leading-6 text-slate-400">
            MarketIQ is currently detecting mixed or
            insufficient signals. Entry, stop loss and
            target are intentionally not provided.
          </p>

        </div>
      )}


      {/* ========================================================
          SIGNAL STRENGTH
      ======================================================== */}

      <div className="min-w-0 rounded-2xl border border-slate-800 bg-slate-900 p-5 shadow-lg sm:p-6">

        <h2 className="text-lg font-semibold text-white">
          Signal Strength
        </h2>

        <div className="mt-4 grid grid-cols-2 gap-3">

          {/* BULLISH */}

          <div className="min-w-0 rounded-xl border border-green-900/40 bg-slate-950 p-4">

            <p className="text-xs text-slate-400 sm:text-sm">
              Bullish Factors
            </p>

            <p className="mt-2 text-2xl font-bold text-green-400">
              {bullishFactors}
            </p>

          </div>


          {/* BEARISH */}

          <div className="min-w-0 rounded-xl border border-red-900/40 bg-slate-950 p-4">

            <p className="text-xs text-slate-400 sm:text-sm">
              Bearish Factors
            </p>

            <p className="mt-2 text-2xl font-bold text-red-400">
              {bearishFactors}
            </p>

          </div>

        </div>

      </div>


      {/* ========================================================
          WHY AI GAVE THIS SIGNAL
      ======================================================== */}

      <div className="min-w-0 rounded-2xl border border-slate-800 bg-slate-900 p-5 shadow-lg sm:p-6">

        <h2 className="text-lg font-semibold text-white">
          Why AI gave this signal
        </h2>

        {(() => {
          const uniqueReasons = Array.from(
            new Set(reasons)
          );

          const technicalReasons = uniqueReasons.filter((reason) => {
            const text = reason.toLowerCase();
            return (
              text.includes("rsi") ||
              text.includes("ema20") ||
              text.includes("ema50") ||
              text.includes("macd") ||
              text.includes("price vs")
            );
          });

          const patternStructureReasons = uniqueReasons.filter((reason) => {
            const text = reason.toLowerCase();
            return (
              text.includes("engulfing") ||
              text.includes("candlestick") ||
              text.includes("market structure") ||
              text.includes("higher high") ||
              text.includes("higher low") ||
              text.includes("lower high") ||
              text.includes("lower low")
            );
          });

          const smcReasons = uniqueReasons.filter((reason) => {
            const text = reason.toLowerCase();
            return (
              text.includes("smc") ||
              text.includes("break of structure") ||
              text.includes("bos") ||
              text.includes("change of character") ||
              text.includes("choch") ||
              text.includes("order block") ||
              text.includes("fair value gap") ||
              text.includes("fvg") ||
              text.includes("liquidity") ||
              text.includes("imbalance")
            );
          });

          const riskReasons = uniqueReasons.filter((reason) => {
            const text = reason.toLowerCase();
            return (
              text.includes("risk/reward") ||
              text.includes("risk reward") ||
              text.includes("trade setup") ||
              text.includes("directional bias") ||
              text.includes("minimum 1:1.5")
            );
          });

          const assignedReasons = new Set([
            ...technicalReasons,
            ...patternStructureReasons,
            ...smcReasons,
            ...riskReasons,
          ]);

          const otherReasons = uniqueReasons.filter(
            (reason) => !assignedReasons.has(reason)
          );

          const sections = [
            {
              title: "Technical Indicators",
              description: "Core momentum and trend signals contributing to the AI decision.",
              items: technicalReasons,
              accent: "blue",
            },
            {
              title: "Candlestick & Market Structure",
              description: "Price-action evidence confirming or challenging the directional bias.",
              items: patternStructureReasons,
              accent: "purple",
            },
            {
              title: "Smart Money Concepts",
              description: "Institutional-style structure, order blocks, liquidity and imbalance signals.",
              items: smcReasons,
              accent: "yellow",
            },
            {
              title: "Risk & Decision",
              description: "Risk checks that determine whether the directional signal becomes a trade setup.",
              items: riskReasons,
              accent: "red",
            },
            {
              title: "Additional Factors",
              description: "Other supporting observations returned by the analysis engine.",
              items: otherReasons,
              accent: "slate",
            },
          ].filter((section) => section.items.length > 0);

          const accentClasses: Record<string, string> = {
            blue: "border-blue-900/40 bg-blue-950/10 text-blue-400",
            purple: "border-purple-900/40 bg-purple-950/10 text-purple-400",
            yellow: "border-yellow-900/40 bg-yellow-950/10 text-yellow-400",
            red: "border-red-900/40 bg-red-950/10 text-red-400",
            slate: "border-slate-800 bg-slate-950 text-slate-400",
          };

          return (
            <div className="mt-4 space-y-4">
              <div className={`rounded-xl border p-4 ${signalBg}`}>
                <p className="text-sm leading-6 text-slate-300">
                  MarketIQ detected a{" "}
                  <span className={`font-semibold ${signalColor}`}>
                    {action.toLowerCase()}
                  </span>{" "}
                  directional bias using multiple independent market factors.
                  The sections below show the evidence behind the final AI decision.
                </p>
              </div>

              {sections.length > 0 ? (
                sections.map((section) => (
                  <div
                    key={section.title}
                    className="overflow-hidden rounded-xl border border-slate-800 bg-slate-950"
                  >
                    <div className="border-b border-slate-800 px-4 py-4">
                      <div className="flex flex-col gap-1 sm:flex-row sm:items-center sm:justify-between">
                        <h3 className="text-sm font-semibold text-white">
                          {section.title}
                        </h3>
                        <span
                          className={`w-fit rounded-full border px-2.5 py-1 text-[11px] font-medium ${accentClasses[section.accent]}`}
                        >
                          {section.items.length} factor{section.items.length === 1 ? "" : "s"}
                        </span>
                      </div>
                      <p className="mt-1 text-xs leading-5 text-slate-500">
                        {section.description}
                      </p>
                    </div>

                    <div className="grid gap-2 p-3 md:grid-cols-2">
                      {section.items.map((reason, index) => (
                        <div
                          key={`${section.title}-${index}-${reason}`}
                          className="flex min-w-0 gap-3 rounded-lg border border-slate-800 bg-slate-900/60 px-3 py-3 text-sm text-slate-300"
                        >
                          <span
                            className={`mt-0.5 shrink-0 ${
                              isBuy
                                ? "text-green-400"
                                : isSell
                                ? "text-red-400"
                                : "text-yellow-400"
                            }`}
                          >
                            ✓
                          </span>
                          <span className="min-w-0 break-words">
                            {reason}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                ))
              ) : (
                <div className="rounded-xl border border-slate-800 bg-slate-950 p-4">
                  <p className="text-sm text-slate-500">
                    No additional explanation is available for this recommendation.
                  </p>
                </div>
              )}
            </div>
          );
        })()}

      </div>


      {/* ========================================================
          PATTERN ANALYSIS
      ======================================================== */}

      {patternAnalysis && (

        <div className="min-w-0 rounded-2xl border border-slate-800 bg-slate-900 p-5 shadow-lg sm:p-6">

          <h2 className="text-lg font-semibold text-white">
            Candlestick Pattern Analysis
          </h2>

          <div className="mt-4 grid grid-cols-3 gap-3">

            <div className="min-w-0 rounded-xl bg-slate-950 p-4">

              <p className="text-xs text-slate-500">
                Pattern
              </p>

              <p className="mt-1 break-words text-sm font-semibold text-white">
                {patternAnalysis.pattern ?? "Unknown"}
              </p>

            </div>

            <div className="min-w-0 rounded-xl bg-slate-950 p-4">

              <p className="text-xs text-slate-500">
                Signal
              </p>

              <p
                className={`mt-1 font-semibold ${
                  patternAnalysis.signal === "BUY"
                    ? "text-green-400"
                    : patternAnalysis.signal === "SELL"
                    ? "text-red-400"
                    : "text-yellow-400"
                }`}
              >
                {patternAnalysis.signal ?? "HOLD"}
              </p>

            </div>

            <div className="min-w-0 rounded-xl bg-slate-950 p-4">

              <p className="text-xs text-slate-500">
                Confidence
              </p>

              <p className="mt-1 font-semibold text-white">
                {patternAnalysis.confidence ?? 0}%
              </p>

            </div>

          </div>

        </div>

      )}


      {/* ========================================================
          MARKET STRUCTURE ANALYSIS
      ======================================================== */}

      {marketStructureAnalysis && (

        <div className="min-w-0 rounded-2xl border border-slate-800 bg-slate-900 p-5 shadow-lg sm:p-6">

          <h2 className="text-lg font-semibold text-white">
            Market Structure Contribution
          </h2>

          <div className="mt-4 grid grid-cols-2 gap-3">

            <div className="min-w-0 rounded-xl bg-slate-950 p-4">

              <p className="text-xs text-slate-500">
                Structure
              </p>

              <p className="mt-1 break-words font-semibold text-white">
                {marketStructureAnalysis.structure ??
                  "Neutral"}
              </p>

            </div>

            <div className="min-w-0 rounded-xl bg-slate-950 p-4">

              <p className="text-xs text-slate-500">
                Trend
              </p>

              <p className="mt-1 break-words font-semibold text-white">
                {marketStructureAnalysis.trend ??
                  "NEUTRAL"}
              </p>

            </div>

            <div className="min-w-0 rounded-xl bg-slate-950 p-4">

              <p className="text-xs text-slate-500">
                Signal
              </p>

              <p
                className={`mt-1 font-semibold ${
                  marketStructureAnalysis.signal === "BUY"
                    ? "text-green-400"
                    : marketStructureAnalysis.signal === "SELL"
                    ? "text-red-400"
                    : "text-yellow-400"
                }`}
              >
                {marketStructureAnalysis.signal ??
                  "HOLD"}
              </p>

            </div>

            <div className="min-w-0 rounded-xl bg-slate-950 p-4">

              <p className="text-xs text-slate-500">
                Confidence
              </p>

              <p className="mt-1 font-semibold text-white">
                {marketStructureAnalysis.confidence ??
                  0}
                %
              </p>

            </div>

          </div>

        </div>

      )}


      {/* ========================================================
          SUPPORT / RESISTANCE CONTRIBUTION
      ======================================================== */}

      {supportResistanceAnalysis && (

        <div className="min-w-0 rounded-2xl border border-slate-800 bg-slate-900 p-5 shadow-lg sm:p-6">

          <h2 className="text-lg font-semibold text-white">
            Support & Resistance Contribution
          </h2>

          <div className="mt-4 grid grid-cols-2 gap-3">

            <div className="min-w-0 rounded-xl border border-green-900/40 bg-slate-950 p-4">

              <p className="text-xs text-slate-500">
                Nearest Support
              </p>

              <p className="mt-1 break-words text-base font-semibold text-green-400">
                {formatPrice(
                  supportResistanceAnalysis.nearest_support
                )}
              </p>

            </div>

            <div className="min-w-0 rounded-xl border border-red-900/40 bg-slate-950 p-4">

              <p className="text-xs text-slate-500">
                Nearest Resistance
              </p>

              <p className="mt-1 break-words text-base font-semibold text-red-400">
                {formatPrice(
                  supportResistanceAnalysis.nearest_resistance
                )}
              </p>

            </div>

          </div>

        </div>

      )}


      {/* ========================================================
          DISCLAIMER
      ======================================================== */}

      <div className="rounded-xl border border-slate-800 bg-slate-950 p-4">

        <p className="text-xs leading-5 text-slate-500">
          MarketIQ provides AI-generated market analysis
          based on available technical data. Trade setups
          are algorithmically generated and are not
          guaranteed trading outcomes. Always perform your
          own research and risk assessment before making
          investment decisions.
        </p>

      </div>

    </div>
  );
}