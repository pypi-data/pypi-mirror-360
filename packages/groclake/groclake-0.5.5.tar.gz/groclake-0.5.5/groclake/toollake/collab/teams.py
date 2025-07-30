import requests
from typing import Dict, Any

class Teams:
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
        self.headers = None
        self.drive_id = None
        self.site_id = None

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

    def get_site_id(self):
        """Get the SharePoint site ID using site name"""
        if not self.headers:
            if not self.authenticate():
                return False

        print(f"Fetching site information for {self.site_name}...")

        try:
            site_url = f"https://graph.microsoft.com/v1.0/sites/{self.domain}.sharepoint.com:/sites/{self.site_name}"
            site_response = requests.get(site_url, headers=self.headers)
            site_response.raise_for_status()
            site = site_response.json()
            self.site_id = site['id']
            print(f"Site ID: {self.site_id}")
            return True
        except requests.exceptions.RequestException as e:
            print(f"Error fetching site information: {e}")
            return False

    def get_drive_id(self):
        """Get the drive ID for the site"""
        if not self.site_id and not self.get_site_id():
            return False

        try:
            drive_url = f"https://graph.microsoft.com/v1.0/sites/{self.site_id}/drive"
            drive_response = requests.get(drive_url, headers=self.headers)
            drive_response.raise_for_status()
            drive_data = drive_response.json()
            self.drive_id = drive_data['id']
            print(f"Drive ID: {self.drive_id}")
            return True
        except requests.exceptions.RequestException as e:
            print(f"Error fetching drive information: {e}")
            return False

    def get_recordings_folder(self):
        """Get the Recordings folder from the General channel"""
        if not self.drive_id:
            print("Drive ID not set. Please get drive ID first.")
            return None

        try:
            recordings_url = f"https://graph.microsoft.com/v1.0/drives/{self.drive_id}/root:/General/Recordings"
            recordings_response = requests.get(recordings_url, headers=self.headers)
            recordings_response.raise_for_status()
            return recordings_response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching recordings folder: {e}")
            return None

    def get_recordings(self, folder_id):
        """Get all recordings in the specified folder"""
        if not self.headers:
            if not self.authenticate():
                return []

        try:
            recordings_url = f"https://graph.microsoft.com/v1.0/drives/{self.drive_id}/items/{folder_id}/children"
            recordings_response = requests.get(recordings_url, headers=self.headers)
            recordings_response.raise_for_status()
            recordings_data = recordings_response.json()

            # Process each recording to include only name and download URL
            recordings = []
            for recording in recordings_data.get('value', []):
                recording_info = {
                    'name': recording['name'],
                    'download_url': recording.get('@microsoft.graph.downloadUrl')
                }
                recordings.append(recording_info)

            return recordings
        except requests.exceptions.RequestException as e:
            print(f"Error fetching recordings: {e}")
            return []


