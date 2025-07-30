twiml_template_inbound = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Connect>
        <Stream url="wss://{wss_url}/ws"></Stream>
    </Connect>
    <Pause length="40"/>
</Response>
"""


twiml_template_outbound = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Connect>
    <Stream url="wss://{wss_url}/ws"></Stream>
  </Connect>
  <Pause length="40"/>
</Response>
"""

twiml_template_outbound_with_play = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Play>{audio_url}</Play>
  <Connect>
    <Stream url="wss://{wss_url}/ws"></Stream>
  </Connect>
  <Pause length="40"/>
</Response>
"""
