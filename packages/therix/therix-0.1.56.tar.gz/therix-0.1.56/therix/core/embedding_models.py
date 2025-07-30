from therix.core.constants import EmbeddingModelMaster
from therix.core.pipeline_component import EmbeddingModel


class OpenAITextAdaEmbeddingModel(EmbeddingModel):
    def __init__(self, **kwargs):
        super().__init__(name=EmbeddingModelMaster.OPENAI_TEXT_ADA, **kwargs)


class OpenAITextEmbedding3SmallEmbeddingModel(EmbeddingModel):
    def __init__(self, **kwargs):
        super().__init__(
            name=EmbeddingModelMaster.OPENAI_TEXT_EMBEDDING_3_SMALL, **kwargs
        )


class OpenAITextEmbedding3LargeEmbeddingModel(EmbeddingModel):
    def __init__(self, **kwargs):
        super().__init__(
            name=EmbeddingModelMaster.OPENAI_TEXT_EMBEDDING_3_LARGE, **kwargs
        )


class AzureOpenAIEmbedding3SmallEmbeddingModel(EmbeddingModel):
    def __init__(self, **kwargs):
        super().__init__(
            name=EmbeddingModelMaster.AZURE_TEXT_EMBEDDING_3_SMALL, **kwargs
        )


class AzureOpenAITextAdaEmbeddingModel(EmbeddingModel):
    def __init__(self, **kwargs):
        super().__init__(name=EmbeddingModelMaster.AZURE_TEXT_ADA, **kwargs)


class AzureOpenAIEmbedding3LargeEmbeddingModel(EmbeddingModel):
    def __init__(self, **kwargs):
        super().__init__(
            name=EmbeddingModelMaster.AZURE_TEXT_EMBEDDING_3_LARGE, **kwargs
        )


class BedrockTitanEmbedding(EmbeddingModel):
    def __init__(self, **kwargs):
        super().__init__(name=EmbeddingModelMaster.BEDROCK_TITAN_EMBEDDING, **kwargs)


class BedrockTitanMultiModalEmbedding(EmbeddingModel):
    def __init__(self, **kwargs):
        super().__init__(
            name=EmbeddingModelMaster.BEDROCK_TITAN_MULTIMODAL_EMBEDDING, **kwargs
        )


class GeminiAIEmbeddings(EmbeddingModel):
    def __init__(self, **kwargs):
        super().__init__(
            name=EmbeddingModelMaster.GEMINI_EMBEDDING, **kwargs
        )