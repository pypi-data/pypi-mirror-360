import random
import numpy as np
from tqdm import tqdm
from collections import Counter

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

        for epoch in tqdm(range(self.epochs)):
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
    def __init__(self, k=2):
        self.k = k
        self.X_train = None
        self.y_train = None

    def fit(self, X, y):
        self.X_train = np.asarray(X, dtype=np.float64)
        self.y_train = np.asarray(y, dtype=np.int32)
        return self

    def _euclidean_distance(self, x1, x2):
        return np.sqrt(np.sum((x1 - x2) ** 2))

    def _predict_one(self, x): 
        distances = [self._euclidean_distance(x, x_train) for x_train in self.X_train]
        k_indices = np.argsort(distances)[:self.k]
        k_nearest_labels = [self.y_train[i] for i in k_indices]
        most_common = Counter(k_nearest_labels).most_common(1)
        return most_common[0][0]

    def predict(self, X): 
        X = np.asarray(X, dtype=np.float64)
        return np.array([self._predict_one(x) for x in X])

class DecisionTreeNode:
    def __init__(self, feature=None, threshold=None, left=None, right=None, value=None):
        self.feature = feature  
        self.threshold = threshold 
        self.left = left
        self.right = right 
        self.value = value 

class DecisionTreeClassifier:
    def __init__(self, max_depth=5, min_samples_split=2):
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.root = None
        self.y_train_fit = np.array([]) 

    def _entropy(self, labels):
        total = len(labels)
        if total == 0:
            return 0
        counts = Counter(labels)
        entropy = 0.0
        for count in counts.values():
            prob = count / total
            entropy -= prob * np.log2(prob + 1e-9)
        return entropy

    def _best_split(self, X, y):
        best_gain = -1.0
        best_feature = None
        best_threshold = None

        n_samples, n_features = X.shape
        base_entropy = self._entropy(y)

        for feature in range(n_features):
            unique_values = np.unique(X[:, feature])
            if len(unique_values) < 2:
                continue 

            for i in range(len(unique_values) - 1):
                threshold = (unique_values[i] + unique_values[i+1]) / 2.0

                left_indices = X[:, feature] <= threshold
                right_indices = X[:, feature] > threshold

                left_y, right_y = y[left_indices], y[right_indices]

                if len(left_y) == 0 or len(right_y) == 0:
                    continue

                gain = base_entropy - (
                    (len(left_y) / n_samples) * self._entropy(left_y) +
                    (len(right_y) / n_samples) * self._entropy(right_y)
                )

                if gain > best_gain:
                    best_gain = gain
                    best_feature = feature
                    best_threshold = threshold
        return best_feature, best_threshold, best_gain

    def _build_tree(self, X, y, depth):
        if len(np.unique(y)) == 1: 
            return DecisionTreeNode(value=y[0])
        if depth >= self.max_depth: 
            return DecisionTreeNode(value=Counter(y).most_common(1)[0][0])
        if len(X) < self.min_samples_split: 
            return DecisionTreeNode(value=Counter(y).most_common(1)[0][0])
        
        feature, threshold, gain = self._best_split(X, y)
        if feature is None or gain <= 0:
            return DecisionTreeNode(value=Counter(y).most_common(1)[0][0])

        left_indices = X[:, feature] <= threshold
        right_indices = X[:, feature] > threshold

        left_node = self._build_tree(X[left_indices], y[left_indices], depth + 1)
        right_node = self._build_tree(X[right_indices], y[right_indices], depth + 1)

        return DecisionTreeNode(feature, threshold, left_node, right_node)

    def fit(self, X, y):
        X = np.asarray(X, dtype=np.float64)
        y = np.asarray(y, dtype=np.int32)
        self.y_train_fit = y 
        self.root = self._build_tree(X, y, 0)
        return self

    def _predict_one(self, x, node=None): 
        if node is None:
            node = self.root
        
        if node.value is not None:
            return node.value

        if node.feature >= len(x) or node.feature < 0:
            if len(self.y_train_fit) > 0:
                return Counter(self.y_train_fit).most_common(1)[0][0]
            else:
                return 0
        
        if x[node.feature] <= node.threshold:
            if node.left:
                return self._predict_one(x, node.left)
            else:
                if len(self.y_train_fit) > 0:
                    return Counter(self.y_train_fit).most_common(1)[0][0]
                else:
                    return 0
        else:
            if node.right:
                return self._predict_one(x, node.right)
            else:
                if len(self.y_train_fit) > 0:
                    return Counter(self.y_train_fit).most_common(1)[0][0]
                else:
                    return 0
    
    def predict(self, X): # 预测
        X = np.asarray(X, dtype=np.float64)
        return np.array([self._predict_one(x) for x in X])

class RandomTreeClassifier: 
    def __init__(self, n_estimators=100, max_depth=10, min_samples_split=2, max_features=None, random_state=None):
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.max_features = max_features
        self.random_state = random_state
        self.trees = []

    def fit(self, X, y):
        X = np.asarray(X, dtype=np.float64)
        y = np.asarray(y, dtype=np.int32)
        n_samples, n_features = X.shape

        if self.random_state is not None:
            np.random.seed(self.random_state)
            random.seed(self.random_state)

        self.trees = []
        for _ in tqdm(range(self.n_estimators)):
            indices = np.random.choice(n_samples, n_samples, replace=True)
            X_sample, y_sample = X[indices], y[indices]

            tree = _RandomForestDecisionTree(
                max_depth=self.max_depth,
                min_samples_split=self.min_samples_split,
                max_features=self.max_features
            )
            tree.fit(X_sample, y_sample)
            self.trees.append(tree)
        return self

    def predict(self, X):
        X = np.asarray(X, dtype=np.float64)
        if X.shape[0] == 0:
            return np.array([], dtype=int)
            
        all_tree_predictions = []
        for tree in self.trees:
            all_tree_predictions.append(tree.predict(X))
        
        predictions = np.array(all_tree_predictions)

        final_predictions = np.zeros(X.shape[0], dtype=int)
        for i in range(X.shape[0]):
            most_common_class = Counter(predictions[:, i]).most_common(1)
            if most_common_class:
                final_predictions[i] = most_common_class[0][0]
            else:
                final_predictions[i] = 0 
        return final_predictions

class _RandomForestDecisionTree(DecisionTreeClassifier):
    def __init__(self, max_depth=5, min_samples_split=2, max_features=None):
        super().__init__(max_depth, min_samples_split)
        self.max_features = max_features

    def _best_split(self, X, y):
        best_gain = -1.0
        best_feature = None
        best_threshold = None
        
        n_samples, n_features = X.shape
        base_entropy = self._entropy(y)

        feature_indices = list(range(n_features))
        
        if self.max_features is not None and self.max_features < n_features:
            if isinstance(self.max_features, float): # If it's a proportion
                num_features_to_consider = max(1, int(n_features * self.max_features))
            else: # If it's an integer
                num_features_to_consider = min(n_features, self.max_features)
            selected_features = random.sample(feature_indices, num_features_to_consider)
        else:
            selected_features = feature_indices 
        for feature in selected_features: 
            unique_values = np.unique(X[:, feature])
            if len(unique_values) < 2:
                continue

            for i in range(len(unique_values) - 1):
                threshold = (unique_values[i] + unique_values[i+1]) / 2.0
                
                left_indices = X[:, feature] <= threshold
                right_indices = X[:, feature] > threshold
                
                left_y, right_y = y[left_indices], y[right_indices]
                
                if len(left_y) == 0 or len(right_y) == 0:
                    continue
                
                gain = base_entropy - (
                    (len(left_y)/n_samples)*self._entropy(left_y) +
                    (len(right_y)/n_samples)*self._entropy(right_y)
                )
                if gain > best_gain:
                    best_gain = gain
                    best_feature = feature
                    best_threshold = threshold
        return best_feature, best_threshold, best_gain 

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

        for _ in tqdm(range(self.epochs)):
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

        for epoch in tqdm(range(self.epochs)):
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

        for epoch in tqdm(range(self.epochs)):
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

        for epoch in tqdm(range(self.epochs)):
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