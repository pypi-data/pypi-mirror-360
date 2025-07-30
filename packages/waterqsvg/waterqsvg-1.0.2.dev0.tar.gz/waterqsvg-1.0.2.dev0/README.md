# WaterQSVG

🌊 专用于从OSS数据生成水质SVG热力图的精简Python工具

## 🚀 项目简介

WaterQSVG (Water Quality SVG Generator) 是一个专门用于处理OSS水质监测数据并生成高质量SVG热力图的工具。支持从OSS ZIP文件下载、解析INDEXS.CSV+POS.TXT格式数据、使用增强插值算法生成平滑热力图，并输出精确的地理边界信息用于地图叠加。

### ✨ 核心特性

- 🔗 **OSS直连下载**：直接从阿里云OSS下载ZIP数据包
- 📋 **标准格式解析**：支持INDEXS.CSV + POS.TXT格式数据
- 🧮 **增强插值算法**：Alpha Shape边界检测 + 高分辨率插值
- 🎨 **SVG矢量输出**：透明背景，适合地图叠加
- 📍 **地理边界信息**：输出精确的经纬度坐标用于地图定位
- 🔄 **批量处理**：自动识别并处理所有可用指标

## 📦 安装方法

### 使用uv安装（推荐）

```bash
# 克隆项目
git clone <repository-url>
cd waterqsvg

# 初始化uv项目
uv init

# 安装依赖
uv add numpy pandas matplotlib scipy requests pillow chardet python-dotenv
```

### 传统pip安装

```bash
# 安装依赖
pip install -r requirements.txt

# 安装项目
pip install -e .
```

### 从PyPI安装（发布后）

```bash
# 使用pip安装
pip install waterqsvg

# 使用uv安装
uv add waterqsvg
```

## 🎯 快速开始

### 基本使用

```python
from waterqsvg import WaterQualityProcessor

# OSS ZIP文件URL
oss_zip_url = "https://your-oss-bucket.oss-cn-shanghai.aliyuncs.com/data.zip"

# 使用处理器
with WaterQualityProcessor(
    output_dir="./outputs",
    grid_resolution=400
) as processor:
    
    # 处理数据并生成SVG
    results = processor.process_from_oss_zip(
        zip_url=oss_zip_url,
        colormap="jet",
        boundary_method="alpha_shape",
        interpolation_method="linear",
        transparent_bg=True
    )
    
    # 查看结果
    for indicator, result in results.items():
        if result:
            print(f"指标: {result['indicator_name']}")
            print(f"SVG文件: {result['svg_path']}")
            print(f"边界文件: {result['bounds_path']}")
```

### 命令行使用

```bash
# 使用waterqsvg命令（安装包后可用）
waterqsvg --zip-url "https://example.com/data.zip" --output-dir "./outputs"

# 使用JSON配置文件
waterqsvg --zip-url "/path/to/config.json" --colormap "water_quality" --resolution 600

# 使用标准输入传递URL（推荐用于复杂URL）
echo "https://example.com/data.zip" | waterqsvg --output-dir "./outputs"
echo "/path/to/config.json" | waterqsvg

# 兼容的interface.py方式（开发模式）
python interface.py --zip-url "https://example.com/data.zip" --output-dir "./outputs"
```

### 运行示例

```bash
# 使用uv运行开发版本
uv run waterqsvg --zip-url "https://example.com/data.zip"

# 运行使用示例
uv run python example_usage.py
```

## 📊 支持的水质指标

自动识别并处理以下指标：

| 指标代码 | 中文名称 | 英文名称 | 单位 |
|---------|---------|----------|------|
| cod | 化学需氧量 | Chemical Oxygen Demand | mg/L |
| nh3n | 氨氮 | Ammonia Nitrogen | mg/L |
| tp | 总磷 | Total Phosphorus | mg/L |
| tn | 总氮 | Total Nitrogen | mg/L |
| chla | 叶绿素a | Chlorophyll-a | μg/L |
| cod_mn | 高锰酸盐指数 | COD Permanganate | mg/L |
| ss | 总悬浮物 | Total Suspended Solids | mg/L |
| bga | 蓝绿藻 | Blue-Green Algae | 细胞/mL |

## 🗂️ 数据格式要求

### 输入数据结构

ZIP文件必须包含：
- `INDEXS.csv` - 水质指标数据
- `POS.txt` - GPS坐标数据

#### INDEXS.csv 格式示例
```csv
number,CHLa,Turbidity,SS,COD,TP,NH3-N,Bga,CODMn,TN
1,6.646,10.689,10.635,9.053,0.066,0.127,6.034,3.174,0.471
2,6.427,11.098,11.172,9.030,0.063,0.123,2.686,3.121,0.463
```

#### POS.txt 格式示例
```
/path/file_1.csv latitude: 31.516106 longitude: 120.267944 height: 110.27
/path/file_2.csv latitude: 31.516125 longitude: 120.267938 height: 110.26
```

## 📂 输出文件

每个水质指标生成两个文件：

### 1. SVG热力图文件
- 文件名：`{指标}_heatmap.svg`
- 格式：矢量SVG，透明背景
- 用途：直接叠加到地图上

### 2. 地理边界JSON文件
- 文件名：`{指标}_bounds.json`
- 内容：精确的经纬度边界信息
- 用途：地图定位和叠加

#### 边界文件示例
```json
{
  "geographic_bounds": {
    "min_longitude": 120.264922,
    "max_longitude": 120.267936,
    "min_latitude": 31.515932,
    "max_latitude": 31.520750,
    "center_longitude": 120.266429,
    "center_latitude": 31.518341
  },
  "grid_info": {
    "grid_resolution": 400,
    "valid_pixels": 83583
  },
  "projection_info": {
    "coordinate_system": "WGS84",
    "units": "degrees"
  }
}
```

## 🎨 配置选项

### 颜色映射
- `jet` - 彩虹色映射（默认）
- `water_quality` - 专业水质色彩
- `viridis` - 感知均匀色彩
- `RdYlBu_r` - 红-黄-蓝反向

### 边界检测方法
- `alpha_shape` - Alpha Shape算法（默认，高精度）
- `convex_hull` - 凸包算法（快速）
- `density_based` - 密度边界检测

### 插值方法
- `linear` - 线性插值（默认）
- `cubic` - 三次插值（更平滑）
- `nearest` - 最近邻插值

## 🏗️ 项目结构

```
svg-water-quality-generator/
├── water_quality_processor.py    # 主处理脚本
├── example_usage.py             # 使用示例
├── src/                         # 核心模块
│   ├── core/                    # 核心功能
│   │   ├── downloader.py        # OSS下载器
│   │   └── extractor.py         # ZIP解压器
│   ├── data/                    # 数据处理
│   │   ├── parser.py            # 数据解析器
│   │   ├── standardizer.py      # 数据标准化
│   │   └── validator.py         # 数据验证
│   ├── interpolation/           # 插值算法
│   │   ├── alpha_shape.py       # Alpha Shape
│   │   ├── convex_hull.py       # 凸包算法
│   │   ├── density_boundary.py  # 密度边界
│   │   └── enhanced_interpolation.py # 增强插值
│   ├── visualization/           # 可视化
│   │   ├── svg_generator.py     # SVG生成器
│   │   ├── color_mapper.py      # 颜色映射
│   │   └── layout_calculator.py # 布局计算
│   ├── config/                  # 配置
│   │   └── indicators.py        # 指标配置
│   └── utils/                   # 工具
│       └── logger.py            # 日志工具
└── tests/                       # 测试
    └── test_basic_functionality.py
```

## 🚀 地图叠加示例

生成的SVG和边界信息可以直接用于Web地图：

### Leaflet.js 示例
```javascript
// 读取边界信息
const bounds = L.latLngBounds(
  [31.515932, 120.264922],  // 西南角
  [31.520750, 120.267936]   // 东北角
);

// 叠加SVG图像
const overlay = L.imageOverlay('cod_heatmap.svg', bounds, {
  opacity: 0.7,
  interactive: false
});

overlay.addTo(map);
```

## 🛠️ 开发环境

### 运行测试
```bash
uv run python tests/test_basic_functionality.py
```

### 代码格式化
```bash
black src/ tests/ *.py
flake8 src/ tests/ *.py
```

## 📝 版本信息

- **当前版本**: 1.0.0
- **Python要求**: >= 3.8
- **主要依赖**: numpy, pandas, matplotlib, scipy

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个项目。

## 📄 许可证

MIT License - 查看 [LICENSE](LICENSE) 文件了解详情。