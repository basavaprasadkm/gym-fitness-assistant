"""
Module 5: Virtual Gym Buddy (AI Chat Companion).

Uses a lightweight keyword-based sentiment lexicon (no heavy model download
needed, works fully offline/free) to detect mood, then picks from
templated, mood-aware motivational responses - this is the "sentiment
analysis + conversational AI" behavior described in the brief without
requiring a paid LLM API key. If an OPENAI_API_KEY is set in the
environment, this can be swapped for a real LLM call (see the commented
hook below) without changing the router.
"""
import random

POSITIVE_WORDS = {"good", "great", "awesome", "strong", "motivated", "happy", "energetic", "proud", "excited", "ready"}
NEGATIVE_WORDS = {"tired", "sad", "lazy", "sore", "unmotivated", "stressed", "exhausted", "bad", "hurt", "sick", "cant", "can't", "give up"}

RESPONSES = {
    "positive": [
        "Love that energy! Let's channel it into today's workout 💪",
        "That's the spirit - let's turn that motivation into a great session!",
    ],
    "negative": [
        "It's okay to have a low-energy day. Even a light 15-minute session counts - want a lighter routine today?",
        "I hear you. Rest is part of training too - but a short walk or stretch might help more than skipping entirely.",
    ],
    "neutral": [
        "Ready when you are - what are we training today?",
        "Let's make today count. Tell me how you're feeling about your workout.",
    ],
}


def detect_mood(message: str) -> str:
    words = set(message.lower().replace(",", " ").replace(".", " ").split())
    pos = len(words & POSITIVE_WORDS)
    neg = len(words & NEGATIVE_WORDS)
    if pos > neg:
        return "positive"
    if neg > pos:
        return "negative"
    return "neutral"


def generate_reply(message: str) -> dict:
    mood = detect_mood(message)
    reply = random.choice(RESPONSES[mood])

    # --- Optional real-LLM hook (disabled by default, no key required) ---
    # import os, requests
    # if os.getenv("OPENAI_API_KEY"):
    #     reply = call_llm(message, mood)  # implement with your provider of choice

    return {"reply": reply, "detected_mood": mood}
