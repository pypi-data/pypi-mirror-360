import requests
from dotenv import load_dotenv
import sendgrid
import os
from sendgrid.helpers.mail import Mail
from twilio.rest import Client
from typing import Dict, Any

class Twilio:
    def __init__(self, tool_config: Dict[str, Any]):
        self.tool_config = tool_config
        self.account_sid = tool_config.get("account_sid")
        self.auth_token = tool_config.get("auth_token")
        self.verify_service_sid = tool_config.get("verify_service_sid")
        self.client = Client(self.account_sid, self.auth_token)
        self.sendgrid_api_key = tool_config.get("api_key")
        self.sg = sendgrid.SendGridAPIClient(api_key=self.sendgrid_api_key)

    def send_otp(self, payload):
        """Send OTP using Twilio Verify service."""
        # Twilio API URL
        url = f"https://verify.twilio.com/v2/Services/{self.verify_service_sid}/Verifications"

        data = {
            "To": payload.get('phno'),
            "Channel": "sms"
        }

        # Make the request
        response = requests.post(url, data=data, auth=(self.account_sid, self.auth_token))
        return response

    def send_email(self, payload):
        """Send email using SendGrid."""
        # Create email
        email = Mail(
            from_email=os.getenv('SENDER'),
            to_emails=payload.get('to_email'),
            subject=payload.get('subject'),
            html_content=payload.get('content')
        )

        # Send email
        try:
            response = self.sg.send(email)
            return response
        except Exception as e:
            raise

    def whatsapp(self, payload):
        """Send WhatsApp message using Twilio."""
        try:
            # Send WhatsApp message
            message = self.client.messages.create(
                from_="whatsapp:"+os.getenv("WHATSAPP"),  
                to="whatsapp:"+payload.get('phno'), 
                body=payload.get('body')
            )

            return message
        except Exception as e:
            raise
