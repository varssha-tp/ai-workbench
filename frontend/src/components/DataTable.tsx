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
    <div className="overflow-x-auto rounded-lg border border-line">
      <table className="w-full text-left text-sm">
        <thead className="bg-surface-2 text-xs tracking-wide text-purple-300 uppercase">
          <tr>
            {table.columns.map((col) => (
              <th key={col} className="px-4 py-2.5 font-medium">
                {col}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-line">
          {table.rows.map((row, i) => (
            <tr key={i} className="text-ink-secondary hover:bg-purple-900/10">
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
