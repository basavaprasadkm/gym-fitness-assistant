import { useState } from "react";
import api from "../api";

export default function Diet() {
  const [form, setForm] = useState({
    weight_kg: "", height_cm: "", age: "", sex: "male",
    activity_level: "moderate", goal: "maintain", dietary_preference: "veg",
  });
  const [plan, setPlan] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const update = (field) => (e) => setForm({ ...form, [field]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const payload = {
        ...form,
        weight_kg: Number(form.weight_kg),
        height_cm: Number(form.height_cm),
        age: Number(form.age),
      };
      const res = await api.post("/diet/plan", payload);
      setPlan(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to generate plan");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page">
      <h2>2. AI Dietician & Calorie Coach</h2>
      <p className="muted">Get a BMI/BMR-based calorie target, macros, meal plan and grocery list.</p>

      <form onSubmit={handleSubmit} className="grid-form">
        <input type="number" placeholder="Weight (kg)" value={form.weight_kg} onChange={update("weight_kg")} required />
        <input type="number" placeholder="Height (cm)" value={form.height_cm} onChange={update("height_cm")} required />
        <input type="number" placeholder="Age" value={form.age} onChange={update("age")} required />
        <select value={form.sex} onChange={update("sex")}>
          <option value="male">Male</option>
          <option value="female">Female</option>
        </select>
        <select value={form.activity_level} onChange={update("activity_level")}>
          <option value="sedentary">Sedentary</option>
          <option value="light">Light activity</option>
          <option value="moderate">Moderate activity</option>
          <option value="active">Active</option>
          <option value="very_active">Very active</option>
        </select>
        <select value={form.goal} onChange={update("goal")}>
          <option value="lose">Lose weight</option>
          <option value="maintain">Maintain</option>
          <option value="gain">Gain muscle</option>
        </select>
        <select value={form.dietary_preference} onChange={update("dietary_preference")}>
          <option value="veg">Vegetarian</option>
          <option value="non_veg">Non-vegetarian</option>
          <option value="vegan">Vegan</option>
        </select>
        <button type="submit">Generate Plan</button>
      </form>

      {error && <p className="error">{error}</p>}
      {loading && <p>Calculating…</p>}

      {plan && (
        <div className="result-card">
          <h3>Your Plan</h3>
          <p>BMI: <strong>{plan.bmi}</strong> ({plan.bmi_category})</p>
          <p>BMR: <strong>{plan.bmr} kcal</strong></p>
          <p>Target calories: <strong>{plan.target_calories} kcal/day</strong></p>
          <p>Macros: {plan.macros.protein_g}g protein · {plan.macros.carbs_g}g carbs · {plan.macros.fat_g}g fat</p>

          <h4>Meal Plan</h4>
          {Object.entries(plan.meal_plan).map(([meal, items]) => (
            <div key={meal}>
              <strong style={{ textTransform: "capitalize" }}>{meal}:</strong> {items.join(", ")}
            </div>
          ))}

          <h4>Grocery List</h4>
          <ul className="grocery-list">
            {plan.grocery_list.map((item, i) => <li key={i}>{item}</li>)}
          </ul>
        </div>
      )}
    </div>
  );
}
