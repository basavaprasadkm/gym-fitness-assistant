import { useEffect, useState } from "react";
import api from "../api";

export default function Habit() {
  const [prediction, setPrediction] = useState(null);
  const [today] = useState(new Date().toISOString().slice(0, 10));
  const [message, setMessage] = useState("");

  const loadPrediction = async () => {
    const res = await api.get("/habit/prediction");
    setPrediction(res.data);
  };

  useEffect(() => {
    loadPrediction();
  }, []);

  const logToday = async (completed) => {
    await api.post("/habit/log", { date: today, workout_completed: completed, planned: true });
    setMessage(completed ? "Logged today's workout ✅" : "Logged a skipped day - no judgment, just data.");
    loadPrediction();
  };

  return (
    <div className="page">
      <h2>4. AI Fitness Habit Tracker</h2>
      <p className="muted">Behavioral AI that predicts skip risk from your recent adherence and nudges you accordingly.</p>

      <div className="workout-controls">
        <button onClick={() => logToday(true)}>✅ I worked out today</button>
        <button onClick={() => logToday(false)}>⏭️ I skipped today</button>
      </div>
      {message && <p>{message}</p>}

      {prediction && (
        <div className="result-card">
          <h4>Your Habit Snapshot</h4>
          <p>Current streak: <strong>{prediction.current_streak} day(s)</strong></p>
          <p>Skip risk: <strong>{prediction.skip_risk_percent}%</strong></p>
          <p className="nudge">💬 {prediction.nudge_message}</p>
        </div>
      )}
    </div>
  );
}
