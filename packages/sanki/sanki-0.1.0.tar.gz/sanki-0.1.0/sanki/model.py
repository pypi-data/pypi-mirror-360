from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier

class Trainer:
    def __init__(self, model_type="logistic"):
        if model_type == "logistic":
            self.model = LogisticRegression()
        elif model_type == "tree":
            self.model = DecisionTreeClassifier()
        else:
            raise ValueError("Unsupported model type")

    def train(self, X, y):
        self.model.fit(X, y)

    def predict(self, X):
        return self.model.predict(X)