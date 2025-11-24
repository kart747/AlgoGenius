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
  failedCaseDetails,
  testCases = [],
  onTestInputChange,
  onRun,
  onSubmit,
}) {
  const [activeTab, setActiveTab] = useState("input");
  const hasTestCases = Array.isArray(testCases) && testCases.length > 0;

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
      <div className="min-h-[180px] max-h-[260px] overflow-auto p-4">
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
            {hasTestCases && (
              <div className="space-y-3 rounded-lg border border-slate-800/60 bg-slate-950/50 p-3">
                <div className="flex flex-wrap items-center justify-between gap-2 text-[11px] uppercase tracking-wide text-slate-400">
                  <span>Hidden test cases ({testCases.length})</span>
                  <button
                    type="button"
                    onClick={() => onTestInputChange(testCases[0]?.input || "")}
                    className="font-semibold text-indigo-300 hover:text-indigo-200"
                  >
                    Use Case #1
                  </button>
                </div>
                <div className="max-h-48 space-y-3 overflow-y-auto pr-1">
                  {testCases.map((testCase, idx) => {
                    const normalizedInput = testCase.input || "";
                    const isActive = normalizedInput === testInput;
                    return (
                      <div
                        key={testCase.key ?? idx}
                        className={`rounded-lg border p-3 text-[11px] text-slate-300 ${
                          isActive
                            ? "border-indigo-400/60 bg-indigo-500/10"
                            : "border-slate-800 bg-slate-900/60"
                        }`}
                      >
                        <div className="flex items-center justify-between text-[10px] font-semibold uppercase tracking-[0.3em] text-slate-400">
                          <span>Case #{idx + 1}</span>
                          <button
                            type="button"
                            onClick={() => onTestInputChange(normalizedInput)}
                            className="text-indigo-300 hover:text-indigo-200"
                          >
                            Use Input
                          </button>
                        </div>
                        <div className="mt-2">
                          <div className="text-[10px] font-semibold uppercase tracking-wide text-slate-400">
                            Input
                          </div>
                          <pre className="mt-1 rounded bg-black/40 p-2 font-mono text-[11px] text-slate-200 whitespace-pre-wrap">
                            {normalizedInput || "(empty input)"}
                          </pre>
                        </div>
                        <div className="mt-2">
                          <div className="text-[10px] font-semibold uppercase tracking-wide text-slate-400">
                            Expected Output
                          </div>
                          <pre className="mt-1 rounded bg-black/40 p-2 font-mono text-[11px] text-slate-200 whitespace-pre-wrap">
                            {testCase.expected || "(empty output)"}
                          </pre>
                        </div>
                      </div>
                    );
                  })}
                </div>
                <p className="text-[10px] text-slate-500">
                  Selecting a case copies its stdin into your custom input so you can iterate quickly.
                </p>
              </div>
            )}
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
            {failedCaseDetails && (
              <div className="rounded-lg border border-amber-500/40 bg-amber-950/20 p-3">
                <div className="text-xs font-semibold uppercase tracking-wide text-amber-200">
                  Hidden test case #{failedCaseDetails.index ?? "?"}
                </div>
                <div className="mt-2 text-xs text-amber-100">
                  <div className="font-semibold text-amber-200">Input</div>
                  <pre className="mt-1 rounded border border-amber-400/30 bg-black/30 p-2 text-[11px] text-amber-100 whitespace-pre-wrap">
                    {failedCaseDetails.input || "(empty input)"}
                  </pre>
                </div>
                <div className="mt-3 text-xs text-amber-100">
                  <div className="font-semibold text-amber-200">
                    Expected Output
                  </div>
                  <pre className="mt-1 rounded border border-amber-400/30 bg-black/30 p-2 text-[11px] text-amber-100 whitespace-pre-wrap">
                    {failedCaseDetails.expected || "(empty output)"}
                  </pre>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
