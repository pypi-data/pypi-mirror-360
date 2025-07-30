import requests
from datetime import datetime, timedelta
from typing import Dict, Any

class SolarWinds:

    def __init__(self, tool_config: Dict[str, Any]):
        """
        Initialize SolarWinds connection with tool configuration.
        
        Expected tool_config format:
        {
            'api_key': 'api_key',
            'base_url': 'base_url'
        }
        """
        self.tool_config = tool_config
        
        # Set API credentials - prioritize passed parameters over environment variables
        self.api_key = tool_config.get("api_key") 
        self.base_url = tool_config.get("base_url")

        # Validate that we have the required credentials
        if not self.api_key or not self.base_url:
            raise ValueError("API key and base URL are required. Set them as parameters or in the .env file.")


    def get_metric_measurements(self,
        metric_name,
        start_time=None,
        end_time=None,
        filter=None,
        group_by=None,
        aggregate_by=None,
        series_type="TIMESERIES",
        page_size=100,
        skip_token=None
    ):
        # Construct the endpoint URL
        endpoint = f"{self.base_url}/{metric_name}/measurements"

        # Set up query parameters
        params = {
            "startTime": start_time or (datetime.utcnow() - timedelta(hours=1)).isoformat() + "Z",  # Default to 1 hour ago
            "endTime": end_time or datetime.utcnow().isoformat() + "Z",  # Default to now
            "seriesType": series_type,
            "pageSize": page_size,
            "filter": filter,
            "groupBy": group_by,
            "aggregateBy": aggregate_by,
            "skipToken": skip_token
        }

        # Remove None values from params
        params = {k: v for k, v in params.items() if v is not None}

        # Set headers for the request
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        try:
            # Make the API request
            response = requests.get(endpoint, headers=headers, params=params)
            response.raise_for_status()  # Raise an error for bad responses
            return response.json()  # Return the JSON response if successful
        except requests.exceptions.HTTPError as err:
            print(f"HTTP error occurred: {err} - {response.text}")
        except Exception as err:
            print(f"An error occurred: {err}")

        return None

