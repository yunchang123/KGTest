"""
工具函数模块
"""
import json
from typing import Dict, List, Any, Optional
from pathlib import Path


def load_json(filepath: Path) -> Dict[str, Any]:
    """加载JSON文件"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json(data: Dict[str, Any], filepath: Path, indent: int = 2) -> None:
    """保存JSON文件"""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=indent)


def truncate_string(s: str, max_length: int, suffix: str = '...') -> str:
    """截断字符串"""
    if len(s) <= max_length:
        return s
    return s[:max_length - len(suffix)] + suffix


def get_function_class_name(func_class: int, mapping: Dict[int, str]) -> str:
    """获取功能类别名称"""
    return mapping.get(func_class, f'Class_{func_class}')


def get_physical_class_name(phy_class: int, mapping: Dict[int, str]) -> str:
    """获取物理类别名称"""
    return mapping.get(phy_class, f'Physical_{phy_class}')


def calculate_node_size(base_size: float, chip_length: float, 
                        scale_factor: float = 5.0) -> float:
    """根据芯片尺寸计算节点大小"""
    return base_size + chip_length * scale_factor


def format_statistics(df) -> Dict[str, Any]:
    """格式化统计数据"""
    return {
        'total_components': len(df),
        'unique_packages': df['C'].nunique(),
        'unique_functions': df['FunctionClass'].nunique(),
        'unique_physical': df['PhysicalClass'].nunique(),
        'avg_length': df['ChipL'].mean(),
        'avg_width': df['ChipW'].mean(),
        'avg_height': df['ChipH'].mean(),
        'top_packages': df['C'].value_counts().head(5).to_dict(),
        'function_distribution': df['FunctionClass'].value_counts().sort_index().to_dict()
    }


class ProgressLogger:
    """进度日志器"""

    def __init__(self, total_steps: int = 0):
        self.total_steps = total_steps
        self.current_step = 0

    def log(self, message: str):
        """记录进度"""
        self.current_step += 1
        if self.total_steps > 0:
            progress = (self.current_step / self.total_steps) * 100
            print(f"[{self.current_step}/{self.total_steps}] ({progress:.1f}%) {message}")
        else:
            print(f"[{self.current_step}] {message}")

    def info(self, message: str):
        """记录信息"""
        print(f"[INFO] {message}")

    def success(self, message: str):
        """记录成功"""
        print(f"[✓] {message}")

    def error(self, message: str):
        """记录错误"""
        print(f"[✗] {message}")
