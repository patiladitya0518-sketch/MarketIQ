"use client";

import { useCallback, useEffect, useState } from "react";
import api from "@/lib/api";

export interface PortfolioItem {
  id: string;
  symbol: string;
  quantity: number;
  average_price: number;

  current_price: number | null;
  invested_value: number;
  current_value: number | null;
  pnl: number | null;
  pnl_percentage: number | null;
  allocation_percentage: number;
  price_available: boolean;
}

export interface PortfolioPerformer {
  symbol: string;
  pnl: number;
  pnl_percentage: number;
}

export interface PortfolioSummary {
  total_invested: number;
  total_current_value: number;
  total_pnl: number;
  total_pnl_percentage: number;

  total_holdings: number;
  profitable_holdings: number;
  losing_holdings: number;

  best_performer: PortfolioPerformer | null;
  worst_performer: PortfolioPerformer | null;

  portfolio_health: string;
  risk_level: string;
}

const emptySummary: PortfolioSummary = {
  total_invested: 0,
  total_current_value: 0,
  total_pnl: 0,
  total_pnl_percentage: 0,

  total_holdings: 0,
  profitable_holdings: 0,
  losing_holdings: 0,

  best_performer: null,
  worst_performer: null,

  portfolio_health: "No Holdings",
  risk_level: "No Data",
};

export default function usePortfolio() {
  const [portfolio, setPortfolio] = useState<PortfolioItem[]>([]);
  const [summary, setSummary] =
    useState<PortfolioSummary>(emptySummary);

  // Initial page loading
  const [loading, setLoading] = useState(true);

  // Background refresh indicator
  const [refreshing, setRefreshing] = useState(false);

  // Last successful update time
  const [lastUpdated, setLastUpdated] =
    useState<Date | null>(null);

  // ============================================================
  // GET LIVE PORTFOLIO
  // ============================================================

  const fetchPortfolio = useCallback(
    async (backgroundRefresh = false) => {
      try {
        if (backgroundRefresh) {
          setRefreshing(true);
        } else {
          setLoading(true);
        }

        const token =
          localStorage.getItem("access_token");

        if (!token) {
          console.warn(
            "No access token found."
          );

          setPortfolio([]);
          setSummary(emptySummary);

          return;
        }

        const response =
          await api.get("/portfolio/live");

        console.log(
          "Portfolio API response:",
          response.data
        );

        if (
          response.data &&
          response.data.success
        ) {
          setPortfolio(
            response.data.holdings || []
          );

          setSummary({
            ...emptySummary,
            ...(response.data.summary || {}),
          });

          // Record successful update time
          setLastUpdated(new Date());
        } else {
          console.warn(
            "Portfolio API returned unsuccessful response:",
            response.data
          );
        }
      } catch (error: any) {
        console.error(
          "Failed to fetch portfolio:",
          error?.response?.data ||
            error?.message ||
            error
        );

        // Keep existing data if a background
        // refresh temporarily fails.
      } finally {
        setLoading(false);
        setRefreshing(false);
      }
    },
    []
  );

  // ============================================================
  // ADD TO PORTFOLIO
  // ============================================================

  const addPortfolioItem = async (
    symbol: string,
    quantity: number,
    averagePrice: number
  ) => {
    const response =
      await api.post("/portfolio", {
        symbol: symbol.toUpperCase(),
        quantity,
        average_price: averagePrice,
      });

    await fetchPortfolio();

    return response.data;
  };

  // ============================================================
  // DELETE FROM PORTFOLIO
  // ============================================================

  const deletePortfolioItem =
    async (id: string) => {
      try {
        await api.delete(
          `/portfolio/${id}`
        );

        await fetchPortfolio();
      } catch (error: any) {
        console.error(
          "Failed to delete portfolio item:",
          error?.response?.data ||
            error?.message ||
            error
        );

        throw error;
      }
    };

  // ============================================================
  // INITIAL LOAD + AUTOMATIC REFRESH
  // ============================================================

  useEffect(() => {
    // Initial request
    fetchPortfolio(false);

    // Refresh every 60 seconds
    const interval = setInterval(() => {
      fetchPortfolio(true);
    }, 60000);

    return () => {
      clearInterval(interval);
    };
  }, [fetchPortfolio]);

  return {
    portfolio,
    summary,

    loading,
    refreshing,
    lastUpdated,

    addPortfolioItem,
    deletePortfolioItem,

    refreshPortfolio: () =>
      fetchPortfolio(true),
  };
}