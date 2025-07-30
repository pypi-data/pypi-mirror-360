#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据合并模块
提供航测数据合并功能，从main.py中提取出来提高代码可维护性
"""

import pandas as pd
import numpy as np
import logging
from typing import Optional, Tuple
from pathlib import Path

from .utils import (EncodingDetector, DataValidator, FileProcessingError, 
                   performance_monitor, EnhancedLogger)

logger = logging.getLogger(__name__)


class DataMerger:
    """数据合并器，负责合并位置数据和指标数据"""
    
    def __init__(self):
        self.encoding_detector = EncodingDetector()
        self.validator = DataValidator()
    
    def merge_position_and_indices(self, indices_file: str, pos_file: str) -> pd.DataFrame:
        """
        合并位置文件和指标文件
        
        Args:
            indices_file: 指标文件路径 (INDEXS.CSV)
            pos_file: 位置文件路径 (POS.TXT)
            
        Returns:
            合并后的DataFrame
            
        Raises:
            FileProcessingError: 文件处理失败
        """
        try:
            EnhancedLogger.log_operation_context("数据合并", 
                                               indices_file=Path(indices_file).name,
                                               pos_file=Path(pos_file).name)
            logger.info("开始合并位置数据和指标数据")
            
            # 读取指标数据
            indices_data = self._read_indices_file(indices_file)
            if indices_data is None or indices_data.empty:
                raise FileProcessingError(f"无法读取指标文件: {indices_file}")
            
            # 读取位置数据
            pos_data = self._read_position_file(pos_file)
            if pos_data is None or pos_data.empty:
                raise FileProcessingError(f"无法读取位置文件: {pos_file}")
            
            # 验证数据完整性
            self._validate_data_compatibility(indices_data, pos_data)
            
            # 执行合并
            merged_data = self._perform_merge(indices_data, pos_data)
            
            logger.info(f"数据合并完成，共 {len(merged_data)} 行，{len(merged_data.columns)} 列")
            return merged_data
            
        except Exception as e:
            logger.error(f"数据合并失败: {str(e)}")
            raise FileProcessingError(f"数据合并失败: {str(e)}") from e
    
    def _read_indices_file(self, indices_file: str) -> Optional[pd.DataFrame]:
        """读取指标数据文件"""
        try:
            logger.debug(f"读取指标文件: {indices_file}")
            
            # 使用统一的编码检测读取
            indices_data = self.encoding_detector.read_csv_file(
                indices_file, 
                header=0, 
                index_col=0
            )
            
            if indices_data is None:
                return None
            
            logger.info(f"指标数据包含 {len(indices_data)} 行和 {len(indices_data.columns)} 列")
            logger.debug(f"指标数据列名: {list(indices_data.columns)}")
            
            return indices_data
            
        except Exception as e:
            logger.error(f"读取指标文件失败: {str(e)}")
            return None
    
    def _read_position_file(self, pos_file: str) -> Optional[pd.DataFrame]:
        """读取位置数据文件"""
        try:
            logger.debug(f"读取位置文件: {pos_file}")
            
            # 读取位置文件内容
            content = self.encoding_detector.read_text_file(pos_file)
            if content is None:
                return None
            
            # 解析位置数据
            pos_data = self._parse_position_content(content)
            
            if pos_data is None or pos_data.empty:
                logger.error("位置数据解析失败或为空")
                return None
            
            logger.info(f"位置数据包含 {len(pos_data)} 行")
            return pos_data
            
        except Exception as e:
            logger.error(f"读取位置文件失败: {str(e)}")
            return None
    
    def _parse_position_content(self, content: str) -> Optional[pd.DataFrame]:
        """解析位置文件内容"""
        try:
            lines = content.strip().split('\n')
            if not lines:
                return None
            
            position_data = []
            for i, line in enumerate(lines):
                line = line.strip()
                if not line:
                    continue
                
                try:
                    # 解析格式: /path/to/REFL_X.csv latitude: Y longitude: Z height: H
                    # 使用正则表达式提取REFL文件编号和坐标信息
                    import re
                    
                    # 匹配REFL_数字.csv文件名和坐标信息
                    match = re.search(r'REFL_(\d+)\.csv\s+latitude:\s*([\d.-]+)\s+longitude:\s*([\d.-]+)', line)
                    
                    if match:
                        index = match.group(1)  # REFL文件编号
                        lat = float(match.group(2))  # 纬度
                        lon = float(match.group(3))  # 经度
                        
                        # 验证坐标
                        is_valid, error_msg = self.validator.validate_coordinates(lat, lon)
                        if not is_valid:
                            logger.warning(f"第{i+1}行坐标无效: {error_msg}")
                            continue
                        
                        position_data.append({
                            'index': index,
                            'longitude': lon,
                            'latitude': lat
                        })
                    else:
                        logger.warning(f"第{i+1}行格式不匹配POS.txt标准格式: {line[:100]}...")
                        
                except ValueError as e:
                    logger.warning(f"第{i+1}行解析失败: {str(e)}")
                    continue
            
            if not position_data:
                logger.error("没有解析到有效的位置数据")
                return None
            
            pos_df = pd.DataFrame(position_data)
            pos_df.set_index('index', inplace=True)
            
            return pos_df
            
        except Exception as e:
            logger.error(f"解析位置文件内容失败: {str(e)}")
            return None
    
    def _validate_data_compatibility(self, indices_data: pd.DataFrame, 
                                   pos_data: pd.DataFrame) -> None:
        """验证数据兼容性"""
        try:
            # 调试信息：打印索引详情
            logger.debug(f"指标数据索引: {list(indices_data.index)} (类型: {type(indices_data.index[0]) if len(indices_data.index) > 0 else 'None'})")
            logger.debug(f"位置数据索引: {list(pos_data.index)} (类型: {type(pos_data.index[0]) if len(pos_data.index) > 0 else 'None'})")
            
            # 统一索引类型为字符串
            indices_data.index = indices_data.index.astype(str)
            pos_data.index = pos_data.index.astype(str)
            
            # 检查索引交集
            common_indices = set(indices_data.index) & set(pos_data.index)
            
            if not common_indices:
                raise FileProcessingError("指标数据和位置数据没有共同的索引")
            
            indices_count = len(indices_data)
            pos_count = len(pos_data)
            common_count = len(common_indices)
            
            logger.info(f"数据匹配情况 - 指标数据: {indices_count}行, "
                       f"位置数据: {pos_count}行, 共同索引: {common_count}个")
            
            if common_count < min(indices_count, pos_count) * 0.5:
                logger.warning("超过50%的数据无法匹配，请检查数据质量")
            
        except Exception as e:
            raise FileProcessingError(f"数据兼容性验证失败: {str(e)}") from e
    
    def _perform_merge(self, indices_data: pd.DataFrame, 
                      pos_data: pd.DataFrame) -> pd.DataFrame:
        """执行数据合并"""
        try:
            # 使用内连接合并数据，只保留有完整信息的行
            merged_data = indices_data.join(pos_data, how='inner')
            
            if merged_data.empty:
                raise FileProcessingError("合并后的数据为空")
            
            # 重新排列列，将经纬度放在前面
            cols = list(merged_data.columns)
            if 'latitude' in cols and 'longitude' in cols:
                cols.remove('latitude')
                cols.remove('longitude')
                new_cols = ['latitude', 'longitude'] + cols
                merged_data = merged_data[new_cols]
            
            return merged_data
            
        except Exception as e:
            raise FileProcessingError(f"数据合并执行失败: {str(e)}") from e


class ReflectanceDataProcessor:
    """反射率数据处理器"""
    
    def __init__(self):
        self.encoding_detector = EncodingDetector()
    
    def process_reflectance_files(self, ref_files: list) -> pd.DataFrame:
        """
        处理反射率数据文件
        
        Args:
            ref_files: 反射率文件路径列表
            
        Returns:
            合并后的反射率数据DataFrame
        """
        try:
            if not ref_files:
                logger.warning("没有找到反射率文件")
                return pd.DataFrame()
            
            # 按文件名中的数字排序
            sorted_files = self._sort_reflectance_files(ref_files)
            
            logger.info(f"开始处理 {len(sorted_files)} 个反射率文件")
            
            # 批量处理文件
            ref_data_list = []
            failed_files = []
            
            for ref_file in sorted_files:
                try:
                    single_data = self._process_single_reflectance_file(ref_file)
                    if single_data is not None:
                        ref_data_list.append(single_data)
                    else:
                        failed_files.append(ref_file)
                except Exception as e:
                    logger.warning(f"处理反射率文件 {ref_file} 失败: {str(e)}")
                    failed_files.append(ref_file)
            
            if failed_files:
                logger.warning(f"有 {len(failed_files)} 个反射率文件处理失败")
            
            if not ref_data_list:
                logger.error("没有成功处理任何反射率文件")
                return pd.DataFrame()
            
            # 合并所有数据
            ref_data = pd.concat(ref_data_list, axis=0)
            
            # 清理临时数据
            del ref_data_list
            
            logger.info(f"反射率数据处理完成，包含 {len(ref_data)} 行和 {len(ref_data.columns)} 列")
            
            return ref_data
            
        except Exception as e:
            logger.error(f"反射率数据处理失败: {str(e)}")
            raise FileProcessingError(f"反射率数据处理失败: {str(e)}") from e
    
    def _sort_reflectance_files(self, ref_files: list) -> list:
        """按文件名中的数字排序反射率文件"""
        try:
            def extract_number(filename):
                try:
                    # 从文件名中提取数字
                    import os
                    basename = os.path.basename(filename)
                    number_str = basename.split("_")[-1].split(".")[0]
                    return int(number_str)
                except Exception:
                    return 0
            
            return sorted(ref_files, key=extract_number)
            
        except Exception as e:
            logger.warning(f"反射率文件排序失败: {str(e)}")
            return ref_files
    
    def _process_single_reflectance_file(self, ref_file: str) -> Optional[pd.DataFrame]:
        """处理单个反射率文件"""
        try:
            # 使用统一的编码检测读取CSV
            single_ref_data = self.encoding_detector.read_csv_file(
                ref_file, 
                header=0, 
                index_col=0
            )
            
            if single_ref_data is None:
                return None
            
            # 转置数据（通常反射率文件需要转置）
            single_ref_data = single_ref_data.T
            
            # 设置索引为文件编号
            import os
            file_index = os.path.basename(ref_file).split("_")[-1].split(".")[0]
            single_ref_data.index = [file_index]
            
            return single_ref_data
            
        except Exception as e:
            logger.debug(f"处理反射率文件 {ref_file} 失败: {str(e)}")
            return None