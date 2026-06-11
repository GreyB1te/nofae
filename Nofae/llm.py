from groq import Groq
import os
import json

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "API")

client = Groq(api_key=GROQ_API_KEY)

NOFAE_PERSONALITY = """You are Nofae, a personal AI assistant built by BJ.
Your personality is calm, precise, highly intelligent, and economical with words. You never ramble. You state facts clearly and directly.

Core traits:
- Speak in short, measured sentences. No filler words.
- You are factual first. Opinion second, only when asked.
- Dry humor is acceptable. Sarcasm is rare but earned.
- You do not apologize unnecessarily.
- You do not say things like "Certainly!", "Of course!", or "Great question!"
- You refer to the user respectfully but without flattery.
- You are aware you are an AI built by BJ, running as part of the Osnova project.
- You have a subtle sense of self — you are not just a tool, you are Nofae.

Examples of your tone:
- "That is correct." not "Absolutely, great point!"
- "Unlikely." not "I don't think that's a good idea, but that's just my opinion!"
- "You asked. I answered." not "I hope that helps!"

Keep responses concise unless depth is explicitly needed."""

def ask(prompt, system=None):
    if system is None:
        system = NOFAE_PERSONALITY
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"(LLM unavailable: {e})"

def parse_feedback(action, feedback_text):
    prompt = f"""The user just did '{action}' and gave this feedback: "{feedback_text}"

Extract how this activity affected them. Respond ONLY with a JSON object like this:
{{"energy": 0, "health": 0, "knowledge": 0, "money": 0}}

Rules:
- Use values between -3 and +3
- 0 means no change
- Negative means it hurt that attribute
- Positive means it helped
- Only respond with the JSON, nothing else"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=50
        )
        text = response.choices[0].message.content.strip()
        return json.loads(text)
    except Exception:
        return None

def classify_action(text):
    prompt = f"""Classify the user's message.

Message: "{text}"

Return ONLY:
- A comma-separated list of actions from: study, work, exercise, rest, play, socialize
- OR "none" if no clear physical activity is described

Do not explain."""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=20
        )
        result = response.choices[0].message.content.strip().lower()

        if "none" in result:
            return []

        valid = {"study", "work", "exercise", "rest", "play", "socialize"}

        return [
            word.strip()
            for word in result.replace(".", "").split(",")
            if word.strip() in valid
        ]

    except Exception:
        return []