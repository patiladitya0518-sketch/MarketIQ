"use client";

import { useEffect, useState } from "react";
import api from "@/lib/api";

interface Pattern {
  pattern: string;
  signal: string;
  confidence: number;
  reason: string[];
}

interface Recommendation {
  recommendation: string;
  confidence: number;
  reasons: string[];
}

interface Indicators {
  RSI: number;
  EMA20: number;
  EMA50: number;
  MACD: number;
  MACD_SIGNAL: number;
}

export interface StockResponse {
  success: boolean;
  symbol: string;
  price: number;
  indicators: Indicators;
  recommendation: Recommendation;

  // NEW
  pattern: Pattern;
}

export default function useStock(symbol: string) {
  const [data, setData] = useState<StockResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!symbol) return;

    async function fetchStock() {
      setLoading(true);

      try {
        const res = await api.get(`/stock/${symbol}`);

        if (res.data.success) {
          setData(res.data);
        } else {
          alert(res.data.message);
        }
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }

    fetchStock();
  }, [symbol]);

  return {
    data,
    loading,
  };
}