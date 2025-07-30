from typing import Dict, Any, List
from datetime import datetime, timedelta
import numpy as np
import random

class Grocmock:
    def __init__(self, tool_config: Dict[str, Any]):
        """
        Initialize Grocmock connection with tool configuration.
        """
        self.tool_config = tool_config

    def get_duration_in_seconds(self, duration_str):
        """Convert '5 min' or '2 hour' to seconds."""
        value, unit = duration_str.strip().split()
        value = int(value)
        unit = unit.lower()
        if unit in ['sec', 'second', 'seconds', 'secs']:
            return value
        elif unit in ['min', 'minute', 'minutes', 'mins']:
            return value * 60
        elif unit in ['hour', 'hours', 'hrs']:
            return value * 3600
        elif unit in ['day', 'days', 'dys']:
            return value * 86400
        else:
            raise ValueError(f"Unsupported unit: {unit}")

    def generate_grocmock_data_timeseries(self, grocmock_payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate grocmock data for timeseries with anomalies.
        """
        grocmock_config = grocmock_payload.get("grocmock_config", {})

        aggregation_interval = grocmock_payload.get('aggregation_interval', '1 min')
        lookback_window = grocmock_payload.get('lookback_window', '1 hour')
        grocmock_config_enhanced = grocmock_payload.get('grocmock_config_enhanced', {})
        y_value_min_enhanced = grocmock_config_enhanced.get('y_value_min', 0)
        y_value_max_enhanced = grocmock_config_enhanced.get('y_value_max', 100)
        y_value_mean_enhanced = grocmock_config_enhanced.get('y_value_mean', (y_value_min_enhanced + y_value_max_enhanced) / 2)
        y_value_base_data_profile_enhanced = grocmock_config_enhanced.get('y_value_base_data_profile', 'gaussian')
        y_value_base_data_std_dev_enhanced = grocmock_config_enhanced.get('y_value_base_data_std_dev', 10)
        anomaly_duration_enhanced = grocmock_config_enhanced.get('anomaly_duration', '1 min')
        anomaly_percentage_enhanced = grocmock_config_enhanced.get('anomaly_percentage', 10)
        anomaly_type_enhanced = grocmock_config_enhanced.get("anomaly_type", "")
        
        y_value_min = grocmock_config.get('y_value_min', y_value_min_enhanced)
        y_value_max = grocmock_config.get('y_value_max', y_value_max_enhanced)
        y_value_mean = grocmock_config.get('y_value_mean', y_value_mean_enhanced)
        y_value_base_data_profile = grocmock_config.get('y_value_base_data_profile', y_value_base_data_profile_enhanced)
        y_value_base_data_std_dev = grocmock_config.get('y_value_base_data_std_dev', y_value_base_data_std_dev_enhanced)

        anomaly_duration = grocmock_config.get('anomaly_duration', anomaly_duration_enhanced)
        anomaly_percentage = grocmock_config.get('anomaly_percentage', anomaly_percentage_enhanced)
        anomaly_type = grocmock_config.get("anomaly_type", anomaly_type_enhanced).lower()
        
        aggregation_interval_seconds = self.get_duration_in_seconds(aggregation_interval)
        lookback_window_seconds = self.get_duration_in_seconds(lookback_window)
        anomaly_duration_seconds = self.get_duration_in_seconds(anomaly_duration)

        num_points = int(lookback_window_seconds / aggregation_interval_seconds)
        anomaly_duration_num_points = max(1, int(anomaly_duration_seconds / aggregation_interval_seconds))
        total_anomaly_points = max(1, int(anomaly_percentage * num_points / 100))
        num_anomaly_blocks = max(1, int(total_anomaly_points / anomaly_duration_num_points))

        x_value_end = grocmock_config.get('x_value_end', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        end_time = datetime.strptime(x_value_end, '%Y-%m-%d %H:%M:%S') if x_value_end else datetime.now()
        start_time = end_time - timedelta(seconds=lookback_window_seconds)

        timestamps = [start_time + timedelta(seconds=i * aggregation_interval_seconds) for i in range(num_points)]

        # Generate base values
        if y_value_base_data_profile == 'gaussian':
            values = np.random.normal(loc=y_value_mean, scale=y_value_base_data_std_dev, size=num_points)
        elif y_value_base_data_profile == 'uniform':
            values = np.random.uniform(low=y_value_min, high=y_value_max, size=num_points)
        elif y_value_base_data_profile == 'sinusoidal':
            values = y_value_mean + y_value_base_data_std_dev * np.sin(np.linspace(0, 6.28, num_points))
        elif y_value_base_data_profile == 'poisson':
            values = np.random.poisson(lam=y_value_mean, size=num_points)
        else:
            raise ValueError(f"Unsupported base profile: {y_value_base_data_profile}")

        # Inject anomalies
        anomaly_indices = set()
        for _ in range(num_anomaly_blocks):
            start_idx = random.randint(0, num_points - anomaly_duration_num_points)
            for j in range(anomaly_duration_num_points):
                idx = start_idx + j
                anomaly_indices.add(idx)
                if anomaly_type == "spike":
                    values[idx] += y_value_max * 1
                elif anomaly_type == "drop":
                    values[idx] -= y_value_max * 1
                elif anomaly_type == "ramp_up" and idx + anomaly_duration_num_points < num_points:
                    values[idx] += y_value_base_data_std_dev * 10
                elif anomaly_type == "ramp_down" and idx + anomaly_duration_num_points < num_points:
                    values[idx] -= y_value_base_data_std_dev * 10

        # Clamp values
        values = np.clip(values, y_value_min, y_value_max)

        # Package result
        result = []
        for i in range(num_points):
            result.append({
                "x_value": timestamps[i].strftime('%Y-%m-%d %H:%M:%S'),
                "y_value": round(float(values[i]), 2),
                "ground_truth_anomaly": "true" if i in anomaly_indices else "false",
                "num_points": num_points,
                "num_anomaly_blocks": num_anomaly_blocks,
                "anomaly_duration_num_points": anomaly_duration_num_points,
                "total_anomaly_points": total_anomaly_points,
                "anomaly_percentage": anomaly_percentage,
                "aggregation_interval_seconds": aggregation_interval_seconds,
                "lookback_window_seconds": lookback_window_seconds,
                "anomaly_duration_seconds": anomaly_duration_seconds,
                "anomaly_type": anomaly_type,
                "anomaly_type_enhanced": anomaly_type_enhanced,
                "y_value_min": y_value_min,
                "y_value_max": y_value_max,
                "y_value_mean": y_value_mean,
                "y_value_base_data_profile": y_value_base_data_profile,
                "y_value_base_data_std_dev": y_value_base_data_std_dev,
                "anomaly_duration": anomaly_duration,
                "anomaly_percentage": anomaly_percentage,
                "aggregation_interval": aggregation_interval,
                "lookback_window": lookback_window,
                "anomaly_indices": list(anomaly_indices),
            })

        grocmock_payload['data'] = result
        grocmock_payload['status'] = "success"
        return grocmock_payload
    
    def generate_grocmock_data_snapshot(self, grocmock_payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate grocmock data for snapshot with anomalies.
        """
        grocmock_config = grocmock_payload.get("grocmock_config", {})
        anomaly_type = grocmock_config.get("anomaly_type", "").lower()
        anomaly_usecase = grocmock_config.get("anomaly_usecase", "").lower()

        grocmock_payload['data'] = []

        if anomaly_usecase == "employee_expense_anomaly":
            grocmock_payload['data'] = self.generate_employee_expense_anomaly(grocmock_payload)
        else:
            grocmock_payload['data'] = []

        grocmock_payload['status'] = "success"
        return grocmock_payload
    
    def generate_employee_expense_anomaly(self, grocmock_payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate mock data for employee expense anomaly detection.
        
        Args:
            grocmock_payload (Dict[str, Any]): Configuration payload containing
                grocmock_config and grocmock_config_enhanced settings.
                
        Returns:
            List[Dict[str, Any]]: List of expense records with anomaly flags.
                Each record contains expense details with ground_truth_anomaly field.
        """
        # Extract configuration (currently unused but available for future customization)
        grocmock_config = grocmock_payload.get("grocmock_config", {})
        grocmock_config_enhanced = grocmock_payload.get('grocmock_config_enhanced', {})

        expense_data = [
            {
                "expense_id": "EXP001",
                "employee_name": "Manoj Gupta",
                "employee_id": "EMP1001",
                "department": "Engineering",
                "expense_date": "2025-06-01",
                "expense_type": "travel",
                "amount": 1500.00,
                "currency": "USD",
                "ground_truth_anomaly": True,
                "anomaly_reason": "Amount exceeds policy limit"
            },
            {
                "expense_id": "EXP002",
                "employee_name": "Manoj Gupta",
                "employee_id": "EMP1001",
                "department": "Engineering",
                "expense_date": "2025-06-02",
                "expense_type": "meals",
                "amount": 200.00,
                "currency": "USD",
                "ground_truth_anomaly": True,
                "anomaly_reason": "Unusually high meal expense"
            },
            {
                "expense_id": "EXP003",
                "employee_name": "Manoj Gupta",
                "employee_id": "EMP1001",
                "department": "Engineering",
                "expense_date": "2025-06-03",
                "expense_type": "misc",
                "amount": 850.00,
                "currency": "USD",
                "ground_truth_anomaly": True,
                "anomaly_reason": "Expense type flagged as suspicious"
            },
            {
                "expense_id": "EXP004",
                "employee_name": "Monica Gupta",
                "employee_id": "EMP1002",
                "department": "Product",
                "expense_date": "2025-06-01",
                "expense_type": "accommodation",
                "amount": 2500.00,
                "currency": "USD",
                "ground_truth_anomaly": True,
                "anomaly_reason": "Accommodation limit exceeded"
            },
            {
                "expense_id": "EXP005",
                "employee_name": "Monica Gupta",
                "employee_id": "EMP1002",
                "department": "Product",
                "expense_date": "2025-06-02",
                "expense_type": "meals",
                "amount": 180.00,
                "currency": "USD",
                "ground_truth_anomaly": True,
                "anomaly_reason": "Exceeds daily meal threshold"
            },
            {
                "expense_id": "EXP006",
                "employee_name": "Monica Gupta",
                "employee_id": "EMP1002",
                "department": "Product",
                "expense_date": "2025-06-03",
                "expense_type": "travel",
                "amount": 1300.00,
                "currency": "USD",
                "ground_truth_anomaly": True,
                "anomaly_reason": "Flight cost outlier for route"
            },
            {
                "expense_id": "EXP007",
                "employee_name": "Tarun Nagpal",
                "employee_id": "EMP2001",
                "department": "Marketing",
                "expense_date": "2025-06-05",
                "expense_type": "travel",
                "amount": 300.00,
                "currency": "USD",
                "ground_truth_anomaly": False,
                "anomaly_reason": None
            },
            {
                "expense_id": "EXP008",
                "employee_name": "Tarun Nagpal",
                "employee_id": "EMP2001",
                "department": "Marketing",
                "expense_date": "2025-06-06",
                "expense_type": "meals",
                "amount": 45.00,
                "currency": "USD",
                "ground_truth_anomaly": False,
                "anomaly_reason": None
            },
            {
                "expense_id": "EXP009",
                "employee_name": "Tarun Nagpal",
                "employee_id": "EMP2001",
                "department": "Marketing",
                "expense_date": "2025-06-07",
                "expense_type": "misc",
                "amount": 60.00,
                "currency": "USD",
                "ground_truth_anomaly": False,
                "anomaly_reason": None
            },
            {
                "expense_id": "EXP010",
                "employee_name": "Neha Vats",
                "employee_id": "EMP2002",
                "department": "Finance",
                "expense_date": "2025-06-05",
                "expense_type": "accommodation",
                "amount": 800.00,
                "currency": "USD",
                "ground_truth_anomaly": False,
                "anomaly_reason": None
            },
            {
                "expense_id": "EXP011",
                "employee_name": "Neha Vats",
                "employee_id": "EMP2002",
                "department": "Finance",
                "expense_date": "2025-06-06",
                "expense_type": "meals",
                "amount": 50.00,
                "currency": "USD",
                "ground_truth_anomaly": False,
                "anomaly_reason": None
            },
            {
                "expense_id": "EXP012",
                "employee_name": "Neha Vats",
                "employee_id": "EMP2002",
                "department": "Finance",
                "expense_date": "2025-06-07",
                "expense_type": "travel",
                "amount": 400.00,
                "currency": "USD",
                "ground_truth_anomaly": False,
                "anomaly_reason": None
            }
        ]
        
        return expense_data

    
