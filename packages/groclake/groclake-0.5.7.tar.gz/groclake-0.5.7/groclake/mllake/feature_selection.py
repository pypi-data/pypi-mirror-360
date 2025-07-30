
from sklearn.feature_selection import SelectKBest, f_classif

class FeatureSelector:
    def __init__(self, k=5):
        self.selector = SelectKBest(score_func=f_classif, k=k)

    def fit_transform(self, X, y):
        return self.selector.fit_transform(X, y)

    def get_selected_features(self, feature_names):
        return [feature_names[i] for i in self.selector.get_support(indices=True)]
