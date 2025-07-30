from therix.core.pipeline_component import PipelineComponent
from langchain_core.output_parsers import JsonOutputParser
from therix.entities.models import ConfigType

class SystemPromptConfig(PipelineComponent):
    def __init__(self, config):
        super().__init__(ConfigType.SYSTEM_PROMPT, 'SYSTEM_PROMPT', config=config)
 