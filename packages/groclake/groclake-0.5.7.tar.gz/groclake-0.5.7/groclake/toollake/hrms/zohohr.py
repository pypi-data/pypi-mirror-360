import requests
from typing import Dict, Any

class ZohoHR:
    def __init__(self, tool_config: Dict[str, Any]):
        """
        Initialize ZohoHR client with OAuth access token.
        """
        self.access_token = tool_config.get("access_token")
        self.base_url = "https://people.zoho.in/people/api/forms"

    def fetch_bulk_records(
        self,
        form_link_name="employee",
        s_index=1,
        limit=100,
        search_column=None,
        search_value=None,
        modified_time=None
    ):
        """
        Fetches bulk records from a Zoho People form.

        Parameters:
            form_link_name (str): Internal form name (e.g., "employee").
            s_index (int): Starting index (starts at 1).
            limit (int): Number of records to fetch (max 200).
            search_column (str): Optional search column (e.g., "EMPLOYEEID").
            search_value (str): Value to search for in the column.
            modified_time (int): Unix timestamp in milliseconds to filter modified records.

        Returns:
            dict: JSON response from the API.
        """
        url = f"{self.base_url}/{form_link_name}/getRecords"
        headers = {
            "Authorization": f"Zoho-oauthtoken {self.access_token}"
        }
        params = {
            "sIndex": s_index,
            "limit": limit
        }
        if search_column and search_value:
            params["SearchColumn"] = search_column
            params["SearchValue"] = search_value
        if modified_time:
            params["modifiedtime"] = modified_time

        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            return None