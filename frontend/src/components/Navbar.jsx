import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const links = [
  { to: "/workout", label: "AI Gym Trainer" },
  { to: "/diet", label: "Diet Coach" },
  { to: "/smart-gym", label: "Smart Gym (IoT)" },
  { to: "/habit", label: "Habit Tracker" },
  { to: "/chat", label: "Gym Buddy" },
  { to: "/performance", label: "Performance" },
  { to: "/gyms", label: "Gym Finder" },
];

export default function Navbar() {
  const { isAuthed, logout } = useAuth();
  const navigate = useNavigate();

  if (!isAuthed) return null;

  return (
    <nav className="navbar">
      <div className="brand">
        <Link to="/">🏋️ AI Fitness</Link>
      </div>
      <div className="nav-links">
        {links.map((l) => (
          <Link key={l.to} to={l.to}>
            {l.label}
          </Link>
        ))}
      </div>
      <button
        className="logout-btn"
        onClick={() => {
          logout();
          navigate("/login");
        }}
      >
        Logout
      </button>
    </nav>
  );
}
