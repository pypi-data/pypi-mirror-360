import os
import random
import string
from datetime import datetime
import json
import re

import pytz

from groclake.datalake import Datalake
from dotenv import load_dotenv
from groclake.modellake import Modellake
from pypdf import PdfReader

resumelake_mapping = {
    "properties": {
        "candidate_name": {"type": "text"},
        "candidate_email": {"type": "keyword"},
        "candidate_phone": {"type": "keyword"},
        "candidate_city": {"type": "text"},
        "candidate_state": {"type": "text"},
        "candidate_country": {"type": "text"},
        "linkedin_profile": {"type": "keyword"},
        "github_profile": {"type": "keyword"},
        "portfolio_website": {"type": "keyword"},
        "current_designation": {"type": "text"},
        "current_company": {"type": "text"},
        "current_company_industry": {"type": "text"},
        "current_company_size": {"type": "keyword"},
        "current_company_start_date": {"type": "date", "format": "yyyy-MM"},
        "previous_experience": {
            "type": "nested",
            "properties": {
                "designation": {"type": "text"},
                "company": {"type": "text"},
                "industry": {"type": "text"},
                "start_date": {"type": "date", "format": "yyyy-MM"},
                "end_date": {"type": "date", "format": "yyyy-MM"},
                "location": {"type": "text"}
            }
        },
        "total_work_experience": {"type": "keyword"},
        "education": {
            "type": "nested",
            "properties": {
                "degree": {"type": "text"},
                "major": {"type": "text"},
                "university": {"type": "text"},
                "graduation_year": {"type": "integer"}
            }
        },
        "skills": {"type": "keyword"},
        "certifications": {
            "type": "nested",
            "properties": {
                "name": {"type": "text"},
                "issuing_organization": {"type": "text"},
                "issue_date": {"type": "date", "format": "yyyy-MM"}
            }
        },
        "languages": {
            "type": "nested",
            "properties": {
                "language": {"type": "text"},
                "proficiency": {"type": "keyword"}
            }
        },
        "projects": {
            "type": "nested",
            "properties": {
                "title": {"type": "text"},
                "description": {"type": "text"},
                "technologies": {"type": "keyword"},
                "role": {"type": "text"}
            }
        },
        "publications": {
            "type": "nested",
            "properties": {
                "title": {"type": "text"},
                "publication": {"type": "text"},
                "year": {"type": "integer"}
            }
        },
        "awards": {
            "type": "nested",
            "properties": {
                "title": {"type": "text"},
                "organization": {"type": "text"},
                "year": {"type": "integer"}
            }
        },
        "references": {
            "type": "nested",
            "properties": {
                "name": {"type": "text"},
                "designation": {"type": "text"},
                "company": {"type": "text"},
                "email": {"type": "keyword"}
            }
        },
        "resume_summary": {
                    "type": "text",
                    "analyzer": "standard"
                },
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


class Resumelake:

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

    def save_resumelake_data_in_db(self, db_params: dict, table_name: str, commit=True) -> int:
        query = "insert into " + table_name + " (" + ",".join(db_params.keys()) + ") VALUES (" + ",".join(
            ['%s' for x in db_params.values()]) + ")"
        if commit:
            return mysql_connection.write(query, tuple(db_params.values()))
        else:
            return mysql_connection.write(query, tuple(db_params.values()))

    def create(self, resumelake_name=None):

        if not resumelake_name:
            return {"message": "Resumelake name is required. Please provide a valid name"}
        if not resumelake_name.lower().strip().isidentifier():
            return {'error': f'Invalid Resumelake name. Only alphanumeric characters and underscores are allowed.'}

        index_uuid = f"rs_{self.index_uuid}"
        if not index_uuid:
            index_uuid = self.generate_unique_id()

        existing_data = self.get_existing_index_uuid(index_uuid, 'resumelake')
        if existing_data and existing_data.get('entity_id', ''):
            self.index_uuid = existing_data.get('entity_id', '')
            print("esisting index", self.index_uuid)
            return {
                "message": "An entry with the same index_uuid already exists.",
                "index_uuid": existing_data.get('entity_id', ''),
                "resumelake_name": existing_data.get('name', '')
            }

        db_params = {
            "entity_id": index_uuid,
            "entity_type": 'resumelake',
            "created_at": self.get_current_datetime(),
            "groc_account_id": '',
            "name": resumelake_name
        }
        # try:
        response = es_connection.create_index(index_uuid, settings=None, mappings=resumelake_mapping)
        self.index_uuid = index_uuid
        print("resposne from es", response)

        # except Exception as es_error:
        # return {"message": "Elasticsearch error occurred while creating Resumelake.", "error": str(es_error)}
        try:
            self.save_resumelake_data_in_db(db_params, 'groclake_entity_master')
        except Exception as db_error:
            return {"message": "Database error occurred while saving Resumelake.", "error": str(db_error)}
        print("index in craete", self.index_uuid)

        return {
            "message": "Resumelake created successfully",
            "index_uuid": index_uuid,
            "resumelake_name": resumelake_name
        }

    # def push(self, job_url):
    #     try:
    #         print("index begining",self.index_uuid)
    #         # Ensure the file exists before processing
    #         if not os.path.exists(job_url):
    #             raise FileNotFoundError(f"File not found: {job_url}")
    #
    #         # Read PDF file
    #         reader = PdfReader(job_url)
    #         text = " ".join([page.extract_text() for page in reader.pages if page.extract_text()])
    #
    #         modellake = Modellake()
    #         query = text
    #
    #         chat_completion_request = {
    #             "groc_account_id": "c4ca4238a0b923820dcc509a6f75849b",
    #             "messages": [
    #                 {
    #                     "role": "system",
    #                     "content": "You are an advanced resume data extractor. Your task is to analyze the given resume content and return a **valid JSON response** that adheres strictly to the predefined structure. If a specific field is missing, return an empty string (`\"\"`) or an empty list (`[]`). Ensure data types match the expected format and maintain consistency."
    #                 },
    #                 {
    #                     "role": "user",
    #                     "content": "Extract details from the resume and return a JSON in the exact format below: {"
    #                             '"candidate_name": "", "candidate_email": "", "candidate_phone": "", "candidate_city": "", '
    #                             '"candidate_state": "", "candidate_country": "", "linkedin_profile": "", "github_profile": "", '
    #                             '"portfolio_website": "", "current_designation": "", "current_company": "", '
    #                             '"current_company_industry": "", "current_company_size": "", "current_company_start_date": "", '
    #                             '"previous_experience": [{"designation": "", "company": "", "industry": "", "start_date": "", '
    #                             '"end_date": "", "location": ""}], "total_work_experience": "", "education": [{"degree": "", '
    #                             '"major": "", "university": "", "graduation_year": ""}], "skills": [], "certifications": '
    #                             '[{"name": "", "issuing_organization": "", "issue_date": ""}], "languages": [{"language": "", '
    #                             '"proficiency": ""}], "projects": [{"title": "", "description": "", "technologies": [], '
    #                             '"role": ""}], "publications": [{"title": "", "publication": "", "year": ""}], "awards": '
    #                             '[{"title": "", "organization": "", "year": ""}], "references": [{"name": "", "designation": "", '
    #                             '"company": "", "email": ""}] }'
    #                 },
    #                 {
    #                     "role": "user",
    #                     "content": text
    #                 }
    #             ],
    #             "token_size": 4000
    #         }
    #         try:
    #             response = modellake.chat_complete(chat_completion_request)
    #             #print("ModelLake answer:", response)
    #
    #             if "answer" not in response:
    #                 raise ValueError("Invalid response from ModelLake API")
    #
    #
    #             body = response["answer"]
    #             #print("raw resonse",body)
    #             try:
    #                 bodyj = json.loads(body)
    #             except json.JSONDecodeError:
    #                 #print("Error: Received an invalid JSON response from ModelLake API")
    #                 return {"error": "Invalid JSON format received from ModelLake"}
    #
    #             # Step 4: Validate Parsed JSON
    #             if not isinstance(bodyj, dict):
    #                 #print("Error: Expected bodyj to be a dictionary, but got:", type(bodyj))
    #                 return {"error": "Invalid structured data format"}
    #
    #             #print("Parsed JSON:", bodyj)
    #
    #             # Ensure the response is valid JSON
    #             # bodyj = json.loads(body)
    #             # print("Type of bodyj:", type(bodyj))  # Should be <class 'dict'>
    #             # print("Content of bodyj:", bodyj)
    #
    #             if not self.index_uuid:
    #                 raise ValueError("Invalid index: resumelake_id is missing.")
    #             #print("resumelake_id:", self.resumelake_id)
    #             def format_date(date_str):
    #                 """
    #                 Formats date strings into ISO 8601 format (YYYY-MM-DDTHH:MM:SS).
    #                 - Converts YYYY-MM to YYYY-MM-DDT00:00:00
    #                 - Converts YYYY-MM-DD to YYYY-MM-DDT00:00:00
    #                 - Returns None for invalid or empty values
    #                 """
    #                 if not date_str or date_str.strip() == "":
    #                     return None  # Convert empty string to None
    #
    #                 try:
    #                     # Handle YYYY-MM format (e.g., "2020-06" → "2020-06-01T00:00:00")
    #                     if len(date_str) == 7 and "-" in date_str:
    #                         return datetime.strptime(date_str, "%Y-%m").strftime("%Y-%m-%dT00:00:00")
    #
    #                     # Handle YYYY-MM-DD format (e.g., "2021-08-15" → "2021-08-15T00:00:00")
    #                     if len(date_str) == 10 and "-" in date_str:
    #                         return datetime.strptime(date_str, "%Y-%m-%d").strftime("%Y-%m-%dT00:00:00")
    #
    #                 except ValueError:
    #                     return None  # Return None if parsing fails
    #
    #                 return None
    #             # def format_date(date_str):
    #             #     if date_str:
    #             #         try:
    #             #             return datetime.strptime(date_str, "%Y-%m-%d").date()  # Ensures proper date format
    #             #         except ValueError:
    #             #             print(f"Warning: Invalid date format for {date_str}")
    #             #     return None
    #
    #             if "current_company_start_date" in bodyj:
    #                 bodyj["current_company_start_date"] = format_date(bodyj["current_company_start_date"])
    #
    #             if "previous_experience" in bodyj:
    #                 for exp in bodyj["previous_experience"]:
    #                     exp["start_date"] = format_date(exp.get("start_date", ""))
    #                     exp["end_date"] = format_date(exp.get("end_date", ""))
    #             if "education" in bodyj:
    #                 for edu in bodyj["education"]:
    #                     if "graduation_year" in edu:
    #                         if isinstance(edu["graduation_year"], str) and edu["graduation_year"].lower() == "present":
    #                             edu["graduation_year"] = None  # Change 'present' to None or use a default integer like 9999
    #                         elif not isinstance(edu["graduation_year"], int):
    #                             try:
    #                                 edu["graduation_year"] = int(edu["graduation_year"])  # Convert to integer if possible
    #                             except ValueError:
    #                                 edu["graduation_year"] = None
    #             if "certifications" in bodyj:
    #                 for cert in bodyj["certifications"]:
    #                     if "issue_date" in cert:
    #                         cert["issue_date"] = format_date(cert["issue_date"])
    #             if "publications" in bodyj:
    #                 for pub in bodyj["publications"]:
    #                     if "year" in pub and isinstance(pub["year"], str) and pub["year"].isdigit():
    #                         pub["year"] = int(pub["year"])
    #                     elif not isinstance(pub["year"], int):
    #                         pub["year"] = None  # Set invalid values to None
    #
    #             # Format award years (Ensure integer)
    #             if "awards" in bodyj:
    #                 for award in bodyj["awards"]:
    #                     if "year" in award and isinstance(award["year"], str) and award["year"].isdigit():
    #                         award["year"] = int(award["year"])
    #                     elif not isinstance(award["year"], int):
    #                         award["year"] = None
    #
    #             index = self.index_uuid
    #             print("index",index)
    #
    #             # write_query = {
    #             #     "index": self.resumelake_id,
    #             #     "body": bodyj
    #             # }
    #
    #             try:
    #                 write_response = es_connection.write(query={'index': index, 'body': bodyj})
    #                 #print("Write response:", write_response)
    #             except Exception as e:
    #                 #print(f"Error writing to Elasticsearch: {e}")
    #                 return {"error": "Failed to push data to Elasticsearch", "details": str(e)}
    #
    #             return {"message": "Resume data pushed successfully", "response": write_response}
    #
    #         except json.JSONDecodeError:
    #             #print("Error: Received an invalid or incomplete JSON response.")
    #             return {"error": "Invalid JSON format received from ModelLake"}
    #
    #     except FileNotFoundError as e:
    #         return {"error": "PDF file not found"}
    #
    #     except PermissionError:
    #         return {"error": "Permission denied while accessing the file"}
    #
    #     except ValueError as e:
    #         return {"error": "Error in extracting structured data"}
    #
    #     except Exception as e:
    #
    #         #print("Unexpected error occurred:", traceback.format_exc())  # Print full error trace
    #         return {"error": "An unexpected error occurred", "details": str(e)}
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

            chat_completion_request = {
                "groc_account_id": "c4ca4238a0b923820dcc509a6f75849b",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an advanced resume data extractor. Your task is to analyze the given resume content and return a **valid JSON response** that adheres strictly to the predefined structure. If a specific field is missing, return an empty string (`\"\"`) or an empty list (`[]`). Ensure data types match the expected format and maintain consistency."
                    },
                    {
                        "role": "user",
                        "content": "Extract details from the resume and return a JSON in the exact format below: {"
                                   '"candidate_name": "", "candidate_email": "", "candidate_phone": "", "candidate_city": "", '
                                   '"candidate_state": "", "candidate_country": "", "linkedin_profile": "", "github_profile": "", '
                                   '"portfolio_website": "", "current_designation": "", "current_company": "", '
                                   '"current_company_industry": "", "current_company_size": "", "current_company_start_date": "", '
                                   '"previous_experience": [{"designation": "", "company": "", "industry": "", "start_date": "", '
                                   '"end_date": "", "location": ""}], "total_work_experience": "", "education": [{"degree": "", '
                                   '"major": "", "university": "", "graduation_year": ""}], "skills": [], "certifications": '
                                   '[{"name": "", "issuing_organization": "", "issue_date": ""}], "languages": [{"language": "", '
                                   '"proficiency": ""}], "projects": [{"title": "", "description": "", "technologies": [], '
                                   '"role": ""}], "publications": [{"title": "", "publication": "", "year": ""}], "awards": '
                                   '[{"title": "", "organization": "", "year": ""}], "references": [{"name": "", "designation": "", '
                                   '"company": "", "email": ""}] }'
                    },
                    {
                        "role": "user",
                        "content": text
                    }
                ],
                "token_size": 4000
            }
            try:
                response = modellake.chat_complete(chat_completion_request)
                # print("ModelLake answer:", response)

                if "answer" not in response:
                    raise ValueError("Invalid response from ModelLake API")

                body = response["answer"]
                # print("raw resonse",body)
                try:
                    bodyj = json.loads(body)
                except json.JSONDecodeError:
                    # print("Error: Received an invalid JSON response from ModelLake API")
                    return {"error": "Invalid JSON format received from ModelLake"}

                # Step 4: Validate Parsed JSON
                if not isinstance(bodyj, dict):
                    # print("Error: Expected bodyj to be a dictionary, but got:", type(bodyj))
                    return {"error": "Invalid structured data format"}
                summary_request = {
                    "groc_account_id": "c4ca4238a0b923820dcc509a6f75849b",
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a professional resume summarizer. Create a concise summary highlighting key qualifications, experience, and skills. Focus on the most relevant and impressive aspects. Keep it under 250 words."
                        },
                        {
                            "role": "user",
                            "content": text
                        }
                    ],
                    "token_size": 4000
                }

                try:
                    summary_response = modellake.chat_complete(summary_request)
                    if "answer" in summary_response:
                        bodyj["resume_summary"] = summary_response["answer"]
                    else:
                        bodyj["resume_summary"] = ""
                except Exception as e:
                    print(f"Error generating summary: {str(e)}")
                    bodyj["resume_summary"] = ""

                # print("Parsed JSON:", bodyj)

                # Ensure the response is valid JSON
                # bodyj = json.loads(body)
                # print("Type of bodyj:", type(bodyj))  # Should be <class 'dict'>
                # print("Content of bodyj:", bodyj)

                if not self.index_uuid:
                    raise ValueError("Invalid index: resumelake_id is missing.")

                # print("resumelake_id:", self.resumelake_id)
                def format_date(date_str):
                    """
                    Formats date strings into ISO 8601 format (YYYY-MM-DDTHH:MM:SS).
                    - Converts YYYY-MM to YYYY-MM-DDT00:00:00
                    - Converts YYYY-MM-DD to YYYY-MM-DDT00:00:00
                    - Returns None for invalid or empty values
                    """
                    if not date_str or date_str.strip() == "":
                        return None  # Convert empty string to None

                    try:
                        # Handle YYYY-MM format (e.g., "2020-06" → "2020-06-01T00:00:00")
                        if len(date_str) == 7 and "-" in date_str:
                            return datetime.strptime(date_str, "%Y-%m").strftime("%Y-%m-%dT00:00:00")

                        # Handle YYYY-MM-DD format (e.g., "2021-08-15" → "2021-08-15T00:00:00")
                        if len(date_str) == 10 and "-" in date_str:
                            return datetime.strptime(date_str, "%Y-%m-%d").strftime("%Y-%m-%dT00:00:00")

                    except ValueError:
                        return None  # Return None if parsing fails

                    return None

                # def format_date(date_str):
                #     if date_str:
                #         try:
                #             return datetime.strptime(date_str, "%Y-%m-%d").date()  # Ensures proper date format
                #         except ValueError:
                #             print(f"Warning: Invalid date format for {date_str}")
                #     return None

                if "current_company_start_date" in bodyj:
                    bodyj["current_company_start_date"] = format_date(bodyj["current_company_start_date"])

                if "previous_experience" in bodyj:
                    for exp in bodyj["previous_experience"]:
                        exp["start_date"] = format_date(exp.get("start_date", ""))
                        exp["end_date"] = format_date(exp.get("end_date", ""))
                if "education" in bodyj:
                    for edu in bodyj["education"]:
                        if "graduation_year" in edu:
                            if isinstance(edu["graduation_year"], str) and edu["graduation_year"].lower() == "present":
                                edu[
                                    "graduation_year"] = None  # Change 'present' to None or use a default integer like 9999
                            elif not isinstance(edu["graduation_year"], int):
                                try:
                                    edu["graduation_year"] = int(
                                        edu["graduation_year"])  # Convert to integer if possible
                                except ValueError:
                                    edu["graduation_year"] = None
                if "certifications" in bodyj:
                    for cert in bodyj["certifications"]:
                        if "issue_date" in cert:
                            cert["issue_date"] = format_date(cert["issue_date"])
                if "publications" in bodyj:
                    for pub in bodyj["publications"]:
                        if "year" in pub and isinstance(pub["year"], str) and pub["year"].isdigit():
                            pub["year"] = int(pub["year"])
                        elif not isinstance(pub["year"], int):
                            pub["year"] = None  # Set invalid values to None

                # Format award years (Ensure integer)
                if "awards" in bodyj:
                    for award in bodyj["awards"]:
                        if "year" in award and isinstance(award["year"], str) and award["year"].isdigit():
                            award["year"] = int(award["year"])
                        elif not isinstance(award["year"], int):
                            award["year"] = None

                index = self.index_uuid
                print("index", index)

                # write_query = {
                #     "index": self.resumelake_id,
                #     "body": bodyj
                # }

                try:
                    write_response = es_connection.write(query={'index': index, 'body': bodyj})
                    # print("Write response:", write_response)
                except Exception as e:
                    # print(f"Error writing to Elasticsearch: {e}")
                    return {"error": "Failed to push data to Elasticsearch", "details": str(e)}

                return {"message": "Resume data pushed successfully", "response": write_response}

            except json.JSONDecodeError:
                # print("Error: Received an invalid or incomplete JSON response.")
                return {"error": "Invalid JSON format received from ModelLake"}

        except FileNotFoundError as e:
            return {"error": "PDF file not found"}

        except PermissionError:
            return {"error": "Permission denied while accessing the file"}

        except ValueError as e:
            return {"error": "Error in extracting structured data"}

        except Exception as e:

            # print("Unexpected error occurred:", traceback.format_exc())  # Print full error trace
            return {"error": "An unexpected error occurred", "details": str(e)}

    def search(self, index, payload):
        try:
            read_response = es_connection.search(index=index, body=payload)
            return read_response
        except Exception as e:
            # print(f"Search error: {e}")  # Debugging output
            return {"error": "Failed to retrieve search results", "details": str(e)}

