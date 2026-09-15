"use client";

import { useEffect, useRef } from "react";
import {
  createChart,
  ColorType,
  HistogramSeries,
} from "lightweight-charts";

interface Candle {
  time: string;
  open: number;
  close: number;
  volume: number;
}

interface Props {
  data: Candle[];
}

export default function VolumeChart({ data }: Props) {
  const chartRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!chartRef.current || data.length === 0) return;

    chartRef.current.innerHTML = "";

    const chart = createChart(chartRef.current, {
      width: chartRef.current.clientWidth,
      height: 180,

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
        visible: false,
      },

      timeScale: {
        borderColor: "#334155",
      },
    });

    const volumeSeries = chart.addSeries(HistogramSeries, {
      priceFormat: {
        type: "volume",
      },
    });

    volumeSeries.setData(
  data.map((item) => ({
    time: item.time.includes(" ")
      ? (Math.floor(new Date(item.time).getTime() / 1000) as any)
      : (item.time as any),

    value: item.volume,

    color:
      item.close >= item.open
        ? "#22c55e"
        : "#ef4444",
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
    <div className="rounded-xl border border-slate-700 bg-slate-900 p-4">
      <h2 className="mb-3 text-lg font-semibold text-white">
        Volume
      </h2>

      <div ref={chartRef} />
    </div>
  );
}