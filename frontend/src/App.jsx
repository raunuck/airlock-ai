import { useState } from "react";

function App() {
  const [prompt, setPrompt] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  async function submit() {
    const trimmedPrompt = prompt.trim();

    if (!trimmedPrompt || loading) {
      return;
    }

    setLoading(true);
    setResult(null);

    try {
      const res = await fetch("http://localhost:8000/task", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt: trimmedPrompt }),
      });

      const data = await res.json();

      if (!res.ok) {
        setResult({
          detail: data.detail || "An error occurred",
        });
      } else {
        setResult(data);
      }
    } catch (err) {
      setResult({
        detail: "Backend unreachable — is uvicorn running?",
      });
    }

    setLoading(false);
  }

  function clearWorkspace() {
    setPrompt("");
    setResult(null);
  }

  return (
    <main className="min-h-screen bg-slate-950 px-4 py-6 text-slate-100 sm:px-6">
      <div className="mx-auto flex max-w-5xl flex-col gap-6">
        <header className="flex flex-col gap-4 border-b border-slate-800 pb-5 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p className="mb-1 text-sm font-medium text-cyan-400">
              Airlock AI
            </p>

            <h1 className="text-2xl font-semibold tracking-tight sm:text-3xl">
              Sovereign Workbench
            </h1>

            <p className="mt-2 max-w-2xl text-sm text-slate-400">
              A private workspace for confidential industrial tasks using
              locally hosted AI models.
            </p>
          </div>

          <div className="flex w-fit items-center gap-2 rounded-full border border-emerald-800 bg-emerald-950/40 px-3 py-2 text-sm text-emerald-300">
            <span className="h-2 w-2 rounded-full bg-emerald-400" />
            Local only
          </div>
        </header>

        <section className="grid gap-6 lg:grid-cols-[1fr_1.2fr]">
          <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5 shadow-xl">
            <div className="mb-4">
              <h2 className="text-lg font-semibold">Create a task</h2>
              <p className="mt-1 text-sm text-slate-400">
                Enter a question, coding request, or document-related task.
              </p>
            </div>

            <textarea
              className="min-h-48 w-full resize-y rounded-xl border border-slate-700 bg-slate-950 p-4 text-sm text-slate-100 outline-none transition placeholder:text-slate-500 focus:border-cyan-500 focus:ring-2 focus:ring-cyan-500/20"
              rows={7}
              placeholder="Example: Debug this code: print(hello world)"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              disabled={loading}
            />

            <div className="mt-4 flex flex-col gap-3 sm:flex-row">
              <button
                className="rounded-xl bg-cyan-500 px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-cyan-400 disabled:cursor-not-allowed disabled:opacity-50"
                onClick={submit}
                disabled={loading || !prompt.trim()}
              >
                {loading ? "Processing..." : "Run task"}
              </button>

              <button
                className="rounded-xl border border-slate-700 px-5 py-3 text-sm font-medium text-slate-300 transition hover:border-slate-500 hover:text-white disabled:cursor-not-allowed disabled:opacity-50"
                onClick={clearWorkspace}
                disabled={loading && !result}
              >
                Clear
              </button>
            </div>

            <p className="mt-4 text-xs text-slate-500">
              Requests are sent to your locally running backend.
            </p>
          </div>

          <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5 shadow-xl">
            <div className="mb-4 flex items-center justify-between gap-3">
              <div>
                <h2 className="text-lg font-semibold">Task result</h2>
                <p className="mt-1 text-sm text-slate-400">
                  The selected model and generated response will appear here.
                </p>
              </div>

              {loading && (
                <span className="rounded-full bg-cyan-950 px-3 py-1 text-xs text-cyan-300">
                  Working
                </span>
              )}
            </div>

            {!result && !loading && (
              <div className="flex min-h-64 items-center justify-center rounded-xl border border-dashed border-slate-700 px-6 text-center">
                <div>
                  <p className="text-sm font-medium text-slate-300">
                    No result yet
                  </p>
                  <p className="mt-2 text-sm text-slate-500">
                    Submit a task to see the model response.
                  </p>
                </div>
              </div>
            )}

            {loading && (
              <div className="flex min-h-64 items-center justify-center rounded-xl border border-slate-700 bg-slate-950/50">
                <div className="text-center">
                  <div className="mx-auto mb-3 h-8 w-8 animate-spin rounded-full border-2 border-slate-700 border-t-cyan-400" />
                  <p className="text-sm text-slate-300">
                    Waiting for the local model...
                  </p>
                </div>
              </div>
            )}

            {result && !loading && (
              <div className="rounded-xl border border-slate-700 bg-slate-950 p-4">
                {result.detail ? (
                  <div className="rounded-lg border border-red-900 bg-red-950/40 p-4">
                    <p className="text-sm font-medium text-red-300">
                      Request failed
                    </p>
                    <p className="mt-2 whitespace-pre-wrap text-sm text-red-200">
                      {result.detail}
                    </p>
                  </div>
                ) : (
                  <>
                    <div className="mb-4 flex flex-wrap gap-2">
                      <span className="rounded-full bg-cyan-950 px-3 py-1 text-xs font-medium text-cyan-300">
                        Task: {result.task_type}
                      </span>

                      <span className="rounded-full bg-slate-800 px-3 py-1 text-xs font-medium text-slate-300">
                        Model: {result.model_used}
                      </span>
                    </div>

                    <div className="border-t border-slate-800 pt-4">
                      <p className="whitespace-pre-wrap text-sm leading-7 text-slate-200">
                        {result.response}
                      </p>
                    </div>
                  </>
                )}
              </div>
            )}
          </div>
        </section>
      </div>
    </main>
  );
}

export default App;