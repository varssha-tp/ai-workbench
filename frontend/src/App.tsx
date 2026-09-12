import { useState } from "react";
import { executeWorkflow, getPlan } from "./api";
import { Dropzone } from "./components/Dropzone";
import { GoalInput } from "./components/GoalInput";
import { ProgressChecklist } from "./components/ProgressChecklist";
import { ResultView } from "./components/ResultView";
import type { FileMeta, ToolCall, WorkflowResult } from "./types";

type Status = "idle" | "planning" | "running" | "done" | "error";

function App() {
  const [files, setFiles] = useState<FileMeta[]>([]);
  const [goal, setGoal] = useState("");
  const [status, setStatus] = useState<Status>("idle");
  const [planSteps, setPlanSteps] = useState<string[]>([]);
  const [planCalls, setPlanCalls] = useState<ToolCall[]>([]);
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
      setPlanCalls(plan.calls);
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
    setPlanCalls([]);
    setError(null);
  }

  return (
    <div className="min-h-screen px-4 py-12">
      <div className="mx-auto max-w-xl overflow-hidden rounded-2xl border border-white/10 bg-surface/60 shadow-2xl shadow-purple-900/50 backdrop-blur-xl">
        <div className="h-1.5 bg-gradient-to-r from-purple-500 via-purple-400 to-pink-400" />
        <div className="p-8">
          <div className="text-center">
            <h1 className="bg-gradient-to-r from-purple-300 via-purple-400 to-pink-400 bg-clip-text text-2xl font-bold tracking-tight text-transparent">
              AI Workbench
            </h1>
            <p className="mt-1.5 text-sm text-ink-secondary">Turn information into useful results.</p>
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
                files={files}
              />
              {status === "error" && error && <p className="mt-3 text-sm text-red-400">{error}</p>}
            </div>
          )}

          {(status === "planning" || status === "running") && (
            <div className="mt-8">
              {status === "planning" ? (
                <div>
                  <p className="text-sm text-ink-secondary">Understanding your request…</p>
                  <div className="mt-3 h-1.5 w-full overflow-hidden rounded-full bg-surface-2">
                    <div className="h-full w-1/3 animate-pulse rounded-full bg-gradient-to-r from-purple-500 to-pink-500" />
                  </div>
                </div>
              ) : (
                <ProgressChecklist steps={planSteps} done={executeDone} />
              )}
            </div>
          )}

          {status === "done" && result && (
            <div className="mt-8">
              <ResultView result={result} workflowSteps={planSteps} planCalls={planCalls} onReset={handleReset} />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
