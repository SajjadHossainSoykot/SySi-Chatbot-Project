from history import load_chat_history, save_chat_history
from memory import load_memory_summary, save_memory_summary, summarize_old_history
from prompt_builder import build_prompt
from gemini_client import generate_reply_with_fallback
from display import show_full_history, show_recent_memory, show_memory_summary


conversation_history = load_chat_history()

print("SySi Chatbot is ready!")
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
            print("SySi: Goodbye!")
            break

        if command == "clear":
            conversation_history = []
            save_chat_history(conversation_history)
            save_memory_summary("")
            print("SySi: Chat history and memory summary cleared.\n")
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
                "role": "SySi",
                "content": bot_reply,
                "model": used_model
            })

            memory_summary = load_memory_summary()
            conversation_history = summarize_old_history(
                conversation_history,
                memory_summary
            )

            save_chat_history(conversation_history)

            print("\nSySi:", bot_reply)
            print()

        except Exception as error:
            print("\nSySi: Something went wrong.")
            print("Your failed message was not saved to chat history.")
            print("Error:", error)
            print()

    except KeyboardInterrupt:
        print("\nSySi: Chat stopped by user. Goodbye!")
        break