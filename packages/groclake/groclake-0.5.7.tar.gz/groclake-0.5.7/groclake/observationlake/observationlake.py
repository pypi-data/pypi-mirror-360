import os
import random
import string
from datetime import datetime
import json
import pytz

from groclake.datalake import Datalake
from dotenv import load_dotenv

observationlake_mapping = {

  "properties": {
    "query_text": {"type": "text"},
    "intent": {"type": "keyword"},
    "entities": {
      "type": "nested",
      "properties": {
        "http.server.status_code": {
          "type": "keyword"
        },
        "http.server.request": {
          "type": "keyword"
        },
        "http.server.latency": {
          "type": "keyword"
        },
        "http.server.status_code_hourly": {
          "type": "keyword"
        },
        "http.server.request_hourly": {
          "type": "keyword"
        },
        "http.server.latency_hourly": {
          "type": "keyword"
        },
        "observation_time": {
          "type": "date",
          "format": "strict_date_optional_time||epoch_millis"
        },
        "observation_value": {
          "type": "double"
        }
      }
    },
    "metadata": {
      "properties": {
        "observation_id": {"type": "keyword"},
        "observation_created_time": {"type": "date"},
        "observation_updated_time": {"type": "date"},
        "service.name": {
          "type": "keyword"
        },
        "service.instance.id": {
          "type": "keyword"
        },
        "monitor_id": {"type": "keyword"},
        "monitor_apm_tool": {"type": "keyword"},
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

# {
#
#   "properties": {
#     "query_text": { "type": "text" },
#     "intent": { "type": "keyword" },
#     "entities": {
#       "type": "nested",
#       "properties": {
#         "monitor_entity_type": { "type": "keyword" },
#         "monitor_entity_request_uri": { "type": "keyword" },
#         "monitor_time_duration": { "type": "keyword" },
#         "monitor_metric_type": { "type": "keyword" },
#         "monitor_data_type": { "type": "keyword" },
#         "metric_name": { "type": "keyword" },
#         "metric_value": { "type": "keyword" },
#         "metric_units": { "type": "keyword" },
#         "metric_details": {
#           "properties": {
#             "status_code": { "type": "keyword" },
#             "method": { "type": "keyword" }
#           }
#         },
#         "timestamp": { "type": "date" }
#       }
#     },
#     "metadata": {
#       "properties": {
#         "observation_id": { "type": "keyword" },
#         "observation_run_time": { "type": "date" },
#         "observation_name": { "type": "text", "fields": { "keyword": { "type": "keyword", "ignore_above": 256 } } },
#         "monitor_id": { "type": "keyword" },
#         "observation_created_time": { "type": "date" },
#         "observation_updated_time": { "type": "date" },
#         "monitor_apm_tool": { "type": "keyword" }
#       }
#     }
#   }
# }


load_dotenv()


class Config:
    # ES Configuration

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
        'db': os.getenv('MYSQL_DB'),
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
        """
        Returns a connection by name from the pipeline.
        """
        return self.plotch_pipeline.get_connection_by_name(connection_name)


datalake_connection = DatalakeConnection()
es_connection = datalake_connection.connections["es_connection"]
mysql_connection = datalake_connection.connections["sql_connection"]


class Observationlake:
    def __init__(self, index_uuid=None):
        if not index_uuid:
            raise ValueError(
                'Missing required index_uuid. Ensure you pass a valid index UUID when initializing the class.')
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

    def save_observationlake_data_in_db(self, db_params: dict, table_name: str, commit=True) -> int:
        query = "insert into " + table_name + " (" + ",".join(db_params.keys()) + ") VALUES (" + ",".join(
            ['%s' for x in db_params.values()]) + ")"
        if commit:
            return mysql_connection.write(query, tuple(db_params.values()))
        else:
            return mysql_connection.write(query, tuple(db_params.values()))

    def create(self, observationlake_name=None):
        if not observationlake_name:
            return {"message": "observationlake name is required. Please provide a valid name"}
        if not observationlake_name.lower().strip().isidentifier():
            return {'error': f'Invalid observationlakename. Only alphanumeric characters and underscores are allowed.'}

        index_uuid = f"ob_{self.index_uuid}"
        if not index_uuid:
            index_uuid = self.generate_unique_id()

        existing_data = self.get_existing_index_uuid(index_uuid, 'observationlake')
        if existing_data and existing_data.get('entity_id', ''):
            self.index_uuid = existing_data.get('entity_id', '')
            #print("esisting index", self.index_uuid)
            return {
                "message": "An entry with the same index_uuid already exists.",
                "index_uuid": existing_data.get('entity_id', ''),
                "observationlake_name": existing_data.get('name', '')
            }

        db_params = {
            "entity_id": index_uuid,
            "entity_type": 'observationlake',
            "created_at": self.get_current_datetime(),
            "groc_account_id": '',
            "name": observationlake_name
        }

        # try:
        response = es_connection.create_index(index_uuid, settings=None, mappings=observationlake_mapping)
        self.index_uuid = index_uuid
        try:
            self.save_observationlake_data_in_db(db_params, 'groclake_entity_master')
        except Exception as db_error:
            return {"message": "Database error occurred while saving observationlake.", "error": str(db_error)}
        #print("index in craete", self.index_uuid)
        return {
            "message": "observationlake created successfully",
            "index_uuid": index_uuid,
            "observationlake_name": observationlake_name
        }

    def push(self, observation_data):
        try:
            if not isinstance(observation_data, dict):
                return {"error": "Invalid observation data format. Expected dictionary."}
            #print("index in push", self.index_uuid)

            if not self.index_uuid:
                raise ValueError("Invalid index: observation_id is missing.")

            # Get the next sequential observation ID
            try:
                # Query to get the highest current observation_id
                query = {
                    "size": 1,
                    "sort": [{"metadata.observation_id": {"order": "desc"}}],
                    "_source": ["metadata.observation_id"]
                }

                existing_records = es_connection.search(index=self.index_uuid, body=query)
                last_id = 0

                if existing_records and "hits" in existing_records and "hits" in existing_records["hits"] and \
                        existing_records["hits"]["hits"]:
                    hit = existing_records["hits"]["hits"][0]
                    if "_source" in hit and "metadata" in hit["_source"] and "observation_id" in hit["_source"][
                        "metadata"]:
                        try:
                            last_id = int(hit["_source"]["metadata"]["observation_id"])
                        except (ValueError, TypeError):
                            # If conversion fails, start from 0
                            pass

                # Increment the ID
                next_id = last_id + 1
                observation_id = str(next_id)  # Simple sequential number without prefix

            except Exception as e:
                # If search fails, default to ID 1
                observation_id = "1"
                #print(f"Error fetching last ID: {str(e)}, using default ID: {observation_id}")

            # Ensure metadata exists
            if "metadata" not in observation_data:
                observation_data["metadata"] = {}

            # Add observation ID and timestamps to metadata
            current_time = datetime.now(pytz.timezone('Asia/Kolkata')).strftime("%Y-%m-%dT%H:%M:%SZ")
            observation_data["metadata"]["observation_id"] = observation_id

            # Add timestamps if they don't exist
            if "observation_created_time" not in observation_data["metadata"]:
                observation_data["metadata"]["observation_created_time"] = current_time
            if "observation_updated_time" not in observation_data["metadata"]:
                observation_data["metadata"]["observation_updated_time"] = current_time

            index = self.index_uuid
            #print("index", index)

            try:
                write_response = es_connection.write(query={'index': index, 'body': observation_data})
                return {
                    "message": "observation data pushed successfully",
                    "observation_id": observation_id
                }
            except Exception as e:
                return {"error": "Failed to push data to Elasticsearch", "details": str(e)}

        except Exception as e:
            return {"error": "An unexpected error occurred", "details": str(e)}

    def fetch(self, index, payload):
        try:
            read_response = es_connection.search(index=index, body=payload)
            return read_response
        except Exception as e:
            return {"error": "Failed to retrieve search results", "details": str(e)}

    def delete(self, index):

        try:
            # Delete the index from Elasticsearch
            es_response = es_connection.delete_index(index=index)

            # Soft delete in database
            status = 2  # Status code for soft delete
            query = "UPDATE groclake_entity_master SET status = %s WHERE entity_id = %s AND entity_type = %s"
            params = (status, index, 'observationlake')
            db_response = mysql_connection.write(query, params)

            return {
                "message": "observationlake deleted successfully",

            }

        except Exception as e:
            return {"error": "Failed to delete observationlake", "details": str(e)}









