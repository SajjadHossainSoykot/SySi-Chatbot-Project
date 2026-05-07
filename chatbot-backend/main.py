import os
import json
import time
from dotenv import load_dotenv
from google import genai

# -----------------------------
# Basic setup
# -----------------------------

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found. Please add it to your .env file.")

client = genai.Client(api_key=api_key)

# Save files beside main.py, not outside the backend folder
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

HISTORY_FILE = os.path.join(BASE_DIR, "chat_history.json")
SUMMARY_FILE = os.path.join(BASE_DIR, "memory_summary.txt")

# Main model first, fallback models later
MODEL_LIST = [
    "gemini-3.1-flash-lite",
    "gemini-1.5-flash",
    "gemini-1.5-flash-8b",
    "gemini-2.5-flash-lite",
    "gemini-2.5-flash",
    "gemma-3-27b",
    "gemma-3-12b",
    "gemma-3-4b",
]

# Only send recent messages to make response faster
MAX_RECENT_MESSAGES = 8

# When history becomes longer than this, old messages will be summarized
SUMMARY_TRIGGER_MESSAGES = 16


# -----------------------------
# Chat history functions
# -----------------------------

def load_chat_history():
    """
    Load previous chat history from JSON file.
    If the file does not exist, return an empty list.
    """
    if not os.path.exists(HISTORY_FILE):
        return []

    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as file:
            return json.load(file)

    except json.JSONDecodeError:
        return []


def save_chat_history(history):
    """
    Save chat history to JSON file.
    """
    with open(HISTORY_FILE, "w", encoding="utf-8") as file:
        json.dump(history, file, indent=4, ensure_ascii=False)


def get_recent_history(history):
    """
    Return only the latest few messages instead of the full history.
    This makes the prompt smaller and response faster.
    """
    return history[-MAX_RECENT_MESSAGES:]


# -----------------------------
# Long-term memory summary functions
# -----------------------------

def load_memory_summary():
    """
    Load long-term memory summary from text file.
    """
    if not os.path.exists(SUMMARY_FILE):
        return ""

    with open(SUMMARY_FILE, "r", encoding="utf-8") as file:
        return file.read().strip()


def save_memory_summary(summary):
    """
    Save long-term memory summary to text file.
    """
    with open(SUMMARY_FILE, "w", encoding="utf-8") as file:
        file.write(summary.strip())


def generate_reply_with_fallback(prompt, show_fallback_messages=True):
    """
    Try the main model first.
    If it fails due to quota/high demand/unavailable issue,
    try the next fallback model.

    Normal successful use is silent.
    Fallback messages only show when one model fails.
    """
    last_error = None

    for index, model_name in enumerate(MODEL_LIST):
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt
            )

            return response.text, model_name

        except Exception as error:
            error_text = str(error)
            last_error = error

            is_quota_error = "RESOURCE_EXHAUSTED" in error_text or "429" in error_text
            is_busy_error = "UNAVAILABLE" in error_text or "503" in error_text
            is_not_found_error = "NOT_FOUND" in error_text or "404" in error_text
            is_permission_error = "PERMISSION_DENIED" in error_text or "403" in error_text

            recoverable_error = (
                is_quota_error
                or is_busy_error
                or is_not_found_error
                or is_permission_error
            )

            if recoverable_error and index < len(MODEL_LIST) - 1:
                next_model = MODEL_LIST[index + 1]

                if show_fallback_messages:
                    if is_quota_error:
                        print(f"SoyShi: {model_name} quota reached. Trying {next_model}...")
                    elif is_busy_error:
                        print(f"SoyShi: {model_name} is busy. Trying {next_model}...")
                    elif is_not_found_error:
                        print(f"SoyShi: {model_name} is not available. Trying {next_model}...")
                    elif is_permission_error:
                        print(f"SoyShi: {model_name} is not allowed for this API key. Trying {next_model}...")

                time.sleep(1)
                continue

            raise error

    raise Exception(f"All models failed. Last error: {last_error}")


def summarize_old_history(history, existing_summary):
    """
    Summarize older conversation messages into compact long-term memory.

    Full history is not sent every time.
    Older messages are compressed into memory_summary.txt.
    Recent messages remain in chat_history.json.
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
You are creating long-term memory for a chatbot named SoyShi.

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
        # If summarization fails, do not delete old history.
        return history


# -----------------------------
# Prompt builder
# -----------------------------

def build_prompt(history, latest_user_message):
    """
    Build prompt using:
    1. Long-term memory summary
    2. Recent conversation only
    3. Latest user message
    """
    memory_summary = load_memory_summary()
    recent_history = get_recent_history(history)

    conversation_text = ""

    for message in recent_history:
        role = message.get("role", "Unknown")
        content = message.get("content", "")
        conversation_text += f"{role}: {content}\n"

    prompt = f"""
You are SoyShi, a friendly and helpful AI chatbot.
You explain things clearly and simply.

Long-term memory summary:
{memory_summary if memory_summary else "No long-term memory summary yet."}

Recent conversation:
{conversation_text}

Latest user message:
User: {latest_user_message}

Reply as SoyShi.

Style rules:
- Be friendly.
- Keep replies clear and natural.
- Do not mention the model name.
- Do not say you cannot remember if the memory summary or recent conversation contains the answer.
- If you do not know something, say it honestly.
"""

    return prompt


# -----------------------------
# Display helper functions
# -----------------------------

def show_full_history(history):
    """
    Display full saved chat history.
    """
    if not history:
        print("SoyShi: No saved history yet.\n")
        return

    print("\n--- Full Saved Chat History ---")
    for message in history:
        role = message.get("role", "Unknown")
        content = message.get("content", "")
        print(f"{role}: {content}")
    print("-------------------------------\n")


def show_recent_memory(history):
    """
    Display only recent memory that is sent to the model.
    """
    recent_history = get_recent_history(history)

    if not recent_history:
        print("SoyShi: No recent memory yet.\n")
        return

    print("\n--- Recent Memory Sent to AI ---")
    for message in recent_history:
        role = message.get("role", "Unknown")
        content = message.get("content", "")
        print(f"{role}: {content}")
    print("--------------------------------\n")


def show_memory_summary():
    """
    Display saved long-term memory summary.
    """
    memory_summary = load_memory_summary()

    if not memory_summary:
        print("SoyShi: No long-term memory summary yet.\n")
        return

    print("\n--- Long-Term Memory Summary ---")
    print(memory_summary)
    print("--------------------------------\n")


# -----------------------------
# Main chatbot loop
# -----------------------------

conversation_history = load_chat_history()

print("SoyShi Chatbot is ready!")
print("Type 'exit', 'quit', or 'bye' to stop.")
print("Type 'clear' to delete chat history and memory summary.")
print("Type 'history' to see full saved chat history.")
print("Type 'recent' to see recent memory sent to AI.")
print("Type 'summary' to see long-term memory summary.\n")

while True:
    try:
        user_message = input("You: ").strip()

        if not user_message:
            continue

        command = user_message.lower()

        if command in ["exit", "quit", "bye"]:
            print("SoyShi: Goodbye!")
            break

        if command == "clear":
            conversation_history = []
            save_chat_history(conversation_history)
            save_memory_summary("")
            print("SoyShi: Chat history and memory summary cleared.\n")
            continue

        if command == "history":
            show_full_history(conversation_history)
            continue

        if command == "recent":
            show_recent_memory(conversation_history)
            continue

        if command == "summary":
            show_memory_summary()
            continue

        full_prompt = build_prompt(conversation_history, user_message)

        try:
            bot_reply, used_model = generate_reply_with_fallback(full_prompt)

            conversation_history.append({
                "role": "User",
                "content": user_message
            })

            conversation_history.append({
                "role": "SoyShi",
                "content": bot_reply,
                "model": used_model
            })

            memory_summary = load_memory_summary()
            conversation_history = summarize_old_history(conversation_history, memory_summary)

            save_chat_history(conversation_history)

            print("\nSoyShi:", bot_reply)
            print()

        except Exception as error:
            print("\nSoyShi: Something went wrong.")
            print("Your failed message was not saved to chat history.")
            print("Error:", error)
            print()

    except KeyboardInterrupt:
        print("\nSoyShi: Chat stopped by user. Goodbye!")
        break