import type { ReactNode } from "react";
import type { ToolCall, WorkflowResult } from "../types";
import { Chart } from "./Chart";
import { DataTable } from "./DataTable";

interface ResultViewProps {
  result: WorkflowResult;
  workflowSteps: string[];
  planCalls: ToolCall[];
  onReset: () => void;
}

function Badge({ kind }: { kind: "computed" | "narrated" }) {
  if (kind === "computed") {
    return (
      <span className="rounded-full bg-emerald-500/15 px-2 py-0.5 text-[10px] font-medium tracking-wide text-emerald-400 normal-case">
        ✓ computed
      </span>
    );
  }
  return (
    <span className="rounded-full bg-surface-2 px-2 py-0.5 text-[10px] font-medium tracking-wide text-ink-muted normal-case">
      AI-narrated
    </span>
  );
}

function SectionHeading({ children, badge }: { children: ReactNode; badge?: "computed" | "narrated" }) {
  return (
    <h3 className="flex items-center gap-1.5 text-sm font-semibold tracking-wide text-purple-300 uppercase">
      <span className="h-3.5 w-1 rounded-full bg-gradient-to-b from-purple-400 to-pink-400" />
      {children}
      {badge && <Badge kind={badge} />}
    </h3>
  );
}

export function ResultView({ result, workflowSteps, planCalls, onReset }: ResultViewProps) {
  return (
    <div className="space-y-6">
      <div>
        <SectionHeading badge="narrated">Result</SectionHeading>
        <p className="mt-1.5 text-sm text-ink-secondary">{result.summary}</p>
      </div>

      {result.findings.length > 0 && (
        <div>
          <SectionHeading badge="narrated">Key findings</SectionHeading>
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
          <SectionHeading badge="computed">{result.table.title}</SectionHeading>
          <div className="mt-1.5">
            <DataTable table={result.table} />
          </div>
        </div>
      )}

      {result.chart && (
        <div>
          <SectionHeading badge="computed">Visualisation</SectionHeading>
          <div className="mt-1.5">
            <Chart chart={result.chart} />
          </div>
        </div>
      )}

      <div>
        <SectionHeading>Workflow used</SectionHeading>
        <ol className="mt-1.5 list-decimal space-y-1 pl-5 text-sm text-ink-muted">
          {workflowSteps.map((step, i) => (
            <li key={i}>{step}</li>
          ))}
        </ol>

        {planCalls.length > 0 && (
          <details className="mt-2 text-xs">
            <summary className="cursor-pointer text-ink-muted hover:text-ink-secondary">
              Show technical details
            </summary>
            <div className="mt-2 space-y-2 rounded-lg border border-line bg-surface-2 p-3">
              {planCalls.map((call, i) => (
                <div key={i}>
                  <div className="flex items-center gap-1.5">
                    <span className="text-ink-muted">{i + 1}.</span>
                    <code className="rounded bg-purple-900/30 px-1.5 py-0.5 text-purple-200">{call.tool}</code>
                  </div>
                  <pre className="mt-1 overflow-x-auto rounded bg-black/30 p-2 text-ink-secondary">
                    {JSON.stringify(call.args, null, 2)}
                  </pre>
                </div>
              ))}
            </div>
          </details>
        )}
      </div>

      <button
        onClick={onReset}
        className="text-sm font-medium text-purple-300 underline decoration-purple-700 underline-offset-2 hover:text-pink-300"
      >
        Start a new request
      </button>
    </div>
  );
}
