from history import get_recent_history
from memory import load_memory_summary


def build_prompt(history, latest_user_message):
    memory_summary = load_memory_summary()
    recent_history = get_recent_history(history)

    conversation_text = ""

    for message in recent_history:
        role = message.get("role", "Unknown")
        content = message.get("content", "")
        conversation_text += f"{role}: {content}\n"

    prompt = f"""
You are SySi, a friendly and helpful AI chatbot.
You explain things clearly and simply.

Long-term memory summary:
{memory_summary if memory_summary else "No long-term memory summary yet."}

Recent conversation:
{conversation_text}

Latest user message:
User: {latest_user_message}

Reply as SySi.

Style rules:
- Be friendly.
- Keep replies clear and natural.
- Do not mention the model name.
- Do not say you cannot remember if the memory summary or recent conversation contains the answer.
- If you do not know something, say it honestly.
"""

    return prompt