"use client";

export function DifficultyBadge({ difficulty }) {
  const styles = {
    easy: "bg-emerald-500/15 text-emerald-300 border-emerald-400/40",
    medium: "bg-amber-500/15 text-amber-300 border-amber-400/40",
    hard: "bg-rose-500/15 text-rose-300 border-rose-400/40",
  };

  const label = (difficulty || "easy").toLowerCase();
  const style = styles[label] || styles.easy;

  return (
    <span
      className={`inline-flex items-center rounded-full border px-3 py-1 text-xs font-semibold uppercase tracking-wide ${style}`}
    >
      {label}
    </span>
  );
}

export function VerdictBadge({ status }) {
  const configs = {
    AC: {
      label: "Accepted",
      className: "bg-emerald-500/15 text-emerald-200 border-emerald-400/40",
    },
    WA: {
      label: "Wrong Answer",
      className: "bg-amber-500/15 text-amber-200 border-amber-400/40",
    },
    TLE: {
      label: "Time Limit",
      className: "bg-sky-500/15 text-sky-200 border-sky-400/40",
    },
    RE: {
      label: "Runtime Error",
      className: "bg-rose-500/15 text-rose-200 border-rose-400/40",
    },
    RUNNING: {
      label: "Running...",
      className:
        "bg-indigo-500/15 text-indigo-200 border-indigo-400/40 animate-pulse",
    },
    SUBMITTING: {
      label: "Submitting...",
      className:
        "bg-purple-500/15 text-purple-200 border-purple-400/40 animate-pulse",
    },
    PENDING: {
      label: "Idle",
      className: "bg-slate-500/15 text-slate-200 border-slate-400/40",
    },
  };

  const config = configs[status] || configs.PENDING;

  return (
    <span
      className={`inline-flex items-center rounded-full border px-3 py-1 text-xs font-semibold ${config.className}`}
    >
      {config.label}
    </span>
  );
}

export function MetricDisplay({ label, value, suffix = "" }) {
  return (
    <div className="flex flex-col gap-1">
      <span className="text-[10px] uppercase tracking-wider text-slate-400">
        {label}
      </span>
      <span className="text-sm font-semibold text-slate-100">
        {value !== null && value !== undefined ? `${value}${suffix}` : "—"}
      </span>
    </div>
  );
}

export function ProblemSection({ title, children, className = "" }) {
  return (
    <section className={`space-y-3 ${className}`}>
      <h3 className="text-sm font-semibold uppercase tracking-wider text-slate-300">
        {title}
      </h3>
      {children}
    </section>
  );
}

function buildVisualSteps(example) {
  const explicitSteps =
    example?.visual_explanation?.steps ||
    example?.visual?.steps ||
    example?.visualExplanation?.steps;

  const normalize = (step, idx) => {
    if (!step) {
      return null;
    }
    if (typeof step === "string") {
      return {
        title: `Step ${idx + 1}`,
        description: step.trim(),
      };
    }
    if (typeof step === "object") {
      return {
        title: step.title || step.label || `Step ${idx + 1}`,
        description: step.description || step.text || step.detail || "",
      };
    }
    return null;
  };

  if (Array.isArray(explicitSteps) && explicitSteps.length) {
    return explicitSteps.map((step, idx) => normalize(step, idx)).filter(Boolean);
  }

  // Derive pseudo-steps from the plain-text explanation when no structured data exists.
  if (typeof example?.explanation === "string" && example.explanation.trim()) {
    const sentences = example.explanation
      .split(/(?<=[.!?])\s+/)
      .map((sentence) => sentence.trim())
      .filter(Boolean)
      .slice(0, 4);
    return sentences.map((sentence, idx) => ({
      title: `Step ${idx + 1}`,
      description: sentence,
    }));
  }

  return [];
}

export function ExampleCard({ example, index }) {
  const visualMetadata =
    example.visual_explanation || example.visual || example.visualExplanation;
  const visualImage =
    visualMetadata?.image_url ||
    visualMetadata?.imageUrl ||
    visualMetadata?.image ||
    visualMetadata?.url;
  const visualCaption = visualMetadata?.caption || visualMetadata?.description;
  const visualSteps = buildVisualSteps(example);
  const hasVisualAid = Boolean(visualImage || visualSteps.length);

  return (
    <div className="rounded-xl border border-slate-700/60 bg-slate-900/40 p-4">
      <h4 className="mb-3 text-xs font-semibold text-slate-300">
        Example {index + 1}
      </h4>
      <div className="space-y-3">
        <div>
          <div className="mb-1.5 text-[11px] font-medium uppercase tracking-wide text-slate-400">
            Input
          </div>
          <pre className="rounded-lg bg-slate-950/60 p-3 text-xs text-slate-200 whitespace-pre-wrap font-mono">
            {example.input ?? example.input_data ?? ""}
          </pre>
        </div>
        <div>
          <div className="mb-1.5 text-[11px] font-medium uppercase tracking-wide text-slate-400">
            Output
          </div>
          <pre className="rounded-lg bg-slate-950/60 p-3 text-xs text-slate-200 whitespace-pre-wrap font-mono">
            {example.output ?? example.output_data ?? ""}
          </pre>
        </div>
        {example.explanation && (
          <p className="text-xs leading-relaxed text-slate-400">
            {example.explanation}
          </p>
        )}

        {hasVisualAid && (
          <div className="space-y-2 rounded-lg border border-indigo-500/30 bg-slate-950/40 p-3">
            <div className="text-[11px] font-semibold uppercase tracking-wide text-indigo-200">
              Visual Walkthrough
            </div>
            <div className="flex flex-col gap-4 lg:flex-row">
              {visualImage && (
                <div className="flex-1">
                  <div className="overflow-hidden rounded-md border border-slate-800 bg-black/40">
                    <img
                      src={visualImage}
                      alt={
                        visualMetadata?.alt ||
                        `Illustration for example ${index + 1}`
                      }
                      className="h-48 w-full object-cover"
                      loading="lazy"
                    />
                  </div>
                  {visualCaption && (
                    <p className="mt-2 text-[11px] text-slate-400">
                      {visualCaption}
                    </p>
                  )}
                </div>
              )}
              {visualSteps.length > 0 && (
                <ol className="flex-1 space-y-2 text-xs text-slate-200">
                  {visualSteps.map((step, idx) => (
                    <li
                      key={`${step.title}-${idx}`}
                      className="rounded-md border border-slate-800/80 bg-slate-900/40 p-3"
                    >
                      <div className="text-[11px] font-bold uppercase tracking-wide text-indigo-300">
                        {step.title || `Step ${idx + 1}`}
                      </div>
                      {step.description && (
                        <p className="mt-1 text-slate-300">{step.description}</p>
                      )}
                    </li>
                  ))}
                </ol>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export function ActionButton({
  onClick,
  disabled,
  variant = "primary",
  children,
  icon,
  className = "",
}) {
  const variants = {
    primary:
      "bg-indigo-600 hover:bg-indigo-700 text-white shadow-lg shadow-indigo-500/25",
    secondary: "border border-slate-600 hover:bg-slate-800 text-slate-200",
    danger: "bg-rose-600 hover:bg-rose-700 text-white",
    ghost: "hover:bg-slate-800 text-slate-300",
  };

  return (
    <button
      type="button"
      onClick={onClick}
      disabled={disabled}
      className={`inline-flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-medium transition disabled:opacity-50 disabled:cursor-not-allowed ${variants[variant]} ${className}`}
    >
      {icon && <span className="text-base">{icon}</span>}
      {children}
    </button>
  );
}
