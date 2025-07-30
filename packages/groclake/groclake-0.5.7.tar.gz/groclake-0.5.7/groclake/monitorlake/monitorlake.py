import os
import random
import string
from datetime import datetime
import json
import pytz

from groclake.datalake import Datalake

from dotenv import load_dotenv

monitorlake_mapping = {

    "properties": {
      "query_text": { "type": "text" },
      "intent": { "type": "keyword" },

      "entities": {
        "type": "nested",
        "properties": {
          "monitor_entity_type": { "type": "keyword" },
          "monitor_entity_request_uri": { "type": "keyword" },
          "monitor_time_duration": { "type": "keyword" },
          "monitor_data_type": { "type": "keyword" },
          "timestamp": { "type": "date" },
          "monitor_metric": {
            "type": "nested",
            "properties": {
              "metric_aggregation_type": { "type": "keyword" },
              "metric_data_format": { "type": "keyword" },
              "metric_data_value_field_type": { "type": "keyword" },
              "metric_entities": { "type": "keyword" },
              "metric_name": { "type": "keyword" }
            }
          }
        }
      },
      "metadata": {
        "properties": {
          "monitor_id": { "type": "keyword" },
          "monitor_name": {
            "type": "text",
            "fields": { "keyword": { "type": "keyword", "ignore_above": 256 } }
          },
          "ai_monitor_name": { "type": "text" },
          "monitor_description": { "type": "text" },
          "monitor_created_time": { "type": "date" },
          "monitor_updated_time": { "type": "date" },
          "monitor_frequency": { "type": "keyword" },
          "monitor_apm_tool": { "type": "keyword" }
        }
      }
    }
}





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




class Monitorlake:
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

    def save_monitorlake_data_in_db(self, db_params: dict, table_name: str, commit=True) -> int:
        query = "insert into " + table_name + " (" + ",".join(db_params.keys()) + ") VALUES (" + ",".join(
            ['%s' for x in db_params.values()]) + ")"
        if commit:
            return mysql_connection.write(query, tuple(db_params.values()))
        else:
            return mysql_connection.write(query, tuple(db_params.values()))





    def create(self, monitorlake_name=None):
        if not monitorlake_name:
            return {"message": "MonitorLake name is required. Please provide a valid name"}
        if not monitorlake_name.lower().strip().isidentifier():
            return {'error': f'Invalid MonitorLake name. Only alphanumeric characters and underscores are allowed.'}

        index_uuid = f"mo_{self.index_uuid}"
        if not index_uuid:
            index_uuid = self.generate_unique_id()

        existing_data = self.get_existing_index_uuid(index_uuid, 'monitorlake')
        if existing_data and existing_data.get('entity_id', ''):
            self.index_uuid = existing_data.get('entity_id', '')
            #print("esisting index", self.index_uuid)
            return {
                "message": "An entry with the same index_uuid already exists.",
                "index_uuid": existing_data.get('entity_id', ''),
                "monitorlake_name": existing_data.get('name', '')
            }

        db_params = {
            "entity_id": index_uuid,
            "entity_type": 'monitorlake',
            "created_at": self.get_current_datetime(),
            "groc_account_id": '',
            "name": monitorlake_name
        }

        #try:
        response = es_connection.create_index(index_uuid, settings=None, mappings=monitorlake_mapping)
        self.index_uuid = index_uuid
        try:
            self.save_monitorlake_data_in_db(db_params, 'groclake_entity_master')
        except Exception as db_error:
            return {"message": "Database error occurred while saving monitorlake.", "error": str(db_error)}
        #print("index in craete", self.index_uuid)
        return {
                "message": "MonitorLake created successfully",
                "index_uuid": index_uuid,
                "monitorlake_name": monitorlake_name
        }


    # def push(self, monitor_data):
    #     try:
    #         if not isinstance(monitor_data, dict):
    #             return {"error": "Invalid monitor data format. Expected dictionary."}
    #         #print("index in push", self.index_uuid)
    #
    #         if not self.index_uuid:
    #             raise ValueError("Invalid index: monitorlake_id is missing.")
    #         metadata = monitor_data.get("metadata", {})
    #         if not metadata or not isinstance(metadata, dict):
    #             return {"error": "Invalid or missing 'metadata' field in monitor data"}
    #
    #         # monitor_id = self.index_uuid
    #         # print("monitor_id",monitor_id)
    #         # if not monitor_id:
    #         #     return {"error": "Missing required field: monitor_id in metadata"}
    #
    #         monitor_id = metadata.get('monitor_id')
    #         if not monitor_id:
    #             return {"error": "monitor_id is required in the monitor data"}
    #
    #         # Validate and format dates
    #         if "monitor_created_time" in monitor_data:
    #             monitor_data["monitor_created_time"] = datetime.strptime(
    #                 monitor_data["monitor_created_time"],
    #                 "%Y-%m-%dT%H:%M:%SZ"
    #             ).strftime("%Y-%m-%dT%H:%M:%S")
    #
    #         if "monitor_updated_time" in monitor_data:
    #             monitor_data["monitor_updated_time"] = datetime.strptime(
    #                 monitor_data["monitor_updated_time"],
    #                 "%Y-%m-%dT%H:%M:%SZ"
    #             ).strftime("%Y-%m-%dT%H:%M:%S")
    #         index = self.index_uuid
    #         #print("index", index)
    #         #monitor_data["metadata"]["monitor_id"] = monitor_id
    #         try:
    #             write_response = es_connection.write(query={'index': index, 'body': monitor_data})
    #             return {
    #                 "message": "Monitor data pushed successfully",
    #                 "monitor_id": monitor_id,
    #
    #             }
    #         except Exception as e:
    #             return {"error": "Failed to push data to Elasticsearch", "details": str(e)}
    #
    #     except Exception as e:
    #         return {"error": "An unexpected error occurred", "details": str(e)}
    def push(self, monitor_data):
        try:
            if not isinstance(monitor_data, dict):
                return {"error": "Invalid monitor data format. Expected dictionary."}
            #print("index in push", self.index_uuid)

            if not self.index_uuid:
                raise ValueError("Invalid index: monitorlake_id is missing.")

            # Get the next sequential monitor ID
            try:
                # Query to get the highest current monitor_id
                query = {
                    "size": 1,
                    "sort": [{"metadata.monitor_id": {"order": "desc"}}],
                    "_source": ["metadata.monitor_id"]
                }

                existing_records = es_connection.search(index=self.index_uuid, body=query)
                last_id = 0

                if existing_records and "hits" in existing_records and "hits" in existing_records["hits"] and \
                        existing_records["hits"]["hits"]:
                    hit = existing_records["hits"]["hits"][0]
                    if "_source" in hit and "metadata" in hit["_source"] and "monitor_id" in hit["_source"]["metadata"]:
                        try:
                            last_id = int(hit["_source"]["metadata"]["monitor_id"])
                        except (ValueError, TypeError):
                            # If conversion fails, start from 0
                            pass

                # Increment the ID
                next_id = last_id + 1
                monitor_id = str(next_id)

            except Exception as e:
                # If search fails, default to ID 1
                monitor_id = "1"
                #print(f"Error fetching last ID: {str(e)}, using default ID: {monitor_id}")

            # Ensure metadata exists
            if "metadata" not in monitor_data:
                monitor_data["metadata"] = {}

            # Add monitor ID and timestamps to metadata
            monitor_data["metadata"]["monitor_id"] = monitor_id

            # Validate and format dates
            if "monitor_created_time" in monitor_data:
                monitor_data["monitor_created_time"] = datetime.strptime(
                    monitor_data["monitor_created_time"],
                    "%Y-%m-%dT%H:%M:%SZ"
                ).strftime("%Y-%m-%dT%H:%M:%S")

            if "monitor_updated_time" in monitor_data:
                monitor_data["monitor_updated_time"] = datetime.strptime(
                    monitor_data["monitor_updated_time"],
                    "%Y-%m-%dT%H:%M:%SZ"
                ).strftime("%Y-%m-%dT%H:%M:%S")

            index = self.index_uuid
            #print("index", index)

            try:
                write_response = es_connection.write(query={'index': index, 'body': monitor_data})
                return {
                    "message": "Monitor data pushed successfully",
                    "monitor_id": monitor_id
                }
            except Exception as e:
                return {"error": "Failed to push data to Elasticsearch", "details": str(e)}

        except Exception as e:
            return {"error": "An unexpected error occurred", "details": str(e)}

    def fetch(self, index,payload):
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
            params = (status, index, 'monitorlake')
            db_response = mysql_connection.write(query, params)

            return {
                "message": "MonitorLake deleted successfully",

            }

        except Exception as e:
            return {"error": "Failed to delete MonitorLake", "details": str(e)}
