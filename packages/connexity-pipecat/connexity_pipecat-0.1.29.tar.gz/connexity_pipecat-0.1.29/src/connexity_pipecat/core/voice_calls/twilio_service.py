import time

from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client
from connexity_pipecat.data.consts import (
    TWILIO_ACCOUNT_ID,
    TWILIO_AUTH_TOKEN,
    TWILIO_REGION,
    TWILIO_EDGE
)


class TwilioClient:
    def __init__(self):
        self.client = Client(TWILIO_ACCOUNT_ID, TWILIO_AUTH_TOKEN,
                             edge=TWILIO_EDGE, region=TWILIO_REGION)

    # Use LLM function calling or some kind of parsing to determine when to transfer away this call
    def transfer_call(self, sid, to_number):
        try:
            call = self.client.calls(sid).update(
                twiml=f"<Response><Dial>{to_number}</Dial></Response>",
            )
            print("Transferred call: ", vars(call))
        except Exception as err:
            print(err)

    def start_call_recording(
            self,
            call_sid,
            *,
            max_retries=8,
            retry_delay_ms=200,
            retryable_statuses=(404, )
    ):
        """
        Try to start recording on a call, retrying up to `max_retries` times.
        - 1st retry: no delay
        - subsequent retries: wait `retry_delay_ms` milliseconds
        """
        for attempt in range(1, max_retries + 1):
            try:
                recording = self.client.calls(call_sid).recordings.create()
                print(f"✅ Recording started (SID: {recording.sid})")
                return recording
            except TwilioRestException as e:
                # Only retry on the statuses you care about
                if e.status in retryable_statuses and attempt < max_retries:
                    # 0 ms for the very first retry, then fixed 100 ms thereafter
                    delay = 0 if attempt == 1 else (retry_delay_ms / 1_000)
                    print(
                        f"⚠️ Attempt {attempt} failed with {e.status}. "
                        f"Retrying in {int(delay*1000)}ms…"
                    )
                    time.sleep(delay)
                    continue
                # out of retries or non-retryable status → bubble up
                print(f"❌ Failed on attempt {attempt}: [{e.status}] {e.msg}")
                return None
        # unreachable
        print(f"Could not start recording after {max_retries} attempts")
        return None

    # Create an outbound call
    def create_phone_call(self, from_number, to_number, server_address):
        call = self.client.calls.create(
            url=f"https://{server_address}/outbound/webhook",
            to=to_number,
            from_=from_number,
        )
        print(f"Calling {to_number} from {from_number}")
        return call.sid
