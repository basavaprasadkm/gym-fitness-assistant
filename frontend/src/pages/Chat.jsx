import { useEffect, useRef, useState } from "react";
import api from "../api";

export default function Chat() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const bottomRef = useRef(null);

  useEffect(() => {
    (async () => {
      const res = await api.get("/chat/history");
      setMessages([...res.data].reverse());
    })();
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const send = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;
    const userMsg = input;
    setInput("");
    const res = await api.post("/chat/message", { message: userMsg });
    setMessages((prev) => [...prev, { message: userMsg, reply: res.data.reply, mood: res.data.detected_mood }]);
  };

  return (
    <div className="page">
      <h2>5. Virtual Gym Buddy</h2>
      <p className="muted">Tell it how you're feeling - it detects your mood and responds accordingly.</p>

      <div className="chat-window">
        {messages.map((m, i) => (
          <div key={i} className="chat-turn">
            <div className="chat-bubble user">{m.message}</div>
            <div className="chat-bubble bot">{m.reply} <span className="mood-tag">({m.mood})</span></div>
          </div>
        ))}
        <div ref={bottomRef} />
      </div>

      <form onSubmit={send} className="chat-input">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="How are you feeling about today's workout?"
        />
        <button type="submit">Send</button>
      </form>
    </div>
  );
}
