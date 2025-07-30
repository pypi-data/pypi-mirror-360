#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
基于密度的边界检测算法
使用点密度信息来确定插值区域边界
"""
import logging
import numpy as np
from scipy.spatial import distance_matrix
from typing import Callable, Optional

logger = logging.getLogger(__name__)

def compute_density_based_boundary(points: np.ndarray, density_threshold: float = 0.5) -> Callable:
    """
    基于密度的边界检测算法（简化版本，不依赖sklearn）
    
    Args:
        points: 二维数组，每行为一个点的坐标 (x, y)
        density_threshold: 密度阈值，控制边界的紧密度(0-1)
        
    Returns:
        边界掩码创建函数
    """
    try:
        logger.debug(f"计算密度边界，输入点数: {len(points)}, 密度阈值: {density_threshold}")
        
        if len(points) < 3:
            logger.warning("点数少于3个，返回全真掩码函数")
            return lambda x, y: np.ones_like(x, dtype=bool)
        
        # 计算每个点的局部密度
        local_density = _calculate_local_density(points)
        
        # 确定密度阈值
        density_threshold_value = np.percentile(local_density, density_threshold * 100)
        
        logger.debug(f"密度阈值值: {density_threshold_value}")
        
        def create_boundary_mask(grid_x: np.ndarray, grid_y: np.ndarray) -> np.ndarray:
            """
            创建基于密度的边界掩码
            
            Args:
                grid_x: 网格X坐标
                grid_y: 网格Y坐标
                
            Returns:
                布尔掩码数组
            """
            try:
                # 将网格坐标转换为点集
                grid_points = np.column_stack((grid_x.ravel(), grid_y.ravel()))
                
                # 对每个网格点，计算到最近数据点的距离和密度
                distances_to_data, nearest_indices = _simple_knn_distances(points, grid_points, k=1)
                
                # 获取最近数据点的密度
                nearest_densities = local_density[nearest_indices.ravel()]
                
                # 基于密度和距离创建掩码
                max_distance = np.percentile(distances_to_data.ravel(), 90)
                distance_mask = distances_to_data.ravel() < max_distance
                density_mask = nearest_densities > density_threshold_value
                
                # 组合掩码
                combined_mask = distance_mask & density_mask
                
                mask = combined_mask.reshape(grid_x.shape)
                logger.debug(f"密度掩码创建完成，内部点数: {mask.sum()}")
                
                return mask
                
            except Exception as e:
                logger.error(f"创建密度掩码失败: {str(e)}")
                return np.ones_like(grid_x, dtype=bool)
        
        return create_boundary_mask
        
    except Exception as e:
        logger.error(f"密度边界计算失败: {str(e)}")
        return lambda x, y: np.ones_like(x, dtype=bool)

def _calculate_local_density(points: np.ndarray, n_neighbors: Optional[int] = None) -> np.ndarray:
    """
    计算每个点的局部密度
    
    Args:
        points: 点坐标数组
        n_neighbors: 邻居数量，None时自动确定
        
    Returns:
        局部密度数组
    """
    try:
        n_points = len(points)
        
        if n_neighbors is None:
            n_neighbors = min(5, n_points - 1)
        else:
            n_neighbors = min(n_neighbors, n_points - 1)
        
        if n_neighbors <= 0:
            return np.ones(n_points)
        
        # 计算距离矩阵
        dist_matrix = distance_matrix(points, points)
        
        # 计算每个点的局部密度
        local_density = np.zeros(n_points)
        
        for i in range(n_points):
            # 排除自己（距离为0）
            distances = dist_matrix[i][dist_matrix[i] > 0]
            
            if len(distances) >= n_neighbors:
                # 第k近邻距离
                kth_distance = np.partition(distances, n_neighbors-1)[n_neighbors-1]
                
                # 使用数值稳定的倒数计算密度
                min_distance = np.finfo(float).eps * 1000
                safe_distance = max(kth_distance, min_distance)
                local_density[i] = 1.0 / safe_distance
            else:
                # 当邻居不足时，给一个合理的默认密度值
                local_density[i] = 1.0
        
        return local_density
        
    except Exception as e:
        logger.error(f"计算局部密度失败: {str(e)}")
        return np.ones(len(points))

def _simple_knn_distances(data_points: np.ndarray, query_points: np.ndarray, k: int = 1) -> tuple:
    """
    简化的KNN距离计算，不依赖sklearn
    
    Args:
        data_points: 数据点
        query_points: 查询点
        k: 邻居数量
        
    Returns:
        (距离数组, 索引数组)
    """
    try:
        n_query = len(query_points)
        distances = np.zeros((n_query, k))
        indices = np.zeros((n_query, k), dtype=int)
        
        for i, query_point in enumerate(query_points):
            # 计算到所有数据点的距离
            dists = np.sqrt(np.sum((data_points - query_point)**2, axis=1))
            
            # 找到k个最近的点
            sorted_indices = np.argsort(dists)
            distances[i] = dists[sorted_indices[:k]]
            indices[i] = sorted_indices[:k]
        
        return distances, indices
        
    except Exception as e:
        logger.error(f"KNN距离计算失败: {str(e)}")
        return np.zeros((len(query_points), k)), np.zeros((len(query_points), k), dtype=int)

def adaptive_density_threshold(points: np.ndarray) -> float:
    """
    根据点分布自适应确定密度阈值
    
    Args:
        points: 点坐标数组
        
    Returns:
        推荐的密度阈值
    """
    try:
        n_points = len(points)
        
        # 根据点数量调整阈值
        if n_points < 10:
            return 0.2  # 点少时使用较低阈值
        elif n_points < 50:
            return 0.3
        elif n_points < 100:
            return 0.4
        else:
            return 0.5  # 点多时使用标准阈值
            
    except Exception as e:
        logger.debug(f"自适应密度阈值计算失败: {str(e)}")
        return 0.5

def validate_density_boundary(mask_func: Callable, test_points: np.ndarray) -> bool:
    """
    验证密度边界函数的有效性
    
    Args:
        mask_func: 掩码函数
        test_points: 测试点集
        
    Returns:
        是否有效
    """
    try:
        if len(test_points) < 3:
            return True
        
        # 创建测试网格
        x_range = [test_points[:, 0].min(), test_points[:, 0].max()]
        y_range = [test_points[:, 1].min(), test_points[:, 1].max()]
        
        test_x = np.linspace(x_range[0], x_range[1], 20)
        test_y = np.linspace(y_range[0], y_range[1], 20)
        test_X, test_Y = np.meshgrid(test_x, test_y)
        
        # 测试掩码函数
        test_mask = mask_func(test_X, test_Y)
        
        # 检查结果合理性
        if not isinstance(test_mask, np.ndarray):
            return False
        
        if test_mask.shape != test_X.shape:
            return False
        
        # 应该有一些内部点和一些外部点
        inside_ratio = np.sum(test_mask) / test_mask.size
        return 0.1 <= inside_ratio <= 0.9
        
    except Exception as e:
        logger.debug(f"验证密度边界失败: {str(e)}")
        return False