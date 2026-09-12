import type { FileMeta, TaskPlan, WorkflowResult } from "./types";

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

async function parseErrorDetail(res: Response, fallback: string): Promise<string> {
  try {
    const body = await res.json();
    return body.detail ?? fallback;
  } catch {
    return fallback;
  }
}

export async function uploadFiles(files: File[]): Promise<FileMeta[]> {
  const formData = new FormData();
  files.forEach((f) => formData.append("files", f));

  const res = await fetch(`${API_BASE}/upload`, { method: "POST", body: formData });
  if (!res.ok) {
    throw new Error(await parseErrorDetail(res, "Upload failed"));
  }
  return res.json();
}

export async function getPlan(goal: string, fileIds: string[]): Promise<TaskPlan> {
  const res = await fetch(`${API_BASE}/plan`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ goal, file_ids: fileIds }),
  });
  if (!res.ok) {
    throw new Error(await parseErrorDetail(res, "Planning failed"));
  }
  return res.json();
}

export async function executeWorkflow(goal: string, fileIds: string[]): Promise<WorkflowResult> {
  const res = await fetch(`${API_BASE}/execute`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ goal, file_ids: fileIds }),
  });
  if (!res.ok) {
    throw new Error(await parseErrorDetail(res, "Execution failed"));
  }
  return res.json();
}
