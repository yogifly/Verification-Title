import { useState } from "react";
import axios from "axios";

function App() {
  const [title, setTitle] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const response = await axios.post("/verify_title", { title });
      setResult(response.data);
    } catch (error) {
      console.error("Error verifying title:", error);
      setResult({ error: "Failed to verify title" });
    }
    setLoading(false);
  };

  return (
    <div style={{ padding: "20px", textAlign: "center" }}>
      <h2>Title Verification System</h2>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="Enter a title"
          style={{ padding: "10px", width: "300px" }}
          required
        />
        <button type="submit" style={{ marginLeft: "10px", padding: "10px" }}>
          Verify
        </button>
      </form>

      {loading && <p>Verifying...</p>}
      {result && (
        <div style={{ marginTop: "20px", padding: "10px", border: "1px solid black" }}>
          <h3>Result:</h3>
          {result.error ? (
            <p style={{ color: "red" }}>{result.error}</p>
          ) : (
            <>
              <p>Status: <strong>{result.status}</strong></p>
              {result.reason && <p>Reason: {result.reason}</p>}
              {result.similarity_score && <p>Similarity Score: {result.similarity_score}</p>}
              <p>Verification Probability: {result.verification_probability}%</p>
            </>
          )}
        </div>
      )}
    </div>
  );
}

export default App;
