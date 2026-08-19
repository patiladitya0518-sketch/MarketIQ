"use client";

import { useCallback, useEffect, useState } from "react";
import api from "@/lib/api";

export interface PortfolioItem {
  id: string;
  symbol: string;
  quantity: number;
  average_price: number;

  // Live market data
  current_price: number | null;

  // P&L data
  invested_value: number;
  current_value: number | null;
  pnl: number | null;
  pnl_percentage: number | null;

  // Whether live price was successfully retrieved
  price_available: boolean;
}

export interface PortfolioSummary {
  total_invested: number;
  total_current_value: number;
  total_pnl: number;
  total_pnl_percentage: number;
}

interface LivePortfolioResponse {
  success: boolean;
  holdings: PortfolioItem[];
  summary: PortfolioSummary;
}

export default function usePortfolio() {
  const [portfolio, setPortfolio] = useState<PortfolioItem[]>([]);
  const [summary, setSummary] = useState<PortfolioSummary>({
    total_invested: 0,
    total_current_value: 0,
    total_pnl: 0,
    total_pnl_percentage: 0,
  });

  const [loading, setLoading] = useState(true);

  // =========================
  // GET LIVE PORTFOLIO
  // =========================
  const fetchPortfolio = useCallback(async () => {
    try {
      setLoading(true);

      const token = localStorage.getItem("access_token");

      if (!token) {
        console.warn("No access token found.");

        setPortfolio([]);

        setSummary({
          total_invested: 0,
          total_current_value: 0,
          total_pnl: 0,
          total_pnl_percentage: 0,
        });

        return;
      }

      const response = await api.get<LivePortfolioResponse>(
        "/portfolio/live"
      );

      setPortfolio(response.data.holdings);

      setSummary(response.data.summary);
    } catch (error: any) {
      console.error(
        "Failed to fetch live portfolio:",
        error?.response?.data || error
      );

      setPortfolio([]);

      setSummary({
        total_invested: 0,
        total_current_value: 0,
        total_pnl: 0,
        total_pnl_percentage: 0,
      });
    } finally {
      setLoading(false);
    }
  }, []);

  // =========================
  // ADD TO PORTFOLIO
  // =========================
  const addPortfolioItem = async (
    symbol: string,
    quantity: number,
    averagePrice: number
  ) => {
    const response = await api.post<PortfolioItem>(
      "/portfolio",
      {
        symbol: symbol.toUpperCase(),
        quantity,
        average_price: averagePrice,
      }
    );

    // Refresh portfolio after successful addition
    await fetchPortfolio();

    return response.data;
  };

  // =========================
  // DELETE FROM PORTFOLIO
  // =========================
  const deletePortfolioItem = async (id: string) => {
    try {
      await api.delete(`/portfolio/${id}`);

      // Refresh live prices + P&L
      await fetchPortfolio();
    } catch (error: any) {
      console.error(
        "Failed to delete portfolio item:",
        error?.response?.data || error
      );

      throw error;
    }
  };

  // =========================
  // LOAD PORTFOLIO
  // =========================
  useEffect(() => {
    fetchPortfolio();
  }, [fetchPortfolio]);

  // =========================
  // AUTO REFRESH LIVE PRICES
  // =========================
  useEffect(() => {
    const interval = setInterval(() => {
      fetchPortfolio();
    }, 60000); // 60 seconds

    return () => {
      clearInterval(interval);
    };
  }, [fetchPortfolio]);

  return {
    portfolio,
    summary,
    loading,

    addPortfolioItem,
    deletePortfolioItem,

    refreshPortfolio: fetchPortfolio,
  };
}