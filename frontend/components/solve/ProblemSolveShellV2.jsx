"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { toast } from "@/lib/toast";
import api from "@/src/lib/api";
import { useUserContext } from "../UserProvider";
import ProblemPanel from "./ProblemPanel";
import CodeEditor from "./CodeEditor";
import ConsolePanel from "./ConsolePanel";
import AssistantPanel from "./AssistantPanel";
import { LANGUAGE_PRESETS, getLanguagePreset } from "./languagePresets";
import AdminProblemDeleteButton from "../admin/AdminProblemDeleteButton";

const MIN_LEFT_WIDTH = 0.22;
const MIN_MIDDLE_WIDTH = 0.28;
const MIN_ASSISTANT_WIDTH = 0.2;
const LANGUAGE_IDS = LANGUAGE_PRESETS.map((preset) => preset.id);

const clamp = (value, min, max) => Math.min(Math.max(value, min), max);

function normalizeStatus(status) {
  if (!status) return "PENDING";
  const normalized = status.toString().trim().toUpperCase();
  if (
    ["AC", "WA", "RE", "TLE", "PENDING", "RUNNING", "SUBMITTING"].includes(
      normalized
    )
  ) {
    return normalized;
  }
  if (normalized.includes("ACCEPT") || normalized.includes("SUCCESS"))
    return "AC";
  if (normalized.includes("WRONG")) return "WA";
  if (normalized.includes("TIME") || normalized.includes("LIMIT")) return "TLE";
  if (
    normalized.includes("RUNTIME") ||
    normalized.includes("ERROR") ||
    normalized.includes("FAIL")
  )
    return "RE";
  return normalized || "PENDING";
}

export default function ProblemSolveShell({ problem }) {
  const router = useRouter();
  const { isAdmin } = useUserContext();
  const [language, setLanguage] = useState("python");
  const [codeMap, setCodeMap] = useState(() =>
    LANGUAGE_IDS.reduce((acc, lang) => {
      acc[lang] = "";
      return acc;
    }, {})
  );
  const code = codeMap[language] ?? "";
  const [testInput, setTestInput] = useState("");
  const [testOutput, setTestOutput] = useState("");
  const [diagnostic, setDiagnostic] = useState("");
  const [verdict, setVerdict] = useState("PENDING");
  const [executionTime, setExecutionTime] = useState(null);
  const [memoryUsage, setMemoryUsage] = useState(null);
  const [theme, setTheme] = useState("vs-dark");
  const [busy, setBusy] = useState(false);
  const [functionTemplateState, setFunctionTemplateState] = useState({});
  const [failedCaseDetails, setFailedCaseDetails] = useState(null);
  const [assistantOpen, setAssistantOpen] = useState(true);
  const [leftWidth, setLeftWidth] = useState(0.35);
  const [assistantWidth, setAssistantWidth] = useState(0.25);
  const [isDesktop, setIsDesktop] = useState(false);
  const initializationRef = useRef({});
  const layoutRef = useRef(null);
  const dragStateRef = useRef(null);
  const leftWidthRef = useRef(leftWidth);
  const assistantWidthRef = useRef(assistantWidth);

  const setCodeForLanguage = useCallback((lang, newCode) => {
    setCodeMap((prev) => {
      const normalizedLang = lang || "python";
      const nextCode = typeof newCode === "string" ? newCode : "";
      if (prev[normalizedLang] === nextCode) {
        return prev;
      }
      return { ...prev, [normalizedLang]: nextCode };
    });
  }, []);

  const assistantPanelClasses = `${assistantOpen ? "flex" : "hidden"} w-full flex-col border-t border-slate-700/60 bg-slate-900/40 xl:border-t-0 ${assistantOpen ? "xl:flex" : "xl:hidden"} xl:border-l`;
  const visibleAssistantPortion = isDesktop && assistantOpen ? assistantWidth : 0;
  const middlePortion = isDesktop
    ? Math.max(MIN_MIDDLE_WIDTH, 1 - leftWidth - visibleAssistantPortion)
    : 1;
  const leftPanelStyle = isDesktop
    ? {
        flexBasis: `${(leftWidth * 100).toFixed(2)}%`,
        maxWidth: `${(leftWidth * 100).toFixed(2)}%`,
        minWidth: 0,
        flexGrow: 0,
        flexShrink: 0,
      }
    : undefined;
  const middlePanelStyle = isDesktop
    ? {
        flexBasis: `${(middlePortion * 100).toFixed(2)}%`,
        maxWidth: `${(middlePortion * 100).toFixed(2)}%`,
        minWidth: 0,
        flexGrow: 0,
        flexShrink: 0,
      }
    : undefined;
  const assistantPanelStyle = isDesktop && assistantOpen
    ? {
        flexBasis: `${(assistantWidth * 100).toFixed(2)}%`,
        maxWidth: `${(assistantWidth * 100).toFixed(2)}%`,
        minWidth: 0,
        flexGrow: 0,
        flexShrink: 0,
      }
    : undefined;

  const selectedLanguage = useMemo(
    () => getLanguagePreset(language),
    [language]
  );

  useEffect(() => {
    if (typeof window === "undefined") return;
    const media = window.matchMedia("(min-width: 1280px)");
    const handleChange = () => setIsDesktop(media.matches);
    handleChange();
    media.addEventListener("change", handleChange);
    return () => media.removeEventListener("change", handleChange);
  }, []);

  useEffect(() => {
    if (typeof document === "undefined") {
      return undefined;
    }
    const previous = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => {
      document.body.style.overflow = previous;
    };
  }, []);

  useEffect(() => {
    leftWidthRef.current = leftWidth;
  }, [leftWidth]);

  useEffect(() => {
    assistantWidthRef.current = assistantWidth;
  }, [assistantWidth]);

  useEffect(() => {
    if (!problem?.function_templates) return;
    setFunctionTemplateState((prev) => {
      const entries = Object.entries(problem.function_templates || {});
      if (!entries.length) {
        return prev;
      }
      const next = { ...prev };
      let changed = false;
      entries.forEach(([lang, template]) => {
        if (!template) {
          return;
        }
        const normalized = lang.toLowerCase();
        const existing = next[normalized];
        if (existing?.template === template) {
          return;
        }
        next[normalized] = {
          ...(existing || {}),
          template,
          loading: false,
          error: null,
        };
        changed = true;
      });
      return changed ? next : prev;
    });
  }, [problem]);

  const storageKey = useCallback(
    (lang) => `algogenius:solve:${problem.id}:${lang}`,
    [problem.id]
  );

  // Load saved code or template
  useEffect(() => {
    if (typeof window === "undefined") return;
    if (initializationRef.current[language]) return;

    const saved = localStorage.getItem(storageKey(language));
    if (saved) {
      setCodeForLanguage(language, saved);
      initializationRef.current[language] = true;
      return;
    }

    const template = functionTemplateState[language]?.template;
    if (template) {
      setCodeForLanguage(language, template);
    } else {
      setCodeForLanguage(language, selectedLanguage.fallbackTemplate);
    }

    initializationRef.current[language] = true;
  }, [functionTemplateState, language, selectedLanguage.fallbackTemplate, setCodeForLanguage, storageKey]);

  // Keyboard shortcuts
  useEffect(() => {
    const handleShortcut = (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
        e.preventDefault();
        handleRun();
      }
    };

    window.addEventListener("keydown", handleShortcut);
    return () => window.removeEventListener("keydown", handleShortcut);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [code, language, testInput]);

  const fetchFunctionTemplate = useCallback(
    async (lang) => {
      const normalized = (lang || "python").toLowerCase();
      const entry = functionTemplateState[normalized];
      const now = Date.now();
      if (entry?.loading || entry?.template) {
        return;
      }
      if (entry?.cooldownUntil && entry.cooldownUntil > now) {
        return;
      }

      setFunctionTemplateState((prev) => ({
        ...prev,
        [normalized]: {
          ...(prev[normalized] || {}),
          loading: true,
          error: null,
        },
      }));

      try {
        const { data } = await api.get(
          `/problems/${problem.id}/function-template`,
          {
            params: { language: normalized },
          }
        );
        setFunctionTemplateState((prev) => ({
          ...prev,
          [normalized]: {
            template: data.template,
            loading: false,
            error: null,
            powered_by: data.powered_by,
          },
        }));
      } catch (err) {
        const message =
          err?.response?.data?.detail ||
          err?.message ||
          "Failed to load template.";
        setFunctionTemplateState((prev) => ({
          ...prev,
          [normalized]: {
            ...(prev[normalized] || {}),
            loading: false,
            error: message,
            cooldownUntil: now + 60_000,
          },
        }));
        toast.error(`Template error (${normalized.toUpperCase()}): ${message}`);
      }
    },
    [functionTemplateState, problem.id]
  );

  useEffect(() => {
    LANGUAGE_IDS.forEach((lang) => {
      fetchFunctionTemplate(lang);
    });
  }, [fetchFunctionTemplate]);

  const handleLanguageChange = useCallback(
    (newLang) => {
      setLanguage(newLang);
      fetchFunctionTemplate(newLang);
    },
    [fetchFunctionTemplate]
  );

  const handleCodeChange = useCallback(
    (newCode) => {
      setCodeForLanguage(language, newCode ?? "");
    },
    [language, setCodeForLanguage]
  );

  const handleInsertTemplate = useCallback(() => {
    const entry = functionTemplateState[language];
    const templateText = entry?.template;
    if (!templateText) {
      fetchFunctionTemplate(language);
      toast.info("Requesting function template...");
      return;
    }

    const shouldReplace =
      !code.trim() ||
      confirm("Replace the current code with the function template?");
    if (!shouldReplace) {
      return;
    }

    setCodeForLanguage(language, templateText);
    toast.success("Function template inserted into the editor.");
  }, [code, fetchFunctionTemplate, functionTemplateState, language, setCodeForLanguage]);

  const handleThemeChange = useCallback((newTheme) => {
    setTheme(newTheme);
  }, []);

  const applyExecutionResult = useCallback((data, intent) => {
    const status = normalizeStatus(
      data?.status || (intent === "submit" ? "SUBMITTED" : "COMPLETED")
    );
    setVerdict(status);
    setExecutionTime(
      data?.execution_time ??
        data?.runtime_ms ??
        data?.runtime ??
        data?.time ??
        null
    );
    setMemoryUsage(
      data?.memory_usage ?? data?.memory_kb ?? data?.memory ?? null
    );

    // Handle output - check both stdout and output fields
    const outputText = data?.stdout ?? data?.output ?? "";
    const errorText = data?.stderr ?? data?.error ?? "";

    setTestOutput(outputText);
    setDiagnostic(errorText);

    if (Number.isInteger(data?.failed_case)) {
      setFailedCaseDetails({
        index: data.failed_case,
        input: data?.failed_case_input || "",
        expected: data?.failed_case_expected_output || "",
      });
    } else {
      setFailedCaseDetails(null);
    }

    const message =
      data?.message ||
      (status === "AC"
        ? intent === "submit"
          ? "Accepted! Great job."
          : "Execution completed successfully."
        : status === "WA"
        ? "Wrong Answer"
        : status === "RE"
        ? "Runtime Error"
        : intent === "submit"
        ? "Submission processed."
        : "Execution finished.");

    if (status === "AC") {
      toast.success(message);
    } else if (status === "PENDING" || status === "IDLE") {
      toast.info(message);
    } else {
      toast.error(message);
    }
  }, []);

  const handleRun = useCallback(async () => {
    if (!code.trim()) {
      toast.error("Write your solution before running.");
      return;
    }

    setBusy(true);
    setVerdict("RUNNING");
    setExecutionTime(null);
    setMemoryUsage(null);
    setTestOutput("");
    setDiagnostic("");
    setFailedCaseDetails(null);

    try {
      const { data } = await api.post("/submissions/run", {
        problem_id: problem.id,
        language,
        code,
        stdin: testInput,
      });
      applyExecutionResult(data, "run");
    } catch (err) {
      const message =
        err?.response?.data?.detail ||
        err?.response?.data?.message ||
        err?.message ||
        "Failed to execute code.";
      setVerdict("RE");
      setDiagnostic(message);
      toast.error(message);
    } finally {
      setBusy(false);
    }
  }, [applyExecutionResult, code, language, problem.id, testInput]);

  const handleSubmit = useCallback(async () => {
    if (!code.trim()) {
      toast.error("Write your solution before submitting.");
      return;
    }

    setBusy(true);
    setVerdict("SUBMITTING");

    try {
      const { data } = await api.post("/submissions", {
        problem_id: problem.id,
        language,
        code,
      });
      applyExecutionResult(data, "submit");
    } catch (err) {
      const message =
        err?.response?.data?.detail ||
        err?.response?.data?.message ||
        err?.message ||
        "Submission failed.";
      setVerdict("RE");
      setDiagnostic(message);
      toast.error(message);
    } finally {
      setBusy(false);
    }
  }, [applyExecutionResult, code, language, problem.id]);

  const startResizeDrag = useCallback(
    (type, clientX) => {
      if (!isDesktop || !layoutRef.current) {
        return;
      }
      dragStateRef.current = {
        type,
        startX: clientX,
        containerWidth: layoutRef.current.getBoundingClientRect().width || 1,
        startLeft: leftWidthRef.current,
        startAssistant: assistantWidthRef.current,
      };
      document.body.style.userSelect = "none";
      document.body.style.cursor = "col-resize";
    },
    [isDesktop]
  );

  const stopResizeDrag = useCallback(() => {
    if (!dragStateRef.current) {
      return;
    }
    dragStateRef.current = null;
    document.body.style.removeProperty("user-select");
    document.body.style.removeProperty("cursor");
  }, []);

  const handlePointerMove = useCallback(
    (clientX) => {
      const state = dragStateRef.current;
      if (!state || !isDesktop) {
        return;
      }
      const { type, startX, containerWidth, startLeft, startAssistant } = state;
      if (!containerWidth) {
        return;
      }
      const deltaRatio = (clientX - startX) / containerWidth;

      if (type === "left") {
        const assistantPortion = assistantOpen ? assistantWidthRef.current : 0;
        const maxLeft = Math.max(
          MIN_LEFT_WIDTH,
          1 - assistantPortion - MIN_MIDDLE_WIDTH
        );
        const next = clamp(startLeft + deltaRatio, MIN_LEFT_WIDTH, maxLeft);
        setLeftWidth(next);
      } else if (type === "right" && assistantOpen) {
        const maxAssistant = Math.max(
          MIN_ASSISTANT_WIDTH,
          1 - leftWidthRef.current - MIN_MIDDLE_WIDTH
        );
        const next = clamp(
          startAssistant + deltaRatio,
          MIN_ASSISTANT_WIDTH,
          maxAssistant
        );
        setAssistantWidth(next);
      }
    },
    [assistantOpen, isDesktop]
  );

  useEffect(() => {
    const handleMouseMove = (event) => {
      if (!dragStateRef.current) {
        return;
      }
      handlePointerMove(event.clientX);
    };

    const handleTouchMove = (event) => {
      if (!dragStateRef.current || event.touches.length === 0) {
        return;
      }
      handlePointerMove(event.touches[0].clientX);
      event.preventDefault();
    };

    const cancelDrag = () => {
      stopResizeDrag();
    };

    window.addEventListener("mousemove", handleMouseMove);
    window.addEventListener("mouseup", cancelDrag);
    window.addEventListener("touchmove", handleTouchMove, { passive: false });
    window.addEventListener("touchend", cancelDrag);
    window.addEventListener("touchcancel", cancelDrag);

    return () => {
      window.removeEventListener("mousemove", handleMouseMove);
      window.removeEventListener("mouseup", cancelDrag);
      window.removeEventListener("touchmove", handleTouchMove);
      window.removeEventListener("touchend", cancelDrag);
      window.removeEventListener("touchcancel", cancelDrag);
      stopResizeDrag();
    };
  }, [handlePointerMove, stopResizeDrag]);

  useEffect(() => {
    if (!isDesktop) {
      stopResizeDrag();
    }
  }, [isDesktop, stopResizeDrag]);

  useEffect(() => {
    const assistantPortion = assistantOpen ? assistantWidth : 0;
    const maxLeft = Math.max(MIN_LEFT_WIDTH, 1 - assistantPortion - MIN_MIDDLE_WIDTH);
    setLeftWidth((prev) => {
      const next = clamp(prev, MIN_LEFT_WIDTH, maxLeft);
      return Math.abs(next - prev) < 0.0001 ? prev : next;
    });
  }, [assistantOpen, assistantWidth]);

  useEffect(() => {
    if (!assistantOpen) {
      stopResizeDrag();
      return;
    }
    const maxAssistant = Math.max(
      MIN_ASSISTANT_WIDTH,
      1 - leftWidth - MIN_MIDDLE_WIDTH
    );
    setAssistantWidth((prev) => {
      const next = clamp(prev, MIN_ASSISTANT_WIDTH, maxAssistant);
      return Math.abs(next - prev) < 0.0001 ? prev : next;
    });
  }, [assistantOpen, leftWidth, stopResizeDrag]);

  const handleProblemDeleted = useCallback(() => {
    toast.success("Problem deleted");
    router.push("/problems/list");
  }, [router]);

  return (
    <div className="flex h-[calc(100vh-var(--navbar-height,72px))] flex-col overflow-hidden bg-slate-950 text-slate-100">
      {/* Header */}
      <header className="flex items-center justify-between border-b border-slate-700/60 bg-slate-900/80 px-6 py-4 backdrop-blur">
        <div>
          <div className="text-xs uppercase tracking-wider text-slate-500">
            Problem
          </div>
          <h1 className="text-lg font-semibold text-slate-100">
            {problem.title}
          </h1>
        </div>
        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={() => setAssistantOpen((prev) => !prev)}
            className="rounded-lg border border-slate-700/70 px-4 py-2 text-xs font-semibold uppercase tracking-wide text-slate-200 transition hover:border-emerald-400 hover:text-emerald-200"
            aria-pressed={assistantOpen}
          >
            {assistantOpen ? "Hide Assistant" : "Show Assistant"}
          </button>
          {isAdmin && (
            <AdminProblemDeleteButton
              problemId={problem.id}
              title={problem.title}
              onDeleted={handleProblemDeleted}
            />
          )}
        </div>
      </header>

      {/* Main Content */}
      <div
        ref={layoutRef}
        className="flex flex-1 min-h-0 flex-col overflow-hidden xl:flex-row"
      >
        {/* Left Panel - Problem */}
        <div
          className="w-full border-b border-slate-700/60 bg-slate-900/40 xl:border-b-0 xl:border-r xl:flex-none xl:min-w-[240px] xl:min-h-0"
          style={leftPanelStyle}
        >
          <ProblemPanel
            problem={problem}
            functionTemplates={functionTemplateState}
            onProblemDeleted={handleProblemDeleted}
          />
        </div>

        {isDesktop && (
          <div
            className="hidden xl:flex w-3 cursor-col-resize items-stretch"
            role="separator"
            aria-label="Resize problem description panel"
            aria-orientation="vertical"
            onMouseDown={(event) => startResizeDrag("left", event.clientX)}
            onTouchStart={(event) => {
              startResizeDrag("left", event.touches[0].clientX);
              event.preventDefault();
            }}
          >
            <span className="mx-auto h-full w-px bg-slate-800/60" />
          </div>
        )}

        {/* Middle Panel - Editor + Console */}
        <div
          className="flex w-full flex-1 min-h-0 flex-col overflow-hidden xl:min-w-[320px]"
          style={middlePanelStyle}
        >
          <CodeEditor
            problemId={problem.id}
            language={language}
            code={code}
            theme={theme}
            onLanguageChange={handleLanguageChange}
            onCodeChange={handleCodeChange}
            onThemeChange={handleThemeChange}
            functionTemplate={functionTemplateState[language]?.template}
            templateLoading={functionTemplateState[language]?.loading}
            onInsertTemplate={handleInsertTemplate}
          />

          <ConsolePanel
            testInput={testInput}
            testOutput={testOutput}
            diagnostic={diagnostic}
            verdict={verdict}
            executionTime={executionTime}
            memoryUsage={memoryUsage}
            busy={busy}
            failedCaseDetails={failedCaseDetails}
            onTestInputChange={setTestInput}
            onRun={handleRun}
            onSubmit={handleSubmit}
          />
        </div>

        {assistantOpen && isDesktop && (
          <div
            className="hidden xl:flex w-3 cursor-col-resize items-stretch"
            role="separator"
            aria-label="Resize assistant panel"
            aria-orientation="vertical"
            onMouseDown={(event) => startResizeDrag("right", event.clientX)}
            onTouchStart={(event) => {
              startResizeDrag("right", event.touches[0].clientX);
              event.preventDefault();
            }}
          >
            <span className="mx-auto h-full w-px bg-slate-800/60" />
          </div>
        )}

        {/* Assistant Panel */}
        <div
          className={`${assistantPanelClasses} min-h-0`}
          aria-hidden={!assistantOpen}
          style={assistantPanelStyle}
        >
          <AssistantPanel
            problemId={problem.id}
            latestCode={code}
            onClose={() => setAssistantOpen(false)}
          />
        </div>
      </div>
    </div>
  );
}
