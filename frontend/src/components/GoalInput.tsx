import { useRef } from "react";
import type { FileMeta } from "../types";

interface GoalInputProps {
  goal: string;
  onGoalChange: (goal: string) => void;
  onGenerate: () => void;
  disabled: boolean;
  isBusy: boolean;
  files: FileMeta[];
}

interface Suggestion {
  label: string;
  template: string;
}

function suggestionsFor(files: FileMeta[]): Suggestion[] {
  const hasPdf = files.some((f) => f.file_type === "pdf");
  const spreadsheets = files.filter((f) => f.file_type === "csv" || f.file_type === "excel");

  const suggestions: Suggestion[] = [];
  if (hasPdf) {
    suggestions.push(
      { label: "Summarise", template: "Summarise this document, focusing on: " },
      { label: "Extract to a table", template: "Extract the following into a table: " }
    );
  }
  if (spreadsheets.length > 0) {
    suggestions.push(
      { label: "Find biggest changes", template: "Find the rows where " },
      { label: "Trend chart", template: "Show me a chart of the trend in " }
    );
  }
  if (spreadsheets.length >= 2) {
    suggestions.push({ label: "Compare files", template: "Compare these files on the column " });
  }
  return suggestions;
}

export function GoalInput({ goal, onGoalChange, onGenerate, disabled, isBusy, files }: GoalInputProps) {
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const suggestions = suggestionsFor(files);

  function applySuggestion(template: string) {
    onGoalChange(template);
    requestAnimationFrame(() => {
      const el = textareaRef.current;
      if (el) {
        el.focus();
        el.setSelectionRange(el.value.length, el.value.length);
      }
    });
  }

  return (
    <div className="mt-5">
      <label className="block text-sm font-medium text-ink-secondary">
        What would you like to achieve?
      </label>

      {suggestions.length > 0 && (
        <div className="mt-2 mb-3 flex flex-wrap gap-1.5">
          {suggestions.map((suggestion) => (
            <button
              key={suggestion.label}
              type="button"
              onClick={() => applySuggestion(suggestion.template)}
              className="rounded-full border border-purple-700/60 bg-purple-900/20 px-2.5 py-1 text-xs text-purple-200 transition-colors hover:bg-purple-900/40"
            >
              {suggestion.label}
            </button>
          ))}
        </div>
      )}

      <textarea
        ref={textareaRef}
        value={goal}
        onChange={(e) => onGoalChange(e.target.value)}
        placeholder="Compare the two months and find products with a significant sales decline…"
        rows={3}
        className={`w-full resize-none rounded-lg border border-line bg-surface-2 px-3 py-2 text-sm text-ink placeholder:text-ink-muted focus:border-purple-400 focus:ring-2 focus:ring-purple-900/60 focus:outline-none ${
          suggestions.length > 0 ? "" : "mt-1.5"
        }`}
      />
      <button
        onClick={onGenerate}
        disabled={disabled || isBusy}
        className="mt-3 w-full rounded-lg bg-gradient-to-r from-purple-600 to-pink-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm shadow-purple-900/50 transition-colors hover:from-purple-500 hover:to-pink-500 disabled:cursor-not-allowed disabled:bg-none disabled:bg-surface-2 disabled:text-ink-muted disabled:shadow-none"
      >
        {isBusy ? "Working…" : "Generate Result"}
      </button>
    </div>
  );
}
