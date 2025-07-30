#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
凸包算法模块
计算点集的凸包边界
"""
import logging
import numpy as np
from scipy.spatial import ConvexHull
from typing import Optional
from matplotlib.path import Path

logger = logging.getLogger(__name__)

def compute_convex_hull(points: np.ndarray) -> np.ndarray:
    """
    计算散点数据的凸包，返回凸包顶点坐标
    
    Args:
        points: 二维数组，每行为一个点的坐标 (x, y)
        
    Returns:
        凸包顶点坐标数组
    """
    try:
        logger.debug(f"计算凸包，输入点数: {len(points)}")
        
        if len(points) < 3:
            logger.warning("点数少于3个，无法构成凸包")
            return points
        
        # 使用scipy计算凸包
        hull = ConvexHull(points)
        hull_points = points[hull.vertices]
        
        logger.debug(f"凸包计算完成，顶点数: {len(hull_points)}")
        return hull_points
        
    except Exception as e:
        logger.error(f"凸包计算失败: {str(e)}")
        return points

def create_convex_hull_mask(grid_x: np.ndarray, grid_y: np.ndarray, hull_points: np.ndarray) -> np.ndarray:
    """
    创建凸包掩码，标记网格中哪些点在凸包内
    
    Args:
        grid_x: 网格X坐标
        grid_y: 网格Y坐标  
        hull_points: 凸包顶点坐标
        
    Returns:
        布尔掩码数组
    """
    try:
        logger.debug("创建凸包掩码")
        
        if len(hull_points) < 3:
            logger.warning("凸包顶点数少于3个，创建全真掩码")
            return np.ones_like(grid_x, dtype=bool)
        
        # 将网格坐标转换为点集
        points = np.column_stack((grid_x.ravel(), grid_y.ravel()))
        
        # 创建凸包路径
        hull_path = Path(hull_points)
        
        # 检查每个网格点是否在凸包内
        mask = hull_path.contains_points(points)
        
        # 重新塑形为网格形状
        mask = mask.reshape(grid_x.shape)
        
        logger.debug(f"凸包掩码创建完成，内部点数: {mask.sum()}")
        return mask
        
    except Exception as e:
        logger.error(f"创建凸包掩码失败: {str(e)}")
        return np.ones_like(grid_x, dtype=bool)

def validate_convex_hull(hull_points: np.ndarray, original_points: np.ndarray) -> bool:
    """
    验证凸包结果的合理性
    
    Args:
        hull_points: 凸包顶点
        original_points: 原始点集
        
    Returns:
        是否合理
    """
    try:
        if len(hull_points) < 3:
            return False
        
        # 检查凸包顶点数是否合理
        if len(hull_points) > len(original_points):
            return False
        
        # 检查所有原始点是否都在凸包内或边界上
        hull_path = Path(hull_points)
        all_inside = hull_path.contains_points(original_points, radius=1e-10)
        
        # 至少90%的点应该在凸包内
        inside_ratio = np.sum(all_inside) / len(original_points)
        
        return inside_ratio >= 0.9
        
    except Exception as e:
        logger.debug(f"验证凸包失败: {str(e)}")
        return False

def get_convex_hull_area(hull_points: np.ndarray) -> float:
    """
    计算凸包面积
    
    Args:
        hull_points: 凸包顶点坐标
        
    Returns:
        凸包面积
    """
    try:
        if len(hull_points) < 3:
            return 0.0
        
        # 使用鞋带公式计算多边形面积
        x = hull_points[:, 0]
        y = hull_points[:, 1]
        
        # 确保多边形闭合
        if not (x[0] == x[-1] and y[0] == y[-1]):
            x = np.append(x, x[0])
            y = np.append(y, y[0])
        
        area = 0.5 * abs(sum(x[i] * y[i+1] - x[i+1] * y[i] for i in range(len(x)-1)))
        
        return area
        
    except Exception as e:
        logger.debug(f"计算凸包面积失败: {str(e)}")
        return 0.0

def get_convex_hull_bounds(hull_points: np.ndarray) -> tuple:
    """
    获取凸包的边界坐标
    
    Args:
        hull_points: 凸包顶点坐标
        
    Returns:
        (min_x, min_y, max_x, max_y)
    """
    try:
        if len(hull_points) == 0:
            return (0, 0, 0, 0)
        
        min_x = float(hull_points[:, 0].min())
        max_x = float(hull_points[:, 0].max())
        min_y = float(hull_points[:, 1].min())
        max_y = float(hull_points[:, 1].max())
        
        return (min_x, min_y, max_x, max_y)
        
    except Exception as e:
        logger.debug(f"获取凸包边界失败: {str(e)}")
        return (0, 0, 0, 0)