import os
import json
from dotenv import load_dotenv
from google import genai

# Load environment variables
load_dotenv()

# Read Gemini API key
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found. Please add it to your .env file.")

# Create Gemini client
client = genai.Client(api_key=api_key)

# File where chat history will be saved
HISTORY_FILE = "chat_history.json"


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


def build_prompt(history):
    """
    Convert chat history into a full prompt for Gemini.
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

Now reply to the latest user message as SoyShi.
"""

    return prompt


# Load old history when program starts
conversation_history = load_chat_history()

print("SoyShi Chatbot is ready!")
print("Type 'exit', 'quit', or 'bye' to stop.")
print("Type 'clear' to delete chat history.\n")

while True:
    try:
        user_message = input("You: ")

        if user_message.lower() in ["exit", "quit", "bye"]:
            print("SoyShi: Goodbye!")
            break

        if user_message.lower() == "clear":
            conversation_history = []
            save_chat_history(conversation_history)
            print("SoyShi: Chat history cleared.\n")
            continue

        # Add user message to history
        conversation_history.append({
            "role": "User",
            "content": user_message
        })

        # Build full prompt with memory
        full_prompt = build_prompt(conversation_history)

        # Send request to Gemini
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=full_prompt
        )

        bot_reply = response.text

        # Add bot reply to history
        conversation_history.append({
            "role": "SoyShi",
            "content": bot_reply
        })

        # Save updated history
        save_chat_history(conversation_history)

        print("\nSoyShi:", bot_reply)
        print()

    except KeyboardInterrupt:
        print("\nSoyShi: Chat stopped by user. Goodbye!")
        break

    except Exception as error:
        print("\nSoyShi: Something went wrong.")
        print("Error:", error)
        print()