import io
from contextlib import redirect_stdout

import gradio as gr
import pandas as pd

from doloris.algorithm import run_doloris_algorithm

ALGORITHM_NAME_MAPPING = {
    "逻辑回归 (Logistic Regression)": "logistic_regression",
    "朴素贝叶斯 (Naive Bayes)": "naive_bayes",
    "支持向量机 (SVM)": "svm",
    "k 近邻算法 (K-Nearest Neighbors)": "knn",
    "随机梯度下降 (SGD)": "sgd",
    "多层感知机 (MLP)": "mlp"
}
LABEL_TYPE_MAPPING = {
    "二分类": "binary",
    "多分类": "multiclass"
}

class DolorisPanel:
    def __init__(self, cache_path):
        self.classification_type = None
        self.selected_subjects = None
        self.algorithm = None
        self.cache_path = cache_path
        self.data_root = cache_path

    def parse_metrics_report(self, report_dict, set_name):
        df = pd.DataFrame(report_dict).T.reset_index()
        df.rename(columns={"index": "类别"}, inplace=True)
        df.insert(0, "数据集", set_name)
        return df

    def train_model(self, params):
        log_buffer = io.StringIO()
        with redirect_stdout(log_buffer):
            print("\n[模型训练开始]")
            print("收到训练参数：")
            for k, v in params.items():
                print(f"  - {k}: {v}")

            (confusion_matrix_path,
             classification_path,
             avg_scores_path,
             val_metrics,
             test_metrics
            ) = run_doloris_algorithm(
                self.cache_path,
                params["label_type"],
                params["feature_cols"],
                params["model_name"]
            )

            print("\n[模型训练完成]")
            print("验证集指标：")
            for k, v in val_metrics.items():
                print(f"  - {k}: {v}")

            print("\n测试集指标：")
            for k, v in test_metrics.items():
                if k not in ["confusion_matrix", "report"]:
                    print(f"  - {k}: {v}")

        logs = log_buffer.getvalue()

        val_df = self.parse_metrics_report(val_metrics["report"], "验证集")
        test_df = self.parse_metrics_report(test_metrics["report"], "测试集")
        metrics_df = pd.concat([val_df, test_df], ignore_index=True)

        return metrics_df, confusion_matrix_path, classification_path, avg_scores_path, logs

    def validate_and_submit(self, classification_type, selected_subjects, algorithm_display_name):
        self.classification_type = classification_type
        self.selected_subjects = selected_subjects
        self.algorithm = algorithm_display_name

        if not selected_subjects:
            return None, None, None, None, None, "请至少选择一个特征用于训练"

        # 映射为后端使用的原始参数
        label_type_code = LABEL_TYPE_MAPPING.get(classification_type)
        model_name_code = ALGORITHM_NAME_MAPPING.get(algorithm_display_name)

        params = {
            "label_type": label_type_code,
            "feature_cols": self.selected_subjects,
            "model_name": model_name_code,
        }

        metrics_df, conf_img_path, class_img_path, avg_img_path, logs = self.train_model(params)

        return metrics_df, conf_img_path, class_img_path, avg_img_path, logs, "模型训练完成"

    def launch(self, is_share):
        with gr.Blocks(title="Doloris 参数配置面板") as demo:
            gr.Markdown("## Doloris 学业风险预测参数面板")

            classification_type = gr.Radio(
                label="请选择任务类型",
                choices=list(LABEL_TYPE_MAPPING.keys()),
                value="二分类",
                info="选择二分类任务或多分类任务"
            )

            subject_choices = [
                "age_band",
                "highest_education",
                "imd_band",
                "num_of_prev_attempts",
                "studied_credits",
                "total_n_days",
                "avg_total_sum_clicks",
                "n_days_oucontent",
                "avg_sum_clicks_quiz",
                "avg_sum_clicks_forumng",
                "avg_sum_clicks_homepage"
            ]
            selected_subjects = gr.CheckboxGroup(
                label="请选择用于训练的特征字段",
                choices=subject_choices,
                info="至少选择一个字段作为模型输入",
                value=subject_choices,
            )

            algorithm = gr.Radio(
                label="请选择训练算法",
                choices=list(ALGORITHM_NAME_MAPPING.keys()),
                value="逻辑回归 (Logistic Regression)",
                info="支持的模型包括逻辑回归、朴素贝叶斯、支持向量机等"
            )

            submit_btn = gr.Button("开始训练模型")

            status_output = gr.Textbox(label="训练状态", interactive=False)

            metrics_table = gr.Dataframe(
                label="模型评估指标",
                interactive=False,
                wrap=True,
                row_count=10,
                col_count=(5, "dynamic")
            )

            with gr.Row():
                conf_img = gr.Image(label="混淆矩阵图")
                class_img = gr.Image(label="分类报告图")
                avg_img = gr.Image(label="平均指标图")

            logs_output = gr.Textbox(
                label="训练过程日志",
                lines=20,
                interactive=False,
                show_copy_button=True
            )

            submit_btn.click(
                fn=self.validate_and_submit,
                inputs=[classification_type, selected_subjects, algorithm],
                outputs=[
                    metrics_table,
                    conf_img,
                    class_img,
                    avg_img,
                    logs_output,
                    status_output
                ]
            )

        demo.launch(share=is_share)
