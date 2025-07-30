from therix.core.constants import InferenceModelMaster
from therix.core.pipeline_component import InferenceModel


class OpenAIGPT35TurboInferenceModel(InferenceModel):
    def __init__(self, config: dict):
        super().__init__(name=InferenceModelMaster.OPENAI_GPT_3_5_TURBO, config=config)


class OpenAIGPT4InferenceModel(InferenceModel):
    def __init__(self, config: dict):
        super().__init__(name=InferenceModelMaster.OPENAI_GPT_4, config=config)


class OpenAIGPT4OInferenceModel(InferenceModel):
    def __init__(self, config: dict):
        super().__init__(
            name=InferenceModelMaster.OPENAI_GPT_4_O, config=config
        )

class OpenAIGPT4OMiniInferenceModel(InferenceModel):
    def __init__(self, config: dict):
        super().__init__(
            name=InferenceModelMaster.OPENAI_GPT_4_O_MINI, config=config
        )
        
        
class OpenAIGPT4TurboPreviewInferenceModel(InferenceModel):
    def __init__(self, config: dict):
        super().__init__(
            name=InferenceModelMaster.OPENAI_GPT_4_TURBO_PREVIEW, config=config
        )


class AzureOpenAIGPT3TurboPreviewInferenceModel(InferenceModel):
    def __init__(self, config: dict):
        super().__init__(name=InferenceModelMaster.AZURE_GPT_3_5_TURBO, config=config)


class AzureOpenAIGPT3TurboInstructnferenceModel(InferenceModel):
    def __init__(self, config: dict):
        super().__init__(
            name=InferenceModelMaster.AZURE_GPT_3_5_TURBO_INSTRUCT, config=config
        )


class AzureOpenAIGPT4InferenceModel(InferenceModel):
    def __init__(self, config: dict):
        super().__init__(name=InferenceModelMaster.AZURE_GPT_4, config=config)
        
        
class AzureOpenAIGPT4OInferenceModel(InferenceModel):
    def __init__(self, config: dict):
        super().__init__(name=InferenceModelMaster.AZURE_GPT_4_O, config=config)


class AzureOpenAIGPT4TurboPreviewInferenceModel(InferenceModel):
    def __init__(self, config: dict):
        super().__init__(
            name=InferenceModelMaster.AZURE_GPT_4_TURBO_PREVIEW, config=config
        )


class GroqMixtral87bInferenceModel(InferenceModel):
    def __init__(self, config: dict):
        super().__init__(
            name=InferenceModelMaster.GROQ_LLM_MIXTRAL_8_7_B, config=config
        )


class GroqLlama38b(InferenceModel):
    def __init__(self, config: dict):
        super().__init__(name=InferenceModelMaster.GROQ_LLM_LLAMA3_8B, config=config)



class GroqGemma7B(InferenceModel):
    def __init__(self, config: dict):
        super().__init__(name=InferenceModelMaster.GROQ_LLM_GEMMA7B, config=config)


class GroqLlama370b(InferenceModel):
    def __init__(self, config: dict):
        super().__init__(name=InferenceModelMaster.GROQ_LLM_LLAMA3_70B, config=config)


class GroqLlama318B(InferenceModel):
    def __init__(self, config: dict):
        super().__init__(name=InferenceModelMaster.GROQ_LLM_LLAMA3_1_8B, config=config)


class GroqLlama3170B(InferenceModel):
    def __init__(self, config: dict):
        super().__init__(name=InferenceModelMaster.GROQ_LLM_LLAMA3_1_70B, config=config)


class GroqLlama31405B(InferenceModel):
    def __init__(self, config: dict):
        super().__init__(name=InferenceModelMaster.GROQ_LLM_LLAMA3_1_405B, config=config)


class BedrockTextExpressV1(InferenceModel):
    def __init__(self, config: dict):
        super().__init__(
            name=InferenceModelMaster.BEDROCK_TEXT_EXPRES_V1, config=config
        )
        
class BedrockTextPremierG1(InferenceModel):
    def __init__(self, config: dict):
        super().__init__(
            name=InferenceModelMaster.BEDROCK_TEXT_PREMIER_G1, config=config
        )


class BedrockLiteG1(InferenceModel):
    def __init__(self, config: dict):
        super().__init__(name=InferenceModelMaster.BEDROCK_TEXT_LITE_G1, config=config)
        
        
class GeminiPro(InferenceModel):
    def __init__(self, config: dict):
        super().__init__(name=InferenceModelMaster.GOOGLE_GEMINI_PRO, config=config)
        
        
class Gemini_1_5_PRO(InferenceModel):
    def __init__(self, config: dict):
        super().__init__(name=InferenceModelMaster.GOOGLE_GEMINI_1_5_PRO, config=config)
        

class Anthropic_Claude_Opus(InferenceModel):
    def __init__(self, config:dict):
        super().__init__(name=InferenceModelMaster.ANTHROPIC_CLAUDE_3_OPUS , config=config)


class Anthropic_Claude_2_1(InferenceModel):
    def __init__(self, config:dict):
        super().__init__(name=InferenceModelMaster.ANTHROPIC_CLAUDE_2_1 , config=config)
        
        
class Anthropic_Claude_3_Haiku(InferenceModel):
    def __init__(self, config:dict):
        super().__init__(name=InferenceModelMaster.ANTHROPIC_CLAUDE_3_HAIKU , config=config)

class Anthropic_Claude_3_Sonnet(InferenceModel):
    def __init__(self, config:dict):
        super().__init__(name=InferenceModelMaster.ANTHROPIC_CLAUDE_3_SONNET , config=config)
        
class Anthropic_Claude_3_5_Sonnet(InferenceModel):
    def __init__(self, config:dict):
        super().__init__(name=InferenceModelMaster.ANTHROPIC_CLAUDE_3_5_SONNET , config=config)
        
class Deepseek_R1_Latest(InferenceModel):
    def __init__(self, config:dict):
        super().__init__(name=InferenceModelMaster.DEEPSEEK_R1_LATEST , config=config)

class Deepseek_R1_14b(InferenceModel):
    def __init__(self, config:dict):
        super().__init__(name=InferenceModelMaster.DEEPSEEK_R1_14_B , config=config)

class PHI_4_14b(InferenceModel):
    def __init__(self, config:dict):
        super().__init__(name=InferenceModelMaster.PHI_4_14_B , config=config)

class Llama_3_1(InferenceModel):
    def __init__(self, config:dict):
        super().__init__(name=InferenceModelMaster.LLAMA_3_1 , config=config)
