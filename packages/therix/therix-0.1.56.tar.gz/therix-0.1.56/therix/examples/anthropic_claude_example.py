from therix.core.data_sources import PDFDataSource
from therix.core.embedding_models import (
    BedrockTitanEmbedding,

)
from therix.core.inference_models import Anthropic_Claude_Opus
from therix.core.agent import Agent
import sys

from therix.core.trace import Trace

agent = Agent(name="My New Published Agent")
(
        agent.add(PDFDataSource(config={"files": ["../../test-data/rat.pdf"]}))
        .add(BedrockTitanEmbedding(config={
                                "bedrock_aws_access_key_id" : "",
                                "bedrock_aws_secret_access_key" :"",
                                "bedrock_aws_session_token" :" ",
                                "bedrock_region_name" : "us-east-1"}))
        .add(Anthropic_Claude_Opus(
            config={"claude_api_key":" "}
        ))

        .add(
            Trace(
                config={
                    "secret_key": "sk-lf-e62aa7ce-c4c8-4c77-ad7d-9d76dfd96db1",
                    "public_key": "pk-lf-282ad728-c1d6-4247-b6cd-8022198591a9",
                    "identifier": "my own agent",
                }
            )
        )
        .save()
    )

agent.preprocess_data()
print(agent.id)
ans = agent.invoke("What are some use cases of RAT?",top_k=3)

print(ans)