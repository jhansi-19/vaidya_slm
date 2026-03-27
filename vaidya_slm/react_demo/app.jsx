const { useState } = React;

function App() {
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  const API_BASE = "http://127.0.0.1:8005";

  async function submitQuery(e) {
    e.preventDefault();
    if (!text.trim()) {
      setError("Please enter symptoms before analyzing.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const response = await fetch(`${API_BASE}/infer`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: text.trim(), language: "en" }),
      });

      if (!response.ok) {
        throw new Error(`Server returned ${response.status}`);
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(`Request failed: ${err.message}`);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="page">
      <div className="card">
        <h1>Vaidya SLM</h1>
        <p className="subtitle">Checkpoint 1 React Demo: Text Query {"->"} AI Response</p>

        <form onSubmit={submitQuery}>
          <label>Symptoms</label>
          <textarea
            rows="4"
            placeholder="Example: I have acidity and burning sensation"
            value={text}
            onChange={(e) => setText(e.target.value)}
          />

          <button type="submit" disabled={loading}>
            {loading ? "Analyzing..." : "Analyze Query"}
          </button>
        </form>

        {error && <div className="error">{error}</div>}

        {result && (
          <div className="result">
            <h3>Response</h3>
            <p><strong>Dosha:</strong> {result.dosha}</p>
            <p><strong>Reason:</strong> {result.reason}</p>
            <p><strong>Remedy:</strong> {result.remedy}</p>
          </div>
        )}
      </div>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(<App />);
