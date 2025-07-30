import requests
import re
from typing import Dict, Any

class Zendesk:
    def __init__(self, tool_config: Dict[str, Any]):
        """Initialize Zendesk connection"""
        self.subdomain = tool_config.get("subdomain")
        self.email = tool_config.get("email")
        self.api_token = tool_config.get("api_token")
        self.base_url = f"https://{self.subdomain}.zendesk.com/api/v2"

        self.auth = (f"{self.email}/token", self.api_token)
        self.headers = {"Content-Type": "application/json"}

    def _validate_email(self, email: str) -> bool:
        """Validate email format"""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(email_pattern, str(email)))

    def create_ticket(self, payload: Dict[str, Any]):
        """Create a new Zendesk ticket"""
        required_fields = ["subject", "description"]
        missing_fields = [field for field in required_fields if field not in payload]
        if missing_fields:
            return {"message": "Missing required fields", "error": ", ".join(missing_fields)}

        data = {
            "ticket": {
                "subject": payload["subject"],
                "comment": {"body": payload["description"]},
                "priority": payload.get("priority", "normal")
            }
        }

        try:
            response = requests.post(f"{self.base_url}/tickets.json", auth=self.auth, headers=self.headers, json=data)
            response.raise_for_status()
            ticket = response.json().get("ticket", {})
            return {"message": "Ticket created successfully", "ticket_id": ticket.get("id")}
        except Exception as e:
            return {"message": "Error creating ticket", "error": str(e)}

    def fetch_ticket(self, ticket_id: int):
        """Fetch ticket details"""
        try:
            response = requests.get(f"{self.base_url}/tickets/{ticket_id}.json", auth=self.auth, headers=self.headers)
            response.raise_for_status()
            ticket = response.json().get("ticket", {})
            return {
                "message": "Ticket fetched successfully",
                "data": {
                    "id": ticket.get("id"),
                    "subject": ticket.get("subject"),
                    "description": ticket.get("description"),
                    "status": ticket.get("status"),
                    "priority": ticket.get("priority")
                }
            }
        except Exception as e:
            return {"message": "Error fetching ticket", "error": str(e)}


# tool_config = {
#     "subdomain": "",
#     "email": "",
#     "api_token": ""
# }

# zendesk = Zendesk(tool_config)

# payload = {
#     "subject": "Test Issue: Unable to login",
#     "description": "User reports login page is throwing error.",
#     "priority": "high"
# }

# response = zendesk.create_ticket(payload)
# print("Create Ticket Response:", response)
# ticket_id = response.get("ticket_id")


# fetch_response = zendesk.fetch_ticket(10)

# print("Fetch Ticket Response:", fetch_response)
