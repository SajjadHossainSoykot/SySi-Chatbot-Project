import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("GEMINI_API_KEY not found. Please add it to your .env file.")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

HISTORY_FILE = os.path.join(BASE_DIR, "chat_history.json")
SUMMARY_FILE = os.path.join(BASE_DIR, "memory_summary.txt")

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

MAX_RECENT_MESSAGES = 8
SUMMARY_TRIGGER_MESSAGES = 16