# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

WaterQSVG 是一个专用于从水质监测数据生成SVG热力图的独立Python库。从原AutoReportV3项目中提取并优化了核心的图像生成功能，支持多种数据源输入，提供高质量的SVG矢量图输出。

## 常用开发命令

### 安装和设置
```bash
# 安装依赖
pip install -r requirements.txt

# 或使用uv (推荐)
uv run pip install -r requirements.txt

# 安装为开发包
pip install -e .
```

### 运行测试
```bash
# 基础测试运行
python tests/test_basic_functionality.py

# 使用uv运行测试
uv run python tests/test_basic_functionality.py

# 使用unittest运行所有测试
python -m unittest discover tests -v
```

### 代码质量检查
```bash
# 代码格式化
black src/ tests/ examples/

# 代码检查
flake8 src/ tests/ examples/
```

### 运行示例
```bash
# 基础使用示例
python examples/basic_usage.py

# 高级功能示例
python examples/advanced_options.py

# 使用uv运行示例
uv run python examples/basic_usage.py

# 使用interface.py处理OSS数据
uv run python interface.py --zip-url "https://example.com/data.zip"

# 使用JSON配置文件
uv run python interface.py --zip-url "/path/to/config.json"

# 使用标准输入传递URL（推荐用于复杂URL）
echo "https://example.com/data.zip" | uv run python interface.py

# 使用标准输入传递JSON配置文件路径
echo "/path/to/config.json" | uv run python interface.py
```

### Windows用户特别注意

如果在Windows命令行中URL包含`&`符号，建议使用以下方式：

```bash
# 方法1：使用标准输入（推荐）
echo https://example.com/data.zip?param1=value1^&param2=value2 | uv run python interface.py

# 方法2：URL用双引号包围
uv run python interface.py --zip-url "https://example.com/data.zip?param1=value1&param2=value2"
```

## 核心架构

### 数据处理流程
1. **数据获取** (`waterqsvg/core/downloader.py`): 支持HTTP/HTTPS URL和阿里云OSS下载
2. **数据解压** (`waterqsvg/core/extractor.py`): 安全的ZIP文件解压处理
3. **数据解析** (`waterqsvg/data/parser.py`): 解析INDEXS.CSV + POS.TXT格式数据
4. **数据标准化** (`waterqsvg/data/standardizer.py`): 统一坐标和指标名称
5. **数据验证** (`waterqsvg/data/validator.py`): 数据质量检查和错误处理

### 插值算法模块 (`waterqsvg/interpolation/`)
- **Alpha Shape** (`alpha_shape.py`): 高精度边界检测算法
- **凸包算法** (`convex_hull.py`): 快速边界计算
- **密度边界** (`density_boundary.py`): 基于点密度的边界检测
- **增强插值** (`enhanced_interpolation.py`): 集成边界检测的智能插值

### 可视化模块 (`waterqsvg/visualization/`)
- **SVG生成器** (`svg_generator.py`): 高质量SVG图片生成
- **布局计算器** (`layout_calculator.py`): 自适应布局计算
- **颜色映射器** (`color_mapper.py`): 专业水质色彩方案

### 配置和工具
- **水质指标配置** (`waterqsvg/config/indicators.py`): 支持15+种水质指标，自动识别未知指标
- **国标分级** (`waterqsvg/config/grading_standards.py`): GB 3838-2002水质标准
- **地理工具** (`waterqsvg/utils/geo.py`): 坐标转换和验证
- **路径管理** (`waterqsvg/utils/path_manager.py`): 文件路径统一管理

## 主要入口点

### WaterQualityProcessor类 (`waterqsvg/unified_interface.py`)
主控制器类，协调整个数据处理和SVG生成流程。

#### 主要方法
- `process_from_oss_zip()`: 从OSS ZIP文件处理水质数据并生成SVG
- `_get_available_indicators()`: 获取数据中可用的水质指标
- `_generate_svg_for_indicator()`: 为单个指标生成SVG
- `_calculate_bounds_info()`: 计算经纬度边界信息用于地图叠加

#### 关键参数
- `indicator`: 水质指标 (cod, nh3n, tp, tn, do, ph, turbidity, chla等)
- `colormap`: 颜色映射 (jet, viridis, water_quality, RdYlBu_r等)
- `boundary_method`: 边界检测方法 (alpha_shape, convex_hull, density_based)
- `interpolation_method`: 插值方法 (linear, cubic, nearest)
- `grid_resolution`: 网格分辨率 (默认400)

## 数据格式要求

### CSV文件格式
需要包含以下列：
- `longitude`: 经度坐标
- `latitude`: 纬度坐标
- 水质指标列 (如 `cod`, `nh3n`, `tp` 等)

### DataFrame格式
```python
df = pd.DataFrame({
    'longitude': [120.2156, 120.2187, ...],
    'latitude': [31.3124, 31.3098, ...],
    'cod': [15.2, 18.7, ...],
    'nh3n': [0.8, 1.2, ...]
})
```

## 支持的水质指标

| 指标代码 | 中文名称 | 英文名称 | 国标分级 |
|---------|---------|----------|---------|
| cod | 化学需氧量 | Chemical Oxygen Demand | ✅ |
| nh3n | 氨氮 | Ammonia Nitrogen | ✅ |
| tp | 总磷 | Total Phosphorus | ✅ |
| tn | 总氮 | Total Nitrogen | ✅ |
| do | 溶解氧 | Dissolved Oxygen | ✅ |
| ph | pH值 | pH Value | ✅ |
| turbidity | 浊度 | Turbidity | ❌ |
| chla | 叶绿素a | Chlorophyll-a | ❌ |

## JSON配置文件格式

支持使用JSON配置文件来传递下载链接，文件格式如下：

```json
{
    "file_url": "https://example.com/water_quality_data.zip",
    "description": "数据描述信息（可选）",
    "project_name": "水质监测项目（可选）",
    "date": "2024-01-15（可选）"
}
```

**必需字段：**
- `file_url`: ZIP文件的下载链接

**可选字段：**
- `description`: 数据描述信息
- `project_name`: 项目名称  
- `date`: 数据日期
- 其他自定义字段（将被忽略）

## 环境变量配置

项目支持通过环境变量配置：
- `OSS_ACCESS_KEY_ID`: 阿里云OSS访问密钥
- `OSS_ACCESS_KEY_SECRET`: 阿里云OSS访问密钥
- `OSS_ENDPOINT`: OSS端点
- `INTERPOLATION_RESOLUTION`: 插值分辨率
- `DEFAULT_COLORMAP`: 默认颜色映射

## 性能特点

- 高精度Alpha Shape边界检测算法
- 支持400x400+高分辨率网格插值
- 大数据集的快速处理能力
- 完善的数据验证和错误处理
- 模块化设计便于扩展和维护

## 测试框架

项目使用Python标准库的unittest框架：
- 测试文件：`tests/test_basic_functionality.py`
- 覆盖数据处理、插值、可视化等核心功能
- 包含正常功能和错误处理测试

## 开发注意事项

1. 使用uv运行Python命令是推荐的方式
2. 项目在WSL环境中运行，通过/mnt/目录访问Windows文件系统
3. 代码使用中文注释，保持与原项目一致的风格
4. 所有核心算法都有详细的数学原理注释
5. 错误处理机制完善，提供详细的错误信息