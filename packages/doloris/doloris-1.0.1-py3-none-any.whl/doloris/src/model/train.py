from .algorithms import get_model
from .evaluate import evaluate_model
from sklearn.model_selection import GridSearchCV

def get_default_param_grid(model_name):
    if model_name == "logistic_regression":
        return {
            'C': [0.01, 0.1, 1, 10],
            'penalty': ['l2'],
            'solver': ['liblinear']
        }
    elif model_name == "random_forest":
        return {
            'n_estimators': [50, 100],
            'max_depth': [5, 10, None],
            'min_samples_split': [2, 5]
        }
    elif model_name == "knn":
        return {
            'n_neighbors': [3, 5, 7],
            'weights': ['uniform', 'distance']
        }
    elif model_name == "svm":
        return {
            'C': [0.1, 1, 10],
            'kernel': ['linear', 'rbf']
        }
    elif model_name == "decision_tree":
        return {
            'max_depth': [5, 10, None],
            'min_samples_split': [2, 5, 10]
        }
    else:
        raise ValueError(f"No default grid defined for model: {model_name}")

def train_model_with_val(model_name, X_train, y_train, X_val, y_val, params=None, use_grid_search=False):
    if use_grid_search:
        base_model = get_model(model_name)
        param_grid = get_default_param_grid(model_name)
        grid = GridSearchCV(base_model, param_grid, scoring='f1', cv=3, n_jobs=-1)
        grid.fit(X_train, y_train)
        model = grid.best_estimator_
    else:
        model = get_model(model_name, params)
        model.fit(X_train, y_train)

    val_metrics = evaluate_model(model, X_val, y_val)
    return model, val_metrics