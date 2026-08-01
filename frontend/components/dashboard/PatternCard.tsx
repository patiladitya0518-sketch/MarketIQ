interface Props {
  pattern?: {
    pattern: string;
    signal: string;
    confidence: number;
    reason: string[];
  };
}

export default function PatternCard({ pattern }: Props) {
  if (!pattern) {
    return (
      <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6 shadow-lg">
        <h2 className="text-xl font-bold text-white">
          🤖 AI Pattern Detection
        </h2>

        <p className="mt-4 text-slate-400">
          Loading pattern...
        </p>
      </div>
    );
  }

  const signalColor =
    pattern.signal === "BUY"
      ? "text-green-400"
      : pattern.signal === "SELL"
      ? "text-red-400"
      : "text-yellow-400";

  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6 shadow-lg">

      <div className="mb-5 flex items-center justify-between">
        <h2 className="text-xl font-bold text-white">
          🤖 AI Pattern Detection
        </h2>

        <span className={`text-lg font-bold ${signalColor}`}>
          {pattern.signal}
        </span>
      </div>

      <div className="space-y-5">

        <div>
          <p className="text-sm text-slate-400">
            Pattern
          </p>

          <h3 className="mt-1 text-2xl font-bold text-white">
            {pattern.pattern}
          </h3>
        </div>

        <div>
          <p className="text-sm text-slate-400">
            Confidence
          </p>

          <h3 className="mt-1 text-xl font-bold text-blue-400">
            {pattern.confidence}%
          </h3>
        </div>

        <div>
          <p className="mb-3 text-sm text-slate-400">
            AI Reasons
          </p>

          <div className="space-y-2">
            {pattern.reason.map((item, index) => (
              <div
                key={index}
                className="rounded-lg bg-slate-800 p-3 text-slate-300"
              >
                ✔ {item}
              </div>
            ))}
          </div>
        </div>

      </div>

    </div>
  );
}