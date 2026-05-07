import time
from google import genai
from config import API_KEY, MODEL_LIST

client = genai.Client(api_key=API_KEY)


def generate_reply_with_fallback(prompt, show_fallback_messages=True):
    last_error = None

    for index, model_name in enumerate(MODEL_LIST):
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt
            )

            return response.text, model_name

        except Exception as error:
            error_text = str(error)
            last_error = error

            is_quota_error = "RESOURCE_EXHAUSTED" in error_text or "429" in error_text
            is_busy_error = "UNAVAILABLE" in error_text or "503" in error_text
            is_not_found_error = "NOT_FOUND" in error_text or "404" in error_text
            is_permission_error = "PERMISSION_DENIED" in error_text or "403" in error_text

            recoverable_error = (
                is_quota_error
                or is_busy_error
                or is_not_found_error
                or is_permission_error
            )

            if recoverable_error and index < len(MODEL_LIST) - 1:
                next_model = MODEL_LIST[index + 1]

                if show_fallback_messages:
                    if is_quota_error:
                        print(f"SySi: {model_name} quota reached. Trying {next_model}...")
                    elif is_busy_error:
                        print(f"SySi: {model_name} is busy. Trying {next_model}...")
                    elif is_not_found_error:
                        print(f"SySi: {model_name} is not available. Trying {next_model}...")
                    elif is_permission_error:
                        print(f"SySi: {model_name} is not allowed for this API key. Trying {next_model}...")

                time.sleep(1)
                continue

            raise error

    raise Exception(f"All models failed. Last error: {last_error}")