import asyncio
from enum import Enum
import json
import os
from therix.utils.rag import get_inference_model
from langchain.chains.llm import LLMChain
from langchain_core.prompts import PromptTemplate
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.text_splitter import CharacterTextSplitter
from langchain.docstore.document import Document
from langchain.chains import MapReduceDocumentsChain, ReduceDocumentsChain
from langchain_core.output_parsers import JsonOutputParser
from therix.services.trace_handler import get_trace_handler


class SummarizerTypeMaster(Enum):
    EXTRACTIVE = 'EXTRACTIVE'
    ABSTRACTIVE = 'ABSTRACTIVE'

PROMPT_TEMPLATE = {
    "EXTRACTIVE": """
        Summarize the provided context below:

        {context}

        ---

        Craft your response with conciseness and accuracy, including only the information provided in the context. 
        Use null values for any missing information.

        Please structure your response in the following JSON format:
        {response_schema_json}
    """,
    "ABSTRACTIVE": "Provide a concise summary for the following text using abstractive summarization:\n\n{context}."
}




async def async_summarizer(summarizer_config, inference_model_details, text, trace_details, pipeline_id, system_prompt=None, session_id=None, trace_api=None,metadata=None, config = None):
    if not config:
        therix_trace_handler = get_trace_handler(trace_details, trace_api, system_prompt, pipeline_id, session_id, metadata)
        chain_callbacks = [therix_trace_handler] if therix_trace_handler else []
    else:
        therix_trace_handler = config    

    pydantic_prompt = summarizer_config['pydantic_model']
    summarization_type = summarizer_config['summarization_type']
    llm = get_inference_model(inference_model_details.name, inference_model_details.config)

    if summarization_type == 'ABSTRACTIVE':
        map_template = PromptTemplate.from_template(
            """Read the following document and provide a detailed summary of the document.\n{pages}"""
        )
        reduce_template = """The following is a set of summaries:\n{pages}\nTake these and distill them into a final, consolidated summary. Verify each and every detail and make sure that the final summary is accurate and complete."""
        
        map_chain = LLMChain(llm=llm, prompt=map_template)
        reduce_chain = LLMChain(llm=llm, prompt=PromptTemplate.from_template(reduce_template))
        
        combine_documents_chain = StuffDocumentsChain(
            llm_chain=reduce_chain, document_variable_name="pages"
        )

        reduce_documents_chain = ReduceDocumentsChain(
            combine_documents_chain=combine_documents_chain,
            collapse_documents_chain=combine_documents_chain,
            token_max=4000,
        )

        map_reduce_chain = MapReduceDocumentsChain(
            llm_chain=map_chain,
            reduce_documents_chain=reduce_documents_chain,
            document_variable_name="pages",
            return_intermediate_steps=False,
        )

        docs = Document(page_content=text, metadata={"source": "local"})
        text_splitter = CharacterTextSplitter.from_tiktoken_encoder(chunk_size=1000, chunk_overlap=0)
        split_docs = text_splitter.split_documents([docs])

        summary = map_reduce_chain.run(split_docs)
    else:
        summary = text

    parser = JsonOutputParser()
    
    prompt_template = system_prompt.get("system_prompt") if system_prompt and "system_prompt" in system_prompt else system_prompt
    prompt = PromptTemplate(
        template=prompt_template or PROMPT_TEMPLATE[summarization_type],
        input_variables=["context"],
        partial_variables={"response_schema_json": pydantic_prompt},
    )

    if summarization_type == SummarizerTypeMaster.EXTRACTIVE.value:
        chain = prompt | llm | parser
        result = await chain.ainvoke({"context": summary}, config={"callbacks": [therix_trace_handler]})
    else:
        chain = prompt | llm
        result = await chain.ainvoke({"context": summary}, config={"callbacks": [therix_trace_handler]})

    return json.dumps(result) if summarization_type == SummarizerTypeMaster.EXTRACTIVE.value else result.content

def summarizer(summarizer_config, inference_model_details, text, trace_details, pipeline_id, system_prompt=None, session_id=None, trace_api=None,metadata=None, config = None):
    create_trace = True if  os.getenv("CREATE_TRACE") == "True" else False
    if not config:
        therix_trace_handler = get_trace_handler(trace_details, trace_api, system_prompt, pipeline_id, session_id, metadata)
        chain_callbacks = [therix_trace_handler] if therix_trace_handler else []
    else:
        therix_trace_handler = config    

    pydantic_prompt = summarizer_config['pydantic_model']
    summarization_type = summarizer_config['summarization_type']
    llm = get_inference_model(inference_model_details.name, inference_model_details.config)

    if summarization_type == 'ABSTRACTIVE':
        map_template = PromptTemplate.from_template(
            """Read the following document and provide a detailed summary of the document.\n{pages}"""
        )
        reduce_template = """The following is a set of summaries:\n{pages}\nTake these and distill them into a final, consolidated summary. Verify each and every detail and make sure that the final summary is accurate and complete."""
        
        map_chain = LLMChain(llm=llm, prompt=map_template)
        reduce_chain = LLMChain(llm=llm, prompt=PromptTemplate.from_template(reduce_template))
        
        combine_documents_chain = StuffDocumentsChain(
            llm_chain=reduce_chain, document_variable_name="pages"
        )

        reduce_documents_chain = ReduceDocumentsChain(
            combine_documents_chain=combine_documents_chain,
            collapse_documents_chain=combine_documents_chain,
            token_max=4000,
        )

        map_reduce_chain = MapReduceDocumentsChain(
            llm_chain=map_chain,
            reduce_documents_chain=reduce_documents_chain,
            document_variable_name="pages",
            return_intermediate_steps=False,
        )

        docs = Document(page_content=text, metadata={"source": "local"})
        text_splitter = CharacterTextSplitter.from_tiktoken_encoder(chunk_size=1000, chunk_overlap=0)
        split_docs = text_splitter.split_documents([docs])

        summary = map_reduce_chain.run(split_docs)
    else:
        summary = text

    parser = JsonOutputParser()
    
    prompt_template = system_prompt.get("system_prompt") if system_prompt and "system_prompt" in system_prompt else system_prompt
    prompt = PromptTemplate(
        template=prompt_template or PROMPT_TEMPLATE[summarization_type],
        input_variables=["context"],
        partial_variables={"response_schema_json": pydantic_prompt},
    )

    config = {"callbacks": [therix_trace_handler]} if therix_trace_handler and create_trace is True else {}

    if summarization_type == SummarizerTypeMaster.EXTRACTIVE.value:
        chain = prompt | llm | parser
        result = chain.invoke({"context": summary}, config=config)
    else:
        chain = prompt | llm
        result = chain.invoke({"context": summary}, config=config)

    return json.dumps(result) if summarization_type == SummarizerTypeMaster.EXTRACTIVE.value else result.content
