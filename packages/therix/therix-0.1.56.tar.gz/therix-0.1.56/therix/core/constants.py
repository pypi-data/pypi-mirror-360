from enum import Enum
import os
class DataSourceMaster:
    TEXT = "TEXT"
    PDF = "PDF"
    PDF_DI = "PDF_DI"  # Document Intelligence PDF
    WEBSITE = "WEBSITE"
    DOCX = "DOCX"
    CSV = "CSV"
    DATABASE = "DATABASE"
    YOUTUBE="YOUTUBE"
    JSON = "JSON"

class EmbeddingModelMaster:
    OPENAI_TEXT_ADA = 'text-embedding-ada-002'
    OPENAI_TEXT_EMBEDDING_3_LARGE = 'text-embedding-3-large'
    OPENAI_TEXT_EMBEDDING_3_SMALL = 'text-embedding-3-small'
    AZURE_TEXT_ADA='text-embedding-ada-002'
    AZURE_TEXT_EMBEDDING_3_LARGE = 'text-embedding-3-large'
    AZURE_TEXT_EMBEDDING_3_SMALL = 'text-embedding-3-small'
    BEDROCK_TITAN_EMBEDDING='amazon.titan-embed-text-v1'
    BEDROCK_TITAN_MULTIMODAL_EMBEDDING='amazon.titan-embed-image-v1'
    GEMINI_EMBEDDING='models/embedding-001'

class InferenceModelMaster:
    OPENAI_GPT_4_TURBO_PREVIEW = 'gpt-4-turbo-preview'
    OPENAI_GPT_4 = 'gpt-4'
    OPENAI_GPT_4_O = 'gpt-4o'
    OPENAI_GPT_4_O_MINI = 'gpt-4o-mini'
    OPENAI_GPT_3_5_TURBO = 'gpt-3.5-turbo'
    OPENAI_GPT_3_5_TURBO_INSTRUCT = 'gpt-3.5-turbo-instruct'
    AZURE_GPT_4_TURBO_PREVIEW = 'gpt-4-turbo-preview'
    AZURE_GPT_4 = 'gpt-4'
    AZURE_GPT_4_O = 'gpt-4o'
    AZURE_GPT_3_5_TURBO = 'gpt-3.5-turbo'
    AZURE_GPT_3_5_TURBO_INSTRUCT = 'gpt-3.5-turbo-instruct'
    GROQ_LLM_MIXTRAL_8_7_B='mixtral-8x7b-32768'
    GROQ_LLM_LLAMA3_70B= 'llama3-70b-8192'
    GROQ_LLM_GEMMA7B= 'gemma-7b-it'
    GROQ_LLM_LLAMA3_8B= 'llama3-8b-8192'
    GROQ_LLM_LLAMA3_1_8B= 'llama-3.1-8b-instant'
    GROQ_LLM_LLAMA3_1_70B= 'llama-3.1-70b-versatile'
    GROQ_LLM_LLAMA3_1_405B= 'llama-3.1-405b-reasoning'
    BEDROCK_TEXT_EXPRES_V1='amazon.titan-text-express-v1'
    BEDROCK_TEXT_LITE_G1='amazon.titan-text-lite-v1'
    BEDROCK_TEXT_PREMIER_G1='amazon.titan-text-premier-v1'
    GOOGLE_GEMINI_PRO='gemini-pro'
    GOOGLE_GEMINI_1_5_PRO='gemini-1.5-pro'
    ANTHROPIC_CLAUDE_3_OPUS='claude-3-opus-20240229'
    ANTHROPIC_CLAUDE_2_1='claude-2.1'
    ANTHROPIC_CLAUDE_3_HAIKU='claude-3-haiku-20240307-v1'
    ANTHROPIC_CLAUDE_3_SONNET='claude-3-sonnet-20240307-v1'
    ANTHROPIC_CLAUDE_3_5_SONNET='claude-3-5-sonnet-20240620-v1'
    DEEPSEEK_R1_LATEST = 'deepseek-r1:latest'
    PHI_4_14_B = 'phi4:14b'
    DEEPSEEK_R1_14_B = 'deepseek-r1:14b'
    LLAMA_3_1 = 'llama3.1'

class OutputSourceMaster:
    S3 = "S3"
    LOCAL = "LOCAL"
    DATABASE = "DATABASE"


class ChatMessage(Enum):
    CHAT_SAVED = "Message saved successfully!"
    CHAT_FAILED = "Error saving message"
    FAILED_TO_RETRIEVE = "Error retrieving message history"

class PipelineTypeMaster(Enum):
    RAG = 'RAG'
    SUMMARIZER = 'SUMMARIZER'
    DEFAULT = 'DEFAULT'
    
class API_Endpoint:
    
    if(os.getenv("THERIX_BASE_URL") is not None):
        BASE_URL = os.getenv("THERIX_BASE_URL")    
    else:
        BASE_URL = 'https://cloud-api.therix.ai/api/sdk/'
        
    EMBEDDING_ENDPOINT = f"{BASE_URL}embedding" 
    CHAT_HISTORY_ENDPOINT = f"{BASE_URL}chat-history/"
    TRACE_INGESTION = BASE_URL.replace('/api/sdk','')