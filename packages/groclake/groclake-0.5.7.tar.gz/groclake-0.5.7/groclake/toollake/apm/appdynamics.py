import requests
import json
import xml.etree.ElementTree as ET
import datetime
import os
from typing import Dict, Any

class AppDynamics:
    def __init__(self, tool_config: Dict[str, Any]):
        self.tool_config = tool_config
        self.controller_url = tool_config.get("controller_url").rstrip('/')
        self.username = tool_config.get("username")
        self.password = tool_config.get("password")
        self.debug = tool_config.get("debug")

    def print_debug(self, message):
        """Print debug messages if debug mode is enabled"""
        if self.debug:
            current_time = datetime.datetime.now().strftime("%H:%M:%S")
            print(f"[DEBUG {current_time}] {message}")

    def parse_xml(self, xml_string):
        """Parse XML string and convert it to a list of dictionaries"""
        root = ET.fromstring(xml_string)
        result = []

        # Check if it's an applications list
        if root.tag == 'applications':
            for app in root.findall('./application'):
                app_dict = {child.tag: child.text for child in app}
                result.append(app_dict)
        else:
            # Default case for unknown XML structure
            for child in root:
                child_dict = {subchild.tag: subchild.text for subchild in child}
                result.append(child_dict)

        return result

    def make_api_request(self, method, endpoint, params=None, data=None):

        url = f"{self.controller_url}{endpoint}"
        headers = {"Accept": "application/json"}

        try:
            response = requests.request(method, url, headers=headers, params=params, json=data,
                                        auth=(self.username, self.password))

            if response.status_code == 200:
                if response.text.strip():
                    content_type = response.headers.get('Content-Type', '')
                    if 'application/json' in content_type:
                        return response.json()
                    elif 'application/xml' in content_type:
                        return self.parse_xml(response.text)
                    else:
                        return self.parse_xml(response.text)  # Fallback to XML parsing
                return []  # Return empty list for empty responses
            else:
                raise Exception(f"API request failed: {response.status_code} - {response.text}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request error: {e}")

    def get_applications(self):
        """Get list of all applications"""
        return self.make_api_request('get', '/controller/rest/applications')

    def get_metric_data(self, application_id, metric_path, start_time=None, end_time=None,
                        time_range_type="BEFORE_NOW", duration_in_mins=1440, rollup=True):
        """
        Get metric data for the specified application and metric path
        """
        params = {
            "metric-path": metric_path,
            "time-range-type": time_range_type,
            "output": "JSON"
        }

        if start_time and end_time:
            params["start-time"] = start_time
            params["end-time"] = end_time
        else:
            params["duration-in-mins"] = duration_in_mins

        if rollup:
            params["rollup"] = "true"

        return self.make_api_request('get', f'/controller/rest/applications/{application_id}/metric-data',
                                     params=params)



