import requests
import json
import os
from dotenv import load_dotenv
from typing import Dict, Any

class Outlook:
    def __init__(self, tool_config: Dict[str, Any]):
        self.tool_config = tool_config
        self.tenant_id = tool_config.get("tenant_id")
        self.client_id = tool_config.get("client_id")
        self.client_secret = tool_config.get("client_secret")
        self.refresh_token = tool_config.get("refresh_token")
        self.redirect_uri = tool_config.get("redirect_uri")
        self.domain = tool_config.get("domain")


        self.access_token = None
        self.headers = None

        # Authenticate for Outlook
        if not self.authenticate():
            raise Exception("Authentication failed for Outlook.")

    def authenticate(self):
        """Authenticate with Microsoft Graph API"""
        print("Obtaining access token via refresh token...")
        token_url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
        token_data = {
            'grant_type': 'refresh_token',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'refresh_token': self.refresh_token,
            'scope': 'https://graph.microsoft.com/.default offline_access',
            'redirect_uri': self.redirect_uri
        }

        try:
            token_r = requests.post(token_url, data=token_data)
            token_r.raise_for_status()
            token_json = token_r.json()
            self.access_token = token_json.get('access_token')

            new_refresh_token = token_json.get('refresh_token')
            if new_refresh_token:
                self.refresh_token = new_refresh_token
                print("Received new refresh token")

            if not self.access_token:
                print("Error: No access token received")
                return False

            self.headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Accept': 'application/json'
            }
            return True

        except requests.exceptions.RequestException as e:
            print(f"Error obtaining access token: {e}")
            return False

    def get_emails_from_folder(self, folder_name):
        """Fetch emails from a specified mail folder"""
        if not self.headers:
            if not self.authenticate():
                return []

        try:
            emails_url = f"https://graph.microsoft.com/beta/me/mailFolders/{folder_name}/messages"
            emails_response = requests.get(emails_url, headers=self.headers)
            emails_response.raise_for_status()
            return emails_response.json().get('value', [])
        except requests.exceptions.RequestException as e:
            print(f"Error fetching emails from folder '{folder_name}': {e}")
            return []

    def get_all_messages(self):
        """Fetch all messages from the user's mailbox"""
        if not self.headers:
            if not self.authenticate():
                return []

        try:
            messages_url = "https://graph.microsoft.com/v1.0/me/messages"
            messages_response = requests.get(messages_url, headers=self.headers)
            messages_response.raise_for_status()
            return messages_response.json().get('value', [])
        except requests.exceptions.RequestException as e:
            print(f"Error fetching all messages: {e}")
            return []

