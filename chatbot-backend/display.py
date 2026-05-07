from history import get_recent_history
from memory import load_memory_summary


def show_full_history(history):
    if not history:
        print("SySi: No saved history yet.\n")
        return

    print("\n--- Full Saved Chat History ---")
    for message in history:
        role = message.get("role", "Unknown")
        content = message.get("content", "")
        print(f"{role}: {content}")
    print("-------------------------------\n")


def show_recent_memory(history):
    recent_history = get_recent_history(history)

    if not recent_history:
        print("SySi: No recent memory yet.\n")
        return

    print("\n--- Recent Memory Sent to AI ---")
    for message in recent_history:
        role = message.get("role", "Unknown")
        content = message.get("content", "")
        print(f"{role}: {content}")
    print("--------------------------------\n")


def show_memory_summary():
    memory_summary = load_memory_summary()

    if not memory_summary:
        print("SySi: No long-term memory summary yet.\n")
        return

    print("\n--- Long-Term Memory Summary ---")
    print(memory_summary)
    print("--------------------------------\n")