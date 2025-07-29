#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Model Finetune - 智能模型微调和自动建模工具包

这是一个专业的模型微调和自动建模工具包，主要用于处理光谱数据与采样数据的
智能匹配、清洗和模型训练。

核心架构：
- 固定接口 (interface.py) - 稳定的外部调用入口
- 包内功能 (本包) - 可更新的算法和工具模块

主要功能：
- 自动数据下载和预处理
- 智能数据清洗和异常值处理  
- 地理坐标匹配和数据融合
- 自动模型训练和结果加密存储

使用方式：
通过固定的 interface.py 文件调用，支持流式输入 JSON 配置。

作者: 周元琦 (Yuan-Qi Zhou)
邮箱: zyq1034378361@gmail.com
版本: 动态版本管理 (基于Git标签)
许可: MIT License (禁止商用)
"""

# 版本号获取，优先级：包元数据 > _version.py > fallback
try:
    from importlib.metadata import version, PackageNotFoundError
    try:
        __version__ = version("model-finetune")
    except PackageNotFoundError:
        # 开发环境或未安装的包，尝试从_version.py获取
        try:
            from ._version import __version__
        except ImportError:
            __version__ = "0.1.0"  # fallback版本
except ImportError:
    # Python < 3.8，使用importlib_metadata
    try:
        from importlib_metadata import version, PackageNotFoundError
        try:
            __version__ = version("model-finetune")
        except PackageNotFoundError:
            try:
                from ._version import __version__
            except ImportError:
                __version__ = "0.1.0"
    except ImportError:
        # 完全fallback
        try:
            from ._version import __version__
        except ImportError:
            __version__ = "0.1.0"

__author__ = "周元琦 (Yuan-Qi Zhou)"
__email__ = "zyq1034378361@gmail.com"
__license__ = "MIT (Non-Commercial)"

# 导入核心功能
from .main import process_data
from .unified_interface import process_interface_config, UnifiedInterface

# 导入基础工具类
from .utils import ConfigManager
from .data_processor import DataProcessor
from .downloader import ResourceDownloader
from .extractor import ZipExtractor
from .data_merger import DataMerger
from .validators import InputValidator
from .exceptions import (
    ModelFinetuneException, ValidationException, FileProcessingException,
    DataProcessingException, NetworkException, ModelException, EncryptionException
)

# 注意：geo_matcher使用频率极低，已从主要导出中移除


# 导出核心API - 极简化后的API
__all__ = [
    # 核心功能
    'process_data',                # 核心处理函数
    'process_interface_config',    # 接口处理函数
    'UnifiedInterface',            # 统一接口类
    
    # 工具类
    'ConfigManager',               # 配置管理
    'DataProcessor',               # 数据处理
    'ResourceDownloader',          # 资源下载
    'ZipExtractor',                # ZIP解压
    'DataMerger',                  # 数据合并
    'InputValidator',              # 输入验证器
    
    # 异常类
    'ModelFinetuneException',      # 基础异常
    'ValidationException',         # 验证异常
    'FileProcessingException',     # 文件处理异常
    'DataProcessingException',     # 数据处理异常
    'NetworkException',            # 网络异常
    'ModelException',              # 模型异常
    'EncryptionException',         # 加密异常
    
    # 版本信息
    '__version__'                  # 版本信息
]