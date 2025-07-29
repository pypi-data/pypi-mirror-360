# Doloris

[![PyPI Version](https://img.shields.io/pypi/v/doloris)](https://pypi.org/project/doloris/)

中山大学 2025 年《模式识别》课程大作业项目

组员：许睿林、傅小桐

**Doloris**（**D**etection **O**f **L**earning **O**bstacles via **R**isk-aware **I**nteraction **S**ignals）是一款用于基于交互信号分析学习障碍的检测系统。它支持用户友好的命令行界面、可视化面板以及灵活的机器学习模型配置，适用于教育行为数据分析与预测任务。

![img](./assets/panel_1.png)

![img](./assets/panel_2.png)

## 🔧 安装方式

### 用户安装（推荐）

使用 pip 一键安装：

```bash
pip install doloris
```

### 开发者模式安装

若你正在开发或调试本项目，建议使用源码安装：

```bash
pip install .
```

安装完成后可通过下列命令验证版本：

```bash
doloris version
```

## 🚀 快速开始

### 启动可视化面板

运行以下命令以启动 Doloris 的交互式面板（默认缓存路径为 `.doloris/`）：

```bash
doloris panel --cache-path <缓存目录路径>
```

可选参数：

* `--cache-path`：指定缓存数据的目录路径（默认 `.doloris/`）
* `--share`：是否开启公网访问链接（默认 False）

### 运行模型算法

Doloris 提供命令行方式运行学习障碍检测算法，算法运行可视化结果保存在缓存路径下的 `algorithm_output` 文件夹：

```bash
doloris algorithm --cache-path <缓存目录路径> \
                  --label-type <binary|multiclass> \
                  --feature-cols <特征列1,特征列2,...> \
                  --model-name <模型名称>
```

可用参数说明：

* `--cache-path`：指定缓存数据的目录路径（默认 `.doloris/`）
* `--label-type`：指定标签类型（默认：`binary`），可选值：`binary`, `multiclass`
* `--feature-cols`：用逗号分隔的特征列名（默认为预设特征）
* `--model-name`：选择的模型名称，支持如下几种：

  * `logistic_regression`
  * `naive_bayes`
  * `knn`
  * `svm`
  * `sgd`
  * `mlp`

示例命令：

```bash
doloris algorithm --label-type binary --model-name random_forest
```

## 🧠 默认特征说明

默认使用以下交互特征进行建模：

* age\_band
* highest\_education
* imd\_band
* num\_of\_prev\_attempts
* studied\_credits
* total\_n\_days
* avg\_total\_sum\_clicks
* n\_days\_oucontent
* avg\_sum\_clicks\_quiz
* avg\_sum\_clicks\_forumng
* avg\_sum\_clicks\_homepage

你也可以通过 `--feature-cols` 参数自定义特征列表。

## 性能评估指标说明

Doloris 在训练与测试阶段均自动计算以下性能指标：

### 准确率（Accuracy）

$$
\text{Accuracy} = \frac{TP + TN}{TP + TN + FP + FN}
$$

表示模型在所有样本中的总体正确预测比例。

### 精确率（Precision）

对于某一类别 $c$，精确率定义为：

$$
\text{Precision}_c = \frac{TP_c}{TP_c + FP_c}
$$

衡量模型预测为该类别时，实际为该类别的比例。

### 召回率（Recall）

$$
\text{Recall}_c = \frac{TP_c}{TP_c + FN_c}
$$

衡量模型成功识别出该类别样本的比例。

### F1 分数（F1-score）

F1-score 是精确率与召回率的调和平均：

$$
\text{F1}_c = \frac{2 \cdot \text{Precision}_c \cdot \text{Recall}_c}{\text{Precision}_c + \text{Recall}_c}
$$

同时计算宏平均（Macro Average）与加权平均（Weighted Average）：

* 宏平均（Macro）为各类 F1-score 的算术平均：

  $$
  \text{Macro-F1} = \frac{1}{C} \sum_{c=1}^{C} \text{F1}_c
  $$
* 加权平均（Weighted）根据每类样本数量加权：

  $$
  \text{Weighted-F1} = \frac{1}{N} \sum_{c=1}^{C} n_c \cdot \text{F1}_c
  $$

其中 $n_c$ 表示第 $c$ 类样本数，$N$ 为总样本数。