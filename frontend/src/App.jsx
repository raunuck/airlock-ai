import { useState, useRef, useEffect } from "react";
import "./App.css";
import airlockLogo from "./assets/airlock-logo.png";

const PROCESSING_MESSAGES = ["Processing locally…", "Routing to the appropriate model…"];
const COMPOSER_MAX_HEIGHT = 168;

function App() {
  const [messages, setMessages] = useState([]);
  const [prompt, setPrompt] = useState("");
  const [loading, setLoading] = useState(false);
  const [messageIndex, setMessageIndex] = useState(0);

  const nextIdRef = useRef(0);
  const bottomRef = useRef(null);
  const textareaRef = useRef(null);

  function nextId() {
    nextIdRef.current += 1;
    return nextIdRef.current;
  }

  // Cycle the honest "what's happening" copy while waiting on the backend.
  // Text only - never implies a step count or a fake progress percentage.
  useEffect(() => {
    if (!loading) {
      setMessageIndex(0);
      return;
    }
    const interval = setInterval(() => {
      setMessageIndex((i) => (i + 1) % PROCESSING_MESSAGES.length);
    }, 2000);
    return () => clearInterval(interval);
  }, [loading]);

  // Keep the newest message in view as the conversation grows.
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages, loading]);

  // Let the composer grow with multi-line input, capped at COMPOSER_MAX_HEIGHT,
  // then hand off to internal scrolling so the shell stays compact.
  useEffect(() => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = `${Math.min(el.scrollHeight, COMPOSER_MAX_HEIGHT)}px`;
  }, [prompt]);

  async function submit() {
    const trimmedPrompt = prompt.trim();

    if (!trimmedPrompt || loading) {
      return;
    }

    setMessages((prev) => [...prev, { id: nextId(), role: "user", content: trimmedPrompt }]);
    setPrompt("");
    setLoading(true);

    try {
      const res = await fetch("http://localhost:8000/task", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt: trimmedPrompt }),
      });

      const data = await res.json();

      if (!res.ok) {
        setMessages((prev) => [
          ...prev,
          { id: nextId(), role: "assistant", isError: true, content: data.detail || "An error occurred" },
        ]);
      } else {
        setMessages((prev) => [
          ...prev,
          {
            id: nextId(),
            role: "assistant",
            content: data.response,
            taskType: data.task_type,
            modelUsed: data.model_used,
            sources: data.sources,
          },
        ]);
      }
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { id: nextId(), role: "assistant", isError: true, content: "Backend unreachable — is uvicorn running?" },
      ]);
    }

    setLoading(false);
  }

  function clearWorkspace() {
    setMessages([]);
    setPrompt("");
  }

  // Enter sends, Shift+Enter inserts a new line - the convention this
  // kind of interface is expected to follow.
  function handleKeyDown(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      submit();
    }
  }

  // Safely format error details whether they are strings, objects, or validation arrays
  const renderError = (detail) => {
    if (typeof detail === "string") return detail;
    if (Array.isArray(detail)) {
      return detail.map((err, idx) => (
        <div key={idx} className="mt-1.5 first:mt-0">
          {err.loc ? (
            <span className="mr-1.5 font-mono text-xs text-error/70">
              {err.loc.join(" → ")}:
            </span>
          ) : null}
          <span>{err.msg}</span>
        </div>
      ));
    }
    return JSON.stringify(detail, null, 2);
  };

  const hasStarted = messages.length > 0 || loading;

  return (
    <main className="relative flex h-screen flex-col overflow-hidden font-sans text-ink">
      {/* ---------- Ambient background ---------- */}
      <div className="airlock-bg" aria-hidden="true">
        <div className="glow-wash" />
        <div className="light-streaks" />
      </div>

      {/* ---------- Header ---------- */}
      <header className="nav-enter relative z-10 border-b border-border/70">
        <div className="mx-auto flex max-w-3xl items-center justify-between gap-4 px-4 py-4 sm:px-6">
          <div className="fade-in-up flex items-center gap-2.5">
            <div className="logo-mark relative flex h-9 w-9 shrink-0 items-center justify-center overflow-hidden rounded-xl">
              <span className="absolute inset-0 rounded-xl bg-accent/20 blur-md" aria-hidden="true" />
              <img
                src={airlockLogo}
                alt="Airlock AI logo"
                className="relative h-full w-full object-contain"
                draggable="false"
              />
            </div>
            <span className="text-sm font-semibold tracking-tight text-ink sm:text-[15px]">Airlock AI</span>
          </div>

          <div className="flex items-center gap-3">
            {hasStarted && (
              <button
                type="button"
                onClick={clearWorkspace}
                className="rounded-full border border-border-strong px-3 py-1.5 text-xs font-medium text-ink-muted transition hover:border-ink-faint hover:text-ink"
              >
                Clear
              </button>
            )}

            <div className="status-badge fade-in-up delay-1 flex items-center gap-2 rounded-full border px-3 py-1.5 text-xs font-medium text-ok">
              <span className="status-dot-ring">
                <span className="status-pulse h-1.5 w-1.5 rounded-full bg-ok" />
              </span>
              <span className="hidden font-mono tracking-wide sm:inline">AIR-GAPPED · LOCAL ONLY</span>
              <span className="font-mono tracking-wide sm:hidden">LOCAL</span>
            </div>
          </div>
        </div>
        <div className="scan-seam" aria-hidden="true" />
      </header>

      {/* ---------- Conversation area ---------- */}
      <div className="relative z-10 flex-1 overflow-y-auto">
        <div className="mx-auto flex min-h-full max-w-3xl flex-col px-4 sm:px-6">
          {!hasStarted ? (
            <div className="flex flex-1 flex-col items-center justify-center py-10 text-center">
              <p className="fade-in-up delay-1 font-mono text-xs uppercase tracking-widest text-ink-faint">
                Local inference · zero external calls
              </p>
              <h1 className="fade-in-up delay-2 mt-4 max-w-xl text-3xl font-semibold leading-tight tracking-tight text-ink sm:text-4xl">
                A private workbench for confidential industrial work.
              </h1>
              <p className="fade-in-up delay-3 mt-3 max-w-md text-base leading-relaxed text-ink-muted">
                Every prompt is handled entirely on this machine, by locally hosted
                models. Nothing you submit here ever leaves the network.
              </p>
            </div>
          ) : (
            <div className="flex flex-1 flex-col gap-5 py-6">
              {messages.map((message) =>
                message.role === "user" ? (
                  <div key={message.id} className="msg-user flex justify-end">
                    <div className="max-w-[80%] rounded-2xl rounded-tr-md bg-gradient-to-br from-indigo/90 to-accent-strong/80 px-4 py-2.5 text-sm leading-6 text-white shadow-[0_8px_24px_-12px_rgba(56,189,248,0.5)]">
                      {message.content}
                    </div>
                  </div>
                ) : (
                  <div key={message.id} className="msg-assistant flex justify-start">
                    <div className="max-w-[88%] rounded-2xl rounded-tl-md border border-border bg-panel/80 px-4 py-3.5 sm:max-w-[80%]">
                      {message.isError ? (
                        <div>
                          <p className="text-sm font-medium text-error">Request failed</p>
                          <div className="mt-1.5 text-sm leading-6 text-error/90">
                            {renderError(message.content)}
                          </div>
                        </div>
                      ) : (
                        <>
                          <p className="response-text whitespace-pre-wrap text-[15px] leading-7 text-ink">
                            {message.content}
                          </p>

                          <div className="mt-3 flex flex-wrap gap-2">
                            <span className="badge-pop delay-1 rounded-full bg-accent/10 px-2.5 py-1 font-mono text-xs font-medium text-accent">
                              {message.taskType}
                            </span>
                            <span className="badge-pop delay-2 rounded-full bg-panel-raised px-2.5 py-1 font-mono text-xs font-medium text-ink-muted">
                              {message.modelUsed}
                            </span>
                          </div>

                          {Array.isArray(message.sources) && message.sources.length > 0 && (
                            <div className="source-expand mt-3 rounded-lg border border-violet/25 bg-violet/[0.08] p-3">
                              <p className="mb-1.5 font-mono text-xs font-medium text-violet">Sources</p>
                              <ul className="flex flex-col gap-1">
                                {message.sources.map((source, idx) => {
                                  const label =
                                    typeof source === "string"
                                      ? source
                                      : source.title || source.url || JSON.stringify(source);
                                  const url = typeof source === "object" ? source.url : null;

                                  return (
                                    <li key={idx} className="text-sm">
                                      {url ? (
                                        <a
                                          href={url}
                                          target="_blank"
                                          rel="noreferrer"
                                          className="text-violet underline decoration-violet/30 underline-offset-2 transition hover:decoration-violet"
                                        >
                                          {label}
                                        </a>
                                      ) : (
                                        <span className="text-ink-muted">{label}</span>
                                      )}
                                    </li>
                                  );
                                })}
                              </ul>
                            </div>
                          )}
                        </>
                      )}
                    </div>
                  </div>
                )
              )}

              {loading && (
                <div className="msg-assistant flex justify-start" aria-live="polite">
                  <div className="max-w-[80%] rounded-2xl rounded-tl-md border border-border bg-panel/80 px-4 py-3.5">
                    <div className="flex items-center gap-3">
                      <span className="processing-ring" aria-hidden="true" />
                      <span className="processing-dots">
                        <span />
                        <span />
                        <span />
                      </span>
                      <span className="text-sm text-ink-muted">{PROCESSING_MESSAGES[messageIndex]}</span>
                    </div>
                    <div className="scan-bar mt-2.5" />
                  </div>
                </div>
              )}

              <div ref={bottomRef} />
            </div>
          )}
        </div>
      </div>

      {/* ---------- Composer ---------- */}
      <div className="relative z-10 px-4 pb-5 pt-2 sm:px-6 sm:pb-6">
        <div className="composer-enter mx-auto max-w-3xl">
          <div className="composer-glow flex items-end gap-2 p-2 sm:p-2.5">
            <textarea
              ref={textareaRef}
              className="composer-input max-h-[168px] min-h-[48px] flex-1 resize-none bg-transparent px-3 py-3 text-base leading-[1.6] text-ink outline-none placeholder:text-ink-faint disabled:opacity-60 sm:text-lg"
              style={{ caretColor: "var(--color-accent)" }}
              rows={1}
              placeholder="Ask Airlock AI anything — it stays on this machine."
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={loading}
            />

            <button
              type="button"
              onClick={submit}
              disabled={loading || !prompt.trim()}
              aria-label="Run task"
              className="send-button group flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-indigo to-accent text-accent-ink disabled:cursor-not-allowed disabled:opacity-40 disabled:hover:brightness-100"
            >
              {loading ? (
                <span className="h-4 w-4 animate-spin rounded-full border-2 border-accent-ink/30 border-t-accent-ink" />
              ) : (
                <svg
                  viewBox="0 0 20 20"
                  fill="none"
                  className="send-icon h-4.5 w-4.5 transition-transform duration-300 ease-out group-hover:translate-x-0.5"
                  aria-hidden="true"
                >
                  <path d="M3 10h13M10 3l7 7-7 7" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
              )}
            </button>
          </div>

          <p className="mt-2 text-center font-mono text-[11px] text-ink-faint">
            Enter to send · Shift+Enter for a new line · POST /task
          </p>
        </div>
      </div>
    </main>
  );
}

export default App;
