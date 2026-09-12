import { useState } from "react";
import { executeWorkflow, getPlan } from "./api";
import { Dropzone } from "./components/Dropzone";
import { GoalInput } from "./components/GoalInput";
import { ProgressChecklist } from "./components/ProgressChecklist";
import { ResultView } from "./components/ResultView";
import type { FileMeta, WorkflowResult } from "./types";

type Status = "idle" | "planning" | "running" | "done" | "error";

function App() {
  const [files, setFiles] = useState<FileMeta[]>([]);
  const [goal, setGoal] = useState("");
  const [status, setStatus] = useState<Status>("idle");
  const [planSteps, setPlanSteps] = useState<string[]>([]);
  const [result, setResult] = useState<WorkflowResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [executeDone, setExecuteDone] = useState(false);

  const canGenerate = files.length > 0 && goal.trim().length > 0;

  async function handleGenerate() {
    setStatus("planning");
    setError(null);
    setExecuteDone(false);
    const fileIds = files.map((f) => f.file_id);

    try {
      const plan = await getPlan(goal, fileIds);
      setPlanSteps(plan.steps);
      setStatus("running");

      const workflowResult = await executeWorkflow(goal, fileIds);
      setExecuteDone(true);
      setResult(workflowResult);
      setStatus("done");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Something went wrong");
      setStatus("error");
    }
  }

  function handleReset() {
    setStatus("idle");
    setResult(null);
    setPlanSteps([]);
    setError(null);
  }

  return (
    <div className="min-h-screen px-4 py-12">
      <div className="mx-auto max-w-xl overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-lg shadow-slate-200/60">
        <div className="h-1.5 bg-gradient-to-r from-brand-600 via-brand-500 to-brand-300" />
        <div className="p-8">
          <div className="text-center">
            <h1 className="bg-gradient-to-r from-brand-700 to-brand-500 bg-clip-text text-2xl font-bold tracking-tight text-transparent">
              AI Workbench
            </h1>
            <p className="mt-1.5 text-sm text-slate-500">Turn information into useful results.</p>
          </div>

          {(status === "idle" || status === "error") && (
            <div className="mt-8">
              <Dropzone files={files} onFilesAdded={(newFiles) => setFiles((f) => [...f, ...newFiles])} />
              <GoalInput
                goal={goal}
                onGoalChange={setGoal}
                onGenerate={handleGenerate}
                disabled={!canGenerate}
                isBusy={false}
              />
              {status === "error" && error && <p className="mt-3 text-sm text-red-600">{error}</p>}
            </div>
          )}

          {(status === "planning" || status === "running") && (
            <div className="mt-8">
              {status === "planning" ? (
                <p className="text-sm text-slate-500">Understanding your request…</p>
              ) : (
                <ProgressChecklist steps={planSteps} done={executeDone} />
              )}
            </div>
          )}

          {status === "done" && result && (
            <div className="mt-8">
              <ResultView result={result} workflowSteps={planSteps} onReset={handleReset} />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
