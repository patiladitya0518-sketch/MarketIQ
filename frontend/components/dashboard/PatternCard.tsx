"use client";

import {
  Activity,
  CheckCircle2,
  AlertTriangle,
  XCircle,
} from "lucide-react";

interface Pattern {
  pattern: string;
  signal: string;
  confidence: number;
  reason: string[];
}

interface Props {
  pattern?: Pattern | null;
}

function getSignalStyles(signal: string) {
  if (signal === "BUY") {
    return {
      text: "text-green-400",
      bg: "bg-green-950/40",
      border: "border-green-900/50",
    };
  }

  if (signal === "SELL") {
    return {
      text: "text-red-400",
      bg: "bg-red-950/40",
      border: "border-red-900/50",
    };
  }

  return {
    text: "text-yellow-400",
    bg: "bg-yellow-950/40",
    border: "border-yellow-900/50",
  };
}

export default function PatternCard({
  pattern,
}: Props) {
  if (!pattern) {
    return (
      <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6 shadow-lg">

        <div className="flex items-center gap-3">

          <Activity
            size={24}
            className="text-blue-400"
          />

          <div>
            <h2 className="text-xl font-bold text-white">
              AI Pattern Detection
            </h2>

            <p className="text-sm text-slate-500">
              No pattern data available
            </p>
          </div>

        </div>

      </div>
    );
  }

  const styles = getSignalStyles(pattern.signal);

  const safeConfidence = Math.max(
    0,
    Math.min(100, pattern.confidence)
  );

  const SignalIcon =
    pattern.signal === "BUY"
      ? CheckCircle2
      : pattern.signal === "SELL"
      ? XCircle
      : AlertTriangle;

  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6 shadow-lg">

      {/* ======================================================
          HEADER
      ====================================================== */}

      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">

        <div className="flex items-center gap-3">

          <div className="rounded-xl bg-blue-950/40 p-3">
            <Activity
              size={24}
              className="text-blue-400"
            />
          </div>

          <div>

            <h2 className="text-xl font-bold text-white">
              AI Pattern Detection
            </h2>

            <p className="text-sm text-slate-500">
              Technical chart pattern analysis
            </p>

          </div>

        </div>

        {/* SIGNAL */}

        <div
          className={`flex items-center gap-2 rounded-xl border px-4 py-2 ${styles.bg} ${styles.border}`}
        >

          <SignalIcon
            size={18}
            className={styles.text}
          />

          <span
            className={`font-bold ${styles.text}`}
          >
            {pattern.signal}
          </span>

        </div>

      </div>

      {/* ======================================================
          PATTERN
      ====================================================== */}

      <div className="mt-6 grid gap-6 md:grid-cols-2">

        <div className="rounded-xl bg-slate-800 p-5">

          <p className="text-sm text-slate-500">
            Detected Pattern
          </p>

          <h3 className="mt-2 text-2xl font-bold text-white">
            {pattern.pattern}
          </h3>

        </div>

        <div className="rounded-xl bg-slate-800 p-5">

          <div className="flex items-center justify-between">

            <p className="text-sm text-slate-500">
              Pattern Confidence
            </p>

            <span
              className={`font-bold ${styles.text}`}
            >
              {pattern.confidence}%
            </span>

          </div>

          <div className="mt-3 h-3 overflow-hidden rounded-full bg-slate-700">

            <div
              className={`h-full rounded-full ${
                pattern.signal === "BUY"
                  ? "bg-green-500"
                  : pattern.signal === "SELL"
                  ? "bg-red-500"
                  : "bg-yellow-500"
              }`}
              style={{
                width: `${safeConfidence}%`,
              }}
            />

          </div>

        </div>

      </div>

      {/* ======================================================
          REASONS
      ====================================================== */}

      <div className="mt-6">

        <h3 className="mb-3 text-lg font-semibold text-white">
          Pattern Analysis
        </h3>

        {pattern.reason.length > 0 ? (
          <div className="grid gap-3 md:grid-cols-2">

            {pattern.reason.map(
              (reason, index) => (
                <div
                  key={`${reason}-${index}`}
                  className="rounded-xl border border-slate-800 bg-slate-800 px-4 py-3 text-sm text-slate-300"
                >
                  <span className="mr-2 text-blue-400">
                    ✓
                  </span>

                  {reason}
                </div>
              )
            )}

          </div>
        ) : (
          <div className="rounded-xl bg-slate-800 p-4 text-sm text-slate-500">
            No detailed pattern reasons available.
          </div>
        )}

      </div>

    </div>
  );
}