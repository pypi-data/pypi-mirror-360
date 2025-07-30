from therix.core.data_sources import PDFDataSource
from therix.core.embedding_models import (
    BedrockTitanEmbedding,

)
from therix.core.inference_models import Anthropic_Claude_Opus, Deepseek_R1_Latest
from therix.core.agent import Agent
import sys

from therix.core.trace import Trace

# agent = Agent(name="My New Published Agent")
# (
#         agent.add(Deepseek_R1_Latest(
#             config={"base_url":"http://192.168.100.20:22434/"}
#         ))
#         .save()
#     )

agent = Agent.from_id("2d2183b5-17b4-4dc6-bc6c-f58e4828a578")

# print(agent.id)
ans = agent.invoke("Who is sonu nigam?")

print(ans)