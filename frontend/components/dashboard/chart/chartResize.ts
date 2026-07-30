import { IChartApi } from "lightweight-charts";

export function setupResize(
  chart: IChartApi,
  container: HTMLDivElement
) {
  const resize = () => {
    chart.applyOptions({
      width: container.clientWidth,
    });
  };

  window.addEventListener("resize", resize);

  return () => window.removeEventListener("resize", resize);
}