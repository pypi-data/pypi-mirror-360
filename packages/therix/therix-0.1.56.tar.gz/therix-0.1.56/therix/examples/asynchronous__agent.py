
from therix.core.data_sources import PDFDataSource
from therix.core.embedding_models import (
    BedrockTitanEmbedding,
    OpenAITextAdaEmbeddingModel,)
from therix.core.inference_models import (
    GroqLlama370b
)
from therix.core.agent import Agent

GROQ_API_KEY=''


agent = Agent(name="RAT  Pirate")
(
        agent.add(PDFDataSource(config={"files": ["../../test-data/rat.pdf"]}))
        .add(BedrockTitanEmbedding(config={"bedrock_aws_access_key_id" : "",
                                "bedrock_aws_secret_access_key" : "",
                                "bedrock_aws_session_token" : "",
                                "bedrock_region_name" : "us-east-1"}))
        .add(GroqLlama370b(config={"groq_api_key": GROQ_API_KEY}))
        .save()
    )


agent.preprocess_data()
print(agent.id)


# ASYNCHRONOUS CALL - EXAMPLE
async def call_agent():
        ans = await agent.async_invoke("What are some use cases of RAT?")
        print(ans)
        return ans

# asyncio.run(call_agent()          Add asyncio dependency to run this