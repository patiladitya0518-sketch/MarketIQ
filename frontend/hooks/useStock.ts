"use client";

import { useCallback, useEffect, useState } from "react";
import api from "@/lib/api";

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

export interface MarketStructure {
  structure: string;
  trend: string;
  signal: string;
  confidence: number;

  swing_counts: {
    higher_high: number;
    higher_low: number;
    lower_high: number;
    lower_low: number;
  };

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
  recommendation: string;
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
}

// ============================================================
// TECHNICAL INDICATORS
// ============================================================

export interface Indicators {
  RSI: number;
  EMA20: number;
  EMA50: number;
  MACD: number;
  MACD_SIGNAL: number;
}

// ============================================================
// COMPLETE STOCK RESPONSE
// ============================================================

export interface StockResponse {
  success: boolean;

  symbol: string;

  price: number;

  indicators: Indicators;

  recommendation: Recommendation;

  pattern: Pattern;

  market_structure: MarketStructure;

  support_resistance: SupportResistance;
}

// ============================================================
// HOOK
// ============================================================

export default function useStock(symbol: string) {
  const [data, setData] =
    useState<StockResponse | null>(null);

  const [loading, setLoading] =
    useState(true);

  const [refreshing, setRefreshing] =
    useState(false);

  const [lastUpdated, setLastUpdated] =
    useState<Date | null>(null);

  const [error, setError] =
    useState<string | null>(null);

  // ============================================================
  // FETCH STOCK DATA
  // ============================================================

  const fetchStock = useCallback(
    async (backgroundRefresh = false) => {
      if (!symbol?.trim()) {
        return;
      }

      try {
        // ------------------------------------------------------
        // Loading states
        // ------------------------------------------------------

        if (backgroundRefresh) {
          setRefreshing(true);
        } else {
          setLoading(true);
        }

        setError(null);

        // ------------------------------------------------------
        // API REQUEST
        // ------------------------------------------------------

        const cleanSymbol =
          symbol.trim().toUpperCase();

        const res = await api.get(
          `/stock/${cleanSymbol}`
        );

        // ------------------------------------------------------
        // SUCCESS
        // ------------------------------------------------------

        if (res.data?.success) {
          setData(res.data);

          setLastUpdated(
            new Date()
          );

          return;
        }

        // ------------------------------------------------------
        // API FAILURE
        // ------------------------------------------------------

        const message =
          res.data?.message ||
          "Unable to analyse this stock.";

        console.warn(
          "Stock API error:",
          message
        );

        setError(message);

        setData(null);

      } catch (error: any) {

        // ------------------------------------------------------
        // ERROR HANDLING
        // ------------------------------------------------------

        console.error(
          "Failed to fetch stock:",
          error?.response?.data ||
            error?.message ||
            error
        );

        const message =
          error?.response?.data?.message ||
          error?.response?.data?.detail ||
          error?.message ||
          "Failed to fetch stock data.";

        setError(
          typeof message === "string"
            ? message
            : "Failed to fetch stock data."
        );

      } finally {

        setLoading(false);

        setRefreshing(false);
      }
    },
    [symbol]
  );

  // ============================================================
  // INITIAL LOAD
  // ============================================================

  useEffect(() => {
    if (!symbol?.trim()) {
      return;
    }

    // Reset old stock while loading new stock
    setLoading(true);
    setError(null);

    fetchStock(false);

    // ============================================================
    // AUTOMATIC REFRESH
    // ============================================================

    const interval = setInterval(() => {
      fetchStock(true);
    }, 60000);

    // ============================================================
    // CLEANUP
    // ============================================================

    return () => {
      clearInterval(interval);
    };

  }, [symbol, fetchStock]);

  // ============================================================
  // MANUAL REFRESH
  // ============================================================

  const refreshStock = useCallback(() => {
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