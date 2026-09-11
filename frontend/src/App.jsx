import { useState, useRef, useEffect } from "react";
import "./App.css";
import airlockLogo from "./assets/airlock-logo.png";
import workbenchLight from "./assets/workbench-light.jpeg";
import workbenchDark from "./assets/workbench-dark.jpeg";

const PROCESSING_MESSAGES = ["Processing locally…", "Routing to the appropriate model…"];
const COMPOSER_MAX_HEIGHT = 168;

const EXAMPLES = [
  { icon: "doc", title: "Summarize a document", subtitle: "Analyze reports, PDFs, logs…" },
  { icon: "code", title: "Explain this code", subtitle: "Get clear, local explanations" },
  { icon: "image", title: "Analyze an image", subtitle: "Understand diagrams, charts…" },
];

const NAV_ITEMS = [
  { icon: "home", label: "Workbench" },
  { icon: "cube", label: "Model Hub" },
  { icon: "file", label: "Docs" },
];

function Icon({ name, className = "h-5 w-5" }) {
  const common = { className, viewBox: "0 0 24 24", fill: "none", stroke: "currentColor", strokeWidth: 1.8, strokeLinecap: "round", strokeLinejoin: "round" };
  switch (name) {
    case "home":
      return <svg {...common}><path d="M3 11.5 12 4l9 7.5" /><path d="M5.5 10v9a1 1 0 0 0 1 1h11a1 1 0 0 0 1-1v-9" /></svg>;
    case "cube":
      return <svg {...common}><path d="M12 3 4 7v10l8 4 8-4V7l-8-4Z" /><path d="M4 7l8 4 8-4M12 11v10" /></svg>;
    case "gear":
      return <svg {...common}><circle cx="12" cy="12" r="3" /><path d="M19.4 13.5a7.6 7.6 0 0 0 0-3l1.9-1.4-2-3.4-2.2.8a7.7 7.7 0 0 0-2.6-1.5L14 2h-4l-.5 2.5a7.7 7.7 0 0 0-2.6 1.5l-2.2-.8-2 3.4L4.6 10a7.6 7.6 0 0 0 0 3l-1.9 1.4 2 3.4 2.2-.8c.76.66 1.65 1.18 2.6 1.5L10 22h4l.5-2.5a7.7 7.7 0 0 0 2.6-1.5l2.2.8 2-3.4-1.9-1.5Z" /></svg>;
    case "monitor":
      return <svg {...common}><rect x="3" y="4" width="18" height="13" rx="1.5" /><path d="M8 21h8M12 17v4" /></svg>;
    case "file":
      return <svg {...common}><path d="M7 3h7l5 5v13a1 1 0 0 1-1 1H7a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1Z" /><path d="M14 3v5h5M9 12h6M9 16h6" /></svg>;
    case "lock":
      return <svg {...common}><rect x="5" y="11" width="14" height="9" rx="1.5" /><path d="M8 11V8a4 4 0 0 1 8 0v3" /></svg>;
    case "bolt":
      return <svg {...common}><path d="M13 2 4 14h6l-1 8 9-12h-6l1-8Z" /></svg>;
    case "box":
      return <svg {...common}><path d="M21 8 12 3 3 8l9 5 9-5Z" /><path d="M3 8v9l9 5 9-5V8M12 13v9" /></svg>;
    case "moon":
      return <svg {...common}><path d="M20 14.5A8.5 8.5 0 1 1 9.5 4a7 7 0 0 0 10.5 10.5Z" /></svg>;
    case "sun":
      return <svg {...common}><circle cx="12" cy="12" r="4.2" /><path d="M12 2.5v2M12 19.5v2M4.2 4.2l1.4 1.4M18.4 18.4l1.4 1.4M2.5 12h2M19.5 12h2M4.2 19.8l1.4-1.4M18.4 5.6l1.4-1.4" /></svg>;
    case "plus":
      return <svg {...common}><path d="M12 5v14M5 12h14" /></svg>;
    case "chevron":
      return <svg {...common} className={className}><path d="M6 9l6 6 6-6" /></svg>;
    case "sliders":
      return <svg {...common}><path d="M4 6h10M18 6h2M4 12h4M12 12h8M4 18h13M20 18h0" /><circle cx="16" cy="6" r="2" /><circle cx="8" cy="12" r="2" /><circle cx="17" cy="18" r="2" /></svg>;
    case "info":
      return <svg {...common}><circle cx="12" cy="12" r="9" /><path d="M12 11v5M12 8v.01" /></svg>;
    case "doc":
      return <svg {...common}><path d="M7 3h7l5 5v13a1 1 0 0 1-1 1H7a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1Z" /><path d="M9 13h6M9 17h6" /></svg>;
    case "code":
      return <svg {...common}><path d="m9 8-4 4 4 4M15 8l4 4-4 4" /></svg>;
    case "image":
      return <svg {...common}><rect x="3" y="4" width="18" height="16" rx="1.5" /><circle cx="8.5" cy="9.5" r="1.5" /><path d="m4 17 4.5-4.5a2 2 0 0 1 2.8 0L15 16l1.5-1.5a2 2 0 0 1 2.8 0L21 16" /></svg>;
    default:
      return null;
  }
}

export default function App() {
  const [messages, setMessages] = useState([]);
  const [prompt, setPrompt] = useState("");
  const [loading, setLoading] = useState(false);
  const [messageIndex, setMessageIndex] = useState(0);
  const [theme, setTheme] = useState("light");

  const nextIdRef = useRef(0);
  const bottomRef = useRef(null);
  const textareaRef = useRef(null);

  function nextId() {
    nextIdRef.current += 1;
    return nextIdRef.current;
  }
  
  const [sessions, setSessions] = useState([]);
  const [currentSessionId, setCurrentSessionId] = useState(null);
  const [attachment, setAttachment] = useState(null); // { path, filename }
  const fileInputRef = useRef(null);

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
  }, [theme]);

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

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages, loading]);

  useEffect(() => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = `${Math.min(el.scrollHeight, COMPOSER_MAX_HEIGHT)}px`;
  }, [prompt]);

    useEffect(() => {
    fetch("http://localhost:8000/sessions")
      .then((r) => r.json())
      .then(setSessions)
      .catch(() => {});
  }, []);

  async function refreshSessions() {
    try {
      const r = await fetch("http://localhost:8000/sessions");
      setSessions(await r.json());
    } catch {
      /* non-fatal — sidebar just won't update this cycle */
    }
  }

  async function loadSession(id) {
    const r = await fetch(`http://localhost:8000/sessions/${id}/messages`);
    const msgs = await r.json();
    setMessages(
      msgs.map((m) => ({
        id: nextId(),
        role: m.role,
        content: m.content,
        taskType: m.task_type,
        modelUsed: m.model_used,
        sources: m.sources ? JSON.parse(m.sources) : null,
      }))
    );
    setCurrentSessionId(id);
  }

  function startNewChat() {
    setMessages([]);
    setCurrentSessionId(null);
    setAttachment(null);
    setPrompt("");
  }

  async function handleFileSelect(e) {
    const file = e.target.files?.[0];
    if (!file) return;
    const formData = new FormData();
    formData.append("file", file);
    try {
      const res = await fetch("http://localhost:8000/upload", { method: "POST", body: formData });
      const data = await res.json();
      setAttachment({ path: data.path, filename: data.filename });
    } catch {
      setAttachment(null);
    }
    e.target.value = "";
  }

    async function submit(overridePrompt) {
    const trimmedPrompt = (overridePrompt ?? prompt).trim();
    if (!trimmedPrompt || loading) return;

    setMessages((prev) => [...prev, { id: nextId(), role: "user", content: trimmedPrompt }]);
    setPrompt("");
    setLoading(true);

    try {
      const res = await fetch("http://localhost:8000/task", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          prompt: trimmedPrompt,
          session_id: currentSessionId,
          attachment_path: attachment?.path || null,
        }),
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
        setCurrentSessionId(data.session_id);
        setAttachment(null);
        refreshSessions();
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

  function handleKeyDown(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      submit();
    }
  }

  const renderError = (detail) => {
    if (typeof detail === "string") return detail;
    if (Array.isArray(detail)) {
      return detail.map((err, idx) => (
        <div key={idx} className="mt-1.5 first:mt-0">
          {err.loc ? <span className="mr-1.5 font-mono text-xs opacity-75">{err.loc.join(" → ")}:</span> : null}
          <span>{err.msg}</span>
        </div>
      ));
    }
    return JSON.stringify(detail, null, 2);
  };

  const hasStarted = messages.length > 0 || loading;

  return (
    <main className="flex h-screen w-full font-sans text-ink overflow-hidden" style={{ backgroundColor: "var(--color-base)" }}>
      {/* Sidebar */}
      <aside className="nav-enter flex w-64 shrink-0 flex-col border-r px-4 py-5 z-20" style={{ backgroundColor: "var(--color-sidebar)", borderColor: "var(--color-border)" }}>
        <div className="flex items-center gap-2.5 px-1">
          <div className="logo-mark relative flex h-9 w-9 shrink-0 items-center justify-center overflow-hidden rounded-xl">
            <img src={airlockLogo} alt="Airlock AI logo" className="relative h-full w-full object-contain" draggable="false" />
          </div>
          <div className="leading-tight">
            <div className="text-[15px] font-semibold tracking-tight text-ink">Airlock</div>
            <div className="flex items-center gap-1.5 text-xs text-ink-muted">
              <span className="h-1.5 w-1.5 rounded-full" style={{ backgroundColor: "var(--color-accent)" }} />
              Local AI
            </div>
          </div>
        </div>

        <nav className="mt-8 flex flex-col gap-1">
          {NAV_ITEMS.map((item, idx) => (
            <button
              key={item.label}
              type="button"
              className="nav-item flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-colors"
              style={
                idx === 0
                  ? { backgroundColor: "var(--color-accent-soft)", color: "var(--color-accent-strong)" }
                  : { color: "var(--color-ink-muted)" }
              }
            >
              <Icon name={item.icon} className="h-[18px] w-[18px]" />
              {item.label}
            </button>
          ))}
        </nav>
        <div className="mt-6 flex items-center justify-between px-1">
          <span className="text-xs font-medium uppercase tracking-wide text-ink-faint">History</span>
          <button
            type="button"
            onClick={startNewChat}
            className="flex h-6 w-6 items-center justify-center rounded-full"
            style={{ backgroundColor: "var(--color-accent-soft)", color: "var(--color-accent-strong)" }}
            aria-label="New chat"
          >
            <Icon name="plus" className="h-3.5 w-3.5" />
          </button>
        </div>

        <div className="mt-2 flex-1 overflow-y-auto">
          {sessions.map((s) => (
            <button
              key={s.id}
              type="button"
              onClick={() => loadSession(s.id)}
              className="block w-full truncate rounded-lg px-2.5 py-2 text-left text-sm"
              style={
                s.id === currentSessionId
                  ? { backgroundColor: "var(--color-accent-soft)", color: "var(--color-accent-strong)" }
                  : { color: "var(--color-ink-muted)" }
              }
            >
              {s.title || "New chat"}
            </button>
          ))}
        </div>

        <div className="mt-auto">
          <div className="rounded-2xl border p-3.5" style={{ borderColor: "var(--color-border)", backgroundColor: "var(--color-panel)", boxShadow: "var(--shadow-card)" }}>
            <div className="flex items-center gap-2 text-sm font-medium text-ink">
              <span className="h-2 w-2 rounded-full" style={{ backgroundColor: "var(--color-accent)" }} />
              Local Mode
            </div>
            <div className="mt-0.5 text-xs text-ink-faint">No external calls</div>
            <div className="mt-3 flex flex-col gap-2 text-xs">
              <StatRow icon="cpu" label="CPU" value="12%" />
              <StatRow icon="ram" label="RAM" value="3.4 / 16 GB" />
              <StatRow icon="gpu" label="GPU" value="0%" />
            </div>
          </div>
          <div className="mt-3 px-1 text-xs text-ink-faint">Airlock AI v0.1.0</div>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="relative flex min-w-0 flex-1 flex-col h-full overflow-hidden">
        
        {/* Full-Bleed Background Image */}
        <div 
          className="hero-photo-scene" 
          style={{ backgroundImage: `url(${theme === "dark" ? workbenchDark : workbenchLight})` }}
        />

        {/* Top Header */}
        <header className="relative z-10 flex items-center justify-between gap-4 px-8 py-4 shrink-0">
          <div className="status-badge flex items-center gap-2 rounded-full border px-4 py-1.5 text-xs font-semibold shadow-sm" style={{ backgroundColor: "var(--color-panel)", borderColor: "rgba(139,197,63,0.4)", color: "var(--color-accent-strong)" }}>
            <Icon name="lock" className="h-3.5 w-3.5" />
            <span className="font-mono tracking-wide">AIR-GAPPED · LOCAL ONLY</span>
          </div>
          <div className="flex items-center gap-3">
            <button
              type="button"
              onClick={() => setTheme((t) => (t === "light" ? "dark" : "light"))}
              className="flex h-9 w-9 items-center justify-center rounded-full border transition shadow-sm"
              style={{ backgroundColor: "var(--color-panel)", borderColor: "var(--color-border-strong)", color: "var(--color-ink)" }}
            >
              <Icon name={theme === "light" ? "moon" : "sun"} className="h-4 w-4" />
            </button>
            <button
              type="button"
              aria-label="User Profile"
              className="flex h-9 w-9 items-center justify-center rounded-full border transition shadow-sm font-semibold text-xs"
              style={{ backgroundColor: "var(--color-panel)", borderColor: "var(--color-border-strong)", color: "var(--color-ink)" }}
            >
              U
            </button>
          </div>
        </header>

        {/* Scrollable Body Area */}
        <div className="relative z-10 flex-1 overflow-y-auto overflow-x-hidden w-full">
          {!hasStarted ? (
            <div className="flex min-h-full w-full relative pb-12">
              
              <div className="flex w-full max-w-[920px] flex-col justify-center px-8 py-6 sm:px-12">
                <h1 className="fade-in-up text-[48px] font-semibold leading-[1.08] tracking-tight text-ink drop-shadow-md">
                  Your Ideas.
                  <br />
                  <span style={{ color: "var(--color-accent)" }}>Your Machine.</span>
                </h1>
                <p className="fade-in-up delay-1 mt-4 max-w-lg text-base leading-relaxed text-ink-muted drop-shadow font-medium">
                  A private workspace for confidential industrial work.
                  <br />
                  Run powerful AI models locally, with complete control.
                </p>

                <div className="fade-in-up delay-3 composer-enter mt-8">
                  <div className="composer-card rounded-3xl border p-3.5 shadow-lg" style={{ backgroundColor: "var(--color-panel)", borderColor: "var(--color-border)"}}>
                    <textarea
                      ref={textareaRef}
                      rows={1}
                      className="w-full resize-none bg-transparent px-2 py-2 text-base text-ink outline-none placeholder:text-gray-400 dark:placeholder:text-gray-500"
                      placeholder="Ask anything…"
                      value={prompt}
                      onChange={(e) => setPrompt(e.target.value)}
                      onKeyDown={handleKeyDown}
                    />
                    <div className="mt-2 flex items-center justify-between px-1">
                      <div className="flex items-center gap-2">
                        <input ref={fileInputRef} type="file" onChange={handleFileSelect} className="hidden" />
                        <button
                          type="button"
                          onClick={() => fileInputRef.current?.click()}
                          className="send-button flex h-9 w-9 items-center justify-center rounded-xl border disabled:cursor-not-allowed disabled:opacity-40 shadow-sm"
                          style={{ borderColor: "var(--color-border-strong)", color: "var(--color-ink-muted)" }}
                          aria-label="Attach file"
                        >
                          <Icon name="plus" className="h-4 w-4" />
                        </button>
                      </div>
                      <div className="flex items-center gap-3">
                        <span className="hidden items-center gap-1 text-xs text-ink-faint sm:flex">
                          <Icon name="info" className="h-3.5 w-3.5" />
                          Shift + Enter for a new line
                        </span>
                        <button
                          type="button"
                          onClick={() => submit()}
                          disabled={!prompt.trim()}
                          className="send-button flex h-9 w-9 items-center justify-center rounded-full disabled:cursor-not-allowed disabled:opacity-40 shadow-sm"
                          style={{ backgroundColor: "var(--color-accent)", color: "var(--color-accent-ink)" }}
                        >
                          <svg viewBox="0 0 20 20" fill="none" className="h-4 w-4"><path d="M3 10h13M10 3l7 7-7 7" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" /></svg>
                        </button>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="fade-in-up delay-3 mt-6">
                  <p className="mb-2.5 text-sm font-medium text-ink-muted drop-shadow">Try an example</p>
                  <div className="flex flex-wrap gap-3">
                    {EXAMPLES.map((ex) => (
                      <button
                        key={ex.title}
                        type="button"
                        onClick={() => submit(ex.title)}
                        className="example-card flex items-center gap-3 rounded-2xl border px-4 py-3 text-left transition shadow-sm"
                        style={{ backgroundColor: "var(--color-panel)", borderColor: "var(--color-border)" }}
                      >
                        <span className="flex h-9 w-9 items-center justify-center rounded-full shrink-0" style={{ backgroundColor: "var(--color-panel-raised)", color: "var(--color-ink-muted)" }}>
                          <Icon name={ex.icon} className="h-4 w-4" />
                        </span>
                        <span>
                          <span className="block text-sm font-semibold text-ink">{ex.title}</span>
                          <span className="block text-xs text-ink-faint">{ex.subtitle}</span>
                        </span>
                      </button>
                    ))}
                  </div>
                </div>
              </div>

              {/* Right Side Overlays */}
              <div className="hidden flex-1 relative lg:block pointer-events-none">
                <div className="absolute right-10 top-6 font-mono text-xs uppercase tracking-widest text-white/95 drop-shadow-md">
                  <div>Local</div>
                  <div>Inference</div>
                  <div>Real</div>
                  <div>Impact</div>
                  <div className="mt-2 h-px w-8 bg-white/80" />
                </div>
              </div>
            </div>
          ) : (
            <div className="mx-auto flex max-w-3xl flex-col gap-5 py-6 px-6">
              {messages.map((message) =>
                message.role === "user" ? (
                  <div key={message.id} className="msg-user flex justify-end">
                    <div className="max-w-[80%] rounded-2xl rounded-tr-md px-4 py-2.5 text-sm leading-6 text-white shadow-sm" style={{ background: `linear-gradient(135deg, var(--color-accent-strong), var(--color-accent))` }}>
                      {message.content}
                    </div>
                  </div>
                ) : (
                  <div key={message.id} className="msg-assistant flex justify-start">
                    <div className="max-w-[88%] rounded-2xl rounded-tl-md border px-4 py-3.5 sm:max-w-[80%] shadow-sm" style={{ backgroundColor: "var(--color-panel)", borderColor: "var(--color-border)" }}>
                      {message.isError ? (
                        <div>
                          <p className="text-sm font-medium text-error">Request failed</p>
                          <div className="mt-1.5 text-sm leading-6 text-error/90">{renderError(message.content)}</div>
                        </div>
                      ) : (
                        <>
                          <p className="response-text whitespace-pre-wrap text-[15px] leading-7 text-ink">{message.content}</p>
                          <div className="mt-3 flex flex-wrap gap-2">
                            <span className="rounded-full px-2.5 py-1 font-mono text-xs font-medium" style={{ backgroundColor: "var(--color-accent-soft)", color: "var(--color-accent-strong)" }}>{message.taskType}</span>
                            <span className="rounded-full px-2.5 py-1 font-mono text-xs font-medium" style={{ backgroundColor: "var(--color-panel-raised)", color: "var(--color-ink-muted)" }}>{message.modelUsed}</span>
                          </div>
                          {Array.isArray(message.sources) && message.sources.length > 0 && (
                            <div className="source-expand mt-3 rounded-lg border p-3" style={{ backgroundColor: "var(--color-panel-raised)", borderColor: "var(--color-border)" }}>
                              <p className="mb-1.5 font-mono text-xs font-medium" style={{ color: "var(--color-accent-strong)" }}>Sources</p>
                              <ul className="flex flex-col gap-1">
                                {message.sources.map((source, idx) => {
                                  const label = typeof source === "string" ? source : source.title || source.url || JSON.stringify(source);
                                  return <li key={idx} className="text-sm text-ink-muted">{label}</li>;
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
                  <div className="max-w-[80%] rounded-2xl rounded-tl-md border px-4 py-3.5 shadow-sm" style={{ backgroundColor: "var(--color-panel)", borderColor: "var(--color-border)" }}>
                    <div className="flex items-center gap-3">
                      <span className="processing-ring" aria-hidden="true" />
                      <span className="processing-dots"><span /><span /><span /></span>
                      <span className="text-sm text-ink-muted">{PROCESSING_MESSAGES[messageIndex]}</span>
                    </div>
                  </div>
                </div>
              )}
              <div ref={bottomRef} />
            </div>
          )}
        </div>

        {/* Floating Composer */}
        {hasStarted && (
          <div className="relative z-10 px-6 pb-5 pt-2">
            <div className="composer-enter mx-auto max-w-3xl">
              <div className="flex items-end gap-2 rounded-3xl border p-2 shadow-sm" style={{ backgroundColor: "var(--color-panel)", borderColor: "var(--color-border)" }}>
                <input ref={fileInputRef} type="file" onChange={handleFileSelect} className="hidden" />
                <button
                  type="button"
                  onClick={() => fileInputRef.current?.click()}
                  className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl border"
                  style={{ borderColor: "var(--color-border-strong)", color: "var(--color-ink-muted)" }}
                  aria-label="Attach file"
                >
                  <Icon name="plus" className="h-4 w-4" />
                </button>
                {attachment && (
                  <div className="mb-2 flex items-center gap-2 rounded-lg px-2.5 py-1.5 text-xs" style={{ backgroundColor: "var(--color-panel-raised)" }}>
                    <span className="truncate text-ink-muted">{attachment.filename}</span>
                    <button type="button" onClick={() => setAttachment(null)} className="text-ink-faint hover:text-ink">✕</button>
                  </div>
                )}
                <textarea
                  ref={textareaRef}
                  className="max-h-[168px] min-h-[48px] flex-1 resize-none bg-transparent px-3 py-3 text-base leading-[1.6] text-ink outline-none placeholder:text-ink-faint disabled:opacity-60"
                  rows={1}
                  placeholder="Ask Airlock AI anything — it stays on this machine."
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  onKeyDown={handleKeyDown}
                  disabled={loading}
                />
                <button
                  type="button"
                  onClick={() => submit()}
                  disabled={loading || !prompt.trim()}
                  className="send-button flex h-10 w-10 shrink-0 items-center justify-center rounded-full disabled:cursor-not-allowed disabled:opacity-40 shadow-sm"
                  style={{ backgroundColor: "var(--color-accent)", color: "var(--color-accent-ink)" }}
                >
                  {loading ? (
                    <span className="h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white" />
                  ) : (
                    <svg viewBox="0 0 20 20" fill="none" className="h-4 w-4"><path d="M3 10h13M10 3l7 7-7 7" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" /></svg>
                  )}
                </button>
              </div>
              <div className="mt-2 flex items-center justify-between">
                <p className="font-mono text-[11px] text-ink-faint">Enter to send · Shift+Enter for a new line</p>
                <button type="button" onClick={clearWorkspace} className="text-xs font-medium text-ink-muted hover:text-ink">Clear</button>
              </div>
            </div>
          </div>
        )}
      </div>
    </main>
  );
}

function Feature({ icon, title, subtitle }) {
  return (
    <div className="flex items-center gap-3">
      <span className="flex h-10 w-10 items-center justify-center rounded-full shrink-0 shadow-sm" style={{ backgroundColor: "var(--color-accent)", color: "var(--color-accent-ink)" }}>
        <Icon name={icon} className="h-4 w-4" />
      </span>
      <span>
        <span className="block text-sm font-semibold text-ink drop-shadow">{title}</span>
        <span className="block text-xs text-ink-faint drop-shadow">{subtitle}</span>
      </span>
    </div>
  );
}

function IconPill({ children }) {
  return (
    <button type="button" className="flex h-8 w-8 items-center justify-center rounded-xl border transition hover:border-slate-400" style={{ backgroundColor: "var(--color-panel)", borderColor: "var(--color-border-strong)", color: "var(--color-ink-muted)" }}>
      {children}
    </button>
  );
}

function TextPill({ icon, label }) {
  return (
    <button type="button" className="flex items-center gap-1.5 rounded-xl border px-3 py-1.5 text-xs font-medium transition hover:border-slate-400" style={{ backgroundColor: "var(--color-panel)", borderColor: "var(--color-border-strong)", color: "var(--color-ink-muted)" }}>
      <Icon name={icon} className="h-3.5 w-3.5" />
      {label}
      <Icon name="chevron" className="h-3 w-3" />
    </button>
  );
}

function StatRow({ icon, label, value }) {
  return (
    <div className="flex items-center justify-between text-ink-muted text-xs">
      <span className="flex items-center gap-1.5">
        <Icon name={icon === "cpu" ? "monitor" : icon === "ram" ? "box" : "cube"} className="h-3.5 w-3.5" />
        {label}
      </span>
      <span className="font-medium text-ink">{value}</span>
    </div>
  );
}