"use client";

import { useEffect, useState } from "react";
import api from "@/lib/api";

export default function useStock(symbol: string) {
  const [data, setData] = useState<any>(null);
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

  return { data, loading };
}