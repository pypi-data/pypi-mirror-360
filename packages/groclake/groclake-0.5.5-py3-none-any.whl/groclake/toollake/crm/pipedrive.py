import os
import requests
from typing import Dict, Any

class Pipedrive:
    def __init__(self, tool_config: Dict[str, Any]):
        self.api_token = tool_config.get("api_token")
        if not self.api_token:
            raise ValueError("API token must be set in the PIPEDRIVE_API_TOKEN environment variable.")
        self.base_url = "https://api.pipedrive.com"


    def _request(self, method, endpoint, params=None, data=None, files=None):
        url = f"{self.base_url}/{endpoint}"
        headers = {"Accept": "application/json"}
        params = params or {}
        params["api_token"] = self.api_token

        response = requests.request(method, url, headers=headers, params=params, json=data, files=files)
        response.raise_for_status()
        return response.json()

    # Activities
    def get_activities(self):
        return self._request("GET", "api/v2/activities")

    def create_activity(self, data):
        return self._request("POST", "api/v2/activities", data=data)

    # Billing (limited API access)
    def get_billing_details(self):
        return self._request("GET", "v1/billing/subscriptions/addons")

    # Call Logs (may require app)
    def get_call_logs(self):
        return self._request("GET", "v1/callLogs")



    # Deals
    def get_deals(self):
        return self._request("GET", "api/v2/deals")


    def get_files(self):
        return self._request("GET", "v1/files")



    # Goals
    def get_goals(self):
        return self._request("GET", "/v1/goals/find")

    # Leads
    def get_leads(self):
        return self._request("GET", "/v1/leads")


    # Organizations
    def get_organizations(self):
        return self._request("GET", "api/v2/organizations")



    # Persons
    def get_persons(self):
        return self._request("GET", "api/v2/persons")



    # Tasks
    def get_tasks(self):
        return self._request("GET", "v1/tasks")


    # Roles
    def get_roles(self):
        return self._request("GET", "/v1/roles")

    # Users
    def get_users(self):
        return self._request("GET", "/v1/users")

