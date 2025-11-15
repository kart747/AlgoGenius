"use client";

import {
  ProblemSection,
  ExampleCard,
  DifficultyBadge,
} from "./SolveComponents";

function splitParagraphs(text) {
  if (!text) return [];
  return text
    .split("\n")
    .map((p) => p.trim())
    .filter(Boolean);
}

export default function ProblemPanel({ problem }) {
  const descriptionParagraphs = splitParagraphs(
    problem.description || problem.problem_statement || ""
  );

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
      </div>
    </div>
  );
}
