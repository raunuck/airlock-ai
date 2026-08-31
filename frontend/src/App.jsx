import { useState } from "react";

function App() {
  const [prompt, setPrompt] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  async function submit() {
    setLoading(true);
    try {
      const res = await fetch("http://localhost:8000/task", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt }),
      });
      setResult(await res.json());
    } catch (err) {
      setResult({ error: "Backend unreachable — is uvicorn running?" });
    }
    setLoading(false);
  }

  return (
    <div className="p-6 max-w-xl mx-auto">
      <h1 className="text-xl font-semibold mb-4">Sovereign Workbench</h1>
      <textarea
        className="w-full border rounded p-2"
        rows={3}
        placeholder="Type a task..."
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
      />
      <button
        className="mt-2 px-4 py-2 bg-blue-600 text-white rounded disabled:opacity-50"
        onClick={submit}
        disabled={loading}
      >
        {loading ? "Sending..." : "Send"}
      </button>

      {result && (
        <div className="mt-4 p-3 border rounded bg-gray-50">
          {result.error ? (
            <p className="text-red-600">{result.error}</p>
          ) : (
            <>
              <span className="text-xs text-gray-500">Model: {result.model_used}</span>
              <p className="mt-1">{result.response}</p>
            </>
          )}
        </div>
      )}
    </div>
  );
}

export default App;