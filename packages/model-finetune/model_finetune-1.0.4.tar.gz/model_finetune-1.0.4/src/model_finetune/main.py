import argparse  # 添加命令行参数解析
import json
import logging
import logging.handlers
import os
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

# 从encryption模块导入加密函数
from autowaterqualitymodeler.utils.encryption import encrypt_data_to_file
from autowaterqualitymodeler.utils.logger import setup_logging

from .data_processor import DataProcessor
from .downloader import ResourceDownloader
from .extractor import ZipExtractor
from .data_merger import DataMerger, ReflectanceDataProcessor
from .utils import EncodingDetector, ConfigManager, FileProcessingError

# 初始化模块级别的logger
logger = logging.getLogger(__name__)


def read_position_data(pos_file: str) -> pd.DataFrame:
    """读取位置数据文件

    Args:
        pos_file: 位置文件路径(POS.TXT)

    Returns:
        包含位置数据的DataFrame，失败返回空DataFrame
    """
    position_data = pd.DataFrame()

    # 检查文件是否存在
    if not os.path.exists(pos_file):
        logger.error(f"位置文件不存在: {pos_file}")
        return pd.DataFrame()

    # 检查文件是否为空
    if os.path.getsize(pos_file) == 0:
        logger.error(f"位置文件为空: {pos_file}")
        return pd.DataFrame()

    try:
        # 尝试多种编码方式读取文件
        encodings = ["utf-8", "gbk", "gb2312", "latin-1"]
        file_content = None

        for encoding in encodings:
            try:
                with open(pos_file, "r", encoding=encoding) as f:
                    file_content = f.readlines()
                logger.debug(f"使用编码 {encoding} 成功读取位置文件")
                break
            except UnicodeDecodeError:
                continue

        if file_content is None:
            logger.error(f"无法使用任何编码读取位置文件: {pos_file}")
            return pd.DataFrame()

        data_list = []
        invalid_lines = 0

        for line_num, line in enumerate(file_content, 1):
            line = line.strip()
            if not line:  # 跳过空行
                continue

            try:
                # 使用正则表达式解析每一行
                match = re.search(
                    r"REFL_(\d+)\.csv latitude: ([0-9.]+) longitude: ([0-9.]+) height: ([0-9.]+)",
                    line,
                )
                if match:
                    sample_id = int(match.group(1))
                    latitude = float(match.group(2))
                    longitude = float(match.group(3))

                    # 验证经纬度范围
                    if not (-90 <= latitude <= 90):
                        logger.warning(f"第{line_num}行纬度超出有效范围: {latitude}")
                        invalid_lines += 1
                        continue

                    if not (-180 <= longitude <= 180):
                        logger.warning(f"第{line_num}行经度超出有效范围: {longitude}")
                        invalid_lines += 1
                        continue

                    data_list.append(
                        {
                            "index": str(sample_id),
                            "latitude": latitude,
                            "longitude": longitude,
                        }
                    )
                else:
                    logger.debug(f"第{line_num}行格式不匹配，跳过: {line[:50]}...")
                    invalid_lines += 1
            except (ValueError, IndexError) as e:
                logger.warning(
                    f"第{line_num}行数据解析错误: {str(e)}, 内容: {line[:50]}..."
                )
                invalid_lines += 1
                continue

        if invalid_lines > 0:
            logger.warning(f"位置文件中有 {invalid_lines} 行无效数据被跳过")

        if data_list:
            position_data = pd.DataFrame(data_list)

            # 检查重复的sample_id
            duplicate_ids = position_data[
                position_data.duplicated("index", keep=False)
            ]["index"].unique()
            if len(duplicate_ids) > 0:
                logger.warning(
                    f"发现重复的样本ID: {duplicate_ids.tolist()}，将保留第一个"
                )
                position_data = position_data.drop_duplicates("index", keep="first")

            position_data.set_index("index", inplace=True)
            logger.info(f"成功读取位置数据，共 {len(position_data)} 条有效记录")
        else:
            logger.error("位置文件中没有找到任何有效数据")

        return position_data

    except FileNotFoundError:
        logger.error(f"位置文件未找到: {pos_file}")
        return pd.DataFrame()
    except PermissionError:
        logger.error(f"没有权限读取位置文件: {pos_file}")
        return pd.DataFrame()
    except Exception as e:
        logger.error(f"读取位置数据失败: {str(e)}", exc_info=True)
        return pd.DataFrame()


def merge_data_files(
    indices_file: str, pos_file: str, output_file=None
) -> pd.DataFrame:
    """合并INDEXS.CSV（水质指标）和POS.TXT（位置信息）文件

    Args:
        indices_file: 水质指标文件路径(INDEXS.CSV)
        pos_file: 位置文件路径(POS.TXT)
        output_file: 可选的输出文件路径

    Returns:
        合并后的DataFrame，失败返回空DataFrame
    """
    try:
        # 使用新的DataMerger模块
        merger = DataMerger()
        merged_df = merger.merge_position_and_indices(indices_file, pos_file)
        
        # 可选：保存到输出文件
        if output_file and not merged_df.empty:
            try:
                os.makedirs(os.path.dirname(output_file), exist_ok=True)
                merged_df.to_csv(output_file, index=True, encoding="utf-8")
                logger.info(f"合并数据已保存到: {output_file}")
            except Exception as e:
                logger.warning(f"保存合并数据失败: {str(e)}")

        return merged_df

    except FileProcessingError as e:
        logger.error(f"文件处理错误: {str(e)}")
        return pd.DataFrame()
    except Exception as e:
        logger.error(f"合并数据文件时出错: {str(e)}", exc_info=True)
        return pd.DataFrame()


def process_data(zip_path, measure_data_path):
    """处理数据文件

    Returns:
        bool: 是否处理成功
    """
    logger.info("开始处理数据...")

    try:
        # 获取ZIP文件路径
        if not zip_path or not os.path.exists(zip_path):
            logger.error("未找到数据文件")
            return False

        # 初始化ZIP解压器
        extractor = ZipExtractor()
        # 解压文件
        extract_dir = extractor.extract(zip_path)

        if not extract_dir:
            logger.error("解压文件失败")
            return False

        # 查找INDEXS.CSV和POS.TXT文件
        indices_file = None
        pos_file = None
        ref_files = []
        for root, _, files in os.walk(extract_dir):
            for file_path in files:
                file_path = os.path.join(root, file_path)
                if os.path.basename(file_path).upper() == "INDEXS.CSV":
                    indices_file = file_path
                elif os.path.basename(file_path).upper() == "POS.TXT":
                    pos_file = file_path
                elif "REFL" in os.path.basename(file_path).upper() and not os.path.basename(file_path).upper().startswith("."):
                    ref_files.append(file_path)

        if not indices_file or not pos_file:
            logger.error("未找到INDEXS.CSV或POS.TXT文件")
            return False
        if ref_files:
            ref_files.sort(
                key=lambda x: int(os.path.basename(x).split("_")[-1].split(".")[0])
            )
            
            # 使用新的ReflectanceDataProcessor处理反射率数据
            reflectance_processor = ReflectanceDataProcessor()
            ref_data = reflectance_processor.process_reflectance_files(ref_files)

            logger.info(
                f"反射率数据包含 {len(ref_data)} 行和 {len(ref_data.columns)} 列"
            )

        # 处理数据 - 直接调用merge_data_files函数
        merged_data = merge_data_files(indices_file, pos_file)
        if merged_data.empty:
            logger.error("数据合并失败")
            return False

        # 处理合并后的数据,是一个字典，不仅仅含有merged_data
        processed_merged_data = DataProcessor().process_data(merged_data)

        if not processed_merged_data:
            logger.error("数据处理失败")
            return False

        # 处理人工采样数据（如果有）
        if measure_data_path and os.path.exists(measure_data_path):
            logger.info(f"开始处理人工采样数据: {measure_data_path}")

            try:
                # 检查文件大小
                if os.path.getsize(measure_data_path) == 0:
                    logger.error(f"人工采样数据文件为空: {measure_data_path}")
                    return False

                # 读取人工采样数据，尝试多种编码
                encodings = ["utf-8", "gbk", "gb2312", "latin-1"]
                measure_data = None

                for encoding in encodings:
                    try:
                        measure_data = pd.read_csv(
                            measure_data_path, encoding=encoding, header=0, index_col=0
                        )
                        logger.debug(f"使用编码 {encoding} 成功读取人工采样数据")
                        break
                    except (UnicodeDecodeError, pd.errors.EmptyDataError):
                        continue

                if measure_data is None:
                    logger.error(
                        f"无法使用任何编码读取人工采样数据文件: {measure_data_path}"
                    )
                    return False

                if measure_data.empty:
                    logger.error(f"人工采样数据文件为空: {measure_data_path}")
                    return False

                logger.info(
                    f"人工采样数据包含 {len(measure_data)} 行，{len(measure_data.columns)} 列"
                )

                # 处理人工采样数据，格式化数据
                processed_measure_data = DataProcessor().process_data(measure_data)
                if not processed_measure_data:
                    logger.error("人工采样数据处理失败")
                    return False

            except pd.errors.EmptyDataError:
                logger.error(f"人工采样数据文件为空或格式错误: {measure_data_path}")
                return False
            except pd.errors.ParserError as e:
                logger.error(f"人工采样数据文件解析错误: {str(e)}")
                return False
            except FileNotFoundError:
                logger.error(f"人工采样数据文件不存在: {measure_data_path}")
                return False
            except PermissionError:
                logger.error(f"没有权限读取人工采样数据文件: {measure_data_path}")
                return False
            except Exception as e:
                logger.error(f"读取人工采样数据时出错: {str(e)}", exc_info=True)
                return False

            # 分析人工采样数据
            matched_ref_df, matched_merged_df, matched_measure_df = (
                DataProcessor().match_and_analyze_data(
                    processed_measure_data["processed_data"],
                    processed_merged_data["processed_data"],
                    ref_data,
                )
            )
            if len(matched_ref_df) == len(matched_merged_df) == len(matched_measure_df):
                logger.info(f"光谱数据、实测数据匹配完成，样本量{len(matched_ref_df)}!")

            from autowaterqualitymodeler.run import main

        return main(matched_ref_df, matched_merged_df, matched_measure_df)
    except Exception as e:
        logger.error(f"数据处理失败: {str(e)}")
        return [None, None]


def _validate_model_data(model_result, logger) -> bool:
    """
    验证模型数据是否为有效的键值对格式
    
    Args:
        model_result: 要验证的模型结果数据
        logger: 日志记录器
        
    Returns:
        bool: 数据有效返回True，否则返回False
    """
    from .common_validators import CommonValidators
    return CommonValidators.validate_model_data(model_result, logger)


if __name__ == "__main__":
    # 添加命令行参数解析
    parser = argparse.ArgumentParser(description="水质数据处理程序")
    # action='store_true'表示当命令行中包含--debug参数时，args.debug的值会被设置为True
    # 如果命令行中没有--debug参数，则args.debug默认为False
    # 这种参数称为标志参数，不需要额外的值，仅通过存在与否来表示布尔状态
    parser.add_argument(
        "--debug", action="store_true", help="启用调试模式，使用测试数据而不是管道输入"
    )
    args = parser.parse_args()

    # 创建下载目录
    output_dir = Path("model_fine_tuning_output")

    # 创建日志目录
    logs_dir = os.path.join(output_dir, "logs")
    os.makedirs(logs_dir, exist_ok=True)

    # 创建下载目录
    downloads_dir = os.path.join(output_dir, "downloads")
    os.makedirs(downloads_dir, exist_ok=True)

    # 创建模型子目录
    models_dir = os.path.join(output_dir, "models")
    os.makedirs(models_dir, exist_ok=True)

    # 配置日志系统
    try:
        # 设置是否在调试模式下输出到控制台
        # console_output = args.debug # 控制控制台输出
        console_output = args.debug  # 控制控制台输出

        # 使用与example.py相同的日志设置工具
        log_file = setup_logging(
            log_name="main", logs_dir=logs_dir, console_output=console_output
        )
        logger = logging.getLogger(__name__)
        logger.info(f"日志文件: {log_file}")
        logger.info(f"调试模式: {console_output}")

        logger.info(f"输出目录: {output_dir}")
        logger.info(f"下载目录: {downloads_dir}")
        logger.info(f"日志目录: {logs_dir}")
        logger.info(f"模型目录: {models_dir}")
    except Exception as e:
        # 如果无法使用共享日志配置，则使用基本配置
        logger.error(f"配置日志系统失败，将使用基本配置: {e}")

        # 创建文件处理器 - 使用'w'模式覆盖之前的日志
        file_handler = logging.FileHandler(
            os.path.join(logs_dir, "processing.log"), mode="w", encoding="utf-8"
        )
        file_handler.setFormatter(
            logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        )

        # 配置根日志记录器
        root_logger = logging.getLogger()  # 获取根日志记录器
        root_logger.setLevel(logging.INFO)

        # 清除任何现有的处理器
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

        # 添加文件处理器
        root_logger.addHandler(file_handler)

        # 添加调试模式下的控制台处理器
        if args.debug:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(
                logging.Formatter(
                    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                )
            )
            root_logger.addHandler(console_handler)

        logger = logging.getLogger(__name__)
        logger.error(f"配置共享日志系统失败: {e}", exc_info=True)

    result = None
    # 调试模式处理
    if args.debug:
        logger.info("运行在调试模式")

        # 使用默认测试数据
        test_data = {
            "file_url": r"D:\OneDrive\OneDriveForBusiness\study\fine_tuning\model_fine_tuning_output\downloads\25307e84-88de-428c-8691-c033f7473c8d 2.zip",
            "measure_data": r"D:\OneDrive\OneDriveForBusiness\study\fine_tuning\model_fine_tuning_output\downloads\模型测试采样数据.csv",
        }
        logger.info("使用默认测试数据")

        # 处理测试数据
        zip_path = test_data.get("file_url")
        csv_path = test_data.get("measure_data")

        if not os.path.exists(zip_path):
            logger.error(f"ZIP文件不存在: {zip_path}")
        elif not os.path.exists(csv_path):
            logger.error(f"测量数据文件不存在: {csv_path}")
        else:
            logger.info(f"开始处理: ZIP={zip_path}, CSV={csv_path}")
            process_result = process_data(
                zip_path=zip_path, measure_data_path=csv_path
            )
            if isinstance(process_result, tuple) and len(process_result) == 2:
                result, pred_df = process_result
            else:
                result = process_result
                pred_df = None

    # 正常模式 - 检查是否有管道输入
    elif not sys.stdin.isatty():
        try:
            # 从标准输入读取文件路径
            json_file_path = sys.stdin.read().strip()
            logger.info(f"从标准输入接收到文件路径: {json_file_path}")

            # 检查文件是否存在
            if not os.path.exists(json_file_path):
                logger.error(f"文件不存在: {json_file_path}")
                sys.exit(1)

            # 读取JSON文件内容
            with open(json_file_path, "r", encoding="utf-8") as f:
                input_data = f.read()

            # 尝试解析为JSON
            data = json.loads(input_data)

            logger.info(f"成功从文件读取JSON数据: {json_file_path}")

            # 如果需要处理数据中的URL，可以使用ResourceDownloader
            if "file_url" in data:
                downloader = ResourceDownloader(downloads_dir)
                zip_path = downloader.download(data["file_url"])

                if zip_path:
                    logger.info(f"zip文件成功下载文件到: {zip_path}")

            if "measure_data" in data:
                downloader = ResourceDownloader(downloads_dir)
                csv_path = downloader.download(data["measure_data"])

                if csv_path:
                    logger.info(f"csv实测数据成功下载文件到: {csv_path}")

            if csv_path and zip_path:
                process_result = process_data(
                    zip_path=zip_path, measure_data_path=csv_path
                )
                if isinstance(process_result, tuple) and len(process_result) == 2:
                    result, pred_df = process_result
                else:
                    result = process_result
                    pred_df = None

        except json.JSONDecodeError:
            logger.error("无法解析JSON数据")
        except Exception as e:
            logger.error(f"处理管道输入时出错: {str(e)}")

    else:
        logger.warning("没有检测到管道输入")

    # 将结果加密并保存到本地
    if result:
        try:
            # 使用安全的加密配置
            from .utils import ConfigManager
            encryption_config = ConfigManager.get_encryption_config()
            
            # 验证数据格式 - 确保是键值对格式
            if not _validate_model_data(result, logger):
                logger.error("模型数据验证失败：数据不是有效的键值对格式")
                sys.exit(1)
            
            encrypted_path = encrypt_data_to_file(
                data_obj=result,
                password=encryption_config['password'],
                salt=encryption_config['salt'],
                iv=encryption_config['iv'],
                output_dir=models_dir,
                logger=logger,
            )

            if encrypted_path:
                # 打印output_path的绝对路径
                print(os.path.abspath(encrypted_path))
        except Exception as e:
            logger.error(f"加密结果时出错: {str(e)}")
    else:
        logger.warning("建模结果为空，没有结果可以加密保存")
        print(f"error: 建模失败，请检查log文件:{log_file}")
