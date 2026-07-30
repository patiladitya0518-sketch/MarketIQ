import { Bot, BarChart3, CandlestickChart, LineChart, Briefcase, Activity } from "lucide-react";
import Card from "@/components/ui/Card";

const features = [
  { icon: Bot, title: "AI Analysis" },
  { icon: BarChart3, title: "Technical Indicators" },
  { icon: CandlestickChart, title: "Pattern Detection" },
  { icon: LineChart, title: "Live Charts" },
  { icon: Activity, title: "Backtesting" },
  { icon: Briefcase, title: "Paper Trading" },
];

export default function Features() {
  return (
    <section className="mx-auto mt-24 max-w-6xl px-6">
      <h2 className="mb-10 text-center text-3xl font-bold text-white">
        Features
      </h2>

      <div className="grid gap-6 md:grid-cols-3">
        {features.map((feature) => {
          const Icon = feature.icon;

          return (
            <Card key={feature.title} className="text-center">
              <Icon className="mx-auto mb-4 h-10 w-10 text-blue-500" />
              <h3 className="text-lg font-semibold text-white">
                {feature.title}
              </h3>
            </Card>
          );
        })}
      </div>
    </section>
  );
}