import os
import json
from config import HISTORY_FILE, MAX_RECENT_MESSAGES


def load_chat_history():
    if not os.path.exists(HISTORY_FILE):
        return []

    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as file:
            return json.load(file)

    except json.JSONDecodeError:
        return []


def save_chat_history(history):
    with open(HISTORY_FILE, "w", encoding="utf-8") as file:
        json.dump(history, file, indent=4, ensure_ascii=False)


def get_recent_history(history):
    return history[-MAX_RECENT_MESSAGES:]