#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
颜色映射器模块
提供颜色映射创建和应用功能
"""
import logging
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.colors import LinearSegmentedColormap, ListedColormap, Normalize, BoundaryNorm
from typing import Optional, Union, List, Tuple, Dict, Any

logger = logging.getLogger(__name__)

def create_colormap(colormap_name: str = 'jet') -> Union[LinearSegmentedColormap, ListedColormap]:
    """
    创建颜色映射
    
    Args:
        colormap_name: 颜色映射名称
        
    Returns:
        颜色映射对象
    """
    try:
        logger.debug(f"创建颜色映射: {colormap_name}")
        
        # 标准matplotlib颜色映射
        standard_cmaps = [
            'jet', 'viridis', 'plasma', 'inferno', 'magma', 'cividis',
            'Blues', 'Greens', 'Reds', 'YlOrRd', 'YlGnBu', 'RdYlBu',
            'coolwarm', 'bwr', 'seismic', 'rainbow', 'hot', 'cool'
        ]
        
        if colormap_name in standard_cmaps:
            return plt.cm.get_cmap(colormap_name)
        
        # 自定义颜色映射
        custom_cmaps = {
            'water_quality': _create_water_quality_colormap(),
            'depth': _create_depth_colormap(),
            'temperature': _create_temperature_colormap(),
            'pollution': _create_pollution_colormap()
        }
        
        if colormap_name in custom_cmaps:
            return custom_cmaps[colormap_name]
        
        # 如果找不到，使用默认的jet
        logger.warning(f"未知的颜色映射 '{colormap_name}'，使用默认的 'jet'")
        return plt.cm.get_cmap('jet')
        
    except Exception as e:
        logger.error(f"创建颜色映射失败: {str(e)}")
        return plt.cm.get_cmap('jet')

def _create_water_quality_colormap() -> LinearSegmentedColormap:
    """创建水质专用颜色映射"""
    colors = [
        '#1E90FF',  # 蓝色 - 优秀
        '#00FF7F',  # 绿色 - 良好
        '#FFFF00',  # 黄色 - 一般
        '#FFA500',  # 橙色 - 较差
        '#FF0000'   # 红色 - 差
    ]
    return LinearSegmentedColormap.from_list('water_quality', colors)

def _create_depth_colormap() -> LinearSegmentedColormap:
    """创建深度专用颜色映射"""
    colors = [
        '#87CEEB',  # 浅蓝 - 浅水
        '#4682B4',  # 钢蓝 - 中等
        '#191970',  # 午夜蓝 - 深水
        '#000080'   # 海军蓝 - 最深
    ]
    return LinearSegmentedColormap.from_list('depth', colors)

def _create_temperature_colormap() -> LinearSegmentedColormap:
    """创建温度专用颜色映射"""
    colors = [
        '#0000FF',  # 蓝色 - 冷
        '#00FFFF',  # 青色
        '#00FF00',  # 绿色
        '#FFFF00',  # 黄色
        '#FF8000',  # 橙色
        '#FF0000'   # 红色 - 热
    ]
    return LinearSegmentedColormap.from_list('temperature', colors)

def _create_pollution_colormap() -> LinearSegmentedColormap:
    """创建污染程度颜色映射"""
    colors = [
        '#00FF00',  # 绿色 - 无污染
        '#ADFF2F',  # 黄绿
        '#FFFF00',  # 黄色 - 轻度污染
        '#FF8C00',  # 橙色 - 中度污染
        '#FF4500',  # 红橙 - 重度污染
        '#8B0000'   # 暗红 - 严重污染
    ]
    return LinearSegmentedColormap.from_list('pollution', colors)

def apply_colormap(
    data: np.ndarray,
    colormap: Union[str, LinearSegmentedColormap, ListedColormap],
    value_range: Optional[Tuple[float, float]] = None,
    alpha: float = 1.0
) -> np.ndarray:
    """
    将颜色映射应用到数据
    
    Args:
        data: 输入数据数组
        colormap: 颜色映射
        value_range: 数值范围 (vmin, vmax)
        alpha: 透明度
        
    Returns:
        彩色图像数组 (RGBA)
    """
    try:
        logger.debug("应用颜色映射到数据")
        
        # 获取颜色映射对象
        if isinstance(colormap, str):
            cmap = create_colormap(colormap)
        else:
            cmap = colormap
        
        # 确定数值范围
        if value_range is None:
            valid_data = data[~np.isnan(data)]
            if len(valid_data) > 0:
                vmin, vmax = float(valid_data.min()), float(valid_data.max())
            else:
                vmin, vmax = 0, 1
        else:
            vmin, vmax = value_range
        
        # 创建归一化对象
        norm = Normalize(vmin=vmin, vmax=vmax)
        
        # 应用颜色映射
        colored_data = cmap(norm(data))
        
        # 设置透明度
        if alpha != 1.0:
            colored_data[..., 3] *= alpha
        
        # 处理NaN值（设为透明）
        nan_mask = np.isnan(data)
        colored_data[nan_mask, 3] = 0
        
        return colored_data
        
    except Exception as e:
        logger.error(f"应用颜色映射失败: {str(e)}")
        # 返回灰度图像
        return np.stack([data, data, data, np.ones_like(data)], axis=-1)

def create_discrete_colormap(
    colors: List[str],
    labels: Optional[List[str]] = None
) -> Tuple[ListedColormap, BoundaryNorm]:
    """
    创建离散颜色映射
    
    Args:
        colors: 颜色列表
        labels: 标签列表
        
    Returns:
        (颜色映射, 边界归一化)
    """
    try:
        logger.debug(f"创建离散颜色映射，颜色数: {len(colors)}")
        
        # 创建列表颜色映射
        cmap = ListedColormap(colors)
        
        # 创建边界
        bounds = list(range(len(colors) + 1))
        norm = BoundaryNorm(bounds, cmap.N)
        
        return cmap, norm
        
    except Exception as e:
        logger.error(f"创建离散颜色映射失败: {str(e)}")
        # 返回默认颜色映射
        default_colors = ['blue', 'green', 'yellow', 'orange', 'red']
        cmap = ListedColormap(default_colors[:len(colors)] if len(colors) <= 5 else default_colors)
        bounds = list(range(len(default_colors) + 1))
        norm = BoundaryNorm(bounds, cmap.N)
        return cmap, norm

def get_colormap_info(colormap_name: str) -> Dict[str, Any]:
    """
    获取颜色映射信息
    
    Args:
        colormap_name: 颜色映射名称
        
    Returns:
        颜色映射信息字典
    """
    try:
        cmap = create_colormap(colormap_name)
        
        info = {
            'name': colormap_name,
            'type': type(cmap).__name__,
            'colors': cmap.N if hasattr(cmap, 'N') else 256,
            'is_segmented': isinstance(cmap, LinearSegmentedColormap),
            'is_listed': isinstance(cmap, ListedColormap)
        }
        
        # 获取颜色样本
        if hasattr(cmap, 'colors'):
            info['color_samples'] = cmap.colors[:10]  # 前10个颜色
        else:
            # 生成颜色样本
            samples = np.linspace(0, 1, 10)
            info['color_samples'] = [cmap(x) for x in samples]
        
        return info
        
    except Exception as e:
        logger.error(f"获取颜色映射信息失败: {str(e)}")
        return {'name': colormap_name, 'error': str(e)}

def create_colorbar_data(
    colormap: Union[str, LinearSegmentedColormap, ListedColormap],
    value_range: Tuple[float, float],
    height: int = 256,
    width: int = 20
) -> np.ndarray:
    """
    创建颜色条数据
    
    Args:
        colormap: 颜色映射
        value_range: 数值范围
        height: 颜色条高度
        width: 颜色条宽度
        
    Returns:
        颜色条图像数组
    """
    try:
        # 获取颜色映射对象
        if isinstance(colormap, str):
            cmap = create_colormap(colormap)
        else:
            cmap = colormap
        
        # 创建数值数组
        vmin, vmax = value_range
        values = np.linspace(vmin, vmax, height)
        data = np.tile(values.reshape(-1, 1), (1, width))
        
        # 应用颜色映射
        colored_data = apply_colormap(data, cmap, value_range)
        
        # 翻转Y轴（颜色条通常是底部小值，顶部大值）
        colored_data = np.flipud(colored_data)
        
        return colored_data
        
    except Exception as e:
        logger.error(f"创建颜色条数据失败: {str(e)}")
        # 返回空白颜色条
        return np.ones((height, width, 4))

def validate_colormap(colormap: Union[str, LinearSegmentedColormap, ListedColormap]) -> bool:
    """
    验证颜色映射的有效性
    
    Args:
        colormap: 颜色映射
        
    Returns:
        是否有效
    """
    try:
        if isinstance(colormap, str):
            cmap = create_colormap(colormap)
        else:
            cmap = colormap
        
        # 测试颜色映射
        test_data = np.array([0, 0.5, 1.0])
        colors = cmap(test_data)
        
        # 检查输出格式
        if colors.shape != (3, 4):  # 应该是3个点，每个点4个通道(RGBA)
            return False
        
        # 检查颜色值范围
        if np.any(colors < 0) or np.any(colors > 1):
            return False
        
        return True
        
    except Exception as e:
        logger.debug(f"颜色映射验证失败: {str(e)}")
        return False

def list_available_colormaps() -> Dict[str, List[str]]:
    """
    列出所有可用的颜色映射
    
    Returns:
        颜色映射分类字典
    """
    try:
        return {
            'standard': [
                'jet', 'viridis', 'plasma', 'inferno', 'magma', 'cividis',
                'Blues', 'Greens', 'Reds', 'YlOrRd', 'YlGnBu', 'RdYlBu',
                'coolwarm', 'bwr', 'seismic', 'rainbow', 'hot', 'cool'
            ],
            'custom': [
                'water_quality', 'depth', 'temperature', 'pollution'
            ],
            'sequential': [
                'viridis', 'plasma', 'inferno', 'magma', 'cividis',
                'Blues', 'Greens', 'Reds', 'YlOrRd', 'YlGnBu'
            ],
            'diverging': [
                'coolwarm', 'bwr', 'seismic', 'RdYlBu'
            ],
            'qualitative': [
                'rainbow', 'jet'
            ]
        }
        
    except Exception as e:
        logger.error(f"列出颜色映射失败: {str(e)}")
        return {'error': str(e)}