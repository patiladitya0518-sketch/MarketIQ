"use client";

import { useEffect, useRef } from "react";
import {
  createChart,
  ColorType,
  LineSeries,
  HistogramSeries,
} from "lightweight-charts";

interface Candle {
  time: string;
  macd: number;
  macdSignal: number;
}

interface Props {
  data: Candle[];
}

export default function MACDChart({ data }: Props) {
  const chartRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!chartRef.current || data.length === 0) return;

    chartRef.current.innerHTML = "";

    const chart = createChart(chartRef.current, {
      width: chartRef.current.clientWidth,
      height: 240,

      layout: {
        background: {
          type: ColorType.Solid,
          color: "#0f172a",
        },
        textColor: "#94a3b8",
      },

      grid: {
        vertLines: {
          color: "#1e293b",
        },
        horzLines: {
          color: "#1e293b",
        },
      },

      rightPriceScale: {
        borderColor: "#334155",
      },

      timeScale: {
        borderColor: "#334155",
      },
    });

    const histogram = chart.addSeries(HistogramSeries);

    histogram.setData(
  data.map((item) => ({
    time: item.time.includes(" ")
      ? (Math.floor(new Date(item.time).getTime() / 1000) as any)
      : (item.time as any),

    value: item.macd - item.macdSignal,

    color:
      item.macd >= item.macdSignal
        ? "#22c55e"
        : "#ef4444",
  }))
);
    const macdSeries = chart.addSeries(LineSeries, {
      color: "#3b82f6",
      lineWidth: 2,
      title: "MACD",
    });

    macdSeries.setData(
  data.map((item) => ({
    time: item.time.includes(" ")
      ? (Math.floor(new Date(item.time.replace(" ", "T")).getTime() / 1000) as any)
      : (item.time as any),

    value: item.macd,
  }))
);

    const signalSeries = chart.addSeries(LineSeries, {
      color: "#f59e0b",
      lineWidth: 2,
      title: "Signal",
    });

    signalSeries.setData(
  data.map((item) => ({
    time: item.time.includes(" ")
      ? (Math.floor(new Date(item.time.replace(" ", "T")).getTime() / 1000) as any)
      : (item.time as any),

    value: item.macdSignal,
  }))
);

    chart.timeScale().fitContent();

    const resize = () => {
      if (!chartRef.current) return;

      chart.applyOptions({
        width: chartRef.current.clientWidth,
      });
    };

    window.addEventListener("resize", resize);

    return () => {
      window.removeEventListener("resize", resize);
      chart.remove();
    };
  }, [data]);

  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900 p-4">
      <h2 className="mb-3 text-lg font-semibold text-white">
        MACD
      </h2>

      <div ref={chartRef} />
    </div>
  );
}