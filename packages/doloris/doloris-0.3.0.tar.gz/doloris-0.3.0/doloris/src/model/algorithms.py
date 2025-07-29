from .models import LogisticRegression, SGDClassifierScratch
from .models import RandomTreeClassifier
from .models import KNNClassifier
from .models import SVC
from .models import DecisionTreeClassifier
from .models import MLPClassifier


def get_model(name, params=None):
    params = params or {}

    if name == "logistic_regression":
        return LogisticRegression(**params)

    elif name == "random_forest":
        return RandomTreeClassifier(**params)

    elif name == "knn":
        return KNNClassifier(**params)

    elif name == "svm":
        return SVC(**params)

    elif name == "decision_tree":
        return DecisionTreeClassifier(**params)

    elif name == "sgd":
        return SGDClassifierScratch(**params)

    elif name == "mlp":
        return MLPClassifier(**params)