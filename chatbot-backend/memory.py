import os
from config import SUMMARY_FILE, SUMMARY_TRIGGER_MESSAGES, MAX_RECENT_MESSAGES
from gemini_client import generate_reply_with_fallback


def load_memory_summary():
    """Load the long-term memory summary from disk."""
    if not os.path.exists(SUMMARY_FILE):
        return ""

    try:
        with open(SUMMARY_FILE, "r", encoding="utf-8") as file:
            return file.read().strip()
    except OSError:
        return ""


def save_memory_summary(summary):
    """
    Save the memory summary atomically to prevent corruption
    if interrupted mid-write.
    """
    temp_file = f"{SUMMARY_FILE}.tmp"
    with open(temp_file, "w", encoding="utf-8") as file:
        file.write(summary.strip())
    os.replace(temp_file, SUMMARY_FILE)


def clear_memory_summary():
    """Clear the memory summary file."""
    save_memory_summary("")


def summarize_old_history(history, existing_summary):
    """
    When history grows past SUMMARY_TRIGGER_MESSAGES, summarize the older messages
    and append them to the long-term memory summary, leaving recent messages intact.
    """
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

        # Protect against empty or invalid responses overwriting existing memory
        if updated_summary and updated_summary.strip():
            save_memory_summary(updated_summary)
            return recent_messages

        return history

    except Exception:
        # If summarization fails, keep history intact to avoid data loss
        return history
