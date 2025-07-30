import os
import time
import json
import requests
import datetime
import pytz
from dotenv import load_dotenv
from typing import Dict, List, Optional, Any

# Load environment variables from .env file
load_dotenv()


class Instana:
    def __init__(self, tool_config: Dict[str, Any]):
        self.tool_config = tool_config
        self.api_token = tool_config.get("api_token")
        self.base_url = tool_config.get("base_url")
        self.headers = {
            "Authorization": f"apiToken {self.api_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "instana-api-client/1.0"
        }

    def _make_request(self, url: str, payload: Dict, params: Optional[Dict] = None) -> Dict:
        """Common method for making API requests with error handling"""
        try:
            response = requests.post(
                url,
                headers=self.headers,
                params=params,
                json=payload
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as err:
            print(f"Error Response: {response.text}")
            raise err

    def _get_current_time(self) -> int:
        """Get the current time in milliseconds since the Unix epoch in IST"""
        # Get the current time in UTC
        utc_now = datetime.datetime.now(pytz.utc)

        # Convert to IST
        ist_now = utc_now.astimezone(pytz.timezone('Asia/Kolkata'))

        # Convert to milliseconds since the Unix epoch
        return int(ist_now.timestamp() * 1000)

    def _get_time_frame(self, granularity: int, time_frame: int) -> Dict:
        """Calculate time frame parameters based on the specified time frame in hours"""
        current_time = self._get_current_time()
        total_duration_seconds = time_frame * 60 * 60  # Convert hours to seconds

        min_window_size = 2 * granularity  # Granularity should be in seconds
        if total_duration_seconds < min_window_size:
            raise ValueError(f"Total duration must be at least twice the granularity: {min_window_size} seconds.")

        window_size_ms = total_duration_seconds * 1000  # Total duration in milliseconds

        return {
            "to": current_time,
            "windowSize": window_size_ms
        }

    def _build_metric_config(self, metrics: List[str], aggregation: str, granularity: int) -> List[Dict]:
        """Build metric configuration array"""
        return [
            {
                "metric": metric,
                "aggregation": aggregation,
                "granularity": granularity
            }
            for metric in metrics
        ]

    def get_application_metrics(
            self,
            application_id: str,
            metrics: List[str],
            aggregation: str = "MEAN",
            granularity: int = 300,
            time_frame: int = 1,  # Time frame in hours, default is 1 hour
            fill_time_series: bool = True,
            boundary_scope: str = "ALL",
            service_id: Optional[str] = None,
            endpoint_id: Optional[str] = None,
            endpoint_types: Optional[List[str]] = None,
            name_filter: Optional[str] = None
    ) -> Dict:
        """Get application metrics from Instana API"""
        url = f"{self.base_url}/api/application-monitoring/metrics/applications"

        # Build base payload
        payload = {
            "applicationId": application_id,
            "applicationBoundaryScope": boundary_scope,
            "metrics": self._build_metric_config(metrics, aggregation, granularity),
            "timeFrame": self._get_time_frame(granularity, time_frame)  # Pass time_frame to get_time_frame
        }

        # Add optional fields
        optional_fields = {
            "serviceId": service_id,
            "endpointId": endpoint_id,
            "endpointTypes": endpoint_types,
            "nameFilter": name_filter
        }
        payload.update({k: v for k, v in optional_fields.items() if v is not None})

        params = {"fillTimeSeries": str(fill_time_series).lower()}

        return self._make_request(url, payload, params)

    def get_endpoint_metrics(
            self,
            application_id: str,
            metrics: List[str],
            aggregation: str = "MEAN",
            granularity: int = 300,
            time_frame: int = 1,  # Time frame in hours, default is 1 hour
            fill_time_series: bool = True,
            application_boundary_scope: str = "ALL",
            endpoint_id: Optional[str] = None,
            endpoint_types: Optional[List[str]] = None,
            service_id: Optional[str] = None,
            name_filter: Optional[str] = None,
            exclude_synthetic: bool = False
    ) -> Dict:
        """Get endpoint metrics from Instana API"""
        url = f"{self.base_url}/api/application-monitoring/metrics/endpoints"

        payload = {
            "applicationId": application_id,
            "applicationBoundaryScope": application_boundary_scope,
            "metrics": self._build_metric_config(metrics, aggregation, granularity),
            "timeFrame": self._get_time_frame(granularity, time_frame),
            "excludeSynthetic": exclude_synthetic
        }

        # Add optional fields
        optional_fields = {
            "endpointId": endpoint_id,
            "endpointTypes": endpoint_types,
            "serviceId": service_id,
            "nameFilter": name_filter
        }
        payload.update({k: v for k, v in optional_fields.items() if v is not None})

        params = {"fillTimeSeries": str(fill_time_series).lower()}

        return self._make_request(url, payload, params)

    def get_v2_metrics(
            self,
            metrics: List[str],
            aggregation: str = "MEAN",
            granularity: int = 300,
            time_frame: int = 1,  # Time frame in hours, default is 1 hour
            include_internal: bool = False,
            include_synthetic: bool = False,
            tag_filter_expression: Optional[str] = None
    ) -> Dict:
        """Get v2 metrics from Instana API"""
        url = f"{self.base_url}/api/application-monitoring/v2/metrics"

        payload = {
            "metrics": self._build_metric_config(metrics, aggregation, granularity),
            "timeFrame": self._get_time_frame(granularity, time_frame),
            "includeInternal": include_internal,
            "includeSynthetic": include_synthetic
        }

        if tag_filter_expression:
            payload["tagFilterExpression"] = tag_filter_expression

        return self._make_request(url, payload)

    def get_service_metrics(
            self,
            service_id: str,
            metrics: List[str],
            aggregation: str = "MEAN",
            granularity: int = 300,
            time_frame: int = 1,  # Time frame in hours, default is 1 hour
            fill_time_series: bool = True,
            application_id: Optional[str] = None,
            application_boundary_scope: Optional[str] = None,
            context_scope: str = "NONE",
            technologies: Optional[List[str]] = None
    ) -> Dict:
        """Get service metrics from Instana API"""
        url = f"{self.base_url}/api/application-monitoring/metrics/services"

        payload = {
            "serviceId": service_id,
            "metrics": self._build_metric_config(metrics, aggregation, granularity),
            "timeFrame": self._get_time_frame(granularity, time_frame),
            "contextScope": context_scope
        }

        # Add optional fields
        optional_fields = {
            "applicationId": application_id,
            "applicationBoundaryScope": application_boundary_scope,
            "technologies": technologies
        }
        payload.update({k: v for k, v in optional_fields.items() if v is not None})

        params = {"fillTimeSeries": str(fill_time_series).lower()}

        return self._make_request(url, payload, params)



