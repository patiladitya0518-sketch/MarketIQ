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

  trade_quality?: "APPROVED" | "NOT_APPROVED" | string;
  v7_explanation?: {
    version?: string;
    primary?: string;
    summary?: string;
    hierarchy?: string[];
    signal_conflict?: string | boolean;
    layers?: {
      market_structure?: string;
      technical_trend_momentum?: string;
      smc?: string;
      support_resistance?: string;
      candlestick?: string;
    };
    signal_balance?: {
      bullish?: number;
      bearish?: number;
    };
    risk_reward?: number | null;
    trade_setup_approved?: boolean;
  };


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

  const explanation = recommendation?.v7_explanation;

  const setupApproved =
    typeof explanation?.trade_setup_approved === "boolean"
      ? explanation.trade_setup_approved
      : recommendation?.trade_quality === "APPROVED";

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
              {setupApproved ? "Trade Setup" : "Trade Setup Not Approved"}
            </h2>
          </div>

          {!setupApproved ? (
            <div className="rounded-xl border border-yellow-900/50 bg-yellow-950/10 p-5">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <p className="text-sm font-semibold text-yellow-400">
                  Directional signal detected — trade rejected
                </p>
                <span className="rounded-full bg-yellow-950/60 px-3 py-1 text-xs font-bold text-yellow-400">
                  NOT APPROVED
                </span>
              </div>

              <p className="mt-3 text-sm leading-6 text-slate-300">
                MarketIQ detected a {isBuy ? "BUY" : "SELL"} directional bias,
                but the calculated risk/reward does not meet the minimum
                1:1.5 requirement. Entry, stop loss and target are therefore
                not presented as an approved trade setup.
              </p>

              <div className="mt-4 rounded-lg border border-slate-800 bg-slate-950 p-4">
                <p className="text-xs text-slate-500">
                  Calculated Risk / Reward
                </p>
                <p className="mt-1 text-lg font-bold text-white">
                  {riskReward !== null &&
                  riskReward !== undefined &&
                  Number.isFinite(Number(riskReward))
                    ? `1 : ${Number(riskReward).toFixed(2)}`
                    : "—"}
                </p>
                <p className="mt-1 text-xs text-slate-500">
                  Minimum required: 1 : 1.50
                </p>
              </div>
            </div>
          ) : (
            <>
              <div className="grid grid-cols-2 gap-3">

                <div className={`${tradeCard} border-slate-800`}>
                  <p className="text-xs text-slate-400 sm:text-sm">
                    Entry Price
                  </p>
                  <p className="mt-2 break-words text-base font-bold text-white sm:text-lg">
                    {formatPrice(entryPrice)}
                  </p>
                </div>

                <div className={`${tradeCard} border-red-900/40`}>
                  <p className="text-xs text-slate-400 sm:text-sm">
                    Stop Loss
                  </p>
                  <p className="mt-2 break-words text-base font-bold text-red-400 sm:text-lg">
                    {formatPrice(stopLoss)}
                  </p>
                </div>

                <div className={`${tradeCard} border-green-900/40`}>
                  <p className="text-xs text-slate-400 sm:text-sm">
                    Target
                  </p>
                  <p className="mt-2 break-words text-base font-bold text-green-400 sm:text-lg">
                    {formatPrice(target)}
                  </p>
                </div>

                <div className={`${tradeCard} border-slate-800`}>
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

              <div className={`mt-5 min-w-0 rounded-xl border p-4 ${signalBg}`}>
                <p className="text-xs text-slate-400 sm:text-sm">
                  Trade Direction
                </p>
                <p className={`mt-1 break-words text-base font-semibold sm:text-lg ${signalColor}`}>
                  {isBuy
                    ? "Bullish setup — potential BUY"
                    : "Bearish setup — potential SELL"}
                </p>
              </div>
            </>
          )}
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
          WHY AI GAVE THIS SIGNAL — V7.1 HIERARCHICAL EXPLANATION
      ======================================================== */}
      <div className="min-w-0 rounded-2xl border border-slate-800 bg-slate-900 p-5 shadow-lg sm:p-6">
        <h2 className="text-lg font-semibold text-white">
          Why AI gave this signal
        </h2>

        {(() => {
          const primary =
            explanation?.primary ||
            `${recommendation.recommendation} is the current directional signal based on the combined evidence.`;

          const summary =
            explanation?.summary ||
            "MarketIQ combines market structure, technical momentum, SMC, support/resistance and risk before presenting the final signal.";

          const hierarchy =
            Array.isArray(explanation?.hierarchy) &&
            explanation.hierarchy.length > 0
              ? explanation.hierarchy
              : [
                  "Market Structure",
                  "Technical Trend & Momentum",
                  "Smart Money Concepts",
                  "Support & Resistance",
                  "Candlestick",
                ];

          const layers = explanation?.layers || {};

          const fallbackMarketStructure =
            marketStructureAnalysis?.signal ||
            marketStructureAnalysis?.trend ||
            "Market structure evidence is unavailable.";

          const fallbackTechnical =
            reasons
              .filter((reason) => {
                const text = reason.toLowerCase();
                return (
                  text.includes("rsi") ||
                  text.includes("ema20") ||
                  text.includes("ema50") ||
                  text.includes("macd") ||
                  text.includes("price")
                );
              })
              .slice(0, 4)
              .join("; ") ||
            "Technical trend and momentum evidence is unavailable.";

          const fallbackSmc =
            reasons
              .filter((reason) => {
                const text = reason.toLowerCase();
                return (
                  text.includes("smc") ||
                  text.includes("order block") ||
                  text.includes("fair value gap") ||
                  text.includes("fvg") ||
                  text.includes("liquidity") ||
                  text.includes("break of structure") ||
                  text.includes("bos") ||
                  text.includes("change of character") ||
                  text.includes("choch")
                );
              })
              .slice(0, 8)
              .join("; ") ||
            "SMC evidence is unavailable.";

          const fallbackSupportResistance =
            supportResistanceAnalysis
              ? `Nearest support ${formatPrice(
                  supportResistanceAnalysis.nearest_support
                )}; nearest resistance ${formatPrice(
                  supportResistanceAnalysis.nearest_resistance
                )}.`
              : "Support and resistance evidence is unavailable.";

          const fallbackCandlestick =
            patternAnalysis?.pattern
              ? `${patternAnalysis.pattern} (${patternAnalysis.signal ?? "HOLD"}, ${patternAnalysis.confidence ?? 0}% confidence)`
              : "No strong candlestick pattern was detected.";

          const marketStructureSignal =
            String(marketStructureAnalysis?.signal ?? "HOLD").toUpperCase();
          const marketStructureConfidence = Number(
            marketStructureAnalysis?.confidence ?? 50
          );
          const marketStructureIsNeutral =
            marketStructureSignal !== "BUY" && marketStructureSignal !== "SELL";

          const structureValue = marketStructureIsNeutral
            ? `Market structure is neutral (${marketStructureSignal}, ${
                Number.isFinite(marketStructureConfidence)
                  ? marketStructureConfidence.toFixed(0)
                  : "50"
              }% confidence) and does not independently confirm the final ${action} signal. Other evidence layers provide the directional support.`
            : layers.market_structure ||
              `Market structure is ${marketStructureSignal} and contributes to the final ${action} directional decision.`;

          const layerItems = [
            {
              key: "market_structure",
              title: "1. Market Structure",
              description: "Highest-priority structural evidence. Neutral structure is explicitly treated as non-confirming.",
              value: structureValue,
            },
            {
              key: "technical_trend_momentum",
              title: "2. Technical Trend & Momentum",
              description: "RSI, EMA relationship and MACD supporting evidence.",
              value: layers.technical_trend_momentum || fallbackTechnical,
            },
            {
              key: "smc",
              title: "3. Smart Money Concepts",
              description: "SMC directional bias is shown separately from a fully confirmed executable SMC setup.",
              value: layers.smc || fallbackSmc,
            },
            {
              key: "support_resistance",
              title: "4. Support & Resistance",
              description: "Location and tradeability context, not an independent directional vote.",
              value: layers.support_resistance || fallbackSupportResistance,
            },
            {
              key: "candlestick",
              title: "5. Candlestick",
              description: "Latest price-action pattern, when meaningful.",
              value: layers.candlestick || fallbackCandlestick,
            },
          ].filter(
            (item) =>
              typeof item.value === "string" &&
              item.value.trim().length > 0
          );

          const conflict =
            typeof explanation?.signal_conflict === "string" &&
            explanation.signal_conflict.trim().length > 0
              ? explanation.signal_conflict
              : null;

          const rr =
            typeof explanation?.risk_reward === "number"
              ? explanation.risk_reward
              : recommendation.risk_reward;

          return (
            <div className="mt-5 space-y-5">
              {/* PRIMARY DECISION */}
              <div className="rounded-xl border border-slate-700 bg-slate-950 p-5">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">
                    AI Decision
                  </span>
                  <span
                    className={`rounded-full px-3 py-1 text-xs font-bold ${
                      recommendation.recommendation === "BUY"
                        ? "bg-green-950/60 text-green-400"
                        : recommendation.recommendation === "SELL"
                        ? "bg-red-950/60 text-red-400"
                        : "bg-yellow-950/60 text-yellow-400"
                    }`}
                  >
                    {recommendation.recommendation}
                  </span>
                </div>

                <p className="mt-3 text-base font-medium leading-7 text-white">
                  {primary}
                </p>

                <p className="mt-2 text-sm leading-6 text-slate-400">
                  {summary}
                </p>
              </div>

              {/* SIGNAL HIERARCHY */}
              {hierarchy.length > 0 && (
                <div className="rounded-xl border border-slate-800 bg-slate-950 p-5">
                  <h3 className="text-sm font-semibold text-white">
                    Signal hierarchy
                  </h3>
                  <p className="mt-1 text-xs leading-5 text-slate-500">
                    MarketIQ does not treat every explanation sentence as an
                    equal-weight factor. Higher-priority evidence can outweigh
                    a larger number of lower-priority observations.
                  </p>

                  <div className="mt-4 space-y-2">
                    {hierarchy.map((item, index) => (
                      <div
                        key={`${index}-${item}`}
                        className="flex gap-3 rounded-lg border border-slate-800 bg-slate-900 px-4 py-3 text-sm text-slate-300"
                      >
                        <span className="shrink-0 font-semibold text-slate-500">
                          {index + 1}.
                        </span>
                        <span>{item}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* EVIDENCE LAYERS */}
              <div className="rounded-xl border border-slate-800 bg-slate-950 p-5">
                <div className="flex items-center justify-between gap-3">
                  <h3 className="text-sm font-semibold text-white">
                    Decision evidence
                  </h3>
                  <span className="text-xs text-slate-500">
                    Hierarchical evidence
                  </span>
                </div>

                <div className="mt-4 space-y-3">
                  {layerItems.map((item) => (
                    <div
                      key={item.key}
                      className="rounded-lg border border-slate-800 bg-slate-900 p-4"
                    >
                      <p className="text-sm font-semibold text-slate-200">
                        {item.title}
                      </p>
                      <p className="mt-1 text-xs leading-5 text-slate-500">
                        {item.description}
                      </p>
                      <p className="mt-2 text-sm leading-6 text-slate-300">
                        {item.value}
                      </p>
                    </div>
                  ))}
                </div>
              </div>

              {/* CONFLICT */}
              {conflict && (
                <div className="rounded-xl border border-yellow-900/50 bg-yellow-950/10 p-5">
                  <p className="text-sm font-semibold text-yellow-400">
                    Signal conflict / caution
                  </p>
                  <p className="mt-2 text-sm leading-6 text-slate-300">
                    {conflict}
                  </p>
                </div>
              )}

              {/* RISK / TRADEABILITY */}
              <div className="rounded-xl border border-slate-800 bg-slate-950 p-5">
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <h3 className="text-sm font-semibold text-white">
                    Risk & tradeability
                  </h3>

                  <span
                    className={`rounded-full px-3 py-1 text-xs font-bold ${
                      setupApproved
                        ? "bg-green-950/60 text-green-400"
                        : "bg-yellow-950/60 text-yellow-400"
                    }`}
                  >
                    {setupApproved ? "SETUP APPROVED" : "SETUP NOT APPROVED"}
                  </span>
                </div>

                <p className="mt-3 text-sm leading-6 text-slate-300">
                  Directional bias and trade approval are separate decisions.
                  MarketIQ can identify BUY or SELL pressure while still
                  rejecting the trade when the entry quality or risk/reward is
                  inadequate.
                </p>

                {typeof rr === "number" && (
                  <p className="mt-3 text-sm font-medium text-slate-200">
                    Calculated Risk / Reward:{" "}
                    <span className="text-white">
                      1 : {rr.toFixed(2)}
                    </span>
                  </p>
                )}
              </div>

              {/* ACTUAL FACTOR BALANCE — not explanation sentence count */}
              {explanation?.signal_balance && (
                <div className="rounded-xl border border-slate-800 bg-slate-950 p-5">
                  <h3 className="text-sm font-semibold text-white">
                    Signal balance
                  </h3>
                  <div className="mt-3 grid grid-cols-2 gap-3">
                    <div className="rounded-lg border border-green-900/40 bg-slate-900 p-3">
                      <p className="text-xs text-slate-500">Bullish</p>
                      <p className="mt-1 text-xl font-bold text-green-400">
                        {explanation.signal_balance.bullish ?? bullishFactors}
                      </p>
                    </div>

                    <div className="rounded-lg border border-red-900/40 bg-slate-900 p-3">
                      <p className="text-xs text-slate-500">Bearish</p>
                      <p className="mt-1 text-xl font-bold text-red-400">
                        {explanation.signal_balance.bearish ?? bearishFactors}
                      </p>
                    </div>
                  </div>

                  <p className="mt-3 text-xs leading-5 text-slate-500">
                    These counts are signal-balance values. They are not the
                    number of explanatory sentences shown above.
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