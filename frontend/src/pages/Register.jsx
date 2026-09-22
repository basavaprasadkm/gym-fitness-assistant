import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import api from "../api";
import { useAuth } from "../context/AuthContext";

export default function Register() {
  const [form, setForm] = useState({
    name: "", email: "", password: "", age: "", height_cm: "", weight_kg: "", goal: "maintain",
  });
  const [error, setError] = useState("");
  const { login } = useAuth();
  const navigate = useNavigate();

  const update = (field) => (e) => setForm({ ...form, [field]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    try {
      const payload = {
        ...form,
        age: form.age ? Number(form.age) : null,
        height_cm: form.height_cm ? Number(form.height_cm) : null,
        weight_kg: form.weight_kg ? Number(form.weight_kg) : null,
      };
      const res = await api.post("/auth/register", payload);
      login(res.data.access_token);
      navigate("/");
    } catch (err) {
      setError(err.response?.data?.detail || "Registration failed");
    }
  };

  return (
    <div className="auth-card">
      <h2>Create your account</h2>
      <form onSubmit={handleSubmit}>
        <input placeholder="Name" value={form.name} onChange={update("name")} required />
        <input type="email" placeholder="Email" value={form.email} onChange={update("email")} required />
        <input type="password" placeholder="Password" value={form.password} onChange={update("password")} required />
        <input type="number" placeholder="Age" value={form.age} onChange={update("age")} />
        <input type="number" placeholder="Height (cm)" value={form.height_cm} onChange={update("height_cm")} />
        <input type="number" placeholder="Weight (kg)" value={form.weight_kg} onChange={update("weight_kg")} />
        <select value={form.goal} onChange={update("goal")}>
          <option value="lose">Lose weight</option>
          <option value="maintain">Maintain</option>
          <option value="gain">Gain muscle</option>
        </select>
        {error && <p className="error">{error}</p>}
        <button type="submit">Create account</button>
      </form>
      <p>
        Already have an account? <Link to="/login">Log in</Link>
      </p>
    </div>
  );
}
