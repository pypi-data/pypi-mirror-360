from therix.core.pipeline_component import PipelineComponent
from therix.entities.models import ConfigType
from therix.core.constants import API_Endpoint


class Trace(PipelineComponent):
    def __init__(self, config):
        config["host"] = API_Endpoint.TRACE_INGESTION
        
        super().__init__(ConfigType.TRACE_DETAILS, "LANGFUSE", config)
