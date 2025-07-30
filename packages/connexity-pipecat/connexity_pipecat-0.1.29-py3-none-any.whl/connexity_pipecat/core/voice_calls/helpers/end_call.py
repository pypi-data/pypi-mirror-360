from twilio.rest import Client
from connexity_pipecat.data.consts import TWILIO_ACCOUNT_ID, TWILIO_AUTH_TOKEN
from pipecat.processors.user_idle_processor import UserIdleProcessor
from pipecat.frames.frames import CancelFrame


def end_call(sid: str) -> None:
    """
    End a Twilio call by setting its status to 'completed'.

    Args:
        sid (str): The SID of the Twilio call to end.
    """
    client = Client(TWILIO_ACCOUNT_ID, TWILIO_AUTH_TOKEN)
    client.calls(sid).update(status="completed")


async def user_idle_end_call(user_idle: UserIdleProcessor) -> None:
    """
    End call on user inactivity
    """
    await user_idle.push_frame(CancelFrame())
