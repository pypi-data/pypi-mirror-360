from dotenv import load_dotenv
from groclake.datalake import Datalake
import os
load_dotenv()

class Config:
    MONGODB_CONFIG = {
            'connection_string': os.getenv('MONGODB_CONNECTION_STRING'),
            'data_base': os.getenv('MONGODB_DATABASE')
            }


class DatalakeConnection(Datalake):
    def __init__(self):
        super().__init__()
        MONGODB_CONFIG = Config.MONGODB_CONFIG
        MONGODB_CONFIG['connection_type'] = 'mongo'

        self.test_pipeline = self.create_pipeline(name="test_pipeline")
        self.test_pipeline.add_connection(name="mongodb_connection", config=MONGODB_CONFIG)
        self.execute_all()

        self.connections = {
            "mongodb_connection": self.get_connection("mongodb_connection")
        }

    def get_connection(self, connection_name):
        return self.test_pipeline.get_connection_by_name(connection_name)

datalake_connection = DatalakeConnection()
mongodb_connection = datalake_connection.connections["mongodb_connection"]

class Promptlake:
    def __init__(self):
        self.mongodb_connection = mongodb_connection

    def save_prompt(self, client_uuid, messages, m=1):
        latest_version = self.fetch_prompt(client_uuid, m, get_latest_version=True) or 0
        print("Latest Version :",latest_version)
        new_version = latest_version + 1
        print(f"New version to be inserted: {new_version}")

        prompt_id = client_uuid + ":" + str(m)
        prompt_data = {
            "prompt_id": prompt_id,
            "prompt_version": new_version,
            "model": "gpt-4",
            "messages": messages,
            "temperature": 0.7,
        }

        inserted_id = self.mongodb_connection.insert(collection_name="promptlake", data=prompt_data)
        print("Prompt inserted into Datalake MongoDB connection with the id ", inserted_id)


    def fetch_prompt(self, client_uuid, m=1, get_latest_version=False):
        prompt_id = client_uuid + ":" + str(m)
        query = {"prompt_id": prompt_id}
        print(f"Fetching prompt with query: {query}")

        results = self.mongodb_connection.read(collection_name="promptlake", query=query)
        print(f"Query results: {results}")

        if not results:
            print("No results found.")
            return None if get_latest_version else []

        if get_latest_version:
            versions = [int(doc["prompt_version"]) for doc in results]
            print(f"Extracted Versions: {versions}")
            latest_version = max(versions, default=0)
            print(f"Latest version found: {latest_version}")
            return latest_version

        print(f"Returning all fetched results.")
        return results







