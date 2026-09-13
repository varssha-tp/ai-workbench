import type { ReactNode } from "react";
import type { FileMeta, ToolCall, WorkflowResult } from "../types";
import { Chart } from "./Chart";
import { DataTable } from "./DataTable";

interface ResultViewProps {
  result: WorkflowResult;
  planCalls: ToolCall[];
  files: FileMeta[];
  onReset: () => void;
}

function ComputedBadge() {
  return (
    <span className="rounded-full bg-emerald-500/15 px-2 py-0.5 text-[10px] font-medium tracking-wide text-emerald-400 normal-case">
      ✓ computed
    </span>
  );
}

function SectionHeading({ children, computed }: { children: ReactNode; computed?: boolean }) {
  return (
    <h3 className="flex items-center gap-1.5 text-sm font-semibold tracking-wide text-purple-300 uppercase">
      <span className="h-3.5 w-1 rounded-full bg-gradient-to-b from-purple-400 to-pink-400" />
      {children}
      {computed && <ComputedBadge />}
    </h3>
  );
}

const RESULT_ID_RE = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

// Tool args carry raw file_id/result_id values, meaningless to a reader.
// Swap in the real filename where we know it, or a plain-English label for
// a reference to an earlier step's result — never show a bare UUID.
function describeArgs(args: Record<string, unknown>, fileNames: Record<string, string>): string {
  return Object.entries(args)
    .map(([key, value]) => {
      if (typeof value !== "string") return `${key}: ${value}`;
      if (fileNames[value]) return `${key}: ${fileNames[value]}`;
      if (value.startsWith("$result_of_step_") || RESULT_ID_RE.test(value)) {
        return `${key}: (result from an earlier step)`;
      }
      return `${key}: ${value}`;
    })
    .join(", ");
}

export function ResultView({ result, planCalls, files, onReset }: ResultViewProps) {
  const fileNames = Object.fromEntries(files.map((f) => [f.file_id, f.filename]));

  return (
    <div className="space-y-6">
      <div>
        <SectionHeading>Result</SectionHeading>
        <p className="mt-1.5 text-sm text-ink-secondary">{result.summary}</p>
      </div>

      {result.findings.length > 0 && (
        <div>
          <SectionHeading>Key findings</SectionHeading>
          <ul className="mt-1.5 space-y-1.5 text-sm text-ink-secondary">
            {result.findings.map((finding, i) => (
              <li key={i} className="flex gap-2">
                <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-purple-400" />
                {finding}
              </li>
            ))}
          </ul>
        </div>
      )}

      {result.table && (
        <div>
          <SectionHeading computed>{result.table.title}</SectionHeading>
          <div className="mt-1.5">
            <DataTable table={result.table} />
          </div>
        </div>
      )}

      {result.chart && (
        <div>
          <SectionHeading computed>Visualisation</SectionHeading>
          <div className="mt-3">
            <Chart chart={result.chart} />
          </div>
        </div>
      )}

      {planCalls.length > 0 && (
        <details className="text-sm">
          <summary className="cursor-pointer text-ink-muted hover:text-ink-secondary">
            How this was generated
          </summary>
          <ol className="mt-2 list-decimal space-y-2 rounded-lg border border-line bg-surface-2 p-3 pl-8 text-xs text-ink-secondary">
            {planCalls.map((call, i) => (
              <li key={i}>
                <div>{call.step}</div>
                <div className="mt-0.5 text-ink-muted">
                  <code className="rounded bg-purple-900/30 px-1 py-0.5 text-purple-200">{call.tool}</code>
                  {Object.keys(call.args).length > 0 && <span> — {describeArgs(call.args, fileNames)}</span>}
                </div>
              </li>
            ))}
          </ol>
        </details>
      )}

      <button
        onClick={onReset}
        className="text-sm font-medium text-purple-300 underline decoration-purple-700 underline-offset-2 hover:text-pink-300"
      >
        Start a new request
      </button>
    </div>
  );
}
