export default function NewsCard() {
  const news = [
    {
      title: "Reliance announces ₹20,000 Cr renewable energy investment",
      sentiment: "Positive",
    },
    {
      title: "RBI keeps repo rate unchanged in latest monetary policy",
      sentiment: "Neutral",
    },
    {
      title: "Infosys beats quarterly earnings estimates",
      sentiment: "Positive",
    },
    {
      title: "Tata Motors shares fall after weaker-than-expected sales",
      sentiment: "Negative",
    },
    {
      title: "NIFTY closes higher led by banking and IT stocks",
      sentiment: "Positive",
    },
  ];

  const sentimentColor = (sentiment: string) => {
    switch (sentiment) {
      case "Positive":
        return "text-green-400";
      case "Negative":
        return "text-red-400";
      default:
        return "text-yellow-400";
    }
  };

  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6 shadow-lg">
      <h2 className="mb-5 text-xl font-bold text-white">
        📰 Latest Financial News
      </h2>

      <div className="space-y-4">
        {news.map((item, index) => (
          <div
            key={index}
            className="rounded-xl border border-slate-800 bg-slate-800 p-4"
          >
            <h3 className="font-medium text-white">{item.title}</h3>

            <p
              className={`mt-2 text-sm font-semibold ${sentimentColor(
                item.sentiment
              )}`}
            >
              {item.sentiment}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}