"""
数据处理模块
提供数据处理和分析功能
"""
import os
import logging
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from .utils import ConfigManager, DataValidator, DataProcessingError, GeographicMatchingError

from .geo_utils import haversine

logger = logging.getLogger(__name__)

class DataProcessor:
    """
    数据处理器类
    用于处理和分析航测数据
    """
    
    def __init__(self, config=None):
        """
        初始化数据处理器
        
        Args:
            config: 配置字典，包含数据处理的相关配置（已弃用，使用ConfigManager）
        """
        self.config_manager = ConfigManager()
        self.validator = DataValidator()
        self.indicator_mapping = self.config_manager.get_indicator_mapping()
        self.cleaning_config = self.config_manager.get_cleaning_config()
        self.config = config or {}
        
    def _clean_data(self, data: pd.DataFrame, indicator_columns: list) -> pd.DataFrame:
        """
        数据清洗函数，处理异常值和缺失值
        
        Args:
            data: 输入数据
            indicator_columns: 指标列名列表
            
        Returns:
            清洗后的数据
        """
        try:
            logger.info("开始数据清洗")
            cleaned_data = data.copy()
            
            # 1. 处理经纬度异常值 - 明显错误直接报错
            if 'latitude' in cleaned_data.columns:
                # 纬度范围检查 (-90, 90)
                invalid_lat = (cleaned_data['latitude'] < -90) | (cleaned_data['latitude'] > 90)
                if invalid_lat.any():
                    invalid_count = invalid_lat.sum()
                    invalid_values = cleaned_data.loc[invalid_lat, 'latitude'].tolist()[:5]  # 显示前5个
                    error_msg = f"发现 {invalid_count} 个明显错误的纬度值 (超出-90°到90°范围): {invalid_values}..."
                    logger.error(error_msg)
                    raise ValueError(error_msg)
                
            if 'longitude' in cleaned_data.columns:
                # 经度范围检查 (-180, 180)
                invalid_lon = (cleaned_data['longitude'] < -180) | (cleaned_data['longitude'] > 180)
                if invalid_lon.any():
                    invalid_count = invalid_lon.sum()
                    invalid_values = cleaned_data.loc[invalid_lon, 'longitude'].tolist()[:5]  # 显示前5个
                    error_msg = f"发现 {invalid_count} 个明显错误的经度值 (超出-180°到180°范围): {invalid_values}..."
                    logger.error(error_msg)
                    raise ValueError(error_msg)
            
            # 2. 处理指标列异常值 - 只设置为空值，不删除行
            for col in indicator_columns:
                if col not in cleaned_data.columns:
                    continue
                    
                try:
                    # 转换为数值类型
                    cleaned_data[col] = pd.to_numeric(cleaned_data[col], errors='coerce')
                    
                    # 处理无穷大值 - 警告并设为空值
                    inf_mask = np.isinf(cleaned_data[col])
                    if inf_mask.any():
                        inf_count = inf_mask.sum()
                        inf_values = cleaned_data.loc[inf_mask, col].tolist()[:3]  # 显示前3个
                        logger.warning(f"指标 '{col}' 包含 {inf_count} 个无穷大值: {inf_values}...，将设为空值")
                        cleaned_data.loc[inf_mask, col] = np.nan
                    
                    # 处理负数值 - 警告并设为空值
                    negative_mask = (cleaned_data[col] < 0) & cleaned_data[col].notna()
                    if negative_mask.any():
                        negative_count = negative_mask.sum()
                        negative_values = cleaned_data.loc[negative_mask, col].tolist()[:3]  # 显示前3个
                        logger.warning(f"指标 '{col}' 包含 {negative_count} 个负数值: {negative_values}...，将设为空值")
                        cleaned_data.loc[negative_mask, col] = np.nan
                    
                    # 统计空值数量
                    null_mask = cleaned_data[col].isna()
                    if null_mask.any():
                        null_count = null_mask.sum()
                        logger.info(f"指标 '{col}' 包含 {null_count} 个空值")
                    
                    # 使用IQR方法检测异常值 - 只记录详细信息，不修改
                    valid_data = cleaned_data[col].dropna()
                    valid_data = valid_data[valid_data >= 0]  # 排除负数（已设为空值）
                    valid_data = valid_data[np.isfinite(valid_data)]  # 排除无穷大（已设为空值）
                    
                    min_samples = self.cleaning_config['min_valid_samples']
                    if len(valid_data) > min_samples:
                        Q1 = valid_data.quantile(0.25)
                        Q3 = valid_data.quantile(0.75)
                        IQR = Q3 - Q1
                        
                        if IQR > 0:  # 避免除零错误
                            iqr_multiplier = self.cleaning_config['iqr_multiplier']
                            lower_bound = Q1 - iqr_multiplier * IQR
                            upper_bound = Q3 + iqr_multiplier * IQR
                            
                            # 在有效数据中找出异常值
                            outliers_mask = ((valid_data < lower_bound) | (valid_data > upper_bound))
                            
                            if outliers_mask.any():
                                outlier_count = outliers_mask.sum()
                                outlier_ratio = outlier_count / len(valid_data)
                                outlier_values = valid_data[outliers_mask].tolist()
                                
                                # 详细记录异常值信息
                                logger.info(f"指标 '{col}' 异常值详细分析:")
                                logger.info(f"  - 异常值数量: {outlier_count} (占比 {outlier_ratio:.1%})")
                                logger.info(f"  - 正常范围: [{lower_bound:.4f}, {upper_bound:.4f}]")
                                logger.info(f"  - Q1: {Q1:.4f}, Q3: {Q3:.4f}, IQR: {IQR:.4f}")
                                
                                # 显示具体异常值（最多显示10个）
                                if len(outlier_values) <= 10:
                                    logger.info(f"  - 异常值: {outlier_values}")
                                else:
                                    logger.info(f"  - 异常值示例: {outlier_values[:10]}... (还有{len(outlier_values)-10}个)")
                        
                except Exception as e:
                    logger.warning(f"处理指标 '{col}' 时出错: {str(e)}")
                    continue
            
            # 3. 最终数据质量验证
            # 检查经纬度完整性 - 经纬度必须完整
            if 'latitude' in cleaned_data.columns and 'longitude' in cleaned_data.columns:
                geo_missing = cleaned_data['latitude'].isna() | cleaned_data['longitude'].isna()
                if geo_missing.any():
                    missing_count = geo_missing.sum()
                    logger.error(f"数据清洗后仍有 {missing_count} 行缺少经纬度信息")
                    # 移除缺少经纬度的行
                    cleaned_data = cleaned_data[~geo_missing]
                    logger.info(f"移除了 {missing_count} 行缺少经纬度的数据")
            
            # 统计指标数据质量情况
            value_cols = [col for col in indicator_columns if col in cleaned_data.columns]
            if value_cols:
                logger.info("指标数据质量统计:")
                for col in value_cols:
                    total_count = len(cleaned_data)
                    null_count = cleaned_data[col].isna().sum()
                    valid_count = total_count - null_count
                    valid_ratio = valid_count / total_count if total_count > 0 else 0
                    logger.info(f"  - {col}: 有效数据 {valid_count}/{total_count} ({valid_ratio:.1%})")
            
            logger.info(f"数据清洗完成，剩余 {len(cleaned_data)} 行数据")
            return cleaned_data
            
        except Exception as e:
            logger.error(f"数据清洗失败: {str(e)}", exc_info=True)
            return data  # 返回原始数据

    def process_data(self, merged_data):
        """
        处理合并后的数据，计算统计信息
        
        Args:
            merged_data: 合并后的数据DataFrame
            
        Returns:
            处理后的统计信息字典
        """
        try:
            # 验证输入数据
            if merged_data is None:
                logger.error("输入数据为空")
                return None
                
            if not isinstance(merged_data, pd.DataFrame):
                logger.error(f"输入数据类型错误，期望DataFrame，实际: {type(merged_data)}")
                return None
                
            if merged_data.empty:
                logger.error("输入数据为空")
                return None
            
            logger.info(f"开始处理数据，包含 {len(merged_data)} 行和 {len(merged_data.columns)} 列")
            
            # 初始化结果字典
            result = dict()
            
            # 备份原始数据
            original_data = merged_data.copy()
            
            # 定义非指标列名的关键词列表
            non_indicator_keywords = [
                'index', 'latitude', 'longitude', 'lat', 'lon', 'lng',
                '采样点', '精度', '维度', '经度', '纬度', '点位', '编号', 'id', 'ID', 'number'
            ]
            
            # 标准化列名，将经纬度相关列统一为标准格式
            column_mapping = {}
            for col in merged_data.columns:
                col_lower = col.lower()
                if any(keyword in col_lower for keyword in ['latitude', 'lat', '纬度', '维度']):
                    column_mapping[col] = 'latitude'
                elif any(keyword in col_lower for keyword in ['longitude', 'lon', 'lng', '经度', '精度']):
                    column_mapping[col] = 'longitude'
                elif any(keyword == col_lower for keyword in ['index', 'id', '编号', '采样点', '点位', 'ID', 'number']):
                    column_mapping[col] = 'index'
            
            # 重命名列
            if column_mapping:
                merged_data = merged_data.rename(columns=column_mapping)
                logger.info(f"列名标准化映射: {column_mapping}")
            
            # 确保必要的列存在
            required_columns = ['latitude', 'longitude']
            for col in required_columns:
                if col not in merged_data.columns:
                    logger.warning(f"缺少必要的列: {col}")
            
            # 获取指标列
            indicator_columns = [col for col in merged_data.columns if col not in ['index', 'latitude', 'longitude']]
            
            if not indicator_columns:
                logger.error("没有找到任何指标列")
                return None
                
            logger.info(f"找到 {len(indicator_columns)} 个指标: {', '.join(indicator_columns)}")
            
            # 数据清洗
            logger.info("开始数据清洗")
            merged_data = self._clean_data(merged_data, indicator_columns)
            
            if merged_data.empty:
                logger.error("数据清洗后为空")
                return None
            
            # 标准化指标名称
            logger.info("开始标准化指标名称")
            
            # 水质参数标准名称映射表
            indicator_name_mapping = {
                # 浊度相关
                'turbidity': 'turbidity',
                '浊度': 'turbidity',
                'turb': 'turbidity',
                # 悬浮物相关
                'ss': 'ss',
                '悬浮物': 'ss',
                'suspended solids': 'ss',
                # 溶解氧相关
                'do': 'do',
                '溶解氧': 'do',
                'dissolved oxygen': 'do',
                # 化学需氧量相关
                'cod': 'codcr',
                '化学需氧量': 'codcr',
                'chemical oxygen demand': 'codcr',
                # 生化需氧量相关
                'bod': 'bod',
                'bod5': 'bod',
                '生化需氧量': 'bod',
                'biochemical oxygen demand': 'bod',
                # 氨氮相关
                'nh3-n': 'nh3n',
                'nh3n': 'nh3n',
                '氨氮': 'nh3n',
                'nh3_n': 'nh3n',
                'ammonia nitrogen': 'nh3n',
                # 总氮相关
                'tn': 'tn',
                '总氮': 'tn',
                'total nitrogen': 'tn',
                # 总磷相关
                'tp': 'tp',
                '总磷': 'tp',
                'total phosphorus': 'tp',
                # pH值相关
                'ph': 'ph',
                'ph值': 'ph',
                # 电导率相关
                'ec': 'ec',
                '电导率': 'ec',
                'conductivity': 'ec',
                # 温度相关
                'temp': 'temperature',
                '温度': 'temperature',
                'temperature': 'temperature',
                'bga': 'bga',
                '蓝绿藻': 'bga',
                'chla': 'chla',
                '叶绿素': 'chla',
                '叶绿素a': 'chla',
                'chlorophyll': 'chla',
                'chl': 'chla',
                'chl_a': 'chla',
                '高锰酸盐指数': 'codmn',
                '高锰酸盐': 'codmn',
                'codmn': 'codmn',
                'cm': 'codmn',
                'CM': 'codmn'
            }
            
            # 创建新的标准化指标列表和重命名映射
            standardized_columns = []
            rename_mapping = {}
            
            for col in indicator_columns:
                col_lower = col.lower()
                if col_lower in indicator_name_mapping:
                    standard_name = indicator_name_mapping[col_lower]
                    rename_mapping[col] = standard_name
                    standardized_columns.append(standard_name)
                else:
                    # 如果没有匹配的标准名称，则使用小写形式
                    rename_mapping[col] = col_lower
                    standardized_columns.append(col_lower)
            
            # 重命名指标列
            merged_data = merged_data.rename(columns=rename_mapping)
            
            # 更新指标列列表
            indicator_columns = standardized_columns
            
            logger.info(f"指标名称标准化完成，标准化后的指标: {', '.join(indicator_columns)}")

            result['processed_data'] = merged_data
            result['statistics'] = {}
            # 计算每个指标的基本统计信息
            for indicator in indicator_columns:
                # 检查该列是否全为空值
                valid_data = merged_data[indicator].dropna()
                
                if len(valid_data) == 0:
                    # 如果该列全为空值，记录警告并跳过统计计算
                    logger.warning(f"指标 '{indicator}' 的数据全为空值，跳过统计计算")
                    result['statistics'][indicator] = {
                        'min': None,
                        'max': None,
                        'mean': None,
                        'std': None,
                        'median': None,
                        'valid_count': 0,
                        'total_count': len(merged_data[indicator]),
                        'units': self._get_indicator_unit(indicator)
                    }
                    continue
                
                # 基本统计量（只计算非空值）
                stats = valid_data.describe()
                
                result['statistics'][indicator] = {
                    'min': float(stats['min']),
                    'max': float(stats['max']),
                    'mean': float(stats['mean']),
                    'std': float(stats['std']),
                    'median': float(valid_data.median()),
                    'valid_count': len(valid_data),
                    'total_count': len(merged_data[indicator]),
                    'units': self._get_indicator_unit(indicator)
                }
                
            
            # 数据摘要
            try:
                data_summary = {
                    'sample_count': len(merged_data),
                    'indicators': indicator_columns,
                }
                
                # 安全计算经纬度范围
                if 'latitude' in merged_data.columns and 'longitude' in merged_data.columns:
                    lat_valid = merged_data['latitude'].dropna()
                    lon_valid = merged_data['longitude'].dropna()
                    
                    if len(lat_valid) > 0 and len(lon_valid) > 0:
                        data_summary['geo_range'] = {
                            'latitude': {
                                'min': float(lat_valid.min()),
                                'max': float(lat_valid.max()),
                                'valid_count': len(lat_valid)
                            },
                            'longitude': {
                                'min': float(lon_valid.min()),
                                'max': float(lon_valid.max()),
                                'valid_count': len(lon_valid)
                            }
                        }
                    else:
                        logger.warning("经纬度数据全为空值")
                        data_summary['geo_range'] = None
                else:
                    logger.warning("缺少经纬度列")
                    data_summary['geo_range'] = None
                
                result['data_summary'] = data_summary
                
            except Exception as e:
                logger.error(f"生成数据摘要时出错: {str(e)}")
                result['data_summary'] = {
                    'sample_count': len(merged_data),
                    'indicators': indicator_columns,
                    'geo_range': None
                }
            
            logger.info("数据处理完成")
            return result
            
        except MemoryError:
            logger.error("内存不足，无法处理大型数据集")
            return None
        except Exception as e:
            logger.error(f"处理数据时出错: {str(e)}", exc_info=True)
            return None

    def _get_indicator_unit(self, indicator):
        """
        根据指标名称获取单位
        
        Args:
            indicator: 指标名称
            
        Returns:
            指标单位字符串
        """
        # 常见指标单位映射表
        default_units = {
            'Turbidity': 'NTU',
            'SS': 'mg/L',
            'Chla': 'μg/L',
            'DO': 'mg/L',
            'pH': '',
            'Temp': '°C',
            'Cond': 'μS/cm',
            'Sal': 'ppt',
            'ORP': 'mV',
            'TDS': 'mg/L'
        }
        
        # 从配置中读取单位信息
        indicators_config = self.config.get('indicators', {})
        if indicator in indicators_config and 'unit' in indicators_config[indicator]:
            return indicators_config[indicator]['unit']
        
        # 如果配置中没有，使用默认单位
        return default_units.get(indicator, '')

    def match_and_analyze_data(self, measure_data, merged_data, ref_data, output_file=None):
        """
        匹配和分析航测数据与人工采样数据
        
        Args:
            merged_data: 合并后的航测数据DataFrame
            measure_data: 人工采样数据DataFrame
            output_file: 可选的输出文件路径
            
        Returns:
            匹配和分析结果字典，包含拟合系数
        """

        try:
            # 验证输入数据
            if measure_data is None or merged_data is None or ref_data is None:
                logger.error("输入数据包含空值")
                return None, None, None
            
            if not isinstance(measure_data, pd.DataFrame) or not isinstance(merged_data, pd.DataFrame):
                logger.error("输入数据类型错误，期望DataFrame")
                return None, None, None
            
            if measure_data.empty or merged_data.empty:
                logger.error("输入数据为空")
                return None, None, None
            
            logger.info(f"开始匹配和分析数据，人工采样数据 {len(measure_data)} 行，航测数据 {len(merged_data)} 行")
            
            # 检查必要的列
            required_cols = ['latitude', 'longitude']
            for col in required_cols:
                if col not in measure_data.columns:
                    logger.error(f"人工采样数据缺少必要列: {col}")
                    return None, None, None
                if col not in merged_data.columns:
                    logger.error(f"航测数据缺少必要列: {col}")
                    return None, None, None
            
            # 获取共同的指标列
            try:
                common_indicators = list(set(merged_data.columns) & set(measure_data.columns))
                common_indicators = [col for col in common_indicators if col not in ['index', 'latitude', 'longitude']]
                
                if not common_indicators:
                    logger.error("没有找到共同的指标列")
                    return None, None, None
                
                logger.info(f"找到共同指标: {', '.join(common_indicators)}")
                
            except Exception as e:
                logger.error(f"获取共同指标时出错: {str(e)}")
                return None, None, None
            
            # 收集匹配到的航测点索引
            matched_idx = []

            # 存储匹配距离统计信息
            all_distances = []
            min_distance = float('inf')
            max_distance = 0
            
            # 对每个人工采样点，找到最近的航测点
            logger.info("开始匹配测量点与最近航测点：")
            
            for idx, measure_row in measure_data.iterrows():
                try:
                    # 检查经纬度数据有效性
                    measure_lat = measure_row['latitude']
                    measure_lon = measure_row['longitude']
                    
                    if pd.isna(measure_lat) or pd.isna(measure_lon):
                        logger.warning(f"样本点 {idx} 经纬度数据无效，跳过")
                        continue
                    
                    # 验证经纬度范围
                    if not (-90 <= measure_lat <= 90) or not (-180 <= measure_lon <= 180):
                        logger.warning(f"样本点 {idx} 经纬度超出有效范围，跳过")
                        continue
                    
                    # 获取样本点索引信息
                    sample_id = idx
                    if 'index' in measure_row:
                        sample_id = measure_row['index']
                    
                    # 计算到所有航测点的距离
                    distances = []
                    valid_points = []
                    
                    for merged_idx, merged_row in merged_data.iterrows():
                        try:
                            merged_lat = merged_row['latitude']
                            merged_lon = merged_row['longitude']
                            
                            # 检查航测点经纬度有效性
                            if pd.isna(merged_lat) or pd.isna(merged_lon):
                                continue
                                
                            if not (-90 <= merged_lat <= 90) or not (-180 <= merged_lon <= 180):
                                continue
                            
                            dist = haversine(measure_lat, measure_lon, merged_lat, merged_lon)
                            
                            # 检查距离是否合理（小于1000公里）
                            if dist < 1000000:  # 1000公里以内
                                distances.append(dist)
                                valid_points.append(merged_idx)
                            
                        except Exception as e:
                            logger.debug(f"计算距离时出错: {str(e)}")
                            continue
                    
                    if not distances:
                        logger.warning(f"样本点 {sample_id} 没有找到有效的匹配航测点，跳过")
                        continue
                    
                    # 找到最近的点
                    min_dist_idx_in_valid = np.argmin(distances)
                    min_dist = distances[min_dist_idx_in_valid]
                    min_dist_idx = valid_points[min_dist_idx_in_valid]
                    closest_point = merged_data.loc[min_dist_idx]

                    matched_idx.append(min_dist_idx)

                    # 更新距离统计
                    all_distances.append(min_dist)
                    min_distance = min(min_distance, min_dist)
                    max_distance = max(max_distance, min_dist)
                    
                    # 记录匹配点距离到日志
                    logger.info(f"样本点 {sample_id} - 测量点坐标: ({measure_lat:.6f}, {measure_lon:.6f}) "
                              f"-> 最近航测点坐标: ({closest_point['latitude']:.6f}, {closest_point['longitude']:.6f}), "
                              f"距离: {min_dist:.2f}米")
                    
                    # 记录匹配点的指标值详情
                    try:
                        indicators_log = ["匹配点详细指标数据:"]
                        indicators_log.append(f"  样本点 {sample_id}:")
                        
                        for indicator in common_indicators:
                            if indicator in closest_point and indicator in measure_row:
                                try:
                                    merged_value = closest_point[indicator]
                                    measure_value = measure_row[indicator]
                                    
                                    if pd.notna(merged_value) and pd.notna(measure_value):
                                        indicators_log.append(f"    {indicator}: 航测值 = {merged_value:.4f}, 测量值 = {measure_value:.4f}")
                                    else:
                                        indicators_log.append(f"    {indicator}: 数据包含空值")
                                except Exception as e:
                                    indicators_log.append(f"    {indicator}: 数据处理出错 - {str(e)}")
                        
                        logger.debug("\n".join(indicators_log))
                        
                    except Exception as e:
                        logger.warning(f"记录指标详情时出错: {str(e)}")
                        
                except Exception as e:
                    logger.error(f"处理样本点 {idx} 时出错: {str(e)}")
                    continue
            
            if not matched_idx:
                logger.error("没有成功匹配任何样本点")
                return None, None, None
                

            # 将匹配的点转换为DataFrame
            logger.info(f"开始创建匹配的DataFrame，matched_idx: {matched_idx}")
            logger.info(f"measure_data shape: {measure_data.shape}, merged_data shape: {merged_data.shape}, ref_data shape: {ref_data.shape}")
            
            # 检查matched_idx的类型并转换为整数索引
            logger.info(f"matched_idx类型: {type(matched_idx[0]) if matched_idx else 'empty'}")
            
            try:
                # 如果索引是字符串，需要找到对应的位置索引
                if matched_idx and isinstance(matched_idx[0], str):
                    logger.info("检测到字符串索引，转换为位置索引")
                    # 获取merged_data的索引位置映射
                    index_to_pos = {str(idx): pos for pos, idx in enumerate(merged_data.index)}
                    matched_pos_idx = []
                    
                    for idx in matched_idx:
                        if str(idx) in index_to_pos:
                            matched_pos_idx.append(index_to_pos[str(idx)])
                        else:
                            logger.error(f"找不到索引 {idx} 在merged_data中的位置")
                            return None, None, None
                    
                    matched_idx = matched_pos_idx
                    logger.info(f"转换后的位置索引: {matched_idx}")
                
                # 检查索引范围
                max_idx = max(matched_idx) if matched_idx else -1
                min_idx = min(matched_idx) if matched_idx else 0
                
                logger.info(f"matched_idx 范围: [{min_idx}, {max_idx}], merged_data长度: {len(merged_data)}")
                
                if max_idx >= len(merged_data):
                    logger.error(f"matched_idx中的最大索引 {max_idx} 超出merged_data范围 {len(merged_data)}")
                    return None, None, None
                    
                if min_idx < 0:
                    logger.error(f"matched_idx中包含负数索引: {min_idx}")
                    return None, None, None
                    
            except Exception as e:
                logger.error(f"处理matched_idx时出错: {str(e)}")
                return None, None, None
            
            matched_measure_df = measure_data[common_indicators]
            matched_merged_df = merged_data.iloc[matched_idx][common_indicators]
            matched_merged_df.index = matched_measure_df.index
            
            # 处理ref_data的索引问题 - 使用正确的索引映射
            try:
                logger.info(f"ref_data索引内容: {ref_data.index.tolist()}")
                logger.info(f"merged_data索引内容: {merged_data.index.tolist()}")
                
                # 获取原始matched_idx（来自merged_data的标签索引）
                original_matched_idx = []
                for pos_idx in matched_idx:
                    original_idx = merged_data.index[pos_idx]
                    original_matched_idx.append(str(original_idx))
                
                logger.info(f"原始匹配索引标签: {original_matched_idx}")
                
                # 在ref_data中查找对应的光谱数据
                matched_ref_rows = []
                missing_refs = []
                
                for ref_idx in original_matched_idx:
                    if ref_idx in ref_data.index:
                        # 获取该索引的所有行
                        matching_rows = ref_data.loc[ref_idx]
                        
                        # 如果有多行，选择第一行（或者可以选择平均值）
                        if isinstance(matching_rows, pd.DataFrame):
                            logger.info(f"索引 {ref_idx} 有 {len(matching_rows)} 行光谱数据，选择第一行")
                            selected_row = matching_rows.iloc[0]
                        else:
                            # 单行数据
                            selected_row = matching_rows
                        
                        matched_ref_rows.append(selected_row)
                    else:
                        logger.warning(f"在ref_data中找不到索引 {ref_idx}")
                        missing_refs.append(ref_idx)
                
                if missing_refs:
                    logger.error(f"缺失的光谱数据索引: {missing_refs}")
                    logger.error(f"ref_data可用索引: {ref_data.index.tolist()}")
                    return None, None, None
                
                if not matched_ref_rows:
                    logger.error("没有找到任何匹配的光谱数据")
                    return None, None, None
                
                # 创建匹配的ref_data DataFrame
                matched_ref_df = pd.DataFrame(matched_ref_rows)
                matched_ref_df.index = matched_measure_df.index
                
                logger.info(f"成功匹配 {len(matched_ref_df)} 条光谱数据")
                
            except Exception as e:
                logger.error(f"处理ref_data索引时出错: {str(e)}")
                logger.error(f"matched_idx: {matched_idx}, ref_data长度: {len(ref_data)}")
                logger.error(f"ref_data索引: {ref_data.index.tolist()}")
                return None, None, None

            # 记录匹配数据的汇总信息
            logger.info(f"匹配数据汇总：共找到 {len(matched_merged_df)} 对匹配点")

            # 检查匹配的航测点是否都相同
            if len(set(matched_idx)) == 1 and len(matched_idx) > 1:
                error_msg = f"错误：所有测量点都匹配到了同一个航测点 (索引: {matched_idx[0]})。请检查数据或增加航测采样点数量。"
                logger.error(error_msg)
                raise ValueError(error_msg)
            elif len(set(matched_idx)) < len(matched_idx):
                duplicate_count = len(matched_idx) - len(set(matched_idx)) + 1
                logger.warning(f"警告：有 {duplicate_count} 个测量点匹配到了相同的航测点，这可能影响分析结果的准确性。")
            
            # 输出匹配距离统计信息
            if all_distances:
                avg_distance = sum(all_distances) / len(all_distances)
                logger.info(f"匹配距离统计 - 最小: {min_distance:.2f}米, 最大: {max_distance:.2f}米, "
                          f"平均: {avg_distance:.2f}米, 样本数: {len(all_distances)}")
            
            # 建模前最终数据质量验证
            logger.info("建模前最终数据质量验证...")
            
            final_count = len(matched_measure_df)
            
            # 验证经纬度和光谱数据完整性
            geo_issues = 0
            ref_issues = 0
            
            # 检查经纬度（必须完整）
            if 'latitude' in matched_merged_df.columns and 'longitude' in matched_merged_df.columns:
                geo_issues = (matched_merged_df['latitude'].isna() | 
                             matched_merged_df['longitude'].isna()).sum()
            
            # 检查光谱数据完整性
            ref_issues = matched_ref_df.isna().sum().sum()
            
            if geo_issues > 0:
                logger.error(f"建模数据中有 {geo_issues} 个样本缺少经纬度信息")
                raise ValueError("建模数据包含经纬度缺失，无法进行建模")
                
            if ref_issues > 0:
                logger.error(f"建模数据中有 {ref_issues} 个光谱数据缺失")
                raise ValueError("建模数据包含光谱数据缺失，无法进行建模")
            
            # 统计指标数据情况（允许有空值，由建模模块处理）
            logger.info("建模数据指标统计:")
            for col in common_indicators:
                measure_null = matched_measure_df[col].isna().sum()
                merged_null = matched_merged_df[col].isna().sum()
                logger.info(f"  - {col}: 测量数据空值 {measure_null}/{final_count}, 航测数据空值 {merged_null}/{final_count}")
            
            logger.info(f"数据质量验证通过，最终建模样本数: {final_count}，指标空值将由建模模块处理")
            
            logger.info("数据匹配完成")
            return matched_ref_df, matched_merged_df, matched_measure_df
        except Exception as e:
            logger.error(f"匹配和分析数据时出错: {str(e)}", exc_info=True)
            return None, None, None
        