#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据验证模块
提供数据完整性和有效性验证功能
"""
import logging
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional

logger = logging.getLogger(__name__)

class DataValidator:
    """数据验证器类"""
    
    def __init__(self):
        """初始化数据验证器"""
        # 坐标有效范围
        self.coordinate_ranges = {
            'longitude': (-180.0, 180.0),
            'latitude': (-90.0, 90.0)
        }
        
        # 水质指标合理范围（用于异常值检测）
        self.indicator_ranges = {
            'cod': (0, 1000),      # COD: 0-1000 mg/L
            'nh3n': (0, 100),      # 氨氮: 0-100 mg/L
            'tp': (0, 50),         # 总磷: 0-50 mg/L
            'tn': (0, 200),        # 总氮: 0-200 mg/L
            'do': (0, 20),         # 溶解氧: 0-20 mg/L
            'ph': (0, 14),         # pH: 0-14
            'turbidity': (0, 1000), # 浊度: 0-1000 NTU
            'chla': (0, 500),      # 叶绿素a: 0-500 μg/L
        }
    
    def validate_dataframe(self, df: pd.DataFrame) -> Dict:
        """验证DataFrame的完整性和有效性
        
        Args:
            df: 待验证的DataFrame
            
        Returns:
            验证结果字典
        """
        try:
            logger.info("开始验证DataFrame")
            
            validation_result = {
                'is_valid': True,
                'errors': [],
                'warnings': [],
                'statistics': {},
                'data_quality': {}
            }
            
            # 基础结构验证
            self._validate_structure(df, validation_result)
            
            # 坐标数据验证
            self._validate_coordinates(df, validation_result)
            
            # 指标数据验证
            self._validate_indicators(df, validation_result)
            
            # 数据完整性验证
            self._validate_completeness(df, validation_result)
            
            # 生成数据质量报告
            self._generate_quality_report(df, validation_result)
            
            # 设置总体验证状态
            validation_result['is_valid'] = len(validation_result['errors']) == 0
            
            if validation_result['is_valid']:
                logger.info("数据验证通过")
            else:
                logger.warning(f"数据验证失败，错误数: {len(validation_result['errors'])}")
            
            return validation_result
            
        except Exception as e:
            logger.error(f"数据验证异常: {str(e)}")
            return {
                'is_valid': False,
                'errors': [f"验证过程异常: {str(e)}"],
                'warnings': [],
                'statistics': {},
                'data_quality': {}
            }
    
    def _validate_structure(self, df: pd.DataFrame, result: Dict):
        """验证DataFrame结构"""
        try:
            # 检查DataFrame是否为空
            if df is None or len(df) == 0:
                result['errors'].append("DataFrame为空")
                return
            
            # 检查必要列
            required_columns = ['longitude', 'latitude']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                result['errors'].append(f"缺少必要列: {missing_columns}")
            
            # 检查是否有指标列
            coord_columns = ['index', 'longitude', 'latitude']
            indicator_columns = [col for col in df.columns if col not in coord_columns]
            
            if len(indicator_columns) == 0:
                result['warnings'].append("未发现水质指标列")
            
            # 记录基础统计
            result['statistics']['total_records'] = len(df)
            result['statistics']['total_columns'] = len(df.columns)
            result['statistics']['indicator_columns'] = len(indicator_columns)
            
        except Exception as e:
            result['errors'].append(f"结构验证失败: {str(e)}")
    
    def _validate_coordinates(self, df: pd.DataFrame, result: Dict):
        """验证坐标数据"""
        try:
            if 'longitude' not in df.columns or 'latitude' not in df.columns:
                return
            
            # 检查坐标数据类型
            if not pd.api.types.is_numeric_dtype(df['longitude']):
                result['errors'].append("经度列不是数值类型")
            
            if not pd.api.types.is_numeric_dtype(df['latitude']):
                result['errors'].append("纬度列不是数值类型")
            
            # 检查缺失值
            lon_missing = df['longitude'].isna().sum()
            lat_missing = df['latitude'].isna().sum()
            
            if lon_missing > 0:
                result['warnings'].append(f"经度缺失值: {lon_missing}条")
            
            if lat_missing > 0:
                result['warnings'].append(f"纬度缺失值: {lat_missing}条")
            
            # 检查坐标范围
            valid_data = df.dropna(subset=['longitude', 'latitude'])
            if len(valid_data) > 0:
                # 经度范围检查
                lon_out_of_range = (
                    (valid_data['longitude'] < self.coordinate_ranges['longitude'][0]) |
                    (valid_data['longitude'] > self.coordinate_ranges['longitude'][1])
                ).sum()
                
                if lon_out_of_range > 0:
                    result['errors'].append(f"经度超出有效范围[-180,180]: {lon_out_of_range}条")
                
                # 纬度范围检查
                lat_out_of_range = (
                    (valid_data['latitude'] < self.coordinate_ranges['latitude'][0]) |
                    (valid_data['latitude'] > self.coordinate_ranges['latitude'][1])
                ).sum()
                
                if lat_out_of_range > 0:
                    result['errors'].append(f"纬度超出有效范围[-90,90]: {lat_out_of_range}条")
                
                # 记录坐标统计
                result['statistics']['coordinate_stats'] = {
                    'longitude_range': [float(valid_data['longitude'].min()), float(valid_data['longitude'].max())],
                    'latitude_range': [float(valid_data['latitude'].min()), float(valid_data['latitude'].max())],
                    'valid_coordinates': len(valid_data)
                }
            
        except Exception as e:
            result['errors'].append(f"坐标验证失败: {str(e)}")
    
    def _validate_indicators(self, df: pd.DataFrame, result: Dict):
        """验证指标数据"""
        try:
            coord_columns = ['index', 'longitude', 'latitude']
            indicator_columns = [col for col in df.columns if col not in coord_columns]
            
            if len(indicator_columns) == 0:
                return
            
            indicator_stats = {}
            
            for col in indicator_columns:
                col_stats = {
                    'total_count': len(df),
                    'valid_count': 0,
                    'missing_count': 0,
                    'negative_count': 0,
                    'outlier_count': 0,
                    'range': [None, None]
                }
                
                # 检查数据类型
                if not pd.api.types.is_numeric_dtype(df[col]):
                    result['warnings'].append(f"指标列 {col} 不是数值类型")
                    continue
                
                # 统计缺失值
                col_stats['missing_count'] = df[col].isna().sum()
                col_stats['valid_count'] = df[col].notna().sum()
                
                if col_stats['valid_count'] == 0:
                    result['warnings'].append(f"指标列 {col} 全部为缺失值")
                    continue
                
                valid_data = df[col].dropna()
                
                # 检查负值
                col_stats['negative_count'] = (valid_data < 0).sum()
                if col_stats['negative_count'] > 0:
                    result['warnings'].append(f"指标 {col} 存在 {col_stats['negative_count']} 个负值")
                
                # 记录数值范围
                col_stats['range'] = [float(valid_data.min()), float(valid_data.max())]
                
                # 检查异常值（如果有预定义范围）
                col_lower = col.lower()
                if col_lower in self.indicator_ranges:
                    valid_range = self.indicator_ranges[col_lower]
                    outliers = (
                        (valid_data < valid_range[0]) |
                        (valid_data > valid_range[1])
                    ).sum()
                    
                    col_stats['outlier_count'] = outliers
                    if outliers > 0:
                        result['warnings'].append(
                            f"指标 {col} 存在 {outliers} 个可能的异常值（超出合理范围 {valid_range}）"
                        )
                
                indicator_stats[col] = col_stats
            
            result['statistics']['indicator_stats'] = indicator_stats
            
        except Exception as e:
            result['errors'].append(f"指标验证失败: {str(e)}")
    
    def _validate_completeness(self, df: pd.DataFrame, result: Dict):
        """验证数据完整性"""
        try:
            total_records = len(df)
            
            # 完全有效记录（所有列都不为空）
            complete_records = df.dropna().shape[0]
            
            # 坐标完整记录
            if 'longitude' in df.columns and 'latitude' in df.columns:
                coordinate_complete = df.dropna(subset=['longitude', 'latitude']).shape[0]
            else:
                coordinate_complete = 0
            
            # 计算完整性比例
            completeness = {
                'total_records': total_records,
                'complete_records': complete_records,
                'coordinate_complete': coordinate_complete,
                'completeness_ratio': complete_records / total_records if total_records > 0 else 0,
                'coordinate_completeness_ratio': coordinate_complete / total_records if total_records > 0 else 0
            }
            
            result['statistics']['completeness'] = completeness
            
            # 生成警告
            if completeness['completeness_ratio'] < 0.8:
                result['warnings'].append(f"数据完整性较低: {completeness['completeness_ratio']:.1%}")
            
            if completeness['coordinate_completeness_ratio'] < 0.9:
                result['warnings'].append(f"坐标完整性较低: {completeness['coordinate_completeness_ratio']:.1%}")
            
        except Exception as e:
            result['errors'].append(f"完整性验证失败: {str(e)}")
    
    def _generate_quality_report(self, df: pd.DataFrame, result: Dict):
        """生成数据质量报告"""
        try:
            quality_score = 100
            
            # 扣分项
            error_penalty = len(result['errors']) * 20
            warning_penalty = len(result['warnings']) * 5
            
            # 完整性奖励
            if 'completeness' in result['statistics']:
                completeness_bonus = result['statistics']['completeness']['completeness_ratio'] * 20
            else:
                completeness_bonus = 0
            
            quality_score = max(0, quality_score - error_penalty - warning_penalty + completeness_bonus)
            
            # 质量等级
            if quality_score >= 90:
                quality_level = "优秀"
            elif quality_score >= 80:
                quality_level = "良好"
            elif quality_score >= 60:
                quality_level = "一般"
            else:
                quality_level = "较差"
            
            result['data_quality'] = {
                'score': quality_score,
                'level': quality_level,
                'error_count': len(result['errors']),
                'warning_count': len(result['warnings'])
            }
            
        except Exception as e:
            logger.warning(f"生成质量报告失败: {str(e)}")
    
    def validate_coordinates_only(self, longitude: float, latitude: float) -> bool:
        """验证单个坐标点
        
        Args:
            longitude: 经度
            latitude: 纬度
            
        Returns:
            是否有效
        """
        try:
            # 检查数值有效性
            if not np.isfinite(longitude) or not np.isfinite(latitude):
                return False
            
            # 检查坐标范围
            lon_valid = (self.coordinate_ranges['longitude'][0] <= longitude <= 
                        self.coordinate_ranges['longitude'][1])
            lat_valid = (self.coordinate_ranges['latitude'][0] <= latitude <= 
                        self.coordinate_ranges['latitude'][1])
            
            return lon_valid and lat_valid
            
        except:
            return False