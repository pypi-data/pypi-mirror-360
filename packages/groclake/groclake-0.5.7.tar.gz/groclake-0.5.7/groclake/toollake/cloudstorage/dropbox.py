import os
import requests
import json
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Load the .env file automatically
load_dotenv()


class DropboxAPIClient:
    def __init__(self):

        self.access_token = os.getenv('DROPBOX_ACCESS_TOKEN')
        if not self.access_token:
            raise ValueError("DROPBOX_ACCESS_TOKEN environment variable is required")

        self.api_base_url = "https://api.dropboxapi.com/2"
        self.content_base_url = "https://content.dropboxapi.com/2"

    def _get_headers(self, content_type: str = "application/json") -> Dict[str, str]:

        return {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': content_type
        }

    def create_folder(self, path: str) -> Dict[str, Any]:

        url = f"{self.api_base_url}/files/create_folder_v2"
        headers = self._get_headers()
        data = {"path": path}

        response = requests.post(url, headers=headers, json=data)

        if response.status_code == 200:
            #print(f"✅ Folder created successfully: {path}")
            return response.json()
        else:
            #print(f"❌ Failed to create folder: {response.status_code}")
            #print(f"Error: {response.text}")
            response.raise_for_status()

    def upload_file(self, local_file_path: str, dropbox_path: str) -> Dict[str, Any]:

        url = f"{self.content_base_url}/files/upload"

        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/octet-stream',
            'Dropbox-API-Arg': json.dumps({
                "path": dropbox_path,
                "mode": "overwrite",  # Overwrite if file exists
                "autorename": False
            })
        }

        try:
            with open(local_file_path, 'rb') as file:
                response = requests.post(url, headers=headers, data=file)

            if response.status_code == 200:
                #print(f"✅ File uploaded successfully: {local_file_path} -> {dropbox_path}")
                return response.json()
            else:
                #print(f"❌ Failed to upload file: {response.status_code}")
                #print(f"Error: {response.text}")
                response.raise_for_status()

        except FileNotFoundError:
            #print(f"❌ Local file not found: {local_file_path}")
            raise

    def download_file(self, dropbox_path: str, local_file_path: str) -> bool:

        url = f"{self.content_base_url}/files/download"

        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Dropbox-API-Arg': json.dumps({"path": dropbox_path})
        }

        response = requests.post(url, headers=headers)

        if response.status_code == 200:
            with open(local_file_path, 'wb') as file:
                file.write(response.content)
            #print(f"✅ File downloaded successfully: {dropbox_path} -> {local_file_path}")
            return True
        else:
            #print(f"❌ Failed to download file: {response.status_code}")
            #print(f"Error: {response.text}")
            response.raise_for_status()

    def list_folder(self, path: str = "") -> Dict[str, Any]:

        url = f"{self.api_base_url}/files/list_folder"
        headers = self._get_headers()
        data = {"path": path}

        response = requests.post(url, headers=headers, json=data)

        if response.status_code == 200:
            result = response.json()
            #print(f"✅ Folder contents for '{path or 'root'}':")
            for entry in result.get('entries', []):
                entry_type = "📁" if entry['.tag'] == 'folder' else "📄"
                #print(f"  {entry_type} {entry['name']}")
            return result
        else:
            #print(f"❌ Failed to list folder: {response.status_code}")
            #print(f"Error: {response.text}")
            response.raise_for_status()


