#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
核心数据处理器 - 从main.py重构出来的核心业务逻辑
"""

import os
import logging
import pandas as pd
from pathlib import Path
from typing import Optional, Tuple, Dict, Any, List
from dataclasses import dataclass

from .data_processor import DataProcessor
from .extractor import ZipExtractor
from .data_merger import DataMerger, ReflectanceDataProcessor
from .utils import (
    performance_monitor, 
    memory_monitor, 
    EnhancedLogger, 
    DataValidator,
    DataProcessingError,
    FileProcessingError
)
from .validators import InputValidator, ValidationError
from .exceptions import (
    ExceptionHandler, handle_exceptions, 
    FileProcessingException, DataProcessingException,
    convert_to_standard_exception
)

logger = logging.getLogger(__name__)


@dataclass
class ProcessingResult:
    """数据处理结果"""
    success: bool
    model_result: Any = None
    prediction_result: Any = None
    error_message: str = ""
    processed_data: Dict[str, Any] = None


@dataclass
class ExtractedFiles:
    """解压文件结果"""
    indices_file: Optional[str] = None
    pos_file: Optional[str] = None
    ref_files: List[str] = None
    extract_dir: Optional[str] = None


class CoreDataProcessor:
    """核心数据处理器 - 单一职责，专注于数据处理流程"""
    
    def __init__(self):
        self.validator = DataValidator()
        self.data_processor = DataProcessor()
        self.extractor = ZipExtractor()
        self.merger = DataMerger()
        
    @handle_exceptions("核心数据处理")
    @performance_monitor("核心数据处理")
    @memory_monitor("核心数据处理")
    def process_data(self, zip_path: str, measure_data_path: str) -> ProcessingResult:
        """
        处理数据文件 - 重构后的主要处理函数
        
        Args:
            zip_path: ZIP文件路径
            measure_data_path: 测量数据文件路径
            
        Returns:
            ProcessingResult: 处理结果
        """
        logger.info("开始核心数据处理流程")
        
        try:
            # 第1步：验证输入参数
            self._validate_inputs(zip_path, measure_data_path)
            
            # 第2步：处理ZIP文件
            extracted = self._process_zip_file(zip_path)
            
            # 第3步：处理反射率数据
            ref_data = self._process_reflectance_data(extracted.ref_files)
            
            # 第4步：合并位置和指标数据
            merged_data = self._merge_position_indices_data(
                extracted.indices_file, 
                extracted.pos_file
            )
            
            # 第5步：处理测量数据
            measure_data = self._process_measure_data(measure_data_path)
            
            # 第6步：数据匹配和模型训练
            model_result, prediction = self._match_and_train_model(
                merged_data, measure_data, ref_data
            )
            
            logger.info("核心数据处理流程完成")
            return ProcessingResult(
                success=True,
                model_result=model_result,
                prediction_result=prediction,
                processed_data={
                    'merged_data': merged_data,
                    'measure_data': measure_data,
                    'ref_data': ref_data
                }
            )
            
        except Exception as e:
            # 转换为标准化异常
            standard_exception = convert_to_standard_exception(e)
            error_msg = f"数据处理失败: {standard_exception.message}"
            
            # 使用统一的异常处理器
            handler = ExceptionHandler(logger)
            error_info = handler.handle_exception(standard_exception, "核心数据处理")
            
            return ProcessingResult(
                success=False,
                error_message=error_msg
            )
    
    def _validate_inputs(self, zip_path: str, measure_data_path: str) -> None:
        """验证输入参数 - 使用统一验证器"""
        try:
            # 使用统一的输入验证器
            validated_zip = InputValidator.validate_zip_file(zip_path)
            validated_csv = InputValidator.validate_csv_file(measure_data_path)
            
            # 获取文件大小信息
            zip_size = Path(validated_zip).stat().st_size
            csv_size = Path(validated_csv).stat().st_size
            
            logger.info(f"输入文件验证通过: ZIP({zip_size/1024/1024:.2f}MB), CSV({csv_size/1024:.2f}KB)")
            
        except ValidationError as e:
            raise FileProcessingException(
                f"输入验证失败: {str(e)}",
                operation="输入验证",
                cause=e
            ) from e
        except Exception as e:
            raise FileProcessingException(
                f"输入验证异常: {str(e)}",
                operation="输入验证", 
                cause=e
            ) from e
    
    @performance_monitor("ZIP文件处理")
    def _process_zip_file(self, zip_path: str) -> ExtractedFiles:
        """处理ZIP文件并提取关键文件"""
        logger.info(f"开始处理ZIP文件: {zip_path}")
        
        # 解压文件
        extract_dir = self.extractor.extract(zip_path)
        if not extract_dir:
            raise FileProcessingError("ZIP文件解压失败")
        
        # 查找关键文件
        extracted = self._find_key_files(extract_dir)
        extracted.extract_dir = extract_dir
        
        # 验证关键文件
        if not extracted.indices_file or not extracted.pos_file:
            raise FileProcessingError("未找到必需的INDEXS.CSV或POS.TXT文件")
        
        logger.info(f"找到关键文件: INDEXS.CSV={bool(extracted.indices_file)}, "
                   f"POS.TXT={bool(extracted.pos_file)}, "
                   f"反射率文件={len(extracted.ref_files or [])}")
        
        return extracted
    
    def _find_key_files(self, extract_dir: str) -> ExtractedFiles:
        """在解压目录中查找关键文件"""
        extracted = ExtractedFiles(ref_files=[])
        
        for root, _, files in os.walk(extract_dir):
            for filename in files:
                file_path = os.path.join(root, filename)
                filename_upper = filename.upper()
                
                if filename_upper == "INDEXS.CSV":
                    extracted.indices_file = file_path
                elif filename_upper == "POS.TXT":
                    extracted.pos_file = file_path
                elif "REFL" in filename_upper and filename_upper.endswith('.CSV'):
                    extracted.ref_files.append(file_path)
        
        # 对反射率文件排序
        if extracted.ref_files:
            try:
                extracted.ref_files.sort(
                    key=lambda x: int(os.path.basename(x).split("_")[-1].split(".")[0])
                )
            except (ValueError, IndexError):
                # 如果排序失败，保持原始顺序
                logger.warning("反射率文件排序失败，使用原始顺序")
        
        return extracted
    
    @performance_monitor("反射率数据处理")
    def _process_reflectance_data(self, ref_files: List[str]) -> Optional[pd.DataFrame]:
        """处理反射率数据"""
        if not ref_files:
            logger.warning("未找到反射率文件")
            return None
        
        logger.info(f"开始处理 {len(ref_files)} 个反射率文件")
        
        try:
            processor = ReflectanceDataProcessor()
            ref_data = processor.process_reflectance_files(ref_files)
            
            EnhancedLogger.log_data_summary(ref_data, "反射率数据")
            return ref_data
            
        except Exception as e:
            logger.error(f"反射率数据处理失败: {str(e)}")
            raise DataProcessingError(f"反射率数据处理失败: {str(e)}") from e
    
    @performance_monitor("位置指标数据合并")
    def _merge_position_indices_data(self, indices_file: str, pos_file: str) -> pd.DataFrame:
        """合并位置数据和指标数据"""
        logger.info("开始合并位置数据和指标数据")
        
        try:
            merged_data = self.merger.merge_position_and_indices(indices_file, pos_file)
            
            if merged_data.empty:
                raise DataProcessingError("位置和指标数据合并结果为空")
            
            EnhancedLogger.log_data_summary(merged_data, "合并后的位置指标数据")
            return merged_data
            
        except Exception as e:
            logger.error(f"位置指标数据合并失败: {str(e)}")
            raise DataProcessingError(f"位置指标数据合并失败: {str(e)}") from e
    
    @performance_monitor("测量数据处理")
    def _process_measure_data(self, measure_data_path: str) -> pd.DataFrame:
        """处理测量数据"""
        logger.info(f"开始处理测量数据: {measure_data_path}")
        
        try:
            # 读取测量数据
            measure_data = self._load_measure_data(measure_data_path)
            
            if measure_data is None or measure_data.empty:
                raise DataProcessingError("测量数据加载失败或为空")
            
            EnhancedLogger.log_data_summary(measure_data, "测量数据")
            logger.info("测量数据处理完成")
            return measure_data
            
        except Exception as e:
            logger.error(f"测量数据处理失败: {str(e)}")
            raise DataProcessingError(f"测量数据处理失败: {str(e)}") from e
    
    def _load_measure_data(self, measure_data_path: str) -> pd.DataFrame:
        """加载测量数据文件"""
        from .utils import EncodingDetector
        
        try:
            # 使用统一的编码检测器读取CSV
            detector = EncodingDetector()
            measure_data = detector.read_csv_file(
                measure_data_path, 
                header=0, 
                index_col=0
            )
            
            if measure_data is None or measure_data.empty:
                raise DataProcessingError(f"测量数据文件为空: {measure_data_path}")
            
            EnhancedLogger.log_data_summary(measure_data, "测量数据")
            return measure_data
            
        except Exception as e:
            raise DataProcessingError(f"加载测量数据失败: {str(e)}") from e
    
    @performance_monitor("数据匹配和模型训练")
    def _match_and_train_model(self, merged_data: Dict[str, Any], 
                              measure_data: Dict[str, Any], 
                              ref_data: Optional[pd.DataFrame]) -> Tuple[Any, Any]:
        """数据匹配和模型训练"""
        logger.info("开始数据匹配和模型训练")
        
        if ref_data is None:
            raise DataProcessingError("反射率数据缺失，无法进行模型训练")
        
        try:
            # 数据匹配分析
            matched_ref_df, matched_merged_df, matched_measure_df = (
                self.data_processor.match_and_analyze_data(
                    measure_data,
                    merged_data, 
                    ref_data
                )
            )
            
            # 验证匹配结果
            if len(matched_ref_df) == len(matched_merged_df) == len(matched_measure_df):
                sample_count = len(matched_ref_df)
                logger.info(f"数据匹配完成，样本量: {sample_count}")
                
                if sample_count < 5:
                    logger.warning(f"样本量过少({sample_count})，可能影响模型质量")
            else:
                raise DataProcessingError(
                    f"数据匹配不一致: 反射率({len(matched_ref_df)}), "
                    f"位置指标({len(matched_merged_df)}), 测量({len(matched_measure_df)})"
                )
            
            # 调用模型训练
            from autowaterqualitymodeler.run import main as train_model
            
            model_result = train_model(matched_ref_df, matched_merged_df, matched_measure_df)
            
            if isinstance(model_result, tuple) and len(model_result) == 2:
                return model_result[0], model_result[1]
            else:
                return model_result, None
                
        except Exception as e:
            logger.error(f"数据匹配和模型训练失败: {str(e)}")
            raise DataProcessingError(f"数据匹配和模型训练失败: {str(e)}") from e


class LegacyProcessor:
    """传统处理器 - 保持向后兼容性"""
    
    def __init__(self):
        self.core_processor = CoreDataProcessor()
    
    def process_data(self, zip_path: str, measure_data_path: str):
        """
        传统的process_data函数 - 保持API兼容性
        
        Returns:
            处理结果，格式与原函数兼容
        """
        result = self.core_processor.process_data(zip_path, measure_data_path)
        
        if result.success:
            if result.prediction_result is not None:
                return result.model_result, result.prediction_result
            else:
                return result.model_result
        else:
            # 保持原有的返回格式
            return [None, None]