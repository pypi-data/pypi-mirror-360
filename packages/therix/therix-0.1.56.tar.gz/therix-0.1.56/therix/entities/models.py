import enum
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from sqlalchemy.orm import DeclarativeBase
import sqlalchemy as sa

from therix.core.constants import PipelineTypeMaster


# Creating a base class
class Base(DeclarativeBase):
    pass


class ConfigType(enum.Enum):
    INPUT_SOURCE = "INPUT_SOURCE"
    EMBEDDING_MODEL = "EMBEDDING_MODEL"
    INFERENCE_MODEL = "INFERENCE_MODEL"
    OUTPUT_SOURCE = "OUTPUT_SOURCE"
    TRACE_DETAILS = "TRACE_DETAILS"
    PII_FILTER = "PII_FILTER"
    SUMMARIZER = "SUMMARIZER"
    CACHE_CONFIG = "CACHE_CONFIG"
    SYSTEM_PROMPT = 'SYSTEM_PROMPT'
    DOCUMENT_INTELLIGENCE = "DOCUMENT_INTELLIGENCE"


class Pipeline(Base):
    __tablename__ = "pipelines"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    name = Column(String, nullable=False)
    type = Column(
        sa.Enum(PipelineTypeMaster)
    )
    status = Column(String, default="IN_DRAFT")  # Adjust default value as needed
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime, nullable=True)
    custom_data = Column(JSON, default=dict)

    configurations = relationship("PipelineConfiguration", back_populates="pipeline")
    chat_history = relationship("ChatHistory", back_populates="pipeline")


class PipelineConfiguration(Base):
    __tablename__ = "pipeline_configurations"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    pipeline_id = Column(UUID(as_uuid=True), ForeignKey("pipelines.id"))
    config_type = Column(
        sa.Enum(ConfigType, name="configtype", create_constraint=True), nullable=False
    )
    name = Column(String, nullable=False)
    config = Column(JSON, default=dict)
    custom_data = Column(JSON, default=dict)
    pipeline = relationship("Pipeline", back_populates="configurations")


class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    message = Column(String, nullable=False)
    message_role=Column(String, nullable=False)
    pipeline_id = Column(UUID(as_uuid=True), ForeignKey("pipelines.id"))
    pipeline = relationship("Pipeline", back_populates="chat_history")
    session_id = Column(UUID(as_uuid=True), default=uuid.uuid4, nullable=False)
