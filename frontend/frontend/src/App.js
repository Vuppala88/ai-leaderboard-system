import React, { useState } from "react";
import axios from "axios";

function App() {
  const [file, setFile] = useState(null);
  const [score, setScore] = useState("");
  const [leaderboard, setLeaderboard] = useState([]);

  const handleFileChange = (e) => setFile(e.target.files[0]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    const formData = new FormData();
    formData.append("notebook", file); 
  
    try {
      const response = await axios.post("http://127.0.0.1:8000/submit-notebook", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
  
      const scores = response.data.f1_scores; // Extract scores from response
      setScore(`C4.5: ${scores.f1_c45}, CART: ${scores.f1_cart}`); // Update score state
    } catch (error) {
      console.error(error);
    }
  };

  const fetchLeaderboard = async () => {
    try {
      const response = await axios.get("http://127.0.0.1:8000/leaderboard");
      setLeaderboard(response.data.filter(entry => entry.isVerified)); // Show only verified models
    } catch (error) {
      console.error(error);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-100 to-blue-50 p-6 flex flex-col items-center">
      <h1 className="text-3xl font-bold text-blue-700 mb-8">AI Leaderboard System</h1>

      {/* Model Submission Form */}
      <form
        onSubmit={handleSubmit}
        className="bg-white shadow-md rounded-lg p-4 mb-6 w-full max-w-md"
      >
        <label className="block text-lg font-medium text-gray-700 mb-2">
          Upload Model:
          <input
            type="file"
            onChange={handleFileChange}
            className="mt-1 block w-full text-sm text-gray-700 border border-gray-300 rounded-lg file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
          />
        </label>
        <button
          type="submit"
          className="w-full bg-blue-600 text-white font-semibold py-2 rounded-lg hover:bg-blue-700"
        >
          Submit Model
        </button>
      </form>

      {/* Score Display */}
      {score && (
        <div
          className="bg-white shadow-md rounded-lg p-4 mb-6 w-full max-w-md"
        >
          <h2 className="text-lg font-medium text-gray-700">Your Score:</h2>
          <p className="text-xl font-bold text-blue-600">{score}</p>
        </div>
      )}

      {/* Leaderboard Section */}
      <div className="bg-white shadow-md rounded-lg p-4 w-full max-w-md">
        <button
          onClick={fetchLeaderboard}
          className="w-full bg-green-600 text-white font-semibold py-2 rounded-lg hover:bg-green-700 mb-4"
        >
          Fetch Leaderboard
        </button>
        <h2 className="text-lg font-medium text-gray-700 mb-2">Leaderboard:</h2>
        <ul className="space-y-2">
          {leaderboard.map((entry, index) => (
            <li
              key={index}
              className="bg-gray-50 px-4 py-2 rounded-lg flex justify-between items-center shadow-sm"
            >
              <span className="text-gray-700 font-medium">{entry.name}</span>
              <span className="text-blue-600 font-bold">{entry.score}</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}

export default App;