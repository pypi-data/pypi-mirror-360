#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
布局计算器模块
提供图形布局的自动计算功能
"""
import logging
from typing import Dict, Any, Tuple

logger = logging.getLogger(__name__)

def calculate_optimal_layout(
    image_width: int,
    image_height: int,
    has_title: bool = False,
    has_colorbar: bool = False,
    has_legend: bool = False,
    margin_factor: float = 0.05
) -> Dict[str, Any]:
    """
    计算最优布局参数
    
    Args:
        image_width: 图像宽度
        image_height: 图像高度  
        has_title: 是否有标题
        has_colorbar: 是否有颜色条
        has_legend: 是否有图例
        margin_factor: 边距因子
        
    Returns:
        布局参数字典
    """
    try:
        logger.debug(f"计算布局，图像尺寸: {image_width}x{image_height}")
        
        # 计算纵横比
        aspect_ratio = image_height / image_width if image_width > 0 else 1.0
        
        # 基础边距
        base_margin = margin_factor
        
        # 计算各部分所需空间
        title_space = 0.08 if has_title else 0.02
        colorbar_space = 0.12 if has_colorbar else 0.0
        legend_space = 0.15 if has_legend else 0.0
        right_space = max(colorbar_space, legend_space)
        
        # 根据纵横比调整布局
        if aspect_ratio > 2.0:  # 极窄长图像
            left = base_margin * 0.5
            bottom = base_margin
            width = 1.0 - left - base_margin * 0.5 - right_space
            height = 1.0 - bottom - title_space
        elif aspect_ratio > 1.5:  # 窄长图像
            left = base_margin * 0.6
            bottom = base_margin * 1.2
            width = 1.0 - left - base_margin * 0.6 - right_space
            height = 1.0 - bottom - title_space
        elif aspect_ratio < 0.5:  # 极宽扁图像
            left = base_margin * 1.5
            bottom = base_margin * 2.0
            width = 1.0 - left - base_margin * 1.5 - right_space
            height = 1.0 - bottom - title_space
        elif aspect_ratio < 0.7:  # 宽扁图像
            left = base_margin * 1.2
            bottom = base_margin * 1.6
            width = 1.0 - left - base_margin * 1.2 - right_space
            height = 1.0 - bottom - title_space
        else:  # 接近正方形
            left = base_margin
            bottom = base_margin * 1.5
            width = 1.0 - left - base_margin - right_space
            height = 1.0 - bottom - title_space
        
        # 确保布局参数在合理范围内
        left = max(left, 0.01)
        bottom = max(bottom, 0.01)
        width = max(width, 0.3)
        height = max(height, 0.3)
        
        # 边界检查
        if left + width > 0.99:
            width = 0.99 - left
        if bottom + height > 0.99:
            height = 0.99 - bottom
        
        # 计算字体大小
        font_sizes = _calculate_font_sizes(image_width, image_height)
        
        layout = {
            'left': left,
            'bottom': bottom, 
            'width': width,
            'height': height,
            'aspect_ratio': aspect_ratio,
            'title_space': title_space,
            'right_space': right_space,
            **font_sizes
        }
        
        logger.debug(f"布局计算完成: {layout}")
        
        return layout
        
    except Exception as e:
        logger.error(f"布局计算失败: {str(e)}")
        # 返回默认布局
        return {
            'left': 0.1,
            'bottom': 0.1,
            'width': 0.8,
            'height': 0.8,
            'aspect_ratio': 1.0,
            'title_fontsize': 16,
            'label_fontsize': 12,
            'tick_fontsize': 10
        }

def _calculate_font_sizes(image_width: int, image_height: int) -> Dict[str, int]:
    """
    根据图像尺寸计算字体大小
    
    Args:
        image_width: 图像宽度
        image_height: 图像高度
        
    Returns:
        字体大小字典
    """
    try:
        # 计算基准尺寸
        base_size = min(image_width, image_height)
        
        # 计算缩放因子
        if base_size <= 400:
            scale_factor = 0.8
        elif base_size <= 800:
            scale_factor = 1.0
        elif base_size <= 1200:
            scale_factor = 1.2
        else:
            scale_factor = 1.4
        
        # 基础字体大小
        base_font = 12
        
        font_sizes = {
            'title_fontsize': int(base_font * scale_factor * 1.4),
            'label_fontsize': int(base_font * scale_factor),
            'tick_fontsize': int(base_font * scale_factor * 0.9),
            'legend_fontsize': int(base_font * scale_factor * 0.8),
            'title_pad': int(20 * scale_factor)
        }
        
        return font_sizes
        
    except Exception as e:
        logger.debug(f"字体大小计算失败: {str(e)}")
        return {
            'title_fontsize': 16,
            'label_fontsize': 12,
            'tick_fontsize': 10,
            'legend_fontsize': 10,
            'title_pad': 20
        }

def calculate_colorbar_layout(
    main_layout: Dict[str, Any],
    colorbar_width: float = 0.03,
    colorbar_pad: float = 0.02
) -> Dict[str, float]:
    """
    计算颜色条布局
    
    Args:
        main_layout: 主图布局
        colorbar_width: 颜色条宽度
        colorbar_pad: 颜色条间距
        
    Returns:
        颜色条布局参数
    """
    try:
        left = main_layout['left'] + main_layout['width'] + colorbar_pad
        bottom = main_layout['bottom']
        width = colorbar_width
        height = main_layout['height']
        
        return {
            'left': left,
            'bottom': bottom,
            'width': width,
            'height': height
        }
        
    except Exception as e:
        logger.debug(f"颜色条布局计算失败: {str(e)}")
        return {
            'left': 0.85,
            'bottom': 0.1,
            'width': 0.03,
            'height': 0.8
        }

def calculate_legend_layout(
    main_layout: Dict[str, Any],
    legend_width: float = 0.15,
    legend_pad: float = 0.02
) -> Dict[str, Any]:
    """
    计算图例布局
    
    Args:
        main_layout: 主图布局
        legend_width: 图例宽度
        legend_pad: 图例间距
        
    Returns:
        图例布局参数
    """
    try:
        # 图例位置（bbox_to_anchor格式）
        x = main_layout['left'] + main_layout['width'] + legend_pad
        y = main_layout['bottom'] + main_layout['height']
        
        return {
            'bbox_to_anchor': (x, y),
            'loc': 'upper left',
            'width': legend_width
        }
        
    except Exception as e:
        logger.debug(f"图例布局计算失败: {str(e)}")
        return {
            'bbox_to_anchor': (1.02, 1.0),
            'loc': 'upper left',
            'width': 0.15
        }

def optimize_layout_for_aspect_ratio(
    layout: Dict[str, Any],
    target_aspect_ratio: float
) -> Dict[str, Any]:
    """
    根据目标纵横比优化布局
    
    Args:
        layout: 当前布局
        target_aspect_ratio: 目标纵横比
        
    Returns:
        优化后的布局
    """
    try:
        current_aspect = layout['height'] / layout['width']
        
        if abs(current_aspect - target_aspect_ratio) < 0.1:
            return layout  # 已经接近目标比例
        
        optimized = layout.copy()
        
        if current_aspect > target_aspect_ratio:
            # 当前太高，需要降低高度或增加宽度
            adjustment = 0.1
            optimized['height'] *= (1 - adjustment)
            optimized['bottom'] += adjustment * layout['height'] / 2
        else:
            # 当前太宽，需要增加高度或降低宽度
            adjustment = 0.1
            optimized['width'] *= (1 - adjustment)
            optimized['left'] += adjustment * layout['width'] / 2
        
        return optimized
        
    except Exception as e:
        logger.debug(f"布局优化失败: {str(e)}")
        return layout

def validate_layout(layout: Dict[str, Any]) -> bool:
    """
    验证布局参数的有效性
    
    Args:
        layout: 布局参数
        
    Returns:
        是否有效
    """
    try:
        required_keys = ['left', 'bottom', 'width', 'height']
        
        # 检查必需键
        for key in required_keys:
            if key not in layout:
                logger.error(f"布局缺少必需参数: {key}")
                return False
        
        # 检查数值范围
        for key in required_keys:
            value = layout[key]
            if not isinstance(value, (int, float)) or value < 0 or value > 1:
                logger.error(f"布局参数超出有效范围[0,1]: {key}={value}")
                return False
        
        # 检查布局是否超出边界
        if layout['left'] + layout['width'] > 1:
            logger.error("布局宽度超出边界")
            return False
        
        if layout['bottom'] + layout['height'] > 1:
            logger.error("布局高度超出边界")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"布局验证失败: {str(e)}")
        return False