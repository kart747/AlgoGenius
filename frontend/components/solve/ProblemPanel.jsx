"use client";

import { toast } from "@/lib/toast";
import {
  ProblemSection,
  ExampleCard,
  DifficultyBadge,
} from "./SolveComponents";
import { LANGUAGE_PRESETS } from "./languagePresets";
import { useUserContext } from "../UserProvider";
import AdminProblemDeleteButton from "../admin/AdminProblemDeleteButton";
import ProblemComments from "./ProblemComments";

function splitParagraphs(text) {
  if (!text) return [];
  return text
    .split("\n")
    .map((p) => p.trim())
    .filter(Boolean);
}

export default function ProblemPanel({
  problem,
  functionTemplates = {},
  onProblemDeleted,
}) {
  const { isAdmin } = useUserContext();
  const descriptionParagraphs = splitParagraphs(
    problem.description || problem.problem_statement || ""
  );

  const hasTemplateData = LANGUAGE_PRESETS.some((preset) => {
    const entry = functionTemplates?.[preset.id];
    return entry?.template || entry?.loading || entry?.error;
  });

  const copyTemplate = async (template) => {
    if (!template) return;
    try {
      await navigator.clipboard.writeText(template);
      toast.success("Function template copied to clipboard.");
    } catch (err) {
      console.error("Copy failed", err);
      toast.error("Unable to copy template.");
    }
  };

  return (
    <div className="scrollbar-thin scrollbar-track-transparent scrollbar-thumb-slate-700 flex h-full flex-col overflow-y-auto">
      <div className="space-y-6 p-6">
        {/* Header */}
        <div className="space-y-3">
          <div className="flex items-center gap-3">
            <h1 className="text-xl font-bold text-slate-100">
              {problem.title}
            </h1>
            <DifficultyBadge difficulty={problem.difficulty} />
          </div>
          {isAdmin && (
            <div className="flex justify-end">
              <AdminProblemDeleteButton
                problemId={problem.id}
                title={problem.title}
                onDeleted={onProblemDeleted}
              />
            </div>
          )}
        </div>

        {/* Description */}
        <ProblemSection title="Description">
          <div className="space-y-3 text-sm leading-relaxed text-slate-300">
            {descriptionParagraphs.length ? (
              descriptionParagraphs.map((paragraph, idx) => (
                <p key={idx}>{paragraph}</p>
              ))
            ) : (
              <p className="text-slate-500">No description provided.</p>
            )}
          </div>
        </ProblemSection>

        {/* Examples */}
        {Array.isArray(problem.examples) && problem.examples.length > 0 && (
          <ProblemSection title="Examples">
            <div className="space-y-3">
              {problem.examples.map((example, idx) => (
                <ExampleCard
                  key={example.id ?? idx}
                  example={example}
                  index={idx}
                />
              ))}
            </div>
          </ProblemSection>
        )}

        {/* Input Format */}
        {problem.input_format && (
          <ProblemSection title="Input Format">
            <div className="rounded-lg border border-slate-700/60 bg-slate-900/40 p-4">
              <pre className="text-xs leading-relaxed text-slate-300 whitespace-pre-wrap">
                {problem.input_format}
              </pre>
            </div>
          </ProblemSection>
        )}

        {/* Output Format */}
        {problem.output_format && (
          <ProblemSection title="Output Format">
            <div className="rounded-lg border border-slate-700/60 bg-slate-900/40 p-4">
              <pre className="text-xs leading-relaxed text-slate-300 whitespace-pre-wrap">
                {problem.output_format}
              </pre>
            </div>
          </ProblemSection>
        )}

        {/* Constraints */}
        {problem.constraints && (
          <ProblemSection title="Constraints">
            <div className="rounded-lg border border-slate-700/60 bg-slate-900/40 p-4">
              <pre className="text-xs leading-relaxed text-slate-300 whitespace-pre-wrap">
                {problem.constraints}
              </pre>
            </div>
          </ProblemSection>
        )}

        {/* Function Templates */}
        {hasTemplateData && (
          <ProblemSection title="Function Templates">
            <div className="space-y-4">
              {LANGUAGE_PRESETS.map((preset) => {
                const entry = functionTemplates?.[preset.id];
                if (!entry) {
                  return null;
                }
                const { template, loading, error } = entry;
                return (
                  <div
                    key={preset.id}
                    className="rounded-2xl border border-slate-700/60 bg-slate-900/40 p-4"
                  >
                    <div className="mb-3 flex flex-wrap items-center gap-3 justify-between">
                      <div className="text-sm font-semibold text-slate-200">
                        {preset.label}
                      </div>
                      {template && (
                        <button
                          type="button"
                          onClick={() => copyTemplate(template)}
                          className="rounded-full border border-slate-600 px-3 py-1 text-xs font-semibold text-slate-200 transition hover:border-emerald-500 hover:text-emerald-200"
                        >
                          Copy Template
                        </button>
                      )}
                      {loading && (
                        <span className="text-xs text-slate-400">
                          Generating...
                        </span>
                      )}
                      {error && (
                        <span className="text-xs text-rose-300">
                          {error}
                        </span>
                      )}
                    </div>
                    {template ? (
                      <pre className="rounded-lg border border-slate-800 bg-black/40 p-3 text-[11px] text-slate-200 whitespace-pre-wrap">
                        {template}
                      </pre>
                    ) : loading ? (
                      <p className="text-xs text-slate-400">
                        Gemini is generating this template. Please hold tight.
                      </p>
                    ) : (
                      <p className="text-xs text-slate-500">
                        Template unavailable for this language.
                      </p>
                    )}
                  </div>
                );
              })}
            </div>
          </ProblemSection>
        )}

        {/* Hidden Tests Info */}
        {Array.isArray(problem.test_cases) && problem.test_cases.length > 0 && (
          <ProblemSection title="Test Cases">
            <div className="rounded-lg border border-slate-700/60 bg-slate-900/40 p-4">
              <p className="text-xs text-slate-400">
                <span className="font-semibold text-slate-300">
                  {problem.test_cases.length} hidden test case
                  {problem.test_cases.length !== 1 ? "s" : ""}
                </span>{" "}
                will be used to validate your submission. Write your own tests
                using the custom input panel.
              </p>
            </div>
          </ProblemSection>
        )}

        <ProblemSection title="Discussion">
          <ProblemComments problemId={problem.id} />
        </ProblemSection>
      </div>
    </div>
  );
}
