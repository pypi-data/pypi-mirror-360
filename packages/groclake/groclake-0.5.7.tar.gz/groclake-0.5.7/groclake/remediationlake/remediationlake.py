import os
import random
import string
from datetime import datetime
import random
import string
import pytz
import logging
import random
import string
from elasticsearch import Elasticsearch
from groclake.datalake import Datalake
from groclake.modellake import Modellake
from dotenv import load_dotenv

load_dotenv()


remediation_mapping = {
    "properties": {
        "remediation_id": {"type": "keyword"},
        "ai_remediation_name": {"type": "text"},
        "remediation_name": {"type": "text"},
        "remediation_description": {"type": "text"},
        "remediation_created_time": {"type": "date"},
        "remediation_updated_time": {"type": "date"},
        "remediation_actions": {
            "type": "nested",
            "properties": {
                "action_id": {"type": "keyword"},
                "action_seq_num": {"type": "integer"},
                "action_description": {"type": "text"},
                "action_name": {"type": "text"},
                "action_ci_id": {"type": "keyword"},
                "action_ci_name": {"type": "text"}
            }
        },
        "rca_data": {
            "type": "nested",
            "properties": {
                "rca_id": {"type": "keyword"},
                "rca_name": {"type": "text"},
                "rca_description": {"type": "text"}
            }
        }
    }
}



class Config:
    ES_CONFIG = {
        "host": os.getenv("ES_HOST"),
        "port": os.getenv("ES_PORT")
    }

    MYSQL_CONFIG = {
        'user': os.getenv('MYSQL_USER'),
        'passwd': os.getenv('MYSQL_PASSWORD'),
        'host': os.getenv('MYSQL_HOST'),
        'port': os.getenv("MYSQL_PORT"),
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

class Remediationlake:

    def __init__(self, index_uuid=None):
        if not index_uuid:
            raise ValueError('Missing required index_uuid. Ensure you pass a valid index UUID when initializing the class.')
        self.index_uuid = index_uuid
        index_uuid =f"rm_{self.index_uuid}"

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

    def save_remediation_data_in_db(self, db_params: dict, table_name: str, commit=True) -> int:
        query = "insert into " + table_name + " (" + ",".join(db_params.keys()) + ") VALUES (" + ",".join(
            ['%s' for x in db_params.values()]) + ")"
        if commit:
            return mysql_connection.write(query, tuple(db_params.values()))
        else:
            return mysql_connection.write(query, tuple(db_params.values()))

    def create(self, remediation_name=None):

        if remediation_name:
            remediation_name = remediation_name

        if not remediation_name:
            return {"message": "remediation name is required. Please provide a valid remediation name"}
        if not remediation_name.lower().strip().isidentifier():
            return {'error': f'Invalid remediation name. Only alphanumeric characters and underscores are allowed.'}

        if not self.index_uuid:
            self.index_uuid = self.generate_unique_id()

        index_uuid =f"rm_{self.index_uuid}"

        existing_data = self.get_existing_index_uuid(index_uuid, 'remediation')
        if existing_data and existing_data.get('entity_id', ''):
            self.index_uuid=existing_data.get('entity_id','')
            return {
                "message": "An entry with the same index_uuid already exists.",
                "index_uuid": existing_data.get('entity_id',''),
                "remediation_name": existing_data.get('name', '')
            }

        db_params = {
            "entity_id": index_uuid,
            "entity_type": 'remediation',
            "created_at": self.get_current_datetime(),
            "groc_account_id": '',
            "name": remediation_name
        }
        try:
            response = es_connection.create_index(f"rm_{index_uuid}", settings=None, mappings=remediation_mapping)
            self.index_uuid=index_uuid
        except Exception as es_error:
            return {"message": "Elasticsearch error occurred while creating remediation.", "error": str(es_error)}
        try:
            self.save_remediation_data_in_db(db_params, 'groclake_entity_master')
        except Exception as db_error:
            return {"message": "Database error occurred while saving remediation.", "error": str(db_error)}
        return {
            "message": "remediation created successfully",
            "index_uuid": index_uuid,
            "response":response,
            "remediation_name":remediation_name
        }
    
    def push(self,json_obj):
        if "remediation_created_time" in json_obj:
            json_obj["remediation_created_time"] = datetime.strptime(
                json_obj["remediation_created_time"],
                "%Y-%m-%dT%H:%M:%SZ"
            ).strftime("%Y-%m-%dT%H:%M:%S")

        if "remediation_updated_time" in json_obj:
            json_obj["remediation_updated_time"] = datetime.strptime(
                json_obj["remediation_updated_time"],
                "%Y-%m-%dT%H:%M:%SZ"
            ).strftime("%Y-%m-%dT%H:%M:%S")

        write_query = {
            "index":self.index_uuid,
            "body":json_obj
        }
        try:
            write_response = es_connection.write(write_query)

            return write_response
        except Exception as e:
            logging.error(f"Write error in Elasticsearch: {str(e)}")
            return {"error": "Failed to write into ES"}
        
    def search(self,payload):
        try:
            print(self.index_uuid)
            read_response = es_connection.search(index=self.index_uuid,body=payload)
            return read_response
        except Exception as e:
            logging.error(f"Search error in Elasticsearch: {str(e)}")
            return {"error": "Failed to retrieve search results"}
        
    def delete(self, index):
        try:
            if not self.index_uuid:
                raise ValueError("Invalid index: rmlake_id is missing.")

            # Delete the index from Elasticsearch
            es_response = es_connection.delete_index(index=index)

            # Soft delete in database
            status = 2 # Status code for soft delete
            query = "UPDATE groclake_entity_master SET status = %s WHERE entity_id = %s AND entity_type = %s"
            params = (status, index, 'rmlake')
            db_response = mysql_connection.write(query, params)

            return {
                "message": "Remediationlake deleted successfully"
            }

        except Exception as e:
            return {"error": "Failed to delete Remediationlake", "details": str(e)}
    
