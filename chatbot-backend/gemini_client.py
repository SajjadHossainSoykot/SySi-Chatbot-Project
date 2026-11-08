import time
from google import genai
from config import API_KEY, MODEL_LIST, RETRY_DELAY_SECONDS

# Cached client instance
_client = None


def get_client():
    """Retrieve or initialize the Google GenAI client instance."""
    global _client
    if _client is None:
        if not API_KEY:
            raise ValueError("GEMINI_API_KEY is not set.")
        _client = genai.Client(api_key=API_KEY)
    return _client


# Default client instance for backward compatibility
client = get_client() if API_KEY else None


def _extract_response_text(response):
    """Safely extract generated text from response, handling candidates and parts."""
    if response is None:
        return None

    # Try response.text attribute first
    try:
        text = response.text
        if text and text.strip():
            return text.strip()
    except Exception:
        pass

    # Fallback to candidates and parts if response.text raised or was empty
    try:
        if response.candidates:
            first_candidate = response.candidates[0]
            if first_candidate.content and first_candidate.content.parts:
                parts_text = [
                    part.text for part in first_candidate.content.parts
                    if hasattr(part, "text") and part.text
                ]
                combined = "".join(parts_text).strip()
                if combined:
                    return combined
    except Exception:
        pass

    return None


def generate_reply_with_fallback(prompt, show_fallback_messages=True):
    """
    Attempt to generate a response across the configured model pipeline.
    If a model fails due to quota, downtime, deprecation, or network errors,
    it automatically falls back to the next model in MODEL_LIST.
    """
    ai_client = get_client()
    last_error = None

    for index, model_name in enumerate(MODEL_LIST):
        try:
            response = ai_client.models.generate_content(
                model=model_name,
                contents=prompt
            )

            response_text = _extract_response_text(response)
            if not response_text:
                raise ValueError(f"Model {model_name} returned an empty response.")

            return response_text, model_name

        except Exception as error:
            error_text = str(error)
            last_error = error

            # Categorize the error to provide educational feedback
            is_quota_error = "RESOURCE_EXHAUSTED" in error_text or "429" in error_text
            is_busy_error = (
                "UNAVAILABLE" in error_text
                or "503" in error_text
                or "500" in error_text
                or "INTERNAL" in error_text
            )
            is_timeout_error = (
                "DEADLINE_EXCEEDED" in error_text
                or "504" in error_text
                or "timeout" in error_text.lower()
            )
            is_not_found_error = (
                "NOT_FOUND" in error_text
                or "404" in error_text
                or "not found" in error_text.lower()
            )
            is_permission_error = (
                "PERMISSION_DENIED" in error_text
                or "403" in error_text
            )
            is_network_error = (
                "ConnectError" in error_text
                or "RemoteProtocolError" in error_text
                or "nodename nor servname" in error_text
            )
            is_empty_response = "returned an empty response" in error_text

            recoverable_error = (
                is_quota_error
                or is_busy_error
                or is_timeout_error
                or is_not_found_error
                or is_permission_error
                or is_network_error
                or is_empty_response
            )

            # If error is recoverable and another model is available, fall back
            if recoverable_error and index < len(MODEL_LIST) - 1:
                next_model = MODEL_LIST[index + 1]

                if show_fallback_messages:
                    if is_quota_error:
                        print(f"SySi: {model_name} quota reached. Trying {next_model}...")
                    elif is_busy_error:
                        print(f"SySi: {model_name} is busy or temporarily unavailable. Trying {next_model}...")
                    elif is_timeout_error:
                        print(f"SySi: {model_name} timed out. Trying {next_model}...")
                    elif is_not_found_error:
                        print(f"SySi: {model_name} is discontinued or not found. Trying {next_model}...")
                    elif is_permission_error:
                        print(f"SySi: {model_name} is not permitted for this API key. Trying {next_model}...")
                    elif is_network_error:
                        print(f"SySi: Network connection issue with {model_name}. Trying {next_model}...")
                    elif is_empty_response:
                        print(f"SySi: {model_name} returned an empty reply. Trying {next_model}...")

                time.sleep(RETRY_DELAY_SECONDS)
                continue

            # If not recoverable or this was the last model, re-raise the error
            raise error

    raise Exception(f"All models in fallback pipeline failed. Last error: {last_error}")
