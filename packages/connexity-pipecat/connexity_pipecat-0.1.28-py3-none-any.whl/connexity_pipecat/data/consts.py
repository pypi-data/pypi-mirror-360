"""Constants and configuration settings loaded from environment variables for the application.

Includes API keys, URLs, prompt types, state enums, supported languages, and phrases used to finalize actions.
"""
import base64
import json
import os
from enum import Enum
from enum import StrEnum
from typing import Literal

from google.oauth2 import service_account

# API keys loaded from environment variables
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
FIREWORKS_API_KEY = os.environ.get("FIREWORKS_API_KEY")
ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY")
DAILY_API_KEY = os.environ.get("DAILY_API_KEY")
CONNEXITY_API_KEY= os.environ.get("CONNEXITY_API_KEY")
DEEPGRAM_API_KEY=os.environ.get("DEEPGRAM_API_KEY")

ELEVENLABS_VOICE_ID=os.getenv("ELEVENLABS_VOICE_ID")
PLAYHT_USER_ID=os.getenv("PLAYHT_USER_ID")
PLAYHT_API_KEY=os.getenv("PLAYHT_API_KEY")
CARTESIA_API_KEY=os.getenv("CARTESIA_API_KEY")
LMNT_API_KEY=os.getenv("LMNT_API_KEY")
RIME_API_KEY=os.getenv("RIME_API_KEY")

b64_creds = os.environ.get("GOOGLE_CREDENTIALS_JSON")
if b64_creds:
    creds_dict = json.loads(base64.b64decode(b64_creds).decode("utf-8"))
    GOOGLE_CREDENTIALS = service_account.Credentials.from_service_account_info(creds_dict)
else:
    GOOGLE_CREDENTIALS = None

os.environ["GIT_PYTHON_REFRESH"] = "quiet"

TOOL_CHECK_SLOT_AVAILABILITY_WEBHOOK_URL = os.environ.get("TOOL_CHECK_SLOT_AVAILABILITY_WEBHOOK_URL")
TOOL_BOOKING_WEBHOOK_URL = os.environ.get("TOOL_BOOKING_WEBHOOK_URL")

CALL_STATUS_URL = os.environ.get("CALL_STATUS_URL")
CONNEXITY_WEBHOOK_URL = os.environ.get(
    "CONNEXITY_WEBHOOK_URL",
    default="https://connexity-gateway-owzhcfagkq-uc.a.run.app/process/pipecat",
)
CONNEXITY_ENV = os.getenv("CONNEXITY_ENV", default="development")

# Time limitation for certain operations, defaulting to 300 seconds (5 minutes)
TIME_LIMITATION_IN_SECONDS = int(
    os.environ.get("TIME_LIMITATION_IN_SECONDS", default=300)
)

# Twilio credentials for communication services
TWILIO_ACCOUNT_ID = os.environ.get("TWILIO_ACCOUNT_ID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
TWILIO_REGION = os.environ.get("TWILIO_REGION")
TWILIO_EDGE = os.environ.get("TWILIO_EDGE")

# Background audio files mapping
BACKGROUND_AUDIO_DICT = {
    "test": "./assets/background_noise_24khz.wav",
    "cafeteria": "./assets/cafe-noise_24khz.wav",
}

# Literal type for supported background noise keys
SupportedBackgroundNoiceLiteral = Literal.__getitem__(
    tuple(BACKGROUND_AUDIO_DICT.keys())
)


class PromptType(str, Enum):
    """Enumeration of supported prompt types for the application."""

    QUICK_RESPONSE = "quick_response"
    AGENT = "agent"
    POST_ANALYSIS = "post_analysis"


class StateEnum(StrEnum):
    """Enumeration of possible states in the application flow."""

    MAIN_AGENT_FLOW = "MainAgentFlow"
    BOOK_APPOINTMENT_FLOW = "BookAppointmentFlow"


# Supported languages mapping
languages = {
    "en": "English",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "zh": "Chinese",
    "ja": "Japanese",
    "pt": "Portuguese",
    "ar": "Arabic",
    "hi": "Hindi",
    "uk": "Ukrainian",
}

# Phrases used to finalize actions by language
finalize_actions_phrases = {
    "en": {"__end__": "Bye."},
    "es": {"__end__": "Adiós."},
    "fr": {"__end__": "Au revoir."},
    "de": {"__end__": "Tschüss."},
    "zh": {"__end__": "再见。"},
    "ja": {"__end__": "さようなら。"},
    "pt": {"__end__": "Tchau."},
    "ar": {"__end__": "مع السلامة."},
    "hi": {"__end__": "अलविदा।"},
    "uk": {"__end__": "До побачення."},
}

supported_models = [
    "OpenAI/gpt-4-0125-preview",
    "OpenAI/gpt-4-turbo-preview",
    "OpenAI/gpt-3.5-turbo-0125",
    "OpenAI/gpt-4o-2024-05-13",
    "OpenAI/gpt-4o-mini-2024-07-18",
    "OpenAI/gpt-4o-2024-08-06",
    "OpenAI/gpt-4o-2024-11-20",
    "Groq/llama3-70b-8192",
    "Groq/llama3-8b-8192",
    "Groq/llama-3.1-8b-instant",
    "Groq/llama-3.1-70b-versatile",
    "Groq/llama-3.1-405b-reasoning",
    "Groq/llama-3.2-3b-preview",
    "Groq/llama-3.2-90b-text-preview",
    "Groq/llama-3.2-90b-vision-preview",
]

SupportedModelsLiteral = Literal.__getitem__(tuple(supported_models))

BASE_MODEL = "gpt-4o-2024-05-13"
BASE_TEMPERATURE = 1
BASE_MAX_TOKENS = 350
BASE_TOP_P = 0.3