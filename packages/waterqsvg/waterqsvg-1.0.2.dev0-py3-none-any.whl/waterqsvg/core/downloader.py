#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
资源下载模块
提供网络资源下载功能，支持阿里云OSS认证和普通HTTP下载
"""
import os
import logging
import requests
import time
from urllib.parse import urlparse, unquote
from typing import Optional, Tuple
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

logger = logging.getLogger(__name__)

class ResourceDownloader:
    """资源下载器类"""
    
    def __init__(self, download_dir: str = "./downloads"):
        """初始化资源下载器
        
        Args:
            download_dir: 下载目录路径
        """
        self.download_dir = download_dir
        self.timeout = 30  # 下载超时时间（秒）
        self.max_retries = 3  # 最大重试次数
        
        # 确保下载目录存在
        os.makedirs(self.download_dir, exist_ok=True)
        
        # 阿里云OSS配置，从环境变量获取（可选）
        self.oss_access_key_id = os.environ.get('OSS_ACCESS_KEY_ID')
        self.oss_access_key_secret = os.environ.get('OSS_ACCESS_KEY_SECRET')
        self.oss_endpoint = os.environ.get('OSS_ENDPOINT', 'oss-cn-shanghai.aliyuncs.com')
    
    def download(self, url: str, filename: Optional[str] = None) -> Optional[str]:
        """下载资源
        
        Args:
            url: 资源URL
            filename: 保存的文件名，如果为None则从URL解析
            
        Returns:
            下载后的文件路径，失败返回None
        """
        try:
            logger.info(f"开始下载资源: {url}")
            
            # 解析URL获取文件名
            if filename is None:
                parsed_url = urlparse(url)
                filename = os.path.basename(unquote(parsed_url.path))
                
                if not filename:
                    logger.warning(f"无法从URL解析文件名: {url}")
                    filename = f"download_{hash(url) % 10000}.dat"
            
            save_path = os.path.join(self.download_dir, filename)
            
            # 如果文件已存在，检查是否需要重新下载
            if os.path.exists(save_path):
                logger.info(f"文件已存在: {save_path}")
                return save_path
            
            # 尝试使用阿里云OSS下载（如果是OSS URL且配置了认证）
            if self._is_oss_url(url) and self._has_oss_config():
                try:
                    return self._download_from_oss(url, save_path)
                except Exception as e:
                    logger.warning(f"OSS下载失败，尝试普通HTTP下载: {str(e)}")
            
            # 普通HTTP下载
            return self._download_via_http(url, save_path)
            
        except Exception as e:
            logger.error(f"下载失败: {str(e)}")
            return None
    
    def _is_oss_url(self, url: str) -> bool:
        """检查是否为OSS URL"""
        return 'aliyuncs.com' in url or 'oss-' in url
    
    def _has_oss_config(self) -> bool:
        """检查是否配置了OSS认证信息"""
        return all([self.oss_access_key_id, self.oss_access_key_secret, self.oss_endpoint])
    
    def _download_from_oss(self, url: str, save_path: str) -> str:
        """从阿里云OSS下载文件"""
        try:
            import oss2
        except ImportError:
            raise ImportError("需要安装oss2库: pip install oss2")
        
        # 解析OSS URL
        parsed_url = urlparse(url)
        
        # 提取bucket名称和object key
        bucket_name = parsed_url.hostname.split('.')[0]
        object_key = parsed_url.path.lstrip('/')
        
        # 创建OSS认证和客户端
        auth = oss2.Auth(self.oss_access_key_id, self.oss_access_key_secret)
        bucket = oss2.Bucket(auth, self.oss_endpoint, bucket_name)
        
        # 下载文件
        bucket.get_object_to_file(object_key, save_path)
        logger.info(f"OSS下载成功: {save_path}")
        
        return save_path
    
    def _download_via_http(self, url: str, save_path: str) -> str:
        """通过HTTP下载文件"""
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
                
                # 获取文件大小
                total_size = int(response.headers.get('content-length', 0))
                
                # 写入文件
                downloaded_size = 0
                with open(save_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded_size += len(chunk)
                            
                            # 显示下载进度
                            if total_size > 0:
                                progress = (downloaded_size / total_size) * 100
                                if downloaded_size % (1024 * 1024) == 0:  # 每MB显示一次
                                    logger.info(f"下载进度: {progress:.1f}%")
                
                logger.info(f"HTTP下载成功: {save_path}")
                return save_path
                
            except Exception as e:
                logger.warning(f"下载失败 (重试 {retry + 1}/{self.max_retries}): {str(e)}")
                if retry < self.max_retries - 1:
                    time.sleep(2 ** retry)  # 指数退避
                else:
                    raise e
    
    def cleanup(self):
        """清理下载目录"""
        try:
            import shutil
            if os.path.exists(self.download_dir):
                shutil.rmtree(self.download_dir)
                logger.info(f"已清理下载目录: {self.download_dir}")
        except Exception as e:
            logger.warning(f"清理下载目录失败: {str(e)}")