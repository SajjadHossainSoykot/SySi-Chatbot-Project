import sys
from config import MODEL_LIST
from history import load_chat_history, save_chat_history, format_timestamp, clear_chat_history
from memory import load_memory_summary, clear_memory_summary, summarize_old_history
from prompt_builder import build_prompt
from gemini_client import generate_reply_with_fallback
from display import (
    show_full_history,
    show_recent_memory,
    show_memory_summary,
    show_help,
    show_model_list,
    show_status,
)


def print_welcome():
    """Print the startup banner and quick start commands."""
    print("==================================================")
    print("        🤖 SySi Chatbot Backend is Ready!        ")
    print("==================================================")
    print("  Type 'help' to see all available commands.")
    print("  Type 'models' to see active fallback models.")
    print("  Type 'exit', 'quit', or 'bye' to stop.\n")


def main():
    conversation_history = load_chat_history()
    print_welcome()

    while True:
        try:
            user_message = input("You: ").strip()

            if not user_message:
                continue

            command = user_message.lower()

            # Exit commands
            if command in ["exit", "quit", "bye"]:
                print("\nSySi: Goodbye! Have a wonderful day!\n")
                break

            # Help command
            if command in ["help", "?"]:
                show_help()
                continue

            # Models pipeline command
            if command in ["models", "model"]:
                show_model_list(MODEL_LIST)
                continue

            # Session status command
            if command in ["status", "info"]:
                show_status(conversation_history)
                continue

            # Clear history command
            if command == "clear":
                conversation_history = []
                clear_chat_history()
                clear_memory_summary()
                print("\nSySi: Chat history and memory summary cleared successfully.\n")
                continue

            # Display history commands
            if command == "history":
                show_full_history(conversation_history)
                continue

            if command == "recent":
                show_recent_memory(conversation_history)
                continue

            if command == "summary":
                show_memory_summary()
                continue

            # Build prompt with memory and recent turns
            current_summary = load_memory_summary()
            full_prompt = build_prompt(
                conversation_history,
                user_message,
                memory_summary=current_summary
            )

            try:
                # Generate AI response with automated model fallback
                bot_reply, used_model = generate_reply_with_fallback(full_prompt)

                timestamp = format_timestamp()

                # Record user input
                conversation_history.append({
                    "role": "User",
                    "content": user_message,
                    "timestamp": timestamp,
                })

                # Record bot response
                conversation_history.append({
                    "role": "SySi",
                    "content": bot_reply,
                    "model": used_model,
                    "timestamp": timestamp,
                })

                # Periodically summarize older messages into persistent memory
                conversation_history = summarize_old_history(
                    conversation_history,
                    current_summary
                )

                # Atomically persist updated conversation history
                save_chat_history(conversation_history)

                # Output SySi's reply
                print(f"\nSySi: {bot_reply}\n")

            except Exception as error:
                print("\nSySi: Something went wrong while generating a response.")
                print("Your failed message was not saved to chat history to keep history clean.")
                print(f"Details: {error}\n")

        except (KeyboardInterrupt, EOFError):
            print("\n\nSySi: Chat session ended. Goodbye!\n")
            sys.exit(0)


if __name__ == "__main__":
    main()
