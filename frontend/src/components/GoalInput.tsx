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
        className="mt-1.5 w-full resize-none rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 placeholder:text-slate-400 focus:border-brand-500 focus:ring-2 focus:ring-brand-100 focus:outline-none"
      />
      <button
        onClick={onGenerate}
        disabled={disabled || isBusy}
        className="mt-3 w-full rounded-lg bg-gradient-to-r from-brand-600 to-brand-500 px-4 py-2.5 text-sm font-semibold text-white shadow-sm shadow-brand-500/30 transition-colors hover:from-brand-700 hover:to-brand-600 disabled:cursor-not-allowed disabled:bg-none disabled:bg-slate-300 disabled:shadow-none"
      >
        {isBusy ? "Working…" : "Generate Result"}
      </button>
    </div>
  );
}
