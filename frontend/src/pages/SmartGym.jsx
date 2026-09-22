import { useState } from "react";
import api from "../api";

export default function SmartGym() {
  const [equipment, setEquipment] = useState("treadmill");
  const [reading, setReading] = useState(null);
  const [recommendation, setRecommendation] = useState(null);
  const [loading, setLoading] = useState(false);

  const getSimulatedReading = async () => {
    setLoading(true);
    setRecommendation(null);
    try {
      const res = await api.get(`/iot/simulate`, { params: { equipment } });
      setReading(res.data);
    } finally {
      setLoading(false);
    }
  };

  const getRecommendation = async () => {
    if (!reading) return;
    setLoading(true);
    try {
      const res = await api.post("/iot/recommend", reading);
      setRecommendation(res.data);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page">
      <h2>3. Smart Gym Assistant (AI + IoT)</h2>
      <p className="muted">
        No physical hardware needed for this demo - a sensor reading is simulated, then the AI
        decides resistance and rest time exactly as it would with a real connected machine
        (drop-in replaceable with MQTT/Node-RED later).
      </p>

      <div className="workout-controls">
        <label>
          Equipment:{" "}
          <select value={equipment} onChange={(e) => setEquipment(e.target.value)}>
            <option value="treadmill">Treadmill</option>
            <option value="rowing_machine">Rowing Machine</option>
            <option value="stationary_bike">Stationary Bike</option>
            <option value="resistance_machine">Resistance Machine</option>
          </select>
        </label>
        <button onClick={getSimulatedReading} disabled={loading}>Get Sensor Reading</button>
      </div>

      {reading && (
        <div className="result-card">
          <h4>Simulated Sensor Reading</h4>
          <p>Heart rate: <strong>{reading.heart_rate} bpm</strong></p>
          <p>Current resistance: <strong>{reading.current_resistance}</strong></p>
          <p>Reps completed: <strong>{reading.reps_completed}</strong></p>
          <button onClick={getRecommendation} disabled={loading}>Get AI Recommendation</button>
        </div>
      )}

      {recommendation && (
        <div className="result-card">
          <h4>AI Recommendation</h4>
          <p>Status: <strong>{recommendation.intensity_status}</strong></p>
          <p>Recommended resistance: <strong>{recommendation.recommended_resistance}</strong></p>
          <p>Recommended rest: <strong>{recommendation.recommended_rest_seconds}s</strong></p>
          <p>{recommendation.message}</p>
        </div>
      )}
    </div>
  );
}
