#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SVG图片生成模块
创建纯净版插值热力图的SVG格式输出
"""
import logging
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from typing import Optional, Tuple, Dict, Any
from pathlib import Path

from .layout_calculator import calculate_optimal_layout
from .color_mapper import create_colormap, apply_colormap

logger = logging.getLogger(__name__)

# 设置matplotlib使用SVG后端
matplotlib.use('Agg')

class SVGMapGenerator:
    """SVG地图生成器类"""
    
    def __init__(self, 
                 figsize: Optional[Tuple[float, float]] = None,
                 dpi: int = 300,
                 transparent_bg: bool = True):
        """
        初始化SVG地图生成器
        
        Args:
            figsize: 图形尺寸 (width, height)
            dpi: 分辨率
            transparent_bg: 是否使用透明背景
        """
        self.figsize = figsize or (10, 8)
        self.dpi = dpi
        self.transparent_bg = transparent_bg
        
        # 设置matplotlib参数
        self._setup_matplotlib()
    
    def _setup_matplotlib(self):
        """设置matplotlib参数"""
        # 尝试设置中文字体
        try:
            import matplotlib.font_manager as fm
            
            # 尝试常见的中文字体
            chinese_fonts = [
                'SimHei',  # 黑体
                'Microsoft YaHei',  # 微软雅黑
                'SimSun',  # 宋体
                'Arial Unicode MS',  # Unicode字体
                'Noto Sans CJK SC',  # Google Noto字体
                'WenQuanYi Micro Hei',  # 文泉驿微米黑
                'DejaVu Sans'  # 默认字体
            ]
            
            available_fonts = [f.name for f in fm.fontManager.ttflist]
            selected_font = 'DejaVu Sans'  # 默认字体
            
            for font in chinese_fonts:
                if font in available_fonts:
                    selected_font = font
                    break
            
            plt.rcParams.update({
                'font.size': 12,
                'font.family': 'sans-serif',
                'font.sans-serif': [selected_font],
                'axes.unicode_minus': False,
                'figure.dpi': self.dpi,
                'savefig.dpi': self.dpi,
                'savefig.format': 'svg'
            })
            
            logger.info(f"使用字体: {selected_font}")
            
        except Exception as e:
            logger.warning(f"字体设置失败，使用默认字体: {e}")
            plt.rcParams.update({
                'font.size': 12,
                'font.family': 'sans-serif',
                'axes.unicode_minus': False,
                'figure.dpi': self.dpi,
                'savefig.dpi': self.dpi,
                'savefig.format': 'svg'
            })
    
    def generate_svg(self,
                     grid_values: np.ndarray,
                     grid_x: np.ndarray, 
                     grid_y: np.ndarray,
                     save_path: str,
                     colormap: str = 'jet',
                     value_range: Optional[Tuple[float, float]] = None,
                     title: Optional[str] = None) -> bool:
        """
        生成SVG热力图
        
        Args:
            grid_values: 插值网格数据
            grid_x: 网格X坐标
            grid_y: 网格Y坐标  
            save_path: 保存路径
            colormap: 颜色映射名称
            value_range: 数值范围 (vmin, vmax)
            title: 图片标题
            
        Returns:
            是否成功
        """
        try:
            logger.info(f"生成SVG图片: {save_path}")
            
            # 数据验证
            if not self._validate_data(grid_values, grid_x, grid_y):
                return False
            
            # 计算布局
            layout = calculate_optimal_layout(
                grid_x.shape[1], grid_x.shape[0], 
                has_title=title is not None
            )
            
            # 创建图形
            fig, ax = self._create_figure(layout)
            
            # 绘制热力图
            self._draw_heatmap(ax, grid_values, grid_x, grid_y, colormap, value_range)
            
            # 设置标题
            if title:
                self._set_title(ax, title, layout)
            
            # 保存SVG
            success = self._save_svg(fig, save_path)
            
            # 清理
            plt.close(fig)
            
            if success:
                logger.info(f"SVG图片生成成功: {save_path}")
            
            return success
            
        except Exception as e:
            logger.error(f"生成SVG图片失败: {str(e)}")
            return False
    
    def _validate_data(self, grid_values: np.ndarray, grid_x: np.ndarray, grid_y: np.ndarray) -> bool:
        """验证输入数据"""
        try:
            if grid_values is None or grid_x is None or grid_y is None:
                logger.error("输入数据为空")
                return False
            
            if grid_values.shape != grid_x.shape or grid_values.shape != grid_y.shape:
                logger.error("网格数据形状不匹配")
                return False
            
            if np.all(np.isnan(grid_values)):
                logger.error("网格数据全为NaN")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"数据验证失败: {str(e)}")
            return False
    
    def _create_figure(self, layout: Dict[str, Any]) -> Tuple[plt.Figure, plt.Axes]:
        """创建图形和轴"""
        try:
            # 创建图形
            fig = plt.figure(figsize=self.figsize)
            
            # 设置透明背景
            if self.transparent_bg:
                fig.patch.set_alpha(0.0)
            
            # 创建轴
            ax = fig.add_axes([
                layout['left'], 
                layout['bottom'], 
                layout['width'], 
                layout['height']
            ])
            
            # 设置轴背景
            if self.transparent_bg:
                ax.patch.set_alpha(0.0)
            
            return fig, ax
            
        except Exception as e:
            logger.error(f"创建图形失败: {str(e)}")
            raise
    
    def _draw_heatmap(self,
                      ax: plt.Axes,
                      grid_values: np.ndarray,
                      grid_x: np.ndarray,
                      grid_y: np.ndarray, 
                      colormap: str,
                      value_range: Optional[Tuple[float, float]]):
        """绘制热力图"""
        try:
            # 计算显示范围
            extent = [
                float(grid_x.min()), 
                float(grid_x.max()),
                float(grid_y.min()), 
                float(grid_y.max())
            ]
            
            # 确定数值范围
            if value_range is None:
                valid_data = grid_values[~np.isnan(grid_values)]
                if len(valid_data) > 0:
                    vmin, vmax = float(valid_data.min()), float(valid_data.max())
                else:
                    vmin, vmax = 0, 1
            else:
                vmin, vmax = value_range
            
            # 创建颜色映射
            cmap = create_colormap(colormap)
            
            # 绘制图像
            im = ax.imshow(
                grid_values,
                extent=extent,
                aspect='auto',
                origin='lower',
                cmap=cmap,
                vmin=vmin,
                vmax=vmax,
                interpolation='bilinear'
            )
            
            # 移除所有装饰元素
            ax.set_xticks([])
            ax.set_yticks([])
            ax.set_xlabel('')
            ax.set_ylabel('')
            ax.axis('off')
            
            # 设置纵横比
            self._adjust_aspect_ratio(ax, extent)
            
        except Exception as e:
            logger.error(f"绘制热力图失败: {str(e)}")
            raise
    
    def _adjust_aspect_ratio(self, ax: plt.Axes, extent: list):
        """调整纵横比"""
        try:
            # 计算地理范围
            x_range = extent[1] - extent[0]
            y_range = extent[3] - extent[2]
            
            if x_range > 0 and y_range > 0:
                # 根据中心纬度调整纵横比
                center_y = (extent[2] + extent[3]) / 2
                aspect_ratio = 1 / np.cos(np.deg2rad(center_y))
                ax.set_aspect(aspect_ratio, adjustable='box')
            
        except Exception as e:
            logger.debug(f"调整纵横比失败: {str(e)}")
    
    def _set_title(self, ax: plt.Axes, title: str, layout: Dict[str, Any]):
        """设置标题"""
        try:
            if title:
                ax.set_title(
                    title,
                    fontsize=layout.get('title_fontsize', 16),
                    pad=layout.get('title_pad', 20),
                    fontweight='bold'
                )
        except Exception as e:
            logger.warning(f"设置标题失败: {str(e)}")
    
    def _save_svg(self, fig: plt.Figure, save_path: str) -> bool:
        """保存SVG文件"""
        try:
            # 确保保存目录存在
            Path(save_path).parent.mkdir(parents=True, exist_ok=True)
            
            # 保存参数
            save_kwargs = {
                'format': 'svg',
                'bbox_inches': 'tight',
                'pad_inches': 0,
                'edgecolor': 'none'
            }
            
            if self.transparent_bg:
                save_kwargs['facecolor'] = 'none'
                save_kwargs['transparent'] = True
            else:
                save_kwargs['facecolor'] = 'white'
            
            # 保存文件
            fig.savefig(save_path, **save_kwargs)
            
            return True
            
        except Exception as e:
            logger.error(f"保存SVG文件失败: {str(e)}")
            return False

def create_clean_interpolation_svg(
    grid_values: np.ndarray,
    grid_x: np.ndarray,
    grid_y: np.ndarray,
    save_path: str,
    figsize: Optional[Tuple[float, float]] = None,
    colormap: str = 'jet',
    value_range: Optional[Tuple[float, float]] = None,
    transparent_bg: bool = True,
    title: Optional[str] = None
) -> bool:
    """
    创建纯净版插值热力图SVG
    
    Args:
        grid_values: 插值网格数据
        grid_x: 网格X坐标
        grid_y: 网格Y坐标
        save_path: 保存路径
        figsize: 图形尺寸
        colormap: 颜色映射
        value_range: 数值范围
        transparent_bg: 是否透明背景
        title: 图片标题
        
    Returns:
        是否成功
    """
    try:
        generator = SVGMapGenerator(
            figsize=figsize,
            transparent_bg=transparent_bg
        )
        
        return generator.generate_svg(
            grid_values=grid_values,
            grid_x=grid_x,
            grid_y=grid_y,
            save_path=save_path,
            colormap=colormap,
            value_range=value_range,
            title=title
        )
        
    except Exception as e:
        logger.error(f"创建SVG失败: {str(e)}")
        return False


def create_multi_format_outputs(
    grid_values: np.ndarray,
    grid_x: np.ndarray,
    grid_y: np.ndarray,
    base_path: str,
    formats: list = ['svg', 'png'],
    **kwargs
) -> Dict[str, str]:
    """
    创建多种格式的输出文件
    
    Args:
        grid_values: 插值网格数据
        grid_x: 网格X坐标
        grid_y: 网格Y坐标
        base_path: 基础文件路径（不含扩展名）
        formats: 输出格式列表
        **kwargs: 其他参数
        
    Returns:
        格式到文件路径的映射
    """
    results = {}
    
    try:
        for fmt in formats:
            file_path = f"{base_path}.{fmt}"
            
            if fmt == 'svg':
                success = create_clean_interpolation_svg(
                    grid_values, grid_x, grid_y, file_path, **kwargs
                )
            elif fmt == 'png':
                # 为PNG格式设置适当的DPI
                generator = SVGMapGenerator(
                    figsize=kwargs.get('figsize'),
                    dpi=kwargs.get('dpi', 300),
                    transparent_bg=kwargs.get('transparent_bg', True)
                )
                # 临时改变保存格式
                plt.rcParams['savefig.format'] = 'png'
                success = generator.generate_svg(
                    grid_values, grid_x, grid_y, file_path,
                    colormap=kwargs.get('colormap', 'jet'),
                    value_range=kwargs.get('value_range'),
                    title=kwargs.get('title')
                )
                plt.rcParams['savefig.format'] = 'svg'
            else:
                logger.warning(f"不支持的格式: {fmt}")
                continue
            
            if success:
                results[fmt] = file_path
                logger.info(f"生成{fmt.upper()}格式成功: {file_path}")
            else:
                logger.error(f"生成{fmt.upper()}格式失败: {file_path}")
        
        return results
        
    except Exception as e:
        logger.error(f"创建多格式输出失败: {str(e)}")
        return results

def validate_svg_output(file_path: str) -> bool:
    """
    验证SVG文件是否有效
    
    Args:
        file_path: SVG文件路径
        
    Returns:
        是否有效
    """
    try:
        if not Path(file_path).exists():
            return False
        
        # 检查文件大小
        file_size = Path(file_path).stat().st_size
        if file_size == 0:
            logger.error(f"SVG文件为空: {file_path}")
            return False
        
        # 检查是否包含SVG标签
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read(1000)  # 读取前1000字符
            if '<svg' not in content:
                logger.error(f"文件不包含SVG标签: {file_path}")
                return False
        
        logger.info(f"SVG文件验证通过: {file_path}")
        return True
        
    except Exception as e:
        logger.error(f"验证SVG文件失败: {str(e)}")
        return False