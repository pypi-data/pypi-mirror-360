import json
import os
from langfuse.callback import CallbackHandler
from pydantic import Json
from therix.core.version import get_current_version
from therix.core.constants import API_Endpoint


class TherixTraceHandler:
    def __init__(self, therix_api_key ,agent_id=None, session_id=None, metadata=None):
        self.agent_id = agent_id
        self.session_id = session_id
        self.metadata = metadata
        self.therix_api_key = therix_api_key

        # Initialize the internal handler
        self.handler = self._initialize_handler()

    def _initialize_handler(self):

            handler_args = {
                "secret_key": 'some-secret-key',
                "public_key":self.therix_api_key ,
                "host": API_Endpoint.TRACE_INGESTION,
                "trace_name": self.agent_id,
                "session_id": self.session_id,
                "version": get_current_version(),
                "metadata": self.metadata
            }
            

            return CallbackHandler(**handler_args)

      
    def get_handler(self):
        return self.handler





    