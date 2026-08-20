"use client";

import {
  ArrowUpCircle,
  ArrowDownCircle,
  MinusCircle,
  Brain,
  Shield,
  Target,
  TrendingUp,
  Activity,
  Layers,
  BarChart3,
} from "lucide-react";

interface PatternAnalysis {
  pattern: string;
  signal: string;
  confidence: number;
}

interface MarketStructureAnalysis {
  structure: string;
  trend: string;
  signal: string;
  confidence: number;
}

interface SupportResistanceAnalysis {
  nearest_support: number | null;
  nearest_resistance: number | null;
}

interface Props {
  recommendation: string;
  confidence: number;
  score?: number;
  reasons: string[];

  patternAnalysis?: PatternAnalysis | null;

  marketStructureAnalysis?: MarketStructureAnalysis | null;

  supportResistanceAnalysis?: SupportResistanceAnalysis | null;
}

function formatPrice(value: number | null | undefined) {
  if (value === null || value === undefined) {
    return "—";
  }

  return `₹${value.toLocaleString("en-IN", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}`;
}

export default function RecommendationCard({
  recommendation,
  confidence,
  score,
  reasons,
  patternAnalysis,
  marketStructureAnalysis,
  supportResistanceAnalysis,
}: Props) {
  const signal = recommendation.toUpperCase();

  const isBuy = signal === "BUY";
  const isSell = signal === "SELL";

  const icon = isBuy ? (
    <ArrowUpCircle size={30} />
  ) : isSell ? (
    <ArrowDownCircle size={30} />
  ) : (
    <MinusCircle size={30} />
  );

  const colour = isBuy
    ? "text-green-400"
    : isSell
    ? "text-red-400"
    : "text-yellow-400";

  const signalBackground = isBuy
    ? "bg-green-950/40 border-green-800/60"
    : isSell
    ? "bg-red-950/40 border-red-800/60"
    : "bg-yellow-950/40 border-yellow-800/60";

  const confidenceColor =
    confidence >= 75
      ? "bg-green-500"
      : confidence >= 50
      ? "bg-yellow-500"
      : "bg-red-500";

  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6 shadow-xl">

      {/* =====================================================
          HEADER
      ===================================================== */}

      <div className="mb-6 flex items-center gap-3">

        <div className={colour}>
          {icon}
        </div>

        <div>
          <h2 className="text-xl font-bold text-white">
            AI Recommendation
          </h2>

          <p className="text-sm text-slate-400">
            Multi-factor market analysis
          </p>
        </div>

      </div>

      {/* =====================================================
          MAIN SIGNAL
      ===================================================== */}

      <div
        className={`mb-6 rounded-xl border p-5 ${signalBackground}`}
      >

        <div className="flex items-center justify-between">

          <div>

            <p className="text-xs uppercase tracking-wider text-slate-400">
              Current Signal
            </p>

            <div
              className={`mt-1 text-4xl font-bold ${colour}`}
            >
              {signal}
            </div>

          </div>

          <div className="text-right">

            <p className="text-xs text-slate-500">
              AI Score
            </p>

            <p className={`text-2xl font-bold ${colour}`}>
              {score !== undefined ? score : "—"}
            </p>

          </div>

        </div>

        {/* Confidence */}

        <div className="mt-5">

          <div className="mb-2 flex justify-between">

            <span className="text-sm text-slate-400">
              Confidence
            </span>

            <span
              className={`text-sm font-bold ${colour}`}
            >
              {confidence}%
            </span>

          </div>

          <div className="h-3 overflow-hidden rounded-full bg-slate-800">

            <div
              className={`h-full rounded-full transition-all duration-500 ${confidenceColor}`}
              style={{
                width: `${Math.min(
                  Math.max(confidence, 0),
                  100
                )}%`,
              }}
            />

          </div>

        </div>

      </div>

      {/* =====================================================
          ANALYSIS COMPONENTS
      ===================================================== */}

      <div className="mb-6 grid grid-cols-1 gap-3 sm:grid-cols-2">

        {/* Pattern */}

        <div className="rounded-xl border border-slate-800 bg-slate-800/70 p-4">

          <div className="mb-2 flex items-center gap-2 text-slate-400">

            <Activity size={16} />

            <span className="text-sm">
              Pattern
            </span>

          </div>

          {patternAnalysis ? (
            <>
              <p className="font-semibold text-white">
                {patternAnalysis.pattern}
              </p>

              <div className="mt-1 flex items-center justify-between">

                <span
                  className={`text-sm font-semibold ${
                    patternAnalysis.signal === "BUY"
                      ? "text-green-400"
                      : patternAnalysis.signal ===
                        "SELL"
                      ? "text-red-400"
                      : "text-yellow-400"
                  }`}
                >
                  {patternAnalysis.signal}
                </span>

                <span className="text-xs text-slate-500">
                  {patternAnalysis.confidence}%
                </span>

              </div>
            </>
          ) : (
            <p className="text-sm text-slate-500">
              Not available
            </p>
          )}

        </div>

        {/* Market Structure */}

        <div className="rounded-xl border border-slate-800 bg-slate-800/70 p-4">

          <div className="mb-2 flex items-center gap-2 text-slate-400">

            <Layers size={16} />

            <span className="text-sm">
              Market Structure
            </span>

          </div>

          {marketStructureAnalysis ? (
            <>
              <p className="font-semibold text-white">
                {marketStructureAnalysis.structure}
              </p>

              <div className="mt-1 flex items-center justify-between">

                <span className="text-sm text-slate-300">
                  {marketStructureAnalysis.trend}
                </span>

                <span
                  className={`text-xs font-semibold ${
                    marketStructureAnalysis.signal ===
                    "BUY"
                      ? "text-green-400"
                      : marketStructureAnalysis.signal ===
                        "SELL"
                      ? "text-red-400"
                      : "text-yellow-400"
                  }`}
                >
                  {marketStructureAnalysis.signal}
                </span>

              </div>
            </>
          ) : (
            <p className="text-sm text-slate-500">
              Not available
            </p>
          )}

        </div>

      </div>

      {/* =====================================================
          SUPPORT / RESISTANCE
      ===================================================== */}

      <div className="mb-6 rounded-xl border border-slate-800 bg-slate-800/70 p-4">

        <div className="mb-4 flex items-center gap-2 text-slate-400">

          <BarChart3 size={17} />

          <span className="text-sm font-medium">
            Key Price Levels
          </span>

        </div>

        <div className="grid grid-cols-2 gap-3">

          <div className="rounded-lg bg-green-950/30 p-3">

            <p className="text-xs text-green-500">
              Support
            </p>

            <p className="mt-1 font-bold text-green-400">
              {formatPrice(
                supportResistanceAnalysis
                  ?.nearest_support
              )}
            </p>

          </div>

          <div className="rounded-lg bg-red-950/30 p-3">

            <p className="text-xs text-red-500">
              Resistance
            </p>

            <p className="mt-1 font-bold text-red-400">
              {formatPrice(
                supportResistanceAnalysis
                  ?.nearest_resistance
              )}
            </p>

          </div>

        </div>

      </div>

      {/* =====================================================
          AI STATS
      ===================================================== */}

      <div className="mb-6 grid grid-cols-2 gap-3">

        <div className="rounded-xl bg-slate-800 p-4">

          <div className="mb-2 flex items-center gap-2 text-slate-400">

            <Target size={16} />

            <span className="text-sm">
              Target
            </span>

          </div>

          <div className="text-lg font-bold text-blue-400">
            Dynamic
          </div>

        </div>

        <div className="rounded-xl bg-slate-800 p-4">

          <div className="mb-2 flex items-center gap-2 text-slate-400">

            <Shield size={16} />

            <span className="text-sm">
              Risk
            </span>

          </div>

          <div className="text-lg font-bold text-yellow-400">
            Medium
          </div>

        </div>

        <div className="rounded-xl bg-slate-800 p-4">

          <div className="mb-2 flex items-center gap-2 text-slate-400">

            <TrendingUp size={16} />

            <span className="text-sm">
              Trend
            </span>

          </div>

          <div className={`text-lg font-bold ${colour}`}>
            {marketStructureAnalysis?.trend ??
              signal}
          </div>

        </div>

        <div className="rounded-xl bg-slate-800 p-4">

          <div className="mb-2 flex items-center gap-2 text-slate-400">

            <Brain size={16} />

            <span className="text-sm">
              AI Confidence
            </span>

          </div>

          <div className="text-lg font-bold text-blue-400">
            {confidence}/100
          </div>

        </div>

      </div>

      {/* =====================================================
          AI REASONS
      ===================================================== */}

      <div>

        <div className="mb-3 flex items-center gap-2">

          <Brain
            size={18}
            className="text-blue-400"
          />

          <h3 className="text-lg font-semibold text-white">
            Why AI gave this signal
          </h3>

        </div>

        {reasons.length > 0 ? (

          <div className="space-y-2">

            {reasons.map((reason, index) => (

              <div
                key={`${index}-${reason}`}
                className="rounded-lg border border-slate-800 bg-slate-800 p-3 text-sm text-slate-300"
              >
                <span className="mr-2 text-blue-400">
                  ✓
                </span>

                {reason}
              </div>

            ))}

          </div>

        ) : (

          <div className="rounded-lg bg-slate-800 p-3 text-sm text-slate-500">
            No detailed reasoning available.
          </div>

        )}

      </div>

      {/* =====================================================
          DISCLAIMER
      ===================================================== */}

      <div className="mt-6 rounded-lg border border-slate-800 bg-slate-950 p-3">

        <p className="text-xs leading-relaxed text-slate-500">
          MarketIQ provides AI-generated market analysis
          based on available technical data. Signals are
          informational and should not be treated as guaranteed
          trading outcomes.
        </p>

      </div>

    </div>
  );
}