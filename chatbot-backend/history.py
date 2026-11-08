import os
import json
from datetime import datetime
from config import HISTORY_FILE, MAX_RECENT_MESSAGES


def format_timestamp():
    """Return a formatted string representing the current local timestamp."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def load_chat_history():
    """Load conversation history from chat_history.json with error tolerance."""
    if not os.path.exists(HISTORY_FILE):
        return []

    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
            return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def save_chat_history(history):
    """
    Save conversation history atomically to prevent file corruption
    if the process is interrupted during writing.
    """
    temp_file = f"{HISTORY_FILE}.tmp"
    with open(temp_file, "w", encoding="utf-8") as file:
        json.dump(history, file, indent=4, ensure_ascii=False)
    os.replace(temp_file, HISTORY_FILE)


def clear_chat_history():
    """Reset the chat history file to an empty list."""
    save_chat_history([])


def get_recent_history(history):
    """Return the last MAX_RECENT_MESSAGES from history."""
    return history[-MAX_RECENT_MESSAGES:] if history else []
