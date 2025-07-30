from slack_sdk import WebClient
from typing import Dict, Any

class Slack:
        
    def __init__(self, tool_config: Dict[str, Any]):
        """
        Initialize Slack connection with tool configuration.
        
        Expected tool_config format:
        {
            'slack_bot_token': 'slack_bot_token'
        }
        """
        self.tool_config = tool_config
        self.slack_bot_token = tool_config.get('slack_bot_token')
        self.slack_client = WebClient(token=self.slack_bot_token)


    def send_message(self, payload):
        try:
            message=payload.get("message")
            channel=payload.get("channel")
            self.slack_client.chat_postMessage(channel=channel, text=message)
            return {"message":"Message Sent Successfully"}
        except Exception as e:
            return {"message":str(e)}
