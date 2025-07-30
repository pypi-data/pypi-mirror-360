import requests
from requests.auth import HTTPBasicAuth
import json
from typing import Dict, Optional, Any, List, Union

class Confluence:
    """
    A class to interact with Confluence REST API for various operations.
    """
    
    def __init__(self, tool_config: Dict[str, Any]):
        """
        Initialize the Confluence client using environment variables or provided parameters.
        
        Args:
            domain (str, optional): Confluence domain (e.g., 'yourcompany.atlassian.net')
            email (str, optional): Email for authentication
            api_token (str, optional): API token for authentication
        """
        self.tool_config = tool_config
        self.domain = tool_config.get("domain")
        self.email = tool_config.get("email")
        self.api_token = tool_config.get("api_token")
        
        if not all([self.domain, self.email, self.api_token]):
            missing = []
            if not self.domain: missing.append("domain")
            if not self.email: missing.append("email")
            if not self.api_token: missing.append("api_token")
            raise ValueError(f"Missing required configuration: {', '.join(missing)}. "
                             f"Set them as environment variables or pass as parameters.")
        
        self.base_url = f"https://{self.domain}/wiki/api/v2"
        self.auth = HTTPBasicAuth(self.email, self.api_token)
        self.headers = {
            "Accept": "application/json"
        }
    
    def _make_request(self, method: str, endpoint: str, 
                     params: Optional[Dict] = None, 
                     data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Make a request to the Confluence API.
        
        Args:
            method (str): HTTP method (GET, POST, PUT, DELETE)
            endpoint (str): API endpoint path
            params (dict, optional): Query parameters
            data (dict, optional): Request body data
            
        Returns:
            dict: Response from the API
        """
        url = f"{self.base_url}/{endpoint}"
        
        headers = self.headers.copy()
        if data:
            headers["Content-Type"] = "application/json"
        
        response = requests.request(
            method,
            url,
            headers=headers,
            auth=self.auth,
            params=params,
            json=data if data else None
        )
        
        if response.status_code >= 400:
            return {
                "success": False,
                "status_code": response.status_code,
                "message": f"Request failed with status {response.status_code}",
                "error": response.text
            }
        
        try:
            return {
                "success": True,
                "status_code": response.status_code,
                "data": response.json() if response.text else None
            }
        except json.JSONDecodeError:
            return {
                "success": True,
                "status_code": response.status_code,
                "data": response.text
            }
    
    def get_attachments(self, attachment_id: Optional[str] = None, content_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get attachments from Confluence.
        
        Args:
            attachment_id (str, optional): Specific attachment ID to retrieve
            content_id (str, optional): Content ID to get attachments from
            
        Returns:
            dict: Response containing attachments data
        """
        if attachment_id:
            # Get a specific attachment by ID
            return self._make_request("GET", f"attachments/{attachment_id}")
        else:
            # Get all attachments, optionally filtered by content ID
            params = {"id": content_id} if content_id else None
            return self._make_request("GET", "attachments", params=params)
    
    

