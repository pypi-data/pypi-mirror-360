import os
import random
import string
from datetime import datetime
import json
import pytz
from groclake.datalake import Datalake
from dotenv import load_dotenv

thresholdlake_mapping = {
    "properties": {
        "query_text": {"type": "text"},
        "intent": {"type": "keyword"},
        "entities": {
            "type": "nested",
            "properties": {
                "metric_type": {"type": "keyword"},
                "metric_name": {"type": "keyword"},
                "threshold_value": {"type": "float"},
                "threshold_unit": {"type": "keyword"},
                "threshold_severity": {"type": "keyword"},
                "threshold_condition": {"type": "keyword"}
            }
        },
        "metadata": {
            "properties": {
                "thresholdlake_id": {"type": "keyword"},
                "thresholdlake_name": {"type": "text"},
                "ai_thresholdlake_description": {"type": "text"},
                "thresholdlake_created_time": {"type": "date"},
                "thresholdlake_updated_time": {"type": "date"}
            }
        }
    }
}

load_dotenv()

class Config:
    ES_CONFIG = {
        "host": os.getenv("ES_HOST"),
        "port": int(os.getenv("ES_PORT")),
        "api_key": os.getenv("ES_API_KEY"),
        "schema": os.getenv("ES_SCHEMA")
    }

    MYSQL_CONFIG = {
        'user': os.getenv('MYSQL_USER'),
        'passwd': os.getenv('MYSQL_PASSWORD'),
        'host': os.getenv('MYSQL_HOST'),
        'port': int(os.getenv('MYSQL_PORT')),
        'db': os.getenv('MYSQL_DB_2'),
        'charset': 'utf8'
    }

class DatalakeConnection(Datalake):
    def __init__(self):
        super().__init__()

        ES_CONFIG = Config.ES_CONFIG
        ES_CONFIG['connection_type'] = 'es'

        MYSQL_CONFIG = Config.MYSQL_CONFIG
        MYSQL_CONFIG['connection_type'] = 'sql'

        self.plotch_pipeline = self.create_pipeline(name="groclake_pipeline")
        self.plotch_pipeline.add_connection(name="es_connection", config=ES_CONFIG)
        self.plotch_pipeline.add_connection(name="sql_connection", config=MYSQL_CONFIG)

        self.execute_all()

        self.connections = {
            "es_connection": self.get_connection("es_connection"),
            "sql_connection": self.get_connection("sql_connection")
        }

    def get_connection(self, connection_name):
        return self.plotch_pipeline.get_connection_by_name(connection_name)

datalake_connection = DatalakeConnection()
es_connection = datalake_connection.connections["es_connection"]
mysql_connection = datalake_connection.connections["sql_connection"]

class ThresholdLake:
    def __init__(self, index_uuid=None):
        if not index_uuid:
            raise ValueError('Missing required index_uuid. Ensure you pass a valid index UUID when initializing the class.')
        self.index_uuid = index_uuid

    def generate_unique_id(self, length=16):
        characters = string.ascii_lowercase + string.digits
        unique_id = ''.join(random.choices(characters, k=length))
        return unique_id

    def get_current_datetime(self) -> str:
        return datetime.now(pytz.timezone('Asia/Kolkata')).strftime("%Y-%m-%d %H:%M:%S")

    def get_existing_index_uuid(self, index_uuid, entity_type):
        condition_clause = "entity_id = %s AND entity_type= %s"
        query = f"SELECT * FROM groclake_entity_master WHERE {condition_clause}"
        params = (index_uuid, entity_type)
        result = mysql_connection.read(query, params, multiple=False)
        return result

    def save_thresholdlake_data_in_db(self, db_params: dict, table_name: str, commit=True) -> int:
        query = "insert into " + table_name + " (" + ",".join(db_params.keys()) + ") VALUES (" + ",".join(['%s' for x in db_params.values()]) + ")"
        return mysql_connection.write(query, tuple(db_params.values()))

    def create(self, thresholdlake_name=None):
        if not thresholdlake_name:
            return {"message": "ThresholdLake name is required. Please provide a valid name"}
        if not thresholdlake_name.lower().strip().isidentifier():
            return {'error': f'Invalid ThresholdLake name. Only alphanumeric characters and underscores are allowed.'}

        index_uuid = f"th_{self.index_uuid}"

        existing_data = self.get_existing_index_uuid(index_uuid, 'thresholdlake')
        if existing_data and existing_data.get('entity_id', ''):
            self.index_uuid = existing_data.get('entity_id', '')
            return {
                "message": "An entry with the same index_uuid already exists.",
                "index_uuid": existing_data.get('entity_id', ''),
                "thresholdlake_name": existing_data.get('name', '')
            }

        db_params = {
            "entity_id": index_uuid,
            "entity_type": 'thresholdlake',
            "created_at": self.get_current_datetime(),
            "groc_account_id": '',
            "name": thresholdlake_name
        }

        try:
            response = es_connection.create_index(index_uuid, settings=None, mappings=thresholdlake_mapping)
            self.index_uuid = index_uuid
            try:
                self.save_thresholdlake_data_in_db(db_params, 'groclake_entity_master')
            except Exception as db_error:
                return {"message": "Database error occurred while saving thresholdlake.", "error": str(db_error)}

            return {
                "message": "ThresholdLake created successfully",
                "index_uuid": index_uuid,
                "thresholdlake_name": thresholdlake_name
            }
        except Exception as e:
            return {"message": "Error creating index", "error": str(e)}

    def push(self, thresholdlake_data):
        try:
            if not isinstance(thresholdlake_data, dict):
                return {"error": "Invalid thresholdlake data format. Expected dictionary."}

            if not self.index_uuid:
                raise ValueError("Invalid index: thresholdlake_id is missing.")

            if "metadata" in thresholdlake_data and isinstance(thresholdlake_data["metadata"], dict):
                metadata = thresholdlake_data["metadata"]
                for time_key in ["thresholdlake_created_time", "thresholdlake_updated_time"]:
                    if time_key in metadata:
                        metadata[time_key] = datetime.strptime(
                            metadata[time_key], "%Y-%m-%dT%H:%M:%SZ"
                        ).strftime("%Y-%m-%dT%H:%M:%S")

            try:
                write_response = es_connection.write(query={'index': self.index_uuid, 'body': thresholdlake_data})
                return {"message": "thresholdlake data pushed successfully", "response": write_response}
            except Exception as e:
                return {"error": "Failed to push data to Elasticsearch", "details": str(e)}

        except Exception as e:
            return {"error": "An unexpected error occurred", "details": str(e)}

    def fetch(self, payload):
        try:
            read_response = es_connection.search(index=self.index_uuid, body=payload)
            return read_response
        except Exception as e:
            return {"error": "Failed to retrieve search results", "details": str(e)}

    def delete(self, index=None, query=None):
        try:
            if not self.index_uuid:
                raise ValueError("Invalid index: thresholdlake_id is missing.")

            if index:
                es_response = es_connection.delete_index(index=index)
                query = "UPDATE groclake_entity_master SET status = %s WHERE entity_id = %s AND entity_type = %s"
                params = (2, index, 'thresholdlake')
                mysql_connection.write(query, params)

                return {"message": "thresholdlake deleted successfully"}
            elif query:
                delete_response = es_connection.delete_by_query(index=self.index_uuid, body=query)
                return {"message": "Documents deleted successfully", "response": delete_response}
            else:
                return {"error": "Either index or query must be provided for deletion"}

        except Exception as e:
            return {"error": "Failed to delete thresholdlake", "details": str(e)}
