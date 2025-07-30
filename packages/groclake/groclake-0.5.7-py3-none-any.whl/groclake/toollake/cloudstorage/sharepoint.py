import requests
import os
from typing import Dict, Any

class SharePoint:

    def __init__(self, tool_config: Dict[str, Any]):

        self.tool_config = tool_config
        self.tenant_id = tool_config.get("tenant_id")
        self.client_id = tool_config.get("client_id")
        self.client_secret = tool_config.get("client_secret")
        self.refresh_token = tool_config.get("refresh_token")
        self.redirect_uri = tool_config.get("redirect_uri")
        self.domain = tool_config.get("domain")
        self.site_name = tool_config.get("site_name")

        self.access_token = None
        self.site_id = None
        self.headers = None

    def authenticate(self):

        # Get Access Token using refresh token
        print("Obtaining access token via refresh token...")
        token_url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
        token_data = {
            'grant_type': 'refresh_token',
            'client_id': self.client_id,
            'client_secret': self.client_secret,  # if applicable
            'refresh_token': self.refresh_token,
            'scope': 'https://graph.microsoft.com/.default offline_access',
            'redirect_uri': self.redirect_uri  # same URI used in original auth code flow
        }

        try:
            token_r = requests.post(token_url, data=token_data)
            token_r.raise_for_status()  # Raise exception for HTTP errors
            token_json = token_r.json()
            self.access_token = token_json.get('access_token')

            # Store the new refresh token for future use if provided
            new_refresh_token = token_json.get('refresh_token')
            if new_refresh_token:
                self.refresh_token = new_refresh_token
                print("Received new refresh token")

            if not self.access_token:
                print("Error: No access token received")
                return False

            # Setup authorization header
            self.headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Accept': 'application/json'
            }
            return True

        except requests.exceptions.RequestException as e:
            print(f"Error obtaining access token: {e}")
            return False

    def get_site_id(self):

        if not self.headers:
            if not self.authenticate():
                return False

        # Get site ID
        print(f"Fetching site information for {self.site_name if self.site_name else 'root'}...")

        # Construct the site URL based on whether site_name is provided
        if self.site_name:
            site_url = f"https://graph.microsoft.com/v1.0/sites/{self.domain}.sharepoint.com:/sites/{self.site_name}"
        else:
            site_url = f"https://graph.microsoft.com/v1.0/sites/{self.domain}.sharepoint.com"

        try:
            site_response = requests.get(site_url, headers=self.headers)
            site_response.raise_for_status()
            site = site_response.json()
            self.site_id = site['id']
            print(f"Site ID: {self.site_id}")
            return True
        except requests.exceptions.RequestException as e:
            print(f"Error fetching site information: {e}")
            return False

    def fetch_files(self, folder_path=None):

        if not self.site_id and not self.get_site_id():
            return []

        # Get files from the site's drive root or specific folder
        print("Fetching files...")

        if folder_path:
            # Clean up folder path to ensure it starts with a /
            if not folder_path.startswith('/'):
                folder_path = '/' + folder_path
            files_url = f"https://graph.microsoft.com/v1.0/sites/{self.site_id}/drive/root:{folder_path}:/children"
        else:
            files_url = f"https://graph.microsoft.com/v1.0/sites/{self.site_id}/drive/root/children"

        try:
            files_response = requests.get(files_url, headers=self.headers)
            files_response.raise_for_status()
            files = files_response.json()

            file_count = len(files.get('value', []))
            print(f"Found {file_count} files/folders")
            return files.get('value', [])
        except requests.exceptions.RequestException as e:
            print(f"Error fetching files: {e}")
            return []

    def download_file(self, item_id, destination_path=None):

        if not self.site_id and not self.get_site_id():
            return False, "Failed to get site ID"

        # First get file metadata to get the name if destination_path is not specified
        if not destination_path:
            destination_path = self.get_destination_path(item_id)
            if not destination_path:
                return False, "Error determining destination path"

        # Download the actual file content
        try:
            download_url = f"https://graph.microsoft.com/v1.0/sites/{self.site_id}/drive/items/{item_id}/content"
            print(f"Downloading file from: {download_url}")

            # Stream the download to handle large files efficiently
            with requests.get(download_url, headers=self.headers, stream=True) as response:
                response.raise_for_status()

                # Ensure directory exists
                os.makedirs(os.path.dirname(os.path.abspath(destination_path)), exist_ok=True)

                # Write content to file
                with open(destination_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)

            print(f"File successfully downloaded to: {destination_path}")
            return True, destination_path

        except requests.exceptions.RequestException as e:
            return False, f"Error downloading file: {e}"

    def get_destination_path(self, item_id):

        try:
            metadata_url = f"https://graph.microsoft.com/v1.0/sites/{self.site_id}/drive/items/{item_id}"
            metadata_response = requests.get(metadata_url, headers=self.headers)
            metadata_response.raise_for_status()
            file_metadata = metadata_response.json()
            file_name = file_metadata.get('name', f"downloaded_file_{item_id}")
            return os.path.join(os.getcwd(), file_name)
        except requests.exceptions.RequestException as e:
            print(f"Error fetching file metadata: {e}")
            return None

    def download_file_by_name(self, file_name, folder_path=None, destination_path=None):

        # Get files in the folder
        files = self.fetch_files(folder_path)

        # Find the file by name
        for file in files:
            if file.get('name') == file_name:
                return self.download_file(file.get('id'), destination_path)

        return False, f"File '{file_name}' not found"

