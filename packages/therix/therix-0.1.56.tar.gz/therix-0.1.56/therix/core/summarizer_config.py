from therix.core.pipeline_component import PipelineComponent
from langchain_core.output_parsers import JsonOutputParser
from therix.entities.models import ConfigType

class SummarizerConfig(PipelineComponent):
    def __init__(self, summarization_type, pydantic_model = None):
        parser = JsonOutputParser(pydantic_object=pydantic_model)
        json_prompt = parser.get_format_instructions()
        config = {
        'pydantic_model' : json_prompt,
        'summarization_type' : summarization_type.value
        }
        super().__init__(ConfigType.SUMMARIZER, 'SUMMARIZER', config)
 