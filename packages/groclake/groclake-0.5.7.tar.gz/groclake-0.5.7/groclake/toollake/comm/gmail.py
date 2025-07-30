from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import base64
import os
import json
from typing import Dict, Any
class Gmail:
    SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

    def __init__(self, tool_config: Dict[str, Any]):
        self.tool_config = tool_config
        self.credentials_file = tool_config.get("credentials_file")
        self.token_file = tool_config.get("token_file")
        self.service = self.authenticate_gmail()

    def authenticate_gmail(self):
        """Authenticate and return the Gmail service."""
        creds = None

        if os.path.exists(self.token_file):
            creds = Credentials.from_authorized_user_file(self.token_file, self.SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self.credentials_file, self.SCOPES)
                creds = flow.run_local_server(port=0, access_type='offline', prompt='consent')

            with open(self.token_file, "w") as token_file:
                token_file.write(creds.to_json())

        return build("gmail", "v1", credentials=creds)

    def get_emails(self, max_results=5):
        """Fetch recent emails and return them as a JSON object."""
        results = self.service.users().messages().list(userId="me", maxResults=max_results).execute()
        messages = results.get("messages", [])

        email_list = []

        for msg in messages:
            msg_id = msg["id"]
            msg_data = self.service.users().messages().get(userId="me", id=msg_id).execute()
            
            headers = msg_data["payload"]["headers"]
            email_info = {
                "To": "Unknown",
                "From": "Unknown",
                "Subject": "No Subject",
                "Body": "No Content"
            }

            # Extract 'To', 'From', and 'Subject' from headers
            for header in headers:
                if header["name"] == "To":
                    email_info["To"] = header["value"]
                elif header["name"] == "From":
                    email_info["From"] = header["value"]
                elif header["name"] == "Subject":
                    email_info["Subject"] = header["value"]

            # Extract email body
            if "parts" in msg_data["payload"]:
                for part in msg_data["payload"]["parts"]:
                    if part["mimeType"] == "text/plain" and "data" in part["body"]:
                        email_info["Body"] = base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8")
                        break
            elif "body" in msg_data["payload"] and "data" in msg_data["payload"]["body"]:
                email_info["Body"] = base64.urlsafe_b64decode(msg_data["payload"]["body"]["data"]).decode("utf-8")

            email_list.append(email_info)

        return json.dumps(email_list, indent=4)
