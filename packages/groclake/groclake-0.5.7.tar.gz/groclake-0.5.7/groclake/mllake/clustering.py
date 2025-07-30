
from sklearn.cluster import KMeans, DBSCAN

class Clustering:
    def __init__(self, model_name="kmeans", **kwargs):
        if model_name.lower() == "dbscan":
            self.model = DBSCAN(**kwargs)
        else:
            self.model = KMeans(**kwargs)

    def fit_predict(self, X):
        return self.model.fit_predict(X)
