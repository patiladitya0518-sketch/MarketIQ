"use client";

import { useEffect, useRef, useState } from "react";
import {
  createChart,
  ColorType,
  CandlestickSeries,
  LineSeries,
  CrosshairMode,
} from "lightweight-charts";

import useChart from "@/hooks/useChart";
import VolumeChart from "./VolumeChart";
import RSIChart from "./RSIChart";
import MACDChart from "./MACDChart";

interface Props {
  symbol: string;
}

const periods = ["1D", "5D", "1M", "3M", "6M", "1Y"];

// ✅ FIXED TIME FORMATTER
const formatChartTime = (time: string) => {
  if (time.includes(" ")) {
    return Math.floor(
      new Date(time.replace(" ", "T")).getTime() / 1000
    ) as any;
  }

  if (time.includes("T")) {
    return time.split("T")[0] as any;
  }

  return time as any;
};

export default function ChartCard({ symbol }: Props) {
  const chartContainerRef = useRef<HTMLDivElement>(null);

  const [period, setPeriod] = useState("6M");

  const { data, levels, loading } = useChart(symbol, period);

  useEffect(() => {
    if (!chartContainerRef.current) return;
    if (loading) return;
    if (data.length === 0) return;

    chartContainerRef.current.innerHTML = "";

    const chart = createChart(chartContainerRef.current, {
      width: chartContainerRef.current.clientWidth,
      height: 520,

      layout: {
        background: {
          type: ColorType.Solid,
          color: "#0f172a",
        },
        textColor: "#CBD5E1",
      },

      grid: {
        vertLines: {
          color: "#1E293B",
        },
        horzLines: {
          color: "#1E293B",
        },
      },

      crosshair: {
        mode: CrosshairMode.Normal,
      },

      rightPriceScale: {
        borderColor: "#334155",
      },

      timeScale: {
        borderColor: "#334155",
      },
    });

    // ==========================
    // Candlestick
    // ==========================

    const candleSeries = chart.addSeries(CandlestickSeries);

    candleSeries.setData(
      data.map((item) => ({
        time: formatChartTime(item.time),
        open: item.open,
        high: item.high,
        low: item.low,
        close: item.close,
      }))
    );

    // ==========================
    // EMA20
    // ==========================

    const ema20Series = chart.addSeries(LineSeries, {
      color: "#3B82F6",
      lineWidth: 2,
      title: "EMA20",
    });

    ema20Series.setData(
      data.map((item) => ({
        time: formatChartTime(item.time),
        value: item.ema20,
      }))
    );

    // ==========================
    // EMA50
    // ==========================

    const ema50Series = chart.addSeries(LineSeries, {
      color: "#F59E0B",
      lineWidth: 2,
      title: "EMA50",
    });

    ema50Series.setData(
      data.map((item) => ({
        time: formatChartTime(item.time),
        value: item.ema50,
      }))
    );

    // ==========================
    // Support Lines
    // ==========================

    levels.support.forEach((price) => {
      candleSeries.createPriceLine({
        price,
        color: "#22c55e",
        lineWidth: 2,
        lineStyle: 2,
        axisLabelVisible: true,
        title: "Support",
      });
    });

    // ==========================
    // Resistance Lines
    // ==========================

    levels.resistance.forEach((price) => {
      candleSeries.createPriceLine({
        price,
        color: "#ef4444",
        lineWidth: 2,
        lineStyle: 2,
        axisLabelVisible: true,
        title: "Resistance",
      });
    });

    chart.timeScale().fitContent();

    const resize = () => {
      if (!chartContainerRef.current) return;

      chart.applyOptions({
        width: chartContainerRef.current.clientWidth,
      });
    };

    window.addEventListener("resize", resize);

    return () => {
      window.removeEventListener("resize", resize);
      chart.remove();
    };
  }, [data, levels, loading]);

  return (
    <div className="space-y-6">
      <div className="rounded-2xl border border-slate-800 bg-slate-900 shadow-xl">
        <div className="flex flex-col gap-4 border-b border-slate-800 p-5 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <h2 className="text-2xl font-bold text-white">{symbol}</h2>

            <p className="text-sm text-slate-400">
              NSE Candlestick Chart
            </p>
          </div>

          <div className="flex flex-wrap gap-2">
            {periods.map((p) => (
              <button
                key={p}
                onClick={() => setPeriod(p)}
                className={`rounded-lg px-4 py-2 text-sm font-semibold transition ${
                  period === p
                    ? "bg-blue-600 text-white"
                    : "bg-slate-800 text-slate-300 hover:bg-slate-700"
                }`}
              >
                {p}
              </button>
            ))}
          </div>
        </div>

        <div className="flex flex-wrap gap-3 border-b border-slate-800 px-5 py-4">
          <span className="rounded-full bg-blue-500/20 px-3 py-1 text-xs font-semibold text-blue-400">
            EMA20
          </span>

          <span className="rounded-full bg-amber-500/20 px-3 py-1 text-xs font-semibold text-amber-400">
            EMA50
          </span>

          <span className="rounded-full bg-green-500/20 px-3 py-1 text-xs font-semibold text-green-400">
            Candlestick
          </span>
        </div>

        {loading ? (
          <div className="flex h-[520px] items-center justify-center">
            <div className="text-center">
              <div className="mx-auto mb-4 h-10 w-10 animate-spin rounded-full border-4 border-blue-600 border-t-transparent"></div>

              <p className="text-slate-400">
                Loading Market Data...
              </p>
            </div>
          </div>
        ) : (
          <div
            ref={chartContainerRef}
            className="w-full"
          />
        )}
      </div>

      {!loading && data.length > 0 && (
        <div className="space-y-6">
          <VolumeChart data={data} />
          <RSIChart data={data} />
          <MACDChart data={data} />
        </div>
      )}
    </div>
  );
}