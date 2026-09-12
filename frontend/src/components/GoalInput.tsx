interface GoalInputProps {
  goal: string;
  onGoalChange: (goal: string) => void;
  onGenerate: () => void;
  disabled: boolean;
  isBusy: boolean;
}

export function GoalInput({ goal, onGoalChange, onGenerate, disabled, isBusy }: GoalInputProps) {
  return (
    <div className="mt-5">
      <label className="block text-sm font-medium text-slate-700">
        What would you like to achieve?
      </label>
      <textarea
        value={goal}
        onChange={(e) => onGoalChange(e.target.value)}
        placeholder="Compare the two months and find products with a significant sales decline…"
        rows={3}
        className="mt-1.5 w-full resize-none rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 placeholder:text-slate-400 focus:border-slate-500 focus:outline-none"
      />
      <button
        onClick={onGenerate}
        disabled={disabled || isBusy}
        className="mt-3 w-full rounded-lg bg-slate-900 px-4 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-slate-700 disabled:cursor-not-allowed disabled:bg-slate-300"
      >
        {isBusy ? "Working…" : "Generate Result"}
      </button>
    </div>
  );
}
