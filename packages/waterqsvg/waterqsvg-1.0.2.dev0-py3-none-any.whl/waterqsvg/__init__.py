"""
WaterQSVG - Water Quality SVG Generator

一个专用于从水质监测数据生成SVG热力图的独立库
支持从ZIP文件下载、数据解析、插值计算到SVG图片生成的完整流程
"""

# 版本号获取，优先级：包元数据 > _version.py > fallback
try:
    from importlib.metadata import version, PackageNotFoundError
    try:
        __version__ = version("waterqsvg")
    except PackageNotFoundError:
        # 开发环境或未安装的包，尝试从_version.py获取
        try:
            from ._version import __version__
        except ImportError:
            __version__ = "0.1.0"  # fallback版本
except ImportError:
    # Python < 3.8，使用importlib_metadata
    try:
        from importlib_metadata import version, PackageNotFoundError
        try:
            __version__ = version("waterqsvg")
        except PackageNotFoundError:
            try:
                from ._version import __version__
            except ImportError:
                __version__ = "0.1.0"
    except ImportError:
        # 完全fallback
        try:
            from ._version import __version__
        except ImportError:
            __version__ = "0.1.0"

__author__ = "Water Quality Monitoring Team"

from .visualization.svg_generator import create_clean_interpolation_svg
from .interpolation.enhanced_interpolation import enhanced_interpolation_with_boundary
from .unified_interface import WaterQualityProcessor, main

__all__ = [
    'WaterQualityProcessor',
    'create_clean_interpolation_svg', 
    'enhanced_interpolation_with_boundary',
    'main'
]