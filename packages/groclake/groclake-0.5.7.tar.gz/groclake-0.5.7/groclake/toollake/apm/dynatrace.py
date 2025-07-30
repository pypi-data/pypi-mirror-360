import requests
import json
import os
from typing import Dict, List, Optional, Union, Any
from datetime import datetime
from dotenv import load_dotenv

class Dynatrace:

    def __init__(self, tool_config: Dict[str, Any]):

        self.tool_config = tool_config
        self.base_url = tool_config.get("base_url")
        self.api_token = tool_config.get("api_token")

        if self.base_url is None:
            raise ValueError("Base URL cannot be None")

        self.base_url = self.base_url.rstrip('/')
        self.headers = {
            'Authorization': f'Api-Token {self.api_token}',
            'Accept': 'application/json'
        }



    def query_metrics(
                self,
                metric_selector: str,
                from_time: Optional[str] = None,
                to_time: Optional[str] = None,
                resolution: Optional[str] = None,
                entity_selector: Optional[str] = None,
                mz_selector: Optional[str] = None
        ) -> Dict[str, Union[str, List]]:

            endpoint = f"{self.base_url}/api/v2/metrics/query"

            # Use dictionary comprehension to filter out None values
            params = {k: v for k, v in {
                'metricSelector': metric_selector,
                'from': from_time,
                'to': to_time,
                'resolution': resolution,
                'entitySelector': entity_selector,
                'mzSelector': mz_selector
            }.items() if v is not None}

            response = requests.get(endpoint, headers=self.headers, params=params)

            try:
                response.raise_for_status()  # Raise an exception for HTTP errors
                return response.json()
            except requests.HTTPError as e:
                # Handle specific HTTP errors here if needed
                raise RuntimeError(f"HTTP error occurred: {e}") from e
            except json.JSONDecodeError:
                raise RuntimeError("Failed to decode JSON response")


