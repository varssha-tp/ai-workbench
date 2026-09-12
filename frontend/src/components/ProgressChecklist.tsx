import { useEffect, useState } from "react";

interface ProgressChecklistProps {
  steps: string[];
  done: boolean;
}

const REVEAL_INTERVAL_MS = 800;

export function ProgressChecklist({ steps, done }: ProgressChecklistProps) {
  const [revealedCount, setRevealedCount] = useState(1);

  useEffect(() => {
    const id = window.setInterval(() => {
      setRevealedCount((count) => Math.min(count + 1, steps.length));
    }, REVEAL_INTERVAL_MS);
    return () => window.clearInterval(id);
  }, [steps.length]);

  const activeIndex = done ? steps.length : revealedCount - 1;

  return (
    <ul className="space-y-2.5">
      {steps.map((step, i) => {
        const isDone = done || i < activeIndex;
        const isActive = !done && i === activeIndex;
        return (
          <li key={i} className="flex items-center gap-2.5 text-sm">
            <span
              className={`flex h-5 w-5 shrink-0 items-center justify-center rounded-full text-xs ${
                isDone
                  ? "bg-emerald-500 text-white"
                  : isActive
                    ? "animate-pulse bg-brand-200 text-brand-700"
                    : "bg-slate-100 text-slate-300"
              }`}
            >
              {isDone ? "✓" : i + 1}
            </span>
            <span className={isDone || isActive ? "text-slate-800" : "text-slate-400"}>{step}</span>
          </li>
        );
      })}
    </ul>
  );
}
