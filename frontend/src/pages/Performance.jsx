import { useEffect, useState } from "react";
import api from "../api";

export default function Performance() {
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      const res = await api.get("/performance/weekly");
      setReport(res.data);
      setLoading(false);
    })();
  }, []);

  return (
    <div className="page">
      <h2>6. Pose-to-Performance Analyzer</h2>
      <p className="muted">Aggregates this week's AI Gym Trainer sessions into a single performance score.</p>

      {loading && <p>Loading…</p>}
      {report && (
        <div className="result-card">
          <p>Week starting: <strong>{report.week_start}</strong></p>
          <p>Sessions logged: <strong>{report.total_sessions}</strong></p>
          <p>Average form score: <strong>{report.avg_form_score}/100</strong></p>
          <p>Average tempo consistency: <strong>{report.avg_tempo_consistency}/100</strong></p>
          <p className="score">Performance Score: <strong>{report.performance_score}/100</strong></p>
          <p>Trend: <strong>{report.trend}</strong></p>
          {report.total_sessions === 0 && (
            <p className="muted">Complete a session in the AI Gym Trainer to see your score here.</p>
          )}
        </div>
      )}
    </div>
  );
}
