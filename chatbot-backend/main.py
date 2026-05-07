import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found. Please add it to your .env file.")

client = genai.Client(api_key=api_key)

print("SoyShi Chatbot is ready!")
print("Type 'exit', 'quit', or 'bye' to stop.\n")

while True:
    try:
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

    except KeyboardInterrupt:
        print("\nSoyShi: Chat stopped by user. Goodbye!")
        break

    except Exception as error:
        print("\nSoyShi: Something went wrong.")
        print("Error:", error)
        print()