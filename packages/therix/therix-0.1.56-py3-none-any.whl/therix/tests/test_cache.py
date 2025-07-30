import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from therix.core.cache import TherixCache, FulltextLLMCache
from therix.db.session import get_sql_alchemy_url


class TestTherixCache(unittest.TestCase):
    def setUp(self):
        # Create an in-memory SQLite database for testing
        self.engine = create_engine(get_sql_alchemy_url())
        # Create tables
        FulltextLLMCache.metadata.create_all(self.engine)
        # Create a session
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

        # Create an instance of TherixCache
        self.cache = TherixCache(self.engine)

    def tearDown(self):
        # Clean up - close the session and dispose the engine
        self.session.close()
        self.engine.dispose()

    def test_update_and_lookup(self):
        # Test updating cache and looking up for a prompt
        prompt = "Test prompt"
        llm_string = "Test LLM"
        answer = "Test answer"
        pipeline_id = "6f3d36d3-2c43-4d07-b07a-3f3e454f5e01"
        self.cache.update(prompt, llm_string, answer, pipeline_id)
        result = self.cache.lookup(prompt, llm_string, pipeline_id)
        self.assertEqual(result.response, answer)

    def test_invalid_pipeline_id(self):
        # Test updating cache with invalid pipeline ID
        prompt = "Test prompt"
        llm_string = "Test LLM"
        answer = "Test answer"
        invalid_pipeline_id = "invalid_id"
        with self.assertRaises(ValueError):
            self.cache.update(prompt, llm_string, answer, invalid_pipeline_id)

    def test_clear_cache(self):
        # Test clearing cache
        prompt = "Test prompt"
        llm_string = "Test LLM"
        answer = "Test answer"
        pipeline_id = "6f3d36d3-2c43-4d07-b07a-3f3e454f5e01"
        self.cache.update(prompt, llm_string, answer, pipeline_id)
        self.cache.clear()
        result = self.cache.lookup(prompt, llm_string, pipeline_id)   
        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()