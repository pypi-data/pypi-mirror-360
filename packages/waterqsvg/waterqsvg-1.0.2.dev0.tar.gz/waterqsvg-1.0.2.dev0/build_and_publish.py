#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
WaterQSVG 包构建和发布脚本
"""

import subprocess
import sys
from pathlib import Path

def run_command(cmd, description):
    """运行命令并检查结果"""
    print(f"\n🔧 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} 成功")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} 失败:")
        print(f"错误代码: {e.returncode}")
        if e.stdout:
            print(f"标准输出: {e.stdout}")
        if e.stderr:
            print(f"错误输出: {e.stderr}")
        return False

def main():
    """主函数"""
    print("🚀 开始构建和发布 WaterQSVG 包")
    
    # 确保在正确的目录
    project_root = Path(__file__).parent
    print(f"📁 项目根目录: {project_root}")
    
    # 步骤1: 清理之前的构建
    print("\n📦 清理构建目录...")
    build_dirs = ["build", "dist", "*.egg-info"]
    for pattern in build_dirs:
        subprocess.run(f"rm -rf {pattern}", shell=True)
    print("✅ 清理完成")
    
    # 步骤2: 运行测试
    if not run_command("uv run python -m pytest tests/ -v", "运行测试"):
        print("⚠️  测试失败，但继续构建...")
    
    # 步骤3: 检查代码风格
    if not run_command("uv run python -c \"import waterqsvg; print(f'包导入成功，版本: {waterqsvg.__version__}')\"", "检查包导入"):
        print("❌ 包导入失败，停止构建")
        return False
    
    # 步骤4: 构建包
    if not run_command("uv build", "构建包"):
        print("❌ 包构建失败")
        return False
    
    # 步骤5: 检查构建结果
    print("\n📋 构建结果:")
    dist_dir = project_root / "dist"
    if dist_dir.exists():
        for file in dist_dir.iterdir():
            print(f"  📦 {file.name}")
    
    # 步骤6: 发布提示
    print("\n🎉 构建完成！")
    print("\n📝 发布步骤:")
    print("1. 检查 dist/ 目录中的文件")
    print("2. 测试安装: pip install dist/waterqsvg-*.whl")
    print("3. 发布到测试PyPI: uv publish --repository testpypi")
    print("4. 发布到正式PyPI: uv publish")
    
    print("\n⚠️  发布前请确保:")
    print("- 已更新版本号")
    print("- 已更新CHANGELOG")
    print("- 已测试所有功能")
    print("- 已配置PyPI令牌")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)