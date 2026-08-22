"use client";

import {
  useCallback,
  useEffect,
  useRef,
  useState,
} from "react";

import api from "@/lib/api";

// ============================================================
// RECOMMENDATION SIGNAL
// ============================================================

export type RecommendationSignal =
  | "BUY"
  | "SELL"
  | "HOLD";

// ============================================================
// CANDLESTICK PATTERN
// ============================================================

export interface Pattern {
  pattern: string;
  signal: string;
  confidence: number;
  reason: string[];
}

// ============================================================
// MARKET STRUCTURE
// ============================================================

export interface SwingCounts {
  higher_high: number;
  higher_low: number;
  lower_high: number;
  lower_low: number;
}

export interface MarketStructure {
  structure: string;
  trend: string;
  signal: string;
  confidence: number;
  swing_counts: SwingCounts;
  reasons: string[];
}

// ============================================================
// SUPPORT & RESISTANCE
// ============================================================

export interface SupportResistance {
  support: number[];
  resistance: number[];
}

// ============================================================
// SMART MONEY CONCEPTS
// ============================================================

export interface SMC {
  signal?: string;
  confidence?: number;

  trend?: string;
  market_bias?: string;

  structure?: string;

  bullish?: boolean;
  bearish?: boolean;

  order_blocks?: unknown[];
  fair_value_gaps?: unknown[];

  liquidity?: unknown[];
  liquidity_zones?: unknown[];

  bos?: unknown;
  choch?: unknown;

  reasons?: string[];

  [key: string]: unknown;
}

// ============================================================
// RECOMMENDATION ANALYSIS
// ============================================================

export interface PatternAnalysis {
  pattern: string;
  signal: string;
  confidence: number;
}

export interface MarketStructureAnalysis {
  structure: string;
  trend: string;
  signal: string;
  confidence: number;
}

export interface SupportResistanceAnalysis {
  nearest_support: number | null;
  nearest_resistance: number | null;
}

// ============================================================
// RECOMMENDATION
// ============================================================

export interface Recommendation {
  recommendation: RecommendationSignal;

  confidence: number;

  score: number;

  reasons: string[];

  pattern_analysis: PatternAnalysis | null;

  market_structure_analysis:
    | MarketStructureAnalysis
    | null;

  support_resistance_analysis:
    | SupportResistanceAnalysis
    | null;

  [key: string]: unknown;
}

// ============================================================
// TECHNICAL INDICATORS
// ============================================================

export interface Indicators {
  Close?: number;

  RSI: number;
  EMA20: number;
  EMA50: number;

  MACD: number;
  MACD_SIGNAL: number;

  MACD_BULLISH_CROSSOVER?: boolean;
  MACD_BEARISH_CROSSOVER?: boolean;

  [key: string]: number | boolean | undefined;
}

// ============================================================
// COMPLETE STOCK RESPONSE
// ============================================================

export interface StockResponse {
  success: boolean;

  query?: string;

  symbol: string;

  yahoo_symbol?: string;

  exchange?: string;

  price: number;

  indicators: Indicators;

  recommendation: Recommendation;

  pattern: Pattern;

  market_structure: MarketStructure;

  support_resistance: SupportResistance;

  smc?: SMC;

  message?: string;
}

// ============================================================
// HOOK
// ============================================================

export default function useStock(symbol: string) {
  const [data, setData] =
    useState<StockResponse | null>(null);

  const [loading, setLoading] =
    useState(false);

  const [refreshing, setRefreshing] =
    useState(false);

  const [lastUpdated, setLastUpdated] =
    useState<Date | null>(null);

  const [error, setError] =
    useState<string | null>(null);

  // ============================================================
  // REQUEST ID
  // Prevent old requests from overwriting newer requests
  // ============================================================

  const requestIdRef = useRef(0);

  // ============================================================
  // FETCH STOCK
  // ============================================================

  const fetchStock = useCallback(
    async (backgroundRefresh = false) => {
      const cleanSymbol =
        symbol?.trim().toUpperCase();

      if (!cleanSymbol) {
        setData(null);
        setError(null);
        setLoading(false);
        setRefreshing(false);

        return;
      }

      const requestId =
        ++requestIdRef.current;

      try {
        // --------------------------------------------------------
        // LOADING STATE
        // --------------------------------------------------------

        if (backgroundRefresh) {
          setRefreshing(true);
        } else {
          setLoading(true);
        }

        setError(null);

        // --------------------------------------------------------
        // API REQUEST
        // --------------------------------------------------------

        const response = await api.get(
          `/stock/${encodeURIComponent(
            cleanSymbol
          )}`
        );

        const result =
          response?.data;

        // --------------------------------------------------------
        // IGNORE OLD REQUEST
        // --------------------------------------------------------

        if (
          requestId !==
          requestIdRef.current
        ) {
          return;
        }

        // --------------------------------------------------------
        // API SUCCESS
        // --------------------------------------------------------

        if (
          result?.success === true
        ) {
          setData(
            result as StockResponse
          );

          setLastUpdated(
            new Date()
          );

          setError(null);

          return;
        }

        // --------------------------------------------------------
        // API FAILURE
        // --------------------------------------------------------

        const message =
          result?.message ||
          `Unable to analyse ${cleanSymbol}.`;

        setError(
          typeof message === "string"
            ? message
            : `Unable to analyse ${cleanSymbol}.`
        );

        // Don't immediately destroy existing data
        // during a background refresh.
        if (!backgroundRefresh) {
          setData(null);
        }

      } catch (error: any) {
        // --------------------------------------------------------
        // IGNORE OLD REQUEST
        // --------------------------------------------------------

        if (
          requestId !==
          requestIdRef.current
        ) {
          return;
        }

        console.error(
          "Failed to fetch stock:",
          error?.response?.data ||
            error?.message ||
            error
        );

        // --------------------------------------------------------
        // DEFAULT ERROR
        // --------------------------------------------------------

        let message =
          "Failed to fetch stock data.";

        // --------------------------------------------------------
        // BACKEND ERROR MESSAGE
        // --------------------------------------------------------

        if (
          typeof error?.response?.data
            ?.message === "string"
        ) {
          message =
            error.response.data.message;
        }

        // --------------------------------------------------------
        // FASTAPI DETAIL
        // --------------------------------------------------------

        else if (
          typeof error?.response?.data
            ?.detail === "string"
        ) {
          message =
            error.response.data.detail;
        }

        // --------------------------------------------------------
        // AXIOS ERROR MESSAGE
        // --------------------------------------------------------

        else if (
          typeof error?.message ===
          "string"
        ) {
          message =
            error.message;
        }

        // --------------------------------------------------------
        // NETWORK ERROR
        // --------------------------------------------------------

        if (
          error?.message ===
          "Network Error"
        ) {
          message =
            "Unable to connect to MarketIQ backend. Make sure the FastAPI server is running.";
        }

        // --------------------------------------------------------
        // 400 ERROR
        // --------------------------------------------------------

        if (
          error?.response?.status ===
          400
        ) {
          message =
            "Invalid stock symbol. Please enter a valid Indian stock.";
        }

        // --------------------------------------------------------
        // 404 ERROR
        // --------------------------------------------------------

        if (
          error?.response?.status ===
          404
        ) {
          message =
            `Stock '${cleanSymbol}' was not found.`;
        }

        // --------------------------------------------------------
        // 429 ERROR
        // --------------------------------------------------------

        if (
          error?.response?.status ===
          429
        ) {
          message =
            "Market data provider rate limit reached. Please try again shortly.";
        }

        // --------------------------------------------------------
        // 500+ ERROR
        // --------------------------------------------------------

        if (
          error?.response?.status >=
          500
        ) {
          message =
            "MarketIQ backend encountered an error while analysing this stock.";
        }

        setError(
          typeof message === "string"
            ? message
            : "Failed to fetch stock data."
        );

        // Keep previous data during
        // background refresh.
        if (!backgroundRefresh) {
          setData(null);
        }

      } finally {
        // --------------------------------------------------------
        // ONLY UPDATE STATE FOR CURRENT REQUEST
        // --------------------------------------------------------

        if (
          requestId ===
          requestIdRef.current
        ) {
          setLoading(false);
          setRefreshing(false);
        }
      }
    },
    [symbol]
  );

  // ============================================================
  // LOAD STOCK WHEN SYMBOL CHANGES
  // ============================================================

  useEffect(() => {
    const cleanSymbol =
      symbol?.trim();

    // ----------------------------------------------------------
    // EMPTY SYMBOL
    // ----------------------------------------------------------

    if (!cleanSymbol) {
      requestIdRef.current++;

      setData(null);
      setError(null);
      setLoading(false);
      setRefreshing(false);
      setLastUpdated(null);

      return;
    }

    // ----------------------------------------------------------
    // RESET
    // ----------------------------------------------------------

    setData(null);
    setError(null);
    setLastUpdated(null);
    setLoading(true);

    // ----------------------------------------------------------
    // INITIAL REQUEST
    // ----------------------------------------------------------

    fetchStock(false);

    // ----------------------------------------------------------
    // AUTO REFRESH
    // Every 60 seconds
    // ----------------------------------------------------------

    const interval =
      setInterval(() => {
        fetchStock(true);
      }, 60 * 1000);

    // ----------------------------------------------------------
    // CLEANUP
    // ----------------------------------------------------------

    return () => {
      clearInterval(interval);

      requestIdRef.current++;
    };

  }, [
    symbol,
    fetchStock,
  ]);

  // ============================================================
  // MANUAL REFRESH
  // ============================================================

  const refreshStock =
    useCallback(() => {
      return fetchStock(true);
    }, [fetchStock]);

  // ============================================================
  // RETURN
  // ============================================================

  return {
    data,

    loading,

    refreshing,

    error,

    lastUpdated,

    refreshStock,
  };
}