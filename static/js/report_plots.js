(function () {
  const reportEl = document.getElementById("report-data");
  const inputsEl = document.getElementById("model-inputs");
  if (!reportEl || !inputsEl || typeof Plotly === "undefined") {
    return;
  }

  const result = JSON.parse(reportEl.textContent);
  const inputs = JSON.parse(inputsEl.textContent);
  if (result.safety_override || result.probability == null) {
    return;
  }

  const PLOT_IDS = [
    "probability-gauge",
    "heartburn-curve",
    "regurgitation-curve",
    "bivariate-surface",
  ];

  const probability = result.probability;
  const plotConfig = { displayModeBar: false, responsive: true };

  function plotPrintWidth() {
    const report = document.querySelector(".report");
    const width = report ? report.clientWidth : 680;
    // ~178mm printable column at 96dpi
    return Math.min(Math.max(width, 520), 680);
  }

  function plotPrintHeight(id) {
    const el = document.getElementById(id);
    if (el && el.classList.contains("plot-box-tall")) {
      return 260;
    }
    return 220;
  }

  function resizeAllPlots(forPrint) {
    const width = plotPrintWidth();
    PLOT_IDS.forEach((id) => {
      const el = document.getElementById(id);
      if (!el || !el.querySelector(".main-svg")) {
        return;
      }
      const height = plotPrintHeight(id);
      Plotly.relayout(el, {
        width: width,
        height: height,
        autosize: !forPrint,
      });
    });
  }

  window.prepareReportPrint = function prepareReportPrint() {
    resizeAllPlots(true);
    window.setTimeout(() => window.print(), 150);
  };

  window.addEventListener("beforeprint", () => resizeAllPlots(true));
  window.addEventListener("afterprint", () => resizeAllPlots(false));

  Plotly.newPlot(
    "probability-gauge",
    [
      {
        type: "indicator",
        mode: "gauge+number",
        value: probability,
        number: { valueformat: ".2f", font: { size: 28 } },
        title: { text: "Illustrative probability", font: { size: 14 } },
        gauge: {
          axis: { range: [0, 1], tickwidth: 1 },
          bar: { color: "#0f6a5a" },
          steps: [
            { range: [0, 0.2], color: "#d9efe6" },
            { range: [0.2, 0.8], color: "#f3efd7" },
            { range: [0.8, 1], color: "#f2d6d0" },
          ],
          threshold: {
            line: { color: "#1c2a24", width: 3 },
            thickness: 0.8,
            value: probability,
          },
        },
      },
    ],
    {
      margin: { t: 52, r: 36, l: 36, b: 56 },
      paper_bgcolor: "rgba(0,0,0,0)",
      font: { color: "#1c2a24", size: 11 },
      annotations: [
        {
          text: "Low · Indeterminate · High (demonstration zones)",
          showarrow: false,
          x: 0.5,
          y: -0.08,
          xref: "paper",
          yref: "paper",
          font: { size: 10, color: "#5a6b63" },
        },
      ],
    },
    plotConfig
  );

  function drawCurve(elementId, points, markerX, title, xTitle) {
    const xs = points.map((p) => p.x);
    const ys = points.map((p) => p.y);
    const markerY = points.find((p) => p.x === markerX)?.y ?? probability;

    Plotly.newPlot(
      elementId,
      [
        {
          x: xs,
          y: ys,
          type: "scatter",
          mode: "lines+markers",
          name: "Illustrative curve",
          line: { color: "#0f6a5a", width: 2.5 },
          marker: { size: 6 },
        },
        {
          x: [markerX],
          y: [markerY],
          type: "scatter",
          mode: "markers",
          name: "Entered value",
          marker: { size: 12, color: "#7a4b00", symbol: "diamond" },
        },
      ],
      {
        title: { text: title, font: { size: 12 }, x: 0.5, xanchor: "center" },
        xaxis: { title: { text: xTitle, font: { size: 11 } }, dtick: 1, range: [-0.2, 7.2] },
        yaxis: { title: { text: "Illustrative probability", font: { size: 11 } }, range: [0, 1] },
        margin: { t: 48, r: 28, l: 58, b: 52 },
        legend: { orientation: "h", y: -0.18, x: 0.5, xanchor: "center", font: { size: 10 } },
        shapes: [
          { type: "rect", xref: "paper", x0: 0, x1: 1, y0: 0, y1: 0.2, fillcolor: "#d9efe6", opacity: 0.35, line: { width: 0 } },
          { type: "rect", xref: "paper", x0: 0, x1: 1, y0: 0.2, y1: 0.8, fillcolor: "#f3efd7", opacity: 0.35, line: { width: 0 } },
          { type: "rect", xref: "paper", x0: 0, x1: 1, y0: 0.8, y1: 1, fillcolor: "#f2d6d0", opacity: 0.35, line: { width: 0 } },
        ],
      },
      plotConfig
    );
  }

  if (result.heartburn_curve) {
    drawCurve(
      "heartburn-curve",
      result.heartburn_curve,
      inputs.HF,
      "Heartburn days vs illustrative probability",
      "Heartburn days (0–7)"
    );
  }

  if (result.regurgitation_curve) {
    drawCurve(
      "regurgitation-curve",
      result.regurgitation_curve,
      inputs.RF,
      "Regurgitation days vs illustrative probability",
      "Regurgitation days (0–7)"
    );
  }

  if (result.bivariate_surface) {
    const surf = result.bivariate_surface;
    Plotly.newPlot(
      "bivariate-surface",
      [
        {
          x: surf.x,
          y: surf.y,
          z: surf.z,
          type: "heatmap",
          colorscale: "YlGnBu",
          colorbar: { title: { text: "P", font: { size: 10 } }, len: 0.85 },
          hovertemplate: "Days %{x}<br>Intensity %{y}<br>P %{z:.3f}<extra></extra>",
        },
      ],
      {
        title: {
          text: "Heartburn days × intensity (illustrative)",
          font: { size: 12 },
          x: 0.5,
          xanchor: "center",
        },
        xaxis: { title: { text: "Heartburn days", font: { size: 11 } }, dtick: 1 },
        yaxis: { title: { text: "Heartburn intensity", font: { size: 11 } }, dtick: 2 },
        margin: { t: 48, r: 36, l: 58, b: 48 },
      },
      plotConfig
    );
  }

  window.setTimeout(() => resizeAllPlots(false), 200);
})();
