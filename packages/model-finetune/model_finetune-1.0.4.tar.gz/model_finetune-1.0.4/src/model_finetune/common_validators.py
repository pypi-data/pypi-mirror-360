#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
公共验证模块

包含所有模块共用的验证逻辑，避免代码重复。
"""

import logging
from typing import Any, Dict, Union
import pandas as pd


class CommonValidators:
    """公共验证器类，包含所有共用的验证方法"""
    
    @staticmethod
    def validate_model_data(model_result: Any, logger: logging.Logger) -> bool:
        """
        验证模型数据是否为有效的键值对格式
        
        Args:
            model_result: 要验证的模型数据
            logger: 日志记录器
            
        Returns:
            bool: 验证通过返回True，否则返回False
        """
        try:
            logger.info("开始验证模型数据格式")
            
            # 检查是否为None
            if model_result is None:
                logger.error("模型数据为None")
                return False
            
            # 如果是字典，检查是否为空
            if isinstance(model_result, dict):
                if not model_result:
                    logger.error("模型数据为空字典")
                    return False
                logger.info(f"模型数据是字典格式，包含 {len(model_result)} 个键值对")
                return True
            
            # 如果是列表，检查内容
            if isinstance(model_result, list):
                if not model_result:
                    logger.error("模型数据为空列表")
                    return False
                
                # 检查列表中的元素
                for i, item in enumerate(model_result):
                    if not isinstance(item, (dict, tuple, list)):
                        logger.error(f"列表第 {i} 个元素不是有效的键值对格式: {type(item)}")
                        return False
                
                logger.info(f"模型数据是列表格式，包含 {len(model_result)} 个元素")
                return True
            
            # 如果是DataFrame，检查是否为空
            if isinstance(model_result, pd.DataFrame):
                if model_result.empty:
                    logger.error("模型数据DataFrame为空")
                    return False
                logger.info(f"模型数据是DataFrame格式，形状: {model_result.shape}")
                return True
            
            # 如果是元组，检查长度
            if isinstance(model_result, tuple):
                if len(model_result) == 0:
                    logger.error("模型数据为空元组")
                    return False
                logger.info(f"模型数据是元组格式，长度: {len(model_result)}")
                return True
            
            # 检查是否有键值对访问能力（类似字典的对象）
            if hasattr(model_result, '__getitem__') and hasattr(model_result, 'keys'):
                try:
                    keys = list(model_result.keys())
                    if not keys:
                        logger.error("模型数据对象没有键")
                        return False
                    logger.info(f"模型数据是类字典对象，包含 {len(keys)} 个键")
                    return True
                except Exception as e:
                    logger.error(f"无法获取模型数据对象的键: {e}")
                    return False
            
            # 检查是否有类似列表的访问能力
            if hasattr(model_result, '__len__') and hasattr(model_result, '__getitem__'):
                try:
                    length = len(model_result)
                    if length == 0:
                        logger.error("模型数据序列为空")
                        return False
                    logger.info(f"模型数据是序列格式，长度: {length}")
                    return True
                except Exception as e:
                    logger.error(f"无法获取模型数据序列长度: {e}")
                    return False
            
            # 如果以上都不符合，检查是否是单个值（可能不适合保存为.bin文件）
            logger.warning(f"模型数据是单个值类型: {type(model_result)}，可能不适合保存为键值对格式")
            
            # 对于单个值，如果不是基础类型，可能还是有效的
            if not isinstance(model_result, (str, int, float, bool, bytes)):
                logger.info("模型数据是复杂对象，假设可以序列化")
                return True
            else:
                logger.error("模型数据是基础类型的单个值，不是键值对格式")
                return False
                
        except Exception as e:
            logger.error(f"验证模型数据时发生异常: {e}")
            return False
    
    @staticmethod
    def looks_like_url(text: str) -> bool:
        """
        检查文本是否看起来像URL
        
        Args:
            text: 要检查的文本
            
        Returns:
            bool: 如果看起来像URL返回True
        """
        if not text or not isinstance(text, str):
            return False
        
        # 检查是否以常见的URL协议开头
        url_schemes = ('http://', 'https://', 'ftp://', 'ftps://', 'file://')
        return text.lower().startswith(url_schemes)
    
    @staticmethod
    def is_file_path(input_data: str) -> bool:
        """
        判断输入是否为文件路径
        
        Args:
            input_data: 输入字符串
            
        Returns:
            bool: 如果是文件路径返回True
        """
        # 安全检查：过滤恶意路径
        if not input_data or len(input_data) > 1000:  # 防止过长路径
            return False
            
        # 检查是否包含JSON特征（排除Windows驱动器路径中的冒号）
        if any(char in input_data for char in ['{', '}', '[', ']']):
            return False
        # 只有当冒号前有引号时才认为是JSON的 "key": 模式
        if '":' in input_data:
            return False
        
        # 检查是否包含可疑的路径遍历
        suspicious_patterns = ['../', '..\\', '~/', '/etc/', '/proc/', '/sys/']
        if any(pattern in input_data.lower() for pattern in suspicious_patterns):
            return False
        
        # 检查是否像文件路径
        return (
            ('/' in input_data or '\\' in input_data or ':' in input_data) and
            not CommonValidators.looks_like_url(input_data) and
            len(input_data.split()) == 1 and
            not input_data.startswith('-')  # 防止命令行参数注入
        )


class CommonUtils:
    """公共工具函数类"""
    
    @staticmethod
    def get_timestamp() -> str:
        """
        获取当前时间戳
        
        Returns:
            str: 格式化的时间戳字符串
        """
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")