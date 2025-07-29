from .models import LogisticRegression, SGDClassifierScratch
from .models import NaiveBayesClassifier
from .models import KNNClassifier
from .models import SVC
from .models import MLPClassifier


def get_model(name, params=None):
    params = params or {}

    if name == "logistic_regression":
        return LogisticRegression(**params)

    elif name == "naive_bayes":
        return NaiveBayesClassifier(**params)

    elif name == "knn":
        return KNNClassifier(**params)

    elif name == "svm":
        return SVC(**params)
    
    elif name == "sgd":
        return SGDClassifierScratch(**params)

    elif name == "mlp":
        return MLPClassifier(**params)