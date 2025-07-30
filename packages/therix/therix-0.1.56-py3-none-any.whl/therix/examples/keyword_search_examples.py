from therix.core.data_sources import PDFDataSource
from typing import List
from therix.core.embedding_models import AzureOpenAIEmbedding3LargeEmbeddingModel
from therix.core.inference_models import AzureOpenAIGPT4InferenceModel
from therix.core.output_parser import OutputParserWrapper
from therix.core.agent import Agent
from pydantic import BaseModel, Field


agent = Agent(name="My New keyword-search Agent")
(agent
    .add(PDFDataSource(config={'files': ['../../test-data/rat.pdf']}))
    .add(AzureOpenAIEmbedding3LargeEmbeddingModel(config={"azure_deployment" : "", "azure_api_key" : "" , "azure_endpoint" : "" , "openai_api_version" :  ""}))
    .add(AzureOpenAIGPT4InferenceModel(config={"azure_api_key" : "" , "openai_api_version" :  "", "azure_endpoint" : "" , "azure_deployment" : "" , "temperature" : ""}))
    # .add(Trace(config={
    #                 'secret_key': 'sk-lf-e62aa7ce-c4c8-4c77-ad7d-9d76dfd96db1',
    #                 'public_key': 'pk-lf-282ad728-c1d6-4247-b6cd-8022198591a9',
    #                 'identifier': 'keyword_search_agent'
    #      }))
        .save()
        )

agent.preprocess_data()
print(agent.id)
    # ans = agent.invoke("What are some use cases of RAT?")
class TestDetails(BaseModel):
        name: str = Field(description="Name of the Topic")
        description: str = Field(description="Short description of the Topic")
        citations: str = Field(description="add source of every topic, from where it is generated")
        page: str = Field(description="page number of the topic")


class OutputParserJSON(BaseModel):
    tests: List[TestDetails] = Field(description="Topic")
        
mergerAgent = Agent.merge(['0ab4aba8-71bb-4822-8561-ae1f11623104', agent.id])

# mergerAgent.set_primary(agent.id)


keyword_search_dict = {
        "prompt" : "Analyze the provided report content for all the documents provided and include only the sentences that matches {keywords} that is being provided separately and also add the keywords whose records are not found and add description as not found. Content: {content}. Response should be a list of JSON  format. {format_instructions} Example: {{tests: [{{name: 'name of test', description: 'short description of Test'}}]}}",
        "keywords" : ["gender" , "RAT"],
        "output_parser" : OutputParserWrapper.parse_output(pydantic_object=OutputParserJSON)
    }
    
ans = mergerAgent.invoke(keyword_search_params=keyword_search_dict, top_k=15)
# ans = agent.invoke(keyword_search_params=keyword_search_dict)

print(ans)

