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
      <label className="block text-sm font-medium text-ink-secondary">
        What would you like to achieve?
      </label>
      <textarea
        value={goal}
        onChange={(e) => onGoalChange(e.target.value)}
        placeholder="Compare the two months and find products with a significant sales decline…"
        rows={3}
        className="mt-1.5 w-full resize-none rounded-lg border border-line bg-surface-2 px-3 py-2 text-sm text-ink placeholder:text-ink-muted focus:border-purple-400 focus:ring-2 focus:ring-purple-900/60 focus:outline-none"
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
