import os
from re import I
from re import I
from click import prompt
from langchain.prompts.chat import ChatPromptTemplate
from langchain_community.vectorstores.pgvector import PGVector
from therix.core import inference_models, pipeline
from therix.utils.rag import get_inference_model
from langfuse.callback import CallbackHandler
from langchain_core.pydantic_v1 import BaseModel, Field
from typing import Any, List
from langchain_core.pydantic_v1 import BaseModel, Field
from typing import List
from therix.services.trace_handler import get_trace_handler

DEFAULT_PROMPT = """
        You are a skilled professional who understands All kinds of documents. 
        You will be provided with Content and keywords.
        You have Analyze given data.
        {{content}}
        {{keywords}}
        Response should be in valid JSON format.
        {{format_instructions}}

"""

BASIC_INSTRUCTIONS = """
If a question seems confusing, simply rephrase it using simpler words. Examples can help too.
When unsure of the user's intent, rephrase the question and ask for confirmation.
Only answer questions related to your knowledge base.
Avoid asking the user questions unrelated to their current request.
Strive for factual answers. If unsure, acknowledge it and offer to find more information.
Always be polite and inclusive in your communication.
Be open to improvement based on user interactions and feedback.
"""


async def async_keyword_search(keyword_search_dict,session_id=None):
        
        retriever = keyword_search_dict["retriever"]
        inference_model = keyword_search_dict["inference_model"]
         
        therix_trace_handler = get_trace_handler(trace_details=keyword_search_dict.get("trace_details"), trace_api=keyword_search_dict.get("trace_api"), system_prompt=keyword_search_dict.get("system_prompt"), pipeline_id=keyword_search_dict.get("pipeline_id"), session_id=keyword_search_dict.get("session").get("session_id"),metadata=keyword_search_dict.get("metadata"))

        
        chain_callbacks = [therix_trace_handler] if therix_trace_handler else []

        content = ""  
        for keyword in keyword_search_dict["keywords"]:
            results = retriever.get_relevant_documents(keyword)
    
            for res in results:
                content += res.page_content + str(res.metadata) + "\n\n---\n\n"
        content = content.rstrip("\n\n---\n\n")

        prompt = keyword_search_dict["prompt"]

        if not prompt:
            prompt = DEFAULT_PROMPT.format(content, keyword_search_dict["keywords"])

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", prompt),
                ("human",
                 "{BASIC_INSTRUCTIONS} {content} {keywords}")
            ]
        )

        model = get_inference_model(inference_model.name, inference_model.config)
        
        chain = prompt | model | keyword_search_dict["output_parser"]
        if(keyword_search_dict.get("trace_details")):
            response_text = chain.invoke({"content": content, "keywords": keyword_search_dict["keywords"], "format_instructions": keyword_search_dict["output_parser"].get_format_instructions(), "BASIC_INSTRUCTIONS": BASIC_INSTRUCTIONS}, config={"callbacks": [therix_trace_handler]})
        else: 
            response_text = chain.invoke({"content": content, "keywords": keyword_search_dict["keywords"], "format_instructions": keyword_search_dict["output_parser"].get_format_instructions(), "BASIC_INSTRUCTIONS": BASIC_INSTRUCTIONS})
        
        return response_text

def keyword_search(keyword_search_dict):

        retriever = keyword_search_dict["retriever"]
        inference_model = keyword_search_dict["inference_model"]
        create_trace =True if  os.getenv("CREATE_TRACE") == "True" else False


        therix_trace_handler = get_trace_handler(trace_details=keyword_search_dict.get("trace_details"), trace_api=keyword_search_dict.get("trace_api"), system_prompt=keyword_search_dict.get("system_prompt"), pipeline_id=keyword_search_dict.get("pipeline_id"), session_id=keyword_search_dict.get("session").get("session_id"),metadata=keyword_search_dict.get("metadata"))

        
        chain_callbacks = [therix_trace_handler] if therix_trace_handler else []
        

        content = ""  
        for keyword in keyword_search_dict["keywords"]:
            results = retriever.get_relevant_documents(keyword)
    
            for res in results:
                content += res.page_content + str(res.metadata) + "\n\n---\n\n"
        content = content.rstrip("\n\n---\n\n")

        prompt = keyword_search_dict["prompt"]

        if not prompt:
            prompt = DEFAULT_PROMPT.format(content, keyword_search_dict["keywords"])
            if(keyword_search_dict.get("output_parser")):
                prompt+="{{format_instructions}}"
            
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", prompt),
                ("human",
                 "{BASIC_INSTRUCTIONS} {content} {keywords}")
            ]
        )

        model = get_inference_model(inference_model.name, inference_model.config)
        config = {"callbacks": [therix_trace_handler]} if therix_trace_handler and create_trace is True else {}
        chain = prompt | model | keyword_search_dict["output_parser"]
        if(keyword_search_dict.get("trace_details") or keyword_search_dict.get("trace_api")):
            response_text = chain.invoke({"content": content, "keywords": keyword_search_dict["keywords"], "format_instructions": keyword_search_dict["output_parser"].get_format_instructions(), "BASIC_INSTRUCTIONS": BASIC_INSTRUCTIONS}, config=config)
        else: 
            response_text = chain.invoke({"content": content, "keywords": keyword_search_dict["keywords"], "format_instructions": keyword_search_dict["output_parser"].get_format_instructions(), "BASIC_INSTRUCTIONS": BASIC_INSTRUCTIONS})
        
        return response_text
    
    
async def cloud_keyword_search(keyword_search_dict):
    inference_model = keyword_search_dict["inference_model"]
    create_trace =  True if  os.getenv("CREATE_TRACE") == "True" else False
    model = get_inference_model(inference_model.name, inference_model.config)
    
    therix_trace_handler = get_trace_handler(trace_details=keyword_search_dict.get("trace_details"), trace_api=keyword_search_dict.get("trace_api"), system_prompt=keyword_search_dict.get("system_prompt"), pipeline_id=keyword_search_dict.get("pipeline_id"), session_id=keyword_search_dict.get("session").get("session_id"),metadata=keyword_search_dict.get("metadata"))    
    chain_callbacks = [therix_trace_handler] if therix_trace_handler else []
    
    content = ""
    
    for keyword in keyword_search_dict["keywords"]:
        if(type(keyword_search_dict.get("store")) is not list ):
            relevant_documents = await keyword_search_dict['store'].get_relevant_documents(keyword, topK=4, agent_id = keyword_search_dict['pipeline_id'])
        else:
            relevant_documents = []
            for store in keyword_search_dict.get("store"):
                relevant_documents.append(await store.get_relevant_documents(keyword, topK=4, agent_id = keyword_search_dict['pipeline_id']))  

        if(type (relevant_documents) is list):
            for document in relevant_documents:
                for doc in document["data"]:
                    content += doc["document"]+"\n"+f"{doc['cmetadata']}"+"\n\n---\n\n"
        else:    
            for doc in relevant_documents["data"]:
                content += doc["document"]+"\n"+f"{doc['cmetadata']}"+"\n\n---\n\n"
            
            
    prompt = keyword_search_dict["prompt"]
    
    if not prompt:
        prompt = DEFAULT_PROMPT.format(content, keyword_search_dict["keywords"])
        if(keyword_search_dict.get("output_parser")):
            prompt+=f"format instructions:{keyword_search_dict['output_parser'].get_format_instructions()}"
        prompt.replace("{{context}}", f"context : {content}")
        prompt.replace("{{keywords}}", f"keywords : {keyword_search_dict['keywords']}")
            
    else:
        if(keyword_search_dict.get("output_parser")):
            prompt = prompt.format(content=content, keywords=keyword_search_dict["keywords"], format_instructions=keyword_search_dict["output_parser"].get_format_instructions())
    
    config = {"callbacks": [therix_trace_handler]} if therix_trace_handler and create_trace is True else {}
    if(keyword_search_dict.get("trace_details") or keyword_search_dict.get("trace_api")):
        response : Any = model.invoke(input=prompt, config=config)
    else:
        response : Any = model.invoke(input=prompt)
        
    return response.content
    
    
    
    
       
