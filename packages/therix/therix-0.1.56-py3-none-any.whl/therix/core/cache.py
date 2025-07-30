import uuid
from sqlalchemy.ext.declarative import declarative_base
from therix.core.pipeline_component import PipelineComponent
from therix.entities.models import ConfigType
import logging
from sqlalchemy.dialects.postgresql import UUID
from therix.db.db_manager import DatabaseManager
from typing import Type
from sqlalchemy.engine.base import Engine
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Session
from typing import (
    Any,
    Type
)



logger = logging.getLogger(__file__)

Base = declarative_base()


db_manager = DatabaseManager()


class CacheConfig(PipelineComponent):
    def __init__(self, config):
        super().__init__(ConfigType.CACHE_CONFIG, 'CACHE_CONFIG', config)       


class FulltextLLMCache(Base): 
    """Postgres table for fulltext-indexed LLM Cache"""

    __tablename__ = "llm_cache_fulltext"
    id = Column(Integer, primary_key=True)
    pipeline_id = Column(UUID(as_uuid=True), nullable=False)
    question = Column(String, nullable=False)
    llm = Column(String, nullable=True)
    response = Column(String)


class TherixCache():


    def __init__(self, engine: Engine, cache_schema: Type[FulltextLLMCache] = FulltextLLMCache):
        self.engine = engine
        self.cache_schema = cache_schema
        self.cache_schema.metadata.create_all(self.engine)


    def lookup(self, question: str, llm_string: str, pipeline_id):
        if not isinstance(pipeline_id, uuid.UUID):
            try:
                pipeline_id = uuid.UUID(pipeline_id)
            except ValueError:
                raise ValueError("pipeline_id is not a valid UUID")
        session = db_manager.get_session()
        query = session.query(FulltextLLMCache).filter(
            FulltextLLMCache.question == question,
            FulltextLLMCache.pipeline_id == pipeline_id
        )
        result = query.first()
        session.close()
        return result
        
    
    
    def update(self, prompt: str, llm_string: str, answer, pipeline_id) -> None:

        if not isinstance(pipeline_id, uuid.UUID):
            try:
                pipeline_id = uuid.UUID(pipeline_id)
            except ValueError:
                raise ValueError("pipeline_id is not a valid UUID")
        session = db_manager.get_session()
        cache_entry = FulltextLLMCache(
            question=prompt,
            llm=llm_string,
            response=answer,
            pipeline_id=pipeline_id
        )
        session.add(cache_entry)
        session.commit()
        session.close()

    def clear(self, **kwargs: Any) -> None:
        """Clear cache."""
        with Session(self.engine) as session:
            session.query(self.cache_schema).delete()
            session.commit()
    
