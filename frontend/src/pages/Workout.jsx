import { useEffect, useRef, useState } from "react";
import api from "../api";

/*
 * Module 1: AI Gym Trainer (Workout Detection & Feedback System)
 *
 * Runs MediaPipe Pose fully client-side on the webcam feed. For each frame we
 * compute the relevant joint angle (knee angle for squats/lunges, elbow angle
 * for pushups/curls/presses) and run a small state machine that only counts a
 * rep once the joint has actually crossed into - and back out of - the target
 * range of motion. That gives real, pose-driven rep counting and lets us
 * capture the angle reached at the peak of every single rep, which is what
 * the backend uses for form scoring (Module 6: Pose-to-Performance Analyzer).
 */

// landmark indices = [proximal, joint, distal], e.g. hip-knee-ankle
const EXERCISE_CONFIG = {
  squat: { label: "Squat", landmarks: [24, 26, 28], direction: "flex", enter: 140, exit: 150 },
  pushup: { label: "Push-up", landmarks: [12, 14, 16], direction: "flex", enter: 140, exit: 150 },
  bicep_curl: { label: "Bicep Curl", landmarks: [12, 14, 16], direction: "flex", enter: 110, exit: 120 },
  lunge: { label: "Lunge", landmarks: [24, 26, 28], direction: "flex", enter: 140, exit: 150 },
  shoulder_press: { label: "Shoulder Press", landmarks: [12, 14, 16], direction: "extend", enter: 140, exit: 130 },
};

function angleBetween(a, b, c) {
  const ab = { x: a.x - b.x, y: a.y - b.y };
  const cb = { x: c.x - b.x, y: c.y - b.y };
  const dot = ab.x * cb.x + ab.y * cb.y;
  const magAb = Math.hypot(ab.x, ab.y);
  const magCb = Math.hypot(cb.x, cb.y);
  if (magAb === 0 || magCb === 0) return 180;
  const cos = Math.min(1, Math.max(-1, dot / (magAb * magCb)));
  return (Math.acos(cos) * 180) / Math.PI;
}

export default function Workout() {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const poseRef = useRef(null);
  const cameraRef = useRef(null);

  const [exercise, setExercise] = useState("squat");
  const exerciseRef = useRef(exercise);
  const [running, setRunning] = useState(false);
  const [repCount, setRepCount] = useState(0);
  const [currentAngle, setCurrentAngle] = useState(null);
  const [visibilityWarning, setVisibilityWarning] = useState(false);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [sdkReady, setSdkReady] = useState(true);

  const repsRef = useRef([]);
  const phaseRef = useRef("rest");
  const peakAngleRef = useRef(null);
  const startTimeRef = useRef(null);
  const lowVisFramesRef = useRef(0);

  useEffect(() => {
    exerciseRef.current = exercise;
    resetSession();
  }, [exercise]);

  const resetSession = () => {
    repsRef.current = [];
    phaseRef.current = "rest";
    peakAngleRef.current = null;
    setRepCount(0);
    setResult(null);
  };

  const onResults = (results) => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    canvas.width = results.image.width;
    canvas.height = results.image.height;
    ctx.save();
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.drawImage(results.image, 0, 0, canvas.width, canvas.height);

    if (results.poseLandmarks) {
      if (window.drawConnectors && window.POSE_CONNECTIONS) {
        window.drawConnectors(ctx, results.poseLandmarks, window.POSE_CONNECTIONS, { color: "#22c55e", lineWidth: 3 });
        window.drawLandmarks(ctx, results.poseLandmarks, { color: "#f97316", radius: 3 });
      }

      const cfg = EXERCISE_CONFIG[exerciseRef.current];
      const [ia, ib, ic] = cfg.landmarks;
      const a = results.poseLandmarks[ia];
      const b = results.poseLandmarks[ib];
      const c = results.poseLandmarks[ic];

      const minVisibility = Math.min(a.visibility ?? 1, b.visibility ?? 1, c.visibility ?? 1);
      if (minVisibility < 0.5) {
        lowVisFramesRef.current += 1;
        setVisibilityWarning(lowVisFramesRef.current > 15);
      } else {
        lowVisFramesRef.current = 0;
        setVisibilityWarning(false);
      }

      const angle = angleBetween(a, b, c);
      setCurrentAngle(Math.round(angle));
      runRepStateMachine(angle, cfg);
    }
    ctx.restore();
  };

  const runRepStateMachine = (angle, cfg) => {
    if (cfg.direction === "flex") {
      if (angle < cfg.enter) {
        phaseRef.current = "down";
        peakAngleRef.current = peakAngleRef.current === null ? angle : Math.min(peakAngleRef.current, angle);
      } else if (angle > cfg.exit && phaseRef.current === "down") {
        completeRep(peakAngleRef.current);
      }
    } else {
      if (angle > cfg.enter) {
        phaseRef.current = "up";
        peakAngleRef.current = peakAngleRef.current === null ? angle : Math.max(peakAngleRef.current, angle);
      } else if (angle < cfg.exit && phaseRef.current === "up") {
        completeRep(peakAngleRef.current);
      }
    }
  };

  const completeRep = (peakAngle) => {
    repsRef.current.push({
      exercise: exerciseRef.current,
      joint_angle: peakAngle,
      timestamp: new Date().toISOString(),
    });
    setRepCount(repsRef.current.length);
    phaseRef.current = "rest";
    peakAngleRef.current = null;
  };

  const startCamera = async () => {
    if (!window.Pose || !window.Camera) {
      setSdkReady(false);
      return;
    }
    resetSession();
    startTimeRef.current = Date.now();

    const pose = new window.Pose({
      locateFile: (file) => `https://cdn.jsdelivr.net/npm/@mediapipe/pose@0.5.1675469404/${file}`,
    });
    pose.setOptions({
      modelComplexity: 1,
      smoothLandmarks: true,
      minDetectionConfidence: 0.6,
      minTrackingConfidence: 0.6,
    });
    pose.onResults(onResults);
    poseRef.current = pose;

    const camera = new window.Camera(videoRef.current, {
      onFrame: async () => {
        await pose.send({ image: videoRef.current });
      },
      width: 640,
      height: 480,
    });
    cameraRef.current = camera;
    camera.start();
    setRunning(true);
  };

  const stopCameraAndSubmit = async () => {
    cameraRef.current?.stop();
    setRunning(false);

    const durationSeconds = (Date.now() - startTimeRef.current) / 1000;
    const formIssues = [];
    if (repsRef.current.length === 0) {
      formIssues.push("no valid reps detected - make sure your full body is visible and try again");
    }

    setLoading(true);
    try {
      const res = await api.post("/workout/session", {
        exercise: exerciseRef.current,
        reps: repsRef.current,
        duration_seconds: durationSeconds,
        form_issues: formIssues,
      });
      setResult(res.data);
    } catch (err) {
      setResult({ error: err.response?.data?.detail || "Failed to save session" });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    return () => cameraRef.current?.stop();
  }, []);

  return (
    <div className="page">
      <h2>1. AI Gym Trainer</h2>
      <p className="muted">Real-time pose detection (MediaPipe) counts reps and scores your form as you go.</p>

      {!sdkReady && (
        <p className="error">
          MediaPipe scripts failed to load (check your internet connection - they load from a CDN).
        </p>
      )}

      <div className="workout-controls">
        <label>
          Exercise:{" "}
          <select value={exercise} onChange={(e) => setExercise(e.target.value)} disabled={running}>
            {Object.entries(EXERCISE_CONFIG).map(([key, cfg]) => (
              <option key={key} value={key}>{cfg.label}</option>
            ))}
          </select>
        </label>
        {!running ? (
          <button onClick={startCamera}>Start Session</button>
        ) : (
          <button onClick={stopCameraAndSubmit}>Stop & Save Session</button>
        )}
      </div>

      <div className="video-wrap">
        <video ref={videoRef} style={{ display: "none" }} playsInline />
        <canvas ref={canvasRef} className="pose-canvas" />
      </div>

      <div className="live-stats">
        <span>Reps: <strong>{repCount}</strong></span>
        <span>Joint angle: <strong>{currentAngle ?? "-"}°</strong></span>
        {visibilityWarning && <span className="warn">⚠ Step back so your full body is visible</span>}
      </div>

      {loading && <p>Analyzing session…</p>}

      {result && !result.error && (
        <div className="result-card">
          <h3>Session Result</h3>
          <p>Valid reps counted: <strong>{result.rep_count}</strong></p>
          <p>Form score: <strong>{result.form_score}/100</strong></p>
          <p>Tempo consistency: <strong>{result.tempo_consistency}/100</strong></p>
          <ul>
            {result.feedback.map((f, i) => <li key={i}>{f}</li>)}
          </ul>
        </div>
      )}
      {result?.error && <p className="error">{result.error}</p>}
    </div>
  );
}
