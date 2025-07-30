from pymongo.mongo_client import MongoClient
from pymongo.operations import SearchIndexModel
import time
from typing import Dict, Any

class MongoVector:
    def __init__(self, tool_config: Dict[str, Any]):
        self.tool_config = tool_config
        self.client = None
        self.database = None
        self.collection = None
        self.index_name = None
        self.path = None
        self.similarity = None
        self.quantization = None
        self.dimension = None
        
        self.connect()

    def connect(self):
        try:
            self.cluster = self.tool_config.get("connection_string")
            self.database_name = self.tool_config.get("data_base")
            if self.tool_config.get("collection"):
                self.collection_name = self.tool_config.get("collection")
            else:
                self.collection_name = None

            self.similarity = self.tool_config.get("similarity","cosine")
            self.quantization = self.tool_config.get("quantization","scalar")
            self.path = self.tool_config.get("path","embedding")
            self.dimension = self.tool_config.get("dimension",1536)
            self.index_name = self.tool_config.get("index_name",self.collection_name)
            self.numCandidates = self.tool_config.get("numCandidates",10)
            self.limit = self.tool_config.get("limit",10)
            
            if not self.cluster or not self.database_name or not self.collection_name:
                raise ValueError("MongoDB 'connection_string', 'data_base', and 'collection' are required in the config.")

            self.client = MongoClient(self.cluster)
            self.database = self.client[self.database_name]
            if self.collection_name: 
                self.collection = self.database[self.collection_name]

        except Exception as e:
            raise ConnectionError(f"Failed to connect to MongoDB: {e}")

    def create_index(self, index_name, dimension=1536, path=None, similarity=None, quantization=None):
        search_index_model = SearchIndexModel(
            definition={
                "fields": [
                    {
                        "type": "vector",
                        "path": path if path else self.path,
                        "numDimensions": dimension if dimension else self.dimension,
                        "similarity": similarity if similarity else self.similarity,
                        "quantization": quantization if quantization else self.quantization
                    }
                ]
            },
            name=index_name if index_name else self.index_name,
            type="vectorSearch"
        )
        result = self.collection.create_search_index(model=search_index_model)

        #predicate = lambda index: index.get("queryable") is True
        #while True:
        #    indices = list(self.collection.list_search_indexes(result))
        #    if len(indices) and predicate(indices[0]):
        #        break
        #    time.sleep(5)
        return result

    def create_collection(self, collection_name):
        if not self.collection_exists(collection_name):
            self.collection = self.database[collection_name]

    def collection_exists(self, collection_name):
        return self.collection.name == collection_name

    def search_vectors(self, query_vector, path, index_name, numCandidates=10, limit=10, payload=None):
        pipeline = [
            {
                '$vectorSearch': {
                    'index': index_name if index_name else self.index_name,
                    'path': path if path else self.path,
                    'queryVector': query_vector,
                    'numCandidates': numCandidates if numCandidates else self.numCandidates,
                    'limit': limit if limit else self.limit
                }
            },
            {
                '$match': 
                    payload['match_filter']
                
            },
            {
                '$project': 
                    payload['project_fields']
                    
            }
    
        ]
        result = self.collection.aggregate(pipeline)
        return result
    
    def index_exists(self, index_name):
        index = self.collection.list_search_indexes(index_name)
        if index:
            return True
        else:
            return False

    def get_index_info(self, index_name):
        index = self.collection.list_search_indexes(index_name)
        if index:
            return index
        else:
            return None
        
    def get_collection_info(self, collection_name):
        collection = self.database[collection_name]
        if collection:
            return collection
        else:
            return None
        
    def get_database_info(self):
        return self.database
    
    def get_cluster_info(self):
        return self.cluster
    
    def get_client_info(self):
        return self.client
    
    def get_database_name(self):
        return self.database_name
    
    def get_collection_name(self):
        return self.collection_name
    
    def get_index_name(self):
        return self.index_name
    
    def insert_vector(self, vector, vector_document, metadata, doc_id=None, parent_doc_id=None, chunk_index=None):
        document = {
            "vector_id": doc_id,
            f"{self.path}": vector,
            "vector_document": vector_document,
            "metadata": metadata
        }
        if parent_doc_id:
            document["parent_doc_id"] = parent_doc_id
        if chunk_index is not None:
            document["chunk_index"] = chunk_index

        try:
            return self.collection.insert_one(document)
        except Exception as e:
            return {"error": f"Document with this ID already exists. {e}"}

    
    def delete_vector(self, doc_id):
        self.collection.delete_one({"vector_id": doc_id})
    
    def update_vector(self, vector, vector_document, metadata, doc_id):
        self.collection.update_one({"vector_id": doc_id}, {"$set": {"vector": vector, "metadata": metadata}})
    
