#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
异常处理模块 - 统一的异常定义和处理机制
"""

import logging
import traceback
from typing import Dict, Any, Optional, List
from enum import Enum


class ErrorCode(Enum):
    """错误代码枚举"""
    # 通用错误 (1000-1999)
    UNKNOWN_ERROR = 1000
    INVALID_INPUT = 1001
    CONFIGURATION_ERROR = 1002
    SYSTEM_ERROR = 1003
    
    # 文件操作错误 (2000-2999)
    FILE_NOT_FOUND = 2001
    FILE_ACCESS_DENIED = 2002
    FILE_CORRUPTED = 2003
    FILE_FORMAT_ERROR = 2004
    FILE_SIZE_ERROR = 2005
    
    # 数据处理错误 (3000-3999)
    DATA_VALIDATION_ERROR = 3001
    DATA_PROCESSING_ERROR = 3002
    DATA_MERGE_ERROR = 3003
    DATA_ENCODING_ERROR = 3004
    DATA_EMPTY_ERROR = 3005
    
    # 网络错误 (4000-4999)
    NETWORK_ERROR = 4001
    DOWNLOAD_ERROR = 4002
    URL_ERROR = 4003
    TIMEOUT_ERROR = 4004
    
    # 模型错误 (5000-5999)
    MODEL_TRAINING_ERROR = 5001
    MODEL_PREDICTION_ERROR = 5002
    MODEL_SAVE_ERROR = 5003
    MODEL_LOAD_ERROR = 5004
    
    # 加密错误 (6000-6999)
    ENCRYPTION_ERROR = 6001
    DECRYPTION_ERROR = 6002
    KEY_ERROR = 6003


class ModelFinetuneException(Exception):
    """Model Finetune 基础异常类"""
    
    def __init__(self, 
                 message: str, 
                 error_code: ErrorCode = ErrorCode.UNKNOWN_ERROR,
                 details: Optional[Dict[str, Any]] = None,
                 cause: Optional[Exception] = None):
        """
        初始化异常
        
        Args:
            message: 错误消息
            error_code: 错误代码
            details: 错误详细信息
            cause: 原始异常
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.cause = cause
        
        # 记录异常堆栈
        self.traceback_str = traceback.format_exc()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "error": True,
            "error_code": self.error_code.value,
            "error_name": self.error_code.name,
            "message": self.message,
            "details": self.details,
            "cause": str(self.cause) if self.cause else None
        }
    
    def __str__(self) -> str:
        return f"[{self.error_code.name}] {self.message}"


class ValidationException(ModelFinetuneException):
    """输入验证异常"""
    
    def __init__(self, message: str, field: str = None, value: Any = None, **kwargs):
        details = kwargs.get('details', {})
        if field:
            details['field'] = field
        if value is not None:
            details['value'] = str(value)
        
        super().__init__(
            message, 
            ErrorCode.INVALID_INPUT, 
            details=details,
            cause=kwargs.get('cause')
        )


class FileProcessingException(ModelFinetuneException):
    """文件处理异常"""
    
    def __init__(self, message: str, file_path: str = None, operation: str = None, **kwargs):
        details = kwargs.get('details', {})
        if file_path:
            details['file_path'] = file_path
        if operation:
            details['operation'] = operation
        
        # 根据具体情况选择错误代码
        error_code = kwargs.get('error_code', ErrorCode.FILE_NOT_FOUND)
        
        super().__init__(
            message,
            error_code,
            details=details,
            cause=kwargs.get('cause')
        )


class DataProcessingException(ModelFinetuneException):
    """数据处理异常"""
    
    def __init__(self, message: str, stage: str = None, data_type: str = None, **kwargs):
        details = kwargs.get('details', {})
        if stage:
            details['stage'] = stage
        if data_type:
            details['data_type'] = data_type
        
        super().__init__(
            message,
            ErrorCode.DATA_PROCESSING_ERROR,
            details=details,
            cause=kwargs.get('cause')
        )


class NetworkException(ModelFinetuneException):
    """网络异常"""
    
    def __init__(self, message: str, url: str = None, status_code: int = None, **kwargs):
        details = kwargs.get('details', {})
        if url:
            details['url'] = url
        if status_code:
            details['status_code'] = status_code
        
        super().__init__(
            message,
            ErrorCode.NETWORK_ERROR,
            details=details,
            cause=kwargs.get('cause')
        )


class ModelException(ModelFinetuneException):
    """模型异常"""
    
    def __init__(self, message: str, model_type: str = None, operation: str = None, **kwargs):
        details = kwargs.get('details', {})
        if model_type:
            details['model_type'] = model_type
        if operation:
            details['operation'] = operation
        
        super().__init__(
            message,
            ErrorCode.MODEL_TRAINING_ERROR,
            details=details,
            cause=kwargs.get('cause')
        )


class EncryptionException(ModelFinetuneException):
    """加密异常"""
    
    def __init__(self, message: str, operation: str = None, **kwargs):
        details = kwargs.get('details', {})
        if operation:
            details['operation'] = operation
        
        super().__init__(
            message,
            ErrorCode.ENCRYPTION_ERROR,
            details=details,
            cause=kwargs.get('cause')
        )


class ExceptionHandler:
    """统一异常处理器"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
    
    def handle_exception(self, exception: Exception, context: str = None) -> Dict[str, Any]:
        """
        处理异常并返回标准化的错误信息
        
        Args:
            exception: 异常对象
            context: 异常上下文信息
            
        Returns:
            Dict[str, Any]: 标准化的错误信息
        """
        if isinstance(exception, ModelFinetuneException):
            # 已知的项目异常
            error_info = exception.to_dict()
            self.logger.error(f"[{context}] {exception}", exc_info=False)
        else:
            # 未知异常，转换为标准格式
            error_info = {
                "error": True,
                "error_code": ErrorCode.UNKNOWN_ERROR.value,
                "error_name": ErrorCode.UNKNOWN_ERROR.name,
                "message": str(exception),
                "details": {
                    "exception_type": type(exception).__name__,
                    "context": context
                }
            }
            self.logger.error(f"[{context}] 未处理的异常: {exception}", exc_info=True)
        
        return error_info
    
    def create_error_result(self, exception: Exception, context: str = None) -> Dict[str, Any]:
        """
        创建错误结果
        
        Args:
            exception: 异常对象
            context: 异常上下文
            
        Returns:
            Dict[str, Any]: 包含错误信息的结果字典
        """
        error_info = self.handle_exception(exception, context)
        
        return {
            "success": False,
            "timestamp": self._get_timestamp(),
            **error_info
        }
    
    @staticmethod
    def _get_timestamp() -> str:
        """获取当前时间戳"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def handle_exceptions(context: str = None, logger: logging.Logger = None):
    """
    异常处理装饰器
    
    Args:
        context: 异常上下文描述
        logger: 日志记录器
    
    Returns:
        装饰器函数
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            handler = ExceptionHandler(logger)
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # 记录异常并重新抛出，让调用者决定如何处理
                handler.handle_exception(e, context or func.__name__)
                raise
        return wrapper
    return decorator


def convert_to_standard_exception(exception: Exception, 
                                  default_error_code: ErrorCode = ErrorCode.UNKNOWN_ERROR) -> ModelFinetuneException:
    """
    将标准异常转换为项目标准异常
    
    Args:
        exception: 原始异常
        default_error_code: 默认错误代码
        
    Returns:
        ModelFinetuneException: 标准化异常
    """
    if isinstance(exception, ModelFinetuneException):
        return exception
    
    # 根据异常类型映射到相应的项目异常
    exception_mappings = {
        FileNotFoundError: (FileProcessingException, ErrorCode.FILE_NOT_FOUND),
        PermissionError: (FileProcessingException, ErrorCode.FILE_ACCESS_DENIED),
        ValueError: (ValidationException, ErrorCode.INVALID_INPUT),
        TypeError: (ValidationException, ErrorCode.INVALID_INPUT),
        ConnectionError: (NetworkException, ErrorCode.NETWORK_ERROR),
        TimeoutError: (NetworkException, ErrorCode.TIMEOUT_ERROR),
        UnicodeDecodeError: (FileProcessingException, ErrorCode.DATA_ENCODING_ERROR),
        KeyError: (ValidationException, ErrorCode.INVALID_INPUT),
    }
    
    exception_type = type(exception)
    if exception_type in exception_mappings:
        target_exception_class, error_code = exception_mappings[exception_type]
        if target_exception_class == FileProcessingException:
            return FileProcessingException(
                str(exception),
                error_code=error_code,
                cause=exception
            )
        elif target_exception_class == ValidationException:
            return ValidationException(
                str(exception),
                cause=exception
            )
        elif target_exception_class == NetworkException:
            return NetworkException(
                str(exception),
                cause=exception
            )
    
    # 默认转换
    return ModelFinetuneException(
        str(exception),
        error_code=default_error_code,
        cause=exception
    )