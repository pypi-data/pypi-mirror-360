import requests
import json
from typing import Dict, Any
class NewRelic:
    def __init__(self, tool_config: Dict[str, Any]):
        """
        Initialize NewRelic connection with tool configuration.
        
        Expected tool_config format:
        {
            'api_key': 'api_key',
            'account_id': 'account_id'
        }
        """
        self.tool_config = tool_config
        self.api_key = tool_config.get('api_key')
        self.account_id = tool_config.get('account_id')
        self.nrql_url = "https://api.newrelic.com/graphql"
        self.headers = {
            "Api-Key": self.api_key,
            "Content-Type": "application/json"
        }

    def execute_nrql(self, nrql_query):
        """
        .

        Returns:
            dict: A dictionary containing the HTTP error metrics.
        """
        NRQL_QUERY = f"""
            {{
            actor {{
                account(id: {self.account_id}) {{
                nrql(query: "{nrql_query}") {{
                    results
                }}
                }}
            }}
            }}
            """
        payload = {
            "query": NRQL_QUERY
        }
        
        response = requests.post(self.nrql_url, headers=self.headers, data=json.dumps(payload))
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print(f"Error fetching data: {response.status_code}")
            return None

        
