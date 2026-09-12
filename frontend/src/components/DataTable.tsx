import type { TableSpec } from "../types";

function formatCell(value: unknown): string {
  if (value === null || value === undefined) return "—";
  if (typeof value === "number") {
    return Number.isInteger(value) ? String(value) : value.toFixed(2);
  }
  return String(value);
}

export function DataTable({ table }: { table: TableSpec }) {
  return (
    <div className="overflow-x-auto rounded-lg border border-slate-200">
      <table className="w-full text-left text-sm">
        <thead className="bg-brand-50 text-xs tracking-wide text-brand-700 uppercase">
          <tr>
            {table.columns.map((col) => (
              <th key={col} className="px-4 py-2.5 font-medium">
                {col}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100">
          {table.rows.map((row, i) => (
            <tr key={i} className="text-slate-700 hover:bg-brand-50/40">
              {table.columns.map((col) => (
                <td key={col} className="px-4 py-2.5 tabular-nums">
                  {formatCell(row[col])}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
