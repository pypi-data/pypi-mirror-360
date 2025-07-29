#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
输入验证模块 - 统一的输入验证器
"""

import os
import re
import logging
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional, Union
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """验证异常"""
    pass


class InputValidator:
    """统一的输入验证器"""
    
    # 支持的文件扩展名
    SUPPORTED_ZIP_EXTENSIONS = {'.zip', '.rar', '.7z'}
    SUPPORTED_CSV_EXTENSIONS = {'.csv', '.txt'}
    SUPPORTED_URL_SCHEMES = {'http', 'https', 'ftp', 'file'}
    
    # 文件大小限制
    MAX_ZIP_SIZE_MB = 500  # 500MB
    MAX_CSV_SIZE_MB = 50   # 50MB
    MIN_FILE_SIZE_BYTES = 10  # 10字节
    
    @classmethod
    def validate_file_path(cls, file_path: str, file_type: str = "文件") -> str:
        """
        验证文件路径
        
        Args:
            file_path: 文件路径
            file_type: 文件类型描述
            
        Returns:
            str: 标准化的文件路径
            
        Raises:
            ValidationError: 验证失败
        """
        if not file_path:
            raise ValidationError(f"{file_type}路径不能为空")
        
        if not isinstance(file_path, (str, Path)):
            raise ValidationError(f"{file_type}路径必须是字符串或Path对象，获得: {type(file_path)}")
        
        # 转换为字符串并标准化
        file_path = str(file_path).strip()
        
        if not file_path:
            raise ValidationError(f"{file_type}路径不能为空白字符")
        
        # 检查路径长度
        if len(file_path) > 4096:  # 大多数文件系统的路径长度限制
            raise ValidationError(f"{file_type}路径过长 (>{4096}字符)")
        
        # 检查非法字符
        illegal_chars = ['<', '>', '|', '?', '*']
        for char in illegal_chars:
            if char in file_path:
                raise ValidationError(f"{file_type}路径包含非法字符: {char}")
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            raise ValidationError(f"{file_type}不存在: {file_path}")
        
        # 检查是否为文件（不是目录）
        if not os.path.isfile(file_path):
            raise ValidationError(f"路径不是文件: {file_path}")
        
        # 检查文件权限
        if not os.access(file_path, os.R_OK):
            raise ValidationError(f"没有读取{file_type}的权限: {file_path}")
        
        return os.path.abspath(file_path)
    
    @classmethod
    def validate_zip_file(cls, zip_path: str) -> str:
        """
        验证ZIP文件
        
        Args:
            zip_path: ZIP文件路径
            
        Returns:
            str: 验证后的文件路径
            
        Raises:
            ValidationError: 验证失败
        """
        # 基础文件验证
        zip_path = cls.validate_file_path(zip_path, "ZIP文件")
        
        # 检查文件扩展名
        file_ext = Path(zip_path).suffix.lower()
        if file_ext not in cls.SUPPORTED_ZIP_EXTENSIONS:
            raise ValidationError(f"不支持的压缩文件格式: {file_ext}，支持: {cls.SUPPORTED_ZIP_EXTENSIONS}")
        
        # 检查文件大小
        file_size = os.path.getsize(zip_path)
        if file_size < cls.MIN_FILE_SIZE_BYTES:
            raise ValidationError(f"ZIP文件太小 ({file_size}字节)，可能已损坏")
        
        max_size_bytes = cls.MAX_ZIP_SIZE_MB * 1024 * 1024
        if file_size > max_size_bytes:
            raise ValidationError(f"ZIP文件过大 ({file_size/1024/1024:.1f}MB)，限制: {cls.MAX_ZIP_SIZE_MB}MB")
        
        # 检查ZIP文件完整性
        if file_ext == '.zip':
            import zipfile
            try:
                with zipfile.ZipFile(zip_path, 'r') as zip_file:
                    # 尝试读取文件列表
                    file_list = zip_file.namelist()
                    if not file_list:
                        raise ValidationError("ZIP文件为空")
                    
                    # 检查文件列表中是否有可疑的路径
                    for filename in file_list:
                        if cls._is_suspicious_zip_path(filename):
                            raise ValidationError(f"ZIP文件包含可疑路径: {filename}")
                    
                    logger.debug(f"ZIP文件验证通过: {len(file_list)}个文件")
                    
            except zipfile.BadZipFile:
                raise ValidationError(f"ZIP文件已损坏或格式无效: {zip_path}")
            except Exception as e:
                raise ValidationError(f"ZIP文件验证失败: {str(e)}")
        
        return zip_path
    
    @classmethod
    def validate_csv_file(cls, csv_path: str) -> str:
        """
        验证CSV文件
        
        Args:
            csv_path: CSV文件路径
            
        Returns:
            str: 验证后的文件路径
            
        Raises:
            ValidationError: 验证失败
        """
        # 基础文件验证
        csv_path = cls.validate_file_path(csv_path, "CSV文件")
        
        # 检查文件扩展名
        file_ext = Path(csv_path).suffix.lower()
        if file_ext not in cls.SUPPORTED_CSV_EXTENSIONS:
            raise ValidationError(f"不支持的数据文件格式: {file_ext}，支持: {cls.SUPPORTED_CSV_EXTENSIONS}")
        
        # 检查文件大小
        file_size = os.path.getsize(csv_path)
        if file_size < cls.MIN_FILE_SIZE_BYTES:
            raise ValidationError(f"CSV文件太小 ({file_size}字节)，可能为空")
        
        max_size_bytes = cls.MAX_CSV_SIZE_MB * 1024 * 1024
        if file_size > max_size_bytes:
            raise ValidationError(f"CSV文件过大 ({file_size/1024/1024:.1f}MB)，限制: {cls.MAX_CSV_SIZE_MB}MB")
        
        # 尝试读取文件头部，验证格式
        try:
            from .utils import EncodingDetector
            detector = EncodingDetector()
            
            # 只读取前几行进行验证
            with open(csv_path, 'rb') as f:
                sample_data = f.read(8192)  # 读取前8KB
            
            # 检测编码
            import chardet
            encoding_result = chardet.detect(sample_data)
            encoding = encoding_result.get('encoding', 'utf-8')
            
            # 尝试解码
            try:
                sample_text = sample_data.decode(encoding, errors='ignore')
            except Exception:
                sample_text = sample_data.decode('utf-8', errors='ignore')
            
            # 检查是否看起来像CSV
            lines = sample_text.split('\n')[:5]  # 只检查前5行
            valid_lines = 0
            
            for line in lines:
                line = line.strip()
                if line and (',' in line or '\t' in line or ';' in line):
                    valid_lines += 1
            
            if valid_lines == 0 and len(lines) > 1:
                logger.warning(f"CSV文件可能不包含分隔符，请检查格式: {csv_path}")
            
            logger.debug(f"CSV文件验证通过: {file_size}字节, 编码: {encoding}")
            
        except Exception as e:
            logger.warning(f"CSV文件格式验证失败: {str(e)}")
            # 不抛出异常，允许后续处理尝试读取
        
        return csv_path
    
    @classmethod
    def validate_url(cls, url: str) -> str:
        """
        验证URL
        
        Args:
            url: URL字符串
            
        Returns:
            str: 验证后的URL
            
        Raises:
            ValidationError: 验证失败
        """
        if not url:
            raise ValidationError("URL不能为空")
        
        if not isinstance(url, str):
            raise ValidationError(f"URL必须是字符串，获得: {type(url)}")
        
        url = url.strip()
        
        if not url:
            raise ValidationError("URL不能为空白字符")
        
        # 检查URL长度
        if len(url) > 2048:  # RFC 2616建议的URL长度限制
            raise ValidationError(f"URL过长 (>{2048}字符)")
        
        # 解析URL
        try:
            parsed = urlparse(url)
        except Exception as e:
            raise ValidationError(f"URL格式无效: {str(e)}")
        
        # 检查协议
        if not parsed.scheme:
            raise ValidationError("URL缺少协议 (http://, https://等)")
        
        if parsed.scheme.lower() not in cls.SUPPORTED_URL_SCHEMES:
            raise ValidationError(f"不支持的URL协议: {parsed.scheme}，支持: {cls.SUPPORTED_URL_SCHEMES}")
        
        # 检查主机名
        if not parsed.netloc and parsed.scheme != 'file':
            raise ValidationError("URL缺少主机名")
        
        # 检查可疑字符
        suspicious_patterns = [
            r'javascript:', r'data:', r'vbscript:', r'file:///etc', 
            r'file:///proc', r'file:///dev'
        ]
        
        url_lower = url.lower()
        for pattern in suspicious_patterns:
            if re.search(pattern, url_lower):
                raise ValidationError(f"URL包含可疑模式: {pattern}")
        
        return url
    
    @classmethod
    def validate_config_dict(cls, config: Dict[str, Any], required_keys: List[str] = None) -> Dict[str, Any]:
        """
        验证配置字典
        
        Args:
            config: 配置字典
            required_keys: 必需的键列表
            
        Returns:
            Dict[str, Any]: 验证后的配置
            
        Raises:
            ValidationError: 验证失败
        """
        if not isinstance(config, dict):
            raise ValidationError(f"配置必须是字典类型，获得: {type(config)}")
        
        if not config:
            raise ValidationError("配置字典不能为空")
        
        # 检查必需的键
        if required_keys:
            missing_keys = [key for key in required_keys if key not in config]
            if missing_keys:
                raise ValidationError(f"配置缺少必需的键: {missing_keys}")
        
        # 检查键值对
        for key, value in config.items():
            if not isinstance(key, str):
                raise ValidationError(f"配置键必须是字符串: {key}")
            
            if key.strip() != key:
                raise ValidationError(f"配置键不能包含前后空格: '{key}'")
            
            if not key:
                raise ValidationError("配置键不能为空")
            
            # 检查值的基本类型
            if value is None:
                logger.warning(f"配置键 '{key}' 的值为None")
            elif isinstance(value, str) and not value.strip():
                logger.warning(f"配置键 '{key}' 的值为空字符串")
        
        return config
    
    @classmethod
    def validate_coordinates(cls, lat: float, lon: float) -> Tuple[float, float]:
        """
        验证地理坐标
        
        Args:
            lat: 纬度
            lon: 经度
            
        Returns:
            Tuple[float, float]: 验证后的坐标
            
        Raises:
            ValidationError: 验证失败
        """
        # 类型检查
        try:
            lat = float(lat)
            lon = float(lon)
        except (ValueError, TypeError):
            raise ValidationError(f"坐标必须是数值类型: lat={lat}, lon={lon}")
        
        # 检查NaN和无穷大
        import math
        if math.isnan(lat) or math.isnan(lon):
            raise ValidationError("坐标不能为NaN")
        
        if math.isinf(lat) or math.isinf(lon):
            raise ValidationError("坐标不能为无穷大")
        
        # 检查范围
        if not (-90 <= lat <= 90):
            raise ValidationError(f"纬度超出有效范围[-90, 90]: {lat}")
        
        if not (-180 <= lon <= 180):
            raise ValidationError(f"经度超出有效范围[-180, 180]: {lon}")
        
        # 检查常见错误
        if lat == 0 and lon == 0:
            raise ValidationError("坐标为(0,0)，可能是无效数据")
        
        return lat, lon
    
    @classmethod
    def validate_directory_path(cls, dir_path: str, create_if_missing: bool = False) -> str:
        """
        验证目录路径
        
        Args:
            dir_path: 目录路径
            create_if_missing: 如果目录不存在是否创建
            
        Returns:
            str: 验证后的目录路径
            
        Raises:
            ValidationError: 验证失败
        """
        if not dir_path:
            raise ValidationError("目录路径不能为空")
        
        if not isinstance(dir_path, (str, Path)):
            raise ValidationError(f"目录路径必须是字符串或Path对象，获得: {type(dir_path)}")
        
        dir_path = str(dir_path).strip()
        
        if not dir_path:
            raise ValidationError("目录路径不能为空白字符")
        
        # 标准化路径
        dir_path = os.path.abspath(dir_path)
        
        # 检查父目录是否存在
        parent_dir = os.path.dirname(dir_path)
        if not os.path.exists(parent_dir):
            raise ValidationError(f"父目录不存在: {parent_dir}")
        
        # 检查目录是否存在
        if os.path.exists(dir_path):
            if not os.path.isdir(dir_path):
                raise ValidationError(f"路径存在但不是目录: {dir_path}")
            
            # 检查权限
            if not os.access(dir_path, os.W_OK):
                raise ValidationError(f"没有写入目录的权限: {dir_path}")
        
        elif create_if_missing:
            try:
                os.makedirs(dir_path, exist_ok=True)
                logger.info(f"创建目录: {dir_path}")
            except PermissionError:
                raise ValidationError(f"没有权限创建目录: {dir_path}")
            except OSError as e:
                raise ValidationError(f"创建目录失败: {dir_path}, 错误: {str(e)}")
        
        return dir_path
    
    @staticmethod
    def _is_suspicious_zip_path(path: str) -> bool:
        """检查ZIP文件中的路径是否可疑（路径遍历攻击等）"""
        # 检查路径遍历
        if '..' in path:
            return True
        
        # 检查绝对路径
        if path.startswith('/') or (len(path) > 1 and path[1] == ':'):
            return True
        
        # 检查可疑的系统路径
        suspicious_patterns = [
            'etc/', 'proc/', 'dev/', 'sys/', 'boot/',
            'windows/', 'system32/', 'program files/'
        ]
        
        path_lower = path.lower()
        for pattern in suspicious_patterns:
            if pattern in path_lower:
                return True
        
        return False