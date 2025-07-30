"""
Gupshup SMS and Email communication module
"""

from groclake.config import GUPSHUP_URL
import requests
import boto3
from typing import Dict, Any
class Gupshup:
    def __init__(self, tool_config: Dict[str, Any]):
        self.tool_config = tool_config
        self.commlake_id = tool_config.get("commlake_id")
        self.params = {}

    def gupshup_send_sms(self, payload):
        sms_params = {
            'message': payload.get('message'),
            'mobile': payload.get('mobile'),
            'userid': payload.get('userid'),
            'dltTemplateId': payload.get('dltTemplateId'),
            'principalEntityId': payload.get('principalEntityId'),
            'password': payload.get('password')
        }
        response = self.send_otp_to_customer(sms_params)
        if response:
            return {"message": "OTP Sent Successfully"}

    def send_otp_to_customer(self, params):
        otp_params = {
            'method': 'SendMessage', 'msg_type': 'TEXT', 'v': '1.1', 'format': 'text', 'auth_scheme': 'plain',
            'userid': params.get('userid'), 'principalEntityId': params.get('principalEntityId'),
            'password': params.get('password'), 'dltTemplateId': params.get('dltTemplateId'),
            'send_to': int(params.get('mobile')), 'msg': params.get('message'), 'mask': 'PLTCAI'
        }

        gupshup_url = GUPSHUP_URL
        response = requests.get(gupshup_url, params=otp_params)

        if response.status_code == 200:
            return True
        else:
            raise Exception('OTP Failure')

    def amazon_ses_send_email(self, payload):
        AWS_REGION = payload.get("region")  # Change to your AWS region
        SENDER = payload.get("sender")  # Must be a verified email in SES
        SUBJECT = payload.get("subject")
        BODY_TEXT = payload.get("body")
        RECIPIENT = payload.get('email')
        if (not RECIPIENT):
            return {"message": "Email not found"}
        ses_client = boto3.client("ses", region_name=AWS_REGION)
        # Sending email
        try:
            response = ses_client.send_email(
                Source=SENDER,
                Destination={"ToAddresses": [RECIPIENT]},
                Message={
                    "Subject": {"Data": SUBJECT},
                    "Body": {"Text": {"Data": BODY_TEXT}},
                },
            )
            if response["ResponseMetadata"]['HTTPStatusCode'] == 200:
                return {"message": "OTP Sent Successfully"}
        except Exception as e:
            return {"message": str(e)} 