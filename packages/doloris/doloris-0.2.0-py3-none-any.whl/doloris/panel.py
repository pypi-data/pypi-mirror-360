import os
import zipfile
import requests
from io import BytesIO

import gradio as gr
import pandas as pd
from tqdm import tqdm

OULAD_DATA_URL = "https://blog.tokisakix.cn/static/OULAD-data.zip"

class DolorisPanel:
    def __init__(self, cache_path):
        self.classification_type = None
        self.num_weeks = None
        self.selected_subjects = None
        self.algorithm = None
        self.cache_path = cache_path
        self.data_root = os.path.join(self.cache_path, "OULAD-data")
        self.__init_data()
        return

    def __init_data(self):
        os.makedirs(self.cache_path, exist_ok=True)

        if not os.path.exists(self.data_root) or not os.listdir(self.data_root):
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
                    z.extractall(self.data_root)

                print("数据集下载并解压完成。")

            except Exception as e:
                print(f"下载或解压数据集失败: {e}")
        else:
            print("数据集已存在，跳过下载。")

        return

    #TODO!
    def train_model(self, params):
        """
        模拟训练过程，返回训练结果。
        """
        print("\n[模型训练开始]")
        print("收到参数：", params)

        # 数据集会自动下载，存放的路径如下
        # for filename in os.listdir(self.data_root):
        #     print(os.path.join(self.data_root, filename))
        # ~\.doloris\OULAD-data\assessments.csv
        # ~\.doloris\OULAD-data\courses.csv
        # ~\.doloris\OULAD-data\studentAssessment.csv
        # ~\.doloris\OULAD-data\studentInfo.csv
        # ~\.doloris\OULAD-data\studentRegistration.csv
        # ~\.doloris\OULAD-data\studentVle.csv
        # ~\.doloris\OULAD-data\vle.csv

        # 模拟多次迭代的 loss
        loss_values = [1.0 / (i + 1) + 0.05 * (i % 3 - 1) for i in range(1, 21)]  # 模拟20轮loss

        # 模拟性能指标
        performance = {
            "集合": ["Train", "Valid", "Test"],
            "Accuracy": [0.92, 0.87, 0.85],
            "F1-score": [0.90, 0.86, 0.84],
        }

        print("训练完成，结果如下：")
        for k, v in performance.items():
            print(f"{k}: {v}")

        loss_df = pd.DataFrame({
            "step": list(range(1, len(loss_values)+1)),
            "loss": loss_values
        })

        return loss_df, pd.DataFrame(performance)

    def validate_and_submit(self, classification_type, num_weeks, selected_subjects, algorithm):
        self.classification_type = classification_type
        self.num_weeks = num_weeks
        self.selected_subjects = selected_subjects
        self.algorithm = algorithm

        # 参数校验
        if not isinstance(num_weeks, int) or num_weeks <= 0 or num_weeks > 16:
            return None, None, "❌ 使用周数应在 1 到 16 之间"

        if not selected_subjects:
            return None, None, "❌ 请至少选择一门学科"

        # 构建参数并调用训练逻辑
        params = {
            "classification_type": self.classification_type,
            "num_weeks": self.num_weeks,
            "selected_subjects": self.selected_subjects,
            "algorithm": self.algorithm,
        }

        loss_values, metrics_df = self.train_model(params)

        return loss_values, metrics_df, "✅ 参数提交成功，模型训练完成"

    def launch(self, is_share):
        with gr.Blocks(title="Doloris 面板") as demo:
            gr.Markdown("## 🎛️ Doloris 参数配置面板")

            with gr.Row():
                classification_type = gr.Radio(
                    label="请选择分类类型",
                    choices=["2 分类", "N 分类"],
                    value="2 分类"
                )

                num_weeks = gr.Number(
                    label="使用几周的数据（填 1~16）",
                    value=4,
                    precision=0,
                    interactive=True
                )

            subject_choices = ["AAA", "BBB", "CCC", "DDD", "EEE", "FFF", "GGG"]
            selected_subjects = gr.CheckboxGroup(
                label="选择使用哪几科的数据",
                choices=subject_choices
            )

            algorithm = gr.Radio(
                label="选择使用的算法",
                choices=["线性分类器", "非线性分类器", "KNN", "逻辑回归", "随机森林", "SVM"],
                value="线性分类器",
            )

            submit_btn = gr.Button("🚀 提交参数，开始训练")

            status_output = gr.Textbox(label="运行状态", interactive=False)

            # 图表和表格输出区
            with gr.Row():
                loss_plot = gr.LinePlot(
                    label="📉 Loss 曲线图",
                    x="step", y="loss",
                    x_title="Step",
                    y_title="Loss",
                    width=500,
                    height=350
                )

                metrics_table = gr.Dataframe(
                    label="📊 模型性能指标",
                    interactive=False,
                )

            # 提交按钮绑定
            submit_btn.click(
                fn=self.validate_and_submit,
                inputs=[classification_type, num_weeks, selected_subjects, algorithm],
                outputs=[loss_plot, metrics_table, status_output]
            )

        demo.launch(share=is_share)
