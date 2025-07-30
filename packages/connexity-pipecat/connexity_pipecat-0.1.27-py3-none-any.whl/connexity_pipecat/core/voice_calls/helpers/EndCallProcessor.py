import time

from pipecat.frames.frames import Frame, CancelFrame
from pipecat.processors.frame_processor import FrameProcessor, FrameDirection

from connexity_pipecat.core.voice_calls.helpers.end_call import end_call


class EndCallProcessor(FrameProcessor):
    """
    Processor that monitors the elapsed time since call start and ends the call
    if a specified duration has passed.
    """

    def __init__(self, start_time: float, sid: str, seconds: int):
        """
        Initialize the EndCallProcessor.

        Args:
            start_time (float): The timestamp when the call started.
            sid (str): The SID of the call.
            seconds (int): Number of seconds after which to end the call.
        """
        super().__init__()
        self._start_time = start_time
        self._sid = sid
        self.seconds = seconds

    async def process_frame(self, frame: Frame, direction: FrameDirection) -> None:
        """
        Process each frame and end the call if the elapsed time exceeds the threshold.

        Args:
            frame (Frame): The current frame being processed.
            direction (FrameDirection): The direction of the frame.
        """
        if self.seconds:
            elapsed_time = time.time() - self._start_time
            # Check if the elapsed time in seconds has reached or exceeded the limit
            if int(elapsed_time) >= self.seconds:
                frame = CancelFrame()
                end_call(self._sid)

        await super().process_frame(frame, direction)
        await self.push_frame(frame)
