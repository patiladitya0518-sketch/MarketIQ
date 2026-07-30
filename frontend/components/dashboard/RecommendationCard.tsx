"use client";

import {
  ArrowUpCircle,
  ArrowDownCircle,
  MinusCircle,
  Brain,
  Shield,
  Target,
  TrendingUp,
} from "lucide-react";

interface Props {
  recommendation: string;
  confidence: number;
  reasons: string[];
}

export default function RecommendationCard({
  recommendation,
  confidence,
  reasons,
}: Props) {
  const isBuy = recommendation === "BUY";
  const isSell = recommendation === "SELL";

  const icon = isBuy ? (
    <ArrowUpCircle size={28} />
  ) : isSell ? (
    <ArrowDownCircle size={28} />
  ) : (
    <MinusCircle size={28} />
  );

  const colour = isBuy
    ? "text-green-400"
    : isSell
    ? "text-red-400"
    : "text-yellow-400";

  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6 shadow-xl">

      {/* Header */}

      <div className="mb-6 flex items-center gap-3">

        <div className={`${colour}`}>
          {icon}
        </div>

        <div>
          <h2 className="text-xl font-bold text-white">
            AI Recommendation
          </h2>

          <p className="text-sm text-slate-400">
            Generated using technical indicators
          </p>
        </div>

      </div>

      {/* Recommendation */}

      <div className="mb-6 rounded-xl bg-slate-800 p-4">

        <div className={`text-3xl font-bold ${colour}`}>
          {recommendation}
        </div>

        <div className="mt-2 text-sm text-slate-400">
          Confidence
        </div>

        <div className="mt-2 h-3 overflow-hidden rounded-full bg-slate-700">

          <div
            className={`h-full rounded-full ${
              confidence >= 75
                ? "bg-green-500"
                : confidence >= 50
                ? "bg-yellow-500"
                : "bg-red-500"
            }`}
            style={{
              width: `${confidence}%`,
            }}
          />

        </div>

        <div className="mt-2 text-right text-white font-semibold">
          {confidence}%
        </div>

      </div>

      {/* AI Stats */}

      <div className="grid grid-cols-2 gap-4">

        <div className="rounded-xl bg-slate-800 p-4">
          <div className="mb-2 flex items-center gap-2 text-slate-400">
            <Target size={16} />
            Target
          </div>

          <div className="text-lg font-bold text-green-400">
            Dynamic
          </div>
        </div>

        <div className="rounded-xl bg-slate-800 p-4">
          <div className="mb-2 flex items-center gap-2 text-slate-400">
            <Shield size={16} />
            Risk
          </div>

          <div className="text-lg font-bold text-yellow-400">
            Medium
          </div>
        </div>

        <div className="rounded-xl bg-slate-800 p-4">
          <div className="mb-2 flex items-center gap-2 text-slate-400">
            <TrendingUp size={16} />
            Trend
          </div>

          <div className={`text-lg font-bold ${colour}`}>
            {recommendation}
          </div>
        </div>

        <div className="rounded-xl bg-slate-800 p-4">
          <div className="mb-2 flex items-center gap-2 text-slate-400">
            <Brain size={16} />
            AI Score
          </div>

          <div className="text-lg font-bold text-blue-400">
            {confidence}/100
          </div>
        </div>

      </div>

      {/* Reasons */}

      <div className="mt-6">

        <h3 className="mb-3 text-lg font-semibold text-white">
          Analysis
        </h3>

        <div className="space-y-2">

          {reasons.map((reason, index) => (
            <div
              key={index}
              className="rounded-lg bg-slate-800 p-3 text-sm text-slate-300"
            >
              ✓ {reason}
            </div>
          ))}

        </div>

      </div>

    </div>
  );
}