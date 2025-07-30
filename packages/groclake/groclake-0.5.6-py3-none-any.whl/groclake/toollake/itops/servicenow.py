import requests
from typing import Dict, Any

class ServiceNow:
    def __init__(self, tool_config: Dict[str, Any]):
        self.instance_url = tool_config.get('instance_url')
        self.token_url = f"{self.instance_url}/oauth_token.do"
        self.client_id = tool_config.get('client_id')
        self.client_secret = tool_config.get('client_secret')
        self.username = tool_config.get('username')
        self.password = tool_config.get('password')
        print(self.instance_url, self.client_id, self.client_secret, self.username, self.password)
        try:
            self.access_token = self.get_access_token()
        except Exception as e:
            print(e)
            raise e

    def get_access_token(self):
        payload = {
            "grant_type": "password",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "username": self.username,
            "password": self.password
        }
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        response = requests.post(self.token_url, data=payload, headers=headers)
        response.raise_for_status()
        return response.json()["access_token"]

    def get_headers(self):
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

    def get_incident_by_sys_id(self, sys_id):
        url = f"{self.instance_url}/api/now/table/incident/{sys_id}"
        response = requests.get(url, headers=self.get_headers())
        return response.json()

    def get_incidents_by_description(self, keyword):
        query = f"short_descriptionLIKE{keyword}"
        url = f"{self.instance_url}/api/now/table/incident?sysparm_query={query}"
        response = requests.get(url, headers=self.get_headers())
        return response.json()

    def get_incidents_by_created_date(self, date_str):
        query = f"sys_created_on>={date_str}"
        url = f"{self.instance_url}/api/now/table/incident?sysparm_query={query}"
        response = requests.get(url, headers=self.get_headers())
        return response.json()

    def get_filtered_incidents(self, keyword, date_str):
        query = f"short_descriptionLIKE{keyword}^sys_created_on>={date_str}"
        url = f"{self.instance_url}/api/now/table/incident?sysparm_query={query}"
        response = requests.get(url, headers=self.get_headers())
        return response.json()

    def create_incident(self, short_description, urgency="3", impact="3", assignment_group=None):
        data = {
            "short_description": short_description,
            "urgency": urgency,
            "impact": impact
        }
        if assignment_group:
            data["assignment_group"] = assignment_group

        url = f"{self.instance_url}/api/now/table/incident"
        response = requests.post(url, headers=self.get_headers(), json=data)
        return response.json()

    def update_incident(self, sys_id, update_data):
        url = f"{self.instance_url}/api/now/table/incident/{sys_id}"
        response = requests.patch(url, headers=self.get_headers(), json=update_data)
        return response.json()

    def get_all_incidents(self, limit=1000):
        url = f"{self.instance_url}/api/now/table/incident?sysparm_limit={limit}"
        response = requests.get(url, headers=self.get_headers())
        return response.json()
