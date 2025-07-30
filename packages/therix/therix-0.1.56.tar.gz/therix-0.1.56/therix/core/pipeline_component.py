from ..entities.models import ConfigType

class PipelineComponent:
    def __init__(self, component_type, name, config):
        if component_type not in ConfigType:
            raise ValueError(f"Invalid component type: {component_type}")
        self.type = ConfigType(component_type)
        self.name = name
        self.config = config
    
    def __str__(self):
        return f"{self.type.name} - {self.name} - {self.config}"

class DataSource(PipelineComponent):
    def __init__(self, name, config):
        super().__init__(ConfigType.INPUT_SOURCE, name, config)

class EmbeddingModel(PipelineComponent):
    def __init__(self, name, config):
        super().__init__(ConfigType.EMBEDDING_MODEL, name, config)

class InferenceModel(PipelineComponent):
    def __init__(self, name, config):
        super().__init__(ConfigType.INFERENCE_MODEL, name, config)

class OutputSource(PipelineComponent):
    def __init__(self, name, config):
        super().__init__(ConfigType.OUTPUT_SOURCE, name, config)

class TraceDetails(PipelineComponent):
    def __init__(self, name, config):
        super().__init__(ConfigType.TRACE_DETAILS, name, config)

class DocumentIntelligence(PipelineComponent):
    def __init__(self, config):
        super().__init__(ConfigType.DOCUMENT_INTELLIGENCE, 'DOCUMENT_INTELLIGENCE', config)