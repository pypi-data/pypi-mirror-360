from therix.core.pipeline_component import PipelineComponent
from therix.entities.models import ConfigType

class PIIFilterConfig(PipelineComponent):
    def __init__(self, config):
        super().__init__(ConfigType.PII_FILTER, 'PII_FILTER', config)