import requests
from typing import Dict, Any

class SAP:
    def __init__(self, tool_config: Dict[str, Any]):
        self.api_key = tool_config.get("api_key")
        if not self.api_key:
            raise Exception('SAP_API_KEY is not set')
        
    
    def fetch_customers(self):
    # API endpoint
        url = "https://sandbox.api.sap.com/subscriptionbilling/api/business-partner/v3/customers"

        # Query parameters
        params = {
            "$count": "true",
            "pageSize": "10"
        }

        # Headers (replace with your API Key)
        headers = {
            "APIKey": self.api_key,
            "Accept": "application/json",
            "DataServiceVersion": "2.0"
        }

        try:
            # Send GET request
            response = requests.get(url, headers=headers, params=params)

            # Check for successful response
            if response.status_code == 200:
                customers = response.json()
                return customers
            else:
                return (f"Error: {response.status_code} - {response.text}")

        except requests.RequestException as e:
            return (f"Request failed: {e}")
    
    def fetch_customer_ID(self,customer_id):
        # 3176169607
        url = f"https://sandbox.api.sap.com/subscriptionbilling/api/business-partner/v3/customers/{customer_id}"

        # Query parameters
        params = {
            "$count": "true",
            "pageSize": "10"
        }

        # Headers (replace with your API Key)
        headers = {
            "APIKey": self.api_key,
            "Accept": "application/json",
            "DataServiceVersion": "2.0"
        }

        try:
            # Send GET request
            response = requests.get(url, headers=headers, params=params)

            # Check for successful response
            if response.status_code == 200:
                customers = response.json()
                return customers
            else:
                return (f"Error: {response.status_code} - {response.text}")

        except requests.RequestException as e:
            return (f"Request failed: {e}")

    def fetch_contacts(self):
        # API endpoint
        url = "https://sandbox.api.sap.com/subscriptionbilling/api/business-partner/v3/contacts"

        # Query parameters
        params = {
            "$count": "true",
            "pageSize": "10"
        }

        # Headers (replace with your API Key)
        headers = {
            "APIKey": self.api_key,
            "Accept": "application/json",
            "DataServiceVersion": "2.0"
        }

        try:
            # Send GET request
            response = requests.get(url, headers=headers, params=params)

            # Check for successful response
            if response.status_code == 200:
                customers = response.json()
                return customers
            else:
                return (f"Error: {response.status_code} - {response.text}")

        except requests.RequestException as e:
            return (f"Request failed: {e}")


    def fetch_contact_ID(self,contact_id):
        # 127378839
        # API endpoint
        url = f"https://sandbox.api.sap.com/subscriptionbilling/api/business-partner/v3/contacts/{contact_id}"

        # Query parameters
        params = {
            "$count": "true",
            "pageSize": "10"
        }

        # Headers (replace with your API Key)
        headers = {
            "APIKey": self.api_key,
            "Accept": "application/json",
            "DataServiceVersion": "2.0"
        }

        try:
            # Send GET request
            response = requests.get(url, headers=headers, params=params)

            # Check for successful response
            if response.status_code == 200:
                customers = response.json()
                return customers
            else:
                return (f"Error: {response.status_code} - {response.text}")

        except requests.RequestException as e:
            return (f"Request failed: {e}")

    def fetch_relations(self):
    # API endpoint
        url = "https://sandbox.api.sap.com/subscriptionbilling/api/business-partner/v3/relationships/customer-contacts"

        # Query parameters
        params = {
            "$count": "true",
            "pageSize": "10"
        }

        # Headers (replace with your API Key)
        headers = {
            "APIKey": self.api_key,
            "Accept": "application/json",
            "DataServiceVersion": "2.0"
        }

        try:
            # Send GET request
            response = requests.get(url, headers=headers, params=params)

            # Check for successful response
            if response.status_code == 200:
                customers = response.json()
                return customers
            else:
                return (f"Error: {response.status_code} - {response.text}")

        except requests.RequestException as e:
            return (f"Request failed: {e}")


    def fetch_relation_ID(self,customer_id):
    # 3176169607
    # API endpoint
        url = f"https://sandbox.api.sap.com/subscriptionbilling/api/business-partner/v3/relationships/customer-contacts/{customer_id}"

        # Query parameters
        params = {
            "$count": "true",
            "pageSize": "10"
        }

        # Headers (replace with your API Key)
        headers = {
            "APIKey": self.api_key,
            "Accept": "application/json",
            "DataServiceVersion": "2.0"
        }

        try:
            # Send GET request
            response = requests.get(url, headers=headers, params=params)

            # Check for successful response
            if response.status_code == 200:
                customers = response.json()
                return customers
            else:
                return (f"Error: {response.status_code} - {response.text}")

        except requests.RequestException as e:
            return (f"Request failed: {e}")
