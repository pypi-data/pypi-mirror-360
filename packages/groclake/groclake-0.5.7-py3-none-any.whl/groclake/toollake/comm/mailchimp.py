import requests
from dotenv import load_dotenv
import os
from typing import Dict, Any
load_dotenv()

class Mailchimp:
    def __init__(self, tool_config: Dict[str, Any]):
        # Initialize with environment variables or default values
        self.tool_config = tool_config
        self.api_key = tool_config.get("api_key")
        self.server_prefix = tool_config.get("server_prefix")
        self.audience_id = tool_config.get("audience_id")
        
        # Set up base URL and headers
        self.base_url = f"https://{self.server_prefix}.api.mailchimp.com/3.0"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def create_campaign(self, payload):
        """Create a new campaign in Mailchimp."""
        url = f"{self.base_url}/campaigns"
        payload = {
            "type": "regular",
            "recipients": {"list_id": self.audience_id},
            "settings": {
                "subject_line": payload.get('subject_line'),
                "title": payload.get('title'),
                "from_name": payload.get("from_name"),
                "from_email": payload.get("from_email"),
                "reply_to": payload.get("reply_to")
            }
        }
        
        response = requests.post(url, headers=self.headers, json=payload)
        if response.status_code == 200:
            campaign_id = response.json().get("id")
            print(f"Campaign Created: {campaign_id}")
            return campaign_id
        else:
            print("Error Creating Campaign:", response.json())
            return None

    def add_campaign_content(self, campaign_id,payload):
        """Add content to an existing campaign."""
        url = f"{self.base_url}/campaigns/{campaign_id}/content"
        payload = {
            "html": payload.get('html')
        }
        
        response = requests.put(url, headers=self.headers, json=payload)
        if response.status_code == 200:
            print("Content Added Successfully!")
            return True
        else:
            print("Error Adding Content:", response.json())
            return False

    def send_campaign(self, campaign_id):
        """Send an existing campaign."""
        url = f"{self.base_url}/campaigns/{campaign_id}/actions/send"
        response = requests.post(url, headers=self.headers)
        
        if response.status_code == 204:
            print("Campaign Sent Successfully!")
            return True
        else:
            print("Error Sending Campaign:", response.json())
            return False

    def send_email(self, payload):
        """Create, add content to, and send a campaign in one go."""
        campaign_id = self.create_campaign(payload)
        
        if campaign_id:
            if self.add_campaign_content(campaign_id, payload):
                return self.send_campaign(campaign_id)
        return False

