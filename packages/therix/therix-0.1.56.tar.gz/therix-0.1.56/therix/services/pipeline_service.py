from hmac import new
from logging import config
import trace
from typing import Any, List
import therix
from therix.core import embedding_models, pipeline
from therix.utils.summarizer import summarizer, async_summarizer
from ..db.session import SessionLocal
from ..entities.models import ConfigType, Pipeline, PipelineConfiguration
import json
import os
import asyncio
import urllib
from therix.services.web_crawling import crawl_website
from therix.utils.pii_filter import pii_filter
from ..db.session import SessionLocal
from therix.utils.rag import (
    chat,
    cloud_chat,
    create_embeddings,
    get_embedding_model,
    get_vectorstore,
    get_loader,
    async_chat,
)
from langchain_openai import AzureOpenAIEmbeddings
from therix.utils.keyword_search import async_keyword_search, cloud_keyword_search, keyword_search, async_keyword_search
from therix.services.api_service import ApiService
from types import SimpleNamespace
from therix.utils.default_chat import async_invoke_default_chat, invoke_default_chat, async_invoke_default_chat, invoke_default_cloud_chat
from langchain.retrievers.merger_retriever import MergerRetriever
import re

class DictToObject:
    def __init__(self, dictionary):
        for key, value in dictionary.items():
            setattr(self, key, value)

class PipelineService:
    def __init__(self, therix_api_key=None, trace_api_key=None):
        self.db_session = SessionLocal()
        self.trace_api_key = trace_api_key
        self.therix_api_key = therix_api_key
        self.api_service = ApiService(therix_api_key) if therix_api_key else None

    def create_pipeline_with_configurations(self, pipeline_data, configurations_data):
        old_configuration_data = configurations_data

        if self.therix_api_key:
            # Adjust configurations before making the API request
            for config_data in configurations_data:
                if config_data["config_type"] == "INFERENCE_MODEL":
                    config = config_data.get("config", {})
                    config.setdefault("temperature", 0.5)
                    config_data["config"] = config

            # Remove 'pipeline_id' before sending the payload
            configurations_data = [{key: value for key, value in config_data.items() if key != "pipeline_id"} for config_data in configurations_data]

            payload = {
                "name": pipeline_data.get("name"),
                "status": pipeline_data.get("status"),
                "type": pipeline_data.get("type"),
                "agent_configurations": configurations_data,
            }
            response_data = self.api_service.post("agent/", payload)
            return DictToObject(response_data['data'])
        else:
            new_pipeline = Pipeline(**pipeline_data)
            self.db_session.add(new_pipeline)
            self.db_session.flush()

            for config_data in configurations_data:
                config_data["pipeline_id"] = str(new_pipeline.id)  # Convert UUID to string here
                new_config = PipelineConfiguration(**config_data)
                if new_config.config_type == "INFERENCE_MODEL":
                    new_config.config.setdefault("temperature", 0.5)
                self.db_session.add(new_config)
            self.db_session.commit()

            if self.trace_api_key:
                self.api_service = ApiService(therix_api_key=self.trace_api_key)
                old_configuration_data = [{key: value for key, value in config_data.items() if key != "pipeline_id"} for config_data in old_configuration_data]
                payload = {
                    "id": str(new_pipeline.id),  
                    "name": pipeline_data.get("name"),
                    "status": pipeline_data.get("status"),
                    "type": pipeline_data.get("type"),
                    "agent_configurations": old_configuration_data,
                }
                response_data = self.api_service.post("agent/", payload)
                return new_pipeline
            else:
                raise Exception("Trace API key not provided")    

            

    def update_pipeline_configuration(self, pipeline_id, component):
        agent_configuration_id = self.get_pipeline_configurations_by_type(
            pipeline_id, component['config_type']
        )
        if agent_configuration_id:
            self.api_service.patch(f"agent-config/{agent_configuration_id[0].id}", component)

    def get_db_url(self):
        database_url = self.api_service.get("agent/db-url")
        return database_url['data']

    def get_trace_creds(self):
        trace_creds = self.api_service.get("trace-keys")
        return trace_creds['data']

    def get_prompt_by_name(self, prompt_name, variables=None):
        response_data = self.api_service.get("prompts/active", params={"prompt_name": prompt_name})
        prompt_template = response_data['data']['prompt']
        name = response_data['data']['name']
        prompt_version = response_data['data']['version']

        def replace_placeholders(template, variables):
            if not variables:
                return template
            def replacer(match):
                key = match.group(1).strip()
                return variables.get(key, match.group(0))
            return re.sub(r'\{([\w\s]+)\}', replacer, template)
        
        formatted_prompt = replace_placeholders(prompt_template, variables)
        return {
            "prompt_name": name,
            "prompt_version": prompt_version,
            "system_prompt": formatted_prompt
        }

    def publish_pipeline(self, pipeline_data):
        pipeline = self.db_session.query(Pipeline).filter_by(id=pipeline_data.get("id")).first()
        if pipeline:
            pipeline.status = "PUBLISHED"
            self.db_session.commit()
        return pipeline

    def get_pipeline(self, pipeline_id):
        if self.therix_api_key:
            response_data = self.api_service.get(f"agent/{pipeline_id}")
            return DictToObject(response_data['data'])
        else:
            return self.db_session.query(Pipeline).filter_by(id=pipeline_id).first()

    def get_pipeline_configuration(self, pipeline_id):
        if self.therix_api_key:
            response_data = self.api_service.get(f"agent/{pipeline_id}")
            return DictToObject(response_data['data'])
        else:
            return self.db_session.query(PipelineConfiguration).filter_by(pipeline_id=pipeline_id).all()

    def get_pipeline_configurations_by_type(self, pipeline_id, config_type):
        if self.therix_api_key:
            params = {"agent_id": pipeline_id, "config_type": config_type if isinstance(config_type, str) else config_type.value}
            response_data = self.api_service.get("agent-config/", params=params)
            data = response_data.get('data', [])
            if not data:
                return None

            first_index_data = data[0]
            if isinstance(first_index_data, list) and first_index_data:
                return [DictToObject(item) for item in first_index_data]
            else:
                return None
        else:
            return self.db_session.query(PipelineConfiguration).filter_by(pipeline_id=pipeline_id, config_type=config_type).all()

    async def preprocess_data(self, pipeline_id):
        data_sources = self.get_pipeline_configurations_by_type(pipeline_id, "INPUT_SOURCE")
        output_file = None
        if data_sources and hasattr(data_sources[0].config, "website"):
            website_url = data_sources[0].config["website"]
            web_content = crawl_website(website_url)
            domain_name = urllib.parse.urlparse(website_url).netloc
            output_file = f"{domain_name}_data.json"
            with open(output_file, "w") as f:
                json.dump(web_content, f, indent=4)
            data_sources[0].config["files"] = [output_file]
            os.remove(output_file)
        embedding_model = self.get_pipeline_configurations_by_type(pipeline_id, "EMBEDDING_MODEL")
        return await create_embeddings(data_sources, embedding_model[0], str(pipeline_id))



    async def async_invoke_pipeline(
        self, 
        pipeline_id, 
        question, 
        session, 
        trace_details=None, 
        system_prompt=None, 
        db_url=None, 
        trace_api=None, 
        pipeline_ids=None, 
        output_parser=None,
        metadata=None,
        top_k=4
    ):
            async def get_store(pipeline_id):
                embedding_model = await self.get_pipeline_configurations_by_type(pipeline_id, ConfigType.EMBEDDING_MODEL)
                if self.therix_api_key:
                    return await get_vectorstore(embedding_model[0], str(pipeline_id), self.get_db_url())
                else:
                    return await get_vectorstore(embedding_model[0], str(pipeline_id))

            if pipeline_ids:
                combined_retrievers = [await get_store(pid).as_retriever(search_kwargs={"k": top_k}) for pid in pipeline_ids]
                retriever = MergerRetriever(retrievers=combined_retrievers)
            else:
                retriever = (await get_store(pipeline_id)).as_retriever(search_kwargs={"k": top_k})

            inference_model = await self.get_pipeline_configurations_by_type(pipeline_id, ConfigType.INFERENCE_MODEL)

            pii_filter_config = await self.get_pipeline_configurations_by_type(pipeline_id, ConfigType.PII_FILTER)
            pii_filter_config = pii_filter_config[0] if pii_filter_config else None

            result = await async_chat(
                question,
                retriever,
                inference_model[0],
                embedding_model,
                session,
                pipeline_id,
                trace_api=trace_api,
                trace_details=trace_details,
                pii_filter_config=pii_filter_config,
                system_prompt=system_prompt,
                db_url=db_url,
                output_parser=output_parser,
                metadata=metadata
            )

            if pii_filter_config:
                entities = pii_filter_config.config['entities']
                return await pii_filter(result, entities)
            else:
                return result


    async def invoke_pipeline(
        self,
        pipeline_id,
        question,
        session,
        trace_details=None,
        system_prompt=None,
        trace_api=None,
        pipeline_ids=None,
        output_parser=None,
        metadata=None,
        config = None,
        top_k = 4
    ):

        embedding_model = None
        if self.therix_api_key:
            def get_store(pipeline_id):
                embedding_model: Any = self.get_pipeline_configurations_by_type(
                    pipeline_id, ConfigType.EMBEDDING_MODEL
                )
                return get_vectorstore(embedding_model[0], str(pipeline_id))

            if(pipeline_ids):
                store = [get_store(pid) for pid in pipeline_ids]
            else:
                store = get_store(pipeline_id)

            inference_model = self.get_pipeline_configurations_by_type(
                pipeline_id, ConfigType.INFERENCE_MODEL
            )

            pii_filter_config = self.get_pipeline_configurations_by_type(
                pipeline_id, ConfigType.PII_FILTER
            )
            pii_filter_config = pii_filter_config[0] if pii_filter_config else None
            result = await cloud_chat(
                    question,
                    store,
                    inference_model[0],
                    embedding_model,
                    session,
                    pipeline_id,
                    trace_api=trace_api,
                    pii_filter_config=pii_filter_config,
                    system_prompt=system_prompt,
                    output_parser=output_parser,
                    metadata=metadata,
                    trace_details=trace_details,
                    top_k=top_k
                )
            
            if pii_filter_config:
                entities = pii_filter_config.config["entities"]
                return pii_filter(result, entities)
            else:
                return result

        else:

            def get_store(pipeline_id):
                embedding_model: Any = self.get_pipeline_configurations_by_type(
                    pipeline_id, ConfigType.EMBEDDING_MODEL
                )
                return get_vectorstore(
                    embedding_model[0], str(pipeline_id)
                )

            if pipeline_ids:
                combined_retrievers = [
                    get_store(pid).as_retriever(search_kwargs={"k": top_k}) for pid in pipeline_ids
                ]
                retriever = MergerRetriever(retrievers=combined_retrievers)
            else:
                retriever = get_store(pipeline_id).as_retriever(search_kwargs={"k": top_k})

            inference_model = self.get_pipeline_configurations_by_type(
                pipeline_id, ConfigType.INFERENCE_MODEL
            )

            pii_filter_config = self.get_pipeline_configurations_by_type(
                pipeline_id, ConfigType.PII_FILTER
            )
            pii_filter_config = pii_filter_config[0] if pii_filter_config else None

            result = chat(
                question,
                retriever,
                inference_model[0],
                embedding_model,
                session,
                pipeline_id,
                trace_api=trace_api,
                trace_details=trace_details,
                pii_filter_config=pii_filter_config,
                system_prompt=system_prompt,
                output_parser=output_parser,
                metadata=metadata,
                config = config
            )

            if pii_filter_config:
                entities = pii_filter_config.config["entities"]
                return pii_filter(result, entities)
            else:
                return result
   

    
    async def async_invoke_summarizer_pipeline(
        self, 
        pipeline_id, 
        text, 
        session, 
        trace_details=None, 
        trace_api=None, 
        system_prompt=None, 
        metadata=None,
        config = None
    ):
        """
        Asynchronously invoke the summarizer pipeline for a given pipeline_id and input text.

        This method fetches the summarizer and inference model configurations for the pipeline,
        then calls the async_summarizer utility to perform summarization using the appropriate LLM.

        Args:
            pipeline_id (str): The pipeline identifier.
            text (str): The input text to summarize.
            session (dict): The session context (should contain 'session_id').
            trace_details (dict, optional): Trace details for logging/tracing.
            trace_api (dict, optional): Trace API info for logging/tracing.
            system_prompt (str or dict, optional): System prompt for the LLM.
            metadata (dict, optional): Additional metadata for trace logging or context.
            config (optional): Additional config for the summarizer.

        Returns:
            The summarization result (usually a string or dict, depending on summarizer config).
        """
        inference_model = self.get_pipeline_configurations_by_type(pipeline_id, ConfigType.INFERENCE_MODEL)[0]
        summarizer_config = self.get_pipeline_configurations_by_type(pipeline_id, ConfigType.SUMMARIZER)[0].config

        return async_summarizer(
            summarizer_config,
            inference_model,
            text,
            trace_details,
            pipeline_id,
            system_prompt,
            trace_api=trace_api,
            session_id=session.get('session_id'),
            metadata=metadata,
            config = config
        )

    def invoke_summarizer_pipeline(
    self, 
    pipeline_id, 
    text, 
    session, 
    trace_details=None, 
    trace_api=None, 
    system_prompt=None,
    metadata=None,
    config = None
):
        inference_model = self.get_pipeline_configurations_by_type(pipeline_id, ConfigType.INFERENCE_MODEL)[0]
        summarizer_config = self.get_pipeline_configurations_by_type(pipeline_id, ConfigType.SUMMARIZER)[0].config

        return summarizer(
            summarizer_config,
            inference_model,
            text,
            trace_details,
            pipeline_id,
            system_prompt,
            trace_api=trace_api,
            session_id=session.get('session_id'),
            metadata=metadata,
            config = config
        )

    
    
    async def async_invoke_default_pipeline(
    self, 
    pipeline_id, 
    session, 
    question, 
    trace_details=None, 
    system_prompt=None, 
    trace_api=None, 
    db_url=None,
    metadata=None,
    config = None
):
        inference_model = (await self.get_pipeline_configurations_by_type(pipeline_id, ConfigType.INFERENCE_MODEL))[0]
        db_url = await self.get_db_url() if self.therix_api_key else db_url

        return await async_invoke_default_chat(
            inference_model_details=inference_model,
            session=session,
            pipeline_id=pipeline_id,
            question=question,
            trace_details=trace_details,
            system_prompt=system_prompt,
            trace_api=trace_api,
            db_url=db_url,
            config=config,
            metadata=metadata
        )

    
    
    async def invoke_default_pipeline(
        self, 
        pipeline_id, 
        session, 
        question, 
        trace_details=None, 
        system_prompt=None, 
        trace_api=None, 
        db_url=None,
        metadata=None,
        config = None
    ):
        inference_model = self.get_pipeline_configurations_by_type(pipeline_id, ConfigType.INFERENCE_MODEL)[0]

        if(not self.therix_api_key):
            return invoke_default_chat(
                inference_model_details=inference_model,
                session=session,
                pipeline_id=pipeline_id,
                question=question,
                trace_details=trace_details,
                system_prompt=system_prompt,
                trace_api=trace_api,
                metadata=metadata,
                config = config
            )
        else:
            return await invoke_default_cloud_chat(
            inference_model_details=inference_model,
            session=session,
            pipeline_id=pipeline_id,
            question=question,
            trace_details=trace_details,
            system_prompt=system_prompt,
            trace_api=trace_api,
            metadata=metadata,
            therix_api_key=self.therix_api_key
        )


    async def async_search_keywords(self, keyword_search_params, top_k=4):
        required_params = ["prompt", "keywords", "output_parser"]
        if not all(param in keyword_search_params for param in required_params):
            return "Request is missing required parameters, please provide all the parameters, i.e. pipeline_id, prompt, keywords, output_parser"

        async def get_store(pipeline_id):
            embedding_model = self.get_pipeline_configurations_by_type(pipeline_id, ConfigType.EMBEDDING_MODEL)[0]
            if self.therix_api_key:
                return await get_vectorstore(embedding_model, str(pipeline_id), self.get_db_url())
            return await get_vectorstore(embedding_model, str(pipeline_id))

        if "pipeline_ids" in keyword_search_params:
            combined_retrievers = [await get_store(pipeline_id).as_retriever(search_kwargs={"k": top_k}) for pipeline_id in keyword_search_params["pipeline_ids"]]
            retriever = MergerRetriever(retrievers=combined_retrievers)
        else:
            pipeline_id = keyword_search_params.get("pipeline_id")
            retriever = await get_store(pipeline_id).as_retriever(search_kwargs={"k": top_k})

        active_pipeline_id = keyword_search_params.get("active_pipeline_id") or \
                            keyword_search_params.get("pipeline_ids", [])[-1] or \
                            keyword_search_params.get("pipeline_id")

        inference_model = self.get_pipeline_configurations_by_type(active_pipeline_id, ConfigType.INFERENCE_MODEL)[0]

        keyword_search_dict = {
            "retriever": retriever,
            "pipeline_id": active_pipeline_id,
            "keywords": keyword_search_params.get("keywords"),
            "output_parser": keyword_search_params.get("output_parser"),
            "prompt": keyword_search_params.get("prompt"),
            "trace_details": keyword_search_params.get("trace_details"),
            "trace_api": keyword_search_params.get("trace_api"),
            "inference_model": inference_model,
            "session": keyword_search_params.get("session"),
        }

        return await async_keyword_search(keyword_search_dict)


    async def search_keywords(self, keyword_search_params, top_k=4):
        # required_params = ["prompt", "keywords", "output_parser"]
        # if not all(param in keyword_search_params for param in required_params):
        #     return "Request is missing required parameters, please provide all the parameters, i.e. pipeline_id, prompt, keywords, output_parser"
        if (self.therix_api_key):
            def get_store(pipeline_id):
                embedding_model = self.get_pipeline_configurations_by_type(pipeline_id, ConfigType.EMBEDDING_MODEL)[0]
                return get_vectorstore(embedding_model, str(pipeline_id))    

            if keyword_search_params["pipeline_ids"]:
                store = [get_store(pipeline_id) for pipeline_id in keyword_search_params["pipeline_ids"]]  
            else:
                pipeline_id = keyword_search_params.get("pipeline_id")
                store = get_store(pipeline_id)

            active_pipeline_id = keyword_search_params.get("active_pipeline_id") or \
                                keyword_search_params.get("pipeline_ids", [])[-1] or \
                                keyword_search_params.get("pipeline_id")

            inference_model = self.get_pipeline_configurations_by_type(active_pipeline_id, ConfigType.INFERENCE_MODEL)[0]

            keyword_search_dict = {
                "store": store,
                "pipeline_id": active_pipeline_id,
                "keywords": keyword_search_params.get("keywords"),
                "output_parser": keyword_search_params.get("output_parser"),
                "prompt": keyword_search_params.get("prompt"),
                "trace_details": keyword_search_params.get("trace_details"),
                "trace_api": keyword_search_params.get("trace_api"),
                "inference_model": inference_model,
                "session": keyword_search_params.get("session"),
            }

            return await cloud_keyword_search(keyword_search_dict)
        else:
            def get_store(pipeline_id):
                embedding_model = self.get_pipeline_configurations_by_type(pipeline_id, ConfigType.EMBEDDING_MODEL)[0]
                return get_vectorstore(embedding_model, str(pipeline_id))
        
            if keyword_search_params['pipeline_ids'] is not None:
                combined_retrievers = [get_store(pipeline_id).as_retriever(search_kwargs={"k": top_k}) for pipeline_id in keyword_search_params["pipeline_ids"]]
                retriever = MergerRetriever(retrievers=combined_retrievers)
            else:
                pipeline_id = keyword_search_params.get("pipeline_id")
                retriever = get_store(pipeline_id).as_retriever(search_kwargs={"k": top_k})

            active_pipeline_id = keyword_search_params.get("active_pipeline_id") or \
                                keyword_search_params.get("pipeline_ids", [])[-1] or \
                                keyword_search_params.get("pipeline_id")

            inference_model = self.get_pipeline_configurations_by_type(active_pipeline_id, ConfigType.INFERENCE_MODEL)[0]

            keyword_search_dict = {
                "retriever": retriever,
                "pipeline_id": active_pipeline_id,
                "keywords": keyword_search_params.get("keywords"),
                "output_parser": keyword_search_params.get("output_parser"),
                "prompt": keyword_search_params.get("prompt"),
                "trace_details": keyword_search_params.get("trace_details"),
                "trace_api": keyword_search_params.get("trace_api"),
                "inference_model": inference_model,
                "session": keyword_search_params.get("session"),
            }

            return keyword_search(keyword_search_dict)
                
                



    def __del__(self):
        
        self.db_session.close()
