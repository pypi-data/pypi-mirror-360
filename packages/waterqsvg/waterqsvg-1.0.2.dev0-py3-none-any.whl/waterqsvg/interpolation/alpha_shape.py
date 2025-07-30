#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Alpha Shape边界检测算法
用于计算点集的Alpha Shape边界，能够处理凹陷形状
"""
import logging
import numpy as np
from scipy.spatial import Delaunay
from typing import Optional

logger = logging.getLogger(__name__)

def compute_alpha_shape(points: np.ndarray, alpha: Optional[float] = None) -> np.ndarray:
    """
    计算Alpha Shape边界，能够处理凹陷形状
    
    Args:
        points: 二维数组，每行为一个点的坐标 (x, y)
        alpha: Alpha参数，控制边界的"紧密度"，None时自动计算
        
    Returns:
        边界点的坐标数组
    """
    try:
        logger.debug(f"计算Alpha Shape，输入点数: {len(points)}")
        
        if len(points) < 3:
            logger.warning("点数少于3个，返回原始点集")
            return points
        
        # 计算Delaunay三角剖分
        tri = Delaunay(points)
        
        # 自动计算alpha值
        if alpha is None:
            alpha = _estimate_alpha(points)
            logger.debug(f"自动估算的alpha值: {alpha}")
        
        # 找到边界边
        boundary_edges = _find_boundary_edges(points, tri, alpha)
        
        if not boundary_edges:
            logger.warning("未找到有效边界，回退到凸包")
            from .convex_hull import compute_convex_hull
            return compute_convex_hull(points)
        
        # 构建边界路径
        boundary_coords = _build_boundary_path(points, boundary_edges)
        
        logger.debug(f"Alpha Shape计算完成，边界点数: {len(boundary_coords)}")
        return boundary_coords
        
    except Exception as e:
        logger.error(f"Alpha Shape计算失败: {str(e)}")
        # 回退到凸包
        try:
            from .convex_hull import compute_convex_hull
            return compute_convex_hull(points)
        except:
            return points

def _estimate_alpha(points: np.ndarray) -> float:
    """
    基于点之间的距离分布自动估算合适的alpha值
    
    Args:
        points: 点坐标数组
        
    Returns:
        估算的alpha值
    """
    try:
        # 计算所有点对之间的距离
        distances = []
        n_points = len(points)
        
        # 采样策略：如果点太多，只计算部分距离以提高效率
        if n_points > 100:
            # 随机采样100个点计算距离
            indices = np.random.choice(n_points, min(100, n_points), replace=False)
            sample_points = points[indices]
        else:
            sample_points = points
        
        for i in range(len(sample_points)):
            for j in range(i+1, len(sample_points)):
                dist = np.sqrt(np.sum((sample_points[i] - sample_points[j])**2))
                distances.append(dist)
        
        if not distances:
            return 1.0
        
        # 使用距离的30%百分位数作为alpha值
        # 这个值通常能够很好地平衡边界的紧密度和连续性
        alpha = np.percentile(distances, 30)
        
        # 确保alpha值在合理范围内
        alpha = max(alpha, np.min(distances) * 1.5)  # 不能太小
        alpha = min(alpha, np.max(distances) * 0.5)  # 不能太大
        
        return alpha
        
    except Exception as e:
        logger.warning(f"估算alpha值失败: {str(e)}")
        return 1.0

def _find_boundary_edges(points: np.ndarray, tri: Delaunay, alpha: float) -> list:
    """
    找到满足alpha条件的边界边
    
    Args:
        points: 点坐标数组
        tri: Delaunay三角剖分结果
        alpha: Alpha参数
        
    Returns:
        边界边列表
    """
    boundary_edges = []
    
    try:
        # 遍历所有三角形
        for simplex in tri.simplices:
            # 计算三角形的外接圆半径
            triangle_points = points[simplex]
            circumradius = _calculate_circumradius(triangle_points)
            
            # 如果外接圆半径小于alpha，则保留这个三角形的边
            if circumradius is not None and circumradius < alpha:
                for i in range(3):
                    edge = (simplex[i], simplex[(i+1) % 3])
                    boundary_edges.append(edge)
        
        # 找到只出现一次的边（真正的边界边）
        edge_count = {}
        for edge in boundary_edges:
            edge_sorted = tuple(sorted(edge))
            edge_count[edge_sorted] = edge_count.get(edge_sorted, 0) + 1
        
        # 只保留出现一次的边
        true_boundary_edges = [edge for edge, count in edge_count.items() if count == 1]
        
        return true_boundary_edges
        
    except Exception as e:
        logger.error(f"查找边界边失败: {str(e)}")
        return []

def _calculate_circumradius(triangle_points: np.ndarray) -> Optional[float]:
    """
    计算三角形的外接圆半径
    
    Args:
        triangle_points: 三角形三个顶点的坐标
        
    Returns:
        外接圆半径，计算失败返回None
    """
    try:
        # 计算三条边的长度
        a = np.linalg.norm(triangle_points[1] - triangle_points[0])
        b = np.linalg.norm(triangle_points[2] - triangle_points[1])
        c = np.linalg.norm(triangle_points[0] - triangle_points[2])
        
        # 检查退化三角形
        min_edge_length = np.finfo(float).eps * 100
        if min(a, b, c) < min_edge_length:
            return None
        
        # 计算半周长
        s = (a + b + c) / 2
        
        # 使用海伦公式计算面积
        area_squared = s * (s - a) * (s - b) * (s - c)
        
        # 检查负数（由于数值误差可能出现）
        if area_squared <= 0:
            return None
        
        area = np.sqrt(area_squared)
        
        # 使用相对阈值检查最小面积
        max_edge = max(a, b, c)
        min_area_threshold = np.finfo(float).eps * 100 * max_edge ** 2
        
        if area <= min_area_threshold:
            return None
        
        # 计算外接圆半径
        circumradius = (a * b * c) / (4 * area)
        
        # 检查结果有效性
        if not np.isfinite(circumradius) or circumradius <= 0:
            return None
        
        return circumradius
        
    except Exception as e:
        logger.debug(f"计算外接圆半径失败: {str(e)}")
        return None

def _build_boundary_path(points: np.ndarray, boundary_edges: list) -> np.ndarray:
    """
    从边界边构建连续的边界路径
    
    Args:
        points: 点坐标数组
        boundary_edges: 边界边列表
        
    Returns:
        边界点坐标数组
    """
    try:
        if not boundary_edges:
            return np.array([])
        
        boundary_points = []
        remaining_edges = list(boundary_edges)
        
        # 从第一条边开始
        current_edge = remaining_edges.pop(0)
        boundary_points.extend([current_edge[0], current_edge[1]])
        
        # 尝试连接后续边
        while remaining_edges:
            last_point = boundary_points[-1]
            found_next = False
            
            for i, edge in enumerate(remaining_edges):
                if edge[0] == last_point:
                    boundary_points.append(edge[1])
                    remaining_edges.pop(i)
                    found_next = True
                    break
                elif edge[1] == last_point:
                    boundary_points.append(edge[0])
                    remaining_edges.pop(i)
                    found_next = True
                    break
            
            if not found_next:
                # 如果无法连接，尝试新的起始点
                if remaining_edges:
                    next_edge = remaining_edges.pop(0)
                    boundary_points.extend([next_edge[0], next_edge[1]])
        
        # 转换为坐标数组
        if boundary_points:
            boundary_coords = points[boundary_points]
            return boundary_coords
        else:
            return np.array([])
        
    except Exception as e:
        logger.error(f"构建边界路径失败: {str(e)}")
        return np.array([])

def validate_alpha_shape_result(boundary_coords: np.ndarray, original_points: np.ndarray) -> bool:
    """
    验证Alpha Shape结果的合理性
    
    Args:
        boundary_coords: 边界坐标
        original_points: 原始点集
        
    Returns:
        是否合理
    """
    try:
        if len(boundary_coords) == 0:
            return False
        
        # 检查边界点数是否合理（不应超过原始点数）
        if len(boundary_coords) > len(original_points):
            return False
        
        # 检查边界是否包含了原始点的范围
        orig_x_range = [original_points[:, 0].min(), original_points[:, 0].max()]
        orig_y_range = [original_points[:, 1].min(), original_points[:, 1].max()]
        
        bound_x_range = [boundary_coords[:, 0].min(), boundary_coords[:, 0].max()]
        bound_y_range = [boundary_coords[:, 1].min(), boundary_coords[:, 1].max()]
        
        # 边界应该包含原始点的范围（允许一些误差）
        tolerance = 1e-6
        x_contained = (bound_x_range[0] <= orig_x_range[0] + tolerance and 
                      bound_x_range[1] >= orig_x_range[1] - tolerance)
        y_contained = (bound_y_range[0] <= orig_y_range[0] + tolerance and 
                      bound_y_range[1] >= orig_y_range[1] - tolerance)
        
        return x_contained and y_contained
        
    except Exception as e:
        logger.debug(f"验证Alpha Shape结果失败: {str(e)}")
        return False