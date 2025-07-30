import requests
import json
from typing import Dict, List, Any

class PowerBI:
    """
    A class to interact with Power BI REST API for pushing data to datasets.
    """
    
    def __init__(self, tool_config: Dict[str, Any]):
        """
        Initialize the PowerBI client using environment variables or provided parameters.
        
        Args:
            workspace_id (str, optional): Power BI workspace ID
            dataset_id (str, optional): Power BI dataset ID
            api_key (str, optional): Authentication key for push dataset API
            api_version (str, optional): API version to use (default: "beta")
        """
        self.tool_config = tool_config
        self.workspace_id = tool_config.get("workspace_id")
        self.dataset_id = tool_config.get("dataset_id")
        self.api_key = tool_config.get("api_key")
        self.api_version = tool_config.get("api_version")
        
        # Base URL of Power BI REST API
        self.base_url = "https://api.powerbi.com/beta"
        
        if not all([self.workspace_id, self.dataset_id, self.api_key]):
            missing = []
            if not self.workspace_id: missing.append("workspace_id")
            if not self.dataset_id: missing.append("dataset_id")
            if not self.api_key: missing.append("api_key")
            raise ValueError(f"Missing required configuration: {', '.join(missing)}. "
                             f"Set them as environment variables or pass as parameters.")
    
    def _get_url(self) -> str:
        """
        Construct the full URL for the Power BI API endpoint.
        
        Returns:
            str: The constructed API URL
        """
        return (
            f"{self.base_url}/{self.workspace_id}/datasets/{self.dataset_id}/rows"
            f"?experience=power-bi&searchQuery=workspace&key={self.api_key}"
        )
    
    def push_data(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Push data to Power BI dataset.
        
        Args:
            data: List of dictionaries representing rows to push to Power BI
            
        Returns:
            dict: Response from the API with status information
        """
        url = self._get_url()
        headers = {"Content-Type": "application/json"}
        payload = {"rows": data}
        
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        
        result = {
            "success": response.status_code == 200,
            "status_code": response.status_code,
            "message": "Data pushed successfully!" if response.status_code == 200 else "Failed to push data"
        }
        
        if response.status_code != 200:
            result["error_detail"] = response.text
            
        return result
