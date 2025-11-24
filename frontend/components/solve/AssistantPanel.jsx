"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { toast } from "@/lib/toast";
import api from "@/src/lib/api";

const MODES = [
  { id: "hint", label: "Hints" },
  { id: "explain", label: "Explain" },
  { id: "debug", label: "Debug" },
];

const CODE_CONTEXT_LIMIT = 8000;

const Paragraph = ({ children }) => (
  <div className="mb-2 text-sm leading-relaxed text-white/90 last:mb-0">
    {children}
  </div>
);

const MARKDOWN_COMPONENTS = {
  p: Paragraph,
  ul: ({ children }) => (
    <ul className="mb-2 list-disc pl-5 text-sm text-white/80">{children}</ul>
  ),
  ol: ({ children }) => (
    <ol className="mb-2 list-decimal pl-5 text-sm text-white/80">{children}</ol>
  ),
  li: ({ children }) => <li className="mb-1">{children}</li>,
  strong: ({ children }) => <strong className="font-semibold">{children}</strong>,
  pre: ({ children }) => (
    <pre className="mb-2 overflow-auto rounded-lg bg-slate-900/80 p-3 text-xs text-emerald-50">
      {children}
    </pre>
  ),
  code: ({ inline, className, children }) => {
    if (inline) {
      return (
        <code className="rounded bg-slate-900/70 px-1 py-0.5 text-[0.85rem] text-emerald-200">
          {children}
        </code>
      );
    }
    const mergedClass = ["text-xs", "text-emerald-50", "font-mono", className]
      .filter(Boolean)
      .join(" ");
    return <code className={mergedClass}>{children}</code>;
  },
  a: ({ href, children }) => (
    <a
      href={href}
      target="_blank"
      rel="noreferrer"
      className="text-emerald-300 underline underline-offset-2"
    >
      {children}
    </a>
  ),
};

function trimCodeContext(code) {
  if (!code) return undefined;
  if (code.length <= CODE_CONTEXT_LIMIT) {
    return code;
  }
  return code.slice(code.length - CODE_CONTEXT_LIMIT);
}

export default function AssistantPanel({ problemId, latestCode, onClose }) {
  const [mode, setMode] = useState("hint");
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState(() => [
    {
      id: "welcome",
      role: "assistant",
      content:
        "Hi! I can nudge you with hints, deeper explanations, or help debug your code. Ask anything about this problem when you're ready.",
      poweredBy: null,
      pending: false,
    },
  ]);
  const [includeCode, setIncludeCode] = useState(false);
  const [sending, setSending] = useState(false);
  const scrollRef = useRef(null);
  const storageKey = useMemo(
    () => `devarena:assistant:${problemId}`,
    [problemId]
  );

  const canSend = input.trim().length > 0 && !sending;
  const hasCodeContext = useMemo(
    () => Boolean(latestCode && latestCode.trim()),
    [latestCode]
  );

  useEffect(() => {
    if (!hasCodeContext && includeCode) {
      setIncludeCode(false);
    }
  }, [hasCodeContext, includeCode]);

  useEffect(() => {
    if (!scrollRef.current) return;
    scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
  }, [messages]);

  useEffect(() => {
    if (typeof window === "undefined") {
      return;
    }
    try {
      const raw = localStorage.getItem(storageKey);
      if (!raw) {
        return;
      }
      const parsed = JSON.parse(raw);
      if (Array.isArray(parsed?.messages) && parsed.messages.length) {
        setMessages(parsed.messages);
      }
    } catch (err) {
      console.warn("Failed to load assistant history", err);
    }
  }, [storageKey]);

  useEffect(() => {
    if (typeof window === "undefined") {
      return;
    }
    try {
      const safeMessages = messages.slice(-40);
      localStorage.setItem(storageKey, JSON.stringify({ messages: safeMessages }));
    } catch (err) {
      console.warn("Failed to persist assistant history", err);
    }
  }, [messages, storageKey]);

  const appendMessage = useCallback((message) => {
    setMessages((prev) => [...prev, message]);
  }, []);

  const updateMessage = useCallback((id, patch) => {
    setMessages((prev) => prev.map((msg) => (msg.id === id ? { ...msg, ...patch } : msg)));
  }, []);

  const removeMessage = useCallback((id) => {
    setMessages((prev) => prev.filter((msg) => msg.id !== id));
  }, []);

  const handleSend = useCallback(async () => {
    const question = input.trim();
    if (!question) {
      return;
    }

    const userMessage = {
      id: `user-${Date.now()}`,
      role: "user",
      content: question,
      pending: false,
    };

    const placeholderId = `assistant-${Date.now()}`;

    appendMessage(userMessage);
    appendMessage({ id: placeholderId, role: "assistant", content: "", pending: true });
    setInput("");
    setSending(true);

    const payload = {
      message: question,
      mode,
    };

    if (includeCode && hasCodeContext) {
      payload.code_context = trimCodeContext(latestCode.trim());
    }

    try {
      const { data } = await api.post(`/problems/${problemId}/assistant`, payload);
      updateMessage(placeholderId, {
        content: data?.reply?.trim() || "I couldn't generate a reply this time.",
        poweredBy: data?.powered_by || null,
        pending: false,
      });
    } catch (err) {
      const detail =
        err?.response?.data?.detail || err?.message || "Assistant request failed.";
      removeMessage(placeholderId);
      toast.error(detail);
      appendMessage({
        id: `assistant-error-${Date.now()}`,
        role: "assistant",
        content: "Something went wrong while reaching the assistant. Please try again.",
        poweredBy: null,
        pending: false,
      });
    } finally {
      setSending(false);
    }
  }, [appendMessage, hasCodeContext, includeCode, input, latestCode, mode, problemId, removeMessage, updateMessage]);

  const handleKeyDown = useCallback(
    (event) => {
      if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        if (canSend) {
          handleSend();
        }
      }
    },
    [canSend, handleSend]
  );

  const assistantStatus = sending ? "Thinking..." : null;

  return (
    <div className="flex h-full flex-col rounded-3xl border border-white/10 bg-white/5 shadow-2xl shadow-black/40 backdrop-blur">
      <div className="flex items-center justify-between border-b border-white/5 px-4 py-3">
        <div>
          <div className="text-xs uppercase tracking-[0.4em] text-white/50">Assistant</div>
          <p className="text-sm text-white/80">
            {assistantStatus || "Ask for hints, explanations, or debugging tips."}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <div className="flex gap-1 rounded-full border border-white/10 bg-white/5 p-1">
            {MODES.map((option) => (
              <button
                key={option.id}
                type="button"
                className={`rounded-full px-3 py-1 text-xs font-semibold transition ${
                  option.id === mode
                    ? "bg-gradient-to-r from-blue-500 via-indigo-500 to-purple-500 text-white"
                    : "text-white/60 hover:text-white"
                }`}
                onClick={() => setMode(option.id)}
              >
                {option.label}
              </button>
            ))}
          </div>
          {typeof onClose === "function" && (
            <button
              type="button"
              onClick={onClose}
              className="rounded-full border border-white/10 px-3 py-1 text-xs font-semibold text-white/70 transition hover:border-white/30 hover:text-white"
            >
              Close
            </button>
          )}
        </div>
      </div>

      <div className="flex-1 overflow-y-auto px-4 py-3" ref={scrollRef}>
        <div className="space-y-4 text-sm">
          {messages.map((message) => (
            <div key={message.id} className="flex flex-col gap-1">
              <div
                className={`w-fit max-w-full rounded-2xl px-3 py-2 text-sm shadow-lg shadow-black/20 ${
                  message.role === "user"
                    ? "self-end bg-gradient-to-r from-blue-500/30 to-purple-500/30 text-white"
                    : "self-start border border-white/10 bg-white/5 text-white"
                }`}
              >
                {message.pending ? (
                  <span className="text-white/60">...thinking</span>
                ) : (
                  <ReactMarkdown
                    remarkPlugins={[remarkGfm]}
                    components={MARKDOWN_COMPONENTS}
                  >
                    {message.content}
                  </ReactMarkdown>
                )}
              </div>
              {message.poweredBy && message.role === "assistant" && !message.pending && (
                <span className="text-[10px] uppercase tracking-[0.3em] text-white/40">
                  Powered by {message.poweredBy}
                </span>
              )}
            </div>
          ))}
        </div>
      </div>

      <div className="border-t border-white/5 p-4">
        <textarea
          value={input}
          onChange={(event) => setInput(event.target.value)}
          onKeyDown={handleKeyDown}
          rows={3}
          placeholder="Ask your question..."
          className="mb-3 w-full rounded-2xl border border-white/10 bg-white/5 p-3 text-sm text-white placeholder:text-white/40 focus:border-blue-400 focus:outline-none"
          disabled={sending}
        />
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <label className="flex items-center gap-2 text-xs text-white/60">
            <input
              type="checkbox"
              className="h-4 w-4 rounded border-white/20 bg-slate-900 text-blue-400"
              checked={includeCode && hasCodeContext}
              onChange={(event) => setIncludeCode(event.target.checked)}
              disabled={!hasCodeContext}
            />
            Share current code snippet
          </label>
          <button
            type="button"
            onClick={handleSend}
            disabled={!canSend}
            className={`rounded-full px-5 py-2 text-sm font-semibold transition ${
              canSend
                ? "bg-gradient-to-r from-emerald-400 to-green-500 text-slate-900 shadow-lg shadow-emerald-500/30 hover:scale-[1.02]"
                : "bg-white/10 text-white/40"
            }`}
          >
            {sending ? "Sending..." : "Send"}
          </button>
        </div>
      </div>
    </div>
  );
}
