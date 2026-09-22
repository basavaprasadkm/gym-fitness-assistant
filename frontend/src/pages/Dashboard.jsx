import { Link } from "react-router-dom";

const modules = [
  { to: "/workout", title: "1. AI Gym Trainer", desc: "Webcam pose detection, rep counting & real-time form feedback." },
  { to: "/diet", title: "2. AI Dietician & Calorie Coach", desc: "BMI, BMR, macros, meal plan & grocery list." },
  { to: "/smart-gym", title: "3. Smart Gym Assistant (AI + IoT)", desc: "Simulated sensor feed drives resistance & rest recommendations." },
  { to: "/habit", title: "4. AI Fitness Habit Tracker", desc: "Skip-risk prediction, streaks & motivational nudges." },
  { to: "/chat", title: "5. Virtual Gym Buddy", desc: "Mood-aware AI chat companion." },
  { to: "/performance", title: "6. Pose-to-Performance Analyzer", desc: "Weekly performance score & trend from your sessions." },
  { to: "/gyms", title: "7. Gym Recommender & Planner", desc: "Nearby gyms matched to your goal." },
];

export default function Dashboard() {
  return (
    <div className="dashboard">
      <h1>AI Gym & Fitness Assistant</h1>
      <p>A unified AI ecosystem for workouts, diet, habits and motivation.</p>
      <div className="module-grid">
        {modules.map((m) => (
          <Link key={m.to} to={m.to} className="module-card">
            <h3>{m.title}</h3>
            <p>{m.desc}</p>
          </Link>
        ))}
      </div>
    </div>
  );
}
