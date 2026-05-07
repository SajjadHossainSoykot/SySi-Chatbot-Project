import os
from dotenv import load_dotenv
from google import genai

# Load environment variables from .env
load_dotenv()

# Read Gemini API key
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found. Please add it to your .env file.")

# Create Gemini client
client = genai.Client(api_key=api_key)

print("SoyShi Chatbot is ready!")
print("Type 'exit', 'quit', or 'bye' to stop.\n")

while True:
    user_message = input("You: ")

    if user_message.lower() in ["exit", "quit", "bye"]:
        print("SoyShi: Goodbye!")
        break

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=user_message
    )

    print("\nSoyShi:", response.text)
    print()