import os
import random
import string
from datetime import datetime
import pytz
from dotenv import load_dotenv
from groclake.datalake import Datalake

# Provided issuelake mapping
issuelake_mapping = {
    "properties": {
        "query_text": {"type": "text"},
        "intent": {"type": "keyword"},
        "entities": {
            "type": "nested",
            "properties": {
                "issue_entity_type": {"type": "keyword"},
                "impacted_endpoint": {"type": "text"},
                "monitor_time_duration": {"type": "keyword"},
                "monitor_data_type": {"type": "keyword"},
                "timestamp": {"type": "date"},
                "observed_value": {"type": "float"},
                "deviation_amount": {"type": "float"},
                "deviation_percentage": {"type": "float"},
                "deviation_severity": {"type": "keyword"},
                "deviation_condition": {"type": "keyword"},
                "deviation_created_time": {"type": "date"},
                "monitor_metric": {
                    "type": "nested",
                    "properties": {
                        "metric_name": {"type": "keyword"},
                        "metric_entities": {"type": "keyword"}
                    }
                }
            }
        },
        "metadata": {
            "properties": {
                "issuelake_id": {"type": "keyword"},
                "issue_name": {"type": "text"},
                "issue_description": {"type": "text"},
                "issue_created_time": {"type": "date"},
                "issue_updated_time": {"type": "date"},
                "related_monitor_id": {"type": "keyword"},
                "graph_relationship": {
                    "properties": {
                        "relationship_type": {"type": "keyword"},
                        "monitor_id": {"type": "keyword"}
                    }
                },
                "cascaded_intent": {
                    "type": "nested",
                    "properties": {
                        "agent_id": {"type": "keyword"},
                        "agent_intent": {"type": "keyword"},
                        "sequence_id": {"type": "keyword"}
                    }
                }
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
        'db': os.getenv('MYSQL_DB_3'),
        'charset': 'utf8'
    }

class DatalakeConnection(Datalake):
    def __init__(self):
        super().__init__()
        ES_CONFIG = Config.ES_CONFIG
        ES_CONFIG['connection_type'] = 'es'
        MYSQL_CONFIG = Config.MYSQL_CONFIG
        MYSQL_CONFIG['connection_type'] = 'sql'
        self.pipeline = self.create_pipeline(name="groclake_pipeline")
        self.pipeline.add_connection(name="es_connection", config=ES_CONFIG)
        self.pipeline.add_connection(name="sql_connection", config=MYSQL_CONFIG)
        self.execute_all()
        self.connections = {
            "es_connection": self.get_connection("es_connection"),
            "sql_connection": self.get_connection("sql_connection")
        }
    def get_connection(self, connection_name):
        return self.pipeline.get_connection_by_name(connection_name)

datalake_connection = DatalakeConnection()
es_connection = datalake_connection.connections["es_connection"]
mysql_connection = datalake_connection.connections["sql_connection"]

class IssueLake:
    def __init__(self, index_uuid=None):
        if not index_uuid:
            raise ValueError('Missing required index_uuid.')
        self.index_uuid = index_uuid

    def generate_unique_id(self, length=16):
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

    def get_current_datetime(self):
        return datetime.now(pytz.timezone('Asia/Kolkata')).strftime("%Y-%m-%d %H:%M:%S")

    def get_existing_index_uuid(self, index_uuid, entity_type='issuelake'):
        query = "SELECT * FROM groclake_entity_master WHERE entity_id = %s AND entity_type = %s"
        params = (index_uuid, entity_type)
        return mysql_connection.read(query, params, multiple=False)

    def save_issuelake_data_in_db(self, db_params, table_name='groclake_entity_master'):
        query = f"INSERT INTO {table_name} ({','.join(db_params.keys())}) VALUES ({','.join(['%s'] * len(db_params.values()))})"
        return mysql_connection.write(query, tuple(db_params.values()))

    def create(self, issuelake_name=None):
        if not issuelake_name:
            return {"message": "IssueLake name is required."}
        if not issuelake_name.lower().strip().isidentifier():
            return {"error": "Invalid IssueLake name. Only alphanumeric characters and underscores allowed."}

        index_uuid = f"is_{self.index_uuid}"
        existing = self.get_existing_index_uuid(index_uuid)
        if existing:
            self.index_uuid = existing.get('entity_id', '')
            return {
                "message": "An entry with the same index_uuid already exists.",
                "index_uuid": existing.get('entity_id', ''),
                "issuelake_name": existing.get('name', '')
            }

        db_params = {
            "entity_id": index_uuid,
            "entity_type": "issuelake",
            "created_at": self.get_current_datetime(),
            "groc_account_id": "",
            "name": issuelake_name
        }

        try:
            es_connection.create_index(index_uuid, settings=None, mappings=issuelake_mapping)
            self.save_issuelake_data_in_db(db_params)
            self.index_uuid = index_uuid
            return {
                "message": "IssueLake created successfully",
                "index_uuid": index_uuid,
                "issuelake_name": issuelake_name
            }
        except Exception as e:
            return {"message": "Error creating IssueLake", "error": str(e)}

    def push(self, issuelake_data):
        try:
            if not isinstance(issuelake_data, dict):
                return {"error": "Invalid issuelake data format. Expected dictionary."}
            if not self.index_uuid:
                raise ValueError("Invalid index_uuid.")

            response = es_connection.write(query={'index': self.index_uuid, 'body': issuelake_data})
            return {"message": "IssueLake data pushed successfully", "response": response}
        except Exception as e:
            return {"error": "An unexpected error occurred", "details": str(e)}

    def fetch(self, payload):
        try:
            return es_connection.search(index=self.index_uuid, body=payload)
        except Exception as e:
            return {"error": "Failed to retrieve results", "details": str(e)}

    def delete(self, index=None, query=None):
        try:
            if not self.index_uuid:
                raise ValueError("Invalid index_uuid.")

            if index:
                es_connection.delete_index(index=index)
                mysql_connection.write(
                    "UPDATE groclake_entity_master SET status = %s WHERE entity_id = %s AND entity_type = %s",
                    (2, index, 'issuelake')
                )
                return {"message": "IssueLake index deleted successfully."}
            elif query:
                delete_response = es_connection.delete_by_query(index=self.index_uuid, body=query)
                return {"message": "Documents deleted successfully.", "response": delete_response}
            else:
                return {"error": "Either index or query must be provided."}
        except Exception as e:
            return {"error": "Failed to delete IssueLake", "details": str(e)}
