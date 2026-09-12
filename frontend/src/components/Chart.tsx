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

// Validated categorical palette (dataviz skill reference), fixed order — never cycled.
const CATEGORICAL = [
  "#2a78d6",
  "#eb6834",
  "#1baf7a",
  "#eda100",
  "#e87ba4",
  "#008300",
  "#4a3aa7",
  "#e34948",
];
const SERIES_1 = CATEGORICAL[0];
const INK_SECONDARY = "#52514e";
const INK_MUTED = "#898781";
const GRIDLINE = "#e1e0d9";
const SURFACE = "#fcfcfb";

const MAX_PIE_SLICES = 7;

function foldPieData(rows: Record<string, unknown>[], xField: string, yField: string) {
  if (rows.length <= MAX_PIE_SLICES + 1) return rows;
  const sorted = [...rows].sort((a, b) => Number(b[yField]) - Number(a[yField]));
  const top = sorted.slice(0, MAX_PIE_SLICES);
  const rest = sorted.slice(MAX_PIE_SLICES);
  const otherValue = rest.reduce((sum, r) => sum + Number(r[yField] ?? 0), 0);
  return [...top, { [xField]: "Other", [yField]: otherValue }];
}

function renderChart(chart: ChartSpec) {
  const { chart_type, x_field, y_field, rows } = chart;

  if (chart_type === "pie") {
    const data = foldPieData(rows, x_field, y_field);
    return (
      <PieChart>
        <Pie data={data} dataKey={y_field} nameKey={x_field} outerRadius="80%" strokeWidth={2} stroke={SURFACE}>
          {data.map((_, i) => (
            <Cell key={i} fill={CATEGORICAL[i % CATEGORICAL.length]} />
          ))}
        </Pie>
        <Legend verticalAlign="bottom" iconType="circle" wrapperStyle={{ fontSize: 12, color: INK_SECONDARY }} />
        <Tooltip contentStyle={{ fontSize: 12, borderRadius: 8, borderColor: GRIDLINE }} />
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
        <Tooltip contentStyle={{ fontSize: 12, borderRadius: 8, borderColor: GRIDLINE }} />
        <Line
          type="monotone"
          dataKey={y_field}
          stroke={SERIES_1}
          strokeWidth={2}
          dot={{ r: 4, fill: SERIES_1, stroke: SURFACE, strokeWidth: 2 }}
          activeDot={{ r: 5 }}
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
      <Tooltip
        contentStyle={{ fontSize: 12, borderRadius: 8, borderColor: GRIDLINE }}
        cursor={{ fill: "rgba(0,0,0,0.03)" }}
      />
      <Bar dataKey={y_field} fill={SERIES_1} radius={[4, 4, 0, 0]} maxBarSize={24} />
    </BarChart>
  );
}

export function Chart({ chart }: { chart: ChartSpec }) {
  const [showTable, setShowTable] = useState(false);

  return (
    <div>
      <h3 className="text-sm font-semibold text-slate-800">{chart.title}</h3>
      <div className="mt-2 h-72 w-full">
        <ResponsiveContainer width="100%" height="100%">
          {renderChart(chart)}
        </ResponsiveContainer>
      </div>
      <button
        onClick={() => setShowTable((v) => !v)}
        className="mt-2 text-xs font-medium text-slate-500 underline decoration-slate-300 underline-offset-2 hover:text-slate-700"
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
