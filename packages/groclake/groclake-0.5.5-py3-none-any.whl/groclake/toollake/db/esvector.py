import uuid
from typing import Dict, Any, Optional, List
from elasticsearch import Elasticsearch, ConflictError, NotFoundError

class ESVector:
    def __init__(self, tool_config: Dict[str, Any]):
        """
        Initialize Elasticsearch connection.

        Supports:
        - Hosted: Use hosts + username/password
        - Serverless: Use cloud_id + api_key
        Common config:
            - index_name
            - Optional: vector_dim, similarity, hnsw_type, hnsw_m, hnsw_ef_construction
        """
        self.tool_config = tool_config
        self.index_name = tool_config["index_name"]
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

    def create_index(self, index_name: Optional[str] = None):
        index_name = index_name or self.index_name

        vector_dim = self.tool_config.get('vector_dim', 1536)
        similarity = self.tool_config.get('similarity', 'cosine')
        hnsw_type = self.tool_config.get('hnsw_type', 'hnsw')
        hnsw_m = self.tool_config.get('hnsw_m', 16)
        hnsw_ef_construction = self.tool_config.get('hnsw_ef_construction', 100)

        body = {
            "settings": {
                "number_of_shards": 3,
                "number_of_replicas": 1,
                "refresh_interval": "10s"
            },
            "mappings": {
                "dynamic": "false",
                "properties": {
                    "vector_id": {"type": "keyword"},
                    "parent_doc_id": {"type": "keyword"},
                    "vector": {
                        "type": "dense_vector",
                        "dims": vector_dim,
                        "index": True,
                        "similarity": similarity,
                        "index_options": {
                            "type": hnsw_type,
                            "m": hnsw_m,
                            "ef_construction": hnsw_ef_construction
                        }
                    },
                    "vector_document": {"type": "text"},
                    "metadata": {"type": "object"},
                    "chunk_index": {"type": "integer"}
                }
            }
        }

        if not self.es_client.indices.exists(index=index_name):
            self.es_client.indices.create(index=index_name, body=body)

    def insert_vector(
        self,
        vector: List[float],
        vector_document: str,
        metadata: Dict[str, Any],
        doc_id: Optional[str] = None,
        parent_doc_id: Optional[str] = None,
        chunk_index: Optional[int] = None,
        index_name: Optional[str] = None
    ) -> Dict[str, Any]:
        index_name = index_name or self.index_name
        doc_id = doc_id or str(uuid.uuid4())

        document = {
            "vector_id": doc_id,
            "vector": vector,
            "vector_document": vector_document,
            "metadata": metadata
        }
        if parent_doc_id:
            document["parent_doc_id"] = parent_doc_id
        if chunk_index is not None:
            document["chunk_index"] = chunk_index

        try:
            return self.es_client.index(index=index_name, id=doc_id, document=document)
        except ConflictError:
            return {"error": "Document with this ID already exists."}

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
        
    def search_vectors(
        self,
        query_vector: List[float],
        top_k: int = 10,
        vector_field: str = "vector",
        num_candidates: Optional[int] = None,
        metadata_filters: Optional[Dict[str, Any]] = None,
        search_type: str = "knn",
        index_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search vectors using either retriever.knn or script_score.

        - search_type = "knn" (default) or "script_score"
        - metadata_filters = optional dict like {"content_language": "en"}
        """
        index_name = index_name or self.index_name
        num_candidates = num_candidates or (top_k * 2)

        if search_type == "knn":
            knn_body = {
                "field": vector_field,
                "query_vector": query_vector,
                "k": top_k,
                "num_candidates": num_candidates
            }

            if metadata_filters:
                filter_clauses = []
                for key, value in metadata_filters.items():
                    filter_clauses.append({
                        "term": {
                            f"metadata.{key}.keyword": value
                        }
                    })
                knn_body["filter"] = {
                    "bool": {
                        "must": filter_clauses
                    }
                }

            es_query = {
                "retriever": {
                    "knn": knn_body
                }
            }

        elif search_type == "script_score":
            filter_clauses = []
            if metadata_filters:
                for key, value in metadata_filters.items():
                    filter_clauses.append({
                        "term": {
                            f"metadata.{key}.keyword": value
                        }
                    })

            es_query = {
                "query": {
                    "script_score": {
                        "query": {
                            "bool": {
                                "filter": filter_clauses if filter_clauses else {"match_all": {}}
                            }
                        },
                        "script": {
                            "source": f"""
                                if (doc['{vector_field}'].size() > 0) {{
                                    return cosineSimilarity(params.query_vector, '{vector_field}') + 1.0;
                                }} else {{
                                    return 0;
                                }}
                            """,
                            "params": {"query_vector": query_vector}
                        }
                    }
                },
                "size": top_k
            }

        else:
            raise ValueError("Invalid search_type. Must be 'knn' or 'script_score'.")

        response = self.es_client.search(index=index_name, body=es_query)
        hits = response.get('hits', {}).get('hits', [])
        return [hit['_source'] for hit in hits]

    def read_vector(self, doc_id: str, index_name: Optional[str] = None) -> Dict[str, Any]:
        index_name = index_name or self.index_name
        try:
            response = self.es_client.get(index=index_name, id=doc_id)
            return response['_source']
        except NotFoundError:
            return {"error": f"Document with id {doc_id} not found."}

    def delete_vector(self, doc_id: str, index_name: Optional[str] = None) -> Dict[str, Any]:
        index_name = index_name or self.index_name
        try:
            return self.es_client.delete(index=index_name, id=doc_id)
        except NotFoundError:
            return {"error": f"Document with id {doc_id} not found."}

    def delete_vectors_by_parent(self, parent_doc_id: str, index_name: Optional[str] = None) -> Dict[str, Any]:
        index_name = index_name or self.index_name
        query = {
            "query": {
                "term": {
                    "parent_doc_id.keyword": parent_doc_id
                }
            }
        }
        return self.es_client.delete_by_query(index=index_name, body=query)

    def delete_index(self, index_name: Optional[str] = None) -> Dict[str, Any]:
        index_name = index_name or self.index_name
        if self.es_client.indices.exists(index=index_name):
            self.es_client.indices.delete(index=index_name)
            return {"message": f"Index '{index_name}' deleted successfully."}
        else:
            return {"error": f"Index '{index_name}' does not exist."}

    def execute(self, query: Dict[str, Any], index_name: Optional[str] = None) -> Dict[str, Any]:
        index_name = index_name or self.index_name
        return self.es_client.search(index=index_name, body=query)

    def index_exists(self, index_name):
        """
        Check if an index exists in Elasticsearch.
        :param index_name: Name of the index to check.
        :return: True if exists, False otherwise.
        """
        return self.es_client.indices.exists(index=index_name)
