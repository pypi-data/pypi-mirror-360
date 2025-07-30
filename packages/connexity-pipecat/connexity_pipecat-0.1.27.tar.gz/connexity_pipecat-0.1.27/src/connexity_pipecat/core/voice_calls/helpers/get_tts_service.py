import os

from pipecat.services.elevenlabs.tts import ElevenLabsTTSService
from pipecat.services.playht.tts import PlayHTTTSService
from pipecat.services.cartesia.tts import CartesiaTTSService
from pipecat.services.lmnt.tts import LmntTTSService
from pipecat.services.rime.tts import RimeTTSService
from pipecat.transcriptions.language import Language

from connexity_pipecat.core.config import get_config
from connexity_pipecat.data.consts import ELEVENLABS_API_KEY, ELEVENLABS_VOICE_ID, PLAYHT_USER_ID, PLAYHT_API_KEY, \
    CARTESIA_API_KEY, LMNT_API_KEY, RIME_API_KEY


def get_tts_service(tts_settings: dict) -> object:
    """
    Return the appropriate TTS service instance based on the voice provider specified in call_info.

    Args:
        call_info (dict): Dictionary containing agent settings, including voice provider and voice ID or URL.

    Returns:
        object: An instance of a TTS service class.
    """
    voice_provider = tts_settings.get(
        "voice_provider", "elevenlabs"
    )

    if voice_provider not in ["elevenlabs", "playht", "cartesia", "lmnt", "rime"]:
        raise ValueError(
            f"Invalid voice_provider: {voice_provider}. It must be either 'elevenlabs', 'playht', 'lmnt', 'rime' or 'cartesia'."
        )

    if voice_provider == "elevenlabs":
        return ElevenLabsTTSService(
            api_key=ELEVENLABS_API_KEY,
            voice_id=tts_settings.get("voice_id", ELEVENLABS_VOICE_ID),
        )
    elif voice_provider == "playht":
        return PlayHTTTSService(
            user_id=PLAYHT_USER_ID,
            api_key=PLAYHT_API_KEY,
            voice_url=tts_settings.get("voice_id"),
            voice_engine="PlayDialog",
            params=PlayHTTTSService.InputParams(
                language=Language.EN,
                speed=1.0
            )
        )
    elif voice_provider == "cartesia":
        return CartesiaTTSService(
            api_key=CARTESIA_API_KEY,
            voice_id=tts_settings.get("voice_id"),
            params=CartesiaTTSService.InputParams(
                language=Language.EN,
                speed="slow",
                emotion=["positivity:high", "curiosity"]
            )
        )
    elif voice_provider == "rime":
        return RimeTTSService(
            api_key=RIME_API_KEY,
            voice_id=tts_settings.get("voice_id"),
            model=tts_settings.get("model"),
            params=RimeTTSService.InputParams(
                language=Language.EN,
                pause_between_brackets=True,
                speed_alpha=1.2)
        )
    elif voice_provider == "lmnt":
        return LmntTTSService(
            api_key=LMNT_API_KEY,
            voice_id=tts_settings.get("voice_id"),
            sample_rate=16000,
        )


