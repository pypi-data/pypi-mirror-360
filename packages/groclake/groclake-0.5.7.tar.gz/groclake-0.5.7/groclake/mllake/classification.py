
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier

class Classifier:
    def __init__(self, model_name="random_forest", **kwargs):
        if model_name.lower() == "xgboost":
            self.model = XGBClassifier(**kwargs)
        else:
            self.model = RandomForestClassifier(**kwargs)

    def fit(self, X, y):
        self.model.fit(X, y)

    def predict(self, X):
        return self.model.predict(X)

    def evaluate(self, X_test, y_test):
        from sklearn.metrics import accuracy_score
        return accuracy_score(y_test, self.model.predict(X_test))

