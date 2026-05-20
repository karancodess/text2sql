import os
from pathlib import Path

def _load_dotenv_fallback():
    # If python-dotenv is installed, prefer it
    try:
        from dotenv import load_dotenv
        load_dotenv()
        return
    except Exception:
        pass

    # Fallback: read .env in project root if exists
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            if not line or line.strip().startswith("#"):
                continue
            if "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())


_load_dotenv_fallback()


def get_openai_api_key():
    """Return the OpenAI API key from environment or None."""
    return os.environ.get("OPENAI_API_KEY")


def get_gemini_api_key():
    """Return the Gemini API key from environment, checking common variants."""
    # prefer canonical uppercase underscore
    for key in ("GEMINI_API_KEY", "Gemini_API_Key", "Gemini_APIKEY", "OPENAI_API_KEY"):
        val = os.environ.get(key)
        if val:
            return val
    return None


def get_model_api_key():
    """Generic accessor for model API key (Gemini preferred)."""
    return get_gemini_api_key() or get_openai_api_key()
