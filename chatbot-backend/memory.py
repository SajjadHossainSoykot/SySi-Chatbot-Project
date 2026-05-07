import os
from config import SUMMARY_FILE, SUMMARY_TRIGGER_MESSAGES, MAX_RECENT_MESSAGES
from gemini_client import generate_reply_with_fallback


def load_memory_summary():
    if not os.path.exists(SUMMARY_FILE):
        return ""

    with open(SUMMARY_FILE, "r", encoding="utf-8") as file:
        return file.read().strip()


def save_memory_summary(summary):
    with open(SUMMARY_FILE, "w", encoding="utf-8") as file:
        file.write(summary.strip())


def summarize_old_history(history, existing_summary):
    if len(history) <= SUMMARY_TRIGGER_MESSAGES:
        return history

    old_messages = history[:-MAX_RECENT_MESSAGES]
    recent_messages = history[-MAX_RECENT_MESSAGES:]

    old_conversation_text = ""

    for message in old_messages:
        role = message.get("role", "Unknown")
        content = message.get("content", "")
        old_conversation_text += f"{role}: {content}\n"

    summary_prompt = f"""
You are creating long-term memory for a chatbot named SySi.

Existing memory summary:
{existing_summary if existing_summary else "No previous memory summary."}

Older conversation to summarize:
{old_conversation_text}

Create an updated short memory summary.

Rules:
- Keep important facts about the user.
- Keep the user's name if mentioned.
- Keep project details.
- Keep learning goals.
- Keep preferences.
- Remove greetings and unnecessary small talk.
- Use short bullet points.
"""

    try:
        updated_summary, used_model = generate_reply_with_fallback(
            summary_prompt,
            show_fallback_messages=False
        )

        save_memory_summary(updated_summary)

        return recent_messages

    except Exception:
        return history