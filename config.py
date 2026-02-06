"""
PCB知识图谱系统配置文件
"""
import os
from pathlib import Path

# 项目根目录
BASE_DIR = Path(__file__).parent.absolute()

# 数据路径
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"

# 确保输出目录存在
OUTPUT_DIR.mkdir(exist_ok=True)

# 输入文件配置
INPUT_FILE = DATA_DIR / "Vayo.json"

# 可视化配置
VIS_CONFIG = {
    'figure_size': (20, 16),
    'dpi': 200,
    'bgcolor': '#0d1117',
    'node_colors': {
        'PhysicalClass': '#ff2e63',
        'FunctionClass': '#08d9d6',
        'Package': '#5d9cec',
        'Component': '#f39c12'
    },
    'edge_colors': {
        'hasPhysicalType': '#ff2e63',
        'hasFunction': '#08d9d6',
        'usesPackage': '#5d9cec'
    },
    'font_size': {
        'PhysicalClass': 11,
        'FunctionClass': 10,
        'Package': 9,
        'Component': 7
    },
    'node_sizes': {
        'PhysicalClass': 1000,
        'FunctionClass': 700,
        'Package': 500,
        'Component': 250
    }
}

# 功能类别映射
FUNCTION_CLASS_MAP = {
    1: 'Resistor',
    2: 'Capacitor',
    7: 'Inductor',
    11: 'LED',
    12: 'Diode',
    14: 'IC/Transistor'
}

# 物理类别映射
PHYSICAL_CLASS_MAP = {
    1: 'Passive',
    2: 'Active',
    3: 'Connector'
}

# 导出配置
EXPORT_CONFIG = {
    'csv_encoding': 'utf-8-sig',
    'graph_formats': ['graphml', 'gml', 'gexf'],
    'max_display_components': 80  # 可视化时最大显示元件数
}
