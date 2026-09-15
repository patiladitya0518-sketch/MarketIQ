import Navbar from "@/components/layout/Navbar";
import Hero from "@/components/home/Hero";
import MarketOverview from "@/components/home/MarketOverview";
import Features from "@/components/home/Features";
import Stats from "@/components/home/Stats";


export default function Home() {
  return (
    <main className="min-h-screen bg-slate-950">
      <Navbar />
      <Hero />
     <Stats />
      <MarketOverview />
      <Features />
    </main>
  );
}