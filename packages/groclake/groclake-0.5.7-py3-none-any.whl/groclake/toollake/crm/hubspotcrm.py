import hubspot
from hubspot.crm.pipelines import PipelineInput, ApiException as PipelineApiException
from hubspot.crm.owners import ApiException as OwnersApiException
from hubspot.crm.contacts import SimplePublicObjectInputForCreate, PublicObjectSearchRequest, ApiException as ContactsApiException
import requests
from typing import Dict, Any

class Hubspot:
    def __init__(self, tool_config: Dict[str, Any]):
        self.access_token = tool_config.get("access_token")
        if not self.access_token:
            raise ValueError("HUBSPOT_ACCESS_TOKEN not set in environment variables.")
        self.client = hubspot.Client.create(access_token=self.access_token)

    def get_all_pipelines(self, object_type):
        try:
            return self.client.crm.pipelines.pipelines_api.get_all(object_type=object_type)
        except PipelineApiException as e:
            return {"error": f"Exception when calling pipelines_api->get_all: {e}"}

    def get_pipeline_by_id(self, object_type, pipeline_id):
        try:
            return self.client.crm.pipelines.pipelines_api.get_by_id(object_type=object_type, pipeline_id=pipeline_id)
        except PipelineApiException as e:
            return {"error": f"Exception when calling pipelines_api->get_by_id: {e}"}

    def create_pipeline(self, object_type, pipeline_input_dict):
        pipeline_input = PipelineInput(**pipeline_input_dict)
        try:
            return self.client.crm.pipelines.pipelines_api.create(object_type=object_type, pipeline_input=pipeline_input)
        except PipelineApiException as e:
            return {"error": f"Exception when calling pipelines_api->create: {e}"}

    def get_owners(self, limit=100, archived=False):
        try:
            return self.client.crm.owners.owners_api.get_page(limit=limit, archived=archived)
        except OwnersApiException as e:
            return {"error": f"Exception when calling owners_api->get_page: {e}"}

    def create_contact(self, properties):
        simple_public_object_input_for_create = SimplePublicObjectInputForCreate(
            properties=properties
        )
        try:
            return self.client.crm.contacts.basic_api.create(
                simple_public_object_input_for_create=simple_public_object_input_for_create
            )
        except ContactsApiException as e:
            return {"error": f"Exception when calling basic_api->create: {e}"}

    def get_contacts(self, limit=10, archived=False):
        try:
            return self.client.crm.contacts.basic_api.get_page(limit=limit, archived=archived)
        except ContactsApiException as e:
            return {"error": f"Exception when calling basic_api->get_page: {e}"}

    def search_contacts(self, search_payload):
        public_object_search_request = PublicObjectSearchRequest(**search_payload)
        try:
            return self.client.crm.contacts.search_api.do_search(
                public_object_search_request=public_object_search_request
            )
        except ContactsApiException as e:
            return {"error": f"Exception when calling search_api->do_search: {e}"}

    def get_leads(self, limit=10, archived=False):
        url = "https://api.hubapi.com/crm/v3/objects/leads"
        headers = {
            'accept': "application/json",
            'authorization': f"Bearer {self.access_token}"
        }
        params = {"limit": str(limit), "archived": str(archived).lower()}
        response = requests.get(url, headers=headers, params=params)
        try:
            return response.json()
        except Exception:
            return {"error": response.text}

    def create_lead(self, properties, associations=None):
        url = "https://api.hubapi.com/crm/v3/objects/leads"
        headers = {
            'accept': "application/json",
            'content-type': "application/json",
            'authorization': f"Bearer {self.access_token}"
        }
        payload = {
            "associations": associations or [],
            "properties": properties
        }
        response = requests.post(url, json=payload, headers=headers)
        try:
            return response.json()
        except Exception:
            return {"error": response.text}

# 