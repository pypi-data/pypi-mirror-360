from pipecat.audio.vad.vad_analyzer import VADParams

from connexity_pipecat.core.config import get_config


def initiate_vad_params(vad_params: dict) -> VADParams:
    """
    Initialize VAD (Voice Activity Detection) parameters from the config.

    Returns:
        VADParams: An instance of VADParams with values from the configuration.

    Raises:
        ValueError: If required VAD parameters are missing in the configuration.
    """
    required_keys = {"confidence", "min_volume", "start_secs", "stop_secs"}

    # Check if any required key is missing in the vad_params
    if any(key not in vad_params for key in required_keys):
        raise ValueError("invalid vad_params config")

    # Initialize and return VADParams with the given configuration
    return VADParams(**vad_params)
