from sklearn.ensemble import IsolationForest
from typing import List, Dict, Any

class AnomalyDetector:
    def __init__(self, n_estimators=100, contamination=0.1):
        self.model = IsolationForest(n_estimators=n_estimators, contamination=contamination)

    def fit(self, X):
        self.model.fit(X)

    def predict(self, X):
        return self.model.predict(X)

    def anomaly_scores(self, X):
        return self.model.decision_function(X)

    def anomaly_detection_z_score(self, data: List[Dict[str, Any]], threshold: float = 1.5) -> List[Dict[str, Any]]:
        """
        Detect anomalies in time series data using z-score algorithm.
        
        Args:
            data: List of dictionaries containing time series data points with format:
                {
                    "x_value": str,  # timestamp
                    "y_value": float,  # metric value
                    "is_anomaly": bool  # will be updated by this method
                }
            threshold: Z-score threshold for anomaly detection (default: 2.0)
                - Values with |z-score| > threshold are considered anomalies
                - Higher threshold = fewer anomalies detected
        
        Returns:
            List of data points with updated is_anomaly flags
        """

        total_anomalies_detected = 0

        anomaly_summary = {
            "detection_method": "z_score",
            "total_anomalies_detected": total_anomalies_detected,
            "anomaly_type": "spike",
            "thresholds": {
                "y_value": threshold
            }
        }
        response_data = {
            "anomaly_summary": anomaly_summary,
            "data": data
        }
        try:
            if not data:
                return response_data

            # Extract y_values for z-score calculation
            y_values = [point['y_value'] for point in data]
            
            # Calculate mean and standard deviation
            mean = sum(y_values) / len(y_values)
            variance = sum((x - mean) ** 2 for x in y_values) / len(y_values)
            std_dev = variance ** 0.5

            # If standard deviation is 0, all points are the same - no anomalies
            if std_dev == 0:
                return response_data

            # Calculate z-scores and update is_anomaly flags
            for point in data:
                z_score = abs((point['y_value'] - mean) / std_dev)
                if(z_score > threshold):    
                    total_anomalies_detected += 1
                    point['is_anomaly'] = True
                    point['anomaly_score'] = z_score  # Add anomaly score for reference
                else:
                    point['is_anomaly'] = False
                    point['anomaly_score'] = z_score  # Add anomaly score for reference

            anomaly_summary = {
                "detection_method": "z_score",
                "total_anomalies_detected": total_anomalies_detected,
                "anomaly_type": "spike",
                "thresholds": {
                    "y_value": threshold
                }
            }
            response_data = {
                "anomaly_summary": anomaly_summary,
                "data": data
            }
            return response_data

        except Exception as e:
            print(f"Error in anomaly detection: {str(e)}")
            return response_data
        
    def anomaly_detection_iqr(self, data: List[Dict[str, Any]], threshold: float = 1.5) -> List[Dict[str, Any]]:
        """
        Detect anomalies in time series data using IQR algorithm.
        
        Args:
            data: List of dictionaries containing time series data points with format:
                {
                    "x_value": str,  # timestamp
                    "y_value": float,  # metric value
                    "is_anomaly": bool  # will be updated by this method
                }
            threshold: IQR threshold for anomaly detection (default: 1.5)
                - Values with |IQR| > threshold are considered anomalies
                - Higher threshold = fewer anomalies detected
        
        Returns:
            List of data points with updated is_anomaly flags
        """

        total_anomalies_detected = 0

        anomaly_summary = {
            "detection_method": "iqr",
            "total_anomalies_detected": total_anomalies_detected,
            "anomaly_type": "spike",
            "thresholds": {
                "y_value": threshold
            }
        }
        response_data = {
            "anomaly_summary": anomaly_summary,
            "data": data
        }
        try:
            if not data:
                return response_data

            # Extract y_values for z-score calculation
            y_values = [point['y_value'] for point in data]
            
            # Calculate mean and standard deviation
            mean = sum(y_values) / len(y_values)
            variance = sum((x - mean) ** 2 for x in y_values) / len(y_values)
            std_dev = variance ** 0.5

            # If standard deviation is 0, all points are the same - no anomalies
            if std_dev == 0:
                return response_data

            # Calculate z-scores and update is_anomaly flags
            for point in data:
                z_score = abs((point['y_value'] - mean) / std_dev)
                if(z_score > threshold):    
                    total_anomalies_detected += 1
                    point['is_anomaly'] = True
                    point['anomaly_score'] = z_score  # Add anomaly score for reference
                else:
                    point['is_anomaly'] = False
                    point['anomaly_score'] = z_score  # Add anomaly score for reference

            anomaly_summary = {
                "detection_method": "iqr",
                "total_anomalies_detected": total_anomalies_detected,
                "anomaly_type": "spike",
                "thresholds": {
                    "y_value": threshold
                }
            }
            response_data = {
                "anomaly_summary": anomaly_summary,
                "data": data
            }
            return response_data

        except Exception as e:
            print(f"Error in anomaly detection: {str(e)}")
            return response_data
