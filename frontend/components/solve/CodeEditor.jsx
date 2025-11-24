"use client";

import dynamic from "next/dynamic";
import { useState, useCallback, useEffect, useRef } from "react";
import { ActionButton } from "./SolveComponents";
import { LANGUAGE_PRESETS } from "./languagePresets";

const MonacoEditor = dynamic(() => import("@monaco-editor/react"), {
  ssr: false,
  loading: () => (
    <div className="flex h-full items-center justify-center text-sm text-slate-400">
      <div className="flex items-center gap-2">
        <div className="h-4 w-4 animate-spin rounded-full border-2 border-slate-600 border-t-indigo-500" />
        Loading editor...
      </div>
    </div>
  ),
});

const MIN_HEIGHT = 280;
const MAX_HEIGHT = 760;
const DEFAULT_EDITOR_HEIGHT = 420;

export default function CodeEditor({
  problemId,
  language,
  code,
  theme,
  onLanguageChange,
  onCodeChange,
  onThemeChange,
}) {
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [editorHeight, setEditorHeight] = useState(DEFAULT_EDITOR_HEIGHT);
  const resizeRef = useRef({
    active: false,
    startY: 0,
    startHeight: DEFAULT_EDITOR_HEIGHT,
  });
  const containerRef = useRef(null);

  const currentLanguage =
    LANGUAGE_PRESETS.find((opt) => opt.id === language) || LANGUAGE_PRESETS[0];

  // Autosave to localStorage
  useEffect(() => {
    const timeout = setTimeout(() => {
      if (typeof window !== "undefined" && code) {
        const key = `devarena:solve:${problemId}:${language}`;
        localStorage.setItem(key, code);
      }
    }, 500);

    return () => clearTimeout(timeout);
  }, [code, language, problemId]);

  const handleReset = useCallback(() => {
    if (confirm(`Reset ${currentLanguage.label} code to template?`)) {
      onCodeChange(currentLanguage.fallbackTemplate);
    }
  }, [currentLanguage, onCodeChange]);

  const handleCopy = useCallback(async () => {
    try {
      await navigator.clipboard.writeText(code);
      // Visual feedback handled by toast in parent
    } catch (err) {
      console.error("Copy failed", err);
    }
  }, [code]);

  const toggleFullscreen = useCallback(() => {
    if (!containerRef.current) return;

    if (!isFullscreen) {
      containerRef.current.requestFullscreen?.();
      setIsFullscreen(true);
    } else {
      document.exitFullscreen?.();
      setIsFullscreen(false);
    }
  }, [isFullscreen]);

  useEffect(() => {
    const handleFullscreenChange = () => {
      setIsFullscreen(Boolean(document.fullscreenElement));
    };

    document.addEventListener("fullscreenchange", handleFullscreenChange);
    return () =>
      document.removeEventListener("fullscreenchange", handleFullscreenChange);
  }, []);

  const startResize = useCallback(
    (clientY) => {
      resizeRef.current = {
        active: true,
        startY: clientY,
        startHeight: editorHeight,
      };
    },
    [editorHeight]
  );

  const handleMouseDown = useCallback(
    (e) => {
      e.preventDefault();
      startResize(e.clientY);
    },
    [startResize]
  );

  useEffect(() => {
    const handleMove = (e) => {
      if (!resizeRef.current.active) return;
      const delta = e.clientY - resizeRef.current.startY;
      const newHeight = Math.max(
        MIN_HEIGHT,
        Math.min(MAX_HEIGHT, resizeRef.current.startHeight + delta)
      );
      setEditorHeight(newHeight);
    };

    const handleUp = () => {
      resizeRef.current.active = false;
    };

    window.addEventListener("mousemove", handleMove);
    window.addEventListener("mouseup", handleUp);

    return () => {
      window.removeEventListener("mousemove", handleMove);
      window.removeEventListener("mouseup", handleUp);
    };
  }, []);

  return (
    <div
      ref={containerRef}
      className={`flex flex-col ${isFullscreen ? "h-screen bg-slate-950" : ""}`}
    >
      {/* Toolbar */}
      <div className="flex items-center justify-between border-b border-slate-700/60 bg-slate-900/60 px-4 py-2">
        <div className="flex items-center gap-2">
          {LANGUAGE_PRESETS.map((opt) => (
            <button
              key={opt.id}
              type="button"
              onClick={() => onLanguageChange(opt.id)}
              className={`flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-medium transition ${
                language === opt.id
                  ? "bg-indigo-600 text-white shadow-sm"
                  : "text-slate-400 hover:bg-slate-800 hover:text-slate-200"
              }`}
            >
              <span>{opt.icon}</span>
              {opt.label}
            </button>
          ))}
        </div>

        <div className="flex items-center gap-2">
          <select
            value={theme}
            onChange={(e) => onThemeChange(e.target.value)}
            className="rounded-lg border border-slate-700 bg-slate-800 px-3 py-1.5 text-xs text-slate-200 focus:border-indigo-500 focus:outline-none"
          >
            <option value="vs-dark">Dark</option>
            <option value="light">Light</option>
            <option value="hc-black">High Contrast</option>
          </select>

          <button
            type="button"
            onClick={handleCopy}
            className="rounded-lg p-2 text-slate-400 transition hover:bg-slate-800 hover:text-slate-200"
            title="Copy code"
          >
            <svg
              className="h-4 w-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"
              />
            </svg>
          </button>

          <button
            type="button"
            onClick={handleReset}
            className="rounded-lg p-2 text-slate-400 transition hover:bg-slate-800 hover:text-slate-200"
            title="Reset to template"
          >
            <svg
              className="h-4 w-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
              />
            </svg>
          </button>

          <button
            type="button"
            onClick={toggleFullscreen}
            className="rounded-lg p-2 text-slate-400 transition hover:bg-slate-800 hover:text-slate-200"
            title={isFullscreen ? "Exit fullscreen" : "Fullscreen"}
          >
            {isFullscreen ? (
              <svg
                className="h-4 w-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            ) : (
              <svg
                className="h-4 w-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4"
                />
              </svg>
            )}
          </button>
        </div>
      </div>

      {/* Editor */}
      <div className="relative overflow-hidden border-b border-slate-700/60 bg-slate-950">
        <MonacoEditor
          height={editorHeight}
          language={language === "cpp" ? "cpp" : language}
          theme={theme}
          value={code}
          onChange={(value) => onCodeChange(value ?? "")}
          options={{
            automaticLayout: true,
            fontSize: 14,
            fontLigatures: true,
            minimap: { enabled: false },
            scrollbar: {
              useShadows: false,
              verticalScrollbarSize: 8,
              horizontalScrollbarSize: 8,
            },
            lineNumbers: "on",
            renderLineHighlight: "all",
            cursorBlinking: "smooth",
            smoothScrolling: true,
            padding: { top: 16, bottom: 16 },
          }}
        />
      </div>

      {/* Resize Handle */}
      {!isFullscreen && (
        <div
          className="flex cursor-row-resize items-center justify-center border-b border-slate-700/60 bg-slate-900/40 py-1.5 transition hover:bg-slate-800/60"
          onMouseDown={handleMouseDown}
        >
          <div className="flex gap-1">
            <div className="h-0.5 w-8 rounded-full bg-slate-600" />
            <div className="h-0.5 w-8 rounded-full bg-slate-600" />
          </div>
        </div>
      )}
    </div>
  );
}
