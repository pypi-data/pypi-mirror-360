import os
from therix.services.therix_trace_handler import TherixTraceHandler



therix_trace_handler = TherixTraceHandler(
    therix_api_key = os.getenv('THERIX_API_KEY'),
    agent_id = "some-agent-id",
    session_id= "some-session-id",
    metadata = {
        "metadata": "some-metadata"
    } 
)


handler = therix_trace_handler.get_handler()




