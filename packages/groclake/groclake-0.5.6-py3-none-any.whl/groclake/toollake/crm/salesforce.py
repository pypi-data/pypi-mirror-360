"""
Salesforce CRM implementation using simple-salesforce
"""

import re
from simple_salesforce import Salesforce as SimpleSalesforce
from typing import Dict, Any
class Salesforce:
    def __init__(self, tool_config: Dict[str, Any]):
        """Initialize Salesforce connection using simple-salesforce"""
        self.tool_config = tool_config
        self.username = tool_config.get("username")
        self.password = tool_config.get("password")
        self.security_token = tool_config.get("security_token")
        self.sf = SimpleSalesforce(
            username=self.username,
            password=self.password,
            security_token=self.security_token
        )

    def _validate_email(self, email):
        """Validate email format"""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(email_pattern, str(email)))

    def _validate_phone(self, phone):
        """Validate phone number format"""
        # Remove any non-digit characters
        phone_digits = re.sub(r'\D', '', str(phone))
        # Check if the number has at least 10 digits
        return len(phone_digits) >= 10

    def _validate_name(self, name):
        """Validate name format"""
        # Check if name is not empty and contains only letters, spaces, and hyphens
        return bool(name and re.match(r'^[a-zA-Z\s-]+$', str(name)))

    def _validate_company(self, company):
        """Validate company name"""
        # Company name should not be empty and should be at least 2 characters
        return bool(company and len(str(company).strip()) >= 2)

    def _validate_fields(self, payload, required_fields):
        """Validate all required fields and their formats"""
        errors = []
        
        # Check for missing fields
        missing_fields = [field for field in required_fields if not payload.get(field)]
        if missing_fields:
            errors.append(f"Missing required fields: {', '.join(missing_fields)}")

        # Validate formats if fields are present
        if 'Email' in payload and payload['Email']:
            if not self._validate_email(payload['Email']):
                errors.append("Invalid email format")

        if 'Phone' in payload and payload['Phone']:
            if not self._validate_phone(payload['Phone']):
                errors.append("Invalid phone number format (should have at least 10 digits)")

        if 'FirstName' in payload and payload['FirstName']:
            if not self._validate_name(payload['FirstName']):
                errors.append("Invalid FirstName format (should contain only letters, spaces, and hyphens)")

        if 'LastName' in payload and payload['LastName']:
            if not self._validate_name(payload['LastName']):
                errors.append("Invalid LastName format (should contain only letters, spaces, and hyphens)")

        if 'Company' in payload and payload['Company']:
            if not self._validate_company(payload['Company']):
                errors.append("Invalid Company name (should be at least 2 characters)")

        return errors

    def create_lead(self, payload):
        """Create a new lead with validation"""
        required_fields = ["FirstName", "LastName", "Email", "Company", "Phone"]
        
        # Validate all fields
        validation_errors = self._validate_fields(payload, required_fields)
        if validation_errors:
            print("Validation errors:")
            for error in validation_errors:
                print(f"- {error}")
            return None

        # Check for existing lead
        existing_lead = self.fetch_lead(payload['Email'])
        if existing_lead:
            print(f"Lead with Email {payload['Email']} already exists. ID: {existing_lead['Id']}")
            return existing_lead['Id']

        try:
            # Clean phone number before sending
            if 'Phone' in payload:
                payload['Phone'] = re.sub(r'\D', '', str(payload['Phone']))
            payload['Status'] = 'Open - Not Contacted'
            result = self.sf.Lead.create(payload)
            if result.get('success'):
                lead_id = result['id']
                print(f"Lead Created Successfully, ID: {lead_id}")
                return lead_id
            else:
                print(f"Error creating lead: {result}")
                return None
        except Exception as e:
            print(f"Error creating lead: {e}")
            return None

    def create_account(self, company_name, industry="Unknown"):
        """Create a new account or fetch existing one"""
        # Validate company name
        if not self._validate_company(company_name):
            print("Invalid company name (should be at least 2 characters)")
            return None

        try:
            # Check for existing account
            existing_account = self.fetch_account(company_name)
            if existing_account:
                return existing_account['Id']

            # Create new account
            account_data = {
                'Name': company_name,
                'Industry': industry,
                'Type': 'Customer'
            }
            result = self.sf.Account.create(account_data)
            if result.get('success'):
                account_id = result['id']
                print(f"Account Created Successfully for {company_name}, ID: {account_id}")
                return account_id
            else:
                print(f"Error creating account: {result}")
                return None
        except Exception as e:
            print(f"Error in account creation: {e}")
            return None

    def create_customer(self, payload):
        """Create a new customer (Contact) with account handling"""
        required_fields = ["FirstName", "LastName", "Email", "Phone", "Company"]
        
        # Validate all fields
        validation_errors = self._validate_fields(payload, required_fields)
        if validation_errors:
            print("Validation errors:")
            for error in validation_errors:
                print(f"- {error}")
            return None

        try:
            # Check for existing customer
            existing_customer = self.fetch_customer(payload['Email'])
            if existing_customer:
                print(f"Customer with Email {payload['Email']} already exists. ID: {existing_customer['Id']}")
                return existing_customer['Id']

            # Handle Account
            account_id = self.create_account(payload['Company'], payload.get('Industry', 'Unknown'))
            if not account_id:
                print("Failed to create/fetch account")
                return None

            # Clean phone number before sending
            if 'Phone' in payload:
                payload['Phone'] = re.sub(r'\D', '', str(payload['Phone']))

            # Create Contact
            contact_data = {
                "FirstName": payload['FirstName'],
                "LastName": payload['LastName'],
                "Email": payload['Email'],
                "Phone": payload['Phone'],
                "AccountId": account_id
            }

            result = self.sf.Contact.create(contact_data)
            if result.get('success'):
                contact_id = result['id']
                print(f"Customer Created Successfully, ID: {contact_id}")
                return contact_id
            else:
                print(f"Error creating customer: {result}")
                return None
        except Exception as e:
            print(f"Error creating customer: {e}")
            return None

    def fetch_lead(self, email):
        """Fetch a lead by email"""
        if not self._validate_email(email):
            print("Invalid email format")
            return None

        query = f"SELECT Id, FirstName, LastName, Company, Email, Phone, Status FROM Lead WHERE Email = '{email}' LIMIT 1"
        result = self.sf.query(query)
        if result['records']:
            return result['records'][0]
        return None

    def fetch_customer(self, email):
        """Fetch a customer by email"""
        if not self._validate_email(email):
            print("Invalid email format")
            return None

        query = f"SELECT Id, FirstName, LastName, Email, Phone, AccountId FROM Contact WHERE Email = '{email}' LIMIT 1"
        result = self.sf.query(query)
        if result['records']:
            return result['records'][0]
        return None

    def fetch_account(self, company_name):
        """Fetch an account by company name"""
        if not self._validate_company(company_name):
            print("Invalid company name")
            return None

        try:
            # First try exact match
            query = f"SELECT Id, Name, Industry, Type FROM Account WHERE Name = '{company_name}' LIMIT 1"
            result = self.sf.query(query)
            
            if result['records']:
                return result['records'][0]
            
            # If no exact match, try LIKE query
            like_query = f"SELECT Id, Name, Industry, Type FROM Account WHERE Name LIKE '%{company_name}%' LIMIT 1"
            like_result = self.sf.query(like_query)
            
            if like_result['records']:
                return like_result['records'][0]
            
            print(f"No account found with name: {company_name}")
            return None

        except Exception as e:
            print(f"Error fetching account: {e}")
            return None

    def fetch_account_leads(self, company_name):
        """Fetch all leads for a company"""
        if not self._validate_company(company_name):
            print("Invalid company name")
            return []

        query = f"SELECT Id, FirstName, LastName, Email, Phone, Status FROM Lead WHERE Company = '{company_name}'"
        result = self.sf.query(query)
        return result['records']

    def fetch_account_customers(self, account_id):
        """Fetch all customers (contacts) for an account"""
        if not account_id or not isinstance(account_id, str) or len(account_id) < 15:
            print("Invalid account ID")
            return []

        query = f"SELECT Id, FirstName, LastName, Email, Phone FROM Contact WHERE AccountId = '{account_id}'"
        result = self.sf.query(query)
        return result['records'] 