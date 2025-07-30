#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
水质指标配置模块
定义各种水质指标的基本信息和合理范围
"""

# 水质指标配置字典
WATER_QUALITY_INDICATORS = {
    'codcr': {
        'name': '化学需氧量',
        'name_en': 'Chemical Oxygen Demand',
        'unit': 'mg/L',
        'description': '反映水体中有机污染物含量的综合指标',
        'typical_range': (0, 1000),
        'optimal_range': (0, 15),
        'aliases': ['COD', '化学需氧量', 'chemical_oxygen_demand', 'cod', 'codcr'],
        'colormap': 'water_quality'
    },
    
    'nh3n': {
        'name': '氨氮',
        'name_en': 'Ammonia Nitrogen',
        'unit': 'mg/L',
        'description': '水体中氨态氮的含量，是重要的水质污染指标',
        'typical_range': (0, 100),
        'optimal_range': (0, 0.15),
        'aliases': ['NH3-N', 'NH3_N', '氨氮', 'ammonia_nitrogen'],
        'colormap': 'water_quality'
    },
    
    'tp': {
        'name': '总磷',
        'name_en': 'Total Phosphorus',
        'unit': 'mg/L',
        'description': '水体中磷的总含量，是富营养化的关键指标',
        'typical_range': (0, 50),
        'optimal_range': (0, 0.02),
        'aliases': ['TP', '总磷', 'total_phosphorus'],
        'colormap': 'water_quality'
    },
    
    'tn': {
        'name': '总氮',
        'name_en': 'Total Nitrogen',
        'unit': 'mg/L',
        'description': '水体中氮的总含量，包括有机氮和无机氮',
        'typical_range': (0, 200),
        'optimal_range': (0, 0.2),
        'aliases': ['TN', '总氮', 'total_nitrogen'],
        'colormap': 'water_quality'
    },
    
    'do': {
        'name': '溶解氧',
        'name_en': 'Dissolved Oxygen',
        'unit': 'mg/L',
        'description': '水体中溶解氧的含量，反映水体的自净能力',
        'typical_range': (0, 20),
        'optimal_range': (6, 20),
        'aliases': ['DO', '溶解氧', 'dissolved_oxygen'],
        'colormap': 'temperature',
        'reverse_scale': True  # 溶解氧越高越好
    },
    
    'ph': {
        'name': 'pH值',
        'name_en': 'pH Value',
        'unit': '',
        'description': '水体的酸碱度指标',
        'typical_range': (0, 14),
        'optimal_range': (6.5, 8.5),
        'aliases': ['pH', 'PH', 'acidity'],
        'colormap': 'coolwarm'
    },
    
    'turbidity': {
        'name': '浊度',
        'name_en': 'Turbidity',
        'unit': 'NTU',
        'description': '水体的混浊程度，反映水中悬浮物含量',
        'typical_range': (0, 1000),
        'optimal_range': (0, 1),
        'aliases': ['TURBIDITY', '浊度', 'ntu'],
        'colormap': 'water_quality'
    },
    
    'chla': {
        'name': '叶绿素a',
        'name_en': 'Chlorophyll-a',
        'unit': 'μg/L',
        'description': '水体中叶绿素a的含量，反映藻类生物量',
        'typical_range': (0, 500),
        'optimal_range': (0, 1),
        'aliases': ['chl-a', 'chlorophyll_a', '叶绿素a', '叶绿素A'],
        'colormap': 'Greens'
    },
    
    'tss': {
        'name': '总悬浮物',
        'name_en': 'Total Suspended Solids',
        'unit': 'mg/L',
        'description': '水体中总悬浮固体的含量',
        'typical_range': (0, 500),
        'optimal_range': (0, 10),
        'aliases': ['TSS', '总悬浮物', 'total_suspended_solids'],
        'colormap': 'water_quality'
    },
    
    'ec': {
        'name': '电导率',
        'name_en': 'Conductivity',
        'unit': 'μS/cm',
        'description': '水体的导电能力，反映水中离子总量',
        'typical_range': (0, 10000),
        'optimal_range': (50, 1500),
        'aliases': ['EC', '电导率', 'conductivity', 'ec'],
        'colormap': 'viridis'
    },
    
    'salinity': {
        'name': '盐度',
        'name_en': 'Salinity',
        'unit': 'ppt',
        'description': '水体中盐分的含量',
        'typical_range': (0, 35),
        'optimal_range': (0, 0.5),
        'aliases': ['salinity', '盐度'],
        'colormap': 'Blues'
    },
    
    'temperature': {
        'name': '水温',
        'name_en': 'Water Temperature',
        'unit': '°C',
        'description': '水体温度',
        'typical_range': (-5, 50),
        'optimal_range': (10, 30),
        'aliases': ['temp', 'temperature', '水温', '温度'],
        'colormap': 'temperature'
    },
    
    'codmn': {
        'name': '高锰酸盐指数',
        'name_en': 'COD Permanganate',
        'unit': 'mg/L',
        'description': '高锰酸钾消耗量，反映水体有机污染程度',
        'typical_range': (0, 50),
        'optimal_range': (0, 2),
        'aliases': ['CODMn', '高锰酸盐指数', 'codmn', 'cod_mn'],
        'colormap': 'water_quality'
    },
    
    'ss': {
        'name': '总悬浮物',
        'name_en': 'Total Suspended Solids',
        'unit': 'mg/L',
        'description': '水体中悬浮固体物质含量',
        'typical_range': (0, 1000),
        'optimal_range': (0, 25),
        'aliases': ['SS', 'TSS', '总悬浮物'],
        'colormap': 'YlBr'
    },
    
    'bga': {
        'name': '蓝绿藻',
        'name_en': 'Blue-Green Algae',
        'unit': '细胞/mL',
        'description': '蓝绿藻密度，水华指示指标',
        'typical_range': (0, 100000),
        'optimal_range': (0, 10000),
        'aliases': ['BGA', 'Bga', '蓝绿藻'],
        'colormap': 'BuGn'
    },
    
    'bod': {
        'name': '生化需氧量',
        'name_en': 'Biochemical Oxygen Demand',
        'unit': 'mg/L',
        'description': '生化需氧量，反映水体有机污染的生物降解能力',
        'typical_range': (0, 500),
        'optimal_range': (0, 3),
        'aliases': ['BOD', 'BOD5', '生化需氧量'],
        'colormap': 'water_quality'
    },
    
    'tds': {
        'name': '总溶解固体',
        'name_en': 'Total Dissolved Solids',
        'unit': 'mg/L',
        'description': '水中总溶解固体含量',
        'typical_range': (0, 2000),
        'optimal_range': (0, 500),
        'aliases': ['TDS', '总溶解固体'],
        'colormap': 'viridis'
    },
    
    'orp': {
        'name': '氧化还原电位',
        'name_en': 'Oxidation-Reduction Potential',
        'unit': 'mV',
        'description': '水体的氧化还原电位',
        'typical_range': (-500, 800),
        'optimal_range': (200, 400),
        'aliases': ['ORP', 'REDOX', '氧化还原电位'],
        'colormap': 'RdYlBu'
    }
}

def get_indicator_info(indicator: str) -> dict:
    """
    获取指标信息
    
    Args:
        indicator: 指标名称
        
    Returns:
        指标信息字典
    """
    # 标准化指标名称
    indicator_lower = indicator.lower().strip()
    
    # 直接匹配
    if indicator_lower in WATER_QUALITY_INDICATORS:
        return WATER_QUALITY_INDICATORS[indicator_lower].copy()
    
    # 别名匹配
    for key, info in WATER_QUALITY_INDICATORS.items():
        aliases = [alias.lower() for alias in info.get('aliases', [])]
        if indicator_lower in aliases:
            return info.copy()
    
    # 包含匹配
    for key, info in WATER_QUALITY_INDICATORS.items():
        if indicator_lower in key or key in indicator_lower:
            return info.copy()
        
        # 检查别名包含
        for alias in info.get('aliases', []):
            if indicator_lower in alias.lower() or alias.lower() in indicator_lower:
                return info.copy()
    
    # 如果找不到，返回默认配置
    return {
        'name': indicator,
        'name_en': indicator,
        'unit': '',
        'description': f'{indicator}指标',
        'typical_range': (0, 100),
        'optimal_range': (0, 10),
        'aliases': [indicator],
        'colormap': 'jet'
    }

def get_all_indicator_names() -> list:
    """
    获取所有指标名称
    
    Returns:
        指标名称列表
    """
    return list(WATER_QUALITY_INDICATORS.keys())

def get_indicator_aliases(indicator: str) -> list:
    """
    获取指标的所有别名
    
    Args:
        indicator: 指标名称
        
    Returns:
        别名列表
    """
    info = get_indicator_info(indicator)
    return info.get('aliases', [indicator])

def validate_indicator_value(indicator: str, value: float) -> dict:
    """
    验证指标数值的合理性
    
    Args:
        indicator: 指标名称
        value: 指标数值
        
    Returns:
        验证结果字典
    """
    info = get_indicator_info(indicator)
    typical_range = info.get('typical_range', (0, 100))
    optimal_range = info.get('optimal_range', (0, 10))
    
    result = {
        'indicator': indicator,
        'value': value,
        'is_valid': True,
        'warnings': [],
        'level': 'normal'
    }
    
    # 检查是否在典型范围内
    if value < typical_range[0] or value > typical_range[1]:
        result['warnings'].append(f'数值超出典型范围 {typical_range}')
        result['level'] = 'unusual'
    
    # 检查是否在最优范围内
    if value < optimal_range[0] or value > optimal_range[1]:
        if result['level'] == 'normal':
            result['level'] = 'suboptimal'
    else:
        result['level'] = 'optimal'
    
    # 检查极端值
    if value < 0:
        result['warnings'].append('数值为负数，可能不合理')
        result['is_valid'] = False
    
    if value > typical_range[1] * 10:
        result['warnings'].append('数值极大，请检查数据正确性')
        result['is_valid'] = False
    
    return result

def get_recommended_colormap(indicator: str) -> str:
    """
    获取指标推荐的颜色映射
    
    Args:
        indicator: 指标名称
        
    Returns:
        颜色映射名称
    """
    info = get_indicator_info(indicator)
    return info.get('colormap', 'jet')

def is_reverse_scale_indicator(indicator: str) -> bool:
    """
    检查指标是否为反向尺度（数值越大越好）
    
    Args:
        indicator: 指标名称
        
    Returns:
        是否为反向尺度
    """
    info = get_indicator_info(indicator)
    return info.get('reverse_scale', False)