from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import numpy as np

class DimensionalityReducer:
    def __init__(self,n_components):
        self.scaler = StandardScaler()
        self.model = PCA(n_components=n_components)

    def create_windows(self, series, window_size):
        """Create sliding windows from time series data."""
        return np.array([series[i:i+window_size] for i in range(len(series) - window_size + 1)])

    def apply_pca(self, data, window_size=15):
        """
        Apply window-based PCA to the input data.
        
        Args:
            data (numpy.ndarray): Input data array (1D time series)
            window_size (int): Size of sliding window
            n_components (int): Number of principal components to keep
            
        Returns:
            dict: Dictionary containing PCA results
        """
        try:
            # Create sliding windows
            X = self.create_windows(data, window_size)
            
            # Scale the data
            X_scaled = self.scaler.fit_transform(X)
            
            # Apply PCA
            X_pca = self.model.fit_transform(X_scaled)
            X_reconstructed = self.model.inverse_transform(X_pca)
            
            # Calculate reconstruction error
            reconstruction_error = np.mean((X_scaled - X_reconstructed)**2, axis=1)
            
            # Calculate anomaly threshold (mean + 3*std)
            threshold = np.mean(reconstruction_error) + 3 * np.std(reconstruction_error)
            
            return {
                "transformed_data": X_pca,
                "explained_variance_ratio": self.model.explained_variance_ratio_,
                "components": self.model.components_,
                "reconstruction_error": reconstruction_error,
                "threshold": threshold,
                "window_size": window_size,
                "scaler": self.scaler,
                "pca": self.model
            }
            
        except Exception as e:
            return {"error": str(e)}
