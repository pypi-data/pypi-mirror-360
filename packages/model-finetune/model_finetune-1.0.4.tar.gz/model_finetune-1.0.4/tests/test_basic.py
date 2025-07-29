#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
基础测试模块 - 测试简化后的核心功能

作者: 周元琦 (Yuan-Qi Zhou)
邮箱: zyq1034378361@gmail.com
"""

import pytest
import tempfile
import json
import os
from pathlib import Path
from unittest.mock import patch, MagicMock


class TestCoreImports:
    """测试核心导入功能"""
    
    def test_basic_imports(self):
        """测试基本导入"""
        from model_finetune import (
            process_data,
            process_interface_config,
            UnifiedInterface,
            ConfigManager,
            DataProcessor,
            ResourceDownloader,
            ZipExtractor,
            DataMerger,
            __version__
        )
        
        # 验证所有核心函数/类都能正常导入
        assert process_data is not None
        assert process_interface_config is not None
        assert UnifiedInterface is not None
        assert ConfigManager is not None
        assert DataProcessor is not None
        assert ResourceDownloader is not None
        assert ZipExtractor is not None
        assert DataMerger is not None
        assert __version__ is not None
    
    def test_version_format(self):
        """测试版本号格式"""
        from model_finetune import __version__
        
        # 版本号应该是字符串格式
        assert isinstance(__version__, str)
        assert len(__version__) > 0
        # 应该包含数字或常见版本格式
        assert any(char.isdigit() for char in __version__)
    
    def test_author_info(self):
        """测试作者信息"""
        from model_finetune import __author__, __email__, __license__
        
        assert __author__ == "周元琦 (Yuan-Qi Zhou)"
        assert __email__ == "zyq1034378361@gmail.com"
        assert "Non-Commercial" in __license__


class TestUnifiedInterface:
    """测试统一接口"""
    
    def test_unified_interface_init(self):
        """测试统一接口初始化"""
        from model_finetune import UnifiedInterface
        
        interface = UnifiedInterface()
        assert interface is not None
        assert interface.output_dir.exists()
    
    def test_unified_interface_with_custom_output(self):
        """测试自定义输出目录"""
        from model_finetune import UnifiedInterface
        
        with tempfile.TemporaryDirectory() as temp_dir:
            interface = UnifiedInterface(output_dir=temp_dir)
            assert temp_dir in str(interface.output_dir)


class TestConfigManager:
    """测试配置管理器"""
    
    def test_config_manager_indicator_mapping(self):
        """测试指标映射配置"""
        from model_finetune import ConfigManager
        
        mapping = ConfigManager.get_indicator_mapping()
        assert isinstance(mapping, dict)
        assert len(mapping) > 0
        
        # 检查一些常见的映射
        assert '浊度' in mapping
        assert 'turbidity' in mapping.values()
    
    def test_config_manager_encryption_config(self):
        """测试加密配置"""
        from model_finetune import ConfigManager
        
        config = ConfigManager.get_encryption_config()
        assert isinstance(config, dict)
        assert 'password' in config
        assert 'salt' in config
        assert 'iv' in config


class TestProcessInterfaceConfig:
    """测试process_interface_config函数"""
    
    def test_process_interface_config_invalid_input(self):
        """测试无效输入"""
        from model_finetune import process_interface_config
        
        # 测试空配置
        result = process_interface_config({})
        assert isinstance(result, dict)
        assert result.get("success") is False
        assert "error" in result
    
    def test_process_interface_config_missing_fields(self):
        """测试缺少必需字段"""
        from model_finetune import process_interface_config
        
        # 测试缺少measure_data字段
        config = {"file_url": "test_url"}
        result = process_interface_config(config)
        assert isinstance(result, dict)
        assert result.get("success") is False
        assert "error" in result
    
    @patch('model_finetune.unified_interface.ResourceDownloader')
    def test_process_interface_config_download_failure(self, mock_downloader):
        """测试下载失败的情况"""
        from model_finetune import process_interface_config
        
        # 模拟下载失败
        mock_instance = MagicMock()
        mock_instance.download.return_value = None
        mock_downloader.return_value = mock_instance
        
        config = {
            "file_url": "http://fake-url.com/test.zip",
            "measure_data": "http://fake-url.com/test.csv"
        }
        
        result = process_interface_config(config)
        assert isinstance(result, dict)
        assert result.get("success") is False
        assert "error" in result


class TestDataProcessor:
    """测试数据处理器"""
    
    def test_data_processor_init(self):
        """测试数据处理器初始化"""
        from model_finetune import DataProcessor
        
        processor = DataProcessor()
        assert processor is not None


class TestResourceDownloader:
    """测试资源下载器"""
    
    def test_resource_downloader_init(self):
        """测试资源下载器初始化"""
        from model_finetune import ResourceDownloader
        
        with tempfile.TemporaryDirectory() as temp_dir:
            downloader = ResourceDownloader(temp_dir)
            assert downloader is not None


class TestZipExtractor:
    """测试ZIP解压器"""
    
    def test_zip_extractor_init(self):
        """测试ZIP解压器初始化"""
        from model_finetune import ZipExtractor
        
        extractor = ZipExtractor()
        assert extractor is not None


class TestDataMerger:
    """测试数据合并器"""
    
    def test_data_merger_init(self):
        """测试数据合并器初始化"""
        from model_finetune import DataMerger
        
        merger = DataMerger()
        assert merger is not None


class TestModuleStructure:
    """测试模块结构"""
    
    def test_all_exports(self):
        """测试__all__导出"""
        import model_finetune
        
        expected_exports = [
            'process_data',
            'process_interface_config',
            'UnifiedInterface',
            'ConfigManager',
            'DataProcessor',
            'ResourceDownloader',
            'ZipExtractor',
            'DataMerger',
            '__version__'
        ]
        
        for export in expected_exports:
            assert hasattr(model_finetune, export), f"Missing export: {export}"
    
    def test_no_removed_exports(self):
        """测试已删除的导出不存在"""
        import model_finetune
        
        removed_exports = [
            'ModelProcessor',
            'BatchProcessor',
            'ProcessingResult',
            'GeoMatcher',
            'InterfaceProcessor',
            'FixedInterface'
        ]
        
        for export in removed_exports:
            assert not hasattr(model_finetune, export), f"Should not export: {export}"


class TestErrorHandling:
    """测试错误处理"""
    
    def test_import_errors_handled(self):
        """测试导入错误处理"""
        # 这个测试确保模块能够正常导入，即使某些依赖不可用
        try:
            import model_finetune
            assert model_finetune is not None
        except ImportError as e:
            pytest.fail(f"Module import failed: {e}")
    
    def test_version_fallback(self):
        """测试版本号回退机制"""
        from model_finetune import __version__
        
        # 版本号应该有有效值，即使setuptools_scm失败
        assert __version__ is not None
        assert isinstance(__version__, str)
        assert len(__version__) > 0


# 集成测试相关
class TestIntegration:
    """集成测试"""
    
    def test_config_to_interface_flow(self):
        """测试配置到接口的完整流程（不涉及实际下载）"""
        from model_finetune import process_interface_config
        
        # 使用虚假但格式正确的配置
        config = {
            "file_url": "http://example.com/test.zip",
            "measure_data": "http://example.com/test.csv"
        }
        
        # 这应该会因为下载失败而返回错误，但不应该崩溃
        result = process_interface_config(config)
        assert isinstance(result, dict)
        assert "success" in result
        assert "error" in result or result.get("success") is True
    
    def test_process_data_with_invalid_paths(self):
        """测试使用无效路径的process_data函数"""
        from model_finetune import process_data
        
        # 使用不存在的文件路径
        result = process_data(
            zip_path="/nonexistent/path.zip",
            measure_data_path="/nonexistent/measure.csv"
        )
        
        # 应该返回False或None，而不是崩溃
        assert result is False or result is None


if __name__ == "__main__":
    # 设置测试环境
    os.environ['SETUPTOOLS_SCM_PRETEND_VERSION_FOR_MODEL_FINETUNE'] = '1.0.0'
    
    # 运行测试
    pytest.main([__file__, "-v"])