
import os
import io
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

class GoogleDrive:
    def __init__(self, credentials_path=r"client_credentials.json", token_path='token.json'):
        self.SCOPES = ['https://www.googleapis.com/auth/drive']
        self.creds = None

        # Load credentials
        if os.path.exists(token_path):
            self.creds = Credentials.from_authorized_user_file(token_path, self.SCOPES)
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(credentials_path, self.SCOPES)
                self.creds = flow.run_local_server(port=0)
            with open(token_path, 'w') as token:
                token.write(self.creds.to_json())

        self.service = build('drive', 'v3', credentials=self.creds)

    def upload_file(self, file_path, mime_type='application/octet-stream', folder_id=None):
        file_metadata = {'name': os.path.basename(file_path)}
        if folder_id:
            file_metadata['parents'] = [folder_id]

        media = MediaFileUpload(file_path, mimetype=mime_type)
        file = self.service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        print(f"File uploaded. File ID: {file.get('id')}")
        return file.get('id')

    def download_file(self, file_id, destination_path):
        request = self.service.files().get_media(fileId=file_id)
        fh = io.FileIO(destination_path, 'wb')
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
            print(f"Download {int(status.progress() * 100)}%.")
        print(f"File downloaded to {destination_path}")

    def list_files(self, query=None, page_size=10):

        results = self.service.files().list(
            q=query,
            pageSize=page_size,
            fields="nextPageToken, files(id, name, mimeType)"
        ).execute()
        items = results.get('files', [])

        if not items:
            print('No files found.')
        else:
            print('Files:')
            for item in items:
                print(f"{item['name']} ({item['id']}) - {item['mimeType']}")

        return items

    def create_folder(self, folder_name, parent_id=None):

        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        if parent_id:
            file_metadata['parents'] = [parent_id]

        folder = self.service.files().create(
            body=file_metadata,
            fields='id'
        ).execute()
        print(f"Folder '{folder_name}' created with ID: {folder.get('id')}")
        return folder.get('id')

    def get_folder_id_by_name(self, folder_name):

        query = f"name = '{folder_name}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
        results = self.service.files().list(
            q=query,
            fields="files(id, name)",
            pageSize=1
        ).execute()
        folders = results.get('files', [])
        if folders:
            return folders[0]['id']
        return None
