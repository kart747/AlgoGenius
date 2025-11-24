"use client";

import {
  ProblemSection,
  ExampleCard,
  DifficultyBadge,
} from "./SolveComponents";
import { useUserContext } from "../UserProvider";
import AdminProblemDeleteButton from "../admin/AdminProblemDeleteButton";
import ProblemComments from "./ProblemComments";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

export default function ProblemPanel({
  problem,
  onProblemDeleted,
}) {
  const { isAdmin } = useUserContext();
  const descriptionMarkdown =
    problem.description || problem.problem_statement || "";

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
          <div className="prose prose-invert prose-slate max-w-none text-sm text-slate-200">
            {descriptionMarkdown.trim().length ? (
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {descriptionMarkdown}
              </ReactMarkdown>
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

        <ProblemSection title="Discussion">
          <ProblemComments problemId={problem.id} />
        </ProblemSection>
      </div>
    </div>
  );
}
