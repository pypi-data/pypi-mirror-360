import requests
import time
import os
from typing import Dict, Any

class Datadog:
    def __init__(self, tool_config: Dict[str, Any]):
        """
        Initialize Datadog connection with tool configuration.
        
        Expected tool_config format:
        {
            'api_key': 'api_key',
            'app_key': 'app_key'
        }
        """
        self.tool_config = tool_config
        self.api_key = tool_config.get("api_key")
        self.app_key = tool_config.get("app_key")
        self.headers = {
            "DD-API-KEY": self.api_key,
            "DD-APPLICATION-KEY": self.app_key,
            "Content-Type": "application/json"
        }
        self.base_url = "https://api.us5.datadoghq.com"


    def fetch_metrics(self, payload):
        url = f"{self.base_url}/api/v1/query"
        params = {
            "from": payload.get('from_time'),
            "to": payload.get("to_time"),
            "query": payload.get("query")
        }
        response = requests.get(url, headers=self.headers, params=params)
        otel_data=self.convert_to_otel(response.json())
        return otel_data


    def convert_to_otel(self, datadog_response):
        otel_metrics = []

        for series in datadog_response.get("series", []):
            tags_dict = {}
            for tag in series.get("tags", []):
                if ":" in tag:
                    k, v = tag.split(":", 1)
                    tags_dict[k] = v

            service = tags_dict.get("service", "unknown-service")
            env = tags_dict.get("env", "unknown-env")
            operation = tags_dict.get("operation")

            data_points = []
            for ts, val in series.get("pointlist", []):
                data_points.append({
                    "attributes": [{"key": "operation", "value": operation}] if operation else [],
                    "timeUnixNano": str(ts * 1_000_000),  # ns
                    "value": val
                })

            metric = {
                "resourceMetrics": [{
                    "resource": {
                        "attributes": [
                            {"key": "service.name", "value": service},
                            {"key": "deployment.environment", "value": env}
                        ]
                    },
                    "scopeMetrics": [{
                        "scope": {
                            "name": "custom.datadog.converter",
                            "version": "1.0"
                        },
                        "metrics": [{
                            "name": series["metric"],
                            "description": "Converted from Datadog",
                            "unit": series.get("unit", [""])[0],
                            "type": "gauge",
                            "data": {
                                "dataPoints": data_points
                            }
                        }]
                    }]
                }]
            }

            otel_metrics.append(metric)

        return otel_metrics

