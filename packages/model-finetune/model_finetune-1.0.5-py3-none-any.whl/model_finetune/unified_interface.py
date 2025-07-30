#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
统一接口模块

合并了原来的 fixed_interface.py 和 interface_processor.py 的功能，
提供统一的、简化的接口处理能力。
"""

import sys
import json
import logging
import traceback
import argparse
import os
import re
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

# 导入公共模块
from .common_validators import CommonValidators, CommonUtils
from .downloader import ResourceDownloader
from .validators import InputValidator, ValidationError
from .exceptions import ExceptionHandler, convert_to_standard_exception


class ErrorCodes:
    """错误码定义"""
    SUCCESS = 0
    INPUT_ERROR = 1001
    CONFIG_ERROR = 1002
    PACKAGE_ERROR = 1003
    PROCESSING_ERROR = 1004
    SYSTEM_ERROR = 1005


class UnifiedInterface:
    """
    统一接口类
    
    合并了固定接口和接口处理器的功能，提供完整的接口服务。
    """
    
    def __init__(self, output_dir: str = "./interface_output"):
        """
        初始化统一接口
        
        Args:
            output_dir: 输出目录路径
        """
        # 添加时间戳文件夹避免多次运行时文件覆盖
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        base_output_dir = Path(output_dir)
        self.output_dir = base_output_dir / f"run_{timestamp}"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 设置日志（输出到文件，不干扰stdout）
        self._setup_logging()
    
    def _setup_logging(self):
        """设置日志配置"""
        log_file = self.output_dir / "interface.log"
        
        # 创建文件处理器
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        
        # 设置日志格式
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        
        # 配置接口日志器
        self.logger = logging.getLogger('unified_interface')
        self.logger.setLevel(logging.INFO)
        self.logger.handlers.clear()
        self.logger.addHandler(file_handler)
        self.logger.propagate = False
        
        # 配置包内模块的日志器，让它们也使用同一个文件处理器
        package_loggers = [
            'model_finetune',
            'model_finetune.downloader',
            'model_finetune.main',
            'model_finetune.data_processor',
            'model_finetune.extractor',
            'autowaterqualitymodeler'
        ]
        
        for logger_name in package_loggers:
            pkg_logger = logging.getLogger(logger_name)
            # 检查日志器是否已经配置过，避免重复配置
            if not pkg_logger.handlers or pkg_logger.handlers[0] != file_handler:
                pkg_logger.setLevel(logging.INFO)
                pkg_logger.handlers.clear()
                pkg_logger.addHandler(file_handler)
                pkg_logger.propagate = False
                self.logger.debug(f"配置日志器: {logger_name}")
            else:
                self.logger.debug(f"日志器 {logger_name} 已配置，跳过")
    
    def read_input_stream(self) -> Optional[Dict[str, Any]]:
        """
        从标准输入读取数据
        
        支持两种输入模式：
        1. JSON文件路径
        2. 直接JSON内容
        
        Returns:
            解析后的JSON配置字典
        """
        try:
            self.logger.info("开始读取标准输入")
            
            # 读取输入
            input_data = sys.stdin.read().strip()
            
            if not input_data:
                self.logger.error("标准输入为空")
                return None
            
            self.logger.info(f"接收到输入数据: {input_data[:100]}...")
            
            # 判断是文件路径还是JSON内容
            if self._is_file_path(input_data):
                self.logger.info("检测到文件路径模式")
                return self._read_json_file(input_data)
            else:
                self.logger.info("检测到JSON内容模式")
                return self._parse_json_string(input_data)
                
        except Exception as e:
            self.logger.error(f"读取输入流失败: {e}")
            return None
    
    def _is_file_path(self, input_data: str) -> bool:
        """判断输入是否为文件路径"""
        # 先使用公共验证器判断基本格式
        is_file_path = CommonValidators.is_file_path(input_data)
        
        # 如果检测到可疑路径，额外记录日志
        if input_data and len(input_data) <= 1000:
            suspicious_patterns = ['../', '..\\', '~/', '/etc/', '/proc/', '/sys/']
            if any(pattern in input_data.lower() for pattern in suspicious_patterns):
                self.logger.warning(f"检测到可疑路径模式: {input_data}")
                
        return is_file_path
    
    def _convert_windows_path(self, path: str) -> str:
        """转换Windows路径到WSL路径（如果在WSL环境中）"""
        # 检查是否在WSL环境中
        try:
            with open('/proc/version', 'r') as f:
                if 'microsoft' in f.read().lower():
                    # 在WSL环境中，转换Windows路径
                    # 例如: D:\path\file.json -> /mnt/d/path/file.json
                    if re.match(r'^[A-Za-z]:', path):
                        drive = path[0].lower()
                        rest_path = path[2:].replace('\\', '/')
                        converted_path = f'/mnt/{drive}{rest_path}'
                        self.logger.debug(f"Windows路径转换: {path} -> {converted_path}")
                        return converted_path
        except (FileNotFoundError, PermissionError):
            # 不在WSL环境或无法检测，使用原路径
            pass
        
        return path
    
    def _read_json_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """从文件读取JSON配置"""
        try:
            # 清理路径：移除引号并标准化路径
            file_path = file_path.strip().strip('"').strip("'")
            
            # Windows路径转换处理（WSL环境下）
            file_path = self._convert_windows_path(file_path)
            
            file_path = Path(file_path)
            self.logger.info(f"读取JSON文件: {file_path}")
            
            if not file_path.exists():
                self.logger.error(f"文件不存在: {file_path}")
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            
            config = json.loads(content)
            self.logger.info(f"JSON文件解析成功: {list(config.keys())}")
            return config
            
        except Exception as e:
            self.logger.error(f"读取JSON文件失败: {e}")
            return None
    
    def _parse_json_string(self, content: str) -> Optional[Dict[str, Any]]:
        """解析JSON字符串"""
        try:
            config = json.loads(content)
            self.logger.info(f"JSON字符串解析成功: {list(config.keys())}")
            return config
            
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON解析失败: {e}")
            return None
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """验证配置格式"""
        if not isinstance(config, dict):
            self.logger.error("配置不是字典格式")
            return False
        
        # 检查必需字段
        required_fields = ["file_url", "measure_data"]
        for field in required_fields:
            if field not in config:
                self.logger.error(f"缺少必需字段: {field}")
                return False
            
            if not isinstance(config[field], str) or not config[field].strip():
                self.logger.error(f"字段 {field} 必须是非空字符串")
                return False
        
        self.logger.info("配置验证通过")
        return True
    
    def process_data_from_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        从配置字典处理数据并返回标准化结果
        
        Args:
            config: 包含file_url和measure_data的配置字典
            
        Returns:
            标准化的处理结果字典
        """
        try:
            self.logger.info("开始处理数据配置")
            
            # 使用统一的输入验证器
            try:
                # 验证配置字典
                validated_config = InputValidator.validate_config_dict(
                    config, 
                    required_keys=["file_url", "measure_data"]
                )
                
                zip_url = validated_config["file_url"]
                measure_url = validated_config["measure_data"]
                
                # 验证URL格式
                if CommonValidators.looks_like_url(zip_url):
                    InputValidator.validate_url(zip_url)
                if CommonValidators.looks_like_url(measure_url):
                    InputValidator.validate_url(measure_url)
                    
            except ValidationError as e:
                return self._create_error_result(f"输入验证失败: {str(e)}")
            
            self.logger.info(f"处理数据源: {zip_url}")
            self.logger.info(f"测量数据: {measure_url}")
            
            # 创建下载目录
            downloads_dir = self.output_dir / "downloads"
            downloads_dir.mkdir(exist_ok=True)
            
            # 下载文件
            downloader = ResourceDownloader(str(downloads_dir))
            
            self.logger.info("开始下载ZIP文件...")
            zip_path = downloader.download(zip_url)
            if not zip_path:
                return self._create_error_result("ZIP文件下载失败")
            
            self.logger.info("开始下载测量数据文件...")
            csv_path = downloader.download(measure_url)
            if not csv_path:
                return self._create_error_result("测量数据文件下载失败")
            
            self.logger.info(f"文件下载完成: ZIP={zip_path}, CSV={csv_path}")
            
            # 调用核心处理函数
            from .main import process_data
            result = process_data(zip_path=zip_path, measure_data_path=csv_path)
            
            # 处理结果并加密保存
            if result:
                # 提取模型结果
                if isinstance(result, tuple) and len(result) >= 1:
                    model_result = result[0]
                else:
                    model_result = result
                
                # 加密保存模型结果
                encrypted_path = self._encrypt_and_save_model(model_result)
                
                return self._create_success_result(
                    model_path=encrypted_path,
                    message="数据处理和模型训练成功完成"
                )
            else:
                return self._create_error_result("模型训练失败")
                
        except Exception as e:
            # 使用统一的异常处理器
            handler = ExceptionHandler(self.logger)
            standard_exception = convert_to_standard_exception(e)
            error_info = handler.handle_exception(standard_exception, "接口数据处理")
            
            return {
                "success": False,
                "timestamp": CommonUtils.get_timestamp(),
                **error_info
            }
    
    def process_data(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理数据 - 调用统一接口的统一处理方法
        
        Args:
            config: 配置字典
            
        Returns:
            处理结果字典
        """
        try:
            self.logger.info("开始调用统一接口处理数据")
            
            # 调用统一处理方法
            result = self.process_data_from_config(config)
            
            self.logger.info(f"统一接口处理完成，成功: {result.get('success', False)}")
            return result
            
        except Exception as e:
            self.logger.error(f"处理数据时发生异常: {e}")
            self.logger.error(traceback.format_exc())
            
            return {
                "success": False,
                "error": f"处理异常: {str(e)}",
                "timestamp": CommonUtils.get_timestamp()
            }
    
    def _encrypt_and_save_model(self, model_result: Any) -> Optional[str]:
        """
        加密并保存模型结果
        
        Args:
            model_result: 模型结果对象
            
        Returns:
            加密文件的路径，失败返回None
        """
        if not model_result:
            return None
            
        try:
            # 导入加密相关模块
            from autowaterqualitymodeler.utils.encryption import encrypt_data_to_file
            
            # 创建模型保存目录
            models_dir = self.output_dir / "models"
            models_dir.mkdir(exist_ok=True)
            
            # 获取加密配置
            encryption_config = self._get_encryption_config()
            
            # 验证数据格式 - 确保是键值对格式
            if not CommonValidators.validate_model_data(model_result, self.logger):
                self.logger.error("模型数据验证失败：数据不是有效的键值对格式")
                return None
            
            # 将模型结果中的keys添加到日志
            if hasattr(model_result, 'keys'):
                self.logger.info(f"模型结果keys: {list(model_result.keys())}")

            # 加密保存
            encrypted_path = encrypt_data_to_file(
                data_obj=model_result,
                password=encryption_config['password'],
                salt=encryption_config['salt'],
                iv=encryption_config['iv'],
                output_dir=str(models_dir),
                logger=self.logger,
            )
            
            if encrypted_path:
                self.logger.info(f"模型已加密保存到: {encrypted_path}")
                return str(encrypted_path)
            else:
                self.logger.error("模型加密保存失败")
                return None
                
        except Exception as e:
            self.logger.error(f"加密模型失败: {e}")
            return None
    
    def _get_encryption_config(self) -> Dict[str, Any]:
        """
        获取加密配置
        
        Returns:
            加密配置字典
        """
        try:
            from .utils import ConfigManager
            return ConfigManager.get_encryption_config()
        except (ImportError, ModuleNotFoundError, AttributeError) as e:
            # 如果无法获取配置，报错不提供默认配置
            error_msg = f"加密配置加载失败: {e}"
            self.logger.error(error_msg)
            self.logger.error("请按照 SECURITY_CONFIG.md 指南配置加密密钥")
            raise RuntimeError(error_msg) from e
    
    def _create_success_result(self, model_path: str, message: str = "处理成功") -> Dict[str, Any]:
        """
        创建成功结果
        
        Args:
            model_path: 模型文件路径
            message: 成功消息
            
        Returns:
            标准化的成功结果字典
        """
        return {
            "success": True,
            "message": message,
            "model_path": model_path,
            "metrics": {"processing": "completed"},
            "output_dir": str(self.output_dir),
            "timestamp": CommonUtils.get_timestamp()
        }
    
    def _create_error_result(self, error_message: str) -> Dict[str, Any]:
        """
        创建错误结果
        
        Args:
            error_message: 错误消息
            
        Returns:
            标准化的错误结果字典
        """
        return {
            "success": False,
            "error": error_message,
            "timestamp": CommonUtils.get_timestamp()
        }
    
    def run(self, debug_mode: bool = False) -> int:
        """
        主运行方法
        
        Args:
            debug_mode: 是否启用调试模式
        
        Returns:
            退出码：0表示成功，1表示失败
        """
        try:
            self.logger.info("统一接口开始运行")
            
            # 1. 读取输入
            if debug_mode:
                self.logger.info("调试模式：使用test.json文件")
                # 调试模式：从test.json读取配置
                test_json_path = Path(__file__).parent.parent.parent / "test.json"
                if test_json_path.exists():
                    config = self._read_json_file(str(test_json_path))
                else:
                    self._output_error(f"调试模式下test.json文件不存在: {test_json_path}", ErrorCodes.INPUT_ERROR)
                    return 1
            else:
                # 正常模式：从标准输入读取
                config = self.read_input_stream()
            
            if config is None:
                self._output_error("无法读取或解析输入数据", ErrorCodes.INPUT_ERROR)
                return 1
            
            # 2. 验证配置
            if not self.validate_config(config):
                self._output_error("配置验证失败", ErrorCodes.CONFIG_ERROR)
                return 1
            
            # 3. 处理数据
            result = self.process_data(config)
            
            # 4. 记录完整结果到日志
            self.logger.info(f"处理结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
            
            # 5. 只输出模型路径的绝对路径到stdout
            if result.get("success", False) and result.get("model_path"):
                model_path = Path(result["model_path"])
                print(str(model_path.resolve()))
            else:
                # 处理失败时输出错误信息
                error_msg = result.get("error", "处理失败")
                error_code = result.get("error_code", ErrorCodes.PROCESSING_ERROR)
                print(f"error[{error_code}]: {error_msg}")
                self.logger.error(f"处理失败: {error_msg}")
            
            # 6. 返回退出码
            exit_code = 0 if result.get("success", False) else 1
            self.logger.info(f"接口运行完成，退出码: {exit_code}")
            
            return exit_code
            
        except Exception as e:
            self.logger.error(f"接口运行异常: {e}")
            self._output_error(f"系统异常: {str(e)}", ErrorCodes.SYSTEM_ERROR)
            return 1
    
    def _output_error(self, error_message: str, error_code: int = ErrorCodes.SYSTEM_ERROR):
        """输出错误信息"""
        error_output = {
            "success": False,
            "error": error_message,
            "error_code": error_code,
            "timestamp": CommonUtils.get_timestamp()
        }
        # 记录完整错误信息到日志
        self.logger.error(f"错误输出: {json.dumps(error_output, ensure_ascii=False, indent=2)}")
        
        # 只输出简洁的错误信息到stdout
        print(f"error[{error_code}]: {error_message}")


def run_interface(output_dir: str = "./interface_output", debug_mode: bool = False) -> int:
    """
    运行统一接口的主函数
    
    Args:
        output_dir: 输出目录路径
        debug_mode: 是否启用调试模式
    
    Returns:
        退出码：0表示成功，1表示失败
    """
    interface = UnifiedInterface(output_dir=output_dir)
    return interface.run(debug_mode=debug_mode)


def process_interface_config(config: Dict[str, Any], output_dir: str = "./interface_output", logger: Optional[logging.Logger] = None) -> Dict[str, Any]:
    """
    便捷函数：从配置处理数据
    
    Args:
        config: 配置字典
        output_dir: 输出目录
        logger: 外部传入的日志器
        
    Returns:
        处理结果字典
    """
    interface = UnifiedInterface(output_dir=output_dir)
    # 如果有外部日志器，使用外部日志器
    if logger is not None:
        interface.logger = logger
    return interface.process_data_from_config(config)


def main():
    """
    主入口函数
    
    支持命令行参数：
    --output-dir: 指定输出目录
    """
    # 版本信息
    __version__ = "1.0.2"
    
    parser = argparse.ArgumentParser(
        description="Model Finetune 统一接口",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
    echo "/path/to/config.json" | python -m model_finetune.unified_interface
    cat path.txt | python -m model_finetune.unified_interface
    echo '{"file_url": "...", "measure_data": "..."}' | python -m model_finetune.unified_interface

配置格式:
    {
        "file_url": "数据ZIP文件URL",
        "measure_data": "测量数据CSV文件URL"
    }
        """
    )
    
    parser.add_argument(
        "--output-dir",
        default="./interface_output",
        help="输出目录路径 (默认: ./interface_output)"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="启用调试模式，使用test.json文件而不是标准输入"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version=f"Unified Interface {__version__}"
    )
    
    args = parser.parse_args()
    
    # 运行接口
    exit_code = run_interface(output_dir=args.output_dir, debug_mode=args.debug)
    sys.exit(exit_code)