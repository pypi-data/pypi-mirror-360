
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor

class Regressor:
    def __init__(self, model_name="random_forest", **kwargs):
        if model_name.lower() == "xgboost":
            self.model = XGBRegressor(**kwargs)
        else:
            self.model = RandomForestRegressor(**kwargs)

    def fit(self, X, y):
        self.model.fit(X, y)

    def predict(self, X):
        return self.model.predict(X)

    def evaluate(self, X_test, y_test):
        from sklearn.metrics import mean_squared_error
        return mean_squared_error(y_test, self.model.predict(X_test)) ** 0.5  # Manually compute RMSE

