import os
from pickle import FALSE
import trace
import uuid
import warnings
from uuid import uuid4
from sqlalchemy import create_engine
from therix.core.pipeline_component import PipelineComponent
from therix.core.response import ModelResponse
from therix.db.session import get_sql_alchemy_url
from .constants import PipelineTypeMaster
from ..services.pipeline_service import PipelineService
from ..entities.models import ConfigType
import asyncio

warnings.simplefilter('always', DeprecationWarning)
engine = create_engine(get_sql_alchemy_url()) 

class Pipeline:
    def __init__(self, name, pipeline_ids=None, status="PUBLISHED"):
        if self.__class__.__name__ != 'Agent':
            warnings.warn(
                "\033[93mThe 'Pipeline' class is deprecated and will be removed in a future release. Please use the 'Agent' class instead.\033[0m",
                DeprecationWarning,
                stacklevel=2
            )
        self.pipeline_data = {"name": name, "status": status}
        self.components = []
        self.type = None
        self.pipeline_ids = pipeline_ids
        self.added_configs = set()
        self.create_trace= os.getenv("CREATE_TRACE")
        self.therix_api_key = os.getenv("THERIX_API_KEY")
        if not self.therix_api_key:
            print(
                "\033[93m🚨THERIX_API_KEY is not set. You are going to use therix-SDK services without authentication.\033[0m"
            )
        self.trace_api_key = os.getenv("TRACE_API_KEY")
        self.pipeline_service = PipelineService(therix_api_key=self.therix_api_key,trace_api_key=self.trace_api_key)

    @classmethod
    def from_id(cls, pipeline_id):
        pipeline = cls.__new__(cls)
        pipeline.__init__(None)
        pipeline.load(pipeline_id)
        return pipeline
    
    @classmethod
    def merge(cls, pipeline_ids):
        if not pipeline_ids:
            raise ValueError("No pipeline IDs provided for merging")

        merged_pipeline = cls.__new__(cls)
        merged_pipeline.__init__(None, pipeline_ids)

        for pid in pipeline_ids:
            pipeline = cls.from_id(pid)
            merged_pipeline.components.extend(pipeline.components)

        return merged_pipeline

    def validate_configuration(self, component):
        if not isinstance(component, PipelineComponent):
            raise ValueError("component must be an instance of PipelineComponent")
        config_key = component.type.value
        if config_key in self.added_configs and config_key != ConfigType.INPUT_SOURCE.value:
            raise ValueError(f"Configuration '{component.type.value}' is added multiple times.")
        self.added_configs.add(config_key)

    def set_primary(self, pipeline_id):
        self.pipeline_data = self.pipeline_service.get_pipeline(pipeline_id)
        self.id = self.pipeline_data.id
        self.name = self.pipeline_data.name
        return self.pipeline_data

    def add(self, component):
        if not isinstance(component, PipelineComponent):
            raise ValueError("component must be an instance of PipelineComponent")

        component_type_to_pipeline_type = {
            ConfigType.EMBEDDING_MODEL.value: PipelineTypeMaster.RAG.value,
            ConfigType.SUMMARIZER.value: PipelineTypeMaster.SUMMARIZER.value,
            ConfigType.DOCUMENT_INTELLIGENCE.value: PipelineTypeMaster.RAG.value,
        }

        if component.type.value in component_type_to_pipeline_type and self.type is None:
            self.type = component_type_to_pipeline_type[component.type.value]
        elif component.type.value not in component_type_to_pipeline_type:
            pass
        else:
            raise Exception(f"Cannot add {component.type.value}.")

        self.validate_configuration(component)
        self.components.append(component)
        return self

    def add_data_source(self, name, config):
        return self.add(PipelineComponent(ConfigType.INPUT_SOURCE, name, config))

    def add_embedding_model(self, name, config):
        return self.add(PipelineComponent(ConfigType.EMBEDDING_MODEL, name, config))

    def add_inference_model(self, name, config):
        return self.add(PipelineComponent(ConfigType.INFERENCE_MODEL, name, config))

    def add_output_source(self, name, config):
        return self.add(PipelineComponent(ConfigType.OUTPUT_SOURCE, name, config))

    def save(self):
        configurations_data = [
            {"config_type": component.type.value, "name": component.name, "config": component.config}
            for component in self.components
        ]

        if self.type is None:
            if any(config["config_type"] == ConfigType.INFERENCE_MODEL.value for config in configurations_data):
                self.type = PipelineTypeMaster.DEFAULT.value

        self.pipeline_data["type"] = self.type
        self.pipeline_data = self.pipeline_service.create_pipeline_with_configurations(self.pipeline_data, configurations_data)

        self.id = self.pipeline_data.id
        self.name = self.pipeline_data.name
        return self.pipeline_data

    def get_db_url(self):
        return self.pipeline_service.get_db_url()

    def get_prompt_by_name(self, prompt_name):
        return self.pipeline_service.get_prompt_by_name(prompt_name)

    def get_trace_api(self):
        return self.pipeline_service.get_trace_creds()

    def update_configuration(self, pipeline_id, component):
        if not isinstance(component, PipelineComponent):
            raise ValueError("component must be an instance of PipelineComponent")

        config_data = {"config_type": component.type.value, "name": component.name, "config": component.config}
        return self.pipeline_service.update_pipeine_configuration(pipeline_id=pipeline_id, component=config_data)

    def publish(self):
        return self.pipeline_service.publish_pipeline(self.pipeline_data)

    def load(self, pipeline_id):
        self.pipeline_data = self.pipeline_service.get_pipeline(pipeline_id)
        self.id = self.pipeline_data.id
        self.name = self.pipeline_data.name
        self.type = self.pipeline_data.type
        return self.pipeline_data

    def preprocess_data(self):
        async def run_preprocess():
            return await self.pipeline_service.preprocess_data(self.pipeline_data.id)

        return self._invoke_method(run_preprocess)
    
    def _invoke_method(self, method, *args, **kwargs):
        if asyncio.iscoroutinefunction(method):
            return asyncio.run(method(*args, **kwargs))
        else:
            return method(*args, **kwargs)

    def get_configurations(self, pipeline_id):
        inference_model = self.pipeline_service.get_pipeline_configurations_by_type(pipeline_id, ConfigType.INFERENCE_MODEL)
        pipeline_trace_config = self.pipeline_service.get_pipeline_configurations_by_type(pipeline_id, ConfigType.TRACE_DETAILS)
        saved_system_prompt = self.pipeline_service.get_pipeline_configurations_by_type(pipeline_id, ConfigType.SYSTEM_PROMPT)
        pipeline_type = self.pipeline_service.get_pipeline(pipeline_id).type
        if not self.therix_api_key:
            pipeline_type = pipeline_type.value
            
        return inference_model, pipeline_trace_config, saved_system_prompt, pipeline_type

    async def async_invoke(
        self,
        question=None,
        session_id=None,
        keyword_search_params=None,
        dynamic_system_prompt=None,
        output_parser=None,
        variables=None,
        metadata=None,
        config = None,
        top_k = None
    ):
        """
        Asynchronously invoke the pipeline for RAG, Summarizer, or Default types.

        This method is the async version of `invoke` and should be used in async contexts (e.g., FastAPI, async jobs).
        It handles all pipeline types and routes the call to the appropriate async or sync service method as needed.

        Args:
            question (str, optional): The user question or input for the pipeline.
            session_id (str, optional): The session identifier for chat/history context.
            keyword_search_params (dict, optional): Parameters for keyword search mode.
            dynamic_system_prompt (str, optional): Override for the system prompt.
            output_parser (optional): Output parser for structured responses.
            variables (dict, optional): Variables for prompt templating.
            metadata (dict, optional): Additional metadata for trace logging or context.
            config (optional): Additional config for the pipeline service.
            top_k (int, optional): Number of top results for retrieval-based pipelines.

        Returns:
            ModelResponse: The response object containing the answer and session id.
        """
        if self.therix_api_key:
            therix_api_key = self.therix_api_key
        else:
            therix_api_key = None

        def get_session(session_id):
            return {"session_id": str(uuid.uuid4()), "source": "AUTO-GENERATED"} if session_id is None else {"session_id": session_id, "source": "USER"}

        def get_system_prompt(saved_system_prompt):
            if self.therix_api_key:
                return {"system_prompt": dynamic_system_prompt} if dynamic_system_prompt else (self.pipeline_service.get_prompt_by_name(saved_system_prompt[0].config.get('system_prompt'), variables) if saved_system_prompt else None)
            return {"system_prompt": dynamic_system_prompt} if dynamic_system_prompt else (saved_system_prompt[0].config if saved_system_prompt else None)

        def handle_keyword_search(keyword_search_params, session, trace_details, top_k):
            keyword_search_params['active_pipeline_id'] = str(self.pipeline_data.id)
            keyword_search_params["pipeline_id"] = self.pipeline_data.id
            keyword_search_params["pipeline_ids"] = self.pipeline_ids
            keyword_search_params["trace_details"] = trace_details
            keyword_search_params['session'] = session
            keyword_search_params["trace_api"] = self.get_trace_api() if self.therix_api_key else None
            return self.pipeline_service.search_keywords(keyword_search_params, top_k=top_k)

        async def invoke_pipeline_method(method, *args, **kwargs):
            if method in [self.pipeline_service.invoke_pipeline, self.pipeline_service.invoke_default_pipeline]:
                kwargs.update({
                    'trace_api': True if self.therix_api_key else None,
                })
            elif method == self.pipeline_service.invoke_summarizer_pipeline:
                kwargs.update({
                    'trace_api': True if self.therix_api_key else None
                }) 
            return await method(*args, **kwargs)

        if isinstance(self.pipeline_data, dict) and 'id' not in self.pipeline_data:
            if self.pipeline_ids:
                self.set_primary(self.pipeline_ids[-1])

        if question is None and keyword_search_params is None:
            return "Please provide the required parameters to invoke the pipeline"

        session = get_session(session_id)
        inference_model, pipeline_trace_config, saved_system_prompt, pipeline_type = self.get_configurations(self.pipeline_data.id)
        pipeline_system_prompt = get_system_prompt(saved_system_prompt)
        trace_details = pipeline_trace_config[0].config if pipeline_trace_config else None

        if pipeline_type == PipelineTypeMaster.RAG.value:
            if keyword_search_params and question is None:
                answer = asyncio.run(handle_keyword_search(keyword_search_params, session, trace_details, top_k))
            else:
                output_parser_arg = {"output_parser": output_parser} if output_parser else {}
                pipeline_id = self.pipeline_data.id
                if isinstance(self.pipeline_ids, list) and len(self.pipeline_ids) > 0:
                    self.pipeline_ids.append(str(pipeline_id))
                answer = invoke_pipeline_method(self.pipeline_service.invoke_pipeline, pipeline_id, question, session, trace_details, pipeline_ids=self.pipeline_ids, **output_parser_arg, system_prompt=pipeline_system_prompt, metadata=metadata, config=config,top_k=top_k)

        elif pipeline_type == PipelineTypeMaster.SUMMARIZER.value: 
            method = self.pipeline_service.async_invoke_summarizer_pipeline
            answer = await invoke_pipeline_method(method, self.pipeline_data.id, text=question, trace_details=trace_details, session=session, system_prompt=pipeline_system_prompt, metadata=metadata, config=config)

        elif pipeline_type == PipelineTypeMaster.DEFAULT.value:
            method = self.pipeline_service.invoke_default_pipeline
            answer = await invoke_pipeline_method(method, self.pipeline_data.id, session, question=question, trace_details=trace_details, system_prompt=pipeline_system_prompt, metadata=metadata, config=config)

        return ModelResponse(answer, session.get("session_id")).create_response()

    def invoke(
        self,
        question=None,
        session_id=None,
        keyword_search_params=None,
        dynamic_system_prompt=None,
        output_parser=None,
        variables=None,
        metadata=None,
        config = None,
        top_k = None
    ):
        if self.therix_api_key:
            therix_api_key = self.therix_api_key
        else:
            therix_api_key = None

        def get_session(session_id):
            return {"session_id": str(uuid.uuid4()), "source": "AUTO-GENERATED"} if session_id is None else {"session_id": session_id, "source": "USER"}

        def get_system_prompt(saved_system_prompt):
            if self.therix_api_key:
                return {"system_prompt": dynamic_system_prompt} if dynamic_system_prompt else (self.pipeline_service.get_prompt_by_name(saved_system_prompt[0].config.get('system_prompt'), variables) if saved_system_prompt else None)
            return {"system_prompt": dynamic_system_prompt} if dynamic_system_prompt else (saved_system_prompt[0].config if saved_system_prompt else None)

        def handle_keyword_search(keyword_search_params, session, trace_details, top_k):
            keyword_search_params['active_pipeline_id'] = str(self.pipeline_data.id)
            keyword_search_params["pipeline_id"] = self.pipeline_data.id
            keyword_search_params["pipeline_ids"] = self.pipeline_ids
            keyword_search_params["trace_details"] = trace_details
            keyword_search_params['session'] = session
            keyword_search_params["trace_api"] = self.get_trace_api() if self.therix_api_key else None
            return self.pipeline_service.search_keywords(keyword_search_params, top_k=top_k)

        def invoke_pipeline_method(method, *args, **kwargs):
            if method in [self.pipeline_service.invoke_pipeline, self.pipeline_service.invoke_default_pipeline]:
                kwargs.update({
                    'trace_api': True if self.therix_api_key else None,
                })
            elif method == self.pipeline_service.invoke_summarizer_pipeline:
                kwargs.update({
                    'trace_api': True if self.therix_api_key else None
                })
            if asyncio.iscoroutinefunction(method):
                return asyncio.run(method(*args, **kwargs))
            else:
                return method(*args, **kwargs)

        if isinstance(self.pipeline_data, dict) and 'id' not in self.pipeline_data:
            if self.pipeline_ids:
                self.set_primary(self.pipeline_ids[-1])

        if question is None and keyword_search_params is None:
            return "Please provide the required parameters to invoke the pipeline"

        session = get_session(session_id)
        inference_model, pipeline_trace_config, saved_system_prompt, pipeline_type = self.get_configurations(self.pipeline_data.id)
        pipeline_system_prompt = get_system_prompt(saved_system_prompt)
        
       
        trace_details = pipeline_trace_config[0].config if pipeline_trace_config else None
       

        if pipeline_type == PipelineTypeMaster.RAG.value:
            if keyword_search_params and question is None:
                answer = asyncio.run(handle_keyword_search(keyword_search_params, session, trace_details, top_k))
            else:
                output_parser_arg = {"output_parser": output_parser} if output_parser else {}
                pipeline_id = self.pipeline_data.id
                if isinstance(self.pipeline_ids, list) and len(self.pipeline_ids) > 0:
                    self.pipeline_ids.append(str(pipeline_id))
                answer = invoke_pipeline_method(self.pipeline_service.invoke_pipeline, pipeline_id, question, session, trace_details, pipeline_ids=self.pipeline_ids, **output_parser_arg, system_prompt=pipeline_system_prompt, metadata=metadata, config=config,top_k=top_k)

        elif pipeline_type == PipelineTypeMaster.SUMMARIZER.value: 
            method = self.pipeline_service.invoke_summarizer_pipeline
            answer = invoke_pipeline_method(method, self.pipeline_data.id, text=question, trace_details=trace_details, session=session, system_prompt=pipeline_system_prompt, metadata=metadata, config=config)

        elif pipeline_type == PipelineTypeMaster.DEFAULT.value:
            method = self.pipeline_service.invoke_default_pipeline
            answer = invoke_pipeline_method(method, self.pipeline_data.id, session, question=question, trace_details=trace_details, system_prompt=pipeline_system_prompt, metadata=metadata, config=config)

        return ModelResponse(answer, session.get("session_id")).create_response()
