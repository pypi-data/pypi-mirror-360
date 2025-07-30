from gc import callbacks
from pickle import NONE
import os
from typing import Any
import json, uuid
from operator import itemgetter
from pathlib import Path
from urllib import response
from langchain.docstore.document import Document
from langchain_community.document_loaders import TextLoader, PyPDFLoader, JSONLoader
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_openai import AzureChatOpenAI
from langchain_ollama.llms import OllamaLLM
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.document_loaders.youtube import YoutubeLoader
from langchain_openai import AzureOpenAIEmbeddings
from therix.core.JSONLoader import JSONLoader
from langchain_community.embeddings.bedrock import BedrockEmbeddings
import boto3
from langchain_community.llms.bedrock import Bedrock
from therix.core.chat_history.base_chat_history import TherixChatMessageHistory
from therix.core.document_intelligence_loader import DocumentIntelligenceLoader
from therix.core.constants import (
    API_Endpoint,
    DataSourceMaster,
    EmbeddingModelMaster,
    InferenceModelMaster,
)
from therix.core.prompt import Prompt
from therix.core.therix_RAG import VectorStore
from therix.db.session import get_sql_alchemy_url
from langchain_core.prompts import PromptTemplate
from langchain_community.vectorstores.pgvector import PGVector
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import get_buffer_string
from langchain_core.prompts import format_document
from langchain_core.runnables import RunnableParallel
from langchain_text_splitters import  RecursiveCharacterTextSplitter
from operator import itemgetter
from langchain_experimental.data_anonymizer import PresidioReversibleAnonymizer
from langchain_core.messages.chat import ChatMessage
from therix.services.trace_handler import get_trace_handler
from langchain_core.output_parsers import JsonOutputParser
from langchain_anthropic import ChatAnthropic
import asyncio

def sanitize_text(text):
    # Remove null characters (0x00) from the text
    sanitized_text = text.replace("\x00", "")
    return sanitized_text


def get_loader(file_type, file_path, config, di_config=None):
    if file_type == DataSourceMaster.TEXT:
        return TextLoader(file_path)
    elif file_type == DataSourceMaster.PDF:
        return PyPDFLoader(file_path)
    elif file_type == DataSourceMaster.PDF_DI:
        if not di_config:
            raise ValueError("Document Intelligence configuration is required for PDF_DI data source")
        # Map the configuration keys to what the DocumentIntelligenceLoader expects
        mapped_config = {
            'endpoint': di_config.get('azure_document_intelligence_endpoint'),
            'key': di_config.get('azure_document_intelligence_key'),
            'model': di_config.get('model', 'prebuilt-document')
        }
        return DocumentIntelligenceLoader(file_path, mapped_config)
    elif file_type == DataSourceMaster.JSON:
        return JSONLoader(file_path)
    elif file_type == DataSourceMaster.YOUTUBE:
        return YoutubeLoader.from_youtube_url(
            file_path,
            add_video_info=True,
            language=[config["language"], "id"],
            translation="en",
        )
        return PyPDFLoader(file_path)
    elif file_type == DataSourceMaster.WEBSITE:
        return JSONLoader(file_path)
    else:
        raise ValueError(f"Unknown data source type: {file_type}")


def get_embedding_model(embedding_model_name, config):
    if (
        embedding_model_name == EmbeddingModelMaster.OPENAI_TEXT_ADA
        or embedding_model_name == EmbeddingModelMaster.OPENAI_TEXT_EMBEDDING_3_SMALL
        or embedding_model_name == EmbeddingModelMaster.OPENAI_TEXT_EMBEDDING_3_LARGE
    ) and ("api_key" in config):
        return OpenAIEmbeddings(
            openai_api_key=config["api_key"], model=embedding_model_name
        )
    elif (
        embedding_model_name == EmbeddingModelMaster.AZURE_TEXT_ADA
        or embedding_model_name == EmbeddingModelMaster.AZURE_TEXT_EMBEDDING_3_LARGE
        or embedding_model_name == EmbeddingModelMaster.AZURE_TEXT_EMBEDDING_3_SMALL
    ) and ("azure_api_key" in config):
        if ("apim_subscription_key" in config):
            print("Using AzureOpenAIEmbeddings with apim_subscription_key")
            return AzureOpenAIEmbeddings(
                api_key=config["azure_api_key"],
                model=embedding_model_name,
                azure_endpoint=config["azure_endpoint"],
                openai_api_version=config["openai_api_version"],
                azure_deployment=config["azure_deployment"],
                default_headers={"Ocp-Apim-Subscription-Key": config["apim_subscription_key"]},
        )
        else:
            print("Using AzureOpenAIEmbeddings without apim_subscription_key")
            return AzureOpenAIEmbeddings(
                api_key=config["azure_api_key"],
                model=embedding_model_name,
                azure_endpoint=config["azure_endpoint"],
                openai_api_version=config["openai_api_version"],
                azure_deployment=config["azure_deployment"],
            )

    elif (
        embedding_model_name == EmbeddingModelMaster.BEDROCK_TITAN_EMBEDDING
        or embedding_model_name
        == EmbeddingModelMaster.BEDROCK_TITAN_MULTIMODAL_EMBEDDING
    ) and ("bedrock_aws_session_token" in config):
        bedrock_client = boto3.client(
            service_name="bedrock-runtime",
            aws_access_key_id=config["bedrock_aws_access_key_id"],
            aws_secret_access_key=config["bedrock_aws_secret_access_key"],
            aws_session_token=config["bedrock_aws_session_token"],
            region_name=config["bedrock_region_name"],
        )

        return BedrockEmbeddings(
            credentials_profile_name="bedrock-admin",
            client=bedrock_client,
            model_id=embedding_model_name,
            region_name=config["bedrock_region_name"],
        )
        
    elif(
        embedding_model_name == EmbeddingModelMaster.GEMINI_EMBEDDING
    ) and ("google_api_key" in config):
        return GoogleGenerativeAIEmbeddings(
            model=EmbeddingModelMaster.GEMINI_EMBEDDING,
            google_api_key=config["google_api_key"],
        )
    else:
        raise ValueError(f"Unknown embedding model: {embedding_model_name}")
    

def get_inference_model(inference_model_name, config):
    if (
        inference_model_name == InferenceModelMaster.OPENAI_GPT_3_5_TURBO
        or inference_model_name == InferenceModelMaster.OPENAI_GPT_3_5_TURBO_INSTRUCT
        or inference_model_name == InferenceModelMaster.OPENAI_GPT_4
        or inference_model_name == InferenceModelMaster.OPENAI_GPT_4_TURBO_PREVIEW
        or inference_model_name == InferenceModelMaster.OPENAI_GPT_4_O
        or inference_model_name == InferenceModelMaster.OPENAI_GPT_4_O_MINI
    ) and ("api_key" in config):
        return ChatOpenAI(openai_api_key=config["api_key"], model=inference_model_name)
    elif (
        inference_model_name == InferenceModelMaster.OPENAI_GPT_3_5_TURBO
        or inference_model_name == InferenceModelMaster.OPENAI_GPT_3_5_TURBO_INSTRUCT
        or inference_model_name == InferenceModelMaster.OPENAI_GPT_4
        or inference_model_name == InferenceModelMaster.OPENAI_GPT_4_TURBO_PREVIEW
        or inference_model_name == InferenceModelMaster.OPENAI_GPT_4_O
         or inference_model_name == InferenceModelMaster.OPENAI_GPT_4_O_MINI
    ) and ("azure_api_key" in config):
        if ("apim_subscription_key" in config):
            print("Using AzureChatOpenAI with apim_subscription_key")
            return AzureChatOpenAI(
                api_key=config["azure_api_key"],
                model=inference_model_name,
                deployment_name=config["azure_deployment"],
                azure_endpoint=config["azure_endpoint"],
                api_version=config["openai_api_version"],
                temperature=config["temperature"],
                default_headers={"Ocp-Apim-Subscription-Key": config["apim_subscription_key"]},
            )
        else:
            print("Using AzureChatOpenAI without apim_subscription_key")
            return AzureChatOpenAI(
                api_key=config["azure_api_key"],
                model=inference_model_name,
                deployment_name=config["azure_deployment"],
                azure_endpoint=config["azure_endpoint"],
                api_version=config["openai_api_version"],
                temperature=config["temperature"],
            )
    elif (
        inference_model_name == InferenceModelMaster.GROQ_LLM_MIXTRAL_8_7_B
        or inference_model_name == InferenceModelMaster.GROQ_LLM_LLAMA3_70B
        or inference_model_name == InferenceModelMaster.GROQ_LLM_GEMMA7B
        or inference_model_name == InferenceModelMaster.GROQ_LLM_LLAMA3_8B
        or inference_model_name == InferenceModelMaster.GROQ_LLM_LLAMA3_1_8B
        or inference_model_name == InferenceModelMaster.GROQ_LLM_LLAMA3_1_70B
        or inference_model_name == InferenceModelMaster.GROQ_LLM_LLAMA3_1_405B
    ) and ("groq_api_key" in config):
         return ChatGroq(groq_api_key=config["groq_api_key"], model=inference_model_name, temperature=config["temperature"])

    elif (
        inference_model_name == InferenceModelMaster.BEDROCK_TEXT_EXPRES_V1
        or inference_model_name == InferenceModelMaster.BEDROCK_TEXT_LITE_G1
        or inference_model_name == InferenceModelMaster.BEDROCK_TEXT_PREMIER_G1
    ) and ("bedrock_aws_session_token" in config):
        bedrock_client = boto3.client(
            service_name="bedrock-runtime",
            aws_access_key_id=config["bedrock_aws_access_key_id"],
            aws_secret_access_key=config["bedrock_aws_secret_access_key"],
            aws_session_token=config["bedrock_aws_session_token"],
            region_name=config["bedrock_region_name"]
        )
        return Bedrock(
            credentials_profile_name="bedrock-admin",
            model_id=inference_model_name,
            client=bedrock_client,
            region_name=config["bedrock_region_name"]
        )
    
    elif(
        inference_model_name == InferenceModelMaster.GOOGLE_GEMINI_PRO
        or inference_model_name == InferenceModelMaster.GOOGLE_GEMINI_1_5_PRO
    ) and ("google_api_key" in config):
        return ChatGoogleGenerativeAI(
            model=inference_model_name,
            google_api_key=config["google_api_key"],
            temperature=config["temperature"], 
            top_p=0.85,
            metadata= {'language': 'en'}
        )
    elif (inference_model_name == InferenceModelMaster.ANTHROPIC_CLAUDE_2_1
        or inference_model_name == InferenceModelMaster.ANTHROPIC_CLAUDE_3_SONNET 
        or inference_model_name == InferenceModelMaster.ANTHROPIC_CLAUDE_3_5_SONNET
        or inference_model_name == InferenceModelMaster.ANTHROPIC_CLAUDE_3_OPUS
        or inference_model_name == InferenceModelMaster.ANTHROPIC_CLAUDE_3_HAIKU
        ) and ("anthropic_api_key" in config):
        return ChatAnthropic(
            model=inference_model_name,
            anthropic_api_key=config["anthropic_api_key"],
            temperature=config["temperature"],
            top_p=0.85
        )
    elif (inference_model_name == InferenceModelMaster.DEEPSEEK_R1_LATEST
        or inference_model_name == InferenceModelMaster.DEEPSEEK_R1_14_B
        or inference_model_name == InferenceModelMaster.PHI_4_14_B
        or inference_model_name == InferenceModelMaster.LLAMA_3_1
        ) and ("base_url" in config):
        return OllamaLLM(
            model=inference_model_name,
            base_url=config["base_url"],
        )
    else:
        raise ValueError(f"Unknown inference model: {inference_model_name}")


async def create_embeddings(data_sources, embedding_model, collection_name):
    if(not os.getenv('THERIX_API_KEY')):
        store = get_vectorstore(embedding_model, collection_name)
    else:
        store = get_vectorstore(embedding_model, collection_name)
        
    config_id = []
    for data_source in data_sources:
        config_id.append(uuid.uuid4())
        # data_source = {'name': 'PDF', 'config': {'files': ['path/to/file', 'path/to/file']}}
        for file_path in data_source.config["files"]:
            loader = get_loader(data_source.name, file_path, data_source.config)
            extra_metadata = [
                ("configId", str(config_id)),
            ]
            pages = loader.load_and_split()
            for page_content in pages:
                for key, value in extra_metadata:
                    page_content.metadata[key] = value
            
            # document.text = mask_data(document.text)
            result=RecursiveCharacterTextSplitter(
                 chunk_size=1000,
                 chunk_overlap=200,
                ).split_documents(pages)
            if(os.getenv('THERIX_API_KEY')):
                await store.add_documents(result)
            else:
                store.add_documents(result)
    # config_id is a list, due to possibility of multiple data_source.
    return {"message" : "embedding created" , "config_id" : config_id}


def get_vectorstore(embedding_model, collection_name):
    embeddings = get_embedding_model(embedding_model.name, embedding_model.config)
    if(not os.getenv('THERIX_API_KEY')):
        store = PGVector(
            collection_name=collection_name,
            connection_string=get_sql_alchemy_url(),
            embedding_function=embeddings,
        )
    else:
        store = VectorStore(
            collection_name=collection_name,
            embedding_function=embeddings,    
        )
    return store


async def async_chat(
    question,
    retriever,
    inference_model,
    embed_model,
    session,
    pipeline_id,
    trace_details=None,
    pii_filter_config=None,
    system_prompt=None,
    output_parser=None,
    trace_api=None,
    db_url=None,
    metadata=None
):
    session_id = session.get('session_id')
    therix_trace_handler = get_trace_handler(trace_details, trace_api, system_prompt, pipeline_id, session_id, metadata)

    chain_callbacks = [therix_trace_handler] if therix_trace_handler else []

    history = TherixChatMessageHistory(
        str(session_id),
        str(pipeline_id),
        db_url or get_sql_alchemy_url(),
        table_name="chat_history",
    )
    message_history = history.get_message_history(str(session_id))
    chat_history = []
    if message_history:
        chat_history = [
            ChatMessage(role=message["message_role"], content=message["message"])
            for message in message_history
        ]

    if system_prompt:
        template = system_prompt.get("system_prompt") or system_prompt
        if "format_instructions" in template and not output_parser:
            template = template.replace("{format_instructions}", "")

        partial_vars = (
            {"format_instructions": output_parser.get_format_instructions()}
            if output_parser
            else {}
        )
    else:
        template = """
        Answer the question based only on the following context:

        {context}

        Answer the question based on the above context: {question}
        The response should be a valid JSON format with the output_parser structure {format_instructions}.
        """
        partial_vars = (
            {"format_instructions": output_parser.get_format_instructions()}
            if output_parser
            else {}
        )

    if partial_vars:
        ANSWER_PROMPT = PromptTemplate(
            template=template,
            input_variables=["context", "question"],
            partial_variables=partial_vars,
        )
    else:
        ANSWER_PROMPT = ChatPromptTemplate.from_template(template)

    CONDENSE_QUESTION_PROMPT = PromptTemplate.from_template(
        """Given the following conversation and a follow up question, rephrase the follow up question to be a standalone question, in its original language.
        Chat History:
        {chat_history}
        Follow Up Input: {question}
        Standalone question:"""
    )
    
    DEFAULT_DOCUMENT_PROMPT = PromptTemplate.from_template(
        template="{page_content} {source} {page}"
    )

    model = get_inference_model(inference_model.name, inference_model.config)

    if pii_filter_config:
        entities = pii_filter_config.config['entities']
        anonymizer = PresidioReversibleAnonymizer(
            analyzed_fields=entities,
            faker_seed=42
        )

        def _combine_documents(docs):
            doc_strings = [
                format_document(doc, DEFAULT_DOCUMENT_PROMPT)
                for doc in docs
            ]
            return anonymizer.anonymize("\n\n".join(doc_strings))

    else:
        def _combine_documents(docs):
            doc_strings = [
                format_document(doc, DEFAULT_DOCUMENT_PROMPT)
                for doc in docs
            ]
            return "\n\n".join(doc_strings)

    _inputs = RunnableParallel(
        standalone_question=RunnablePassthrough.assign(
            chat_history=lambda x: anonymizer.anonymize(get_buffer_string(x["chat_history"]))
            if pii_filter_config else get_buffer_string(x["chat_history"])
        )
        | CONDENSE_QUESTION_PROMPT
        | model
        | StrOutputParser(),
    )

    if session.get('source') == 'USER':
        _context = {
            "context": itemgetter("standalone_question") | retriever | _combine_documents,
            "question": lambda x: x["standalone_question"],
        }
    else:
        _context = {
            "context": itemgetter("standalone_question") | retriever | _combine_documents,
            "question": lambda x: question,
        }

    conversational_qa_chain = _inputs | _context | ANSWER_PROMPT | model

    config = {}
    if trace_details or trace_api:
        if output_parser:
            config = {"callbacks": [therix_trace_handler]}
        else:
            config = {"callbacks": [therix_trace_handler]}
    if output_parser and not (trace_details or trace_api):
        config = {"callbacks": [therix_trace_handler]}

    result = conversational_qa_chain.invoke(
        {"question": question, "chat_history": chat_history},
        config=config,
    )

    if inference_model.name in [InferenceModelMaster.BEDROCK_TEXT_EXPRES_V1, InferenceModelMaster.BEDROCK_TEXT_LITE_G1]:
        response = str(result)
    elif inference_model.name in [InferenceModelMaster.DEEPSEEK_R1_LATEST]:
        response = result
    else:
        response = json.loads(result.json())["content"]

    if pii_filter_config:
        response = anonymizer.deanonymize(response)

    history.add_message("user", question, pipeline_id, session_id)
    history.add_message("system", response, pipeline_id, session_id)
    
    return response


def chat(
    question,
    retriever,
    inference_model,
    embed_model,
    session,
    pipeline_id,
    trace_details=None,
    pii_filter_config=None,
    system_prompt=None,
    output_parser=None,
    trace_api=None,
    metadata=None,
    config = None
):
    session_id = session.get('session_id')
    create_trace = True if  os.getenv("CREATE_TRACE") == "True" else False
    if not config:
        therix_trace_handler = get_trace_handler(trace_details, trace_api, system_prompt, pipeline_id, session_id, metadata)
        chain_callbacks = [therix_trace_handler] if therix_trace_handler else []
    else :
        therix_trace_handler = config
    history = TherixChatMessageHistory(
        str(session_id),
        str(pipeline_id),
        get_sql_alchemy_url(),
        table_name="chat_history",
    )
    message_history = history.get_message_history(str(session_id))
    chat_history = []
    if message_history:
        chat_history = [
            ChatMessage(role=message["message_role"], content=message["message"])
            for message in message_history
        ]
    
    template = None
    partial_vars = {}

    if system_prompt:
        if "system_prompt" in system_prompt:
            template = system_prompt.get("system_prompt")
        else:
            template = system_prompt     
        if "format_instructions" in template and output_parser is None:
            template = template.replace("{format_instructions}", "")

        if output_parser:
            partial_vars = {"format_instructions": output_parser.get_format_instructions()} 
    else:
        if output_parser:
            template = """
            Answer the question based only on the following context and chat history:

            Context :{context}
            Chat History : {chat_history}

            Question: {question}


            The response should be a valid JSON format with the output_parser structure {format_instructions}.
            """
            partial_vars = {"format_instructions": output_parser.get_format_instructions()}
        else:
            template = """
            Answer the question based only on the following context and chat history:

            Context :{context}
            Chat History : {chat_history}
            question: {question}
            
            """

    if partial_vars:
        ANSWER_PROMPT = PromptTemplate(
            template=template,
            input_variables=["context", "question", "chat_history"],
            partial_variables=partial_vars,
        )
    else:
        ANSWER_PROMPT = PromptTemplate(
            template=template,
            input_variables=["context", "question", "chat_history"]
        )

    CONDENSE_QUESTION_PROMPT = PromptTemplate.from_template(
        """Given the following conversation and a follow up question, rephrase the follow up question to be a standalone question, in its original language.
        Chat History:
        {chat_history}
        Follow Up Input: {question} 
        Standalone question:"""
    )
    
    DEFAULT_DOCUMENT_PROMPT = PromptTemplate.from_template(
        template="{page_content} {source} {page}"
    )

    model = get_inference_model(inference_model.name, inference_model.config)

    if pii_filter_config:
        pii_filter_config = pii_filter_config.config
        entities = pii_filter_config['entities']
        anonymizer = PresidioReversibleAnonymizer(
        analyzed_fields=entities,
        faker_seed=42)

        def _combine_documents(
            docs, document_prompt=DEFAULT_DOCUMENT_PROMPT, document_separator="\n\n"
        ):
            doc_strings = [format_document(doc, document_prompt) for doc in docs]
            return anonymizer.anonymize(document_separator.join(doc_strings))
        
        _inputs = RunnableParallel(
        standalone_question=RunnablePassthrough.assign(
            chat_history=lambda x: anonymizer.anonymize(get_buffer_string(x["chat_history"]))
        )
        | CONDENSE_QUESTION_PROMPT
        | model
        | StrOutputParser(),
        )
    else :
        def _combine_documents(
            docs, document_prompt=DEFAULT_DOCUMENT_PROMPT, document_separator="\n\n"
        ):
            doc_strings = [format_document(doc, document_prompt) for doc in docs]
            return document_separator.join(doc_strings)
            
        _inputs = RunnableParallel(
        standalone_question=RunnablePassthrough.assign(
            chat_history=lambda x: get_buffer_string(x["chat_history"])
        )
        | CONDENSE_QUESTION_PROMPT
        | model
        | StrOutputParser(),
        )
    
    if session.get('source') == 'USER':
        _context = {
            "context": itemgetter("standalone_question") | retriever | _combine_documents,
            "question": lambda x: x["standalone_question"],
            "chat_history": lambda x: chat_history
        }
    else:
        _context = {
            "context": itemgetter("standalone_question") | retriever | _combine_documents,
            "question": lambda x: question,
            "chat_history": lambda x:chat_history
        }

    conversational_qa_chain = _inputs | _context | ANSWER_PROMPT | model

    config = {"callbacks": [therix_trace_handler]} if therix_trace_handler and create_trace is True else {}
    if((trace_details or trace_api) and output_parser):
        result = conversational_qa_chain.invoke({"question": question, "chat_history": chat_history , "format_instructions" : output_parser.get_format_instructions()},config=config)
    elif((trace_details or trace_api) and not output_parser):
        result = conversational_qa_chain.invoke({"question": question, "chat_history": chat_history},config=config)
    elif(output_parser and not (trace_details or trace_api)):
        result = conversational_qa_chain.invoke({"question": question, "chat_history": chat_history , "format_instructions" : output_parser.get_format_instructions()})
    else:   
        result = conversational_qa_chain.invoke(
            {"question": question, "chat_history": chat_history}
        )
   
    if inference_model.name in [InferenceModelMaster.BEDROCK_TEXT_EXPRES_V1, InferenceModelMaster.BEDROCK_TEXT_LITE_G1]:
        response = str(result)
    elif inference_model.name in [InferenceModelMaster.DEEPSEEK_R1_LATEST]:
        response = result
    else:
        response = json.loads(result.json())["content"]

    if pii_filter_config:
        response = anonymizer.deanonymize(response)

    history.add_message("user", question, pipeline_id, session_id)
    history.add_message("system", response, pipeline_id, session_id)
    
    return response


async def cloud_chat(
    question,
    store,
    inference_model,
    embedding_model,
    session,
    pipeline_id,
    trace_api,
    pii_filter_config,
    system_prompt,
    output_parser,
    metadata,
    trace_details=None,
    top_k=4
):
    session_id = session.get('session_id')
    therix_trace_handler = get_trace_handler(trace_details, trace_api, system_prompt, pipeline_id, session_id, metadata)
    
    if system_prompt:
        system_prompt = system_prompt.get('system_prompt')

    chain_callbacks = [therix_trace_handler] if therix_trace_handler else []
    
    chat_history_endpoint = API_Endpoint.CHAT_HISTORY_ENDPOINT
    
    history = TherixChatMessageHistory(
            session_id=str(session_id),
            pipeline_id=str(pipeline_id),
            api_url=chat_history_endpoint
        )
    message_history_response = await history.async_get_message_history(str(session_id))
    if message_history_response and 'data' in message_history_response and message_history_response['data']:
        message_history = message_history_response['data'][0]
    chat_history = [ChatMessage(role=msg["message_role"], content=msg["message"]) for msg in message_history]
    
    
    
    model = get_inference_model(inference_model.name, inference_model.config)
    
    relevant_documents = await store.get_relevant_documents(query=question, topK=top_k, agent_id = pipeline_id)
    
    context = ""
    for doc in relevant_documents["data"]:
        context += doc["document"]+" "+f"{doc['cmetadata']}"
    
    if(chat_history):
        question = f"""Given the following conversation and a follow up question, answer the question.
            Chat History:
            {chat_history}
            Follow Up Input: {question}
            """
    else:
        question = question
    
    if(output_parser and system_prompt):
        format_instructions = output_parser.get_format_instructions()
        if("format_instructions" in system_prompt):
            prompt = system_prompt
    elif(output_parser and not system_prompt):
        format_instructions = output_parser.get_format_instructions()
        prompt = """You are a skilled professional who understands All kinds of documents. 
                You will be provided with Content and keywords.
                You have Analyze given data.
                Answer the question based only on the following context:
                {context}
                
                standalone question:
                {question}
                
                Response should be in valid JSON format.
                {format_instructions}
                """
                
    elif(system_prompt and not output_parser):
        prompt = system_prompt
    else:
        prompt = """You are a skilled professional who understands All kinds of documents. 
                You will be provided with Content and keywords.
                You have Analyze given data.
                Answer the question based only on the following context:
                {context}
                {question}
                """
                
    if(output_parser):
        prompt = PromptTemplate(
            template=prompt,
            input_variables=["context", "question"],
            partial_variables={"format_instructions": format_instructions}
        )
        chain = prompt | model | output_parser
        
        if(trace_details or trace_api):
            result : Any = chain.invoke({"question": question, "context": context}, config={"callbacks": [therix_trace_handler]})
        else:
            result : Any = chain.invoke({"question": question, "context": context})
        response = json.loads(result.json()) 
        await history.async_add_message("user", question, pipeline_id, session_id)
        await history.async_add_message("system", str(response), pipeline_id, session_id)
    
        return response
    else:
        prompt = PromptTemplate(
            template=prompt,
            input_variables=["context", "question"],
        )
        chain = prompt | model

        if(trace_details or trace_api):
            result : Any = chain.invoke({"question": question, "context": context}, config={"callbacks": [therix_trace_handler]})
        else:
            result : Any = chain.invoke({"question": question, "context": context})

    
        response = json.loads(result.json()) 
        await history.async_add_message("user", question, pipeline_id, session_id)
        await history.async_add_message("system", str(response['content']), pipeline_id, session_id)
        
        return response['content']
    
    # if pii_filter_config:
    #     pii_filter_config = pii_filter_config.config
    #     entities = pii_filter_config['entities']
    #     anonymizer = PresidioReversibleAnonymizer(
    #     analyzed_fields=entities,
    #     faker_seed=42)
        
    

    
    