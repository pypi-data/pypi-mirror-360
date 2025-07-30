import requests
from typing import Dict, Any


class Microsoft365Dynamics:
    def __init__(self, tool_config: Dict[str, Any]):
        self.tool_config = tool_config
        self.tenant_id = tool_config.get("tenant_id")
        self.client_id = tool_config.get("client_id")
        self.client_secret = tool_config.get("client_secret")
        self.resource = tool_config.get("resource")

        # Authenticate and set headers
        self.headers = self.authenticate()

    def authenticate(self):
        """Get access token using client credentials and set headers."""
        token_url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
        token_data = {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'scope': f'{self.resource}/.default'
        }

        token_r = requests.post(token_url, data=token_data)
        token = token_r.json().get('access_token')

        if not token:
            print("❌ Failed to get access token")
            print(token_r.json())
            exit()

        return {
            'Authorization': f'Bearer {token}',
            'OData-MaxVersion': '4.0',
            'OData-Version': '4.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

    def fetch_accounts(self):
        """Fetch accounts from Dynamics 365."""
        url = f"{self.resource}/api/data/v9.2/accounts"
        return self.fetch_data(url)

    def fetch_contacts(self):
        """Fetch contacts from Dynamics 365."""
        url = f"{self.resource}/api/data/v9.2/contacts"
        return self.fetch_data(url)

    def fetch_leads(self):
        """Fetch leads from Dynamics 365."""
        url = f"{self.resource}/api/data/v9.2/leads"
        return self.fetch_data(url)

    def fetch_opportunities(self):
        """Fetch opportunities from Dynamics 365."""
        url = f"{self.resource}/api/data/v9.2/opportunities"
        return self.fetch_data(url)

    def fetch_cases(self):
        """Fetch cases from Dynamics 365."""
        url = f"{self.resource}/api/data/v9.2/incidents"
        return self.fetch_data(url)

    def fetch_tasks(self):
        """Fetch tasks from Dynamics 365."""
        url = f"{self.resource}/api/data/v9.2/tasks"
        return self.fetch_data(url)

    def fetch_emails(self):
        """Fetch emails from Dynamics 365."""
        url = f"{self.resource}/api/data/v9.2/emails"
        return self.fetch_data(url)

    def fetch_appointments(self):
        """Fetch appointments from Dynamics 365."""
        url = f"{self.resource}/api/data/v9.2/appointments"
        return self.fetch_data(url)

    def fetch_phone_calls(self):
        """Fetch phone calls from Dynamics 365."""
        url = f"{self.resource}/api/data/v9.2/phonecalls"
        return self.fetch_data(url)

    def fetch_data(self, endpoint):
        """Fetch data from the specified endpoint."""
        res = requests.get(endpoint, headers=self.headers)
        if res.status_code == 200:
            return res.json().get('value', [])
        else:
            print(f"❌ Failed to fetch data from {endpoint}")
            print(res.status_code, res.text)
            return []


