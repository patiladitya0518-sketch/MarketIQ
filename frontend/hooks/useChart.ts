import { useEffect, useState } from "react";
import api from "@/lib/api";

export interface Candle {
  time: string;
  open: number;
  high: number;
  low: number;
  close: number;

  volume: number;

  ema20: number;
  ema50: number;

  rsi: number;

  macd: number;
  macdSignal: number;
}

interface Levels {
  support: number[];
  resistance: number[];
}

export default function useChart(
  symbol: string,
  period: string = "6M"
) {
  const [data, setData] = useState<Candle[]>([]);
  const [levels, setLevels] = useState<Levels>({
    support: [],
    resistance: [],
  });

  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchChart() {
      try {
        setLoading(true);

        const res = await api.get(
          `/chart/${symbol}?period=${period}`
        );

        if (res.data.success) {
          setData(res.data.data);
          setLevels(res.data.levels);
        }
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }

    fetchChart();
  }, [symbol, period]);

  return {
    data,
    levels,
    loading,
  };
}