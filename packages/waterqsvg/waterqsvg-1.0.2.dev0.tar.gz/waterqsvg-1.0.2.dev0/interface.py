#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
WaterQSVG 固定启动接口

这是一个固定的启动接口，用于接收参数并调用waterqsvg包进行处理。
算法更新只需要重新发布和安装waterqsvg包，无需修改此接口文件。
"""

import sys

# 导入并运行主程序 - 直接使用统一接口
try:
    from waterqsvg.unified_interface import main
except ImportError:
    # 尝试开发模式导入
    try:
        from pathlib import Path

        # 添加src到Python路径
        src_path = Path(__file__).parent / "src"
        if src_path.exists():
            sys.path.insert(0, str(src_path))
            from waterqsvg.unified_interface import main
        else:
            print("error[1003]: waterqsvg包未安装或导入失败")
            sys.exit(1)
    except Exception as e:
        print(f"error[1003]: waterqsvg包未安装或导入失败: {str(e)}")
        sys.exit(1)

OUTPUT_DIR = "./water_quality_outputs/"

if __name__ == "__main__":
    # 添加默认输出目录参数到命令行参数
    if "--output-dir" not in sys.argv:
        sys.argv.extend(["--output-dir", OUTPUT_DIR])
    main()