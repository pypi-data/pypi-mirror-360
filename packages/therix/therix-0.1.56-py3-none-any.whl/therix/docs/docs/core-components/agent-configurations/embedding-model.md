---
slug: /components/agent-config/embedding-model
sidebar_position: 5
---

# Embedding Model


Therix provides an embedding layer for Large Language Model (LLM). Embeddings create a vector representation of a piece of text. This is useful because it means we can think about text in the vector space, and do things like semantic search where we look for pieces of text that are most similar in the vector space.

Therix offers seamless integration with various embedding models, providing users with flexibility and customization options for their specific use cases. One such integration is the AzureOpenAI Embedding, which leverages Azure endpoints for enhanced performance and scalability.

## Adding OpenAI Embedding

Let’s load the OpenAI Embedding class with environment variables set to indicate to use OpenAI endpoints:
To incorporate the OpenAI Embedding into your agent configuration, follow these steps:

Import the required class and ensure environment variables are set to indicate the usage of OpenAI endpoints.
```python
  from therix.core.embedding_models import (
    OpenAITextAdaEmbeddingModel,
)
# if you want to use other embedding models change it accordingly :
# for using Text-Embedding-3-Small Embedding Model change import to OpenAITextEmbedding3SmallEmbeddingModel 
# for using Text-Embedding-3-Large Embedding Model change import to OpenAITextEmbedding3LargeEmbeddingModel 

# Add AzureOpenAIEmbedding to your agent
 .add(OpenAITextAdaEmbeddingModel(config={'api_key':''}))
```


## Adding AzureOpenAI Embedding

Let’s load the Azure OpenAI Embedding class with environment variables set to indicate to use Azure endpoints:
To incorporate the AzureOpenAI Embedding into your agent configuration, follow these steps:

Import the required class and ensure environment variables are set to indicate the usage of Azure endpoints.
```python
  from therix.core.embedding_models import (
    AzureOpenAIEmbedding3SmallEmbeddingModel,
)
# if you want to use other embedding models change it accordingly :
# for using Text-Embedding-3-Large change import to AzureOpenAIEmbedding3LargeEmbeddingModel 
# for using Text-Ada Embedding Model change import to AzureOpenAITextAdaEmbeddingModel 

# Add AzureOpenAIEmbedding to your agent
 .add(AzureOpenAIEmbedding3SmallEmbeddingModel(config={'azure_api_key':'',
                                                       'azure_endpoint':'',
                                                       'openai_api_version':'',
                                                       'azure_deployment':''
                                                          }))
```

## Adding Bedrock Embedding
Let’s load the Bedrock Embedding class with environment variables set to indicate to use Amazon Bedrock endpoints:
To incorporate the Bedrock Embedding into your agent configuration, follow these steps:
Import the required class and ensure environment variables are set to indicate the usage of Bedrock endpoints.
```python
  from therix.core.embedding_models import (
    BedrockTitanEmbedding,
)
# if you want to use other embedding models change it accordingly :
# for using BedrockTitanMultiModalEmbedding change import to BedrockTitanMultiModalEmbedding 

# Add AzureOpenAIEmbedding to your agent
 .add(BedrockTitanEmbedding(config={'bedrock_aws_access_key_id': "",
                                       'bedrock_aws_secret_access_key':"",
                                      'bedrock_aws_session_token':"",
                                      'bedrock_region_name':''
                                      }))


## Example
```python
 agent = Agent(name="My New Published Agent")
    (
        agent.add(DataSource(config={"files": []}))
        .add(Embedding Model(config={"api_key": ""}))
        .add(Inferenc eModel(config={"api_key": ""}))
        .add(Trace(config={}))
        .save()
    )

     
    agent.preprocess_data()
```