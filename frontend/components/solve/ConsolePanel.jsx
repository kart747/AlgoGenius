"use client";

import { useState } from "react";
import { ActionButton, VerdictBadge, MetricDisplay } from "./SolveComponents";

export default function ConsolePanel({
  testInput,
  testOutput,
  diagnostic,
  verdict,
  executionTime,
  memoryUsage,
  busy,
  onTestInputChange,
  onRun,
  onSubmit,
}) {
  const [activeTab, setActiveTab] = useState("input");

  return (
    <div className="flex flex-col border-t border-slate-700/60 bg-slate-900/40">
      {/* Action Bar */}
      <div className="flex items-center justify-between border-b border-slate-700/60 bg-slate-900/60 px-4 py-3">
        <div className="flex items-center gap-3">
          <ActionButton onClick={onRun} disabled={busy} icon="▶">
            Run Code
          </ActionButton>
          <ActionButton
            onClick={onSubmit}
            disabled={busy}
            variant="secondary"
            icon="✓"
          >
            Submit
          </ActionButton>
          <span className="text-xs text-slate-500">Ctrl+Enter to run</span>
        </div>

        <div className="flex items-center gap-4">
          <VerdictBadge status={verdict} />
          <div className="flex gap-4">
            <MetricDisplay label="Time" value={executionTime} suffix=" ms" />
            <MetricDisplay label="Memory" value={memoryUsage} suffix=" KB" />
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-slate-700/60 bg-slate-900/40">
        {["input", "output", "stderr"].map((tab) => (
          <button
            key={tab}
            type="button"
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-2.5 text-xs font-medium uppercase tracking-wide transition ${
              activeTab === tab
                ? "border-b-2 border-indigo-500 text-indigo-300"
                : "text-slate-400 hover:text-slate-200"
            }`}
          >
            {tab === "input" && "Custom Input"}
            {tab === "output" && "Output"}
            {tab === "stderr" && "Errors"}
            {tab === "stderr" && diagnostic && (
              <span className="ml-1.5 inline-flex h-1.5 w-1.5 rounded-full bg-rose-500" />
            )}
          </button>
        ))}
      </div>

      {/* Content */}
      <div className="min-h-[200px] max-h-[300px] overflow-auto p-4">
        {activeTab === "input" && (
          <div className="space-y-2">
            <label className="block text-xs font-medium text-slate-400">
              Enter your test input (stdin)
            </label>
            <textarea
              value={testInput}
              onChange={(e) => onTestInputChange(e.target.value)}
              placeholder="Paste test input here..."
              className="h-40 w-full rounded-lg border border-slate-700 bg-slate-950/60 p-3 font-mono text-sm text-slate-200 placeholder-slate-600 focus:border-indigo-500 focus:outline-none"
            />
          </div>
        )}

        {activeTab === "output" && (
          <div className="space-y-2">
            <div className="text-xs font-medium text-slate-400">
              Program Output (stdout)
            </div>
            <pre className="rounded-lg border border-slate-700/60 bg-slate-950/60 p-3 font-mono text-sm text-slate-200 whitespace-pre-wrap">
              {testOutput || "Run your code to see output here."}
            </pre>
          </div>
        )}

        {activeTab === "stderr" && (
          <div className="space-y-2">
            <div className="text-xs font-medium text-slate-400">
              Error Output (stderr)
            </div>
            {diagnostic ? (
              <pre className="rounded-lg border border-rose-500/40 bg-rose-950/20 p-3 font-mono text-sm text-rose-200 whitespace-pre-wrap">
                {diagnostic}
              </pre>
            ) : (
              <div className="rounded-lg border border-slate-700/60 bg-slate-950/60 p-3 text-center text-sm text-slate-500">
                No errors
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
