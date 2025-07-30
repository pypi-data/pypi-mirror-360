#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据解析模块
解析INDEXS.CSV和POS.TXT文件，提取水质指标和GPS坐标数据
"""
import os
import logging
import pandas as pd
from typing import Optional, Dict, Any, List
from pathlib import Path

logger = logging.getLogger(__name__)

class DataParser:
    """数据解析器类"""
    
    def __init__(self):
        """初始化数据解析器"""
        self.supported_encodings = ['utf-8', 'gbk', 'gb2312', 'latin-1']
    
    def parse_uav_data(self, data_dir: str) -> Optional[pd.DataFrame]:
        """解析无人机数据目录，合并指标数据和GPS坐标
        
        Args:
            data_dir: 数据目录路径
            
        Returns:
            合并后的DataFrame，包含经纬度和各水质指标
        """
        try:
            logger.info(f"开始解析无人机数据目录: {data_dir}")
            
            # 查找关键文件
            indexs_file = self._find_file(data_dir, "INDEXS.CSV")
            pos_file = self._find_file(data_dir, "POS.TXT")
            
            if not indexs_file:
                logger.error("未找到INDEXS.CSV文件")
                return None
            
            if not pos_file:
                logger.error("未找到POS.TXT文件")
                return None
            
            # 解析指标数据
            indexs_data = self._parse_indexs_file(indexs_file)
            if indexs_data is None:
                return None
            
            # 解析GPS数据
            pos_data = self._parse_pos_file(pos_file)
            if pos_data is None:
                return None
            
            # 合并数据
            merged_data = self._merge_data(indexs_data, pos_data)
            
            if merged_data is not None:
                logger.info(f"数据解析成功，共 {len(merged_data)} 条记录")
                logger.info(f"数据列: {list(merged_data.columns)}")
            
            return merged_data
            
        except Exception as e:
            logger.error(f"解析无人机数据失败: {str(e)}")
            return None
    
    def parse_csv_file(self, file_path: str) -> Optional[pd.DataFrame]:
        """解析CSV文件
        
        Args:
            file_path: CSV文件路径
            
        Returns:
            DataFrame或None
        """
        try:
            logger.info(f"解析CSV文件: {file_path}")
            
            # 尝试不同编码读取文件
            for encoding in self.supported_encodings:
                try:
                    df = pd.read_csv(file_path, encoding=encoding)
                    logger.info(f"CSV文件解析成功，编码: {encoding}")
                    return df
                except UnicodeDecodeError:
                    continue
                except Exception as e:
                    logger.warning(f"编码 {encoding} 解析失败: {str(e)}")
                    continue
            
            logger.error(f"所有编码尝试失败: {file_path}")
            return None
            
        except Exception as e:
            logger.error(f"解析CSV文件失败: {str(e)}")
            return None
    
    def _find_file(self, directory: str, filename: str) -> Optional[str]:
        """在目录中查找指定文件（不区分大小写）
        
        Args:
            directory: 搜索目录
            filename: 文件名
            
        Returns:
            文件路径或None
        """
        try:
            filename_lower = filename.lower()
            
            for root, dirs, files in os.walk(directory):
                for file in files:
                    if file.lower() == filename_lower:
                        file_path = os.path.join(root, file)
                        logger.info(f"找到文件: {file_path}")
                        return file_path
            
            logger.warning(f"未找到文件: {filename}")
            return None
            
        except Exception as e:
            logger.error(f"查找文件失败: {str(e)}")
            return None
    
    def _parse_indexs_file(self, file_path: str) -> Optional[pd.DataFrame]:
        """解析INDEXS.CSV文件，提取水质指标数据
        
        Args:
            file_path: INDEXS.CSV文件路径
            
        Returns:
            包含指标数据的DataFrame
        """
        try:
            logger.info(f"解析INDEXS文件: {file_path}")
            
            # 读取CSV文件
            df = self.parse_csv_file(file_path)
            if df is None:
                return None
            
            # 检查数据完整性
            if len(df) == 0:
                logger.warning("INDEXS文件为空")
                return None
            
            # 添加索引列
            if 'index' not in df.columns:
                df['index'] = range(len(df))
            
            logger.info(f"INDEXS文件解析成功，共 {len(df)} 条记录，{len(df.columns)} 列")
            logger.debug(f"INDEXS列名: {list(df.columns)}")
            
            return df
            
        except Exception as e:
            logger.error(f"解析INDEXS文件失败: {str(e)}")
            return None
    
    def _parse_pos_file(self, file_path: str) -> Optional[pd.DataFrame]:
        """解析POS.TXT文件，提取GPS坐标数据
        
        Args:
            file_path: POS.TXT文件路径
            
        Returns:
            包含GPS坐标的DataFrame
        """
        try:
            logger.info(f"解析POS文件: {file_path}")
            
            # 首先尝试修复版本的解析方法（适用于包含文件名的格式）
            import re
            data = []
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    
                    # 使用正则表达式提取GPS信息
                    # 格式: /path/to/file.csv latitude: 31.516106 longitude: 120.267944 height: 110.27
                    pattern = r'(\d+)\.csv.*?latitude:\s*([\d.-]+).*?longitude:\s*([\d.-]+)'
                    match = re.search(pattern, line)
                    
                    if match:
                        index = int(match.group(1))
                        latitude = float(match.group(2))
                        longitude = float(match.group(3))
                        
                        data.append({
                            'index': index,
                            'longitude': longitude,
                            'latitude': latitude
                        })
                    else:
                        logger.warning(f"第{line_num}行格式不正确: {line}")
            
            if data:
                df = pd.DataFrame(data)
                logger.info(f"POS文件解析成功（修复版本），共 {len(df)} 条有效记录")
                return df
            
            # 如果修复版本失败，尝试原来的CSV解析方法
            logger.info("尝试标准CSV格式解析")
            
            # 尝试不同的分隔符
            separators = ['\t', ',', ' ', ';']
            df = None
            
            for sep in separators:
                try:
                    for encoding in self.supported_encodings:
                        try:
                            df = pd.read_csv(file_path, sep=sep, encoding=encoding, header=None)
                            if len(df.columns) >= 3:  # 至少需要3列：索引、经度、纬度
                                logger.info(f"POS文件解析成功，分隔符: '{sep}', 编码: {encoding}")
                                break
                        except:
                            continue
                    if df is not None and len(df.columns) >= 3:
                        break
                except:
                    continue
            
            if df is None or len(df.columns) < 3:
                logger.error("POS文件格式不正确，无法解析")
                return None
            
            # 设置列名
            if len(df.columns) == 3:
                df.columns = ['index', 'longitude', 'latitude']
            elif len(df.columns) > 3:
                df.columns = ['index', 'longitude', 'latitude'] + [f'extra_{i}' for i in range(len(df.columns) - 3)]
            
            # 数据类型转换
            try:
                df['index'] = pd.to_numeric(df['index'], errors='coerce').astype('Int64')
                df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')
                df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
            except Exception as e:
                logger.warning(f"数据类型转换警告: {str(e)}")
            
            # 删除无效行
            initial_count = len(df)
            df = df.dropna(subset=['longitude', 'latitude'])
            final_count = len(df)
            
            if initial_count != final_count:
                logger.warning(f"删除 {initial_count - final_count} 条无效GPS记录")
            
            if len(df) == 0:
                logger.error("POS文件中没有有效的GPS数据")
                return None
            
            logger.info(f"POS文件解析成功，共 {len(df)} 条有效GPS记录")
            
            return df
            
        except Exception as e:
            logger.error(f"解析POS文件失败: {str(e)}")
            return None
    
    def _merge_data(self, indexs_data: pd.DataFrame, pos_data: pd.DataFrame) -> Optional[pd.DataFrame]:
        """合并指标数据和GPS数据
        
        Args:
            indexs_data: 指标数据
            pos_data: GPS数据
            
        Returns:
            合并后的DataFrame
        """
        try:
            logger.info("开始合并指标数据和GPS数据")
            
            # 检查索引列
            if 'index' not in indexs_data.columns:
                indexs_data['index'] = range(len(indexs_data))
            
            if 'index' not in pos_data.columns:
                pos_data['index'] = range(len(pos_data))
            
            # 按索引合并数据
            merged = pd.merge(
                indexs_data, 
                pos_data[['index', 'longitude', 'latitude']], 
                on='index', 
                how='inner'
            )
            
            if len(merged) == 0:
                logger.error("合并后没有数据，可能索引不匹配")
                return None
            
            # 验证合并结果
            missing_gps = len(indexs_data) - len(merged)
            if missing_gps > 0:
                logger.warning(f"有 {missing_gps} 条指标数据缺少对应的GPS坐标")
            
            logger.info(f"数据合并成功，最终 {len(merged)} 条记录")
            
            return merged
            
        except Exception as e:
            logger.error(f"合并数据失败: {str(e)}")
            return None
    
    def get_indicator_columns(self, df: pd.DataFrame) -> List[str]:
        """获取水质指标列名
        
        Args:
            df: 数据DataFrame
            
        Returns:
            指标列名列表
        """
        if df is None:
            return []
        
        # 排除非指标列
        non_indicator_cols = ['index', 'longitude', 'latitude', 'lat', 'lon']
        indicator_cols = [col for col in df.columns if col not in non_indicator_cols]
        
        logger.info(f"识别到 {len(indicator_cols)} 个水质指标: {indicator_cols}")
        
        return indicator_cols