from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.engine.url import URL
from alembic.config import Config
from alembic import command
import threading
import logging
import os
from dotenv import load_dotenv

from therix.entities.models import Base

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    _instance = None
    _engine = None
    _session_factory = None

    def __new__(cls):
        logger.debug("Checking instance...")
        if cls._instance is None:
            with threading.Lock():
                if cls._instance is None:
                    logger.debug("Creating new instance...")
                    cls._instance = super(DatabaseManager, cls).__new__(cls)

                    if cls._is_api_key_present():
                        logger.info("THERIX_API_KEY is present. Skipping database operations.")
                    elif cls._are_db_env_vars_present():
                        cls._engine = cls._create_engine()
                        cls._session_factory = sessionmaker(
                            bind=cls._engine, autoflush=False, autocommit=False
                        )
                        cls._setup_database()
                    else:
                        pass
        return cls._instance

    @classmethod
    def get_session(cls):
        if cls._session_factory is None:
            raise Exception("DatabaseManager is not initialized properly.")
        return scoped_session(cls._session_factory)

    @classmethod
    def _create_engine(cls):
        db_url = cls._construct_db_url()
        return create_engine(db_url, pool_size=10,           # Number of connections to keep in the pool (default: 5)
            max_overflow=5,         # Number of connections allowed in overflow (default: 10)
            pool_timeout=30, 
            pool_recycle=0,       # Recycle connections after a specified number of seconds (optional)
            pool_pre_ping=True )

    @classmethod
    def _construct_db_url(cls):
        drivername = os.getenv("THERIX_DB_TYPE", "postgresql")
        username = os.getenv("THERIX_DB_USERNAME")
        password = os.getenv("THERIX_DB_PASSWORD")
        host = os.getenv("THERIX_DB_HOST")
        port = os.getenv("THERIX_DB_PORT")
        db_name = os.getenv("THERIX_DB_NAME")
        return URL.create(
            drivername=drivername,
            username=username,
            password=password,
            host=host,
            port=port,
            database=db_name,
        ).render_as_string(hide_password=False)

    @staticmethod
    def _setup_database():
        if DatabaseManager._engine:
            Base.metadata.create_all(DatabaseManager._engine)
            logger.info("Database tables created.")

            alembic_cfg = DatabaseManager._get_alembic_config()
            DatabaseManager._upgrade_database(alembic_cfg)

    @staticmethod
    def _get_alembic_config():
        base_dir = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
        alembic_config_path = os.path.join(base_dir, "therix/alembic.ini")
        alembic_cfg = Config(alembic_config_path)
        alembic_cfg.set_main_option(
            "script_location", os.path.join(base_dir, "therix/alembic")
        )
        alembic_cfg.set_main_option(
            "sqlalchemy.url", str(DatabaseManager._construct_db_url())
        )
        return alembic_cfg

    @staticmethod
    def _upgrade_database(alembic_cfg):
        try:
            if alembic_cfg:
                # command.upgrade(alembic_cfg, "head")
                # logger.info("Database upgraded successfully.")
                pass
        except Exception as e:
            logger.error(f"An error occurred while upgrading the database: {e}")
            raise

    @staticmethod
    def _is_api_key_present():
        
        return bool(os.getenv("THERIX_API_KEY"))

    @staticmethod
    def _are_db_env_vars_present():
        required_vars = [
            "THERIX_DB_USERNAME",
            "THERIX_DB_PASSWORD",
            "THERIX_DB_HOST",
            "THERIX_DB_PORT",
            "THERIX_DB_NAME"
        ]
        for var in required_vars:
            if not os.getenv(var):
                return False
        return True