import os
import random
import string
from datetime import datetime
import pytz
import base64
import os
from io import BytesIO
import random
import string
import logging
from pypdf import PdfReader
import random
import string
from elasticsearch import Elasticsearch
from groclake.datalake import Datalake
from dotenv import load_dotenv
from groclake.modellake import Modellake

joblake_mapping = {
    "properties": {
        "job_title": {"type": "text"},
        "job_department": {"type": "text"},
        "job_location": {
            "properties": {
                "city": {"type": "text"},
                "state": {"type": "text"},
                "country": {"type": "text"},
                "remote": {"type": "boolean"}
            }
        },
        "company_name": {"type": "text"},
        "company_industry": {"type": "text"},
        "company_size": {"type": "keyword"},
        "employment_type": {"type": "keyword"},
        "experience_required": {"type": "text"},
        "education_required": {
            "type": "nested",
            "properties": {
                "degree": {"type": "keyword"},
                "major": {"type": "text"},
                "preferred_university": {"type": "text"}
            }
        },
        "skills_required": {"type": "keyword"},
        "preferred_certifications": {
            "type": "nested",
            "properties": {
                "name": {"type": "text"},
                "issuing_organization": {"type": "text"}
            }
        },
        "job_responsibilities": {"type": "text"},
        "preferred_experience": {
            "type": "nested",
            "properties": {
                "designation": {"type": "text"},
                "industry": {"type": "text"},
                "company_type": {"type": "text"},
                "min_years": {"type": "integer"},
                "max_years": {"type": "integer"}
            }
        },
        "languages_required": {
            "type": "nested",
            "properties": {
                "language": {"type": "text"},
                "proficiency": {"type": "keyword"}
            }
        },
        "technologies_used": {"type": "keyword"},
        "compensation": {
            "properties": {
                "salary_range": {
                    "properties": {
                        "min": {"type": "keyword"},
                        "max": {"type": "keyword"}
                    }
                },
                "equity": {"type": "boolean"},
                "bonuses": {"type": "boolean"}
            }
        },
        "benefits": {"type": "keyword"},
        "company_culture": {"type": "text"},
        "recruiter_contact": {
            "properties": {
                "name": {"type": "text"},
                "email": {"type": "keyword"},
                "phone": {"type": "keyword"}
            }
        },
        "application_deadline": {"type": "date", "format": "yyyy-MM-dd"}
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
        'port': int(os.getenv("MYSQL_PORT")),
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


class Joblake:

    def __init__(self, index_uuid=None):
        if not index_uuid:
            raise ValueError('Missing required index_uuid. Ensure you pass a valid index UUID when initializing the class.')
        self.index_uuid = index_uuid
        index_uuid =f"jb_{self.index_uuid}"

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

    def save_joblake_data_in_db(self, db_params: dict, table_name: str, commit=True) -> int:
        query = "insert into " + table_name + " (" + ",".join(db_params.keys()) + ") VALUES (" + ",".join(
            ['%s' for x in db_params.values()]) + ")"
        if commit:
            return mysql_connection.write(query, tuple(db_params.values()))
        else:
            return mysql_connection.write(query, tuple(db_params.values()))

    def create(self, joblake_name=None):

        if joblake_name:
            joblake_name = joblake_name

        if not joblake_name:
            return {"message": "Joblake name is required. Please provide a valid joblake name"}
        if not joblake_name.lower().strip().isidentifier():
            return {'error': f'Invalid Joblake name. Only alphanumeric characters and underscores are allowed.'}

        if not self.index_uuid:
            self.index_uuid = self.generate_unique_id()

        index_uuid =f"jb_{self.index_uuid}"

        existing_data = self.get_existing_index_uuid(index_uuid, 'joblake')
        if existing_data and existing_data.get('entity_id', ''):
            self.index_uuid=existing_data.get('entity_id','')
            return {
                "message": "An entry with the same index_uuid already exists.",
                "index_uuid": existing_data.get('entity_id',''),
                "joblake_name": existing_data.get('name', '')
            }

        db_params = {
            "entity_id": index_uuid,
            "entity_type": 'joblake',
            "created_at": self.get_current_datetime(),
            "groc_account_id": '',
            "name": joblake_name
        }
        try:
            response = es_connection.create_index(index_uuid, settings=None, mappings=joblake_mapping)
            self.index_uuid=index_uuid
        except Exception as es_error:
            return {"message": "Elasticsearch error occurred while creating Joblake.", "error": str(es_error)}
        try:
            self.save_joblake_data_in_db(db_params, 'groclake_entity_master')
        except Exception as db_error:
            return {"message": "Database error occurred while saving Joblake.", "error": str(db_error)}
        return {
            "message": "JobLake created successfully",
            "index_uuid": index_uuid,
            "response":response,
            "joblake_name":joblake_name
        }
    
    def push(self, input_data):
        try:
            text = ""

            # Check if input is a base64 string
            if isinstance(input_data, bytes):
                import io
                from PyPDF2 import PdfReader

                reader = PdfReader(io.BytesIO(input_data))
                text = " ".join([page.extract_text() for page in reader.pages if page.extract_text()])

                # Handle file path (not likely in your use case but kept for completeness)
            elif isinstance(input_data, str) and os.path.exists(input_data):
                from PyPDF2 import PdfReader

                reader = PdfReader(input_data)
                text = " ".join([page.extract_text() for page in reader.pages if page.extract_text()])

                # Handle already extracted text
            elif isinstance(input_data, str):
                text = input_data

            else:
                raise ValueError("Unsupported input format")

                # Validate extracted text
            if not text:
                return {"error": "No text could be extracted from the provided resume"}
        
            modellake = Modellake()
            query = text
            chat_completion_request={
                "groc_account_id": "e60ddfb6ee3b1b48d70acc13d5be99e3",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a structured text analyzer. Your task is to extract key details from the given content and return a *valid JSON response*. Ensure the JSON follows the correct structure. If any data is missing, return an empty string."
                    },
                    {
                        "role": "user",
                        "content": "Below is the structured JSON response format. Please strictly follow this format:\n\n"
                    },
                    {
                        "role": "user",
                        "content": "{\n"
                            "    \"job_title\": \"\",\n"
                            "    \"job_department\": \"\",\n"
                            "    \"job_location\": {\n"
                            "        \"city\": \"\",\n"
                            "        \"state\": \"\",\n"
                            "        \"country\": \"\",\n"
                            "        \"remote\": false\n"
                            "    },\n"
                            "    \"company_name\": \"\",\n"
                            "    \"company_industry\": \"\",\n"
                            "    \"company_size\": \"\",\n"
                            "    \"employment_type\": \"\",\n"
                            "    \"experience_required\": \"\",\n"
                            "    \"education_required\": [\n"
                            "        {\n"
                            "            \"degree\": \"\",\n"
                            "            \"major\": \"\",\n"
                            "            \"preferred_university\": \"\"\n"
                            "        }\n"
                            "    ],\n"
                            "    \"skills_required\": [],\n"
                            "    \"preferred_certifications\": [\n"
                            "        {\n"
                            "            \"name\": \"\",\n"
                            "            \"issuing_organization\": \"\"\n"
                            "        }\n"
                            "    ],\n"
                            "    \"job_responsibilities\": [],\n"
                            "    \"preferred_experience\": [\n"
                            "        {\n"
                            "            \"designation\": \"\",\n"
                            "            \"industry\": \"\",\n"
                            "            \"company_type\": \"\",\n"
                            "            \"min_years\": \"\",\n"
                            "            \"max_years\": \"\"\n"
                            "        }\n"
                            "    ],\n"
                            "    \"languages_required\": [\n"
                            "        {\n"
                            "            \"language\": \"\",\n"
                            "            \"proficiency\": \"\"\n"
                            "        }\n"
                            "    ],\n"
                            "    \"technologies_used\": [],\n"
                            "    \"compensation\": {\n"
                            "        \"salary_range\": {\n"
                            "            \"min\": \"\",\n"
                            "            \"max\": \"\"\n"
                            "        },\n"
                            "        \"equity\": false,\n"
                            "        \"bonuses\": false,\n"
                            "        \"salary_currency\": \"\"\n"
                            "    },\n"
                            "    \"benefits\": [],\n"
                            "    \"company_culture\": [],\n"
                            "    \"recruiter_contact\": {\n"
                            "        \"name\": \"\",\n"
                            "        \"email\": \"\",\n"
                            "        \"phone\": \"\"\n"
                            "    },\n"
                            "    \"application_deadline\": \"\"\n"
                            "}"
                    },
                    {
                        "role": "user",
                        "content": query
                    }
                ],
                "token_size": 4000
            }


            import json
            # Call Modellake API
            response = modellake.chat_complete(chat_completion_request)

            if isinstance(response, str):  # If it's a JSON string, convert it
                response = json.loads(response)

            if not isinstance(response, dict) or "answer" not in response:
                raise ValueError("Invalid response format from Modellake API")

            import json
            import logging

            answer = response.get("answer", "")

            print(f"Raw Response: {repr(answer)}")  # Check what `answer` contains

            if answer.strip():  # Ensures answer is not empty or just whitespace
                try:
                    body = json.loads(answer) if isinstance(answer, str) else answer
                except json.JSONDecodeError as e:
                    logging.error(f"JSON decoding error: {e} - Raw input: {repr(answer)}")
                    body = {}  # Set a default value to avoid crashes
            else:
                logging.error("Response answer is empty or invalid")
                body = {}  # Default empty dictionary


            # Validate application_deadline format
            if "application_deadline" in body and not body["application_deadline"]:
                body["application_deadline"] = None  # Set to None if empty

            # Write data to Elasticsearch
            index=self.index_uuid
            write_query = {
                "index": index,
                "body": body
            }
            write_response = es_connection.write(write_query)

            logging.info("Data successfully written to Elasticsearch.")
            return {"message": "Job data pushed successfully", "response": write_response}

        except FileNotFoundError as e:
            logging.error(f"File error: {str(e)}")
            return {"error": "PDF file not found"}
        
        except PermissionError:
            logging.error("Permission error: Unable to read the PDF file.")
            return {"error": "Permission denied while accessing the file"}

        # except PdfReadError:
        #     logging.error("PDF Read error: The file might be corrupted or not a valid PDF.")
        #     return {"error": "Invalid or corrupted PDF file"}

        except ValueError as e:
            logging.error(f"Data processing error: {str(e)}")
            return {"error": "Error in extracting structured data"}

        except Exception as e:
            logging.error(f"Unexpected error: {str(e)}")
            return {"error": "An unexpected error occurred"}

    def search(self, payload):

        try:
            read_response = es_connection.search(index=self.index_uuid,body=payload)
            return read_response
        except Exception as e:
            logging.error(f"Search error in Elasticsearch: {str(e)}")
            return {"error": "Failed to retrieve search results"}
