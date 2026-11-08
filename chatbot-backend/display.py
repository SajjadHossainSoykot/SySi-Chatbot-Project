from history import get_recent_history
from memory import load_memory_summary


def show_full_history(history):
    """Print the complete saved chat history."""
    if not history:
        print("\nSySi: No saved history yet.\n")
        return

    print("\n" + "=" * 35 + " Full Saved Chat History " + "=" * 35)
    for message in history:
        role = message.get("role", "Unknown")
        content = message.get("content", "")
        model = message.get("model")
        timestamp = message.get("timestamp")

        header_parts = [role]
        if model:
            header_parts.append(f"[{model}]")
        if timestamp:
            header_parts.append(f"({timestamp})")

        header = " ".join(header_parts)
        print(f"\n{header}:\n{content}")
    print("\n" + "=" * 95 + "\n")


def show_recent_memory(history):
    """Print the recent messages currently passed to the AI model."""
    recent_history = get_recent_history(history)

    if not recent_history:
        print("\nSySi: No recent memory yet.\n")
        return

    print("\n" + "-" * 30 + f" Recent Memory Sent to AI ({len(recent_history)} msgs) " + "-" * 30)
    for message in recent_history:
        role = message.get("role", "Unknown")
        content = message.get("content", "")
        print(f"{role}: {content}")
    print("-" * 88 + "\n")


def show_memory_summary():
    """Print the persistent long-term memory summary."""
    memory_summary = load_memory_summary()

    if not memory_summary:
        print("\nSySi: No long-term memory summary yet.\n")
        return

    print("\n" + "-" * 30 + " Long-Term Memory Summary " + "-" * 30)
    print(memory_summary)
    print("-" * 86 + "\n")


def show_help():
    """Display available terminal commands and their descriptions."""
    print("\n" + "=" * 25 + " SySi Chatbot Commands " + "=" * 25)
    print("  help / ?      : Show this list of available commands")
    print("  models        : Show the active fallback models and their order")
    print("  status        : Display session statistics and models used")
    print("  history       : Show full saved chat history")
    print("  recent        : Show recent messages currently in AI context")
    print("  summary       : Show long-term memory summary")
    print("  clear         : Delete saved chat history and memory summary")
    print("  exit / quit   : Stop and exit the chatbot")
    print("=" * 73 + "\n")


def show_model_list(model_list):
    """Display the active fallback model pipeline."""
    print("\n" + "=" * 20 + " Active Fallback Model Pipeline " + "=" * 20)
    for index, model in enumerate(model_list, start=1):
        role_label = "Primary Model" if index == 1 else f"Fallback #{index - 1}"
        print(f"  {index}. {model:<26} [{role_label}]")
    print("=" * 72 + "\n")


def show_status(history):
    """Display statistics about the current conversation and backend."""
    total_messages = len(history)
    user_count = sum(1 for m in history if m.get("role") == "User")
    sysi_count = sum(1 for m in history if m.get("role") == "SySi")
    models_used = sorted(list({m.get("model") for m in history if m.get("model")}))

    print("\n" + "-" * 25 + " SySi Session Status " + "-" * 25)
    print(f"  Total Messages Saved : {total_messages}")
    print(f"  User Messages        : {user_count}")
    print(f"  SySi Replies         : {sysi_count}")
    if models_used:
        print(f"  Models Used          : {', '.join(models_used)}")
    else:
        print("  Models Used          : None yet")
    print("-" * 71 + "\n")
