import os
import json
import time
from dotenv import load_dotenv
from google import genai
MODEL_NAME = "gemini-3.1-flash-lite"

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found. Please add it to your .env file.")

client = genai.Client(api_key=api_key)

HISTORY_FILE = "chat_history.json"


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


def build_prompt(history, latest_user_message):
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


conversation_history = load_chat_history()

print("SoyShi Chatbot is ready!")
print("Type 'exit', 'quit', or 'bye' to stop.")
print("Type 'clear' to delete chat history.")
print("Type 'history' to see saved chat history.\n")

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
            response = client.models.generate_content(
            model=MODEL_NAME,
            contents=full_prompt
            )
            
            bot_reply = response.text

            conversation_history.append({
                "role": "User",
                "content": user_message
            })

            conversation_history.append({
                "role": "SoyShi",
                "content": bot_reply
            })

            save_chat_history(conversation_history)

            print("\nSoyShi:", bot_reply)
            print()

        except Exception as error:
            error_text = str(error)

            if "RESOURCE_EXHAUSTED" in error_text or "429" in error_text:
                print("\nSoyShi: Free API quota limit reached.")
                print("Please wait a little and try again, or use a lighter model/free quota later.")
                print("Your failed message was not saved to chat history.\n")
            else:
                print("\nSoyShi: Something went wrong.")
                print("Error:", error)
                print("Your failed message was not saved to chat history.\n")

    except KeyboardInterrupt:
        print("\nSoyShi: Chat stopped by user. Goodbye!")
        break