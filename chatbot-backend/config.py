import os
from dotenv import load_dotenv

# Base directory for the backend
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Look for .env in the backend directory first, then root
ENV_FILE = os.path.join(BASE_DIR, ".env")
if os.path.exists(ENV_FILE):
    load_dotenv(dotenv_path=ENV_FILE)
else:
    load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY or API_KEY.strip() == "your_gemini_api_key_here":
    raise ValueError(
        "GEMINI_API_KEY not found or unconfigured. "
        "Please create a .env file inside 'chatbot-backend/' with: "
        "GEMINI_API_KEY=your_actual_gemini_api_key"
    )

# File paths
HISTORY_FILE = os.path.join(BASE_DIR, "chat_history.json")
SUMMARY_FILE = os.path.join(BASE_DIR, "memory_summary.txt")

# ==============================================================================
# Model Fallback Pipeline (Updated for Discontinued Models)
# ==============================================================================
# Note: Google has discontinued and shut down the Gemini 1.5 series (gemini-1.5-flash
# and gemini-1.5-flash-8b). Those endpoints now return 404/Not Found.
#
# Replacements & Current Active Models:
# - gemini-3.1-flash-lite: Fast, ultra-low latency, and quota-friendly (Primary).
# - gemini-3.8-flash: State-of-the-art Flash generation with high reasoning & coding.
# - gemini-3.5-flash: High-speed multimodal workhorse.
# - gemini-2.5-flash: Reliable standard fallback.
# - gemini-2.5-flash-lite: Lightweight 2.5 series fallback.
# - gemma-3-*-it: Google's instruction-tuned Gemma 3 open models (27B, 12B, 4B).
# ==============================================================================
DEFAULT_MODEL_LIST = [
    "gemini-3.1-flash-lite",  # Primary: Fast, lightweight, quota-friendly
    "gemini-3.8-flash",       # Fallback 1: Latest high-intelligence Flash model
    "gemini-3.5-flash",       # Fallback 2: High-speed multimodal reasoning
    "gemini-2.5-flash",       # Fallback 3: Stable production model
    "gemini-2.5-flash-lite",  # Fallback 4: Lightweight 2.5 series
    "gemma-3-27b-it",         # Fallback 5: Instruction-tuned Gemma 3 (27B)
    "gemma-3-12b-it",         # Fallback 6: Instruction-tuned Gemma 3 (12B)
    "gemma-3-4b-it",          # Fallback 7: Instruction-tuned Gemma 3 (4B)
]

# Allow custom primary model or full list override via environment variables if desired
_custom_models = os.getenv("GEMINI_MODELS")
_primary_override = os.getenv("GEMINI_PRIMARY_MODEL")

if _custom_models:
    MODEL_LIST = [m.strip() for m in _custom_models.split(",") if m.strip()]
elif _primary_override:
    if _primary_override in DEFAULT_MODEL_LIST:
        MODEL_LIST = [_primary_override] + [m for m in DEFAULT_MODEL_LIST if m != _primary_override]
    else:
        MODEL_LIST = [_primary_override] + DEFAULT_MODEL_LIST
else:
    MODEL_LIST = list(DEFAULT_MODEL_LIST)

# Memory & Conversation parameters
MAX_RECENT_MESSAGES = 8
SUMMARY_TRIGGER_MESSAGES = 16
RETRY_DELAY_SECONDS = 1
