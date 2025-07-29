import os
import yaml
import time
import zipfile
import requests
from io import BytesIO

import pandas as pd
from tqdm import tqdm

from doloris.src.data import DataLoader, define_label_binary, define_label_multiclass, LabelEncoder
from doloris.src.model import train_model_with_val, evaluate_model
from doloris.src.plot import plot_confusion_matrix, plot_classification_report, plot_avg_scores

OULAD_DATA_URL = "https://blog.tokisakix.cn/static/.doloris.zip"

def __init_data(cache_path, data_root):
        os.makedirs(cache_path, exist_ok=True)

        if not os.path.exists(data_root) or not os.listdir(data_root):
            print("数据集不存在，正在下载...")

            try:
                response = requests.get(OULAD_DATA_URL, stream=True)
                response.raise_for_status()
                total_size = int(response.headers.get('content-length', 0))
                block_size = 1024  # 1 Kibibyte

                temp_buffer = BytesIO()
                with tqdm(total=total_size, unit='B', unit_scale=True, desc='下载中') as pbar:
                    for data in response.iter_content(block_size):
                        temp_buffer.write(data)
                        pbar.update(len(data))

                temp_buffer.seek(0)
                with zipfile.ZipFile(temp_buffer) as z:
                    z.extractall(data_root)

                print("数据集下载并解压完成。")

            except Exception as e:
                print(f"下载或解压数据集失败: {e}")
        else:
            print("数据集已存在，跳过下载。")

        return

def run_doloris_algorithm(cache_path, label_type, feature_cols, model_name):
    __init_data(cache_path, data_root = cache_path)

    config_path = os.path.join(cache_path, "config.yaml")
    data_path = os.path.join(cache_path, "cleaned_data.csv")
    
    config = yaml.safe_load(open(config_path, 'r', encoding='utf-8'))
    df = pd.read_csv(data_path)
    df = LabelEncoder(df)

    if label_type == "binary":
        df = define_label_binary(df)
        label_col = "label_binary"
    elif label_type == "multiclass":
        df = define_label_multiclass(df)
        label_col = "label_multiclass"
    else:
        raise ValueError("config['label_type'] must be 'binary' or 'multiclass'")

    loader = DataLoader(
        df=df,
        feature_cols=feature_cols,
        label_col=label_col,
        val_size=config["val_size"],
        test_size=config["test_size"],
        random_state=config["random_state"],
        scale=config["scale"]
    )
    
    X_train_df, X_val_df, X_test_df, y_train_series, y_val_series, y_test_series = loader.load_data()
    X_train = X_train_df.values
    y_train = y_train_series.values

    X_val = X_val_df.values
    y_val = y_val_series.values
    
    X_test = X_test_df.values
    y_test = y_test_series.values
    
    if "all_model_params" in config and model_name in config["all_model_params"]:
        params = config["all_model_params"][model_name]
    print(f"\nTraining model: {model_name}")
    
    start_time = time.time()
    model, val_metrics = train_model_with_val(
        model_name=model_name,
        X_train=X_train, 
        y_train=y_train,
        X_val=X_val, 
        y_val=y_val,
        params=params,
        use_grid_search=config.get("use_grid_search", False)
    )
    end_time = time.time() 
    training_time = end_time - start_time
    print(f"Training time: {training_time:.2f} seconds")
    print("\nValidation Results:", val_metrics)

    test_metrics = evaluate_model(model, X_test, y_test)
    print("\nTest Results:", test_metrics)
    
    conf_matrix = test_metrics["confusion_matrix"]
    report = test_metrics["report"]

    plot_path = os.path.join(cache_path, "algorithm_output", model_name)
    plot_confusion_matrix(conf_matrix, class_names=["Not At Risk", "At Risk"], title="Confusion Matrix", plot_path=plot_path)
    plot_classification_report(report, title="Test Set Classification Report", plot_path=plot_path)
    plot_avg_scores(report, plot_path)