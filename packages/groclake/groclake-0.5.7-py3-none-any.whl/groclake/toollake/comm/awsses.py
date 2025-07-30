import boto3
from typing import Dict, Any

class AWSSes:
    def __init__(self, tool_config: Dict[str, Any]):
        self.tool_config = tool_config
        self.region = tool_config.get("region", "us-east-1")
        self.access_key_id = tool_config.get("access_key_id")
        self.secret_access_key = tool_config.get("secret_access_key")
        #self.aws_session_token = tool_config.get("aws_session_token")  # Optional

    def send_email(self, payload):
        self.sender = payload.get("sender")
        self.recipient = payload.get("recipient")
        self.subject = payload.get("subject")
        self.body = payload.get("body")
        self.body_mime_type = payload.get("body_mime_type", "html")
        self.cc_recipients = payload.get("cc_recipients", [])
        self.bcc_recipients = payload.get("bcc_recipients", [])
        self.reply_to = payload.get("reply_to", [])
        
        if not self.recipient:
            return {"message": "Email not found", "status": "failed"}

        # Create boto3 SES client using credentials from tool_config
        ses_client_params = {
            "region_name": self.region,
            "aws_access_key_id": self.access_key_id,
            "aws_secret_access_key": self.secret_access_key,
        }

        #if self.session_token:
        #    ses_client_params["aws_session_token"] = self.session_token

        ses_client = boto3.client("ses", **ses_client_params)

        # Sending email
        try:
            if self.body_mime_type == "text":
                message_body = {"Text": {"Data": self.body}}
            else:
                message_body = {"Html": {"Data": self.body}}

            response = ses_client.send_email(
                Source=self.sender,
                Destination={"ToAddresses": [self.recipient]},
                Message={
                    "Subject": {"Data": self.subject},
                    "Body": message_body,
                },
            )
            if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
                return {"message": "Email Sent Successfully", "status": "success"}
        except Exception as e:
            return {"message": str(e), "status": "failed"}
