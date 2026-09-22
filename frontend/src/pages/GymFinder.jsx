import { useState } from "react";
import api from "../api";

export default function GymFinder() {
  const [coords, setCoords] = useState(null);
  const [goal, setGoal] = useState("");
  const [gyms, setGyms] = useState([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const useMyLocation = () => {
    setError("");
    if (!navigator.geolocation) {
      setError("Geolocation isn't supported in this browser.");
      return;
    }
    navigator.geolocation.getCurrentPosition(
      (pos) => setCoords({ latitude: pos.coords.latitude, longitude: pos.coords.longitude }),
      () => setError("Couldn't get your location - enter coordinates manually below."),
    );
  };

  const search = async () => {
    if (!coords) {
      setError("Set your location first.");
      return;
    }
    setLoading(true);
    setError("");
    try {
      const res = await api.post("/gyms/recommend", { ...coords, goal: goal || null, max_distance_km: 10 });
      setGyms(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || "Search failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page">
      <h2>7. Gym Recommender & Planner</h2>
      <p className="muted">Finds nearby gyms matched to your fitness goal.</p>

      <div className="workout-controls">
        <button onClick={useMyLocation}>📍 Use My Location</button>
        <select value={goal} onChange={(e) => setGoal(e.target.value)}>
          <option value="">Any goal</option>
          <option value="lose">Lose weight</option>
          <option value="gain">Gain muscle</option>
          <option value="maintain">Maintain</option>
          <option value="strength">Strength</option>
          <option value="cardio">Cardio</option>
        </select>
        <button onClick={search} disabled={loading}>Find Gyms</button>
      </div>

      {coords && <p className="muted">Using location: {coords.latitude.toFixed(4)}, {coords.longitude.toFixed(4)}</p>}
      {error && <p className="error">{error}</p>}

      <div className="gym-list">
        {gyms.map((g, i) => (
          <div key={i} className="result-card">
            <h4>{g.name}</h4>
            <p>{g.distance_km} km away · ⭐ {g.rating}</p>
            <p>Programs: {g.programs.join(", ")}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
