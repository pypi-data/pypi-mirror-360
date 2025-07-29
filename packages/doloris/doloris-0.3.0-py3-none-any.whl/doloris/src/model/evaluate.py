from sklearn.metrics import accuracy_score, f1_score, confusion_matrix, classification_report

def evaluate_model(model, X, y):
    y_pred = model.predict(X)
    
    unique_labels = sorted(set(y))
    if len(unique_labels) == 2:
        average = 'binary'
    else:
        average = 'weighted'

    metrics = {
        "accuracy": accuracy_score(y, y_pred),
        "f1_score": f1_score(y, y_pred, average=average),
        "confusion_matrix": confusion_matrix(y, y_pred).tolist(),
        "report": classification_report(y, y_pred, output_dict=True)
    }
    return metrics

