from typing import Any, List
from wsgiref import headers
from langchain_core.documents import Document
import uuid
import aiohttp
import asyncio
import logging
import json
import os

from therix.core.constants import API_Endpoint
class VectorStore:
    def __init__(self, collection_name, embedding_function):
        self.collection = collection_name
        self.embeddings = embedding_function        
        
    async def add_documents(self, documents: List[Document], **kwargs: Any) -> List[str]:
        async with aiohttp.ClientSession() as session:
            tasks = []
            print('Generating Embeddings ...')
            for doc in documents:
                embeddings = self.embeddings.embed_query(doc.page_content)
        
                payload = {
                    "agent_id": self.collection,
                    "document_id": str(uuid.uuid4()),
                    "document": doc.page_content,
                    "embeddings": embeddings,
                    "cmetadata": doc.metadata
                }
                
                api_endpoint = API_Endpoint.EMBEDDING_ENDPOINT
                
                tasks.append(self.post_to_server(session, api_endpoint, payload))

            responses = await asyncio.gather(*tasks)
            return responses


    async def get_relevant_documents(self, query: str , topK: int, agent_id: str):
        try:
            async with aiohttp.ClientSession() as session: 
                embedded_query = self.embeddings.embed_query(query)
                
                api_endpoint = API_Endpoint.EMBEDDING_ENDPOINT
                
                payload = {
                    "embeddings" : embedded_query,
                    "topK" : topK,
                    "agent_id" : agent_id
                }
                headers = {
                "THERIX_API_KEY": os.getenv('THERIX_API_KEY'),
                "Content-Type": "application/json"
            }
                
                async with session.get(api_endpoint, json=payload, headers=headers) as response:
                    response.raise_for_status()
                    return await response.json()
        except aiohttp.ClientError as e:
            logging.error(e)
            return None
    
    async def post_to_server(self, session, url, payload):
        try:
            headers = {
                "THERIX_API_KEY": os.getenv('THERIX_API_KEY'),
                "Content-Type": "application/json"
            }
            async with session.post(url, json=payload, headers=headers) as response:
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientError as e:
            logging.error(e)
            return None
    
