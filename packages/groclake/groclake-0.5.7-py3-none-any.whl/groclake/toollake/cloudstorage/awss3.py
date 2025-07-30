import boto3
import base64
import requests
from typing import Dict, Any

class AWSS3:
    def __init__(self, tool_config: Dict[str, Any]):
        """
        :param tool_config: Dict with keys for both auth and bucket config:
            - access_key_id or aws_access_key_id
            - secret_access_key or aws_secret_access_key
            - region or bucket_region
            - bucket_name
            - bucket_file_path
        """
        # Auth
        self.access_key_id = tool_config.get('access_key_id') or tool_config.get('aws_access_key_id')
        self.secret_access_key = tool_config.get('secret_access_key') or tool_config.get('aws_secret_access_key')
        # Bucket
        if tool_config.get('region'):
            self.region = tool_config.get('region')
        else:
            self.region = 'us-east-1'
        
        if tool_config.get('bucket_name'):
            self.bucket_name = tool_config.get('bucket_name')
        else:
            self.bucket_name = 'groclake'
        
        if tool_config.get('bucket_file_path'):
            self.bucket_file_path = tool_config.get('bucket_file_path', '').rstrip('/')
        else:
            self.bucket_file_path = ''

        self.s3_client = self._init_s3_client()

    def _init_s3_client(self):
        return boto3.client(
            's3',
            aws_access_key_id=self.access_key_id,
            aws_secret_access_key=self.secret_access_key,
            region_name=self.region
        )
    
    def set_bucket_config(self, bucket_config: Dict[str, Any]):
        self.region = bucket_config.get('region') or bucket_config.get('bucket_region')
        self.bucket_name = bucket_config.get('bucket_name')
        self.bucket_file_path = bucket_config.get('bucket_file_path', '').rstrip('/')


    def upload_document(self, document, file_name: str, is_base64: bool = True) -> Dict[str, Any]:
        """
        Uploads a document to S3.
        :param document: base64 string or URL
        :param file_name: Name to use for the file in S3
        :param is_base64: If True, document is base64; if False, document is a URL
        :return: Dict with upload status and S3 URL
        """
        #check if document is a url
        if isinstance(document, str) and document.startswith('http'):
            is_url = True
        else:
            is_url = False
        
        # Get file bytes
        if is_base64:
            file_bytes = base64.b64decode(document)
        elif is_url:
            response = requests.get(document)
            response.raise_for_status()
            file_bytes = response.content
        else:
            file_bytes = document.read() if hasattr(document, 'read') else document
        
        file_size_mb = len(file_bytes) / (1024 * 1024)
        file_size_mb = round(file_size_mb, 3)

        s3_key = f"{self.bucket_file_path}/{file_name}" if self.bucket_file_path else file_name
        #print(f"Uploading to S3: {s3_key}")
        # Upload to S3
        self.s3_client.put_object(
            Bucket=self.bucket_name,
            Key=s3_key,
            Body=file_bytes
        )

        s3_url = f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{s3_key}"
        return {
            "status": "success",
            "file_path": s3_url,
            "s3_url": s3_url,
            "bucket": self.bucket_name,
            "key": s3_key,
            "file_name": file_name,
            "data_object_id": file_name,
            "data_object_path": self.bucket_file_path,
            "data_warehouse_name": "AWSS3",
            "file_size_mb": file_size_mb
        }

    def fetch_document(self, file_name: str, file_path: str) -> bytes:
        """
        Fetches a file from S3 and returns its bytes.
        :param file_name: The name of the file (e.g., 'mydoc.pdf')
        :param file_path: The S3 key or prefix (e.g., 'folder1/folder2')
        :return: File content as bytes
        """
        # Compose the full S3 key
        if file_path:
            s3_key = f"{file_path.rstrip('/')}/{file_name}"
        else:
            s3_key = file_name

        response = self.s3_client.get_object(Bucket=self.bucket_name, Key=s3_key)
        return response['Body'].read()
