from therix.core.data_sources import PDFDataSource
from therix.core.embedding_models import (
    BedrockTitanEmbedding,

)
from therix.core.inference_models import Anthropic_Claude_Opus, OpenAIGPT4OMiniInferenceModel
from therix.core.agent import Agent
import sys

from therix.core.trace import Trace

agent = Agent(name="My New Published Agent")
(
        agent.add(OpenAIGPT4OMiniInferenceModel(
            config={"api_key":""}
        ))
        .save()
    )

print(agent.id)
ans = agent.invoke("Who is sonu nigam?")

print(ans)