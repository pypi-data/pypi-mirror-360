#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据提取模块
提供文件解压和数据提取功能

本模块主要用于从压缩文件(主要是ZIP文件)中提取和处理数据。
主要功能包括：
1. 解压ZIP文件到指定目录
2. 获取ZIP文件内容列表
3. 根据模式匹配查找文件
4. 检测并修复文本文件编码
5. 验证ZIP文件完整性
6. 安全路径检查，防止路径穿越攻击
7. 估算解压后的文件大小
8. 清理临时文件

使用示例：
```python
from waterquality_processor.extractor import ZipExtractor

# 初始化ZIP解压器
extractor = ZipExtractor()

# 解压ZIP文件
extract_dir = extractor.extract("./data.zip")
if extract_dir:
    print(f"文件已解压到: {extract_dir}")
    
    # 查找特定文件
    csv_file = extractor.find_file("./data.zip", ".csv")
    if csv_file:
        print(f"找到CSV文件: {csv_file}")
        
    # 清理临时文件
    extractor.cleanup("./data.zip")
```
"""
import os
import logging
import zipfile
import tempfile
import shutil
import chardet
import time
from typing import Dict, List, Optional, Union
from pathlib import Path

from .utils import EncodingDetector

logger = logging.getLogger(__name__)


class ZipExtractor():
    """
    ZIP文件提取器
    
    专门用于处理ZIP格式文件的解压和内容提取。
    提供了安全检查、编码修复、文件查找等功能。
    
    属性:
        _extracted_files: 缓存已提取文件列表的字典
        
    示例:
        extractor = ZipExtractor()
        extract_dir = extractor.extract("data.zip")
        csv_file = extractor.find_file("data.zip", "data.csv")
    """
    
    def __init__(self):
        """初始化ZIP文件提取器"""
        self._extracted_files = {}  # 用于缓存已提取的文件
        self._extract_dirs = {}  # 用于缓存每个zip文件对应的解压目录
    
    def extract(self, zip_path: Union[str, Path]) -> Optional[str]:
        """解压ZIP文件
        
        将ZIP文件解压到指定目录，并执行安全检查。
        
        Args:
            zip_path: ZIP文件路径
            
        Returns:
            解压后的目录路径，失败返回None
            
        示例:
            extract_dir = extractor.extract("data.zip")
            if extract_dir:
                print(f"文件已解压到: {extract_dir}")
        """
        try:
            # 验证输入参数 - 处理Path对象和字符串
            if not zip_path:
                logger.error("ZIP文件路径不能为空")
                return None
            
            # 转换为字符串统一处理
            if isinstance(zip_path, Path):
                zip_path = str(zip_path)
            elif isinstance(zip_path, str):
                if not zip_path.strip():
                    logger.error("ZIP文件路径不能为空")
                    return None
                zip_path = zip_path.strip()
            else:
                logger.error(f"不支持的路径类型: {type(zip_path)}")
                return None
            
            # 检查文件是否存在
            if not os.path.exists(zip_path):
                logger.error(f"ZIP文件不存在: {zip_path}")
                return None
            
            # 检查文件大小
            file_size = os.path.getsize(zip_path)
            if file_size == 0:
                logger.error(f"ZIP文件为空: {zip_path}")
                return None
            
            logger.info(f"ZIP文件大小: {file_size / 1024 / 1024:.2f} MB")
                
            # 检查是否为ZIP文件
            if not zipfile.is_zipfile(zip_path):
                logger.error(f"文件不是有效的ZIP格式: {zip_path}")
                return None
            
            # 验证ZIP文件完整性
            if not self._verify_zip_file(zip_path):
                logger.error(f"ZIP文件损坏或不完整: {zip_path}")
                return None
            
            # 创建提取目录
            zip_name = os.path.splitext(os.path.basename(zip_path))[0]
            if not zip_name:
                zip_name = f"extracted_{int(time.time())}"
            
            # 创建提取目录
            extract_dir = os.path.join(os.path.dirname(os.path.abspath(zip_path)), zip_name)
            
            try:
                os.makedirs(extract_dir, exist_ok=True)
            except PermissionError:
                logger.error(f"没有权限创建解压目录: {extract_dir}")
                return None
            except OSError as e:
                logger.error(f"创建解压目录失败: {extract_dir}, 错误: {str(e)}")
                return None
            
            logger.info(f"开始解压ZIP文件: {zip_path} -> {extract_dir}")
            
            # 估算解压后的大小
            estimated_size = self._estimate_uncompressed_size(zip_path)
            if estimated_size > 0:
                logger.info(f"估算解压后大小: {estimated_size / 1024 / 1024:.2f} MB")
                
                # 检查磁盘空间
                free_space = self._get_free_space(extract_dir)
                if free_space < estimated_size * 1.2:  # 预畗20%空间
                    logger.error(f"磁盘空间不足，需要 {estimated_size / 1024 / 1024:.2f} MB，可用 {free_space / 1024 / 1024:.2f} MB")
                    return None
            
            # 解压文件
            extracted_count = 0
            failed_files = []
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                file_list = zip_ref.namelist()
                
                # 检查文件名安全性
                unsafe_files = self._check_path_safety(file_list)
                if unsafe_files:
                    logger.warning(f"发现不安全的文件路径，将跳过: {unsafe_files[:5]}...")  # 只显示前5个
                
                for file_info in zip_ref.infolist():
                    try:
                        # 跳过不安全的文件
                        if file_info.filename in unsafe_files:
                            continue
                            
                        # 解压单个文件
                        zip_ref.extract(file_info, extract_dir)
                        extracted_count += 1
                        
                        # 修复文本文件编码
                        extracted_path = os.path.join(extract_dir, file_info.filename)
                        if os.path.isfile(extracted_path):
                            self._fix_text_file_encoding(extracted_path)
                            
                    except Exception as e:
                        failed_files.append(file_info.filename)
                        logger.warning(f"解压文件失败: {file_info.filename}, 错误: {str(e)}")
                        continue
                
                # 存储已提取的文件列表（排除失败的文件）
                successful_files = [f for f in file_list if f not in failed_files and f not in unsafe_files]
                self._extracted_files[zip_path] = successful_files
                
                # 存储文件对应的解压目录
                self._extract_dirs[zip_path] = extract_dir
                
                logger.info(f"ZIP文件解压完成，成功 {extracted_count} 个文件")
                
                if failed_files:
                    logger.warning(f"有 {len(failed_files)} 个文件解压失败")
                
                if unsafe_files:
                    logger.warning(f"有 {len(unsafe_files)} 个不安全文件被跳过")
            
            return extract_dir
            
        except zipfile.BadZipFile:
            logger.error(f"无效的ZIP文件: {zip_path}")
            return None
        except zipfile.LargeZipFile:
            logger.error(f"ZIP文件过大，需要ZIP64支持: {zip_path}")
            return None
        except MemoryError:
            logger.error("内存不足，无法解压大型ZIP文件")
            return None
        except FileNotFoundError:
            logger.error(f"ZIP文件不存在: {zip_path}")
            return None
        except PermissionError:
            logger.error(f"没有权限访问ZIP文件: {zip_path}")
            return None
        except Exception as e:
            logger.error(f"解压ZIP文件时出错: {str(e)}", exc_info=True)
            return None
    
    def get_extracted_files(self, zip_path: Union[str, Path]) -> List[str]:
        """获取已提取的文件列表
        
        获取指定ZIP文件解压后的所有文件路径列表。
        如果文件尚未解压，则尝试读取ZIP文件内容列表。
        
        Args:
            zip_path: ZIP文件路径
            
        Returns:
            文件路径列表
            
        示例:
            files = extractor.get_extracted_files("data.zip")
            for file in files:
                print(f"- {file}")
        """
        # 转换为字符串
        if isinstance(zip_path, Path):
            zip_path = str(zip_path)
            
        if zip_path in self._extracted_files:
            return self._extracted_files[zip_path]
        
        # 如果没有缓存记录，尝试读取
        if zipfile.is_zipfile(zip_path):
            try:
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    self._extracted_files[zip_path] = zip_ref.namelist()
                    return zip_ref.namelist()
            except Exception as e:
                logger.error(f"读取ZIP文件内容列表时出错: {str(e)}")
        
        return []
    
    def find_file(self, zip_path: Union[str, Path], pattern: str) -> Optional[str]:
        """在已提取的文件中查找匹配的文件
        
        根据文件名模式在已解压的文件中查找匹配的文件。
        模式匹配使用部分匹配（包含关系），不区分大小写。
        
        Args:
            zip_path: ZIP文件路径
            pattern: 文件名模式，支持部分匹配
            
        Returns:
            匹配的文件路径，未找到返回None
            
        示例:
            # 查找包含"report"的文件
            report_file = extractor.find_file("data.zip", "report")
            
            # 查找CSV文件
            csv_file = extractor.find_file("data.zip", ".csv")
        """
        # 转换为字符串
        if isinstance(zip_path, Path):
            zip_path = str(zip_path)
            
        files = self.get_extracted_files(zip_path)
        
        # 获取提取目录
        if zip_path not in self._extract_dirs:
            zip_name = os.path.splitext(os.path.basename(zip_path))[0]
            extract_dir = os.path.join(os.path.dirname(os.path.abspath(zip_path)), zip_name)
            self._extract_dirs[zip_path] = extract_dir
        else:
            extract_dir = self._extract_dirs[zip_path]
        
        for file in files:
            if pattern.lower() in file.lower():
                return os.path.join(extract_dir, file)
        
        return None
    
    def _get_free_space(self, path) -> int:
        """获取指定路径的可用磁盘空间
        
        Args:
            path: 目录路径
            
        Returns:
            可用字节数
        """
        try:
            _, _, free = shutil.disk_usage(path)
            return free
        except Exception as e:
            logger.warning(f"获取磁盘空间失败: {str(e)}")
            return float('inf')  # 如果获取失败，假设有足够空间
    
    def _check_path_safety(self, file_list: List[str]) -> List[str]:
        """检查文件路径安全性，防止路径穿越攻击
        
        Args:
            file_list: 文件路径列表
            
        Returns:
            不安全的文件路径列表
        """
        unsafe_files = []
        
        for file_path in file_list:
            try:
                # 检查绝对路径
                if os.path.isabs(file_path):
                    unsafe_files.append(file_path)
                    continue
                
                # 检查路径穿越 ("..", "../", "..\\", etc.)
                if '..' in file_path.replace('\\', '/').split('/'):
                    unsafe_files.append(file_path)
                    continue
                
                # 检查Windows路径穿越
                if '\\' in file_path and '..' in file_path:
                    unsafe_files.append(file_path)
                    continue
                    
                # 检查特殊字符
                dangerous_chars = ['<', '>', ':', '"', '|', '?', '*']
                if any(char in file_path for char in dangerous_chars):
                    unsafe_files.append(file_path)
                    continue
                    
            except Exception as e:
                logger.warning(f"检查文件路径安全性时出错: {file_path}, 错误: {str(e)}")
                unsafe_files.append(file_path)
        
        return unsafe_files
    
    def _detect_encoding(self, file_path: str) -> str:
        """检测文件编码
        
        使用chardet库检测文本文件的编码类型。
        
        Args:
            file_path: 文件路径
            
        Returns:
            str: 检测到的编码，如果检测失败则返回utf-8
        """
        try:
            if not os.path.exists(file_path):
                logger.warning(f"文件不存在，无法检测编码: {file_path}")
                return 'utf-8'
                
            if os.path.getsize(file_path) == 0:
                logger.debug(f"文件为空，使用默认编码: {file_path}")
                return 'utf-8'
                
            with open(file_path, 'rb') as f:
                # 限制读取大小以避免内存问题
                raw_data = f.read(min(8192, os.path.getsize(file_path)))
                
                if not raw_data:
                    return 'utf-8'
                    
                result = chardet.detect(raw_data)
                encoding = result.get('encoding', 'utf-8')
                confidence = result.get('confidence', 0)
                
                # 如果置信度太低，使用默认编码
                if confidence < 0.7:
                    logger.debug(f"编码检测置信度低 ({confidence:.2f})，使用默认编码: {file_path}")
                    encoding = 'utf-8'
                    
                return encoding or 'utf-8'
        except MemoryError:
            logger.warning(f"内存不足，无法检测文件编码: {file_path}")
            return 'utf-8'
        except Exception as e:
            logger.warning(f"编码检测失败: {str(e)}")
            return 'utf-8'
    
    def _fix_text_file_encoding(self, file_path: str) -> bool:
        """修复文本文件编码
        
        将文本文件转换为UTF-8编码，便于后续处理。
        
        Args:
            file_path: 文件路径
            
        Returns:
            bool: 是否成功修复
        """
        try:
            # 检查文件是否存在
            if not os.path.exists(file_path):
                logger.warning(f"文件不存在，无法修复编码: {file_path}")
                return False
            
            # 只处理文本文件
            if not file_path.lower().endswith(('.txt', '.csv')):
                return True
            
            # 检查文件大小
            file_size = os.path.getsize(file_path)
            if file_size == 0:
                logger.debug(f"文件为空，跳过编码修复: {file_path}")
                return True
            
            # 限制文件大小以避免内存问题
            max_size = 100 * 1024 * 1024  # 100MB
            if file_size > max_size:
                logger.warning(f"文件过大 ({file_size / 1024 / 1024:.2f} MB)，跳过编码修复: {file_path}")
                return True
            
            # 检测编码
            encoding = self._detect_encoding(file_path)
            
            # 如果已经是UTF-8，跳过转换
            if encoding.lower() in ['utf-8', 'utf8', 'ascii']:
                logger.debug(f"文件已是 UTF-8 编码，跳过转换: {file_path}")
                return True
            
            logger.debug(f"将文件从 {encoding} 转换为 UTF-8: {file_path}")
            
            # 使用统一的编码检测器
            detector = EncodingDetector()
            content = detector.read_text_file(file_path)
            
            if content is None:
                logger.error(f"无法读取文件内容: {file_path}")
                return False
            
            # 备份原文件
            backup_path = file_path + '.backup'
            try:
                shutil.copy2(file_path, backup_path)
            except Exception as e:
                logger.warning(f"创建备份文件失败: {str(e)}")
            
            # 以UTF-8重新写入
            try:
                with open(file_path, 'w', encoding='utf-8', errors='ignore') as f:
                    f.write(content)
                    
                # 删除备份文件
                if os.path.exists(backup_path):
                    os.remove(backup_path)
                    
                logger.debug(f"文件编码修复成功: {file_path}")
                return True
                
            except Exception as e:
                # 恢复备份
                if os.path.exists(backup_path):
                    try:
                        shutil.move(backup_path, file_path)
                        logger.info(f"已恢复原文件: {file_path}")
                    except Exception:
                        pass
                raise e
            
        except MemoryError:
            logger.error(f"内存不足，无法修复文件编码: {file_path}")
            return False
        except PermissionError:
            logger.error(f"没有权限修改文件: {file_path}")
            return False
        except Exception as e:
            logger.error(f"修复文件编码失败 {file_path}: {str(e)}")
            return False
    
    def _verify_zip_file(self, zip_path: str) -> bool:
        """验证ZIP文件完整性
        
        检查ZIP文件是否损坏或不完整。
        
        Args:
            zip_path: ZIP文件路径
            
        Returns:
            bool: 文件是否完整
            
        示例:
            if extractor._verify_zip_file("data.zip"):
                print("ZIP文件完好无损")
            else:
                print("ZIP文件已损坏")
        """
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                result = zip_ref.testzip()
                if result is not None:
                    logger.error(f"ZIP文件损坏，首个损坏文件: {result}")
                    return False
                return True
        except Exception as e:
            logger.error(f"验证ZIP文件失败: {str(e)}")
            return False
    
    def _estimate_uncompressed_size(self, zip_path: str) -> int:
        """估算解压后的总大小
        
        计算ZIP文件解压后将占用的磁盘空间。
        
        Args:
            zip_path: ZIP文件路径
            
        Returns:
            int: 估算的总大小（字节）
            
        示例:
            size = extractor._estimate_uncompressed_size("data.zip")
            print(f"解压后大小约: {size / 1024 / 1024:.1f} MB")
        """
        try:
            total_size = 0
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                for info in zip_ref.infolist():
                    total_size += info.file_size
            return total_size
        except Exception as e:
            logger.error(f"估算解压大小失败: {str(e)}")
            return 0
    
    def cleanup(self, zip_path: Union[str, Path] = None):
        """清理解压的临时文件
        
        删除解压过程中生成的临时文件，释放磁盘空间。
        
        Args:
            zip_path: 指定要清理的ZIP文件，如果为None则清理所有
            
        示例:
            # 清理单个ZIP文件的临时文件
            extractor.cleanup("data.zip")
            
            # 清理所有临时文件
            extractor.cleanup()
        """
        try:
            if zip_path:
                # 转换为字符串
                if isinstance(zip_path, Path):
                    zip_path = str(zip_path)
                    
                # 清理指定ZIP文件的解压目录
                if zip_path in self._extract_dirs:
                    extract_dir = self._extract_dirs[zip_path]
                    if os.path.exists(extract_dir):
                        try:
                            # 检查目录是否被占用
                            self._force_remove_directory(extract_dir)
                            logger.info(f"已清理目录: {extract_dir}")
                            del self._extract_dirs[zip_path]
                            if zip_path in self._extracted_files:
                                del self._extracted_files[zip_path]
                        except PermissionError:
                            logger.error(f"没有权限删除目录: {extract_dir}")
                        except Exception as e:
                            logger.error(f"清理目录失败 {extract_dir}: {str(e)}")
            else:
                # 清理所有解压文件
                failed_cleanups = []
                
                for zip_path_key, extract_dir in list(self._extract_dirs.items()):
                    try:
                        if os.path.exists(extract_dir):
                            self._force_remove_directory(extract_dir)
                            logger.info(f"已清理目录: {extract_dir}")
                    except Exception as e:
                        failed_cleanups.append((extract_dir, str(e)))
                        logger.error(f"清理目录失败 {extract_dir}: {str(e)}")
                
                # 清空缓存
                self._extract_dirs.clear()
                self._extracted_files.clear()
                
                if failed_cleanups:
                    logger.warning(f"有 {len(failed_cleanups)} 个目录清理失败")
            
            logger.debug("清理完成")
            
        except Exception as e:
            logger.error(f"清理操作失败: {str(e)}")
    
    def _force_remove_directory(self, directory: str, max_retries: int = 3):
        """强制删除目录，包括处理被占用的文件
        
        Args:
            directory: 要删除的目录路径
            max_retries: 最大重试次数
        """
        import time
        
        for attempt in range(max_retries):
            try:
                # 先尝试正常删除
                shutil.rmtree(directory)
                return
            except PermissionError:
                if attempt < max_retries - 1:
                    # 尝试修改文件权限
                    try:
                        self._make_writable(directory)
                        time.sleep(0.1)  # 等待一下
                    except Exception:
                        pass
                else:
                    raise
            except OSError as e:
                if attempt < max_retries - 1:
                    time.sleep(0.1)  # 等待一下再重试
                else:
                    raise
    
    def _make_writable(self, path: str):
        """使文件或目录可写
        
        Args:
            path: 文件或目录路径
        """
        import stat
        
        try:
            if os.path.isfile(path):
                os.chmod(path, stat.S_IWRITE | stat.S_IREAD)
            elif os.path.isdir(path):
                for root, dirs, files in os.walk(path):
                    for d in dirs:
                        try:
                            os.chmod(os.path.join(root, d), stat.S_IWRITE | stat.S_IREAD | stat.S_IEXEC)
                        except Exception:
                            pass
                    for f in files:
                        try:
                            os.chmod(os.path.join(root, f), stat.S_IWRITE | stat.S_IREAD)
                        except Exception:
                            pass
        except Exception as e:
            logger.debug(f"修改文件权限失败: {str(e)}")

# 优化建议:
# 1. 多格式支持: 扩展支持RAR、7Z等其他压缩格式
# 2. 并行解压: 对大型ZIP文件使用多线程提高解压速度
# 3. 密码支持: 添加对加密ZIP文件的支持
# 4. 内存优化: 对大文件进行流式处理，减少内存占用
# 5. 提供进度回调: 添加进度通知机制，便于显示解压进度
# 6. 健壮性: 增强错误恢复能力，例如损坏文件跳过
# 7. 安全性: 增强目录遍历和文件类型的安全检查
# 8. 跨平台: 优化文件路径处理，确保跨平台兼容性 