from .algorithms import get_model
from .evaluate import evaluate_model
from sklearn.model_selection import GridSearchCV


# 针对每种模型定义默认调参范围（可用于 GridSearchCV）
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


# 主训练函数：可传入参数，也支持自动 Grid Search

def train_model_with_val(model_name, X_train, y_train, X_val, y_val, params=None, use_grid_search=False):
    """
    训练模型并在验证集上评估，可选自动网格搜索调参。

    :param model_name: 模型名称，如 'logistic_regression', 'random_forest' 等
    :param X_train: 训练特征
    :param y_train: 训练标签
    :param X_val: 验证特征
    :param y_val: 验证标签
    :param params: 模型超参数（字典）
    :param use_grid_search: 是否启用 GridSearchCV 自动调参
    :return: 训练好的模型、验证集评估结果（字典）
    """

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