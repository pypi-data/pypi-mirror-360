# Model Finetune 项目记忆 v1.0.0

## 📋 项目概览

**项目名称**: Model Finetune  
**原始名称**: WaterQuality Processor (已重命名)  
**作者**: 周元琦 (Yuan-Qi Zhou)  
**邮箱**: zyq1034378361@gmail.com  
**许可**: MIT License (Non-Commercial Use Only)  
**Python版本**: ≥3.10  
**版本**: 1.0.0 (2025-07-02)

## 🎯 核心功能

这是一个专业的**智能模型微调和自动建模工具包**，主要用于：

1. **光谱数据处理**: 处理航测光谱数据ZIP文件
2. **采样数据匹配**: 与人工采样CSV数据进行地理坐标匹配
3. **数据清洗**: 自动异常值检测和数据预处理
4. **模型训练**: 自动机器学习模型训练和优化
5. **结果加密**: 安全的模型结果存储

## 🏗️ 项目架构

采用**固定接口 + 可更新包**设计：

```
固定接口 (interface.py)     ←── 稳定的外部调用入口
    ↓
包内功能 (model-finetune)   ←── 可更新的算法实现
```

### 核心模块结构

```
src/model_finetune/
├── __init__.py              # 主API入口，版本管理
├── _version.py              # 动态版本文件 (Git标签生成)
├── unified_interface.py     # 统一接口处理器 ⭐
├── common_validators.py     # 公共验证器 ⭐
├── main.py                  # 传统main函数入口
├── data_processor.py        # 数据处理模块
├── data_merger.py          # 数据合并模块
├── downloader.py           # 资源下载器 (支持OSS/HTTP)
├── extractor.py            # ZIP文件提取器
├── geo_utils.py            # 地理工具 (坐标匹配)
├── utils.py                # 通用工具函数
├── exceptions.py           # 异常处理体系 ⭐
└── validators.py           # 输入验证器 ⭐
```

## 🔧 技术栈

- **包管理**: uv (现代Python包管理器)
- **构建系统**: setuptools + setuptools_scm
- **版本管理**: 基于Git标签的自动版本控制
- **依赖库**: numpy, pandas, scikit-learn, oss2, requests等
- **文档格式**: Markdown
- **测试框架**: 内置测试模块

## 📥 输入格式

**JSON配置格式**:
```json
{
  "file_url": "https://aims-dev.fpi-inc.site/file-base-server/api/v1/sys/download/xxx",
  "measure_data": "https://aims-dev.fpi-inc.site/file-base-server/api/v1/sys/download/yyy"
}
```

**支持两种输入方式**:
1. **直接JSON内容**: 通过stdin传递JSON字符串
2. **文件路径模式**: 传递JSON文件的绝对路径

## 📤 输出格式

**成功输出**:
```json
{
  "success": true,
  "message": "处理完成",
  "timestamp": "2024-01-01 12:00:00",
  "model_path": "/path/to/trained_model.bin",
  "metrics": {
    "r2_score": 0.85,
    "rmse": 0.123
  },
  "output_dir": "./results"
}
```

## ⚙️ 使用方式

### 1. 环境设置
```bash
# 设置版本号环境变量 (开发期必需)
export SETUPTOOLS_SCM_PRETEND_VERSION_FOR_MODEL_FINETUNE=1.0.0

# 同步依赖
uv sync
```

### 2. 固定接口调用
```bash
# 通过固定接口调用（推荐）
echo "/path/to/config.json" | python interface.py
```

### 3. 直接模块调用
```bash
# 直接JSON模式
echo '{"file_url": "...", "measure_data": "..."}' | uv run python -m model_finetune.unified_interface

# 文件路径模式 (Java常用)
echo "/path/to/config.json" | uv run python -m model_finetune.unified_interface
```

## 🔐 安全特性

1. **ZIP安全**: 防止路径遍历攻击
2. **编码检测**: 自动文件编码识别
3. **异常处理**: 完整的错误捕获和日志
4. **模型加密**: 训练结果加密存储
5. **非商用许可**: 保护知识产权

## 📁 数据流程

1. **输入**: JSON配置 (URLs或本地路径)
2. **下载**: 光谱数据ZIP + 采样数据CSV
3. **提取**: ZIP文件解压和安全检查
4. **匹配**: 地理坐标匹配 (Haversine距离)
5. **清洗**: 异常值检测 (IQR方法)
6. **训练**: 机器学习模型训练
7. **输出**: 加密模型文件 + 性能指标

## 🔧 配置管理

### 环境变量
- `SETUPTOOLS_SCM_PRETEND_VERSION_FOR_MODEL_FINETUNE`: 开发版本号
- `WATER_QUALITY_ENCRYPTION_KEY`: 加密密钥 (32字节十六进制)
- `WATER_QUALITY_SALT`: 盐值 (16字节十六进制) 
- `WATER_QUALITY_IV`: 初始化向量 (16字节十六进制)

### .env文件配置
项目支持在根目录放置`.env`文件，包含加密配置等敏感信息：
```bash
# 加密配置
WATER_QUALITY_ENCRYPTION_KEY=your_32_byte_hex_key
WATER_QUALITY_SALT=your_16_byte_hex_salt
WATER_QUALITY_IV=your_16_byte_hex_iv
```

## 🚀 最新更新 (v1.0.0)

### 已修复问题
- ✅ 完成代码重构，统一接口架构
- ✅ 创建unified_interface.py统一处理所有接口逻辑
- ✅ 创建common_validators.py消除代码重复
- ✅ 删除废弃的fixed_interface.py和interface_processor.py模块
- ✅ 修复.env文件加载路径问题，确保加密配置正确读取
- ✅ 优化文件搜索逻辑，提高反射率文件识别准确性

### 代码质量提升
- 🏗️ 重构核心处理器架构，提高模块化程度
- 🔧 优化异常处理机制，统一错误处理流程
- ✅ 所有核心模块导入测试通过
- 📋 完善项目结构和依赖管理

### 架构改进
- **模块解耦**: 通过延迟导入避免循环依赖问题
- **异常统一**: 使用统一的异常处理框架
- **配置优化**: 改进.env文件加载路径逻辑
- **测试完善**: 添加模块导入测试确保代码质量

## 🧪 测试验证

### 导入测试
```bash
# 运行模块导入测试
cd model-finetune && .venv/bin/python -c "
import sys; sys.path.insert(0, 'src')
for module in ['model_finetune', 'model_finetune.main', 'model_finetune.unified_interface']:
    __import__(module)
    print(f'✅ {module}')
"
```

### 功能测试
```bash
# 完整功能测试
export SETUPTOOLS_SCM_PRETEND_VERSION_FOR_MODEL_FINETUNE=1.0.0
echo "/path/to/test.json" | python interface.py
```

## ⚠️ 重要提醒

1. **版本环境变量**: 开发阶段必须设置环境变量
2. **加密配置**: 需要在根目录配置.env文件或设置环境变量
3. **依赖要求**: Python ≥3.10，完整依赖安装
4. **网络要求**: 需要访问目标下载服务器
5. **许可限制**: 仅限非商业用途，商业使用需联系作者

## 🔄 项目演进历史

1. **初始版本**: 水质数据处理脚本
2. **重构阶段**: 转换为PyPI包架构
3. **重命名**: waterquality-processor → model-finetune
4. **架构升级**: 固定接口 + 可更新包设计
5. **Java集成**: 添加Java调用支持
6. **代码优化**: 修复导入错误和依赖问题 (v1.0.0)

## 🎯 未来规划

- [ ] 添加更多数据格式支持
- [ ] 性能优化和并行处理
- [ ] 模型可视化和分析工具
- [ ] 云端部署和API服务
- [ ] 更多机器学习算法支持
- [ ] 完善单元测试覆盖率

---

**最后更新**: 2025年7月2日  
**维护者**: 周元琦 (zyq1034378361@gmail.com)  
**项目状态**: 稳定版本，积极维护中  
**Git标签**: v1.0.0