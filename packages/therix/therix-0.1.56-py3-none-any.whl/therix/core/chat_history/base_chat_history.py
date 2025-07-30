import uuid
import psycopg
import logging
from langchain_postgres import PostgresChatMessageHistory
import os
import aiohttp

logger = logging.getLogger(__name__)

class TherixChatMessageHistory(PostgresChatMessageHistory):
    def __init__(
        self,
        session_id,
        pipeline_id,
        engine=None,
        table_name=None,
        api_url=None,
    ):
        self.session_id = session_id
        self.pipeline_id = pipeline_id
        self.engine = engine
        self.table_name = table_name
        self.api_url = api_url

        if self.engine:
            self.sync_connection = psycopg.connect(engine)
            super().__init__(table_name, session_id, sync_connection=self.sync_connection)
        else:
            self.sync_connection = None
            self.therix_api_key = os.getenv('THERIX_API_KEY')

    def add_message(self, message_role, message, pipeline_id, session_id):
        try:
            id = uuid.uuid4()
            cursor = self.sync_connection.cursor()
            insert_query = f"""INSERT INTO {self.table_name} (id, message_role, message, pipeline_id, session_id) VALUES (%s, %s, %s, %s, %s);"""
            cursor.execute(insert_query, (id, message_role, message, pipeline_id, session_id))
            self.sync_connection.commit()
            cursor.close()
        except (Exception, psycopg.DatabaseError) as e:
            logging.error(e)

    async def async_add_message(self, message_role, message, pipeline_id, session_id):
        try:
            payload = {
                "message_role": message_role,
                "message": message,
                "pipeline_id": pipeline_id,
                "session_id": session_id
            }
            headers = {
                "THERIX_API_KEY": self.therix_api_key,
                "Content-Type": "application/json"
            }
            async with aiohttp.ClientSession() as session:
                async with session.post(self.api_url, json=payload, headers=headers) as response:
                    response.raise_for_status()
        except aiohttp.ClientError as e:
            logging.error(e)

    def get_message_history(self, session_id):
        try:
            cursor = self.sync_connection.cursor()
            get_query = f"""SELECT message, message_role FROM {self.table_name} WHERE session_id = %s"""
            cursor.execute(get_query, (session_id,))
            columns = list(cursor.description)
            messages = cursor.fetchall()
            cursor.close()

            results = []
            for row in messages:
                row_dict = {}
                for i, col in enumerate(columns):
                    row_dict[col.name] = row[i]
                results.append(row_dict)
            return results
        except (Exception, psycopg.DatabaseError) as e:
            logging.error(e)

    async def async_get_message_history(self, session_id):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.api_url, params={"session_id": session_id}, headers={"THERIX_API_KEY": self.therix_api_key, "Content-Type": "application/json"}) as response:
                    response.raise_for_status()
                    return await response.json()
        except aiohttp.ClientError as e:
            logging.error(e)
            return None

