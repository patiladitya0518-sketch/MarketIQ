"use client";

import {
  useCallback,
  useEffect,
  useRef,
  useState,
} from "react";

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
  const [portfolio, setPortfolio] =
    useState<PortfolioItem[]>([]);

  const [summary, setSummary] =
    useState<PortfolioSummary>(emptySummary);

  // Initial page loading
  const [loading, setLoading] =
    useState(true);

  // Background refresh indicator
  const [refreshing, setRefreshing] =
    useState(false);

  // Last successful update time
  const [lastUpdated, setLastUpdated] =
    useState<Date | null>(null);

  /*
   * Prevent multiple portfolio API requests
   * from running at the same time.
   */
  const requestInProgress =
    useRef(false);

  // ============================================================
  // GET LIVE PORTFOLIO
  // ============================================================

  const fetchPortfolio = useCallback(
    async (backgroundRefresh = false) => {
      /*
       * Do not start another request if one
       * is already running.
       */
      if (requestInProgress.current) {
        return;
      }

      requestInProgress.current = true;

      try {
        if (backgroundRefresh) {
          setRefreshing(true);
        } else {
          setLoading(true);
        }

        const token =
          localStorage.getItem(
            "access_token"
          );

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
          /*
           * Update holdings with the latest
           * live prices and P&L.
           */
          setPortfolio(
            response.data.holdings || []
          );

          /*
           * Update portfolio totals.
           */
          setSummary({
            ...emptySummary,
            ...(response.data.summary || {}),
          });

          /*
           * Store the exact time when
           * the API successfully updated.
           */
          setLastUpdated(
            new Date()
          );
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

        /*
         * IMPORTANT:
         * Keep existing portfolio data if
         * a background refresh temporarily fails.
         */
      } finally {
        setLoading(false);
        setRefreshing(false);

        requestInProgress.current =
          false;
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
        symbol:
          symbol.toUpperCase(),

        quantity,

        average_price:
          averagePrice,
      });

    /*
     * Immediately refresh after adding
     * a stock so the new holding appears.
     */
    await fetchPortfolio(false);

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

        /*
         * Immediately refresh after
         * deleting a holding.
         */
        await fetchPortfolio(false);
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
  // INITIAL LOAD + AUTOMATIC LIVE REFRESH
  // ============================================================

  useEffect(() => {
    /*
     * Initial portfolio request.
     */
    fetchPortfolio(false);

    /*
     * Refresh live P&L every 30 seconds.
     */
    const interval = setInterval(() => {
      fetchPortfolio(true);
    }, 30000);

    /*
     * Refresh immediately when the user
     * returns to the browser tab.
     */
    const handleVisibilityChange = () => {
      if (
        document.visibilityState ===
        "visible"
      ) {
        fetchPortfolio(true);
      }
    };

    /*
     * Refresh immediately when the
     * browser window gets focus.
     */
    const handleWindowFocus = () => {
      fetchPortfolio(true);
    };

    document.addEventListener(
      "visibilitychange",
      handleVisibilityChange
    );

    window.addEventListener(
      "focus",
      handleWindowFocus
    );

    /*
     * Cleanup everything when the
     * dashboard component unmounts.
     */
    return () => {
      clearInterval(interval);

      document.removeEventListener(
        "visibilitychange",
        handleVisibilityChange
      );

      window.removeEventListener(
        "focus",
        handleWindowFocus
      );
    };
  }, [fetchPortfolio]);

  // ============================================================
  // RETURN
  // ============================================================

  return {
    portfolio,
    summary,

    loading,
    refreshing,
    lastUpdated,

    addPortfolioItem,
    deletePortfolioItem,

    /*
     * Manual refresh button.
     */
    refreshPortfolio: () =>
      fetchPortfolio(true),
  };
}