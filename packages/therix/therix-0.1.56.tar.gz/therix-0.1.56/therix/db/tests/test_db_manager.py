import pytest
from unittest.mock import patch, MagicMock
from sqlalchemy.engine.url import URL
from therix.db.db_manager import DatabaseManager


class TestDatabaseManager:
    @patch("therix.db.db_manager.DatabaseManager._create_engine")
    @patch("therix.db.db_manager.DatabaseManager._setup_database")
    def test_singleton_pattern(self, mock_setup, mock_engine):
        # Test to ensure that the DatabaseManager is a singleton
        db_manager1 = DatabaseManager()
        db_manager2 = DatabaseManager()
        assert db_manager1 is db_manager2

    @patch("therix.db.db_manager.create_engine")
    def test_create_engine_called_with_correct_url(self, mock_engine):
        # Environment setup for testing
        with patch.dict(
            "os.environ",
            {
                "THERIX_DB_TYPE": "postgresql",
                "THERIX_DB_USERNAME": "user",
                "THERIX_DB_PASSWORD": "pass",
                "THERIX_DB_HOST": "localhost",
                "THERIX_DB_PORT": "5432",
                "THERIX_DB_NAME": "testdb",
            },
        ):
            DatabaseManager._create_engine()
            mock_engine.assert_called_once_with(
                URL.create(
                    drivername="postgresql",
                    username="user",
                    password="pass",
                    host="localhost",
                    port="5432",
                    database="testdb",
                )
            )

    @patch("therix.db.db_manager.scoped_session")
    def test_get_session_raises_exception_if_not_initialized(self, mock_scoped_session):
        # Resetting class variables to test initialization failure
        DatabaseManager._session_factory = None
        with pytest.raises(Exception) as excinfo:
            DatabaseManager.get_session()
        assert "DatabaseManager is not initialized properly." in str(excinfo.value)
