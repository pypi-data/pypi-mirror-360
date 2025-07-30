from typing import List, Text
from pydantic import BaseModel, Field
from therix.core.data_sources import PDFDataSource
from therix.core.embedding_models import BedrockTitanEmbedding

from therix.core.output_parser import OutputParserWrapper
from therix.core.agent import Agent

from therix.core.system_prompt_config import SystemPromptConfig
from therix.core.agent import Agent
from therix.core.data_sources import TextDataSource
from therix.core.embedding_models import BedrockTitanEmbedding
from therix.core.inference_models import GroqMixtral87bInferenceModel,GroqLlama370b
import asyncio

GROQ_API_KEY=''

sys_prompt = """Answer the question like a pirate based only on the following context and reply with your capabilities if something is out of context.
        Context: 
        {{context}}

        Question: {{question}}
        
        Give the output as follows : {{format_instructions}}

        """
        # Always adress me with my name {name}


variables = {
        "name": "Abhishek Dubey",
}

agent = Agent(name="new smarttttttt agent")
(
        agent.add(TextDataSource(config={"files": ["../../test-data/rat.pdf"]}))   
        .add(BedrockTitanEmbedding(config={"bedrock_aws_access_key_id" : "",
                                "bedrock_aws_secret_access_key" : "",
                                "bedrock_aws_session_token" : "",
                                "bedrock_region_name" : "us-east-1"}))
        .add(GroqLlama370b(config={"groq_api_key": GROQ_API_KEY}))
        # .add(SystemPromptConfig(config={"system_prompt" : "new-prompt"}))
        .save()
    )

agent.preprocess_data()

print(agent.id)

class TestDetails(BaseModel):
        name: str = Field(description="Name of the Topic")
        description: str = Field(description="Short description of the Topic")
        citations: str = Field(description="add source of every topic, from where it is generated")
        page: str = Field(description="page number of the topic")


class OutputParserJSON(BaseModel):
    tests: List[TestDetails] = Field(description="Topic")
    
answer = agent.invoke("What kind of experiments are performed in the study?" , output_parser=OutputParserWrapper.parse_output(pydantic_object=OutputParserJSON), prompt_variables=variables)

print(answer)