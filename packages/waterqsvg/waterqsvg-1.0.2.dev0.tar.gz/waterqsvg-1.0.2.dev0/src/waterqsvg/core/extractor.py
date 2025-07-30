#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据提取模块
提供ZIP文件解压和数据提取功能，包含安全检查和编码修复
"""
import os
import logging
import zipfile
import tempfile
import shutil
import chardet
from typing import List, Optional, Dict
from pathlib import Path

logger = logging.getLogger(__name__)

class ZipExtractor:
    """ZIP文件提取器"""
    
    def __init__(self, extract_dir: str = None):
        """初始化ZIP文件提取器
        
        Args:
            extract_dir: 解压目录，如果为None则使用临时目录
        """
        if extract_dir is None:
            self.extract_dir = tempfile.mkdtemp(prefix='svg_generator_')
        else:
            self.extract_dir = extract_dir
            os.makedirs(self.extract_dir, exist_ok=True)
        
        self._extracted_files = {}  # 缓存已提取的文件
        logger.info(f"初始化解压器，解压目录: {self.extract_dir}")
    
    def extract(self, zip_path: str) -> Optional[str]:
        """解压ZIP文件
        
        Args:
            zip_path: ZIP文件路径
            
        Returns:
            解压后的目录路径，失败返回None
        """
        try:
            logger.info(f"开始解压ZIP文件: {zip_path}")
            
            # 验证ZIP文件
            if not self._validate_zip_file(zip_path):
                return None
            
            # 创建解压子目录
            zip_name = Path(zip_path).stem
            extract_subdir = os.path.join(self.extract_dir, zip_name)
            os.makedirs(extract_subdir, exist_ok=True)
            
            # 解压文件
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # 安全检查，防止路径穿越攻击
                for member in zip_ref.namelist():
                    if self._is_safe_path(member):
                        zip_ref.extract(member, extract_subdir)
                    else:
                        logger.warning(f"跳过不安全的路径: {member}")
            
            # 修复文件编码
            self._fix_file_encodings(extract_subdir)
            
            # 缓存提取的文件列表
            self._extracted_files[zip_path] = self._list_extracted_files(extract_subdir)
            
            logger.info(f"ZIP文件解压成功: {extract_subdir}")
            return extract_subdir
            
        except Exception as e:
            logger.error(f"解压ZIP文件失败: {str(e)}")
            return None
    
    def find_file(self, zip_path: str, pattern: str) -> Optional[str]:
        """在解压后的文件中查找匹配的文件
        
        Args:
            zip_path: ZIP文件路径
            pattern: 文件名模式（支持通配符）
            
        Returns:
            找到的文件路径，未找到返回None
        """
        try:
            if zip_path not in self._extracted_files:
                logger.warning(f"ZIP文件尚未解压: {zip_path}")
                return None
            
            files = self._extracted_files[zip_path]
            
            # 简单的模式匹配
            for file_path in files:
                filename = os.path.basename(file_path)
                if self._match_pattern(filename, pattern):
                    logger.info(f"找到匹配文件: {file_path}")
                    return file_path
            
            logger.warning(f"未找到匹配模式 '{pattern}' 的文件")
            return None
            
        except Exception as e:
            logger.error(f"查找文件失败: {str(e)}")
            return None
    
    def find_files(self, zip_path: str, patterns: List[str]) -> Dict[str, Optional[str]]:
        """查找多个文件
        
        Args:
            zip_path: ZIP文件路径
            patterns: 文件名模式列表
            
        Returns:
            模式到文件路径的映射字典
        """
        result = {}
        for pattern in patterns:
            result[pattern] = self.find_file(zip_path, pattern)
        return result
    
    def get_file_list(self, zip_path: str) -> List[str]:
        """获取ZIP文件中的文件列表
        
        Args:
            zip_path: ZIP文件路径
            
        Returns:
            文件路径列表
        """
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                return [f for f in zip_ref.namelist() if not f.endswith('/')]
        except Exception as e:
            logger.error(f"获取文件列表失败: {str(e)}")
            return []
    
    def _validate_zip_file(self, zip_path: str) -> bool:
        """验证ZIP文件的有效性"""
        try:
            if not os.path.exists(zip_path):
                logger.error(f"ZIP文件不存在: {zip_path}")
                return False
            
            if not zipfile.is_zipfile(zip_path):
                logger.error(f"不是有效的ZIP文件: {zip_path}")
                return False
            
            # 测试ZIP文件完整性
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.testzip()
            
            return True
            
        except Exception as e:
            logger.error(f"ZIP文件验证失败: {str(e)}")
            return False
    
    def _is_safe_path(self, path: str) -> bool:
        """检查路径是否安全，防止路径穿越攻击"""
        # 标准化路径
        normalized = os.path.normpath(path)
        
        # 检查是否包含危险的路径元素
        dangerous_patterns = ['..', '~', '/', '\\']
        
        # 检查绝对路径
        if os.path.isabs(normalized):
            return False
        
        # 检查路径穿越
        if any(pattern in normalized for pattern in dangerous_patterns[:2]):
            return False
        
        return True
    
    def _fix_file_encodings(self, directory: str):
        """修复文件编码问题"""
        try:
            for root, dirs, files in os.walk(directory):
                for file in files:
                    file_path = os.path.join(root, file)
                    
                    # 只处理文本文件
                    if self._is_text_file(file_path):
                        self._fix_single_file_encoding(file_path)
                        
        except Exception as e:
            logger.warning(f"修复文件编码失败: {str(e)}")
    
    def _is_text_file(self, file_path: str) -> bool:
        """检查是否为文本文件"""
        text_extensions = {'.txt', '.csv', '.log', '.json', '.xml', '.yml', '.yaml'}
        return Path(file_path).suffix.lower() in text_extensions
    
    def _fix_single_file_encoding(self, file_path: str):
        """修复单个文件的编码"""
        try:
            # 检测文件编码
            with open(file_path, 'rb') as f:
                raw_data = f.read()
                
            detected = chardet.detect(raw_data)
            encoding = detected.get('encoding', 'utf-8')
            
            if encoding and encoding.lower() not in ['utf-8', 'ascii']:
                # 转换为UTF-8编码
                content = raw_data.decode(encoding)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                logger.debug(f"文件编码已转换: {file_path} ({encoding} -> utf-8)")
                
        except Exception as e:
            logger.debug(f"文件编码转换失败: {file_path}, {str(e)}")
    
    def _list_extracted_files(self, directory: str) -> List[str]:
        """列出解压后的所有文件"""
        files = []
        try:
            for root, dirs, filenames in os.walk(directory):
                for filename in filenames:
                    files.append(os.path.join(root, filename))
        except Exception as e:
            logger.warning(f"列出文件失败: {str(e)}")
        
        return files
    
    def _match_pattern(self, filename: str, pattern: str) -> bool:
        """简单的文件名模式匹配"""
        import fnmatch
        return fnmatch.fnmatch(filename.lower(), pattern.lower())
    
    def cleanup(self):
        """清理解压目录"""
        try:
            if os.path.exists(self.extract_dir):
                shutil.rmtree(self.extract_dir)
                logger.info(f"已清理解压目录: {self.extract_dir}")
        except Exception as e:
            logger.warning(f"清理解压目录失败: {str(e)}")