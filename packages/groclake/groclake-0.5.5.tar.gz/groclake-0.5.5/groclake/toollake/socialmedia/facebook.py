import requests
from typing import Dict, Any

class Facebook:
    def __init__(self, tool_config: Dict[str, Any]):
        """
        Initialize Facebook client with page ID and access token.
        """
        self.access_token = tool_config.get("access_token")
        self.base_url = f"https://graph.facebook.com/v23.0"

    def create_post(self, message, page_id):
        """
        Create a post on the Facebook page.

        Parameters:
            message (str): The message to post.

        Returns:
            dict: JSON response from the API.
        """
        payload = {
            "message": message,
            "access_token": self.access_token
        }
        url = f"{self.base_url}/{page_id}/feed"
        response = requests.post(url, data=payload)
        return response.json()

    def get_post_analytics(self, post_id):
        """
        Get analytics/details for a specific post.
        """
        url = f"https://graph.facebook.com/v23.0/{post_id}?fields=likes.summary(true),comments.summary(true),shares,message,created_time"
        params = {
            "access_token": self.access_token
        }
        response = requests.get(url, params=params)
        return response.json()
    
