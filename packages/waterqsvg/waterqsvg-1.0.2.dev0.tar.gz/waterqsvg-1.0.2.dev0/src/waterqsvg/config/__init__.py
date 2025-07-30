"""
配置模块

包含水质指标配置和国标分级标准
"""

from .indicators import WATER_QUALITY_INDICATORS, get_indicator_info

__all__ = [
    'WATER_QUALITY_INDICATORS',
    'get_indicator_info'
]