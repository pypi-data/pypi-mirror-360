from .pipeline import Pipeline
import threading

# from ..utillake import Utillake

# from ..utillake import Utillake
from notion_client import Client

import PyPDF2
from markdownify import markdownify as md
import unicodedata
from io import BytesIO
import requests
from docx import Document
import os

from ..config import BASE_URL

import re



class Datalake:
    def __init__(self):
        self.pipelines = {}
        #self.utillake=Utillake()
        self.datalake_id = None
        self.params = {}

    @staticmethod
    def _get_groc_api_headers():
        return {'GROCLAKE-API-KEY': os.getenv('GROCLAKE_API_KEY')}

    @staticmethod
    def _add_groc_account_id(payload):
        if payload:
            return payload.update({'groc_account_id': os.getenv('GROCLAKE_ACCOUNT_ID')})

    def call_api(self, endpoint, payload, lake_obj=None):
        headers = self._get_groc_api_headers()
        url = f"{BASE_URL}{endpoint}"
        if lake_obj:
            lake_ids = ['cataloglake_id', 'vectorlake_id', 'datalake_id', 'modellake_id']

            for lake_id in lake_ids:
                if hasattr(lake_obj, lake_id) and getattr(lake_obj, lake_id):
                    payload[lake_id] = getattr(lake_obj, lake_id)

        self._add_groc_account_id(payload)
        if not endpoint:
            raise ValueError("Invalid API call.")
        response = requests.post(url, json=payload, headers=headers, timeout=90)
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=90)
            response_data = response.json()
            if response.status_code == 200 and 'api_action_status' in response_data:
                response_data.pop('api_action_status')
            return response_data if response.status_code == 200 else {}
        except requests.RequestException as e:
            return {}

    def create_pipeline(self, name):
        if name in self.pipelines:
            raise ValueError(f"Pipeline with name '{name}' already exists.")
        pipeline = Pipeline(name)
        self.pipelines[name] = pipeline
        return pipeline

    def get_pipeline_by_name(self, name):
        return self.pipelines.get(name)

    def execute_all(self):
        threads = []
        for pipeline in self.pipelines.values():
            thread = threading.Thread(target=pipeline.execute)
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()


    def create(self, payload=None):
        api_endpoint = '/datalake/create'
        if not payload:
            payload = {'groc_account_id': os.getenv('GROCLAKE_ACCOUNT_ID')}

        response = self.call_api(api_endpoint, payload, self)
        if response and 'datalake_id' in response:
            self.datalake_id = response['datalake_id']

        return response

    def document_fetch(self, payload):
        api_endpoint = '/datalake/document/fetch'
        return self.call_api(api_endpoint, payload, self)

    def document_push(self, payload):
        api_endpoint = '/datalake/document/push'
        return self.call_api(api_endpoint, payload, self)

    def generate_markdown(self, payload):
        """
        Transforms a document (PDF from URL, PDF from local file, or DOCX) into markdown content.

        Args:
            payload (dict): Contains document data, source, and type.

        Returns:
            str: Markdown content extracted from the document.
        """
        file = payload["document_data"]
        document_type = payload["document_type"]
        document_source = payload["document_source"]

        # **Handle URL Documents**
        if document_source == "url" and document_type == "pdf":
            response = requests.get(file)
            if response.status_code != 200:
                raise ValueError(f"Failed to fetch document from URL: {file}")

            content_type = response.headers.get("Content-Type", "")
            if "pdf" in content_type.lower() or file.lower().endswith(".pdf") or self.is_pdf(response.content):
                pdf_reader = PyPDF2.PdfReader(BytesIO(response.content))
                text_content = "".join(page.extract_text() for page in pdf_reader.pages if page.extract_text())

                # Normalize and convert to Markdown
                normalized_text = unicodedata.normalize("NFKD", text_content)
                return md(normalized_text)
            else:
                raise ValueError("Unsupported file type. Only PDFs are supported.")

        # **Handle Local Files**
        elif document_source == "local_storage":
            if not os.path.exists(file):
                raise ValueError(f"Local file not found: {file}")

            if document_type == "pdf" and file.lower().endswith(".pdf"):
                with open(file, "rb") as pdf_file:
                    pdf_reader = PyPDF2.PdfReader(pdf_file)
                    text_content = "".join(page.extract_text() for page in pdf_reader.pages if page.extract_text())

                normalized_text = unicodedata.normalize("NFKD", text_content)
                return md(normalized_text)

            elif document_type == "docx" and file.lower().endswith(".docx"):
                doc = Document(file)
                text_content = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])

                normalized_text = unicodedata.normalize("NFKD", text_content)
                return md(normalized_text)

            else:
                raise ValueError("Unsupported local file type. Only PDFs and DOCX are supported.")

        else:
            raise ValueError("Unsupported document source. Use 'url' or 'local_file'.")

    def extract_google_doc(self,url: str) -> str:
        """
        Extracts the Google Doc ID from a given Google Docs URL.
        
        Args:
            url (str): The URL of the Google Document.
            
        Returns:
            str: The extracted document ID if found; otherwise, returns None.
        """
        # The pattern looks for '/d/' followed by the document id which usually consists of alphanumeric characters, hyphens, or underscores.
        pattern = r"/d/([a-zA-Z0-9-_]+)"
        match = re.search(pattern, url)
        
        if match:
            DOC_ID = match.group(1)
            DOC_URL = f"https://docs.google.com/document/d/{DOC_ID}/export?format=txt"
            response = requests.get(DOC_URL)
            if response.status_code == 200:
                return response.text
            else:
                print("Error fetching document")
                return "Error fetching document"
        else:
            return None

    def extract_google_sheet(self,url: str) -> str:
    # Replace 'YOUR_SHEET_ID' with your actual Google Sheet ID
        DOC_ID = self.extract_google_doc_ID(url)
        SHEET_URL = f"https://docs.google.com/spreadsheets/d/{DOC_ID}/export?format=csv"

        response = requests.get(SHEET_URL)

        if response.status_code == 200:
            return response.text
        else:
            print("Error fetching sheet")
            return None
        
    def extract_google_doc_ID(self,url: str) -> str:
        """
        Extracts the Google Doc ID from a given Google Docs URL.
        
        Args:
            url (str): The URL of the Google Document.
            
        Returns:
            str: The extracted document ID if found; otherwise, returns None.
        """
        # The pattern looks for '/d/' followed by the document id which usually consists of alphanumeric characters, hyphens, or underscores.
        pattern = r"/d/([a-zA-Z0-9-_]+)"
        match = re.search(pattern, url)
        
        if match:
            DOC_ID = match.group(1)
            return DOC_ID
        else:
            return None


    def is_pdf(self, file_bytes):
        """
        Checks if the given file bytes represent a valid PDF.

        Args:
            file_bytes (bytes): The file content.

        Returns:
            bool: True if it's a valid PDF, False otherwise.
        """
        try:
            pdf_reader = PyPDF2.PdfReader(BytesIO(file_bytes))
            return True
        except PyPDF2.errors.PdfReadError:
            return False
    def extract_notion_id(self,url):
            """Extracts the Notion ID from the given URL."""
            match = re.search(r"([a-f0-9]{32})", url)
            return match.group(1) if match else None
    
    
    def parse_block_to_markdown(self,block):
            """Converts a Notion block into Markdown format."""
            block_type = block["type"]
            text_content = ""

            if "rich_text" in block[block_type]:
                text_content = "".join([t["plain_text"] for t in block[block_type]["rich_text"]])

            if block_type == "heading_1":
                return f"# {text_content}\n"
            elif block_type == "heading_2":
                return f"## {text_content}\n"
            elif block_type == "heading_3":
                return f"### {text_content}\n"
            elif block_type == "paragraph":
                return f"{text_content}\n"
            elif block_type == "bulleted_list_item":
                return f"- {text_content}\n"
            elif block_type == "numbered_list_item":
                return f"1. {text_content}\n"
            elif block_type == "quote":
                return f"> {text_content}\n"
            elif block_type == "to_do":
                checked = "☑" if block["to_do"]["checked"] else "☐"
                return f"- [ {checked} ] {text_content}\n"
            elif block_type == "code":
                language = block["code"].get("language", "plaintext")
                return f"```{language}\n{text_content}\n```\n"
            return text_content

    # Initialize Notion client
    def parse_page_content(self,page_id):
            """Fetches and converts a Notion page's content into Markdown."""
            try:
                blocks = self.notion.blocks.children.list(page_id)["results"]
                markdown_content = ""
                for block in blocks:
                    markdown_content += self.parse_block_to_markdown(block) + "\n"

                return markdown_content.strip()
            except Exception as e:
                print(f"Error retrieving page {page_id}: {e}")
                return ""

    def parse_database_to_markdown(self,database_data):
            """Converts a Notion database into a Markdown format including its pages."""
            markdown_content = ""

            if not database_data or "results" not in database_data:
                return "No database data found."

            # Extract database properties (columns)
            first_item = database_data["results"][0]
            # filename = "test_text.txt"
            columns = list(first_item["properties"].keys())

            # # Create table headers
            # markdown_content += "| " + " | ".join(columns) + " |\n"
            # markdown_content += "| " + " | ".join(["---"] * len(columns)) + " |\n"

            # Iterate through database rows (each row is a page)
            for item in database_data["results"]:
                row = []
                page_id = item["id"]  # This is the Notion Page ID inside the database
                page_title = "Untitled"
                for col in columns:
                    prop = item["properties"][col]
                    if "title" in prop and prop["title"]:
                        page_title = prop["title"][0]["plain_text"]
                        row.append(page_title)
                    elif "rich_text" in prop and prop["rich_text"]:
                        row.append(prop["rich_text"][0]["plain_text"])
                    elif "number" in prop and prop["number"] is not None:
                        row.append(str(prop["number"]))
                    elif "checkbox" in prop:
                        row.append("☑" if prop["checkbox"] else "☐")
                    elif "date" in prop and prop["date"]:
                        row.append(prop["date"]["start"])
                    elif "select" in prop and prop["select"]:
                        row.append(prop["select"]["name"])
                    elif "multi_select" in prop and prop["multi_select"]:
                        row.append(", ".join([x["name"] for x in prop["multi_select"]]))
                    else:
                        row.append("")

                # markdown_content += "| " + " | ".join(row) + " |\n"

                # Fetch and append each page’s content below the table
                markdown_content += f"\n### Page Content: {page_title}\n"
                
                markdown_content += self.parse_page_content(page_id)
                markdown_content += "\n---\n"

            return markdown_content
             
    def fetch_notion_data(self,url):
        """Fetches data from a Notion page or database and converts it to Markdown."""
        auth_ID = os.getenv("NOTION_AUTH_ID")
        if not auth_ID:
            raise ValueError("Notion auth ID is missing.")
        self.notion = Client(auth=auth_ID)
        notion_id = self.extract_notion_id(url)
        markdown_content = ""

        # Try fetching as a Database
        try:
            database_data = self.notion.databases.query(database_id=notion_id)
            markdown_content = self.parse_database_to_markdown(database_data)
            print("notion Database data retrieved successfully!")
            return markdown_content
        except Exception as e:
            if e.code != "object_not_found":
                print("Error retrieving database:", e)

        # Try fetching as a Page
        try:
            markdown_content = self.parse_page_content(notion_id)
            print("notion Page data retrieved successfully!")
            return markdown_content
        except Exception as e:
            print("Error retrieving page:", e)
            return None

