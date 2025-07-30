# Model Finetune 🚀

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT (Non-Commercial)](https://img.shields.io/badge/License-MIT%20(Non--Commercial)-orange.svg)](LICENSE)

**智能模型微调和自动建模工具包**

Model Finetune 是一个专业的Python包，专门用于处理光谱数据与采样数据的智能匹配、清洗和机器学习模型训练。

## 🏗️ 项目架构

采用**固定接口 + 可更新包**的设计架构：

```
固定接口 (interface.py)     ←── 稳定的外部调用入口
    ↓
包内功能 (model-finetune)   ←── 可更新的算法实现
```

## ✨ 主要功能

- 🎯 **智能数据匹配**: 光谱数据与采样数据的地理坐标匹配
- 🧹 **数据清洗**: 自动异常值检测和数据预处理
- 🤖 **自动建模**: 智能模型训练和参数优化
- 🌐 **多数据源**: 支持URL下载和本地文件处理
- 🔐 **安全存储**: 加密的模型结果存储
- 📊 **流式处理**: 支持JSON配置的流式输入

## ⚙️ 配置设置

### 🔐 安全配置（必需）

#### ⭐ 推荐：.env文件方式（跨平台）
```bash
# 一键生成.env文件（包含所有必需配置）
python generate_debug_config.py env

# 自动加载，无需额外设置
# 支持 Windows、Linux、macOS
```

#### 其他方式
```bash
# 环境变量
export WATER_QUALITY_ENCRYPTION_KEY="your_key"
export WATER_QUALITY_SALT="your_salt"
export WATER_QUALITY_IV="your_iv"

# JSON配置文件
export WATER_QUALITY_CONFIG_FILE="./config.json"

# 二进制密钥文件
export WATER_QUALITY_KEY_FILE="./secret.key"
```

📝 详细配置指南请查看 [SECURITY_CONFIG.md](SECURITY_CONFIG.md)

### 🔧 调试配置（开发环境）

```bash
# 在.env文件中添加调试配置
# DEBUG_ZIP_PATH=/path/to/test.zip
# DEBUG_CSV_PATH=/path/to/test.csv

# 或者使用环境变量
export DEBUG_ZIP_PATH="/path/to/test.zip"
export DEBUG_CSV_PATH="/path/to/test.csv"

# 或者使用JSON配置文件
python generate_debug_config.py debug
```

## 🚀 快速使用

### 安装

```bash
# 安装包
pip install model-finetune

# 或使用uv（推荐）
uv add model-finetune
```

### 基本使用

通过固定接口调用，支持两种输入方式：

#### 1. 直接JSON输入

```bash
echo '{"file_url": "数据ZIP的URL", "measure_data": "测量数据CSV的URL"}' | python interface.py
```

#### 2. JSON文件路径输入

```bash
echo "/path/to/config.json" | python interface.py
```

### 配置文件格式

创建 `config.json` 文件：

```json
{
  "file_url": "https://example.com/spectral_data.zip",
  "measure_data": "https://example.com/ground_truth.csv"
}
```

### 使用示例

```bash
# Windows路径（WSL环境自动转换）
echo 'D:\data\config.json' | python interface.py

# Linux路径
echo '/mnt/d/data/config.json' | python interface.py

# 直接JSON
echo '{"file_url": "https://...", "measure_data": "https://..."}' | python interface.py
```

## 📋 输出结果

- **成功时**: 输出加密模型文件的绝对路径
- **失败时**: 输出 `error[错误码]: 错误信息`
- **日志文件**: 自动保存在 `./interface_output/run_时间戳/interface.log`

## 🔄 算法更新流程

1. 修改 `model-finetune` 包中的算法代码
2. 重新发布包: `pip install --upgrade model-finetune`
3. **固定接口自动使用新算法**，无需修改

## 🛠️ 开发环境

### 使用 uv 管理环境

```bash
# 安装依赖
uv sync

# 运行开发版本
uv run python interface.py

# 运行测试
uv run pytest tests/
```

### 使用 pip 管理环境

```bash
# 安装开发版本
pip install -e .

# 设置版本环境变量（开发阶段）
export SETUPTOOLS_SCM_PRETEND_VERSION_FOR_MODEL_FINETUNE=1.0.0
```

## 📁 项目结构

```
project/
├── interface.py                    # 固定接口文件（永不变更）
└── model-finetune/                # 可更新的算法包
    ├── src/model_finetune/
    │   ├── main.py                # 核心处理逻辑
    │   ├── unified_interface.py   # 统一接口处理器
    │   ├── common_validators.py   # 公共验证器
    │   ├── data_processor.py      # 数据处理
    │   ├── downloader.py          # 文件下载
    │   ├── extractor.py           # ZIP解压
    │   ├── data_merger.py         # 数据合并
    │   ├── geo_utils.py           # 地理工具
    │   └── utils.py              # 通用工具
    ├── tests/                     # 测试文件
    └── pyproject.toml            # 包配置
```

## 🧪 测试

```bash
# 基础功能测试
uv run python -c "from model_finetune import process_interface_config; print('导入成功')"

# 接口测试
echo '{"file_url": "test", "measure_data": "test"}' | timeout 5 uv run python interface.py

# 完整测试套件
uv run pytest tests/ -v
```

## 🔧 配置选项

### 环境变量

```bash
# 开发阶段版本号
export SETUPTOOLS_SCM_PRETEND_VERSION_FOR_MODEL_FINETUNE=1.0.0

# OSS配置（如使用阿里云存储）
export OSS_ACCESS_KEY_ID=your_key_id
export OSS_ACCESS_KEY_SECRET=your_secret
```

### 调试模式

```bash
# 启用调试模式
python interface.py --debug
```

## 🆘 故障排除

### 常见问题

1. **路径问题**: Windows路径在WSL环境下会自动转换
2. **版本问题**: 开发环境需要设置 `SETUPTOOLS_SCM_PRETEND_VERSION`
3. **权限问题**: 确保对输出目录有写权限

### 日志查看

```bash
# 查看最新日志
tail -f ./interface_output/run_*/interface.log
```

## 📄 许可证

本项目采用 **MIT (Non-Commercial Use Only)** 许可证：

- ✅ **允许**: 研究、教育、个人使用
- ❌ **禁止**: 任何形式的商业使用
- 📧 **商业授权**: 请联系 zyq1034378361@gmail.com

详情请查看 [LICENSE](LICENSE) 文件。

## 👨‍💻 作者

**周元琦 (Yuan-Qi Zhou)**
- 📧 Email: zyq1034378361@gmail.com
- 🌟 专注于智能数据处理和机器学习

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！请注意：
- 保持固定接口的稳定性
- 算法改进请在包内实现
- 遵循项目的编码规范

## 📞 支持

如有问题，请通过以下方式联系：

- 📧 **邮箱**: zyq1034378361@gmail.com
- 🐛 **问题反馈**: 通过邮箱联系
- 📖 **使用文档**: 查看项目内的 Markdown 文档

---

**让模型微调变得简单高效哟！** 🎯