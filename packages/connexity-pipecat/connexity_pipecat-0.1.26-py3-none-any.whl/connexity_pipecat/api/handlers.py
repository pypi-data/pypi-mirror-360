"""
Voice-AI FastAPI handlers and helpers.

This module exposes several FastAPI-compatible coroutine handlers used by the
Connexity voice-AI stack:

*  Initiating inbound / outbound Twilio calls.
*  Handling Twilio web-hook callbacks (TwiML & WebSocket media).
*  Plain HTTP inference endpoints for text-only chat.
*  Utility callbacks for updating call status in Redis‐like cache.

The codebase is large, so the most valuable improvements concentrate on:

*   Import ordering & deduplication (PEP 8 § Imports).
*   Type annotations, doc-strings and inline comments.
*   Removal of unused / duplicate imports.
"""

from __future__ import annotations

# ──────────────────────────────── stdlib ──────────────────────────────────────
import json
import sys
import time
from typing import Any, Dict, Optional

from connexity.metrics.pipecat import ConnexityTwilioObserver
from deepgram import LiveOptions
# ────────────────────────────── 3rd-party ─────────────────────────────────────
from fastapi import Request, WebSocket
from loguru import logger
from pipecat.audio.mixers.soundfile_mixer import SoundfileMixer
from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.serializers.twilio import TwilioFrameSerializer
from pipecat.services.deepgram.stt import DeepgramSTTService
from pipecat.transports.network.fastapi_websocket import FastAPIWebsocketTransport, FastAPIWebsocketParams
from pipecat.processors.user_idle_processor import UserIdleProcessor
from starlette.responses import HTMLResponse, JSONResponse
from starlette.websockets import WebSocketDisconnect

from pipecat.frames.frames import (
    EndFrame, TTSSpeakFrame, LLMMessagesFrame,
)
# Metrics collection
from pipecat.frames.frames import MetricsFrame
from pipecat.pipeline.task_observer import FramePushed  # add near other imports
from pipecat.metrics.metrics import (
    TTFBMetricsData,
    ProcessingMetricsData,
    LLMUsageMetricsData,
)
from pipecat.observers.base_observer import BaseObserver
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.aggregators.openai_llm_context import (
    OpenAILLMContext,
    OpenAILLMContextFrame,
)
from pipecat.services.openai.llm import OpenAILLMService

from connexity_pipecat.core.voice_calls.helpers.EndCallProcessor import EndCallProcessor
from connexity_pipecat.core.voice_calls.helpers.get_tts_service import get_tts_service
from connexity_pipecat.core.config import get_config
from connexity_pipecat.core.tools import get_tool_manager
from connexity_pipecat.core.voice_calls.helpers.initiate_vad_params import initiate_vad_params
from connexity_pipecat.core.prompts import get_prompt
from connexity_pipecat.data.consts import (
    OPENAI_API_KEY,
    PromptType, BACKGROUND_AUDIO_DICT, CONNEXITY_API_KEY, TWILIO_ACCOUNT_ID, TWILIO_AUTH_TOKEN, DEEPGRAM_API_KEY, CONNEXITY_ENV
)
from connexity_pipecat.data.schemas import (
    RequestBody,
    RequestBodyForVoiceAI,
    create_agent_inputs,
)
from connexity_pipecat.data.validators import (
    is_valid_end_call_time,
    is_valid_iso_language
)
from connexity_pipecat.core.voice_calls.templates import (
    twiml_template_inbound,
    twiml_template_outbound,
    twiml_template_outbound_with_play,
)
from connexity_pipecat.core.voice_calls.twilio_service import TwilioClient
from connexity_pipecat.helpers.get_model import get_llm_service
from connexity_pipecat.helpers.append_message_history_to_function import append_message_history_to_function
from connexity_pipecat.helpers.perform_post_call_analytics import perform_post_call_analysis

from connexity_pipecat.core.voice_calls.helpers.end_call import user_idle_end_call

# ────────────────────────────── logging ───────────────────────────────────────
# Remove any default handlers (Loguru raises if id 0 does not exist)
logger.remove()
logger.add(sys.stderr, level="DEBUG")


# ─────────────────────────── module globals ───────────────────────────────────
# Helper for metrics collection in debug_inference()
class _MetricsCollector(BaseObserver):
    """
    Observer that stores every MetricsFrame pushed through the pipeline so we
    can expose latency / token‑usage in HTTP responses.
    """

    def __init__(self) -> None:
        # Ensure BaseObserver sets up required internal state (e.g. `_name`)
        super().__init__()
        self.samples: list = []

    async def on_push_frame(self, data: FramePushed):  # noqa: D401
        """Handle a frame‑pushed event coming from PipelineTaskObserver."""
        if isinstance(data.frame, MetricsFrame):
            # pipecat<=0.67 stores payload under `.data`, newer snapshots use `.metrics`
            metrics_payload = getattr(data.frame, "metrics", None) or getattr(
                data.frame, "data", [])
            self.samples.extend(metrics_payload)


twilio_client = TwilioClient()
#: In-memory scratch-pad storing per-call data (non-persistent, process-local).
data_storage: Dict[str, Dict[str, Any]] = {}


# =============================================================================
#                          Outbound call handlers
# =============================================================================


async def initiate_phone_call(request: Request, request_body: RequestBodyForVoiceAI, prefix: Optional[str] = None) -> Any:
    """
    Trigger an **outbound** Twilio voice call and stash the request details
    for use by subsequent WebSocket media streams.

    Args:
        request:
        prefix:
        request_body: JSON payload received from the orchestrating
            application / front-end.

    Returns:
        • ``JSONResponse`` with *403 / 500* on failure.

        • ``dict``     with *sid*, *from*, *to* on success (HTTP 200).
    """
    host = request.headers["host"]
    webhook_url = f"{host}/{prefix}" if prefix else host

    # ─────────────── validation ───────────────
    language = request_body.language
    if not is_valid_iso_language(language):
        return JSONResponse(
            status_code=403,
            content={"message": f"Invalid language {language!r}"},
        )

    if not is_valid_end_call_time(request_body.end_call_seconds):
        return JSONResponse(
            status_code=403,
            content={"message": "end_call_seconds must be ≥ 60"},
        )

    # ─────────────── Twilio call ───────────────
    try:
        sid = twilio_client.create_phone_call(
            request_body.from_number,
            request_body.to_number,
            webhook_url
        )
    except Exception as exc:  # pragma: no-cover – Twilio raises dozens of types
        return JSONResponse(
            status_code=500,
            content={"message": f"Internal Server Error: {exc}"},
        )

    # cache everything we'll need when WebSocket media starts streaming
    data_storage[sid] = request_body.model_dump()
    data_storage[sid]["to"] = request_body.to_number
    data_storage[sid]["from"] = request_body.from_number
    data_storage[sid].update({"sid": sid, "call_type": "outbound"})

    return {"sid": sid, "from": request_body.from_number, "to": request_body.to_number}


async def outbound_webhook(request: Request, prefix: Optional[str] = None) -> HTMLResponse:
    """
    Twilio *TwiML* webhook for **outbound** calls – returns an XML document
    instructing Twilio to connect to our WebSocket media stream.

    Args:
        prefix:
        request: FastAPI Request (x-www-form-urlencoded).

    Returns:
        TwiML XML wrapped in :class:`starlette.responses.HTMLResponse`.
    """
    host = request.headers.get("host")
    wss_url = f"{host}/{prefix}" if prefix else host
    data = await request.form()
    sid = data.get("CallSid")
    call_info = data_storage.get(sid, {})
    audio_url = call_info.get("play_audio_url")

    xml_template = (
        twiml_template_outbound_with_play
        if audio_url
        else twiml_template_outbound
    )

    formatted_xml = xml_template.format(audio_url=audio_url, wss_url=wss_url)

    return HTMLResponse(content=formatted_xml, media_type="application/xml")


async def websocket_endpoint(websocket: WebSocket, prefix: Optional[str] = None) -> None:
    """
    Handle Twilio media stream for inbound and outbound calls.

    The first two messages sent by Twilio are JSON control frames
    (``start`` / stream info). After that we switch to 8 kHz 16-bit
    mono µ-law *audio/PCMU*.
    """
    call_sid = None
    try:
        await websocket.accept()
        start_data = websocket.iter_text()
        await start_data.__anext__()  # Skip first message
        call = json.loads(await start_data.__anext__())
        print(call, flush=True)
        call_sid = call["start"]["callSid"]
        twilio_client.start_call_recording(call_sid)
        stream_sid = call["start"]["streamSid"]
        call_info = data_storage.get(call_sid, {})
        print("WebSocket connection accepted")

        start_time = time.time()

        selected_sound = call_info.get("background_noise")

        default_sound = (
            selected_sound if selected_sound in BACKGROUND_AUDIO_DICT.keys() else "test"
        )

        soundfile_mixer = SoundfileMixer(
            sound_files=BACKGROUND_AUDIO_DICT,
            default_sound=default_sound,
            volume=0.5,
        )

        config = get_config(prefix)
        raw_vad_params = config.get("vad_params")
        vad_params = initiate_vad_params(raw_vad_params)

        transport = FastAPIWebsocketTransport(
            websocket=websocket,
            params=FastAPIWebsocketParams(
                audio_out_enabled=True,
                audio_out_mixer=(
                    soundfile_mixer if call_info.get(
                        "background_noise") else None
                ),
                add_wav_header=False,
                audio_in_enabled=True,
                vad_analyzer=SileroVADAnalyzer(params=vad_params),
                audio_in_passthrough=True,
                serializer=TwilioFrameSerializer(stream_sid, call_sid=call_info.get("sid"),
                                                 account_sid=TWILIO_ACCOUNT_ID,
                                                 auth_token=TWILIO_AUTH_TOKEN)
            ),
        )

        call_type = call_info.get("call_type")
        cfg_defaults = config.get("agent_inputs")
        if call_type == "outbound":
            agent_inputs = create_agent_inputs(cfg_defaults, call_info.get("agent_inputs"))
            llm_service = OpenAILLMService(
                model=config["llm"]["main"]["model"],
                params=OpenAILLMService.InputParams(
                    top_p=0.05,
                    temperature=1,
                    max_tokens=1000
                ),
                api_key=OPENAI_API_KEY
            )
        else:
            agent_inputs = create_agent_inputs(cfg_defaults)
            llm_service = get_llm_service(
                vendor=config["llm"]["main"]["vendor"],
                model_name=config["llm"]["main"]["model"]
            )

        if agent_inputs.translate_prompt:
            prompt_str = get_prompt(
                PromptType.AGENT,
                config,
                agent_inputs.language_code,
            )
        else:
            prompt_str = get_prompt(
                PromptType.AGENT,
                config,
            )

        prompt = prompt_str.format(**agent_inputs.model_dump())

        message_history = [{"role": "system", "content": prompt}]

        if start_message := config["start_message"]:
            start_message = start_message.format(**agent_inputs.model_dump())
            message_history.append(
                {"role": "assistant", "content": start_message})

        if agent_inputs.language_code != "en":
            live_options = LiveOptions(
                model="nova-2-general",
                language=agent_inputs.language_code,
            )
        else:
            live_options = None

        stt = DeepgramSTTService(
            api_key=DEEPGRAM_API_KEY, live_options=live_options
        )
        tts_settings = config.get("tts")
        tts = get_tts_service(tts_settings)

        tools_meta = get_tool_manager().get_tools_schema(config["tools"])
        function_handlers = get_tool_manager().get_handlers(config["tools"])

        context = OpenAILLMContext(message_history, tools=tools_meta)
        context_aggregator = llm_service.create_context_aggregator(context)

        for name, raw_handler in function_handlers.items():
            llm_service.register_function(
                name,
                append_message_history_to_function(raw_handler, context)
            )

        pipeline_steps_list = [
            transport.input(),
            stt,
            context_aggregator.user(),
            llm_service,
            tts,
            transport.output(),
            context_aggregator.assistant(),
        ]

        if "use_idle_processor" in config and config["use_idle_processor"]["is_on"]:
            user_idle = UserIdleProcessor(
                callback=user_idle_end_call,
                timeout=config["use_idle_processor"]["timeout"],
            )
            stt_index = pipeline_steps_list.index(stt)
            pipeline_steps_list.insert(stt_index+1, user_idle)

        if "call_max_duration" in config and config["call_max_duration"]:
            end_call = EndCallProcessor(
                start_time=start_time, sid=call_info.get("sid"), seconds=config["call_max_duration"]
            )
            pipeline_steps_list.append(end_call)

        pipeline = Pipeline(pipeline_steps_list)

        observers = []
        if config["use_connexity_observer"]:
            connexity_metrics_observer = ConnexityTwilioObserver()
            await connexity_metrics_observer.initialize(sid=call_sid,
                                                        api_key=CONNEXITY_API_KEY,
                                                        agent_id=config["agent_id"],
                                                        agent_phone_number=call_info.get("to"),
                                                        user_phone_number=call_info.get("from"),
                                                        phone_call_provider='twilio',
                                                        twilio_client=twilio_client.client,
                                                        voice_provider=config["tts"]["voice_provider"],
                                                        llm_model=config["llm"]["utils"]["model"],
                                                        llm_provider=config["llm"]["utils"]["vendor"],
                                                        call_type=call_info.get('call_type'),
                                                        transcriber='deepgram',
                                                        vad_params=vad_params,
                                                        env=CONNEXITY_ENV,
                                                        vad_analyzer="silero"
                                                        )

            observers.append(connexity_metrics_observer)

        task = PipelineTask(
            pipeline,
            params=PipelineParams(
                audio_in_sample_rate=config["pipeline_settings"].get(
                    "audio_in_sample_rate", 8000),
                allow_interruptions=config["pipeline_settings"].get(
                    "allow_interruptions", True),
                enable_metrics=config["pipeline_settings"].get(
                    "enable_metrics", True),
                report_only_initial_ttfb=config["pipeline_settings"].get(
                    "report_only_initial_ttfb", True),
            ),
            observers=observers
        )

        @transport.event_handler("on_client_connected")
        async def on_client_connected(transport, client):
            """
            Sends a greeting or initial message when the client connects.
            """
            if start_message := config["start_message"]:
                start_message_formatted = start_message.format(
                    **agent_inputs.model_dump())
                await task.queue_frames([TTSSpeakFrame(start_message_formatted)])
            else:
                await task.queue_frames([LLMMessagesFrame(message_history)])

        @transport.event_handler("on_client_disconnected")
        async def on_client_disconnected(transport, client):
            """
            Cancels the task and marks call as completed on disconnect.
            """
            await task.cancel()

            if "perform_post_call_analysis" in config and config["perform_post_call_analysis"]:
                conversation_history = [m.copy() for m in context.messages]
                arguments = {"messages_history": conversation_history}
                result = await perform_post_call_analysis(arguments, config)

                logger.info(f"Post call analysis result:\n{json.dumps(json.loads(result), indent=2, sort_keys=True)}\n")

        runner = PipelineRunner(handle_sigint=False, force_gc=True)

        await runner.run(task)

    except WebSocketDisconnect:
        print(f"LLM WebSocket disconnected for {call_sid}")
    except Exception as e:
        print(f"Error in LLM WebSocket: {e} for {call_sid}")
        await websocket.close(1011, "Server error")


# =============================================================================
#                          Inbound call handlers
# =============================================================================


async def inbound_webhook(request: Request, prefix: Optional[str] = None) -> HTMLResponse:
    """
    Twilio *TwiML* webhook for **inbound** PSTN calls.

    Args:
        prefix:
        request: FastAPI Request (JSON or x-www-form-urlencoded).

    Returns:
        XML response instructing Twilio to connect to our WebSocket.
    """
    host = request.headers.get("host")

    if request.headers.get("content-type", "").startswith("application/json"):
        form: Dict[str, Any] = await request.json()
    else:
        form = dict(await request.form())

    sid = form.get("CallSid")
    data_storage[sid] = {
        "to": form.get("To"),
        "from": form.get("From"),
        "sid": sid,
        "inputs": form.get("inputs", {}),
        "agent_settings": form.get("agent_settings", {}),
        "call_type": "inbound",
        "language": "en",
        "end_call_seconds": form.get("end_call_seconds") or True,
        "prompt": "",
    }

    formatted_xml = twiml_template_inbound.format(
        wss_url=f"{host}/{prefix}" if prefix else host,
    )
    return HTMLResponse(content=formatted_xml, media_type="application/xml")


async def platform_inference(request_body: RequestBody, prefix: Optional[str] = None) -> JSONResponse:
    """
    One-shot plain-text inference (no streaming) for embedding
    Connexity Agent into messaging platforms (Slack, Discord …).

    * Builds 'system' prompt using :data:`PromptType.AGENT`.
    * Registers **function-call** handlers.
    * Returns assistant message and cached usage metrics.
    """
    # extend chat history with the new user turn
    conversation_history = list(request_body.history or [])
    conversation_history.append(
        {"role": "user", "content": request_body.query})

    config = get_config(prefix)

    llm_service = get_llm_service(
        vendor=config["llm"]["main"]["vendor"],
        model_name=config["llm"]["main"]["model"]
    )

    cfg_defaults = config["agent_inputs"]
    agent_inputs = create_agent_inputs(cfg_defaults)
    system_prompt = get_prompt(PromptType.AGENT, agent_inputs.language_code).format(
        **agent_inputs.model_dump()
    )

    message_history = [
        {"role": "system", "content": system_prompt}, *conversation_history]

    tools_meta = get_tool_manager().get_tools_schema(config["tools"])
    function_handlers = get_tool_manager().get_handlers(config["tools"])
    for name, handler in function_handlers.items():
        llm_service.register_function(name, handler)

    context = OpenAILLMContext(message_history, tools=tools_meta)
    assistant_aggr = llm_service.create_context_aggregator(context).assistant()

    pipeline = Pipeline([llm_service, assistant_aggr])
    collector = _MetricsCollector()

    task = PipelineTask(
        pipeline,
        params=PipelineParams(
            allow_interruptions=config["pipeline_settings"].get(
                "allow_interruptions", True),
            enable_metrics=config["pipeline_settings"].get(
                "enable_metrics", True),
            report_only_initial_ttfb=config["pipeline_settings"].get(
                "report_only_initial_ttfb", True),
        ),
        observers=[collector],
        check_dangling_tasks=False,  # suppress "coroutine never awaited"
    )

    await task.queue_frames([OpenAILLMContextFrame(context), EndFrame()])
    await PipelineRunner(handle_sigint=False, force_gc=True).run(task)

    # ---------------------------  harvest metrics ----------------------------
    latency: dict[str, dict[str, float]] = {}
    llm_usage: dict[str, dict[str, int]] = {}

    for metric in collector.samples:
        service = (
            metric.model
            if getattr(metric, "model", None)
            else metric.processor.split("#")[0].replace("LLMService", "").lower()
        )

        if isinstance(metric, TTFBMetricsData):
            latency.setdefault(service, {})[
                "time_to_first_byte"] = metric.value
        elif isinstance(metric, ProcessingMetricsData):
            latency.setdefault(service, {})[
                "generation_seconds"] = metric.value
        elif isinstance(metric, LLMUsageMetricsData):
            llm_usage[service] = metric.value.model_dump()

    latency = {
        name: stats
        for name, stats in latency.items()
        if any(v > 0 for v in stats.values())
    }

    return JSONResponse(
        content={
            "model": get_config(prefix)["llm"]["main"]["model"],
            "message": context.messages[-1]["content"].replace('  ', 'A0TEMP').replace(' ', '').replace('A0TEMP', ' '),
            "steps": [],
            "error": None,
            "metadata": {
                "generated_messages_per_turn": context.messages[len(conversation_history) + 1:],
                "metrics": {
                    "latency": latency,
                    "llm_usage": llm_usage,
                },
            },
            "body": {},
        }
    )
