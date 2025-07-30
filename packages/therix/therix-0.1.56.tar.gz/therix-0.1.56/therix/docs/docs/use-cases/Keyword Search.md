---
slug: /use-cases/keyword-search
sidebar_position: 3
---

# Keyword Search


Keyword search is a method used to quickly find specific words or phrases within a dataset or document. By specifying keywords of interest, users can efficiently locate relevant information without manually going through the entire dataset. 

It supports decision-making by retrieving matching content, facilitates information retrieval, and is customizable to meet specific requirements. Overall, keyword search improves efficiency in data analysis and exploration by enabling quick access to relevant information.



## Smart Search

Smart Search simplifies the process of exploring extensive data distributed across numerous documents. Users can input keywords to search across multiple documents and retrieve relevant outputs. By providing a list of documents instead of a single one, users can efficiently access desired information related to their specified keywords.

## Setting up Keyword Search in your therix Agent

### Step 1: Add PDF Data Source
First, you need to add the PDF documents that you want to analyze. Use the `add` method of the Agent object to add a PDFDataSource. Provide a list of file paths as the `files` parameter.

Example:
```python
agent.add(PDFDataSource(config={'files': ['./test-data/rat.pdf']}))
```

### Step 2: Add Embedding Model and Inference Model
Next, add an embedding model to convert text into numerical vectors for analysis. In the example, an Azure OpenAI Embedding 3 Large Embedding Model is added.
Additionally, include an inference model to send the necessary data to the Language Model and obtain the desired output.

Example:
```python
 .add(AzureOpenAIEmbedding3SmallEmbeddingModel(config={'azure_api_key':'',
                                                       'azure_endpoint':'',
                                                       'openai_api_version':'',
                                                       'azure_deployment':'',
                                                          })
 .add(AzureOpenAIGPT4InferenceModel(config={'azure_api_key':'',
                                            'openai_api_version':'',
                                            'azure_endpoint':'',
                                            'azure_deployment':'',
                                            'temperature':''}))                                                       
```


### Step 3: Define Output Parser
An output parser is needed to structure the output based on requirements. In the example, a PydanticOutputParser is used.

Example:

```python
from therix.core.output_parser import OutputParserWrapper
```

#### Output Parser Definition

The OutputParserJSON class is defined as a Pydantic model to structure the output in JSON format. It includes a list of test details containing the name and description of each test.

Example:
```python
class TestDetails(BaseModel):
    name: str = Field(description="Name of the Test")
    description: str = Field(description="Short description of the Test")

class OutputParserJSON(BaseModel):
    tests: List[TestDetails] = Field(description="Test")

 #You can define your own output parser json   
```


### Step 4: Define Keyword Search Parameters
Define a dictionary containing parameters for keyword search. This includes the document ID, prompt, keywords to search for, and output parser.

Example:

```python
keyword_search_dict = {
    "config_id" : #document id returned by the embedding model(should be a list[]),
    "prompt" : #human readable prompt ,
    "keywords" :#list of keywords eg:-["RAT" , "abc"],
    "output_parser" : OutputParserWrapper.parse_output(pydantic_object=OutputParserJSON) #pass your defined output parser here
}
```

### Step 5: Invoke the Agent with Keyword Search Parameters
Finally, invoke the agent with the keyword search parameters. Pass the keyword_search_dict as the keyword_search_params parameter to the invoke method of the Agent object.

```python
ans = agent.invoke(keyword_search_params=keyword_search_dict)
```


By following these steps, you can set up keyword search functionality in your therix agent and structure the output according to your requirements.



