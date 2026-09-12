export type FileType = "pdf" | "csv" | "excel";

export interface FileMeta {
  file_id: string;
  filename: string;
  file_type: FileType;
  size_bytes: number;
}

export interface ToolCall {
  step: string;
  tool: string;
  args: Record<string, unknown>;
}

export interface TaskPlan {
  goal: string;
  calls: ToolCall[];
  steps: string[];
  tools: string[];
}

export interface TableSpec {
  title: string;
  columns: string[];
  rows: Record<string, unknown>[];
}

export type ChartType = "bar" | "line" | "pie";

export interface ChartSpec {
  chart_type: ChartType;
  x_field: string;
  y_field: string;
  title: string;
  rows: Record<string, unknown>[];
}

export interface WorkflowResult {
  goal: string;
  summary: string;
  findings: string[];
  table: TableSpec | null;
  chart: ChartSpec | null;
}
