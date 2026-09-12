import type { ReactNode } from "react";
import type { WorkflowResult } from "../types";
import { Chart } from "./Chart";
import { DataTable } from "./DataTable";

interface ResultViewProps {
  result: WorkflowResult;
  workflowSteps: string[];
  onReset: () => void;
}

function SectionHeading({ children }: { children: ReactNode }) {
  return (
    <h3 className="flex items-center gap-1.5 text-sm font-semibold tracking-wide text-purple-300 uppercase">
      <span className="h-3.5 w-1 rounded-full bg-gradient-to-b from-purple-400 to-pink-400" />
      {children}
    </h3>
  );
}

export function ResultView({ result, workflowSteps, onReset }: ResultViewProps) {
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
          <SectionHeading>{result.table.title}</SectionHeading>
          <div className="mt-1.5">
            <DataTable table={result.table} />
          </div>
        </div>
      )}

      {result.chart && (
        <div>
          <SectionHeading>Visualisation</SectionHeading>
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
