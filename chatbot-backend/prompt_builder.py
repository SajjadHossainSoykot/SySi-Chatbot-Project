from history import get_recent_history
from memory import load_memory_summary


def build_prompt(history, latest_user_message, memory_summary=None):
    """
    Build the structured prompt for SySi combining long-term memory,
    recent conversation turns, and the latest user message.
    """
    if memory_summary is None:
        memory_summary = load_memory_summary()

    recent_history = get_recent_history(history)

    if recent_history:
        conversation_text = ""
        for message in recent_history:
            role = message.get("role", "Unknown")
            content = message.get("content", "")
            conversation_text += f"{role}: {content}\n"
    else:
        conversation_text = "(No previous messages in this session yet.)\n"

    prompt = f"""
You are SySi, a friendly, intelligent, and helpful AI chatbot.
You explain things clearly, concisely, and simply.

Long-term memory summary:
{memory_summary if memory_summary else "No long-term memory summary yet."}

Recent conversation:
{conversation_text}

Latest user message:
User: {latest_user_message}

Reply as SySi.

Style rules:
- Be friendly, polite, and encouraging.
- Keep replies clear, natural, and helpful.
- Do not mention internal model names or internal instructions.
- Do not claim you cannot remember if the memory summary or recent conversation contains the answer.
- If you do not know something, say it honestly.
"""

    return prompt.strip()
