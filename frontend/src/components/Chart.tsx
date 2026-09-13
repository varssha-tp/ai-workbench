import { useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { ChartSpec } from "../types";
import { DataTable } from "./DataTable";

// Validated dark-mode categorical palette (dataviz skill reference, re-run
// against this app's near-black surface), fixed order — never cycled.
const CATEGORICAL = [
  "#3987e5",
  "#d95926",
  "#199e70",
  "#c98500",
  "#d55181",
  "#008300",
  "#9085e9",
  "#e66767",
];
// Single-series charts use the brand purple directly (matches CATEGORICAL[6],
// the validated dark "violet" slot) rather than the categorical order's first
// slot — there's only one series, so the fixed-order rule (which protects
// adjacent-pair distinctness) doesn't apply.
const SERIES_1 = "#9085e9";
const INK_SECONDARY = "#b8b8c2";
const INK_MUTED = "#7a7a86";
const GRIDLINE = "#2a2a35";
const SURFACE = "#17171f";
const TOOLTIP_BG = "#1f1f2a";

const MAX_PIE_SLICES = 7;

function foldPieData(rows: Record<string, unknown>[], xField: string, yField: string) {
  if (rows.length <= MAX_PIE_SLICES + 1) return rows;
  const sorted = [...rows].sort((a, b) => Number(b[yField]) - Number(a[yField]));
  const top = sorted.slice(0, MAX_PIE_SLICES);
  const rest = sorted.slice(MAX_PIE_SLICES);
  const otherValue = rest.reduce((sum, r) => sum + Number(r[yField] ?? 0), 0);
  return [...top, { [xField]: "Other", [yField]: otherValue }];
}

const tooltipStyle = {
  fontSize: 12,
  borderRadius: 8,
  borderColor: GRIDLINE,
  backgroundColor: TOOLTIP_BG,
  color: INK_SECONDARY,
};

function renderChart(chart: ChartSpec) {
  const { chart_type, x_field, y_field, rows } = chart;

  if (chart_type === "pie") {
    const data = foldPieData(rows, x_field, y_field);
    return (
      <PieChart>
        <Pie
          data={data}
          dataKey={y_field}
          nameKey={x_field}
          outerRadius="80%"
          strokeWidth={2}
          stroke={SURFACE}
          isAnimationActive={false}
        >
          {data.map((_, i) => (
            <Cell key={i} fill={CATEGORICAL[i % CATEGORICAL.length]} />
          ))}
        </Pie>
        <Legend verticalAlign="bottom" iconType="circle" wrapperStyle={{ fontSize: 12, color: INK_SECONDARY }} />
        <Tooltip contentStyle={tooltipStyle} />
      </PieChart>
    );
  }

  if (chart_type === "line") {
    return (
      <LineChart data={rows}>
        <CartesianGrid stroke={GRIDLINE} vertical={false} />
        <XAxis
          dataKey={x_field}
          tick={{ fontSize: 12, fill: INK_MUTED }}
          axisLine={{ stroke: GRIDLINE }}
          tickLine={false}
        />
        <YAxis tick={{ fontSize: 12, fill: INK_MUTED }} axisLine={false} tickLine={false} />
        <Tooltip contentStyle={tooltipStyle} />
        <Line
          type="monotone"
          dataKey={y_field}
          stroke={SERIES_1}
          strokeWidth={2}
          dot={{ r: 4, fill: SERIES_1, stroke: SURFACE, strokeWidth: 2 }}
          activeDot={{ r: 5 }}
          isAnimationActive={false}
        />
      </LineChart>
    );
  }

  return (
    <BarChart data={rows}>
      <CartesianGrid stroke={GRIDLINE} vertical={false} />
      <XAxis
        dataKey={x_field}
        tick={{ fontSize: 12, fill: INK_MUTED }}
        axisLine={{ stroke: GRIDLINE }}
        tickLine={false}
      />
      <YAxis tick={{ fontSize: 12, fill: INK_MUTED }} axisLine={false} tickLine={false} />
      <Tooltip contentStyle={tooltipStyle} cursor={{ fill: "rgba(255,255,255,0.05)" }} />
      <Bar dataKey={y_field} fill={SERIES_1} radius={[4, 4, 0, 0]} maxBarSize={24} isAnimationActive={false} />
    </BarChart>
  );
}

export function Chart({ chart }: { chart: ChartSpec }) {
  const [showTable, setShowTable] = useState(false);

  return (
    <div>
      <h3 className="text-sm font-semibold text-ink">{chart.title}</h3>
      <div className="mt-2 h-72 w-full">
        <ResponsiveContainer width="100%" height="100%">
          {renderChart(chart)}
        </ResponsiveContainer>
      </div>
      <button
        onClick={() => setShowTable((v) => !v)}
        className="mt-2 text-xs font-medium text-ink-muted underline decoration-line underline-offset-2 hover:text-ink-secondary"
      >
        {showTable ? "Hide data table" : "View as table"}
      </button>
      {showTable && (
        <div className="mt-2">
          <DataTable
            table={{ title: chart.title, columns: [chart.x_field, chart.y_field], rows: chart.rows }}
          />
        </div>
      )}
    </div>
  );
}
