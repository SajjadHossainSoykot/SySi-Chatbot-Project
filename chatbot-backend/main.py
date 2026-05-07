import os
import json
import time
from dotenv import load_dotenv
from google import genai

# Load environment variables from .env file
load_dotenv()

# Read Gemini API key
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found. Please add it to your .env file.")

# Create Gemini client
client = genai.Client(api_key=api_key)

# Chat history file will always be saved beside main.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HISTORY_FILE = os.path.join(BASE_DIR, "chat_history.json")

# Multiple model fallback list
# The chatbot will try these models one by one.
MODEL_LIST = [
    "gemini-3.1-flash-lite",
    "gemma-3-12b",
    "gemma-3-4b",
    "gemma-3-2b",
    "gemma-3-1b",
]


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


def build_prompt(history, latest_user_message):
    """
    Build the full prompt with conversation history and latest user message.
    """
    conversation_text = ""

    for message in history:
        role = message["role"]
        content = message["content"]
        conversation_text += f"{role}: {content}\n"

    prompt = f"""
You are SoyShi, a friendly and helpful AI chatbot.
You explain things clearly and simply.

Conversation history:
{conversation_text}

Latest user message:
User: {latest_user_message}

Now reply to the latest user message as SoyShi.
"""

    return prompt


def generate_reply_with_fallback(prompt):
    """
    Try multiple Gemini/Gemma models.
    If one model fails because of quota, high demand, or server issue,
    automatically try the next model.
    """
    last_error = None

    for model_name in MODEL_LIST:
        try:
            print(f"SoyShi: Trying model: {model_name}...")

            response = client.models.generate_content(
                model=model_name,
                contents=prompt
            )

            return response.text, model_name

        except Exception as error:
            error_text = str(error)
            last_error = error

            if "RESOURCE_EXHAUSTED" in error_text or "429" in error_text:
                print(f"SoyShi: {model_name} quota/rate limit reached. Trying next model...")
                time.sleep(1)
                continue

            elif "UNAVAILABLE" in error_text or "503" in error_text:
                print(f"SoyShi: {model_name} is busy right now. Trying next model...")
                time.sleep(1)
                continue

            elif "NOT_FOUND" in error_text or "404" in error_text:
                print(f"SoyShi: {model_name} is not available for your account. Trying next model...")
                time.sleep(1)
                continue

            elif "PERMISSION_DENIED" in error_text or "403" in error_text:
                print(f"SoyShi: {model_name} is not allowed for your API key. Trying next model...")
                time.sleep(1)
                continue

            else:
                print(f"SoyShi: {model_name} failed with an unknown error. Trying next model...")
                print("Error:", error)
                time.sleep(1)
                continue

    raise Exception(f"All models failed. Last error: {last_error}")


# Load old history when program starts
conversation_history = load_chat_history()

print("SoyShi Chatbot is ready!")
print("Type 'exit', 'quit', or 'bye' to stop.")
print("Type 'clear' to delete chat history.")
print("Type 'history' to see saved chat history.")
print("Using fallback models:")
for model in MODEL_LIST:
    print(f"- {model}")
print()

while True:
    try:
        user_message = input("You: ").strip()

        if not user_message:
            continue

        if user_message.lower() in ["exit", "quit", "bye"]:
            print("SoyShi: Goodbye!")
            break

        if user_message.lower() == "clear":
            conversation_history = []
            save_chat_history(conversation_history)
            print("SoyShi: Chat history cleared.\n")
            continue

        if user_message.lower() == "history":
            if not conversation_history:
                print("SoyShi: No saved history yet.\n")
            else:
                print("\n--- Saved Chat History ---")
                for message in conversation_history:
                    print(f"{message['role']}: {message['content']}")
                print("--------------------------\n")
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

            save_chat_history(conversation_history)

            print(f"\nSoyShi [{used_model}]:", bot_reply)
            print()

        except Exception as error:
            print("\nSoyShi: All available models failed.")
            print("Your failed message was not saved to chat history.")
            print("Error:", error)
            print()

    except KeyboardInterrupt:
        print("\nSoyShi: Chat stopped by user. Goodbye!")
        break