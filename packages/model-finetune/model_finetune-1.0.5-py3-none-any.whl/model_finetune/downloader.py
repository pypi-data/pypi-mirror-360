#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
资源下载模块
提供网络资源下载功能，支持阿里云OSS认证
"""
import os
import logging
import requests
# import oss2  # 已移除OSS SDK依赖，采用安全策略
import time
import re
from urllib.parse import urlparse, parse_qsl, unquote
from pathlib import Path
from typing import Optional, Tuple
# from dotenv import load_dotenv  # 不再加载环境变量中的OSS凭据

# 安全策略：不加载.env文件中的OSS凭据

logger = logging.getLogger(__name__)

class ResourceDownloader:
    """资源下载器类"""
    
    def __init__(self, save_dir="downloads"):
        """初始化资源下载器
        
        Args:
            save_dir: 文件保存目录
        """
        try:
            self.save_dir = Path(save_dir)
            self.timeout = 30  # 下载超时时间（秒）
            self.max_retries = 3  # 最大重试次数
            
            # 验证保存目录路径
            if not save_dir or save_dir.strip() == "":
                raise ValueError("保存目录不能为空")
            
            # 确保保存目录存在
            try:
                os.makedirs(self.save_dir, exist_ok=True)
            except PermissionError:
                logger.error(f"没有权限创建保存目录: {self.save_dir}")
                raise
            except OSError as e:
                logger.error(f"创建保存目录失败: {self.save_dir}, 错误: {str(e)}")
                raise
            
            # 安全策略：不存储OSS凭据，仅支持有效的预签名URL下载
            # 当OSS链接过期时，应该由调用方提供新的有效链接，而不是自动重新签名
            logger.info('下载器采用安全策略：仅支持有效的HTTP/HTTPS链接下载')
                
        except Exception as e:
            logger.error(f"初始化下载器失败: {str(e)}")
            raise
    
    def download(self, url: str, filename=None) -> Optional[Path]:
        """下载资源
        
        Args:
            url: 资源URL
            filename: 指定文件名，如果为None则从URL中提取
            
        Returns:
            下载后的文件路径，失败返回None
        """
        try:
            # 验证URL
            if not url or not url.strip():
                logger.error("下载URL不能为空")
                return None
            
            url = url.strip()
            
            # 验证URL格式
            try:
                parsed_url = urlparse(url)
                if not all([parsed_url.scheme, parsed_url.netloc]):
                    logger.error(f"URL格式无效: {url}")
                    return None
            except Exception as e:
                logger.error(f"URL解析失败: {url}, 错误: {str(e)}")
                return None
            
            logger.info(f"开始下载资源: {url}")
            
            # 解析URL获取文件名
            if not filename:
                # 解析URL获取文件名
                filename = os.path.basename(unquote(parsed_url.path))
                
                if not filename or filename == '':
                    logger.warning(f"无法从URL解析文件名: {url}")
                    filename = f"download_{abs(hash(url)) % 10000}.dat"
            
            # 清理文件名
            filename = self._sanitize_filename(filename)
            
            # 生成完整保存路径
            save_path = self.save_dir / filename
            
            # 检查文件是否已存在
            if save_path.exists():
                logger.info(f"文件已存在，跳过下载: {save_path}")
                return save_path
            
            # 创建保存目录
            try:
                os.makedirs(os.path.dirname(save_path), exist_ok=True)
            except PermissionError:
                logger.error(f"没有权限创建目录: {os.path.dirname(save_path)}")
                return None
            except OSError as e:
                logger.error(f"创建目录失败: {os.path.dirname(save_path)}, 错误: {str(e)}")
                return None
            
            # 安全策略：统一使用HTTP下载，不区分OSS和普通URL
            # OSS预签名URL将作为普通HTTPS链接处理
            if 'aliyuncs.com' in url or 'oss-' in url:
                logger.info("检测到OSS链接，将作为普通HTTP链接处理")
            
            # 统一HTTP下载（包括OSS预签名URL和普通HTTP链接）
            for retry in range(self.max_retries):
                try:
                    # 设置请求头来模拟浏览器
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                        'Accept': '*/*',
                        'Accept-Encoding': 'gzip, deflate, br',
                        'Connection': 'keep-alive'
                    }
                    
                    response = requests.get(url, headers=headers, timeout=self.timeout, stream=True, allow_redirects=True)
                    response.raise_for_status()
                    
                    # 检查响应内容类型
                    content_type = response.headers.get('content-type', '').lower()
                    if 'text/html' in content_type:
                        logger.warning(f"响应内容可能是HTML页面而非文件: {url}")
                    
                    # 如果原始文件名没有扩展名，尝试从响应头获取
                    if not os.path.splitext(filename)[1]:  # 检查是否没有扩展名
                        header_filename = self._extract_filename_from_headers(response.headers)
                        if header_filename:
                            # 更新文件名和保存路径
                            filename = self._sanitize_filename(header_filename)
                            save_path = self.save_dir / filename
                            logger.info(f"从响应头获取到文件名: {filename}")
                    
                    # 获取文件大小
                    total_size = int(response.headers.get('content-length', 0))
                    if total_size > 0:
                        logger.info(f"文件大小: {total_size / 1024 / 1024:.2f} MB")
                    
                    # 检查磁盘空间
                    if total_size > 0:
                        free_space = self._get_free_space(self.save_dir)
                        if free_space < total_size * 1.1:  # 预留10%空间
                            logger.error(f"磁盘空间不足，需要 {total_size / 1024 / 1024:.2f} MB，可用 {free_space / 1024 / 1024:.2f} MB")
                            return None
                    
                    # 写入文件
                    downloaded_size = 0
                    try:
                        with open(save_path, 'wb') as f:
                            for chunk in response.iter_content(chunk_size=8192):
                                if chunk:
                                    f.write(chunk)
                                    downloaded_size += len(chunk)
                    except IOError as e:
                        logger.error(f"写入文件失败: {str(e)}")
                        # 删除部分下载的文件
                        if save_path.exists():
                            try:
                                save_path.unlink()
                            except Exception:
                                pass
                        raise
                    
                    # 验证下载完整性
                    if total_size > 0 and downloaded_size != total_size:
                        logger.error(f"下载不完整，期望 {total_size} 字节，实际 {downloaded_size} 字节")
                        if save_path.exists():
                            save_path.unlink()
                        return None
                    
                    # 检查文件是否为空
                    if save_path.stat().st_size == 0:
                        logger.error(f"下载的文件为空: {save_path}")
                        save_path.unlink()
                        return None
                    
                    logger.info(f"资源下载完成: {save_path} ({downloaded_size / 1024 / 1024:.2f} MB)")
                    return save_path
                    
                except requests.exceptions.Timeout:
                    logger.warning(f"下载超时 (尝试 {retry+1}/{self.max_retries})")
                    if retry < self.max_retries - 1:
                        time.sleep(2 ** retry)  # 指数退避
                except requests.exceptions.ConnectionError as e:
                    logger.warning(f"连接错误 (尝试 {retry+1}/{self.max_retries}): {str(e)}")
                    if retry < self.max_retries - 1:
                        time.sleep(2 ** retry)  # 指数退避
                except requests.exceptions.HTTPError as e:
                    if e.response.status_code == 404:
                        logger.error(f"文件不存在 (404): {url}")
                        return None
                    elif e.response.status_code == 403:
                        logger.error(f"访问被禁止 (403): {url}")
                        return None
                    else:
                        logger.warning(f"HTTP错误 {e.response.status_code} (尝试 {retry+1}/{self.max_retries}): {str(e)}")
                        if retry < self.max_retries - 1:
                            time.sleep(2 ** retry)
                except requests.exceptions.RequestException as e:
                    logger.warning(f"HTTP下载失败 (尝试 {retry+1}/{self.max_retries}): {str(e)}")
                    if retry < self.max_retries - 1:
                        time.sleep(2 ** retry)
                    elif retry == self.max_retries - 1:
                        logger.error(f"所有重试均失败: {url}")
                        return None
            
            logger.error("所有下载方法均失败")
            return None
            
        except MemoryError:
            logger.error("内存不足，无法下载大文件")
            return None
        except Exception as e:
            logger.error(f"下载资源失败: {str(e)}", exc_info=True)
            return None
    
    
    def _download_from_oss(self, url: str, save_path: str) -> Optional[str]:
        """从阿里云OSS下载资源
        
        安全策略：仅支持有效的预签名URL，不进行凭据存储和自动重新签名
        
        Args:
            url: OSS预签名URL
            save_path: 保存路径
            
        Returns:
            保存的文件路径，失败返回None
        """
        logger.info("使用安全策略：仅支持有效的OSS预签名URL下载，不进行自动重新签名")
        return self._download_directly(url, save_path)
    
    def _download_directly(self, url: str, save_path: str) -> Optional[str]:
        """直接通过HTTP请求下载，安全策略：仅支持有效的预签名URL
        
        Args:
            url: 有效的HTTP/HTTPS资源URL
            save_path: 保存路径
            
        Returns:
            保存的文件路径，失败或URL过期返回None
        """
        try:
            logger.info(f"尝试HTTP下载: {url}")
            
            # 确保目录存在
            os.makedirs(os.path.dirname(os.path.abspath(save_path)), exist_ok=True)
            
            # 设置请求头来模拟浏览器
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': '*/*',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive'
            }
            
            # 安全策略：直接使用提供的URL，不进行凭据操作
            response = requests.get(url, headers=headers, timeout=self.timeout, stream=True)
            response.raise_for_status()
            
            # 写入文件
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            logger.info(f"HTTP下载成功: {save_path}")
            return save_path
        
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 403:
                logger.error(f"OSS下载链接已过期或无权限 (403): {url}")
                logger.error("请提供有效的预签名下载链接")
            else:
                logger.error(f"HTTP错误 {e.response.status_code}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"HTTP下载失败: {str(e)}")
            return None
    
    def _parse_oss_url(self, url: str) -> Tuple[Optional[str], Optional[str]]:
        """解析OSS URL，提取bucket和object信息
        
        Args:
            url: OSS资源URL
            
        Returns:
            (bucket_name, object_key)元组
        """
        try:
            parsed_url = urlparse(url)
            
            # 尝试从主机名中提取bucket信息
            host_parts = parsed_url.netloc.split('.')
            if len(host_parts) >= 1 and ('aliyuncs.com' in parsed_url.netloc or 'oss-' in parsed_url.netloc):
                bucket_name = host_parts[0]
                
                # 处理路径中的对象名
                object_key = parsed_url.path
                if object_key.startswith('/'):
                    object_key = object_key[1:]  # 移除开头的斜杠
                
                # URL解码
                object_key = unquote(object_key)
                
                # 从查询参数中尝试获取key
                query_params = dict(parse_qsl(parsed_url.query))
                if 'key' in query_params:
                    object_key = unquote(query_params['key'])
                
                # 处理编码的反斜杠
                # OSS对象键可能包含%5C (编码的反斜杠)
                # 有些系统使用反斜杠分隔路径，但OSS标准是正斜杠
                if '%5C' in object_key:
                    object_key = object_key.replace('%5C', '/')
                elif '\\' in object_key:
                    # 保持原始路径格式以便直接使用
                    # 但OSS API可能需要正斜杠
                    pass
                
                logger.debug(f"解析的对象键: {object_key}")
                return bucket_name, object_key
            
            return None, None
        except Exception as e:
            logger.error(f"解析OSS URL时出错: {str(e)}")
            return None, None
    
    def _fix_filename_encoding(self, filename: str) -> str:
        """修复文件名编码问题
        
        Args:
            filename: 原始文件名
            
        Returns:
            修复编码后的文件名
        """
        try:
            # 如果文件名已经是URL编码的，先解码
            if '%' in filename:
                try:
                    filename = unquote(filename)
                    logger.debug(f"URL解码后的文件名: {filename}")
                except Exception as e:
                    logger.warning(f"URL解码失败: {e}")
            
            # 尝试多种编码方式解决中文乱码问题
            encoding_attempts = [
                # 如果是Latin-1编码的中文（常见的HTTP头编码问题）
                lambda f: f.encode('latin-1').decode('utf-8'),
                # 如果是GBK编码
                lambda f: f.encode('latin-1').decode('gbk'),
                # 如果是GB2312编码
                lambda f: f.encode('latin-1').decode('gb2312'),
                # 直接使用原文件名
                lambda f: f
            ]
            
            for attempt in encoding_attempts:
                try:
                    decoded_filename = attempt(filename)
                    # 检查解码后的文件名是否包含有效字符（避免出现乱码）
                    if decoded_filename and not any(ord(c) > 65535 for c in decoded_filename):
                        logger.debug(f"编码修复成功: {filename} -> {decoded_filename}")
                        return decoded_filename
                except (UnicodeDecodeError, UnicodeEncodeError, AttributeError) as e:
                    logger.debug(f"编码尝试失败: {e}")
                    continue
            
            # 如果所有编码尝试都失败，返回原文件名
            logger.warning(f"无法修复文件名编码，使用原文件名: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"修复文件名编码时出错: {e}")
            return filename

    def _get_free_space(self, path) -> int:
        """获取指定路径的可用磁盘空间
        
        Args:
            path: 目录路径
            
        Returns:
            可用字节数
        """
        try:
            import shutil
            _, _, free = shutil.disk_usage(path)
            return free
        except Exception as e:
            logger.warning(f"获取磁盘空间失败: {str(e)}")
            return float('inf')  # 如果获取失败，假设有足够空间
    
    def _sanitize_filename(self, filename: str) -> str:
        """清理文件名中的非法字符
        
        Args:
            filename: 原始文件名
            
        Returns:
            清理后的安全文件名
        """
        try:
            if not filename or not filename.strip():
                return "download_file.dat"
                
            # 移除或替换Windows/Linux文件系统不支持的字符
            # Windows禁用字符: < > : " | ? * \ /
            # 以及控制字符 (ASCII 0-31)
            illegal_chars = r'[<>:"|?*\\/]'
            
            # 替换非法字符为下划线
            sanitized = re.sub(illegal_chars, '_', filename)
            
            # 移除控制字符
            sanitized = re.sub(r'[\x00-\x1f\x7f]', '', sanitized)
            
            # 移除文件名开头和结尾的空格和点号
            sanitized = sanitized.strip(' .')
            
            # 避免Windows保留文件名
            windows_reserved = {
                'CON', 'PRN', 'AUX', 'NUL',
                'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
                'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
            }
            
            name_part, ext_part = os.path.splitext(sanitized)
            if name_part.upper() in windows_reserved:
                name_part = f"{name_part}_file"
                sanitized = name_part + ext_part
            
            # 确保文件名不为空
            if not sanitized.strip():
                sanitized = "download_file.dat"
            
            # 限制文件名长度（保留扩展名）
            max_length = 200  # 大多数文件系统支持255字符，保留一些余量
            if len(sanitized) > max_length:
                name_part, ext_part = os.path.splitext(sanitized)
                name_part = name_part[:max_length - len(ext_part)]
                sanitized = name_part + ext_part
            
            logger.debug(f"文件名清理: {filename} -> {sanitized}")
            return sanitized
            
        except Exception as e:
            logger.error(f"清理文件名时出错: {e}")
            # 如果清理失败，返回一个安全的默认文件名
            return f"download_{abs(hash(str(filename))) % 10000}.dat"

    def _extract_filename_from_headers(self, headers) -> Optional[str]:
        """从HTTP响应头中提取文件名
        
        Args:
            headers: HTTP响应头
            
        Returns:
            提取的文件名，失败返回None
        """
        try:
            # 1. 尝试从Content-Disposition头获取
            content_disposition = headers.get('Content-Disposition', '')
            if content_disposition:
                # 优先处理 filename*=UTF-8''xxx 格式
                utf8_match = re.search(r'filename\*\s*=\s*UTF-8\'\'([^;\r\n]+)', content_disposition)
                if utf8_match:
                    filename = unquote(utf8_match.group(1).strip())
                    logger.debug(f"从Content-Disposition头获取UTF-8编码文件名: {filename}")
                    return filename
                
                # 处理普通 filename="xxx" 或 filename=xxx 格式，支持等号周围的空格
                filename_match = re.search(r'filename\s*=\s*["\']?([^;\r\n]*?)["\']?\s*(?:;|$)', content_disposition)
                if filename_match:
                    filename = filename_match.group(1).strip()
                    
                    # 尝试解决中文编码问题
                    filename = self._fix_filename_encoding(filename)
                    
                    # 清理文件名中的非法字符
                    filename = self._sanitize_filename(filename)
                    
                    logger.debug(f"从Content-Disposition头获取文件名: {filename}")
                    return filename
            
            # 2. 尝试从Content-Type头推断扩展名
            content_type = headers.get('Content-Type', '').lower()
            if content_type:
                # 常见MIME类型到扩展名的映射
                mime_to_ext = {
                    'application/zip': '.zip',
                    'application/x-zip-compressed': '.zip',
                    'text/csv': '.csv',
                    'application/csv': '.csv',
                    'text/plain': '.txt',
                    'application/json': '.json',
                    'application/xml': '.xml',
                    'text/xml': '.xml',
                    'application/pdf': '.pdf',
                    'image/jpeg': '.jpg',
                    'image/png': '.png',
                    'image/gif': '.gif',
                    'application/octet-stream': '.bin',
                    'application/vnd.ms-excel': '.xls',
                    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': '.xlsx'
                }
                
                # 提取主要的MIME类型（忽略charset等参数）
                main_type = content_type.split(';')[0].strip()
                if main_type in mime_to_ext:
                    ext = mime_to_ext[main_type]
                    logger.debug(f"从Content-Type头推断扩展名: {ext}")
                    return f"download_{hash(str(headers)) % 10000}{ext}"
            
            return None
        except Exception as e:
            logger.warning(f"从响应头提取文件名失败: {str(e)}")
            return None

    # generate_presigned_url 函数已移除 - 基于安全策略禁用 