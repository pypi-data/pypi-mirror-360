import uuid
from typing import Dict, Any, Optional, List
from elasticsearch import Elasticsearch, ConflictError, NotFoundError

class Elastic:
    def __init__(self, tool_config: Dict[str, Any]):
        """
        Initialize Elasticsearch connection.

        Supports:
        - Hosted: Use hosts + username/password
        - Serverless: Use cloud_id + api_key
        Common config:
            - index_name
        """
        self.tool_config = tool_config
        self.es_client = self._init_es_client()

    def _init_es_client(self) -> Elasticsearch:
        cloud_id = self.tool_config.get("cloud_id")
        api_key = self.tool_config.get("api_key")

        if cloud_id and api_key:
            # ✅ Serverless mode
            return Elasticsearch(
                cloud_id=cloud_id,
                api_key=api_key
            )
        elif self.tool_config.get("hosts"):
            # ✅ Hosted mode
            return Elasticsearch(
                hosts=self.tool_config["hosts"],
                basic_auth=(
                    self.tool_config.get("username"),
                    self.tool_config.get("password")
                ) if self.tool_config.get("username") else None,
                verify_certs=True
            )
        else:
            raise ValueError(
                "Invalid tool_config: Must specify (cloud_id + api_key) for serverless or (hosts [+ username/password]) for hosted."
            )
       

    def create_index(self, index_name, data_schema):
        """
        Creates an index with the provided data schema.
        """
        try:
            # Check if index exists
            if self.es_client.indices.exists(index=index_name):
                return {"status": "success", "message": f"Index {index_name} already exists"}

            # Create index with mapping from data_schema
            mapping = {
                "mappings": {
                    "properties": data_schema
                },
                "settings": {
                    "number_of_shards": 1,
                    "number_of_replicas": 1
                }
            }

            response = self.es_client.indices.create(
                index=index_name,
                body=mapping
            )

            return {
                "status": "success",
                "message": f"Index {index_name} created successfully",
                "response": response
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to create index: {str(e)}"
            }

    def read_document(self, index_name, document_id):
        """
        Retrieves a document by its ID.
        """
        try:
            response = self.es_client.get(
                index=index_name,
                id=document_id
            )
            return {
                "status": "success",
                "document": response['_source']
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to read document: {str(e)}"
            }

    def search_documents(self, index_name, query):
        """
        Searches for documents using the provided query.
        """
        try:
            response = self.es_client.search(
                index=index_name,
                body=query
            )
            return {
                "status": "success",
                "hits": response['hits']['hits'],
                "total": response['hits']['total']['value']
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to search documents: {str(e)}"
            }

    def index_document(self, index_name, document, document_id=None):
        """
        Indexes a document with optional document_id.
        """
        try:
            response = self.es_client.index(
                index=index_name,
                body=document,
                id=document_id
            )
            return {
                "status": "success",
                "message": "Document indexed successfully",
                "document_id": response['_id']
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to index document: {str(e)}"
            }

    def update_document(self, index_name, document_id, update_data):
        """
        Updates a document by its ID.
        """
        try:
            response = self.es_client.update(
                index=index_name,
                id=document_id,
                body={"doc": update_data}
            )
            return {
                "status": "success",
                "message": "Document updated successfully"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to update document: {str(e)}"
            }

    def delete_document(self, index_name, document_id):
        """
        Deletes a document by its ID.
        """
        try:
            response = self.es_client.delete(
                index=index_name,
                id=document_id
            )
            return {
                "status": "success",
                "message": "Document deleted successfully"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to delete document: {str(e)}"
            }

    def bulk_index_documents(self, index_name, documents):
        """
        Bulk indexes multiple documents.
        """
        try:
            actions = []
            for doc in documents:
                action = {
                    "_index": index_name,
                    "_source": doc
                }
                if 'id' in doc:
                    action['_id'] = doc['id']
                actions.append(action)

            response = self.es_client   .bulk(body=actions)
            
            if response.get('errors'):
                return {
                    "status": "error",
                    "message": "Some documents failed to index",
                    "errors": response['items']
                }
            
            return {
                "status": "success",
                "message": "All documents indexed successfully"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to bulk index documents: {str(e)}"
            }

    def delete_index(self, index_name):
        """
        Deletes an index.
        """
        try:
            if self.es_client.indices.exists(index=index_name):
                response = self.es_client.indices.delete(index=index_name)
                return {
                    "status": "success",
                    "message": f"Index {index_name} deleted successfully"
                }
            return {
                "status": "success",
                "message": f"Index {index_name} does not exist"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to delete index: {str(e)}"
            }
