import {
  IChartApi,
  CandlestickSeries,
  LineSeries,
} from "lightweight-charts";

interface Candle {
  time: string;
  open: number;
  high: number;
  low: number;
  close: number;
  ema20: number;
  ema50: number;
}

export function addChartSeries(
  chart: IChartApi,
  data: Candle[]
) {
  // Candlesticks
  const candleSeries = chart.addSeries(CandlestickSeries);

  candleSeries.setData(
    data.map((item) => ({
      time: item.time,
      open: item.open,
      high: item.high,
      low: item.low,
      close: item.close,
    }))
  );

  // EMA20
  const ema20Series = chart.addSeries(LineSeries, {
    color: "#3b82f6",
    lineWidth: 2,
    title: "EMA20",
  });

  ema20Series.setData(
    data.map((item) => ({
      time: item.time,
      value: item.ema20,
    }))
  );

  // EMA50
  const ema50Series = chart.addSeries(LineSeries, {
    color: "#f59e0b",
    lineWidth: 2,
    title: "EMA50",
  });

  ema50Series.setData(
    data.map((item) => ({
      time: item.time,
      value: item.ema50,
    }))
  );

  return {
    candleSeries,
    ema20Series,
    ema50Series,
  };
}