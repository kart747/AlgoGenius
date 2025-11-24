"use client";

import { useMemo } from "react";
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

const TagPill = ({ label }) => (
  <span className="inline-flex items-center rounded-full border border-indigo-400/40 bg-indigo-500/10 px-3 py-1 text-[11px] font-semibold uppercase tracking-wide text-indigo-100">
    {label}
  </span>
);

export default function ProblemPanel({
  problem,
  onProblemDeleted,
}) {
  const { isAdmin } = useUserContext();
  const descriptionMarkdown =
    problem.description || problem.problem_statement || "";
  const topicTags = useMemo(() => {
    if (!Array.isArray(problem.topics)) {
      return [];
    }
    return problem.topics
      .map((tag) => (typeof tag === "string" ? tag.trim() : ""))
      .filter(Boolean);
  }, [problem.topics]);
  const hasTopics = topicTags.length > 0;

  const updatedTimestamp = problem.updated_at || problem.created_at;
  const updatedLabel = updatedTimestamp
    ? new Date(updatedTimestamp).toLocaleDateString(undefined, {
        month: "short",
        day: "numeric",
        year: "numeric",
      })
    : "—";

  const metaHighlights = [
    {
      label: "Hidden Tests",
      value: Array.isArray(problem.test_cases)
        ? problem.test_cases.length
        : 0,
    },
    {
      label: "Examples",
      value: Array.isArray(problem.examples)
        ? problem.examples.length
        : 0,
    },
    {
      label: "Updated",
      value: updatedLabel,
    },
  ];

  return (
    <div className="scrollbar-thin scrollbar-track-transparent scrollbar-thumb-slate-700 flex h-full flex-col overflow-y-auto">
      <div className="space-y-8 p-6">
        <header className="space-y-4">
          <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
            <div>
              <p className="text-[11px] font-semibold uppercase tracking-[0.35em] text-slate-500">
                DevArena Challenge
              </p>
              <h1 className="mt-1 text-3xl font-bold text-slate-50">
                {problem.title}
              </h1>
            </div>
            <DifficultyBadge difficulty={problem.difficulty} />
          </div>

          <div className="flex flex-wrap items-center gap-3 text-xs text-slate-400">
            {metaHighlights.map((stat) => (
              <span key={stat.label} className="inline-flex items-center gap-1 rounded-full border border-white/10 px-3 py-1 text-[11px] uppercase tracking-[0.3em] text-white/70">
                <span>{stat.label}</span>
                <strong className="font-semibold text-white/90 tracking-normal">
                  {stat.value}
                </strong>
              </span>
            ))}
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <span className="text-[11px] font-semibold uppercase tracking-[0.35em] text-slate-500">
              Topics
            </span>
            {hasTopics ? (
              <div className="flex flex-wrap gap-2">
                {topicTags.map((tag) => (
                  <TagPill key={tag} label={tag} />
                ))}
              </div>
            ) : (
              <p className="text-xs text-slate-500">No topic tags assigned yet.</p>
            )}
          </div>

          {isAdmin && (
            <div>
              <AdminProblemDeleteButton
                problemId={problem.id}
                title={problem.title}
                onDeleted={onProblemDeleted}
              />
            </div>
          )}
        </header>

        <section className="space-y-3">
          <h3 className="text-sm font-semibold uppercase tracking-[0.35em] text-slate-400">
            Description
          </h3>
          <div className="text-sm leading-relaxed text-slate-200">
            {descriptionMarkdown.trim().length ? (
              <ReactMarkdown
                remarkPlugins={[remarkGfm]}
                className="prose prose-invert prose-slate max-w-none text-sm leading-relaxed [&_*]:text-slate-200"
              >
                {descriptionMarkdown}
              </ReactMarkdown>
            ) : (
              <p className="text-slate-500">No description provided.</p>
            )}
          </div>
        </section>

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
                guard the final verdict. Switch to the Custom Input tab to
                preview each case and one-click copy its stdin before running
                locally.
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
