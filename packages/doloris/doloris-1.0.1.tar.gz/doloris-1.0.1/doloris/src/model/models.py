import random
import numpy as np
from collections import defaultdict, Counter
from numba import njit

class LogisticRegression:
    def __init__(self, lr=0.1, epochs=100):
        self.lr = lr
        self.epochs = epochs
        self.weights = None
        self.bias = 0.0

    def sigmoid(self, z):
        if z < -500:
            return 0.0
        if z > 500:
            return 1.0
        return 1 / (1 + np.exp(-z))

    def fit(self, X, y):
        X = np.asarray(X, dtype=np.float64)
        y = np.asarray(y, dtype=np.float64)

        n_samples, n_features = X.shape
        self.weights = np.random.uniform(-1, 1, n_features)
        self.bias = 0.0

        for epoch in range(self.epochs):
            for i in range(n_samples):
                linear_output = np.dot(X[i], self.weights) + self.bias
                pred = self.sigmoid(linear_output)
                error = pred - y[i]

                self.weights -= self.lr * error * X[i]
                self.bias -= self.lr * error
        return self

    def _predict_proba_one(self, x):
        linear_output = np.dot(x, self.weights) + self.bias
        return self.sigmoid(linear_output)

    def predict_proba(self, X): 
        X = np.asarray(X, dtype=np.float64)
        return np.array([self._predict_proba_one(x) for x in X])

    def predict(self, X):
        probabilities = self.predict_proba(X)
        return (probabilities >= 0.5).astype(int)

class KNNClassifier:
    def __init__(self, k=4):
        self.k = k
        self.X_train = None
        self.y_train = None

    def fit(self, X, y):
        self.X_train = np.asarray(X, dtype=np.float64)
        self.y_train = np.asarray(y, dtype=np.int32)
        return self

    def predict(self, X):
        X = np.asarray(X, dtype=np.float64)

        X_norm = np.sum(X ** 2, axis=1).reshape(-1, 1)
        X_train_norm = np.sum(self.X_train ** 2, axis=1).reshape(1, -1)
        distances = X_norm + X_train_norm - 2 * X @ self.X_train.T

        return knn_predict_numba(distances, self.y_train, self.k)


@njit
def knn_predict_numba(distances, y_train, k):
    n_test = distances.shape[0]
    preds = np.empty(n_test, dtype=np.int32)

    max_label = np.max(y_train)
    for i in range(n_test):
        row = distances[i]
        idx = np.argpartition(row, k)[:k]

        votes = np.zeros(max_label + 1, dtype=np.int32)
        for j in idx:
            votes[y_train[j]] += 1

        preds[i] = np.argmax(votes)

    return preds

class NaiveBayesClassifier:
    def __init__(self, var_smoothing=1e-9, normalize=False, clip_log_prob=None, priors=None):
        self.var_smoothing = var_smoothing
        self.normalize = normalize
        self.clip_log_prob = clip_log_prob
        self.priors = priors
        self.class_priors = {}
        self.feature_likelihoods = defaultdict(dict)
        self.classes = []
        self.feature_mean = None
        self.feature_std = None

    def fit(self, X, y):
        X = np.asarray(X, dtype=np.float64)
        y = np.asarray(y)
        n_samples, n_features = X.shape
        self.classes = np.unique(y)

        if self.normalize:
            self.feature_mean = X.mean(axis=0)
            self.feature_std = X.std(axis=0) + 1e-9
            X = (X - self.feature_mean) / self.feature_std

        if self.priors is not None:
            self.class_priors = {c: p for c, p in zip(self.classes, self.priors)}
        else:
            for c in self.classes:
                self.class_priors[c] = np.mean(y == c)

        for c in self.classes:
            X_c = X[y == c]
            for feature in range(n_features):
                mean = X_c[:, feature].mean()
                var = X_c[:, feature].var() + self.var_smoothing
                self.feature_likelihoods[c][feature] = (mean, var)
        return self

    def _gaussian_log_prob(self, x, mean, var):
        log_prob = -0.5 * np.log(2 * np.pi * var) - ((x - mean) ** 2) / (2 * var)
        if self.clip_log_prob:
            log_prob = np.clip(log_prob, self.clip_log_prob[0], self.clip_log_prob[1])
        return log_prob

    def _predict_one(self, x):
        if self.normalize and self.feature_mean is not None:
            x = (x - self.feature_mean) / self.feature_std

        log_probs = {}
        for c in self.classes:
            log_prob = np.log(self.class_priors[c])
            for feature, value in enumerate(x):
                mean, var = self.feature_likelihoods[c][feature]
                log_prob += self._gaussian_log_prob(value, mean, var)
            log_probs[c] = log_prob
        return max(log_probs.items(), key=lambda item: item[1])[0]

    def predict(self, X):
        X = np.asarray(X, dtype=np.float64)
        return np.array([self._predict_one(x) for x in X])

class PerceptronClassifier:
    def __init__(self, epochs=100, lr=1.0):
        self.epochs = epochs
        self.lr = lr 
        self.weights = None
        self.bias = 0.0

    def fit(self, X, y):
        X = np.asarray(X, dtype=np.float64)
        y = np.asarray(y, dtype=np.int32)
        y_binary = np.where(y == 1, 1, -1)

        n_samples, n_features = X.shape
        self.weights = np.zeros(n_features)
        self.bias = 0.0

        for _ in range(self.epochs):
            for i in range(n_samples):
                linear_output = np.dot(X[i], self.weights) + self.bias
                prediction = 1 if linear_output >= 0 else -1 

                if y_binary[i] * prediction <= 0:
                    self.weights += self.lr * y_binary[i] * X[i]
                    self.bias += self.lr * y_binary[i]
        return self

    def _predict_one(self, x): 
        linear_output = np.dot(x, self.weights) + self.bias
        return 1 if linear_output >= 0 else 0

    def predict(self, X):
        X = np.asarray(X, dtype=np.float64)
        return np.array([self._predict_one(x) for x in X])


class MLPClassifier:
    def __init__(self, hidden_sizes=[100], output_size=1, lr=0.01, epochs=100):
        self.lr = lr
        self.epochs = epochs
        self.hidden_sizes = hidden_sizes
        self.output_size = output_size
        
        self.weights = []
        self.biases = []
        self.sizes = []

    def relu(self, x):
        return np.maximum(0, x)

    def relu_deriv(self, x):
        return (x > 0).astype(float) 

    def sigmoid(self, x):
        x_clipped = np.clip(x, -500, 500)
        return 1 / (1 + np.exp(-x_clipped))

    def sigmoid_deriv(self, x):
        s = self.sigmoid(x)
        return s * (1 - s)

    def _initialize_network(self, input_size):
        self.sizes = [input_size] + self.hidden_sizes + [self.output_size]
        self.weights = []
        self.biases = []
        for i in range(len(self.sizes) - 1):
            w = np.random.randn(self.sizes[i+1], self.sizes[i]) * 0.01
            b = np.zeros(self.sizes[i+1])
            self.weights.append(w)
            self.biases.append(b)

    def forward(self, x):
        activations = [x] 
        zs = [] 

        for i in range(len(self.weights)):
            layer_input = activations[-1]
            z = np.dot(self.weights[i], layer_input) + self.biases[i]
            zs.append(z)
            
            if i == len(self.weights) - 1:
                a = self.sigmoid(z)
            else: 
                a = self.relu(z)
            activations.append(a)
        return zs, activations

    def backward(self, x, y, zs, activations):
        delta = [None] * len(self.weights)

        delta_L = activations[-1] - y
        delta[-1] = delta_L

        for l in range(len(self.weights) - 2, -1, -1):
            z = zs[l]
            sp = self.relu_deriv(z) 
            delta[l] = np.dot(self.weights[l+1].T, delta[l+1]) * sp

        for l in range(len(self.weights)):
            self.weights[l] -= self.lr * np.outer(delta[l], activations[l])
            self.biases[l] -= self.lr * delta[l]

    def fit(self, X, y):
        X = np.asarray(X, dtype=np.float64)
        y = np.asarray(y, dtype=np.float64) 

        n_samples, input_size = X.shape
        self._initialize_network(input_size)

        for epoch in range(self.epochs):
            permutation = np.random.permutation(n_samples)
            X_shuffled = X[permutation]
            y_shuffled = y[permutation]

            for i in range(n_samples):
                xi, yi = X_shuffled[i], y_shuffled[i]
                
                zs, activations = self.forward(xi)
                self.backward(xi, yi, zs, activations)
        return self

    def _predict_proba_one(self, x):
        _, activations = self.forward(x)
        return activations[-1][0] 

    def predict_proba(self, X):
        X = np.asarray(X, dtype=np.float64)
        return np.array([self._predict_proba_one(x) for x in X])

    def predict(self, X):
        probabilities = self.predict_proba(X)
        return (probabilities >= 0.5).astype(int)

class SGDClassifierScratch: 
    def __init__(self, lr=0.01, epochs=100):
        self.lr = lr
        self.epochs = epochs
        self.weights = None
        self.bias = 0.0

    def sigmoid(self, z):
        if z < -500:
            return 0.0
        if z > 500:
            return 1.0
        return 1 / (1 + np.exp(-z))

    def fit(self, X, y):
        X = np.asarray(X, dtype=np.float64)
        y = np.asarray(y, dtype=np.float64)

        n_samples, n_features = X.shape
        self.weights = np.random.uniform(-1, 1, n_features)
        self.bias = 0.0

        for epoch in range(self.epochs):
            permutation = np.random.permutation(n_samples)
            X_shuffled = X[permutation]
            y_shuffled = y[permutation]

            for i in range(n_samples):
                xi, yi = X_shuffled[i], y_shuffled[i]
                
                linear_output = np.dot(xi, self.weights) + self.bias
                pred = self.sigmoid(linear_output)
                error = pred - yi

                self.weights -= self.lr * error * xi
                self.bias -= self.lr * error
        return self

    def _predict_proba_one(self, x):
        linear_output = np.dot(x, self.weights) + self.bias
        return self.sigmoid(linear_output)

    def predict_proba(self, X): 
        X = np.asarray(X, dtype=np.float64)
        return np.array([self._predict_proba_one(x) for x in X])

    def predict(self, X): 
        probabilities = self.predict_proba(X)
        return (probabilities >= 0.5).astype(int)


class SVC: 
    def __init__(self, lr=0.001, epochs=100, C=1.0):
        self.lr = lr
        self.epochs = epochs
        self.C = C
        self.weights = None
        self.bias = 0.0

    def fit(self, X, y):
        X = np.asarray(X, dtype=np.float64)
        y = np.asarray(y, dtype=np.int32)
        y_scaled = np.where(y == 1, 1, -1)

        n_samples, n_features = X.shape
        self.weights = np.random.uniform(-0.01, 0.01, n_features)
        self.bias = 0.0

        for epoch in range(self.epochs):
            permutation = np.random.permutation(n_samples)
            X_shuffled = X[permutation]
            y_shuffled = y_scaled[permutation]

            for i in range(n_samples):
                xi, yi = X_shuffled[i], y_shuffled[i]
                
                linear_output = np.dot(xi, self.weights) + self.bias
                
                if yi * linear_output >= 1: 
                    self.weights -= self.lr * (2 * self.weights)
                else: 
                    self.weights -= self.lr * (2 * self.weights - yi * xi)
                    self.bias -= self.lr * (-yi) 
        return self

    def _predict_one(self, x):
        linear_output = np.dot(x, self.weights) + self.bias
        return 1 if linear_output >= 0 else 0 

    def predict(self, X):
        X = np.asarray(X, dtype=np.float64)
        return np.array([self._predict_one(x) for x in X])