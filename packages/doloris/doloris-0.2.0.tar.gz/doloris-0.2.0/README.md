# Doloris

中山大学 2025 年《模式识别》大作业。

组员：许睿林、傅小桐。

**Doloris**：**D**etection **O**f **L**earning **O**bstacles via **R**isk-aware **I**nteraction **S**ignals.

## 环境配置

可直接运行下方命令安装 `Doloris`。

```bash
pip install doloris
```

对于项目的开发者而言，请执行下方的指令，便于本地进行开发与调试。

```bash
pip install .
```

安装成功后，执行下列指令，可以得到 `Doloris` 版本号的输出。

```bash
doloris version
```

## 使用方式

运行下列命令，启动 `Doloris`，其中 <cache path> 指明了运行时缓存的存储路径，默认存放在 `~/.doloris/`

```bash
doloris panel --cache-path <cache path>
```