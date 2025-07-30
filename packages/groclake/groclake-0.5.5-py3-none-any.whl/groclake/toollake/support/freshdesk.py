import requests
from typing import Dict, Any
import base64
import json
import re

class Freshdesk:
    def __init__(self, tool_config: Dict[str, Any]):
        """Initialize Freshdesk connection"""
        self.domain = tool_config.get("domain")
        self.api_key = tool_config.get("api_key")
        self.base_url = f"https://{self.domain}.freshdesk.com/api/v2"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Basic {base64.b64encode(f'{self.api_key}:X'.encode()).decode()}"
        }

    def _validate_email(self, email: str) -> bool:
        """Validate email format"""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(email_pattern, email))

    def create_ticket(self, payload: Dict[str, Any]):
        """Create a new Freshdesk ticket"""
        required_fields = ["email", "subject", "description"]
        missing_fields = [f for f in required_fields if f not in payload]
        if missing_fields:
            return {"message": "Missing required fields", "error": ", ".join(missing_fields)}

        if not self._validate_email(payload["email"]):
            return {"message": "Invalid email format", "error": payload["email"]}

        url = f"{self.base_url}/tickets"
        try:
            response = requests.post(url, headers=self.headers, data=json.dumps(payload))
            if response.status_code == 201:
                return {"message": "Ticket created successfully", "ticket_id": response.json()["id"]}
            else:
                return {"message": "Failed to create ticket", "error": response.text}
        except Exception as e:
            return {"message": "Exception occurred while creating ticket", "error": str(e)}

    def get_ticket(self, ticket_id: int):
        """Fetch ticket by ID"""
        url = f"{self.base_url}/tickets/{ticket_id}"
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                return {"message": "Ticket fetched successfully", "data": response.json()}
            else:
                return {"message": "Failed to fetch ticket", "error": response.text}
        except Exception as e:
            return {"message": "Exception occurred while fetching ticket", "error": str(e)}

# tool_config = {
#     "domain": "",  # freshdesk domain: yourcompany.freshdesk.com
#     "api_key": ""
# }

# fd = Freshdesk(tool_config)

# payload = {
#     "email": "user@example.com",
#     "subject": "Example Issue",
#     "description": "Details about the issue",
#     "priority": 2,
#     "status": 2
# }

# print(fd.create_ticket(payload))
# ticket_id = 4

# result = fd.get_ticket(ticket_id)
# print(result)
