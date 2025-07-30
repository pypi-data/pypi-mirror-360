from pymongo import MongoClient
from typing import Dict, Any

class MongoDB:
    def __init__(self, tool_config: Dict[str, Any]):
        self.tool_config = tool_config
        self.client = None
        self.database = None
        self.collection = None

        self.connect()

    def connect(self):
        try:
            connection_string = self.tool_config.get("connection_string")
            database_name = self.tool_config.get("data_base")
            if self.tool_config.get("collection"):
                collection_name = self.tool_config.get("collection")
            else:
                collection_name = None

            if not connection_string or not database_name:
                raise ValueError("'connection_string' and 'data_base' are required in the config.")

            self.client = MongoClient(connection_string)
            self.database = self.client[database_name]
            if collection_name:
                self.collection = self.database[collection_name]
        except Exception as e:
            raise ConnectionError(f"Failed to connect to MongoDB: {e}")

    def insert_document(self, collection_name: str, document: Dict[str, Any], document_id: str):
        document['_id'] = document_id
        return self.database[collection_name].insert_one(document)

    def update_document(self, filter_query: Dict[str, Any], update_fields: Dict[str, Any]):
        return self.collection.update_one(filter_query, {"$set": update_fields})

    def delete_document(self, filter_query: Dict[str, Any]):
        return self.collection.delete_one(filter_query)

    def find_document(self, filter_query: Dict[str, Any]):
        return self.collection.find_one(filter_query)
    
    def read_document(self, collection_name: str, document_id: str):
        return self.database[collection_name].find_one({'_id': document_id})

    def find_documents(self, filter_query: Dict[str, Any], limit: int = 10):
        return list(self.collection.find(filter_query).limit(limit))

    def search_documents(self, collection_name: str, filter_query: Dict[str, Any], limit: int = 10):
        return list(self.database[collection_name].find(filter_query).limit(limit))

    def create_index(self, keys: Dict[str, int], unique: bool = False):
        return self.collection.create_index(list(keys.items()), unique=unique)

    def list_indexes(self):
        return list(self.collection.list_indexes())

    def collection_exists(self, collection_name: str):
        return collection_name in self.database.list_collection_names()

    def create_collection(self, collection_name: str):
        if not self.collection_exists(collection_name):
            self.database.create_collection(collection_name)
        self.collection = self.database[collection_name]

    def get_database_info(self):
        return self.database

    def get_client_info(self):
        return self.client

    def get_database_name(self):
        return self.database.name

    def get_collection_name(self):
        return self.collection.name

    def get_cluster_info(self):
        return self.client.cluster_info()
    
    def get_server_info(self):
        return self.client.server_info()
