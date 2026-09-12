import type { WorkflowResult } from "../types";
import { Chart } from "./Chart";
import { DataTable } from "./DataTable";

interface ResultViewProps {
  result: WorkflowResult;
  workflowSteps: string[];
  onReset: () => void;
}

export function ResultView({ result, workflowSteps, onReset }: ResultViewProps) {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-sm font-semibold tracking-wide text-slate-400 uppercase">Result</h2>
        <p className="mt-1.5 text-sm text-slate-700">{result.summary}</p>
      </div>

      {result.findings.length > 0 && (
        <div>
          <h3 className="text-sm font-semibold tracking-wide text-slate-400 uppercase">Key findings</h3>
          <ul className="mt-1.5 list-disc space-y-1 pl-5 text-sm text-slate-700">
            {result.findings.map((finding, i) => (
              <li key={i}>{finding}</li>
            ))}
          </ul>
        </div>
      )}

      {result.table && (
        <div>
          <h3 className="text-sm font-semibold tracking-wide text-slate-400 uppercase">{result.table.title}</h3>
          <div className="mt-1.5">
            <DataTable table={result.table} />
          </div>
        </div>
      )}

      {result.chart && (
        <div>
          <h3 className="text-sm font-semibold tracking-wide text-slate-400 uppercase">Visualisation</h3>
          <div className="mt-1.5">
            <Chart chart={result.chart} />
          </div>
        </div>
      )}

      <div>
        <h3 className="text-sm font-semibold tracking-wide text-slate-400 uppercase">Workflow used</h3>
        <ol className="mt-1.5 list-decimal space-y-1 pl-5 text-sm text-slate-500">
          {workflowSteps.map((step, i) => (
            <li key={i}>{step}</li>
          ))}
        </ol>
      </div>

      <button
        onClick={onReset}
        className="text-sm font-medium text-slate-500 underline decoration-slate-300 underline-offset-2 hover:text-slate-700"
      >
        Start a new request
      </button>
    </div>
  );
}
