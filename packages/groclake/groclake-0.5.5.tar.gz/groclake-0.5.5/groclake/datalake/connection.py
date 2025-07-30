# connection.
import mysql.connector
import redis
from elasticsearch import Elasticsearch
from io import BytesIO
from PIL import Image
import requests
from google.cloud import storage
from google.oauth2 import service_account
import boto3
import uuid
from pymongo import MongoClient
import base64
import snowflake.connector
from neo4j import GraphDatabase
from urllib.parse import urlparse



class Connection:
    def __init__(self):
        self.connection = None

    def connect(self):
        raise NotImplementedError("Subclasses must implement the connect method.")

    def read(self, query):
        raise NotImplementedError("Subclasses must implement the read method.")

class SQLConnection(Connection):
    def __init__(self, db_config):
        super().__init__()
        self.db_config = db_config
        self.cursor = None  # Initialize the cursor attribute
        self.connect()

    def connect(self):
        try:
            if self.connection and self.connection.is_connected():
                return  # Connection is active, no need to reconnect
            self.connection = mysql.connector.connect(**self.db_config)
            self.cursor = self.connection.cursor(dictionary=True)
        except mysql.connector.Error as e:
            print(f"Error connecting to MySQL: {e}")
            self.connection = None
    def ensure_connection(self):
        """Reconnects if the connection is lost."""
        if not self.connection or not self.connection.is_connected():
            self.connect()

    def read(self, query, params=None, multiple=False, parsed=True):
        self.ensure_connection()
        """
        Executes a SELECT query and retrieves the result.

        Args:
            query (str): SQL query to execute.
            params (tuple): Parameters for the SQL query.
            fetch_all (bool): Whether to fetch all results or a single result.
            parsed (bool): Whether to parse results into a dictionary.

        Returns:
            list or dict: Query result as a list of dictionaries (fetch_all=True),
                          or a single dictionary (fetch_all=False and parsed=True).
        """
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()
            cursor = self.connection.cursor(dictionary=parsed)
            cursor.execute(query, params)

            if multiple:
                # Fetch all rows and return as a list
                result = cursor.fetchall()
            else:
                # Fetch a single row
                result = cursor.fetchone()

            # Return an empty dictionary or list if no result is found
            if multiple and not result:
                return []
            elif not multiple and not result:
                return {} if parsed else None

            return result
        except mysql.connector.Error as err:
            raise Exception(f"MySQL query error: {err}")
        finally:
            cursor.close()


    def write(self, query, params=None):
        self.ensure_connection()

        """
        Executes a write query and commits the transaction.

        Args:
            query (str): The SQL query to execute.
            params (tuple or None): Parameters to pass to the query.

        Returns:
            int: The last inserted ID if applicable.
        """
        if not self.connection:
            raise Exception("Connection not established. Call connect() first.")
        try:
            self.cursor.execute(query, params or ())
            self.connection.commit()
            return self.cursor.lastrowid
        except Exception as e:
            self.connection.rollback()
            print(f"Error executing write query: {e}")
            raise

    def close(self):
        """Closes the connection and cursor."""
        if self.cursor:
            self.cursor.close()
            self.cursor = None
        if self.connection:
            self.connection.close()
            self.connection = None


    #Add close method here as well

class RedisConnection(Connection):
    def __init__(self, config):
        super().__init__()
        self.config = config

    def connect(self):
        self.connection = redis.StrictRedis(**self.config)

    def read(self, query):
        if not self.connection:
            raise Exception("Connection not established.")
        if query == "dbsize":
            return self.connection.dbsize()
        else:
            raise ValueError("Unsupported query for Redis.")

    def get(self, key):
        return self.connection.get(key)

    def set(self, key, value, cache_ttl=86400):
        """
        Set a value in Redis with an optional TTL (time-to-live).

        Args:
            key (str): The key to set in Redis.
            value (any): The value to associate with the key.
            cache_ttl (int): Time-to-live in seconds (default: 1 day).
        """
        self.connection.set(key, value, ex=cache_ttl)


class ESConnection(Connection):

    def __init__(self, config):
        super().__init__()
        self.es_host = config.get('host', 'localhost')
        self.es_port = config.get('port', 9200)
        self.api_key = config.get('api_key', None)
        self.schema = config.get('schema', 'http')
        self.connection = None

    from elasticsearch import Elasticsearch, ConnectionError

    def connect(self):
        """
        Establishes a connection to Elasticsearch.
        """
        try:
            if self.api_key:
                self.connection = Elasticsearch(
                    f"{self.schema}://{self.es_host}:{self.es_port}",
                    api_key=self.api_key
                )
            else:
                self.connection = Elasticsearch(
                    f"{self.schema}://{self.es_host}:{self.es_port}"
                )
        except ConnectionError as e:
            print("Error connecting to Elasticsearch:", str(e))
            self.connection = None

    def read(self, query):
        """
        Executes a query to Elasticsearch, here 'query' contains 'index' dynamically passed in.
        """
        if not self.connection:
            raise Exception("Connection not established.")

        # Access 'index' dynamically from 'query' dictionary
        index = query.get('index')
        body = query.get('body')

        es_response = self.connection.count(index=index, body=body)
        return es_response.get("count", 0)

    def write(self, query, params=None):
        """
        Executes a write query to Elasticsearch, where 'index' is dynamically passed in.
        """
        if not self.connection:
            raise Exception("Connection not established.")

        index = query.get('index')
        body = query.get('body')

        try:
            response = self.connection.index(index=index, body=body)
            return response
        except Exception as e:
            raise Exception(f"Error executing write query: {e}")

    def search(self, query=None, index=None, body=None):
        """
        Executes a search query to Elasticsearch.
        Accepts a dictionary query or individual index and body arguments.
        """
        if not self.connection:
            raise Exception("Connection not established.")

        # Validate index and body
        if not index or not body:
            raise ValueError("Both 'index' and 'body' are required for the search query.")

        try:
            response = self.connection.search(index=index, body=body)
            return response
        except Exception as e:
            raise Exception(f"Error executing search query: {e}")

    def delete(self, index, doc_id=None, body=None):
        """
        Deletes a document by ID or deletes multiple documents by query.

        - If `doc_id` is provided, deletes a single document.
        - If `body` (query) is provided, deletes multiple documents.
        """
        if not self.connection:
            raise Exception("Connection not established.")

        try:
            if doc_id:
                # Delete a single document by ID
                response = self.connection.delete(index=index, id=doc_id)
            elif body:
                # Delete multiple documents based on query
                response = self.connection.delete_by_query(index=index, body=body)
            else:
                raise ValueError("Either 'doc_id' or 'body' must be provided for deletion.")

            return response
        except Exception as e:
            raise Exception(f"Error executing delete query: {e}")

    def create_index(self, index_name, settings=None, mappings=None):
        """
        Creates an index in Elasticsearch with optional settings and mappings.
        """
        if not self.connection:
            raise Exception("Connection not established.")

        try:
            if self.connection.indices.exists(index=index_name):
                return {"message": f"Index '{index_name}' already exists."}

            body = {}
            if settings:
                body["settings"] = settings
            if mappings:
                body["mappings"] = mappings
            response = self.connection.indices.create(index=index_name, body=body)
            return response
        except Exception as e:
            raise Exception(f"Error creating index: {e}")

    def delete_index(self, index):
        """
        Deletes an index from Elasticsearch.

        :param index_name: Name of the index to be deleted.
        :return: Response from Elasticsearch.
        """
        if not self.connection:
            raise Exception("Connection not established.")

        try:
            if self.connection.indices.exists(index=index):
                response = self.connection.indices.delete(index=index)
                return response
            else:
                return {"message": f"Index '{index}' does not exist."}
        except Exception as e:
            raise Exception(f"Error deleting index: {e}")


class GCPConnection(Connection):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.gcp_storage = None
        self.bucket = None
        self.bucket_name = config.get("gcp_bucket_name")
        self.IMAGE_PREFIX  = config.get("host_cdn_url")
        if not self.bucket_name:
            raise ValueError("Bucket name is required in GCP config.")

    def connect(self):
        """
        Establishes a connection to the specified GCP bucket by initializing the storage client.
        """
        try:
            credentials_json = self.config.get("gcp_credentials_json")
            if not credentials_json:
                raise ValueError("Service account file is required in GCP config.")

            if isinstance(credentials_json, dict):
                # Create credentials from a dictionary
                credentials = service_account.Credentials.from_service_account_info(credentials_json)
            else:
                raise ValueError("The credentials_json must be a dictionary.")

            # Initialize the GCP storage client
            self.gcp_storage = storage.Client(credentials=credentials)
            self.bucket = self.gcp_storage.bucket(self.bucket_name)

        except Exception as e:
            raise ConnectionError(f"Failed to connect to GCP bucket: {e}")

    @staticmethod
    def decode_base64_image(base64_string):
        """Decodes base64 string to bytes."""
        return base64.b64decode(base64_string)

    @staticmethod
    def download_image_from_url(url):
        """Downloads an image from the given URL and returns the binary content."""
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.content
        else:
            raise ValueError(f"Failed to download image from URL: {response.status_code}")

    @staticmethod
    def process_image_to_webp(image_content):
        """Processes the image and converts it to WEBP format."""
        image = Image.open(BytesIO(image_content)).convert('RGBA')
        webp_image = BytesIO()
        image.save(webp_image, 'WEBP', quality=90)
        webp_image.seek(0)
        return webp_image


    @staticmethod
    def process_image(response):
        image = Image.open(BytesIO(response)).convert('RGBA')
        if image.mode == 'RGB':
            file_ext = '.jpg'
            content_type = 'image/jpg'
            format_type = 'JPEG'
        else:
            file_ext = '.png'
            content_type = 'image/png'
            format_type = 'PNG'
        gcp_file = BytesIO()
        image.save(gcp_file, format=format_type)
        gcp_file.seek(0)
        return gcp_file, file_ext, content_type



    def upload(self, params):
        """Handles image processing and uploads to GCP."""
        image_type = params.get("image_type")
        image_data = params.get("image_data")
        image_format = params.get("image")
        destination_blob_name = params.get("gcp_bucket_path")

        if not image_type or not image_data:
            raise ValueError("Both image_type and image_data must be provided.")

        # Process image
        if image_type == "base64":
            processed_image = self.decode_base64_image(image_data)
        elif image_type == "url":
            processed_image = self.download_image_from_url(image_data)
        else:
            raise ValueError("Unsupported image type. Use 'base64' or 'url'.")

        # Logic for processing and uploading images based on format
        if image_format == "webp":
            # Convert to WEBP format
            webp_image = self.process_image_to_webp(processed_image)
            self.upload_webp_image(webp_image, destination_blob_name, content_type="image/webp")
            return self.IMAGE_PREFIX + destination_blob_name + ".webp"
        else:
            # Convert to JPEG format
            image_data, file_ext, content_type = self.process_image(processed_image)
            self.upload_jpeg_image(image_data, destination_blob_name, file_ext, content_type)
            return self.IMAGE_PREFIX + destination_blob_name + f'{file_ext}'


    def upload_webp_image(self, image_data, destination_path, content_type="image/webp"):
        bucket = self.gcp_storage.bucket(self.bucket_name)
        destination_path += '.webp'
        blob = bucket.blob(destination_path)
        blob.upload_from_file(image_data, content_type=content_type)


    def upload_jpeg_image(self, image_data, destination_path, file_ext, content_type):
        bucket = self.gcp_storage.bucket(self.bucket_name)
        destination_path += f'{file_ext}'
        blob = bucket.blob(destination_path)
        blob.upload_from_file(image_data, content_type=content_type)





class S3Connection(Connection):

    def __init__(self, config):
        super().__init__()
        self.config = config
        self.s3_client = None
        self.s3_bucket = config.get("aws_s3_bucket")
        self.region_name = config.get("aws_region_name", "us-east-1")
        self.S3_FOLDER = config.get("aws_s3_folder")



    def connect(self):
        """
        Establishes a connection to the specified S3 bucket by initializing the S3 client.
        """
        try:
            aws_access_key_id = self.config.get("aws_access_key_id")
            aws_secret_access_key = self.config.get("aws_secret_access_key")
            if not aws_access_key_id or not aws_secret_access_key:
                raise ValueError("AWS access key ID and secret access key are required in S3 config.")

            # Initialize the S3 client
            self.s3_client = boto3.client(
                "s3",
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
                region_name=self.region_name
            )
        except Exception as e:
            raise ConnectionError(f"Failed to connect to S3 bucket: {e}")

    def download_file_from_url(self, file_url):
        try:
            response = requests.get(file_url)
            response.raise_for_status()
            content_type = response.headers.get('Content-Type')
            extension = 'pdf' if 'pdf' in content_type else 'docx'
            filename = f"downloaded_document.{extension}"
            file_obj = BytesIO(response.content)

            return file_obj, filename
        except requests.RequestException as e:
            raise ValueError("Failed to download file from URL") from e

    def decode_base64_data(self, base64_data):
        try:
            decoded_data = base64.b64decode(base64_data)
            filename = f"{uuid.uuid4().hex[:16]}.pdf"
            file_obj = BytesIO(decoded_data)
            return file_obj, filename
        except Exception as e:
            raise ValueError("Invalid base64 data") from e

    def upload(self, params):
        document_type = params.get("document_type")
        document_data = params.get("document_data")
        file_obj, filename = self.download_file_from_url(document_data)
        folder_name = params.get("folder_name")

        if document_type == "base64":
            file_obj, filename = self.decode_base64_data(document_data)
        elif document_type == "url":
            file_obj, filename = self.download_file_from_url(document_data)
        else:
            raise ValueError("Unsupported document type. Use 'base64' or 'url'.")

        try:
            # s3_key = f"{self.folder_name}/{filename}"
            s3_key = f'{self.S3_FOLDER}/{folder_name}/{filename}'
            self.s3_client.upload_fileobj(
                file_obj,
                self.s3_bucket,
                s3_key            )
            return f'https://{self.s3_bucket}/{s3_key}'
        except Exception as e:
            return e
            raise


class MongoDBConnection(Connection):
    """
    Class to manage MongoDB connections and operations.
    """

    def __init__(self, config):
        super().__init__()
        self.config = config
        self.client = None
        self.database = None

    def connect(self):
        """
        Establishes a connection to the MongoDB database.
        """
        try:
            cluster = self.config.get("connection_string")
            database_name = self.config.get("data_base")
            if not cluster or not database_name:
                raise ValueError("MongoDB 'cluster' and 'data_base' are required in the config.")

            self.client = MongoClient(cluster)
            self.database = self.client[database_name]
        except Exception as e:
            raise ConnectionError(f"Failed to connect to MongoDB: {e}")

    def insert(self, collection_name, data):
        """
        Inserts a document into a MongoDB collection.

        :param collection_name: Name of the collection to insert the document.
        :param data: Dictionary representing the document to insert.
        :return: The inserted document ID.
        """
        try:
            collection = self.database[collection_name]
            result = collection.insert_one(data)
            return str(result.inserted_id)
        except Exception as e:
            raise RuntimeError(f"Failed to insert data into MongoDB: {e}")


    def read(self, collection_name, query):
        """
        Reads documents from a MongoDB collection based on a query.

        :param collection_name: Name of the collection to read from.
        :param query: Dictionary representing the query to filter documents.
        :return: List of matching documents.
        """
        try:
            collection = self.database[collection_name]
            results = collection.find(query)
            return [doc for doc in results]
        except Exception as e:
            raise RuntimeError(f"Failed to read data from MongoDB: {e}")

    def fetch_sort(self, collection, sort_key, num, desc, filter_query=None):
        """
        Fetches sorted records from a MongoDB collection with optional filtering.

        :param collection: Name of the collection to fetch logs from.
        :param sort_key: Field to sort by.
        :param num: Number of records to fetch.
        :param desc: Sort order (True for descending, False for ascending).
        :param filter_query: (Optional) Dictionary to filter results.
        :return: List of sorted logs.
        """
        try:
            collection = self.database[collection]
            sort_order = -1 if desc else 1
            query = filter_query if filter_query else {}

            results = collection.find(query).sort(sort_key, sort_order).limit(num)
            return list(results)

        except Exception as e:
            raise RuntimeError(f"Failed to fetch logs from MongoDB: {e}")

class SnowflakeConnection(Connection):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.connection = None
        self.cursor = None
        self.connect()

    def connect(self):
        try:
            self.connection = snowflake.connector.connect(
                user=self.config.get('user'),
                password=self.config.get('password'),
                account=self.config.get('account'),
                warehouse=self.config.get('warehouse'),
                database=self.config.get('database'),
                schema=self.config.get('schema')
            )
            self.cursor = self.connection.cursor()
        except snowflake.connector.Error as e:
            print(f"Error connecting to Snowflake: {e}")
            self.connection = None

    def read(self, query, params=None):
        self.ensure_connection()
        try:
            self.cursor.execute(query, params)
            return self.cursor.fetchall()
        except snowflake.connector.Error as e:
            raise Exception(f"Snowflake query error: {e}")

    def write(self, query, params=None):
        self.ensure_connection()
        try:
            self.cursor.execute(query, params)
            self.connection.commit()
        except snowflake.connector.Error as e:
            self.connection.rollback()
            raise Exception(f"Error executing write query: {e}")

    def close(self):
        if self.cursor:
            self.cursor.close()
            self.cursor = None
        if self.connection:
            self.connection.close()
            self.connection = None

    def ensure_connection(self):
        if not self.connection:
            self.connect()


class Neo4jConnection(Connection):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.uri = self.config['URI']
        self.user = self.config['USER']
        self.pwd = self.config['PWD']
        
    def connect(self):
        self._driver = GraphDatabase.driver(self.uri, auth=(self.user, self.pwd))
        

    def close(self):
        self._driver.close()

    def format_properties(self,prefix, props):
        """Build Cypher properties string and parameters."""
        prop_str = ", ".join([f"{k}: ${prefix}_{k}" for k in props])
        param_dict = {f"{prefix}_{k}": v for k, v in props.items()}
        return f"{{{prop_str}}}", param_dict
    
    def convert_nodes_to_json(self, nodes):
        results = []
        for record in nodes:
            node = record["n"]  # Extract the Node object from the Record
            node_data = dict(node)
            node_data["type"] = list(node.labels)[0]  # Get label like 'Class', 'Method', etc.
            results.append(node_data)
        return results

    
    def create_node(self, payload):
        """Create or merge a node using all properties, and return meaningful properties."""
        label = payload.get("label")
        properties = payload.get("properties")

        if not label or not properties:
            raise ValueError({"error": "label and at least one property must be provided to create a Node"})

        # Build dynamic MERGE clause using all properties
        merge_props_str = ", ".join([f"{key}: ${key}" for key in properties.keys()])
        
        query = (
            f"MERGE (n:{label} {{ {merge_props_str} }}) "
            f"SET n += $props "
            f"RETURN n"
        )

        with self._driver.session() as session:
            result = session.run(query, **properties, props=properties).single()
            node = result["n"]
            return {
                "message": f"Node for {label} Merged",
                "Node": dict(node)
            }


     
    def update_node_properties(self, payload):
        """
        Updates properties of a node and returns a meaningful response.
        """
        label = payload['label']
        identity_props = payload['identity_props']
        update_props = payload['update_props']

        match_query = f"""
        MATCH (n:{label} {{{', '.join([f'{k}: ${k}' for k in identity_props])}}})
        RETURN n
        """
        update_query = f"""
        MATCH (n:{label} {{{', '.join([f'{k}: ${k}' for k in identity_props])}}})
        SET {', '.join([f'n.{k} = ${k}' for k in update_props])}
        RETURN n
        """

        with self._driver.session() as session:
            match_result = session.run(match_query, **identity_props)
            if not match_result.peek():
                return {"status": "error", "message": "Node not found", "identity": identity_props}

            result = session.run(update_query, **identity_props, **update_props)
            updated_node = result.single()['n']
            return {
                "status": "success",
                "message": "Node properties updated",
                "updated_fields": list(update_props.keys()),
                "node": dict(updated_node)
            }
 
    
    def add_property_to_node(self, payload):
        """
        Adds or updates a single property on a matched node and returns a response.
        """
        label = payload['label']
        identity_props = payload['identity_props']
        prop_key = payload['prop_key']
        prop_value = payload['prop_value']

        match_query = f"""
        MATCH (n:{label} {{{', '.join([f'{k}: ${k}' for k in identity_props])}}})
        RETURN n
        """
        update_query = f"""
        MATCH (n:{label} {{{', '.join([f'{k}: ${k}' for k in identity_props])}}})
        SET n.{prop_key} = $prop_value
        RETURN n
        """

        with self._driver.session() as session:
            match_result = session.run(match_query, **identity_props)
            if not match_result.peek():
                return {"status": "error", "message": "Node not found", "identity": identity_props}

            result = session.run(update_query, **identity_props, prop_value=prop_value)
            updated_node = result.single()['n']
            return {
                "status": "success",
                "message": f"Property '{prop_key}' set successfully",
                "updated_property": {prop_key: prop_value},
                "node": dict(updated_node)
            }
    
    
    def create_relationship(self, payload):
        """
        Create a relationship between two nodes with the given label and properties.

        Expected payload:
        {
            "node1": "Person", // label
            "node2": "Person", // label
            "relation": "Friends_with",
            "prop1": { "name": "Alice", "age": 53 },
            "prop2": { "name": "John", "age": 35 }
        }
        """
        label1 = payload["node1"]
        label2 = payload["node2"]
        rel_type = payload["relation"]
        props1 = payload["prop1"]
        props2 = payload["prop2"]
        if not props1 or not props2:
            raise ValueError("Both 'prop1' and 'prop2' must contain at least one property to create a relation.")

        props1_str, params1 = self.format_properties("p1", props1)
        props2_str, params2 = self.format_properties("p2", props2)

        query = (
            f"MERGE (a:{label1} {props1_str}) "
            f"MERGE (b:{label2} {props2_str}) "
            f"MERGE (a)-[r:{rel_type}]->(b) "
            f"RETURN r"
        )

        params = {**params1, **params2}

        with self._driver.session() as session:
            session.run(query, params).single()
            return {"message": f"Relationship `{rel_type}` created between `{label1}` and `{label2}`"}

    
    def get_nodes(self, payload=None):
        """
        Retrieve all nodes, or nodes with a specific label and properties from a payload.
        
        Args:
            payload (dict): Dictionary with optional 'label' (str) and 'properties' (dict) keys.
            
        Returns:
            list: Matching nodes.
        """
        payload = payload or {}
        label = payload.get("label", "")
        properties = payload.get("properties", {})

        props_string = ""
        if properties:
            props_list = [f"{key}: ${key}" for key in properties]
            props_string = "{" + ", ".join(props_list) + "}"

        if label:
            query = f"MATCH (n:{label} {props_string}) RETURN n"
        else:
            query = f"MATCH (n {props_string}) RETURN n"

        with self._driver.session() as session:
            return self.convert_nodes_to_json(session.run(query, properties))
        
    def get_nodes_by_modified_time(self, payload=None):
        """
        Retrieve nodes with an optional label where 'last_modified' is on or after a given timestamp.
        
        Args:
            payload (dict): Should include:
                - 'label' (str): Optional node label.
                - 'modified_since' (str): ISO 8601 formatted timestamp (e.g. '2024-12-01T00:00:00').
                
        Returns:
            list: Matching nodes.
        """
        payload = payload or {}
        label = payload.get("label", "")
        modified_since = payload.get("modified_time")

        if not modified_since:
            raise ValueError("The 'modified_time' field is required in the payload.")

        label_str = f":{label}" if label else ""
        query = (
        f"MATCH (n{label_str}) "
        f"WHERE datetime(n.modified_time) >= datetime($modified_since) "
        f"RETURN n"
    )


        with self._driver.session() as session:
            result = session.run(query, {"modified_since": modified_since})
            return self.convert_nodes_to_json(result)
   
        
    def get_node_relations(self, payload=None):
        """
        Retrieve all nodes with a specific label and properties, along with their relationships.

        Args:
            payload (dict): Dictionary with optional 'label' (str) and 'properties' (dict) keys.

        Returns:
            list: List of dictionaries with start_node, relationship, and end_node in JSON format.
        """
        payload = payload or {}
        label = payload.get("label", "")
        properties = payload.get("properties", {})

        # Construct Cypher query based on provided parameters
        if label:
            # Start node has a label
            if properties:
                # Label with properties
                props_list = [f"{key}: ${key}" for key in properties]
                props_string = "{" + ", ".join(props_list) + "}"
                query = f"MATCH (a:{label} {props_string})-[r]->(b) RETURN a, r, b"
            else:
                # Label only, no properties
                query = f"MATCH (a:{label})-[r]->(b) RETURN a, r, b"
        else:
            # No label specified, just properties
            if properties:
                props_list = [f"{key}: ${key}" for key in properties]
                props_string = "{" + ", ".join(props_list) + "}"
                query = f"MATCH (a {props_string})-[r]->(b) RETURN a, r, b"
            else:
                # Require at least label or properties
                raise ValueError("Either 'label' or 'properties' must be provided")
        with self._driver.session() as session:
            result = session.run(query, properties)
            return [
                {
                    "start_node": {
                        "labels": list(record["a"].labels),
                        "properties": dict(record["a"])
                    },
                    "relationship": {
                        "type": record["r"].type,
                        "properties": dict(record["r"])
                    },
                    "end_node": {
                        "labels": list(record["b"].labels),
                        "properties": dict(record["b"])
                    }
                }
                for record in result
            ]


    def get_relationships(self, payload=None):
        """
        Retrieve relationships based on relationship type and optional properties.

        Args:
            payload (dict): Optional dictionary with 'rel_type' (str) and 'properties' (dict).

        Returns:
            list: Matching relationships.
        """
        payload = payload or {}
        rel_type = payload.get("rel_type", "")
        properties = payload.get("properties", {})

        props_string = ""
        if properties:
            props_list = [f"{key}: ${key}" for key in properties]
            props_string = "{" + ", ".join(props_list) + "}"

        # Build Cypher query based on presence of rel_type and properties
        if rel_type:
            query = f"MATCH ()-[r:{rel_type} {props_string}]->() RETURN r"
        else:
            query = f"MATCH ()-[r {props_string}]->() RETURN r"

        with self._driver.session() as session:
            return [record["r"] for record in session.run(query, properties)]

    def delete_node(self, payload):
        """
        Delete a node with the specified label and matching properties.
        
        Args:
            label (str): The label of the node to delete.
            properties (dict): Dictionary of properties to identify the node.
            
        Raises:
            ValueError: If label or properties are not provided.
        """
        label = payload.get("label","")
        properties = payload.get("properties",{})
        if not label or not properties:
            raise ValueError("Both label and at least one property are required to delete a node.")

        props_list = [f"{key}: ${key}" for key in properties]
        props_string = "{" + ", ".join(props_list) + "}"
        
        query = f"MATCH (n:{label} {props_string}) DETACH DELETE n"
        
        with self._driver.session() as session:
            session.run(query, properties)
            return session.run(query, properties)
        
    
    def delete_all_nodes(self, label):
        """
        Delete all nodes with the specified label and optional properties.
        
        Args:
            label (str): The label of the nodes to delete.
            properties (dict, optional): Properties to match for deletion.
        
        Raises:
            ValueError: If label is not provided.
        """
        if not label:
            raise ValueError("Label is required to delete nodes.")
        query = f"MATCH (n:{label}) DETACH DELETE n"
        print(f"Deleting {label}")
        with self._driver.session() as session:
            return session.run(query)



    def delete_relationship(self, payload):
        """
        Delete a relationship between two nodes using dynamic labels and properties.

        Payload format:
        {
            "label1": "Person",
            "prop1": { "name": "Alice" },
            "label2": "Person",
            "prop2": { "name": "Bob" },
            "rel_type": "FRIENDS_WITH"
        }
        """
        label1 = payload.get("label1")
        label2 = payload.get("label2")
        prop1 = payload.get("prop1", {})
        prop2 = payload.get("prop2", {})
        rel_type = payload.get("rel_type")

        if not (label1 and label2 and prop1 and prop2 and rel_type):
            raise ValueError("Payload must include label1, prop1, label2, prop2, and rel_type")

        # Convert prop1 and prop2 to Cypher match strings
        prop1_str = ", ".join([f"{k}: $prop1_{k}" for k in prop1])
        prop2_str = ", ".join([f"{k}: $prop2_{k}" for k in prop2])

        query = (
            f"MATCH (a:{label1} {{{prop1_str}}})"
            f"-[r:{rel_type}]->"
            f"(b:{label2} {{{prop2_str}}}) DELETE r"
        )

        # Merge parameters with prefixes to avoid collision
        parameters = {f"prop1_{k}": v for k, v in prop1.items()}
        parameters.update({f"prop2_{k}": v for k, v in prop2.items()})

        with self._driver.session() as session:
            return session.run(query, parameters)
        

    def delete_all_relationships(self, rel_type):
        """
        Delete all relationships of a specific type (label).

        Args:
            rel_type (str): The type of the relationship to delete.

        Raises:
            ValueError: If rel_type is not provided.
        """
        if not rel_type:
            raise ValueError("Relationship type (label) is required to delete relationships.")

        query = f"MATCH ()-[r:{rel_type}]->() DELETE r"
        print(f"Deleting all relations of '{rel_type}")
        with self._driver.session() as session:
            session.run(query)
      
    def node_exists(self, payload, match_keys=None):
        """
        Check if a node exists with the given label and properties.

        :param payload: dict with 'label' and full 'properties'
        :param match_keys: list of property keys to use for the MATCH query (e.g. ['instance_id'])
        """
        label = payload.get("label")
        properties = payload.get("properties", {})

        if not label or not properties:
            raise ValueError("Payload must contain 'label' and 'properties'.")

        # Use only match_keys to build the MATCH clause
        if not match_keys:
            # default to all keys (existing behavior, but risky for timestamps)
            match_keys = properties.keys()

        match_props = {k: properties[k] for k in match_keys if k in properties}
        prop_query = ", ".join(f"{k}: ${k}" for k in match_props)
        query = f"MATCH (n:{label} {{{prop_query}}}) RETURN n LIMIT 1"

        print(f"Executing Query: {query} with properties: {match_props}")

        with self._driver.session() as session:
            result = session.run(query, match_props).single()
            if result:
                print("Node exists.")
            else:
                print("No node found.")
            return result is not None

    def relationship_exists(self, payload, match_keys1=None, match_keys2=None):
        """
        Check if a relationship exists between two nodes using only selected property keys for matching.

        match_keys1 and match_keys2 allow controlling which keys to use for node1 and node2 matching.
        """
        label1 = payload.get("node1")
        label2 = payload.get("node2")
        rel_type = payload.get("relation")
        prop1 = payload.get("prop1", {})
        prop2 = payload.get("prop2", {})

        if not label1 or not label2 or not rel_type or not prop1 or not prop2:
            raise ValueError("Payload must contain 'node1', 'node2', 'relation', 'prop1', and 'prop2'.")

        if not match_keys1:
            match_keys1 = list(prop1.keys())
        if not match_keys2:
            match_keys2 = list(prop2.keys())

        prop1_filtered = {k: prop1[k] for k in match_keys1 if k in prop1}
        prop2_filtered = {k: prop2[k] for k in match_keys2 if k in prop2}

        prop1_query = ", ".join(f"{k}: $p1_{k}" for k in prop1_filtered)
        prop2_query = ", ".join(f"{k}: $p2_{k}" for k in prop2_filtered)

        query = (
            f"MATCH (a:{label1} {{{prop1_query}}})-[r:{rel_type}]->(b:{label2} {{{prop2_query}}}) "
            f"RETURN r LIMIT 1"
        )

        params = {f"p1_{k}": v for k, v in prop1_filtered.items()}
        params.update({f"p2_{k}": v for k, v in prop2_filtered.items()})

        print(f"Executing Relationship Query: {query} with params: {params}")

        with self._driver.session() as session:
            result = session.run(query, params).single()
            return result is not None

    def run_cypher_query(self, cypher_query, parameters=None):
        """
        Run a raw Cypher query and return results.

        Args:
            cypher_query (str): The Cypher query string.
            parameters (dict, optional): Parameters for the query.

        Returns:
            list: Query result.
        """
        parameters = parameters or {}
        with self._driver.session() as session:
            result = session.run(cypher_query, parameters)
            return [record.data() for record in result]
          
    def get_path_parts(self,file_url):
        if file_url.startswith("http"):
            parsed_url = urlparse(file_url)
            path_parts = parsed_url.path.split('/')[5:]  # user/repo/blob/branch/file/path...
        else:
            path_parts = file_url.split('/')
        return path_parts

    def upload_repo_data_to_neo4j(self, git_data):
        file_count = 1
        for item in git_data:
            file_url = item['file_url']
            file_name = file_url.split("/")[-1].split("?")[0]
            
            repo_name = item['repo']
            repo_url = item['repo_url']

            path_parts = self.get_path_parts(file_url)
            file_path = "/".join(path_parts[:-1])
            full_file_path = "/".join(path_parts)

            last_modified_time = item.get('last_modified_time')
            commit_message = item.get('commit_message')
            committer_name = item.get('committer_name')

            # Create Repository node
            repo_props = {
                "label": "Repository",
                "properties": {
                    "name": repo_name,
                    "url": repo_url
                }
            }
            self.create_node(repo_props)
            print(f"file {file_name} uploaded to Neo4j count: {file_count}")
            
            file_count+=1
            # Create Directory nodes
            current_dir_path = ""
            parent_label = "Repository"
            parent_props = {"name": repo_name}

            for part in path_parts[:-1]:
                current_dir_path = f"{current_dir_path}/{part}" if current_dir_path else part
                dir_props = {
                    "label": "Directory",
                    "properties": {
                        "name": part,
                        "full_path": current_dir_path
                    }
                }

                self.create_node(dir_props)
                self._driver.create_relationship({
                    "node1": parent_label,
                    "prop1": parent_props,
                    "relation": "HAS_DIRECTORY",
                    "node2": "Directory",
                    "prop2": {"name": part, "full_path": current_dir_path},
                    "rel_props": {"nested": True}
                })

                parent_label = "Directory"
                parent_props = {"name": part, "full_path": current_dir_path}

            # Create File node
            file_props = {
                "label": "File",
                "properties": {
                    "name": file_name,
                    "full_path": full_file_path,
                    "created_time": last_modified_time,
                    "modified_time": last_modified_time,
                    "commit_message": commit_message,
                    "committer": committer_name
                }
            }
            self.create_node(file_props)

            # File relationship
            if path_parts[:-1]:
                self.create_relationship({
                    "node1": parent_label,
                    "prop1": parent_props,
                    "relation": "HAS_FILE",
                    "node2": "File",
                    "prop2": {"name": file_name, "full_path": full_file_path},
                    "rel_props": {"defined_in_repo": repo_name}
                })
            else:
                self.create_relationship({
                    "node1": "Repository",
                    "prop1": {"name": repo_name},
                    "relation": "HAS_FILE",
                    "node2": "File",
                    "prop2": {"name": file_name, "full_path": full_file_path},
                    "rel_props": {"defined_in_repo": repo_name}
                })

            # Import nodes
            for imp in item['imports']:
                import_props = {
                    "label": "Import",
                    "properties": {
                        "name": imp
                    }
                }
                self.create_node(import_props)
                self.create_relationship({
                    "node1": "File",
                    "prop1": {"name": file_name, "full_path": full_file_path},
                    "relation": "IMPORTS",
                    "node2": "Import",
                    "prop2": {"name": imp},
                    "rel_props": {"from": file_name}
                })

            # Class and Method nodes
            for class_name, method_list in item['classes'].items():
                class_props = {
                    "label": "Class",
                    "properties": {
                        "name": class_name,
                        "file": file_name,
                        "full_path": full_file_path,
                        "created_time": last_modified_time,
                        "modified_time": last_modified_time,
                        "commit_message": commit_message,
                        "committer": committer_name
                    }
                }
                self.create_node(class_props)
                self.create_relationship({
                    "node1": "File",
                    "prop1": {"name": file_name, "full_path": full_file_path},
                    "relation": "HAS_CLASS",
                    "node2": "Class",
                    "prop2": {"name": class_name, "file": file_name, "full_path": full_file_path},
                    "rel_props": {"defined_in": file_name}
                })

                for method_name in method_list:
                    method_props = {
                        "label": "Method",
                        "properties": {
                            "name": method_name,
                            "class": class_name,
                            "file": file_name,
                            "full_path": full_file_path,
                            "created_time": last_modified_time,
                            "modified_time": last_modified_time,
                            "commit_message": commit_message,
                            "committer": committer_name
                        }
                    }
                    self.create_node(method_props)
                    self.create_relationship({
                        "node1": "Class",
                        "prop1": {"name": class_name, "file": file_name, "full_path": full_file_path},
                        "relation": "HAS_METHOD",
                        "node2": "Method",
                        "prop2": {"name": method_name, "class": class_name, "file": file_name, "full_path": full_file_path},
                        "rel_props": {"method_of": class_name}
                    })            
