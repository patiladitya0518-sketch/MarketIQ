const stats = [
  { value: "50+", label: "Technical Indicators" },
  { value: "40+", label: "Chart Patterns" },
  { value: "10K+", label: "Analyses Processed" },
  { value: "99.9%", label: "Platform Uptime" },
];

export default function Stats() {
  return (
    <section className="mx-auto mt-24 max-w-6xl px-6">
      <div className="grid grid-cols-2 gap-6 md:grid-cols-4">
        {stats.map((stat) => (
          <div
            key={stat.label}
            className="rounded-2xl border border-slate-800 bg-slate-900 p-6 text-center"
          >
            <h3 className="text-4xl font-bold text-blue-500">
              {stat.value}
            </h3>
            <p className="mt-2 text-slate-400">
              {stat.label}
            </p>
          </div>
        ))}
      </div>
    </section>
  );
}