from enum import Enum
import json
import os

from anyio import create_task_group
import therix
import asyncio
from therix.core.chat_history.base_chat_history import TherixChatMessageHistory
from therix.core.constants import API_Endpoint, InferenceModelMaster
from therix.db.session import get_sql_alchemy_url
from therix.utils.rag import get_inference_model
from langchain.prompts.chat import ChatPromptTemplate, MessagesPlaceholder
from langfuse.callback import CallbackHandler
from langchain_core.messages.chat import ChatMessage
from therix.services.trace_handler import get_trace_handler


DEFAULT_SYSTEM_PROMPT = "You are a helpful chatbot, you can use your own brain to provide answer to questions by users. The question is: {question}"


async def async_invoke_default_chat(inference_model_details, session, pipeline_id, question, trace_details=None, system_prompt=None, trace_api=None, db_url=None, metadata=None, config = None):
    
    session_id = session.get('session_id')
    create_trace = True if  os.getenv("CREATE_TRACE") == "True" else False
    if not config:
        therix_trace_handler = get_trace_handler(trace_details, trace_api, system_prompt, pipeline_id, session_id, metadata)
        chain_callbacks = [therix_trace_handler] if therix_trace_handler else []
    else:    
        therix_trace_handler = config
    
    history = TherixChatMessageHistory(
        str(session_id),
        str(pipeline_id),
        db_url or get_sql_alchemy_url(),
        table_name="chat_history",
    )
    message_history = await history.get_message_history(str(session_id))
    chat_history = [ChatMessage(role=msg["message_role"], content=msg["message"]) for msg in message_history]

    model = get_inference_model(inference_model_details.name, inference_model_details.config)
    system_prompt_text = system_prompt.get('system_prompt', DEFAULT_SYSTEM_PROMPT) if system_prompt else DEFAULT_SYSTEM_PROMPT

    ANSWER_PROMPT = ChatPromptTemplate.from_messages([
        ("system", system_prompt_text),
        MessagesPlaceholder("chat_history"),
        ("human", "{question}")
    ])

    chain = ANSWER_PROMPT | model
    chain_input = {"question": question, "chat_history": chat_history}
    config = {"callbacks": [therix_trace_handler]} if therix_trace_handler  and create_trace is True else {}

    result = await chain.invoke(chain_input, config=config)

    if inference_model_details.name in [InferenceModelMaster.BEDROCK_TEXT_EXPRES_V1, InferenceModelMaster.BEDROCK_TEXT_LITE_G1]:
        response = f'{result}'
    elif inference_model_details.name in [InferenceModelMaster.DEEPSEEK_R1_LATEST]:
        response = result
    else:
        response = json.loads(result.json())["content"]

    await history.add_message("user", question, pipeline_id, session_id)
    await history.add_message("system", response, pipeline_id, session_id)
    return response


def invoke_default_chat(inference_model_details, session, pipeline_id, question, trace_details=None, system_prompt=None, trace_api=None, metadata=None, config = None):
    session_id = session.get('session_id')

    create_trace = True if  os.getenv("CREATE_TRACE") == "True" else False

    if not config:
        therix_trace_handler = get_trace_handler(trace_details, trace_api, system_prompt, pipeline_id, session_id, metadata)
        chain_callbacks = [therix_trace_handler] if therix_trace_handler  and create_trace is True else []
    else:
        therix_trace_handler = config
    history = TherixChatMessageHistory(
            str(session_id),
            str(pipeline_id),
            get_sql_alchemy_url(),
            table_name="chat_history"
    )

    message_history = history.get_message_history(str(session_id))
    chat_history = [ChatMessage(role=msg["message_role"], content=msg["message"]) for msg in message_history]

    model = get_inference_model(inference_model_details.name, inference_model_details.config)
    system_prompt_text = system_prompt.get('system_prompt', DEFAULT_SYSTEM_PROMPT) if system_prompt else DEFAULT_SYSTEM_PROMPT

    ANSWER_PROMPT = ChatPromptTemplate.from_messages([
        ("system", system_prompt_text),
        MessagesPlaceholder("chat_history"),
        ("human", "{question}")
    ])

    chain = ANSWER_PROMPT | model
    chain_input = {"question": question, "chat_history": chat_history}
    config = {"callbacks": [therix_trace_handler]} if therix_trace_handler and create_trace is True else {}

    result = chain.invoke(chain_input, config=config)

    if inference_model_details.name in [InferenceModelMaster.BEDROCK_TEXT_EXPRES_V1, InferenceModelMaster.BEDROCK_TEXT_LITE_G1]:
        response = f'{result}'
    elif inference_model_details.name in [InferenceModelMaster.DEEPSEEK_R1_LATEST]:
        response = result
    else:
        response = json.loads(result.json())["content"]

    history.add_message("user", question, pipeline_id, session_id)
    history.add_message("system", response, pipeline_id, session_id)
    return response


async def invoke_default_cloud_chat(inference_model_details, session, pipeline_id, question, trace_details=None, system_prompt=None, trace_api=None, db_url=None, metadata=None, therix_api_key=None):
    session_id = session.get('session_id')
    create_trace =True if  os.getenv("CREATE_TRACE") == "True" else False
    therix_trace_handler = get_trace_handler(trace_details, trace_api, system_prompt, pipeline_id, session_id, metadata)

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
    model = get_inference_model(inference_model_details.name, inference_model_details.config)
    system_prompt_text = system_prompt.get('system_prompt', DEFAULT_SYSTEM_PROMPT) if system_prompt else DEFAULT_SYSTEM_PROMPT

    ANSWER_PROMPT = ChatPromptTemplate.from_messages([
        ("system", system_prompt_text),
        MessagesPlaceholder("chat_history"),
        ("human", "{question}")
    ])

    chain = ANSWER_PROMPT | model
    chain_input = {"question": question, "chat_history": chat_history}
    config = {"callbacks": [therix_trace_handler]} if therix_trace_handler and create_trace is True else {}

    result = chain.invoke(chain_input, config=config)

    if inference_model_details.name in [InferenceModelMaster.BEDROCK_TEXT_EXPRES_V1, InferenceModelMaster.BEDROCK_TEXT_LITE_G1]:
        response = f'{result}'
    elif inference_model_details.name in [InferenceModelMaster.DEEPSEEK_R1_LATEST, InferenceModelMaster.PHI_4_14_B, InferenceModelMaster.LLAMA_3_1, InferenceModelMaster.DEEPSEEK_R1_14_B]:
        response = result
    else:
        response = json.loads(result.json())["content"]
        

    await history.async_add_message("user", question, pipeline_id, session_id)
    await history.async_add_message("system", response, pipeline_id, session_id)
    return response