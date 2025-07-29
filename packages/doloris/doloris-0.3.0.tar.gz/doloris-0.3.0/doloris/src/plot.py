import os
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from datetime import datetime


def _save_fig(title: str, save_dir):
    os.makedirs(save_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    filename = f"{title.lower().replace(' ', '_')}_{timestamp}.png"
    path = os.path.join(save_dir, filename)
    plt.savefig(path, dpi=300, bbox_inches="tight")


def plot_confusion_matrix(conf_matrix, class_names, title, plot_path):
    plt.figure(figsize=(6, 5))
    sns.heatmap(conf_matrix, annot=True, fmt="d", cmap="Blues",
                xticklabels=class_names, yticklabels=class_names)
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    plt.title(title)
    plt.tight_layout()
    _save_fig("confusion_matrix", plot_path)
    plt.close()


def plot_classification_report(report_dict, title, plot_path):
    per_class_metrics = {
        label: metrics for label, metrics in report_dict.items()
        if label not in ["accuracy", "macro avg", "weighted avg"]
    }

    df = pd.DataFrame(per_class_metrics).T[["precision", "recall", "f1-score"]]
    df.plot(kind="bar", figsize=(8, 6), colormap="Set2")
    plt.title(title)
    plt.xticks(rotation=0)
    plt.ylabel("Score")
    plt.ylim(0, 1.05)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.legend(loc='lower right')
    plt.tight_layout()
    _save_fig("classification_report", plot_path)
    plt.close()


def plot_avg_scores(report_dict, plot_path):
    macro = report_dict["macro avg"]
    weighted = report_dict["weighted avg"]

    df = pd.DataFrame({
        "Macro Avg": macro,
        "Weighted Avg": weighted
    }).loc[["precision", "recall", "f1-score"]]

    df.plot(kind="bar", figsize=(6, 4), colormap="Pastel2")
    plt.title("Macro vs Weighted Average Scores")
    plt.ylim(0, 1.05)
    plt.xticks(rotation=0)
    plt.ylabel("Score")
    plt.grid(axis="y", linestyle="--", alpha=0.6)
    plt.tight_layout()
    _save_fig("macro_vs_weighted_avg", plot_path)
    plt.close()


# def plot_loss_curve(loss_values, title="Training Loss Curve"):
#     steps = list(range(1, len(loss_values) + 1))
#     plt.figure(figsize=(6, 4))
#     plt.plot(steps, loss_values, marker="o", linestyle="-", color="darkorange")
#     plt.title(title)
#     plt.xlabel("Step")
#     plt.ylabel("Loss")
#     plt.grid(True, linestyle="--", alpha=0.6)
#     plt.tight_layout()
#     _save_fig("loss_curve")
#     plt.close()
