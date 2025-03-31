// src/App.js

import React, { useState } from "react";
import axios from "axios";

function App() {
  const [title, setTitle] = useState("");
  const [result, setResult] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      const response = await axios.post("http://127.0.0.1:5000/verify_title", {
        title,
      });
      setResult(response.data);
    } catch (error) {
      console.error("Error verifying title:", error);
    }
  };

  return (
    <div className="container mx-auto p-6">
      <h1 className="text-2xl font-bold mb-4">Title Verification System</h1>

      <form onSubmit={handleSubmit} className="mb-4">
        <input
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="Enter Title"
          className="border p-2 rounded w-full mb-2"
          required
        />
        <button
          type="submit"
          className="bg-blue-500 text-white px-4 py-2 rounded"
        >
          Verify Title
        </button>
      </form>

      {result && (
        <div className="mt-4 p-4 border rounded bg-gray-100">
          <h2 className="text-xl font-semibold">Result:</h2>
          <p>Status: {result.status}</p>
          {result.status === "Rejected" && (
            <>
              <p>
                <strong>Reason:</strong> {result.reason}
              </p>
              <p>
                <strong>Matched Title:</strong> {result.similarity_score
                  ? `${result.similarity_score} - ${result.reason}`
                  : "N/A"}
              </p>
            </>
          )}
          <p>
            <strong>Verification Probability:</strong>{" "}
            {result.verification_probability}%
          </p>
        </div>
      )}
    </div>
  );
}

export default App;
